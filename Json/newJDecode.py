import types
import re


def str_deserialize(jstr=str):
    value = jstr[1:-1]
    return value


def int_deserialize(jstr=str):
    return int(jstr)


def float_deserialize(jstr=str):
    return float(jstr)


def none_deserialize(jstr=str):
    return None


def bool_deserialize(jstr=str):
    if jstr == 'true':
        return True
    return False


def bytes_deserialize(jstr=str):
    if len(jstr) == 3:
        return bytes()
    jstr = jstr[1:]
    str_values = jstr[1:-1].split(', ')
    int_values = []
    for i in str_values:
        int_values.append(int(i))
    return bytes(bytearray(int_values))


def module_deserialize(jstr=str):
    jstr = jstr[7:-1]
    try:
        return __import__(jstr)
    except ModuleNotFoundError:
        raise ImportError(jstr + " not found")


def list_deserialize(jstr=str):
    counter = 0
    border_start_counter = 0
    border_end_counter = 0
    begin = 0
    end = 0
    border_start_symbol = ''
    border_end_symbol = ''
    value = []
    if len(jstr) == 2:
        return value
    jstr = jstr[1:-1]
    for i in jstr:
        if (i == '[' or i == '{') and border_start_symbol == '':
            border_start_symbol = i
            if border_start_symbol == '[':
                border_end_symbol = ']'
            else:
                border_end_symbol = '}'
        if border_start_symbol != '':
            if i == border_start_symbol:
                border_start_counter = 1 + border_start_counter
            if i == border_end_symbol:
                border_end_counter = 1 + border_end_counter
        if border_start_counter == border_end_counter and i == ',':
            end = counter
            value.append(choose_deserializer(jstr[begin:end]))
            begin = counter + 2
            border_start_symbol = ''
            border_end_symbol = ''
        counter = counter+1
    value.append(choose_deserializer(jstr[begin:counter]))
    return value


def dict_deserialize(jstr=str):#
    value = dict()
    if len(jstr) == 2:
        return value
    keys = []
    items = []
    jstr = jstr[1:-1]
    counter = 0
    border_start_counter = 0
    border_end_counter = 0
    border_start_symbol = ''
    border_end_symbol = ''

    find_key = re.search(r'".+?":', jstr)
    while find_key != None:
        keys.append(find_key.group(0)[1:-2])
        jstr = jstr[find_key.end() + 1:]
        for i in jstr:
            if (i == '[' or i == '{') and border_start_symbol == '':
                border_start_symbol = i
                if border_start_symbol == '[':
                    border_end_symbol = ']'
                else:
                    border_end_symbol = '}'
            if border_start_symbol != '':
                if i == border_start_symbol:
                    border_start_counter = 1 + border_start_counter
                if i == border_end_symbol:
                    border_end_counter = 1 + border_end_counter
            if border_start_counter == border_end_counter and i == ',':
                end = counter
                items.append(jstr[:end])
                border_start_symbol = ''
                border_end_symbol = ''
                jstr = jstr[end+2:]
                break
            counter = counter + 1
        counter = 0
        if i == jstr[-1]:
            break
        find_key = re.search(r'".+?":', jstr)
    jstr = jstr.replace('\t', '')  #
    if jstr[-1] == '\n':
        items.append(jstr[:-1])
    else:
        items.append(jstr)
    for i in range(len(keys)):
        value[keys[i]] = choose_deserializer(items[i])

    return value


def globals_deserialize(jstr=str):#
    values = dict_deserialize(jstr)
    return values


def code_deserialize(jstr=str):
    values = dict_deserialize(jstr)
    return types.CodeType(values['co_argcount'],
                          values['co_posonlyargcount'],
                          values['co_kwonlyargcount'],
                          values['co_nlocals'],
                          values['co_stacksize'],
                          values['co_flags'],
                          values['co_code'],
                          tuple(values['co_consts']),
                          tuple(values['co_names']),
                          tuple(values['co_varnames']),
                          values['co_filename'],
                          values['co_name'],
                          values['co_firstlineno'],
                          values['co_lnotab'],
                          tuple(values['co_freevars']),
                          tuple(values['co_cellvars']))


def func_deserialize(jstr=str):
    values = dict_deserialize(jstr)
    if values["__defaults__"] == None:
        return types.FunctionType(values["__code__"],
                                  values["__globals__"],
                                  values["__name__"],
                                  values["__defaults__"],
                                  values["__closure__"])
    else:
        return types.FunctionType(values["__code__"],
                                values["__globals__"],
                                values["__name__"],
                                tuple(values["__defaults__"]),
                                values["__closure__"])


def class_deserialize(jstr=str):
    values = dict_deserialize(jstr)
    values.pop("myjson_type")
    class_name = values["__name__"]
    values.pop("__name__")
    base = tuple(values["__bases__"])
    values.pop("__bases__")
    return type(class_name, base, values)


def choose_deserializer(jstr=str):
    if jstr[0] == '{':
        try_to_type = re.match(r'{\n?(\t+)?"myjson_type": ".+",', jstr)#
        if try_to_type != None:
            current_type = re.split(r' ', try_to_type.group(0))[1][1:-2]
            if current_type == 'function':
                return func_deserialize(jstr)
            if current_type == 'class':
                return class_deserialize(jstr)
            if current_type == 'code':
                return code_deserialize(jstr)
            if current_type == 'globals':
                return globals_deserialize(jstr)
        return dict_deserialize(jstr)
    if jstr[0] == 'd':
        return bytes_deserialize(jstr)
    if jstr[0] == '[':
        return list_deserialize(jstr)
    if jstr[0] == 'm':
        return module_deserialize(jstr)
    if jstr[0] == '"':
        return str_deserialize(jstr)
    else:
        if is_digit(jstr):
            if jstr.isdigit():
                return int_deserialize(jstr)
            else:
                return float_deserialize(jstr)
        if jstr == 'true' or jstr == 'false':
            return bool_deserialize(jstr)
        if jstr == 'null':
            return none_deserialize(jstr)


def is_digit(string):
    if string.isdigit():
       return True
    else:
        try:
            float(string)
            return True
        except ValueError:
            return False


def loads(jstr=str):
    value = choose_deserializer(jstr)
    return value


def load(file_name = str):
    try:
        with open(file_name, 'r') as file:
            jstr = file.read()
    except FileNotFoundError:
        return None
    value = choose_deserializer(jstr)
    return value