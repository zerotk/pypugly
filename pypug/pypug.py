from pypug import peg_parser
from reraiseit import reraise


class LineToken(object):

    class EmptyToken(RuntimeError):
        pass

    INDENTATION = 4

    LINE_TYPE_ROOT = 'ROOT'
    LINE_TYPE_TAG = 'TAG'
    LINE_TYPE_CODE = 'CODE'
    LINE_TYPE_DJANGO = 'DJANGO'
    LINE_TYPE_COMMENT = 'COMMENT'
    _LINE_TYPE_VALIDS = {
        '-': LINE_TYPE_CODE,
        '%': LINE_TYPE_DJANGO,
        '#': LINE_TYPE_COMMENT,
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

        def preprocess_text(text):
            return text.replace('\t', '    ').replace('\r', '')

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


class HtmlGenerator(object):

    def __init__(self):
        self.HANDLERS = {
            LineToken.LINE_TYPE_ROOT: self.handle_root,
            LineToken.LINE_TYPE_COMMENT: self.handle_comment,
            LineToken.LINE_TYPE_CODE: self.handle_code,
            LineToken.LINE_TYPE_DJANGO: self.handle_django,
            LineToken.LINE_TYPE_COMMENT: self.handle_comment,
            LineToken.LINE_TYPE_TAG: self.handle_tag,
        }

    def handle_root(self, token, after=False):
        return []

    def handle_comment(self, token, after=False):
        if after:
            return []
        return [repr(token)]

    def handle_code(self, token, after=False):
        if after:
            return []
        return ['(CODE)' + repr(token)]

    def handle_django(self, token, after=False):
        if after:
            return []
        return ['(DJANGO)' + repr(token)]

    def handle_comment(self, token, after=False):
        if after:
            return []
        return [repr(token)]

    def handle_tag(self, token, after=False):
        from zerotk.tag import create_tag

        # Parses the TAG line, extracting the id, classes, arguments and the contents.
        try:
            tag = peg_parser.parse_tag(token.line)
        except Exception as e:
            reraise(e, 'While parsing tag in line %d' % token.line_no)

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
                line += tag.content + end_tag

            result.append(line)

        return result

    def generate(self, line_token):

        def _handle(result, t):
            handler = self.HANDLERS.get(t.line_type)
            assert handler is not None, 'No handler for token of type "{}"'.format(t.line_type)
            result += handler(t, after=False)
            for i_child in t.children:
                _handle(result, i_child)
            result += handler(t, after=True)

        result = []
        _handle(result, line_token)

        return '\n'.join(result)
