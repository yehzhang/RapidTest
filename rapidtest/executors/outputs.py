from .operations import Operation
from ..utils import sentinel


class Output(object):
    def __str__(self):
        raise NotImplementedError

    def check(self, val):
        """Check equality of val against output

        :return bool:
        """
        raise NotImplementedError

    def get_val(self):
        """Do not check. Simply return the value of output. """
        raise NotImplementedError


class OperationOutput(Output):
    def __init__(self, func_name, args, collect, val=sentinel):
        """
        :param str func_name: name of function from target to be called. Ignored if target is
            Runnable
        :param (any, ...) args: arguments to be called with
        :param bool collect: whether returned value of this operation is collected or not
        :param any val: returned value of this operation. Required iff collect is True
        """
        self.func_name = func_name
        self.args = args
        self.collect = collect
        if collect:
            if val is sentinel:
                raise RuntimeError('Operation output is collected but val is not specified')
            self.val = val
            self.asserted_val = sentinel
            self.result = None

    def __str__(self):
        if self.collect:
            if self.asserted_val is sentinel:
                repr_comp = '?'
            else:
                repr_comp = '√' if self.result else '!= {}'.format(repr(self.asserted_val))
            repr_output = ' -> {} {}'.format(repr(self.val), repr_comp)
        else:
            repr_output = ''
        return Operation.format(self.func_name, self.args, repr_output)

    def get_val(self):
        if not self.collect:
            raise RuntimeError('Returned value was not collected')
        return self.val

    def check(self, asserted_val):
        val = self.get_val()
        self.asserted_val = asserted_val
        self.result = val == self.asserted_val
        return self.result


class ExecutionOutput(Output):
    MAX_ENT_LNS = 4
    ABBR_ENTS = '...'

    def __init__(self, outputs):
        """
        :param iterable outputs: an iterable of Output
        """
        self._checked_outputs = []
        self._pending_outputs = iter(outputs)
        self.result = None

    def __str__(self):
        """String representation of current state of result."""
        entries = []

        if self.result is None:
            entries.append('output has not been completely checked: ')

            # Populate _checked_outputs with entries to be displayed
            for _ in zip(range(self.MAX_ENT_LNS + 1), self):
                pass

            ents = self._checked_outputs
            trim_bottom = True

        elif self.result is False:
            entries.append('output differs: ')

            # Display until failure
            i_end = len(self._checked_outputs)
            for i, o in enumerate(self._checked_outputs, 1):
                if o.collect and not o.result:
                    i_end = i
                    break

            ents = self._checked_outputs[:i_end]
            trim_bottom = False

        else:  # self.result is True
            entries.append('output equals: ')

            ents = self._checked_outputs
            trim_bottom = False

        if ents:
            # Abbreviate outputs if there are too many
            if len(ents) > self.MAX_ENT_LNS:
                if trim_bottom:
                    i_start = 0
                    i_end = self.MAX_ENT_LNS
                    i_abbr = -1
                else:  # trim_top
                    i_end = len(ents)
                    i_start = i_end - self.MAX_ENT_LNS
                    i_abbr = 0
                ents = ents[i_start:i_end]
                ents[i_abbr] = self.ABBR_ENTS

            entries.append('\n' + '\n'.join('{}{}'.format(' ' * 4, e) for e in ents))
        else:
            entries.append('no operations')

        return ''.join(entries)

    def __iter__(self):
        """Iterate through all outputs."""
        i = 0

        while True:
            while i < len(self._checked_outputs):
                yield self._checked_outputs[i]
                i += 1
            try:
                o = next(self._pending_outputs)
            except StopIteration:
                break
            self._checked_outputs.append(o)

    def check(self, asserted_vals):
        self.result = None

        # assert len(asserted_vals) == len(total outputs)
        q_vals = iter(asserted_vals)
        for o in self:
            if o.collect:
                asserted_val = next(q_vals)
                if not o.check(asserted_val):
                    self.result = False
                    break
        else:
            self.result = True

        return self.result

    def get_val(self):
        return (o.get_val() for o in self if o.collect)
