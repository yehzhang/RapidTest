import atexit
import json
import re
import shlex
from os import path
from subprocess import Popen
from threading import Timer

from .common_executors import BaseExecutor
from .rpc import ExecutionTargetRPCClient
from .._compat import with_metaclass, raise_from
from ..utils import natural_format


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


class ExternalExecutor(with_metaclass(ExternalExecutorFabric, BaseExecutor)):
    _SOCKET_ADDRESS = 'localhost', 0

    client = ExecutionTargetRPCClient(_SOCKET_ADDRESS)

    RETRY_TARGET = 1
    CONNECT_TIMEOUT = 1
    REQUEST_TIMEOUT = 5

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
            self.curr_target_id = self.new_target_id()
            self.prepare_external_target(addr)

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
        for i in range(max(self.RETRY_TARGET, 1)):
            try:
                self.run()
                self.client.connect(self.curr_target_id, self.CONNECT_TIMEOUT)
                result = self.client.request(self.curr_target_id, self.client.METHOD_EXECUTE,
                                             request_params, self.REQUEST_TIMEOUT)
            except OSError as e:
                if i == self.RETRY_TARGET - 1:
                    raise_from(IOError('failed to communicate with target properly'), e)
            else:
                # Update executed method names
                method_names, vals = result
                operations.update_operation_names(method_names)

                assert len(method_names) == len(vals)
                return (self.finalize_operation(*t) for t in zip(operations, vals))

    def prepare_external_target(self, socket_address):
        """Called once to prepare external resources.

        :param Tuple[str, int] socket_address:
        """
        raise NotImplementedError

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
        """
        :return Any: identification of external target for client
        """
        return 'Target:{}:{}:{}'.format(self.ENVIRONMENT, self.target_name, self.count_executions)

    @staticmethod
    def start_process(cmd):
        """
        :param str cmd:
        :return Popen:
        """
        return Popen(shlex.split(cmd))

    @staticmethod
    def wait_terminate(proc, timeout):
        """
        :param Popen proc:
        :param int timeout: in seconds. Kill process if it times out
        :return Any: retcode
        """

        def _t():
            proc.kill()

        t = Timer(timeout, _t)
        t.name = "Waiter-{}".format(proc)
        t.start()
        retcode = proc.wait()
        t.cancel()
        return retcode


def close_client():
    ExternalExecutor.client.close()


atexit.register(close_client)


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

    def get_compile_command(self):
        raise NotImplementedError
