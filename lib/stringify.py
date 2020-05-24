def stringify(value):
    if type(value) is int:
        return str(value)

    if type(value) is float:
        return str(value)

    if type(value) is str:
        return value

    if value is None:
        return "nil"

    if value is True:
        return "true"

    if value is False:
        return "false"

    from lib.function import Function
    from lib.klass import Klass, Instance

    if (
        isinstance(value, Function)
        or isinstance(value, Klass)
        or isinstance(value, Instance)
    ):
        return value.to_str()

    raise ValueError("[stringify] cannot stringify value [%s]" % value)


def stringify_type(type):
    if type == None.__class__:
        return "nil"

    if type is bool:
        return "bool"

    if type in (int, float):
        return "number"

    if type is str:
        return "string"

    raise ValueError("[stringify] cannot stringify type [%s]" % type)


def stringify_types(types):
    return unique_list(map(stringify_type, types))


def unique_list(list):
    result = []
    for x in list:
        if x not in result:
            result.append(x)
    return result
