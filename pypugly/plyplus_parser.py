from __future__ import unicode_literals
from plyplus import Grammar


grammar = Grammar(r"""
start: element (NEWLINE element)* ;

@element: tag ;

tag: name string? suite? ;

suite: NEWLINE INDENT tag* DEDENT ;

name: '\w+' ;
string: STRING ;

// Don't count on the + to prevent multiple NEWLINE tokens. It's just an
// optimization
NEWLINE: '(\r?\n[\t ]*)+'
    (%newline)
    ;

%fragment QUOTE: '\"' ;
%fragment STRING_INTERNAL: '.*' ;
STRING : QUOTE STRING_INTERNAL QUOTE ;

SPACES: '[ ]+' (%ignore) ;
INDENT: '<INDENT>';
DEDENT: '<DEDENT>';
EOF: '<EOF>';

###
from plyplus.grammars.python_indent_postlex import PythonIndentTracker
self.lexer_postproc = PythonIndentTracker
""")

grammar2 = (
    """
start: (NEWLINE|tag)+;

tag : symbol ;

// Don't count on the + to prevent multiple NEWLINE tokens. It's just an
// optimization
NEWLINE: '(\r?\n[\t ]*)+'
    (%newline)
    ;


string : '"*?(?<!\\)(\\\\)*?"' ;

symbol : NAME ;

null : 'null' ;

suite : tag | NEWLINE INDENT tag+ DEDENT ;


%fragment I: '(?i)';    // Case Insensitive
%fragment QUOTE: '\'' ;
%fragment STRING_INTERNAL: '.*?(?<!\\)(\\\\)*?' ;

NAME: I '[a-z_]\w*(?!r?"|r?\')' ;

STRING : QUOTE '(?!\'\')' STRING_INTERNAL QUOTE ;

WS: '[\t \f]+' (%ignore) ;
LINE_CONT: '\\[\t \f]*\r?\n' (%ignore) (%newline) ;
COMMENT: '\#[^\n]*'(%ignore) ;

INDENT: '<INDENT>' ;
DEDENT: '<DEDENT>' ;
EOF: '<EOF>' ;

###
from plyplus.grammars.python_indent_postlex import PythonIndentTracker
self.lexer_postproc = PythonIndentTracker
""")


# class Transformer(STransformer):
#     """
#     Transforms JSON AST into Python native objects.
#     """
#     number = lambda self, node: float(node.tail[0])
#     string = lambda self, node: node.tail[0][1:-1]
#     boolean = lambda self, node: True if node.tail[0] == 'true' else False
#     null  = lambda self, node: None
#     array = lambda self, node: node.tail
#     pair = lambda self, node: { node.tail[0] : node.tail[1] }
#
#     def object(self, node):
#         result = {}
#         for i in node.tail:
#             result.update(i)
#         return result
#
#
# def pypugly_parse(input_text):
#     """Parses a JSON string into native Python objects."""
#     return Transformer().transform(
#         grammar.parse(input_text)
#     )
