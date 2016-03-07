from __future__ import unicode_literals
import six


def create_tag(name, args=None, klass=[], id_=''):
    """

    Shortcut to create the contents of an open XML tag.
    :param str name:
    :param dict(str:str) args:
    :param list(str) klass:
    :param str id_:
    :return str:
    """
    result = name

    if args is None:
        args = {}

    # Add classes defined using dot syntax.
    if klass:
        lst = args.setdefault('class', [])
        lst += klass

    # Override "id" by the one defined using hash syntax.
    if id_:
        args['id'] = id_

    # Format tag arguments in alphabetical order.
    for i_name, i_value in sorted(args.items()):
        # Name without value
        if i_value is True:
            result += ' {}'.format(i_name)
            continue

        # List values: join with spaces
        if isinstance(i_value, list):
            value = ' '.join(i_value)
        else:
            value = i_value

        # Quote value
        if isinstance(value, six.text_type) and not (value.startswith("'") and value.endswith("'")):
            value = '"' + value + '"'
        result += ' {}={}'.format(i_name, value)

    return result
