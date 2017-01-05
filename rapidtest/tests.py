from __future__ import print_function

from collections import deque
from sys import stdout

from .cases import Case


class Test(object):
    """Manage each case, run it, and print its result.

    Use cases:
        Test a solution that finds the median of numbers from two sorted arrays:
        # content of solution.py
        # class Solution(object):
        #     def findMedianSortedArrays(self, nums1, nums2):
        #         '''
        #         :type nums1: List[int]
        #         :type nums2: List[int]
        #         :rtype: float
        #         '''
        #         # code here

        >>> from rapidtest import Test, Case
        >>> from solution import Solution
        >>>
        >>> with Test(Solution):
        ...     Case([1, 3], [2], result=2.0)
        ...     Case([1, 2], [3, 4], result=2.5)
        ...
        ..
        Passed all 2 test cases


        >>> from statistics import median
        >>> from rapidtest import randints
        >>>
        >>> with Test(Solution) as test:
        ...     @test
        ...     def random_numbers(i):
        ...         '''
        ...         :param int i: number of times this function is called starting from 0
        ...         :return Case:
        ...         '''
        ...         nums1 = sorted(randints(count=i, max_num=i * 100))
        ...         nums2 = sorted(randints(count=max(i, 1), max_num=i * 100))
        ...         result = float(median(nums1 + nums2))
        ...         return Case(nums1, nums2, result=result)
        ...
        ....................................................................................................
        Passed all 100 test cases

    :param target: same as the keyword argument 'target' of the Case class
    :param kwargs: same as those of the Case class
    """
    _context_stack = []

    EXIT_PASS = 0
    EXIT_FAIL = 1
    EXIT_PENDING = 2
    EXIT_EMPTY = 3
    EXIT_GEN_ERR = 4
    EXIT_UNKNOWN = -1

    def __init__(self, target=None, **kwargs):
        self._current_session = None
        self._pending_sessions = deque([])
        self.passed_cases = []
        self.failed_cases = []
        self.unborn_cases = 0

        self.closed = False

        if target is not None:
            kwargs[Case.BIND_EXECUTOR_STUB] = target
        self.bound_params = Case.preprocess_params(**kwargs)

    def __del__(self):
        self.close()

    def __enter__(self):
        if Case.current_test is not None:
            self._context_stack.append(Case.current_test)
        Case.current_test = self
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        Case.current_test = None
        try:
            self.run()
        finally:
            self.close()
            Case.current_test, = self._context_stack[-1:] or None,

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
            # Called like @self
            [f] = args
            self.add_func(f)
            return f

        else:
            # Called like @self(100), @self(repeat=100), etc
            def _d(f):
                self.add_func(f, *args, **kwargs)
                return f

            return _d

    def add_func(self, generator, repeat=100):
        """
        :param callable generator: a test-case-generating function that takes an index and
            returns a case
        :param int repeat: how many times to run the test-generating function, if provided
        """
        if not callable(generator):
            raise TypeError('generator is not a function')
        if not isinstance(repeat, int):
            raise TypeError('repeat is not an integer')
        if repeat > 0:
            self._add_generator(generator(i) for i in range(repeat))

    def add_case(self, case):
        """Add a case to be run when run() is called next time."""
        self._initialize(case)

        if self._current_session is None:
            self._current_session = []
            # noinspection PyTypeChecker
            self._pending_sessions.append(iter(self._current_session))
        self._current_session.append(case)

    def add_cases(self, cases):
        """
        :param Iterable[Case] cases:
        """
        for case in cases:
            self.add_case(case)

    def _add_generator(self, gen):
        """Add an iterable of cases which are lazy-evaluated."""
        self.separate()

        gen_cases = (self._initialize(case) for case in gen)
        self._pending_sessions.append(iter(gen_cases))

    def separate(self):
        """Separate a set of individual cases from another one."""
        self._current_session = None

    def _initialize(self, case):
        """Called to _initialize a case."""
        if not isinstance(case, Case):
            raise TypeError('case is not of type Case')
        case._initialize(self.bound_params)
        return case

    def run(self):
        """Run all pending cases."""
        self._run_sessions()

    def _run_sessions(self):
        """Cases are already initialized at this time."""
        self.closed = False
        self.separate()

        while self._pending_sessions:
            session = self._pending_sessions.popleft()
            last_unborn_cases = self.unborn_cases

            try:
                self._run_cases(session)
            except:
                # If case generator raises an exception, it is stopped. No need to recycle it
                if self.unborn_cases == last_unborn_cases:
                    # iterator did not raise an exception. It is the case.run()
                    self._pending_sessions.appendleft(session)
                raise

    def _run_cases(self, cases):
        """
        :param iterator cases:
        """
        has_printed = False

        try:
            while True:
                try:
                    case = next(cases)
                except StopIteration:
                    break
                except:
                    print('?', end='')
                    stdout.flush()
                    has_printed = True

                    self.unborn_cases += 1
                    raise

                success = False
                try:
                    success = case.run()
                finally:
                    symbol = '.' if success else 'x'
                    print(symbol, end='')
                    stdout.flush()
                    has_printed = True

                    (self.passed_cases if success else self.failed_cases).append(case)

                if not success:
                    raise ValueError(str(case))
        finally:
            if has_printed:
                print()
                stdout.flush()

    def close(self):
        if not self.closed:
            self.print_summary()
            self.closed = True

    def print_summary(self):
        _, msg = self.summary()
        if msg:
            print(msg)
            stdout.flush()

    def summary(self):
        """
        :return Tuple[int, str]: exit code and description
        """
        if self.unborn_cases:
            return self.EXIT_GEN_ERR, None
        try:
            cnt_pending_cases = 0
            for i in range(len(self._pending_sessions)):
                s = list(self._pending_sessions.popleft())
                cnt_pending_cases += len(s)
                self._pending_sessions.append(iter(s))
        except Exception as e:
            return self.EXIT_GEN_ERR, 'Exception raised when counting pending cases: {}'.format(e)
        if cnt_pending_cases:
            return self.EXIT_PENDING, 'Leaving {} pending cases'.format(cnt_pending_cases)
        if self.failed_cases:
            return self.EXIT_FAIL, None
        if self.passed_cases:
            return self.EXIT_PASS, 'Passed all {} test cases'.format(len(self.passed_cases))
        return self.EXIT_EMPTY, 'No case was tested'
        # return self.EXIT_UNKNOWN, None
