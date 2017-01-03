import re
from os import path, mkdir, listdir
from shutil import rmtree, copytree
from string import Template
from tempfile import mkdtemp

from ..common_executors import CompiledExecutor
from ..rpc.exceptions import MSG_CANNOT_GUESS_METHOD


class JavaExecutor(CompiledExecutor):
    SRC_PATH = './src'
    LIB_DIR = 'lib'
    PKG_DIR = 'execution'
    OUT_DIR = 'out'
    ENTRY_CLASS = 'Main'

    PKG_PATTERN = re.compile(r'\s*package\b')

    # Must in PACKAGE
    TEMPLATE_TARGETS = 'StaticConfig.java',

    COMMAND_COMPILE = 'javac -d "{out_path}" -cp "{src_path}:{lib_path}/*" {src_files} {args}'
    COMMAND_RUN = 'java -cp "{out_path}:{lib_path}/*" {entry_point} {args}'

    def __init__(self, target, target_name=None):
        super(JavaExecutor, self).__init__(target, target_name)

        # Validate target_name
        target_name_from_file, _, _ = self.target_filename.rpartition('.')
        if target_name is None:
            self.target_name = target_name_from_file
        else:
            if target_name_from_file != target_name:
                raise ValueError(
                    'Java class name {} does not corresponds to its filename {}'.format(
                        target_name, target_name_from_file))

        self.src_path = path.join(path.dirname(__file__), self.SRC_PATH)
        self.temp_working_directory = None
        self.temp_package_path = None
        self.temp_lib_path = None
        self.temp_out_path = None

    def prepare_external_target(self, socket_address):
        # Move files to a temp directory
        self.temp_working_directory = mkdtemp()
        self.temp_package_path = self._copy_src_dir(self.PKG_DIR)
        self.temp_lib_path = self._copy_src_dir(self.LIB_DIR)
        self._copy_target()

        # Replacement templates
        for t in self.TEMPLATE_TARGETS:
            self._replace_template(t)

        super(JavaExecutor, self).prepare_external_target(socket_address)

    def close(self):
        super(JavaExecutor, self).close()

        # Release prepared temp files
        if self.temp_working_directory is not None:
            rmtree(self.temp_working_directory)
            self.temp_working_directory = None

    def _copy_src_dir(self, src_dir):
        src = path.join(self.src_path, src_dir)
        dest = path.join(self.temp_working_directory, src_dir)
        copytree(src, dest)
        return dest

    def _copy_target(self):
        with open(self.target_path) as fin:
            content = fin.read()

        if self.PKG_PATTERN.match(content) is not None:
            raise ValueError('Cannot execute target that belongs to a package')

        with open(path.join(self.temp_package_path, self.target_filename), 'w') as fout:
            fout.write('package {};\n'.format(self.PKG_DIR))
            fout.write(content)

    def _replace_template(self, filename):
        template_path = path.join(self.temp_package_path, '{}.template'.format(filename))
        with open(template_path, 'r') as fin:
            template = fin.read()

        content = Template(template).substitute(
            target_name=self.target_name,
            method_hello=self.client.METHOD_HELLO,
            method_execute=self.client.METHOD_EXECUTE,
            method_terminate=self.client.METHOD_TERMINATE,
            host_name=self.client.addr[0],
            host_port=self.client.addr[1],
            target_id=self.curr_target_id,
            exc_msg_guess_method=MSG_CANNOT_GUESS_METHOD)

        output_path = path.join(self.temp_package_path, filename)
        with open(output_path, 'w') as fout:
            fout.write(content)

    def get_compile_command(self):
        self.temp_out_path = path.join(self.temp_working_directory, self.OUT_DIR)
        mkdir(self.temp_out_path)

        filenames = ('"{}"'.format(path.join(self.temp_package_path, p)) for p in
                     listdir(self.temp_package_path) if p.endswith('.java'))

        return self.COMMAND_COMPILE.format(
            out_path=self.temp_out_path,
            src_path=self.temp_package_path,
            lib_path=self.temp_lib_path,
            src_files=' '.join(filenames),
            args=self.compiler_options or '')

    def get_run_command(self):
        return self.COMMAND_RUN.format(
            out_path=self.temp_out_path,
            lib_path=self.temp_lib_path,
            entry_point='.'.join([self.PKG_DIR, self.ENTRY_CLASS]),
            args=self.running_options or '')


class Java8Executor(JavaExecutor):
    ENVIRONMENT = 'Java8'
