import dis
import sys
from types import CodeType
from typing import Iterator

CALL_FLOW = '[CALL FLOW]'

def _code_objects(code: CodeType) -> Iterator[CodeType]:
    """Iterate over all code objects in `code`."""
    stack = [code]
    while stack:
        code = stack.pop()
        for c in code.co_consts:
            if isinstance(c, CodeType):
                stack.append(c)
        yield code


def _analyze_calls(code: CodeType):
    """Analyze the call flow in a code object."""
    call_graph = {}

    for sub_code in _code_objects(code):
        call_graph[sub_code.co_name] = []

        for instr in dis.Bytecode(sub_code):
            if instr.opname in {"LOAD_GLOBAL", "LOAD_ATTR", "LOAD_METHOD"}:
                call_graph[sub_code.co_name].append(f"{instr.argrepr}")

    return call_graph


def _getattribute(obj, name):
    parent = None
    for subpath in name.split('.'):
        if subpath == '<locals>':
            raise AttributeError("Can't get local attribute {!r} on {!r}"
                                 .format(name, obj))
        try:
            parent = obj
            obj = getattr(obj, subpath)
        except AttributeError:
            raise AttributeError("Can't get attribute {!r} on {!r}"
                                 .format(name, obj)) from None
    return obj, parent


def call_flow(raw_global, proto):
    module, name = raw_global
    __import__(module, level=0)
    if proto >= 4:
        attr = _getattribute(sys.modules[module], name)[0]
    else:
        attr = getattr(sys.modules[module], name)
    return _analyze_calls(attr.__code__)

