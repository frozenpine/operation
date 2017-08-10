from yaml import YAMLError, dump, load

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


def Load(path, **kwargs):
    try:
        src = open(path)
    except IOError, err:
        print err
    else:
        try:
            data = load(src, Loader=Loader, **kwargs)
        except YAMLError, err:
            print err
        else:
            return data


def Dump(data, **kwargs):
    return dump(data, Dumper=Dumper, default_flow_style=False, **kwargs)
