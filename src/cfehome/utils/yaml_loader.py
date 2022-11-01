import yaml
from yaml import dump as _dump

try:
    from yaml import CDumper as Dumper
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Dumper, Loader


def dump(*args, **kwargs):
    return _dump(*args, **kwargs, Dumper=Dumper)


def load(content):
    return yaml.safe_load(str(content))
