from __future__ import print_function

from collections import deque
from sys import stdout

from .utils import super_len
from .cases import Case


class Test(object):
    """Manage cases, run them, and print results.

    :param type target: same as the keyword argument 'target' of the Case class
    :param kwargs: same as those of the Case class
    """

    def __init__(self, target=None, **kwargs):
        self._current_session = None
        self._pending_sessions = deque([])
        self.passed_cases = []
        self.failed_cases = []
        self.unborn_cases = 0

        self.closed = False

        if target is not None:
            kwargs[Case.BIND_TARGET_CLASS] = target
        self.bound_params = Case.process_params(**kwargs)

    def __del__(self):
        self.close()

    def __enter__(self):
        if Case.current_test:
            raise RuntimeError('There is already a test running')
        Case.current_test = self
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        Case.current_test = None
        self.run()
        self.close()

    def __call__(self, *args, **kwargs):
        """Call self.add_generator() on behalf of user.
        Should be used as a decorator.

        :param kwargs: keyword arguments passed to add_generator()
        """
        # type_err_msg = (
        #     'Test object is a shortcut for calling add_generator if used as a decorator. The '
        #     'test-generating function decorated will be passed to add_generator when @t is used, '
        #     'or passed preceding other arguments when @t(*args, **kwargs) is used. '
        #     'Check the method signature of add_generator to see what arguments are taken. ')

        if len(args) == 1 and callable(args[0]) and not kwargs:
            # Used like @self
            [f] = args
            self.add_generator(f)
            return f

        else:
            # Used like @self(100), @self(repeat=100), etc
            def _d(f):
                self.add_generator(f, *args, **kwargs)
                return f

            return _d

    def add_generator(self, generator, repeat=100):
        """
        :param generator: a test-generating function that takes an index and returns a case
        :param int repeat: how many times to run the test-generating function, if provided
        """
        if not callable(generator):
            raise TypeError('generator is not a function')
        if not isinstance(repeat, int):
            raise TypeError('repeat is not an integer')
        if repeat > 0:
            self.separate()
            self._add_generator(generator(i) for i in range(repeat))

    def add_case(self, case):
        """Add a case to be run when run() is called next time."""
        self._initialize(case)

        if self._current_session is None:
            s = self._current_session = []
            self._pending_sessions.append(iter(s))
        self._current_session.append(case)

    def add_cases(self, cases):
        if isinstance(cases, (list, tuple)):
            # not a generator. Do not lazy-evaluate for validating params immediately
            for case in cases:
                self.add_case(case)
        else:
            # probably a generator, using lazy-evaluation
            self._add_generator(iter(cases))
            self.separate()

    def _add_generator(self, gen):
        """Add a iterable of cases which are lazy-evaluated."""
        gen_cases = (self._initialize(case) for case in gen)
        self._pending_sessions.append(iter(gen_cases))

    def separate(self):
        """Separate a set of individual cases from another one."""
        self._current_session = None

    def _initialize(self, case):
        """Called to initialize a case."""
        if not isinstance(case, Case):
            raise TypeError('case is not of type Case')
        case.initialize(self.bound_params)
        return case

    def run(self):
        """Run all pending cases."""
        self._run_sessions()

    def _run_sessions(self):
        """Cases are already initialized at this time."""
        self.closed = False

        while self._pending_sessions:
            session = self._pending_sessions.popleft()
            last_unborn_cases = self.unborn_cases

            try:
                self._run_cases(session)
            except Exception:
                if self.unborn_cases == last_unborn_cases:
                    # iterator did not raise an exception. It is the case.run()
                    self._pending_sessions.appendleft(session)
                raise

    def _run_cases(self, cases):
        """
        :param iterator cases:
        """
        has_print = False

        try:
            while True:
                try:
                    case = next(cases)
                except StopIteration:
                    break
                except Exception:
                    print('?', end='')
                    stdout.flush()
                    has_print = True

                    self.unborn_cases += 1
                    raise

                success = False

                try:
                    success = case.run()
                finally:
                    symbol = '.' if success else 'x'
                    print(symbol, end='')
                    stdout.flush()
                    has_print = True

                    (self.passed_cases if success else self.failed_cases).append(case)

                if not success:
                    raise ValueError(str(case))
        finally:
            if has_print:
                print()
                stdout.flush()

    def close(self):
        if not self.closed:
            self.print_stats()
            self.closed = True

    def print_stats(self):
        if self.unborn_cases:
            return

        try:
            cnt_pending_cases = sum(map(super_len, self._pending_sessions))
        except Exception:
            return
        if cnt_pending_cases:
            print('Leaving {} pending cases'.format(cnt_pending_cases))
        elif self.passed_cases:
            if not self.failed_cases:
                print('Passed all {} test cases'.format(len(self.passed_cases)))
        else:
            print('No case was tested')
        stdout.flush()
