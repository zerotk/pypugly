from __future__ import unicode_literals, print_function
from zerotk.reraiseit import reraise

from pypugly.tag import create_tag
from ast import literal_eval



class LineToken(object):

    class EmptyToken(RuntimeError):
        pass

    INDENTATION = 4

    LINE_TYPE_ROOT = 'ROOT'
    LINE_TYPE_TAG = 'TAG'
    LINE_TYPE_CODE = 'CODE'
    LINE_TYPE_DJANGO = 'DJANGO'
    LINE_TYPE_COMMENT = 'COMMENT'
    LINE_TYPE_CALL = 'CALL'
    _LINE_TYPE_VALIDS = {
        '-': LINE_TYPE_CODE,
        '%': LINE_TYPE_DJANGO,
        '#': LINE_TYPE_COMMENT,
        '+': LINE_TYPE_CALL,
    }

    def __init__(self, line):
        self.indent, self.line_type, self.line = self._parse_line(line)
        self.children = []
        self.line_no = 0

    def _parse_line(self, line):
        if line == self.LINE_TYPE_ROOT:
            return 0, self.LINE_TYPE_ROOT, ''

        indent = len(line)
        line = line.lstrip()
        indent = int((indent - len(line)) / self.INDENTATION)

        if not line:
            raise LineToken.EmptyToken

        line_type = self._LINE_TYPE_VALIDS.get(line[0])
        if line_type:
            line = line[1:]
        else:
            line_type = self.LINE_TYPE_TAG

        return indent, line_type, line

    def __repr__(self):
        return '<{}:{} {}>'.format(self.__class__.__name__, self.line_type, self.line)

    @property
    def indentation(self):
        return ' ' * self.INDENTATION * self.indent


class PugParser(object):

    INDENT = '>>>'
    DEDENT = '<<<'

    def tokenize(self, text):

        def preprocess_text(txt):
            return txt.replace('\t', '    ').replace('\r', '')

        context = self.ParseContext()
        text = preprocess_text(text)
        for i, i_line in enumerate(text.split('\n')):
            assert len(context.current_token) > 0, 'Sanity check!'

            try:
                line_token = LineToken(i_line)
                line_token.line_no = i + 1
                context.build_tree(line_token)
            except LineToken.EmptyToken:
                pass

        return context.current_token[0]

    class ParseContext(object):

        def __init__(self):
            self.current_token = [LineToken(LineToken.LINE_TYPE_ROOT)]
            self.current_indent = 0

        def build_tree(self, token):
            # Handle token tree building.
            delta = token.indent - self.current_indent
            if delta > 0:
                assert delta == 1, 'Single indents (%s chars) only.' % LineToken.INDENTATION
            elif delta < 0:
                self.current_token.pop()
                for i in range(-delta):
                    self.current_token.pop()
            else:
                if len(self.current_token) > 1:
                    self.current_token.pop()
            parent = self.current_token[-1]
            parent.children.append(token)
            self.current_token.append(token)
            self.current_indent = token.indent


class Function(object):

    def __init__(self, name, parameters, code):
        self.name = name
        self.parameters = parameters
        self.code = code

    def format_arguments(self, arguments):
        """
        Returns a dictionary with the arguments. Obtain missing arguments names from the function parameter definition.

        :return dict(str, object):
        """
        result = {}
        for i_parameter, i_argument in zip(self.parameters, arguments):
            if isinstance(i_argument, tuple) and len(i_argument) == 2:
                key = i_argument[0]
                value = i_argument[1]
            else:
                key = i_parameter[0]
                value = i_argument or i_parameter[1]
            value = literal_eval(value)
            result[key] = value
        return result


class HtmlGenerator(object):

    def __init__(self):
        self.HANDLERS = {
            LineToken.LINE_TYPE_ROOT: self.handle_root,
            LineToken.LINE_TYPE_COMMENT: self.handle_comment,
            LineToken.LINE_TYPE_CODE: self.handle_code,
            LineToken.LINE_TYPE_DJANGO: self.handle_django,
            LineToken.LINE_TYPE_TAG: self.handle_tag,
            LineToken.LINE_TYPE_CALL: self.handle_call,
        }
        # Code variables (for now, later it will be more complex... with IFs and FORs and expand_vars...
        self.functions = {}
        self.variables = {}

        from pypugly.peg_parser import PegParser
        self.__parser = PegParser()

    def handle_root(self, token, after, context):
        return []

    def handle_code(self, token, after, context):
        if after:
            return []

        code = self.__parser.parse_code(token.line)
        code_class = code.__class__.__name__

        if code_class == 'Assignment':
            self.variables[str(code.left)] = literal_eval(code.right)
        elif code_class == 'Def':
            self.functions[str(code.name)] = Function(code.name, code.parameters, token.children)
            token.children = []
            return []
        elif code_class == 'ForLoop':
            return [token.indentation + repr(code)]

        return []

    def handle_call(self, token, after, context):
        if after:
            return []

        # Parse function call...
        code = self.__parser.parse_call(token.line)

        # Obtain the associated function
        function = self.functions.get(str(code.name))
        assert function is not None

        # Prepare arguments
        arguments = function.format_arguments(code.arguments)

        # Prepare context for the function call, adding the global variables and argument values
        context = self.variables
        context.update(arguments)

        # Call the function 'code'
        tokens = function.code[:]

        # Replaces the code indent with the function call indent.
        for i in tokens:
            i.indent -= 1

        return self._handle_children(tokens, context=context)

    def handle_django(self, token, after, context):

        if after:
            if not token.children:
                return []
            code = self.__parser.parse_django(token.line)
            end_tag = code.name
            end_tag = '{% end' + end_tag.strip() + ' %}'
            return [token.indentation + end_tag]
        else:
            code = self.__parser.parse_django(token.line)
            start_tag = code.name + ' ' + code.restline
            start_tag = '{% ' + start_tag.strip() + ' %}'
            return [token.indentation + start_tag]

    def handle_comment(self, token, after, context):
        if after:
            return []
        return [repr(token)]

    def handle_tag(self, token, after, context):

        def get_content(tag):
            result = literal_eval(tag.content)
            return result.format(**self.variables)

        # Parses the TAG line, extracting the id, classes, arguments and the contents.
        try:
            tag = self.__parser.parse_tag(token.line)
        except Exception as e:
            reraise(e, 'While parsing tag in line %d' % token.line_no)
            raise

        result = []

        have_content = hasattr(tag, 'content') and tag.content
        have_children = len(token.children) > 0

        if have_content and have_children:
            raise RuntimeError('A tag should have contents OR children nodes.')

        if after:
            if not have_content and have_children:
                result.append(token.indentation + '</{name}>'.format(name=tag.name))
        else:
            tag_text = create_tag(
                tag.name,
                getattr(tag, 'args', []),
                klass=tag.classes,
                id_=tag.id
            )
            if have_content or have_children:
                tag_format = '<{}>'
            else:
                tag_format = '<{} />'
            line = token.indentation + tag_format.format(tag_text)

            if have_content:
                # With content, close the tag in the same line.
                end_tag = '</{}>'.format(tag.name)
                content = get_content(tag)
                line += content + end_tag

            result.append(line)

        return result

    def generate(self, line_token):
        lines = self._handle_line_token(line_token, self.variables)
        return '\n'.join(lines)

    def _handle_line_token(self, t, context):
        handler = self.HANDLERS.get(t.line_type)
        assert handler is not None, 'No handler for token of type "{}"'.format(t.line_type)

        result = handler(t, after=False, context=context)
        result += self._handle_children(t.children, context=context)
        result += handler(t, after=True, context=context)
        return result

    def _handle_children(self, children, context):
        result = []
        for i_child in children:
            result += self._handle_line_token(i_child, context=context)
        return result
