from __future__ import unicode_literals, print_function
from pypugly.peg_parser import PegParser


def test_parse_tag():
    parser = PegParser()

    f = parser.parse_tag("tag")
    assert str(f) == '''tag'''
    assert not hasattr(f, 'args')

    f = parser.parse_tag("tag()")
    assert str(f) == '''tag'''
    assert len(f.args) == 0

    f = parser.parse_tag("tag(a=alpha, b=2, c='charlie')")
    assert str(f) == '''tag'''
    assert len(f.args) == 3
    arg1 = f.args[0]
    assert arg1.key == 'a'
    assert arg1.value == 'alpha'
    arg1 = f.args[1]
    assert arg1.key == 'b'
    assert arg1.value == '2'
    arg1 = f.args[2]
    assert arg1.key == 'c'
    assert arg1.value == "'charlie'"

    f = parser.parse_tag("tag.cls1()")
    assert str(f) == '''tag.cls1'''
    assert f.classes == ['cls1']
    assert f.id is None
    assert len(f.args) == 0

    f = parser.parse_tag("tag.cls1.cls2()")
    assert str(f) == '''tag.cls1.cls2'''
    assert f.classes == ['cls1', 'cls2']
    assert f.id is None
    assert len(f.args) == 0

    f = parser.parse_tag("tag#id1()")
    assert str(f) == '''tag#id1'''
    assert f.classes == []
    assert f.id == 'id1'
    assert len(f.args) == 0

    f = parser.parse_tag("tag.cls1.cls2#id1()")
    assert str(f) == '''tag.cls1.cls2#id1'''
    assert f.classes == ['cls1', 'cls2']
    assert f.id == 'id1'
    assert len(f.args) == 0


def test_parse_code():
    parser = PegParser()

    f = parser.parse_code("var alpha = 'bravo'")
    assert f.__class__.__name__ == 'Assignment'
    assert f.left == 'alpha'
    assert f.right == '\'bravo\''
    assert str(f) == '''assign(alpha, 'bravo')'''

    f = parser.parse_code("for i in 10:")
    assert f.__class__.__name__ == 'ForLoop'
    assert f.var == 'i'
    assert f.iterator == '10'
    assert str(f) == '''forloop(i, 10)'''

    f = parser.parse_code("def alpha(bravo, charlie)")
    assert f.__class__.__name__ == 'Def'
    assert f.name == 'alpha'
    assert f.parameters == [('bravo', None), ('charlie', None)]


def test_parse_call():
    parser = PegParser()

    f = parser.parse_call("function(alpha, bravo, charlie)")
    assert f.__class__.__name__ == 'Call'
    assert f.name == 'function'
    assert f.arguments == ['alpha', 'bravo', 'charlie']

    f = parser.parse_call("function('Alpha', 1)")
    assert f.__class__.__name__ == 'Call'
    assert f.name == 'function'
    assert f.arguments == ["'Alpha'", '1']

    f = parser.parse_call("function(1, bravo=2, charlie=3)")
    assert f.__class__.__name__ == 'Call'
    assert f.name == 'function'
    assert f.arguments == ['1', ('bravo', '2'), ('charlie', '3')]


def test_parse_django():
    parser = PegParser()

    f = parser.parse_django("include alpha.html")
    assert f.__class__.__name__ == 'Django'
    assert f.name == 'include'
    assert f.restline == 'alpha.html'

    f = parser.parse_django("include alpha.html bravo charlie.html delta=object.pk")
    assert f.__class__.__name__ == 'Django'
    assert f.name == 'include'
    assert f.restline == 'alpha.html bravo charlie.html delta=object.pk'
