from .peg_parser import parse_tag


def test_parse_tag():
    f = parse_tag("tag")
    assert str(f) == '''tag'''
    assert not hasattr(f, 'args')

    f = parse_tag("tag()")
    assert str(f) == '''tag'''
    assert len(f.args) == 0

    f = parse_tag("tag(a=alpha, b=2, c='charlie')")
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

    f = parse_tag("tag.cls1()")
    assert str(f) == '''tag.cls1'''
    assert f.classes == ['cls1']
    assert f.id is None
    assert len(f.args) == 0

    f = parse_tag("tag.cls1.cls2()")
    assert str(f) == '''tag.cls1.cls2'''
    assert f.classes == ['cls1', 'cls2']
    assert f.id is None
    assert len(f.args) == 0

    f = parse_tag("tag#id1()")
    assert str(f) == '''tag#id1'''
    assert f.classes == []
    assert f.id == 'id1'
    assert len(f.args) == 0

    f = parse_tag("tag.cls1.cls2#id1()")
    assert str(f) == '''tag.cls1.cls2#id1'''
    assert f.classes == ['cls1', 'cls2']
    assert f.id == 'id1'
    assert len(f.args) == 0
