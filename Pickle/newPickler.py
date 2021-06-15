from __future__ import print_function

import copyreg
import dis
import io
import itertools
import opcode
import pickle
import sys
import types
import typing
import weakref
from _pickle import Pickler
from collections import ChainMap

DEFAULT_PROTOCOL = pickle.HIGHEST_PROTOCOL

_extract_code_globals_cache = weakref.WeakKeyDictionary()


STORE_GLOBAL = opcode.opmap["STORE_GLOBAL"]
DELETE_GLOBAL = opcode.opmap["DELETE_GLOBAL"]
LOAD_GLOBAL = opcode.opmap["LOAD_GLOBAL"]
GLOBAL_OPS = (STORE_GLOBAL, DELETE_GLOBAL, LOAD_GLOBAL)
HAVE_ARGUMENT = dis.HAVE_ARGUMENT
EXTENDED_ARG = dis.EXTENDED_ARG

_BUILTIN_TYPE_NAMES = {}
for k, v in types.__dict__.items():
    if type(v) is type:
        _BUILTIN_TYPE_NAMES[v] = k


def dump(obj, file, protocol=None, buffer_callback=None):
    BetterPickler(file, protocol=protocol, buffer_callback=buffer_callback).dump(obj)


def dumps(obj, protocol=None, buffer_callback=None):
    with io.BytesIO() as file:
        cp = BetterPickler(file, protocol=protocol, buffer_callback=buffer_callback)
        cp.dump(obj)
        return file.getvalue()


load, loads = pickle.load, pickle.loads


def _function_getstate(func):  # забор полей из ф-и
    slotstate = {
        "__name__": func.__name__,
        "__qualname__": func.__qualname__,
        "__annotations__": func.__annotations__,
        "__kwdefaults__": func.__kwdefaults__,
        "__defaults__": func.__defaults__,
        "__module__": func.__module__,
        "__doc__": func.__doc__,
        "__closure__": func.__closure__,
    }

    f_globals_ref = _extract_code_globals(func.__code__)
    f_globals = {k: func.__globals__[k] for k in f_globals_ref if k in func.__globals__}

    closure_values = list(map(func.__closure__)) if func.__closure__ is not None else ()
    slotstate["_cloudpickle_submodules"] = _find_imported_submodules(
        func.__code__, itertools.chain(f_globals.values(), closure_values)
    )
    slotstate["__globals__"] = f_globals

    state = func.__dict__
    return state, slotstate


def _find_imported_submodules(code, top_level_dependencies):  # находит подмодули ф-и
    subimports = []
    for x in top_level_dependencies:
        if (
            isinstance(x, types.ModuleType)
            and hasattr(x, "__package__")
            and x.__package__
        ):
            prefix = x.__name__ + "."
            for name in list(sys.modules):
                if name is not None and name.startswith(prefix):
                    tokens = set(name[len(prefix) :].split("."))
                    if not tokens - set(code.co_names):
                        subimports.append(sys.modules[name])
    return subimports


def _extract_code_globals(co):  # забор кода из глобалсов ф-и
    out_names = _extract_code_globals_cache.get(co)
    if out_names is None:
        names = co.co_names
        out_names = {names[oparg] for _, oparg in _walk_global_ops(co)}
        if co.co_consts:
            for const in co.co_consts:
                if isinstance(const, types.CodeType):
                    out_names |= _extract_code_globals(const)

        _extract_code_globals_cache[co] = out_names

    return out_names


def _walk_global_ops(code):
    for instr in dis.get_instructions(code):
        op = instr.opcode
        if op in GLOBAL_OPS:
            yield op, instr.arg


def _code_reduce(obj):  # забор полей из кода ф-и
    if hasattr(obj, "co_posonlyargcount"):  # pragma: no branch
        args = (
            obj.co_argcount,
            obj.co_posonlyargcount,
            obj.co_kwonlyargcount,
            obj.co_nlocals,
            obj.co_stacksize,
            obj.co_flags,
            obj.co_code,
            obj.co_consts,
            obj.co_names,
            obj.co_varnames,
            obj.co_filename,
            obj.co_name,
            obj.co_firstlineno,
            obj.co_lnotab,
            obj.co_freevars,
            obj.co_cellvars,
        )
    else:
        args = (
            obj.co_argcount,
            obj.co_kwonlyargcount,
            obj.co_nlocals,
            obj.co_stacksize,
            obj.co_flags,
            obj.co_code,
            obj.co_consts,
            obj.co_names,
            obj.co_varnames,
            obj.co_filename,
            obj.co_name,
            obj.co_firstlineno,
            obj.co_lnotab,
            obj.co_freevars,
            obj.co_cellvars,
        )
    return types.CodeType, args


def _function_setstate(obj, state):
    state, slotstate = state
    obj.__dict__.update(state)

    obj_globals = slotstate.pop("__globals__")
    obj_closure = slotstate.pop("__closure__")

    slotstate.pop("_cloudpickle_submodules")

    obj.__globals__.update(obj_globals)
    obj.__globals__["__builtins__"] = __builtins__  # с лямбдами

    for k, v in slotstate.items():
        setattr(obj, k, v)


def _class_reduce(obj):  # нахождение базового типа класса, уменьшение до него
    if obj is type(None):
        return type, (None,)
    elif obj in _BUILTIN_TYPE_NAMES:
        return _builtin_type, (_BUILTIN_TYPE_NAMES[obj],)
    return NotImplemented


def _builtin_type(name):
    if name == "ClassType":
        return type
    return getattr(types, name)


def _is_importable(obj, name=None):  # проверка является ли ф-я динамической
    if isinstance(obj, types.FunctionType):
        return _lookup_module_and_qualname(obj, name=name) is not None
    elif issubclass(type(obj), type):
        return _lookup_module_and_qualname(obj, name=name) is not None
    elif isinstance(obj, types.ModuleType):
        return obj.__name__ in sys.modules
    else:
        raise TypeError(
            "cannot check importability of {} instances".format(type(obj).__name__)
        )


def _lookup_module_and_qualname(obj, name=None):  # если и ф-и имя и модуль
    if name is None:
        name = getattr(obj, "__qualname__", None)
    if name is None:
        name = getattr(obj, "__name__", None)

    module_name = _whichmodule(obj, name)

    if module_name is None:
        return None

    if module_name == "__main__":
        return None

    module = sys.modules.get(module_name, None)
    if module is None:
        return None

    try:
        obj2, parent = pickle._getattribute(module, name)
    except AttributeError:
        return None
    if obj2 is not obj:
        return None
    return module, name


def _whichmodule(obj, name):  # какому модулю пренадлежит
    if sys.version_info[:2] < (3, 7) and isinstance(obj, typing.TypeVar):
        module_name = None
    else:
        module_name = getattr(obj, "__module__", None)

    if module_name is not None:
        return module_name
    for module_name, module in sys.modules.copy().items():
        if (
            module_name == "__main__"
            or module is None
            or not isinstance(module, types.ModuleType)
        ):
            continue
        try:
            if pickle._getattribute(module, name)[0] is obj:
                return module_name
        except Exception:
            pass
    return None


class BetterPickler(Pickler):
    _dispatch_table = {}
    _dispatch_table[types.CodeType] = _code_reduce

    dispatch_table = ChainMap(_dispatch_table, copyreg.dispatch_table)

    def _dynamic_function_reduce(self, func):
        newargs = self._function_getnewargs(func)
        state = _function_getstate(func)
        return (types.FunctionType, newargs, state, None, None, _function_setstate)

    def _function_reduce(self, obj):
        if _is_importable(obj):
            return NotImplemented
        else:
            return self._dynamic_function_reduce(obj)

    def _function_getnewargs(self, func):
        code = func.__code__

        base_globals = self.globals_ref.setdefault(id(func.__globals__), {})

        if base_globals == {}:
            for k in ["__package__", "__name__", "__path__", "__file__"]:
                if k in func.__globals__:
                    base_globals[k] = func.__globals__[k]

        if func.__closure__ is None:
            closure = None

        return code, base_globals, None, None, closure

    def dump(self, obj):
        try:
            return Pickler.dump(self, obj)
        except RuntimeError as e:
            if "recursion" in e.args[0]:
                msg = (
                    "Could not pickle object as excessively deep recursion " "required."
                )
                raise pickle.PicklingError(msg) from e
            else:
                raise

    dispatch = dispatch_table

    def __init__(self, file, protocol=None, buffer_callback=None):
        if protocol is None:
            protocol = DEFAULT_PROTOCOL
        Pickler.__init__(self, file, protocol=protocol, buffer_callback=buffer_callback)
        self.globals_ref = {}
        self.proto = int(protocol)

    def reducer_override(self, obj):  # определяет какой уменьшитель исспользовать

        t = type(obj)
        try:
            is_anyclass = issubclass(t, type)
        except TypeError:
            is_anyclass = False

        if is_anyclass:
            return _class_reduce(obj)
        elif isinstance(obj, types.FunctionType):
            return self._function_reduce(obj)
        else:
            return NotImplemented
