import json
import re

from six import with_metaclass

from .outputs import ExecutionOutput
from ..utils import is_sequence, PRIMITIVE_TYPES as P_TYPES, identity, natural_format


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
        self.initialize(**operations.params)
        return ExecutionOutput(self._execute(operations))

    def _execute(self, operations):
        """
        :param Operations operations:
        :return: iterable of OperationOutput
        """
        raise NotImplementedError

    def normalize_raw_output(self, output):
        return self.post_proc(self._normalize_type(output))

    @classmethod
    def _normalize_type(cls, output):
        if isinstance(output, cls.PRIMITIVE_TYPES) or output is None:
            pass
        elif is_sequence(output):
            output = [cls._normalize_type(o) for o in output]
        else:
            raise RuntimeError('Type of output {} is invalid'.format(type(output)))
        return output


class ExternalExecutorFabric(type):
    _executors = {}

    _DEFAULT_CONFIG = {
        'Java8': {
            'suffix':          '.java',
            'package':         'execution',
            'command_compile': 'javac -cp {default_class_path} {filename}',
            'command_run':     'java -cp {default_class_path} {class_name}',
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

    def __init__(self, target, target_name=None):
        """Depending on what language to execute, target may be different. For example,
        in Java it is a class. """
        super(ExternalExecutor, self).__init__(target)
        self.target_name = target_name

    def _execute(self, operations):
        pass


class CompiledExecutor(ExternalExecutor):
    command_compile = None

    def compile(self):
        pass
