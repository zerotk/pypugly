# coding: UTF-8
from __future__ import unicode_literals
from pypugly.tag import create_tag


def test_tag():
    assert create_tag('alpha') == 'alpha'
    assert create_tag('alpha', id_='id_alpha') == 'alpha id="id_alpha"'
    assert create_tag('alpha', klass=['zulu', 'zebra']) == 'alpha class="zulu zebra"'
