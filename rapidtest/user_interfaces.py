from contextlib import contextmanager
from importlib import import_module
from inspect import getmodule

_kernel_mode = True
_privilege_violation_msg = None


@contextmanager
def user_mode(msg=None):
    """Prevent running privileged functions in this context.

    :param str msg: message to warn user about when calling privileged functions
    """
    global _kernel_mode, _privilege_violation_msg
    if not _kernel_mode:
        raise RuntimeError('Already in user mode')

    if msg is not None:
        _privilege_violation_msg = msg
    _kernel_mode = False
    yield
    _kernel_mode = True
    _privilege_violation_msg = None


def privileged(f):
    """Mark a function as privileged."""
    def _f(*args, **kwargs):
        if not _kernel_mode:
            msg = 'Using this feature is unsupported' if _privilege_violation_msg is None else \
                _privilege_violation_msg
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

try:
    get_dependency()
except Exception:
    raise AssertionError('Invalid dependency name')
