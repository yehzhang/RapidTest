from unittest import TestCase

EXAMPLES_PATH = '../examples'
SKIPPED_EXAMPLES = {472, 473, 477}


def _set_test_class():
    import re
    from imp import load_module, find_module, PY_SOURCE
    from pathlib import Path

    def _load_module(name, file, pathname, description):
        load_module(name, file, pathname, description)
        if file:
            file.close()

    def get_method(module_name, module_tuple):
        def _test(self):
            _load_module(module_name, *module_tuple)

        return _test

    sols_module_name = 'solutions'
    _load_module(sols_module_name, *find_module(sols_module_name, [EXAMPLES_PATH]))

    pat_example = re.compile(r'\d+\. .+\.py')
    attrs = {}

    for i, example_path in enumerate(Path(EXAMPLES_PATH).iterdir()):
        if not re.match(pat_example, example_path.name):
            continue
        module_name = example_path.stem
        if int(module_name.split('. ')[0]) in SKIPPED_EXAMPLES:
            continue
        module_tuple = open(str(example_path), 'rb'), example_path.stem, ('.py', 'rb', PY_SOURCE)

        func_name = module_name.replace(' ', '_').replace('.', '').lower()
        func_name = 'test_' + ''.join(c for c in func_name if c.isalnum() or c == '_')
        attrs[func_name] = get_method(module_name, module_tuple)

    class_name = 'TestByExamples'
    globals()[class_name] = type(class_name, (TestCase,), attrs)


_set_test_class()
del _set_test_class
