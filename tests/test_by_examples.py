import re
from imp import load_module, find_module, PY_SOURCE
from unittest import TestCase

from pathlib import Path


def _load_module(name, file, pathname, description):
    load_module(name, file, pathname, description)
    if file:
        file.close()


def ClassFactory(class_name):
    def get_method(module_name, module_tuple):
        def _test(self):
            _load_module(module_name, *module_tuple)

        return _test

    SKIPPED_EXAMPLES = {472, 473, 477}

    sols_module_name = 'solutions'
    _load_module(sols_module_name, *find_module(sols_module_name, ['../examples']))

    pat_example = re.compile(r'\d+\. .+\.py')
    attrs = {}

    for i, example_path in enumerate(Path('../examples').iterdir()):
        if not re.match(pat_example, example_path.name):
            continue
        module_name = example_path.stem
        if int(module_name.split('. ')[0]) in SKIPPED_EXAMPLES:
            continue
        module_tuple = open(str(example_path), 'rb'), example_path.stem, ('.py', 'rb', PY_SOURCE)

        func_name = module_name.replace(' ', '_').replace('.', '')
        func_name = 'test_' + ''.join(c for c in func_name.lower() if c.isalnum() or c == '_')
        attrs[func_name] = get_method(module_name, module_tuple)

    return type(class_name, (TestCase,), attrs)


class_name = 'TestByExamples'
globals()[class_name] = ClassFactory(class_name)
