

def create_tag(name, args=[], klass=[], id_=''):
    """

    Shortcut to create the contents of an open XML tag.
    :param str name:
    :param list(str) args:
    :param list(str) klass:
    :param str id_:
    :return str:
    """
    result = name

    # Convert args (list of Argument token) into a dictionary.
    args = {i.key: i.value for i in args}

    # Add classes defined using dot syntax.
    if klass:
        lst = args.setdefault('class', [])
        lst += klass

    # Override "id" by the one defined using hash syntax.
    if id_:
        args['id'] = id_

    # Format tag arguments in alphabetical order.
    for i_name, i_value in sorted(args.items()):
        if isinstance(i_value, list):
            value = ' '.join(i_value)
        else:
            value = i_value
        # Quote value
        if not (value.startswith("'") and value.endswith("'")):
            value = '"' + value + '"'
        result += ' {}={}'.format(i_name, value)

    return result
