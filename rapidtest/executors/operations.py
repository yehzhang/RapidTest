class Operation(object):
    def __init__(self, name=None, args=(), collect=False):
        """
        :param str|None name: name of function
        :param (any, ...) args:
        :param bool collect:
        """
        self.name = name
        self.args = args
        self.collect = collect

    def __str__(self):
        repr_output = ' -> ?' if self.collect else ''
        return self.format(self.name or '?', self.args, repr_output)

    @classmethod
    def format(cls, func_name, args, repr_output):
        repr_args = ', '.join(map(repr, args))
        return '{}({}){}'.format(func_name, repr_args, repr_output)

    def __eq__(self, other):
        """For testing. """
        return isinstance(other, type(
            self)) and self.name == other.name and self.args == other.args and self.collect == \
                                                                               other.collect


class Operations(object):
    def __init__(self, init_args, operations, **kwargs):
        self.init_args = init_args
        self.operations = operations
        self.params = kwargs

    def __iter__(self):
        return iter(self.operations)

    def __len__(self):
        return len(self.operations)

    def __eq__(self, other):
        """For testing. """
        return isinstance(other, type(self)) and self.init_args == other.init_args and len(
            self) == len(other) and all(s == o for s, o in zip(self, other))
