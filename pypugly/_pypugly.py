from __future__ import unicode_literals, print_function

import os

import six
from zerotk.easyfs import GetFileContents, GetFileLines, IsFile
from zerotk.easyfs._exceptions import FileNotFoundError
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
        """

        :param str name:
            The function name.
        :param list(tuple(str,str) parameters:
            List of parameters names and default values.
        :param ??? code:
        :return:
        """
        self.name = name
        self.parameters = parameters
        self.code = code

    def format_arguments(self, arguments):
        """
        Returns a dictionary with the arguments. Obtain arguments names from
        the function parameter.

        It handles positional and keywords arguments. It also handles default
        parameter values.

        :param list result:
            ?
        :return dict(str, object):
        """
        args = []
        kwargs = {}
        for i_argument in arguments:
            if isinstance(i_argument, tuple) and len(i_argument) == 2:
                kwargs[i_argument[0]] = i_argument[1]
            else:
                args.append(i_argument)

        result = {}
        for i, (i_parameter_name, i_default_value) in enumerate(self.parameters):
            try:
                arg = kwargs[i_parameter_name]
            except KeyError:
                try:
                    arg = args.pop(0)
                except IndexError:
                    if i_default_value is not None:
                        arg = i_default_value
                    else:
                        arg = ''
            result[i_parameter_name] = literal_eval(arg)

        return result


class HtmlGenerator(object):

    def __init__(self, include_paths):
        self.HANDLERS = {
            LineToken.LINE_TYPE_ROOT: self.handle_root,
            LineToken.LINE_TYPE_COMMENT: self.handle_comment,
            LineToken.LINE_TYPE_CODE: self.handle_code,
            LineToken.LINE_TYPE_DJANGO: self.handle_django,
            LineToken.LINE_TYPE_TAG: self.handle_tag,
            LineToken.LINE_TYPE_CALL: self.handle_call,
        }
        # Code variables (for now, later it will be more complex... with IFs
        # and FORs and expand_vars...
        self.functions = {}
        self.variables = {}
        self.include_paths = include_paths

        from pypugly.peg_parser import PegParser
        self.__parser = PegParser()

    def generate(self, line_token):
        """
        Generates HTML from a line_token (tree).

        :param LineToken line_token:
        :return str:
        """
        lines = self._handle_line_token(line_token, self.variables)
        return '\n'.join(lines)

    def _handle_line_token(self, t, context):
        handler = self.HANDLERS.get(t.line_type)
        assert \
            handler is not None, \
            'No handler for token of type "{}"'.format(t.line_type)

        try:
            result = handler(t, after=False, context=context)
            result += self._handle_children(t.children, context=context)
            result += handler(t, after=True, context=context)
        except Exception as e:
            reraise(e, 'While handling line-token {}'.format(six.text_type(t)))
        return result

    def _handle_children(self, children, context):
        result = []
        for i_child in children:
            result += self._handle_line_token(i_child, context=context)
        return result

    def handle_root(self, token, after, context):
        return []

    def handle_code(self, token, after, context):
        if after:
            return []

        code = self.__parser.parse_code(token.line)
        code_class = code.__class__.__name__

        if code_class == 'Assignment':
            self.variables[six.text_type(code.left)] = literal_eval(code.right)
        elif code_class == 'Def':
            self.functions[six.text_type(code.name)] = \
                Function(code.name, code.parameters, token.children)
            token.children = []
            return []
        elif code_class == 'Include':
            filename = self._eval(code.filename)
            parser = PugParser()
            input_contents = GetFileContents(self._find_file(filename))
            token_tree = parser.tokenize(input_contents)
            return self._handle_line_token(token_tree, self.variables)

        elif code_class == 'ForLoop':
            return [token.indentation + repr(code)]

        return []

    def handle_call(self, token, after, context):
        if after:
            return []

        # Parse function call...
        code = self.__parser.parse_call(token.line)

        # Obtain the associated function
        function = self.functions.get(six.text_type(code.name))
        assert function is not None

        # Prepare arguments
        arguments = function.format_arguments(code.arguments)

        # Prepare context for the function call, adding the global variables
        # and argument values
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
        return []

    def handle_tag(self, token, after, context):

        # Parses the TAG line, extracting the id, classes, arguments and the
        # contents.
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
                result.append(
                    token.indentation + '</{name}>'.format(
                        name=tag.name
                    )
                )
        else:
            args = getattr(tag, 'args', [])
            args = {
                i.key: self._eval(getattr(i, 'value', 'True'))
                for i in args
            }
            tag_text = create_tag(
                tag.name,
                args,
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
                content = self._eval(tag.content)
                line += content + end_tag

            result.append(line)

        return result

    def _eval(self, literal):
        """
        Evaluates a literal.

        For now, we evaluate only text (unicode) or boolean values
        (True/False).

        :param str literal:
        :return object:
        """
        try:
            result = literal_eval(literal)
            if isinstance(result, bytes):
                result = result.decode('UTF-8')
            if isinstance(result, six.text_type):
                result = result.format(**self.variables)
            return result
        except Exception as e:
            reraise(e, 'While evaluation literal: "{}"'.format(literal))

    def _find_file(self, filename):
        filenames = []
        for i_include_path in self.include_paths:
            filenames.append(i_include_path + '/' + filename)

        for i_filename in filenames:
            if IsFile(i_filename):
                return i_filename

        raise FileNotFoundError(filename)


def generate(filename, include_paths=()):
    """
    Creates and HTML from the given PyPUGly filename.

    :param str filename:
    :param list(str) include_paths:
    :return str:
    """
    from pypugly._pypugly import PugParser, HtmlGenerator

    parser = PugParser()
    input_contents = GetFileContents(filename)
    token_tree = parser.tokenize(input_contents)
    generator = HtmlGenerator([os.path.dirname(filename)] + list(include_paths))
    return generator.generate(token_tree)
