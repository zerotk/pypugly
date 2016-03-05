from __future__ import unicode_literals, print_function
from pypeg2 import *

number = re.compile(r"\d+")
symbol = re.compile(r"\w+")
single_quote_string = re.compile(r"'((?:[^'\\]|\\')*)'")


class Argument(object):
    grammar = attr('key', Symbol), optional('=', attr('value', [number, symbol, single_quote_string]))


class Arguments(List):
    grammar = optional(csl([Argument]))


class Parameter(object):
    grammar = attr('key', Symbol), optional('=', attr('value', [number, symbol, single_quote_string]))


class Parameters(List):
    grammar = optional(csl([Parameter]))


class Assignment(object):
    grammar = 'var', attr('left', Symbol), '=', attr('right', [Symbol, single_quote_string])

    def __repr__(self):
        return 'assign({}, {})'.format(self.left, self.right)


class ForLoop(object):
    grammar = 'for', attr('var', Symbol), 'in', attr('iterator', Symbol), ':'

    def __repr__(self):
        return 'forloop({}, {})'.format(self.var, self.iterator)


class Def(object):
    grammar = 'def', name(), '(', attr('_parameters', Parameters), ')'

    @property
    def parameters(self):
        return [(i.key.name, getattr(i, 'value', None)) for i in self._parameters]


class CallArgument(object):
    grammar = attr(
        'value',
        [
            single_quote_string,
            number,
            (
                symbol,
                optional('=', [number, symbol, single_quote_string])
            )
        ]
    )


class CallArguments(List):
    grammar = optional(csl([CallArgument]))


class Call(object):
    grammar = name(), '(', attr('_arguments', CallArguments), ')'

    @property
    def arguments(self):
        result = []
        for i in self._arguments:
            value = i.value
            if isinstance(value, list):
                if len(value) == 1:
                    value = value[0]
                else:
                    value = tuple(value)
            result.append(value)
        return result


class Tag(List):

    grammar = (
        name(),
        attr('classes', maybe_some(('.', word))),
        attr('id', optional(('#', word))),
        optional('(', attr('args', Arguments), ')'),
        attr('content', restline),
        endl
    )

    def __repr__(self):
        result = self.name
        if self.classes:
            result += ''.join(['.{}'.format(i) for i in sorted(self.classes)])
        if self.id:
            result += '#{}'.format(self.id)
        if self.content:
            result += ' ...'
        return result


class Django(str):
    grammar = name(), attr('restline', restline)


class Include(object):
    grammar = 'include', attr('filename', single_quote_string)


class PegParser(object):
    """
    This class implements the parser interface for PyPUGly.

    Once the returning values are standardized one can implement the parser using another technology such as PLY.
    """

    def parse_tag(self, text):
        result = parse(text, Tag)
        return result

    def parse_code(self, text):
        result = parse(text, [Def, ForLoop, Assignment, Include])
        return result

    def parse_call(self, text):
        result = parse(text, Call)
        return result

    def parse_django(self, text):
        result = parse(text, Django)
        return result
