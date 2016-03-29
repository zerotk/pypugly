from __future__ import unicode_literals, print_function

from pytest import xfail

from zerotk.text import dedent


@xfail('This is a work in progress.')
def test_plyplus_parse():
    from pypugly.plyplus_parser import grammar

    input_text = dedent(
        '''
            html
        '''
    )
    assert unicode(grammar.parse(input_text)) == (
        """start("""
        """tag(name(u'html'))"""
        """)"""
    )

    input_text = dedent(
        '''
            html
                head
        '''
    )
    assert unicode(grammar.parse(input_text)) == (
        "start("
        "tag(name(u'html'), suite(tag(name(u'head')))))"
    )

    input_text = dedent(
        '''
            html
                head
                    title "TITLE"
        '''
    )
    assert unicode(grammar.parse(input_text)) == (
        "start("
        """tag(name(u'html'), suite(tag(name(u'head'), """
        """suite(tag(name(u'title'), string(u'"TITLE"')))))"""
        """))"""
    )

    input_text = dedent(
        '''
            html
                head
                title "TITLE"
        '''
    )
    assert unicode(grammar.parse(input_text)) == (
        "start("
        """tag(name(u'html'), suite(tag(name(u'head'), """
        """suite(tag(name(u'title'), string(u'"TITLE"')))))"""
        """))"""
    )

    input_text = dedent(
        '''
            html
                head
                    title "title"
                body
                    h1 "header"
                    p "contents"
        '''
    )
    assert unicode(grammar.parse(input_text)) == (
        "start("
        "tag(name(u'html')), "
        "tag(name(u'head')), "
        r"""tag(name(u'title'), string(u'"title"')), """
        "tag(name(u'body')), "
        """tag(name(u'h1'), string(u'"header"')), """
        """tag(name(u'p'), string(u'"contents"'))"""
        ")"
    )
