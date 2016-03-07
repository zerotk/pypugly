from __future__ import unicode_literals, print_function
import pytest
from zerotk.easyfs import CreateFile

from pypugly._pypugly import generate


@pytest.mark.parametrize(
    'basename',
    [
        'smoke_test',
        'var',
        'def',
        'django',
        'def-defaults',
        'include',
        'attrs',
        'unicode',
    ]
)
def test_parser(embed_data, basename):
    input_filename = embed_data[basename + '.lang']
    obtained_filename = embed_data[basename + '.obtained.html']
    expected_filename = embed_data[basename + '.html']
    CreateFile(obtained_filename, generate(input_filename))
    embed_data.assert_equal_files(obtained_filename, expected_filename)


def test_format_arguments():
    from pypugly._pypugly import Function
    f = Function(
        'alpha',
        [('first', None), ('second', "'two'"), ('third', "'three'")],
        None
    )
    assert (
        f.format_arguments(
            ["'alpha'", "'bravo'", "'charlie'"]
        ) == {
            'first': 'alpha',
            'second': 'bravo',
            'third': 'charlie',
        }
    )
    assert (
        f.format_arguments(
            ["'alpha'"]
        ) == {
            'first': 'alpha',
            'second': 'two',
            'third': 'three',
        }
    )
    assert (
        f.format_arguments(
            ["'FIRST'", ('third', "'333'")]
        ) == {
            'first': 'FIRST',
            'second': 'two',
            'third': '333',
        }
    )
