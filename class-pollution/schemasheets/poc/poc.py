import random
import logging
from typing import Union, List, Any

def ensure_path_tokens(path: Union[str, List[str]]) -> List[str]:
    if isinstance(path, list):
        return path
    if "." in path:
        return path.split(".")
    return [path]


def get_attr_via_path_accessor(obj: Union[dict], path: Union[str, List[str]]) -> Any:
    """
    Given an object and a path, return the value at the end of the path

    :param obj: object
    :param path: path
    :return: value
    """
    toks = ensure_path_tokens(path)
    tok = toks[0]
    toks = toks[1:]
    if isinstance(obj, dict):
        v = obj.get(tok, None)
    else:
        # https://github.com/linkml/linkml/issues/971
        v = getattr(obj, tok, None)
    if v and toks:
        return get_attr_via_path_accessor(v, toks)
    else:
        return v


def set_attr_via_path_accessor(obj: Union[dict], path: Union[str, List[str]], value: Any, depth=0) -> None:
    """
    Given an object, a path, and a value, set the value at the end of the path

    :param obj: object
    :param path: path
    :param value: value
    :param depth: recursion depth
    :return: None
    """
    toks = ensure_path_tokens(path)
    tok = toks[0]
    toks = toks[1:]
    logging.debug(f"[{depth}] Setting attr {tok} / {toks} in {obj} to {value}")
    if isinstance(obj, dict):
        if not toks:
            obj[tok] = value
        else:
            if tok not in obj:
                obj[tok] = {}
                logging.info(f"Creating empty dict for: {tok}")
            set_attr_via_path_accessor(obj[tok], toks, value, depth+1)
    else:
        if not toks:
            setattr(obj, tok, value)
        else:
            if not hasattr(obj, tok):
                setattr(obj, tok, {})
            set_attr_via_path_accessor(getattr(obj, tok), toks, value, depth+1)


class Animal:
  def __init__(self, typ, age):
      self.type = typ
      self.age = age
      self.id = random.randint(1, 99999)
      

obj = Animal('cat', 11)
addr = ["__init__", "__globals__", "__name__"]
set_attr_via_path_accessor(obj, addr, 'polluted')

print(__name__)