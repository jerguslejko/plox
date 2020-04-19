def stringify_type(type):
    if type == None.__class__:
        return "nil"

    if type is bool:
        return "bool"

    if type in (int, float):
        return "number"

    if type is str:
        return "string"

    raise ValueError("[stringify] cannot stringify [%s]" % type)


def stringify_types(types):
    return unique_list(map(stringify_type, types))


def unique_list(list):
    result = []
    for x in list:
        if x not in result:
            result.append(x)
    return result
