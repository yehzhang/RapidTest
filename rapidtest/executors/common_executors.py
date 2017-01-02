import json
import re
import shlex
from subprocess import Popen
from time import sleep

from os import path

from .clients import ExecutionRPCClient, Request
from .dependencies import get_dependencies
from .exceptions import ExternalExecutionTargetError
from .outputs import ExecutionOutput
from .._compat import with_metaclass, raise_from, is_sequence, isstring
from ..utils import PRIMITIVE_TYPES as P_TYPES, identity, natural_format


class BaseExecutor(object):
    ENVIRONMENT = None

    PRIMITIVE_TYPES = P_TYPES

    def __init__(self, target):
        self.target = target
        self.initialize()

    def initialize(self, post_proc=None, in_place_selector=None):
        self.in_place_selector = in_place_selector
        self.post_proc = post_proc or identity

    def execute(self, operations):
        """
        :param Operations operations:
        :return ExecutionOutput:
        """
        operations.initialize(self)
        return ExecutionOutput(self.execute_operations(operations))

    def execute_operations(self, operations):
        """
        :param Operations operations:
        :return iterable[OperationOutput]:
        """
        raise NotImplementedError

    def finalize_operation(self, operation, output):
        """
        :param Operation operation:
        :param any output: returned value from the operation
        :return OperationOutput:
        """
        if self.in_place_selector:
            output = self.in_place_selector(output)
        output = self.normalize_raw(output)
        return operation.to_output(output)

    def normalize_raw(self, val):
        return self.post_proc(self._normalize_type(val))

    @classmethod
    def _normalize_type(cls, val):
        if isinstance(val, cls.PRIMITIVE_TYPES) or val is None:
            pass
        elif is_sequence(val):
            val = [cls._normalize_type(o) for o in val]
        else:
            raise RuntimeError('Type of return value {} is invalid'.format(type(val)))
        return val


class ExternalExecutorFabric(type):
    _executors = {}

    _DEFAULT_CONFIG = {
        'Java8': {
            'suffix':          '.java',
            'command_compile': 'javac -cp ".:lib/*" {compiling_path}',
            'command_run':     'java -cp ".:lib/*" {running_path}',
        },
    }
    # noinspection PyTypeChecker
    _config = dict(_DEFAULT_CONFIG)

    def __new__(mcs, *args):
        """Register ExternalExecutors and initialize class variables."""
        cls = super(ExternalExecutorFabric, mcs).__new__(mcs, *args)

        # If cls is a terminal executor
        if cls.ENVIRONMENT:
            # Register cls
            mcs.set(cls)
            # Assign class variables
            mcs._initialize_class(cls)
        return cls

    @classmethod
    def load_config(mcs, path=None):
        """
        :param str path:
        """
        # noinspection PyTypeChecker
        config = dict(mcs._DEFAULT_CONFIG)
        if path:
            config.update(json.load(path))
        mcs._config = config

        # Update class variables
        for cls in mcs._executors.values():
            mcs._initialize_class(cls)

    @classmethod
    def _initialize_class(mcs, cls):
        cls_config = mcs._config.get(cls.ENVIRONMENT, {})
        for k, v in cls_config.items():
            if hasattr(cls, k):
                setattr(cls, k, v)

    @classmethod
    def get(mcs, env, default=None):
        """
        :param str env:
        :param any default:
        :return: type extends ExternalExecutor
        """
        if env is None:
            return None
        return mcs._executors.get(env.lower(), default)

    @classmethod
    def set(mcs, cls):
        """
        :param cls: type extends ExternalExecutor
        """
        mcs._executors[cls.ENVIRONMENT.lower()] = cls

    @classmethod
    def supported_environments(mcs):
        """
        :return [str]:
        """
        return [E.ENVIRONMENT for E in mcs._executors.values()]

    @classmethod
    def guess(mcs, path):
        """
        :param str path:
        :return ExternalExecutor:
        """
        for env, config in mcs._config.items():
            if 'suffix' in config:
                if path.endswith(config['suffix']):
                    break
            if 'filename_pattern' in config:
                _, _, filename = path.rpartition('/')
                if re.match(config['filename_pattern'], filename) is not None:
                    break
        else:
            raise ValueError(natural_format(
                'Cannot identify the way to execute {}. Supported external environment{s}: {item}',
                path, item=mcs.supported_environments()))
        return mcs.get(env)


class ExternalExecutor(with_metaclass(ExternalExecutorFabric, BaseExecutor)):
    command_run = None

    _SOCKET_ADDRESS = 'localhost', 0

    client = ExecutionRPCClient(_SOCKET_ADDRESS, get_dependencies())

    RETRY_TARGET = 1

    def __init__(self, target, target_name=None):
        """
        :param str target: path to target
        :param str target_name: Depending on what language to execute, it may be different. In
            Java, for example, it is a class name. """
        target = path.abspath(target)

        super(ExternalExecutor, self).__init__(target)

        self.target_path = target
        _, _, self.target_filename = target.rpartition('/')
        self.target_name = target_name  # validate it in subclasses
        self.count_executions = 0
        self.curr_target_id = None
        self.proc = None
        self.prepared = False
        self.running_path = None

    def __del__(self):
        self.close()

    def run(self):
        """Start client and target, and restart them if down. """
        # Start client
        addr = self.client.run()

        # Start target
        self.curr_target_id = self.get_target_id()
        if not self.prepared:
            self.prepare_external(addr)
            self.prepared = True
        self.run_external()

    def close(self):
        # Terminate target
        if self.proc is not None:
            if self.proc.poll() is None:
                self.client.notify(self.curr_target_id, self.client.METHOD_TERMINATE)
                self.wait_terminate(self.proc, 1)
            self.proc = None

        self.curr_target_id = None
        # Client keeps running until program exits

    def execute_operations(self, operations):
        request = Request(self.client.METHOD_EXECUTE, operations.to_params())

        self.count_executions += 1

        # Retry execution on failure
        resp = None
        for i in range(max(self.RETRY_TARGET, 1)):
            try:
                self.run()
                resp = self.client.request(self.curr_target_id, request)
            except IOError as e:
                if i == self.RETRY_TARGET - 1:
                    import traceback
                    traceback.print_exc()
                    raise_from(IOError('Failed to communicate with target properly'), e)
            else:
                break

        if resp.error:
            self.raise_external_exception(resp.error)

        assert len(operations) == len(resp.result)
        return (self.finalize_operation(*t) for t in zip(operations, resp.result))

    def prepare_external(self, socket_address):
        """Called once to prepare external resources. """
        raise NotImplementedError

    def run_external(self):
        """Non-blocking method to start a process running the target. """
        # Check whether process is still up
        if self.proc is not None:
            if self.proc.poll() is None:
                return  # assume process is running
        # Start a new process
        self.proc = self.start_process(self.get_run_command())

    def get_run_command(self):
        return self.command_run.format(running_path=self.running_path)

    def get_target_id(self):
        ret = '{}_target_{}_{}'.format(self.ENVIRONMENT, self.target_name, self.count_executions)
        return ret

    def raise_external_exception(self, e):
        """
        :param dict e: {'name': ..., 'message': ..., 'stack_trace': ...}
        """
        msg = 'Exception raised while executing external target'
        Ex = type(e['name'], (Exception,), {})
        resp_msg = '{}\n{}'.format(e['message'], e['stack_trace'])
        raise_from(ExternalExecutionTargetError(msg), Ex(resp_msg))

    @staticmethod
    def start_process(cmd):
        """
        :param str cmd:
        :return Popen:
        """
        return Popen(shlex.split(cmd))

    @staticmethod
    def wait_terminate(proc, timeout=None):
        """
        :param Popen proc:
        :param int timeout: in seconds
        :return any: retcode
        """
        if timeout is None:
            proc.wait()
        else:
            for _ in range(timeout // 0.1):
                if proc.poll() is None:
                    sleep(0.1)
                else:
                    break
            else:
                proc.kill()
        return proc.returncode


class CompiledExecutor(ExternalExecutor):
    command_compile = None

    COMPILE_TIMEOUT = 10

    def __init__(self, target, target_name=None):
        super(CompiledExecutor, self).__init__(target, target_name)

        self.compiling_path = None

    def prepare_external(self, socket_address):
        proc = self.start_process(self.get_compile_command())
        ret_code = self.wait_terminate(proc, self.COMPILE_TIMEOUT)
        if ret_code is None:
            raise RuntimeError('Compilation timed out')
        elif ret_code != 0:
            raise RuntimeError('Compilation failed')

    def get_compile_command(self):
        return self.command_compile.format(compiling_path=self.compiling_path)
