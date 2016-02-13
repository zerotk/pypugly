from pypeg2 import *


number = re.compile(r"\d+")
symbol = re.compile(r"\w+")
literal = re.compile(r"'((?:[^'\\]|\\')*)'")


class KeywordArgument(object):
    grammar = attr('key', Symbol), optional('=', attr('value', [number, symbol, literal]))


class Arguments(List):
    grammar = optional(csl([KeywordArgument]))


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


class Assignment(object):
    grammar = 'var', attr('left', Symbol), '=', attr('right', [Symbol, literal])

    def __repr__(self):
        return 'assign({}, {})'.format(self.left, self.right)


class ForLoop(object):
    grammar = 'for', attr('var', Symbol), 'in', attr('iterator', Symbol), ':'

    def __repr__(self):
        return 'forloop({}, {})'.format(self.var, self.iterator)


def parse_tag(text):
    result = parse(text, Tag)
    return result


def parse_code(text):
    result = parse(text, [ForLoop, Assignment])
    return result
