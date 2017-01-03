import json
import re
import shlex
from os import path
from subprocess import Popen
from threading import Timer

from .clients import ExecutionRPCClient
from .dependencies import get_dependencies
from .exceptions import ExternalException
from .outputs import ExecutionOutput
from .._compat import with_metaclass, raise_from, is_sequence, PRIMITIVE_TYPES as P_TYPES
from ..utils import identity, natural_format


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
        :return Iterable[OperationOutput]:
        """
        raise NotImplementedError

    def finalize_operation(self, operation, output):
        """
        :param Operation operation:
        :param Any output: returned value from the operation
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
            raise RuntimeError('type of return value {} is invalid'.format(type(val)))
        return val


class ExternalExecutorFabric(type):
    _executors = {}

    _DEFAULT_CONFIG = {
        'Java8': {
            'suffix': '.java',
            # 'compile_args': '',
            # 'run_args': '',
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
        :param Any default:
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
        :return List[str]:
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
                'cannot identify the way to execute {}. Supported external environment{s}: {item}',
                path, item=mcs.supported_environments()))
        return mcs.get(env)


def get_external_dependencies():
    ds = get_dependencies()
    ds.update({T.__name__: T for T in (ExternalException,)})
    return ds


class ExternalExecutor(with_metaclass(ExternalExecutorFabric, BaseExecutor)):
    _SOCKET_ADDRESS = 'localhost', 0

    client = ExecutionRPCClient(_SOCKET_ADDRESS, get_external_dependencies())

    RETRY_TARGET = 1

    running_options = None

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

    def __del__(self):
        self.close()

    def run(self):
        """Start client and target, and restart them if down. """
        # Start client
        addr = self.client.run()

        # Start target
        if self.curr_target_id is None:
            self.curr_target_id = self.prepare_external_target(addr)

        self.run_external_target()

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
        request_params = operations.to_params()

        self.count_executions += 1

        # Retry execution on failure
        # TODO move retry to client?
        for i in range(max(self.RETRY_TARGET, 1)):
            try:
                self.run()
                output = self.client.request(self.curr_target_id, self.client.METHOD_EXECUTE,
                                             request_params)
            except OSError as e:
                if i == self.RETRY_TARGET - 1:
                    raise_from(IOError('failed to communicate with target properly'), e)
            else:
                assert len(operations) == len(output)
                return (self.finalize_operation(*t) for t in zip(operations, output))

    def prepare_external_target(self, socket_address):
        """Called once to prepare external resources.

        :param Tuple[str, int] socket_address:
        :return Any: identification of external target for client
        """
        return self.new_target_id()

    def run_external_target(self):
        """Non-blocking method to start a process running the target. """
        # Check whether process is still up
        if self.proc is not None:
            if self.proc.poll() is None:
                # Assume process is running in this case
                # TODO any better idea?
                return

                # Start a new process
        self.proc = self.start_process(self.get_run_command())

    def get_run_command(self):
        raise NotImplementedError

    def new_target_id(self):
        return 'Target:{}:{}:{}'.format(self.ENVIRONMENT, self.target_name, self.count_executions)

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
        :param int timeout: in seconds. Kill process if it times out
        :return Any: retcode
        """
        if timeout is not None:
            def _t():
                proc.kill()

            Timer(timeout, _t).start()

        return proc.wait()


class CompiledExecutor(ExternalExecutor):
    COMPILE_TIMEOUT = 10

    compiler_options = None

    def prepare_external_target(self, socket_address):
        proc = self.start_process(self.get_compile_command())
        ret_code = self.wait_terminate(proc, self.COMPILE_TIMEOUT)
        if ret_code is None:
            raise RuntimeError('compilation timed out')
        elif ret_code != 0:
            raise RuntimeError('compilation failed')
        return super(CompiledExecutor, self).prepare_external_target(socket_address)

    def get_compile_command(self):
        raise NotImplementedError
