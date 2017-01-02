import re
from os import path
from shutil import rmtree, copytree
from string import Template
from tempfile import mkdtemp

from ..common_executors import CompiledExecutor


class JavaExecutor(CompiledExecutor):
    SRC_PATH = './src'
    PACKAGE = 'execution'
    LIB_DIR = 'lib'
    ENTRY_POINT = 'Main'

    PKG_PATTERN = re.compile(r'\s*package\b')

    # Must in PACKAGE
    TEMPLATES = 'StaticConfig.java',

    def __init__(self, target, target_name=None):
        super(JavaExecutor, self).__init__(target, target_name)

        # Validate target_name
        target_name_from_file, _, _ = self.target_filename.rpartition('.')
        if target_name is not None:
            if target_name_from_file != target_name:
                raise ValueError('target_name {} does not corresponds to filename {}'.format(
                    target_name, target_name_from_file))

        self.src_path = path.join(path.dirname(__file__), self.SRC_PATH)
        self.temp_package_path = None
        self.temp_path = None

    def prepare_external(self, socket_address):
        # Move files to a temp directory
        self.temp_path = mkdtemp()
        self.temp_package_path = self._copy_src_dir(self.PACKAGE)
        self._copy_src_dir(self.LIB_DIR)
        self.compiling_path = path.join(self.temp_package_path, '{}.java'.format(self.ENTRY_POINT))
        self._copy_target()

        # Replacement templates
        for t in self.TEMPLATES:
            self._replace_template(t)

        return super(JavaExecutor, self).prepare_external(socket_address)

    def close(self):
        super(JavaExecutor, self).close()

        # Release prepared temp files
        if self.temp_path is not None:
            rmtree(self.temp_path)
            self.temp_path = None

    def _copy_src_dir(self, src_dir):
        src = path.join(self.src_path, src_dir)
        dest = path.join(self.temp_path, src_dir)
        copytree(src, dest)
        return dest

    def _copy_target(self):
        with open(self.target_path) as fin:
            content = fin.read()

        if self.PKG_PATTERN.match(content) is not None:
            raise ValueError('Cannot execute target that belongs to a package')

        with open(self.compiling_path, 'w') as fout:
            fout.write('package {};\n'.format(self.PACKAGE))
            fout.write(content)

    def _replace_template(self, filename):
        with open(path.join(self.temp_package_path, filename), 'r+') as f:
            template = f.read()
            content = Template(template).substitute(
                target_name=self.target_name,
                method_execute=self.client.METHOD_EXECUTE,
                method_terminate=self.client.METHOD_TERMINATE,
                host_name=self.client.addr[0],
                host_port=self.client.addr[1],
                target_id=self.curr_target_id)

            f.seek(0)
            f.write(content)
            f.truncate()


class Java8Executor(JavaExecutor):
    ENVIRONMENT = 'Java8'
