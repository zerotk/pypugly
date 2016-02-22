from __future__ import unicode_literals, print_function
import pytest
from zerotk.easyfs import CreateFile, GetFileContents


@pytest.mark.parametrize('basename', ['smoke_test', 'var', 'def', 'django'])
def test_parser(embed_data, basename):
    input_filename = embed_data[basename + '.lang']
    obtained_filename = embed_data[basename + '.obtained.html']
    expected_filename = embed_data[basename + '.html']
    CreateFile(obtained_filename, generate(input_filename))
    embed_data.assert_equal_files(obtained_filename, expected_filename)


def generate(filename):
    from pypugly._pypugly import PugParser, HtmlGenerator

    parser = PugParser()
    input_contents = GetFileContents(filename)
    token_tree = parser.tokenize(input_contents)
    generator = HtmlGenerator()
    return generator.generate(token_tree)
