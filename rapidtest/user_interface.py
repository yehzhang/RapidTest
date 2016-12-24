from contextlib import contextmanager
from importlib import import_module
from inspect import getmodule

_kernel_mode = True


class UserMode(object):
    """Prevent running privileged functions in this context. """
    def __enter__(self):
        global _kernel_mode
        if not _kernel_mode:
            raise RuntimeError('Already in user mode')
        _kernel_mode = False

    def __exit__(self, exc_type, exc_val, exc_tb):
        global _kernel_mode
        _kernel_mode = True


def privileged(f):
    """Mark a function as privileged."""
    if not callable(f):
        raise TypeError('{} is not callable'.format(repr(f)))

    def _f(*args, **kwargs):
        if not _kernel_mode:
            msg = 'Calling {func_name} when judging is unsupported'.format(func_name=f.__name__)
            raise RuntimeError(msg)
        return f(*args, **kwargs)

    return _f


def inject_dependency(o):
    module = getmodule(o)
    if module is None:
        return

    dependency = get_dependency()
    for obj_name, obj in dependency.items():
        if not hasattr(module, obj_name):
            setattr(module, obj_name, obj)


def get_dependency():
    """
    :return dict, dict: {class_name: class}, {obj_name: obj}. Obj could be anything but class
    """
    dependency = {}
    pkg_name, _ = __name__.rsplit('.', 1)
    for module_name, obj_names in DEPENDENCY_NAMES.items():
        module = import_module(module_name, pkg_name)
        for obj_name in obj_names:
            obj = getattr(module, obj_name)
            dependency[obj_name] = obj
    return dependency


DEPENDENCY_NAMES = {
    '.data_structures': ['TreeNode', 'ListNode'],
    # __name__: [],
}
