from yaml import dump as _dump
from yaml import load as _load

try:
    from yaml import CDumper as Dumper
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Dumper, Loader


def dump(*args, **kwargs):
    return _dump(*args, **kwargs, Dumper=Dumper)


def load(*args, **kwargs):
    return _load(*args, **kwargs, Loader=Loader)
