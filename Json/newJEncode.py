import types


def str_serialize(value=str):
    jstr = '"' + value + '"'
    return jstr


def number_serialize(value=int):
    return str(value)


def byte_serialize(value=bytes):
    return 'd'+str(list(bytearray(value)))


def bool_serialize(value=bool):
    if value:
        return 'true'
    return 'false'


def none_serialize(value=None):
    return 'null'


def module_serialize(value=types.ModuleType):
    return 'module'+'"'+value.__name__+'"'


def array_serialize(value=tuple):  #
    jstr = '['
    if len(value) != 0:
        for i in value:
            jstr += swith_type[type(i)](i) + ', '
        jstr = jstr[:-2] + ']'
    else:
        jstr += ']'
    return jstr


def dict_serialize(value=dict):  #
    jstr = '{'
    if len(value) != 0:
        for i in value.keys():
            jstr += '"' + i + '": ' + swith_type[type(value[i])](value[i]) + ', '
        jstr = jstr[:-2] + '}'
    else:
        jstr += '}'
    return jstr


def code_serialize(code=types.CodeType, depth=1, jstr=''):
    jstr += '{\n'
    jstr += '\t' * depth + '"myjson_type": "code",\n'
    for attribute_name in dir(code):
        if not callable(getattr(code, attribute_name)) and attribute_name != '__doc__':
            jstr += '\t' * depth + '"' + attribute_name + '": '
            serialized_value = swith_type[type(getattr(code, attribute_name))](getattr(code, attribute_name))
            jstr += serialized_value + ',\n'
    jstr = jstr[:-2] + jstr[-1:]
    jstr += '\t' * (depth - 1) + "}"
    return jstr


def globals_serialize(func=types.FunctionType, depth=1, jstr=''):
    jstr += '{\n'
    jstr += '\t' * depth + '"myjson_type": "globals",\n'
    if len(func.__code__.co_names) != 0:
        for i in func.__code__.co_names:
            try:
                current_type = type(func.__globals__[i])
                if current_type == type or current_type == types.FunctionType:  #
                    serialized_value = swith_type[type(func.__globals__[i])](func.__globals__[i],
                                                                             depth + 1)
                else:
                    serialized_value = swith_type[type(func.__globals__[i])](func.__globals__[i])
                jstr += '\t' * depth + '"' + i + '": ' + serialized_value + ',\n'
            except KeyError:
                continue
        jstr = jstr[:-2] + jstr[-1:]
        jstr += '\t' * (depth - 1) + '}'
    else:
        jstr = jstr[:-2] + '\n'+'\t' * (depth - 1)+'}'
    return jstr


def func_serialize(func, depth=1, jstr=''):
    jstr += '{\n'
    jstr += '\t' * depth + '"myjson_type": "function",\n'
    for attribute_name in dir(func):
        if not callable(getattr(func, attribute_name)) and attribute_name != '__doc__':
            jstr += '\t' * depth + '"' + attribute_name + '": '
            if attribute_name == '__code__':
                jstr = code_serialize(getattr(func, attribute_name), depth + 1, jstr)
                jstr += ',\n'
                continue
            if attribute_name == '__globals__':
                jstr = globals_serialize(func, depth + 1, jstr)
                jstr += ',\n'
                continue
            current_type = type(getattr(func, attribute_name))
            if current_type == type or current_type == types.FunctionType:  #
                serialized_value = swith_type[type(getattr(func, attribute_name))](getattr(func, attribute_name),
                                                                                    depth + 1)
            else:
                serialized_value = swith_type[type(getattr(func, attribute_name))](getattr(func, attribute_name))
            jstr += serialized_value + ',\n'
    jstr = jstr[:-2] + jstr[-1:]
    jstr += '\t' * (depth - 1) + "}"
    return jstr


def class_serialize(value=type, depth=1, jstr=''):
    jstr += '{\n'#
    jstr += '\t' * depth + '"myjson_type": "class",\n'
    jstr += '\t' * depth + '"__name__": "' + value.__name__ + '",\n'
    jstr += '\t' * depth + '"__bases__": ' + swith_type[type(value.__bases__)](value.__bases__) + ",\n"
    for attribute_name in dir(value):
        if not attribute_name.startswith('__'):
            jstr += '\t' * depth + '"' + attribute_name + '": '
            current_type = type(getattr(value, attribute_name))
            if current_type == type or current_type == types.FunctionType:#
                serialized_value = swith_type[type(getattr(value, attribute_name))](getattr(value, attribute_name),
                                                                                     depth + 1)
            else:
                serialized_value = swith_type[type(getattr(value, attribute_name))](getattr(value, attribute_name))
            jstr += serialized_value + ',\n'
    jstr = jstr[:-2] + jstr[-1:]
    jstr += '\t' * (depth - 1) + "}"
    return jstr


def dumps(obj):
    return swith_type[type(obj)](obj)


def dump(obj, file_name='test.json'):
    with open(file_name, 'w') as file:
        file.write(dumps(obj))


swith_type = {
    int: number_serialize,
    str: str_serialize,
    float: number_serialize,
    tuple: array_serialize,
    list: array_serialize,
    bool: bool_serialize,
    type(None): none_serialize,
    dict: dict_serialize,
    bytes: byte_serialize,
    types.FunctionType: func_serialize,
    type: class_serialize,
    types.ModuleType: module_serialize,
    types.CodeType: code_serialize
}
