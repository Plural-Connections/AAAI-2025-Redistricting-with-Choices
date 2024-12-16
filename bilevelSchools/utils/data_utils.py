import os, argparse, json, yaml, pickle

def loadYaml(path):
    with open(path, 'r') as stream:
        data = yaml.safe_load(stream)
    return data

def loadJson(path):
    with open(path) as file:
        data = json.load(file)
    return data

def saveJson(data, path):
    with open(path, "w") as file:
        json.dump(data, file, indent = 4)

def loadPickle(path):
    with open(path, 'rb') as file:
        data = pickle.load(file)
    return data

def savePickle(data, path):
    with open(path, 'wb') as file:
        pickle.dump(data, file)

def checkDir(*dirs):
    for s_dir in dirs:
        if not os.path.isdir(s_dir):
            os.makedirs(s_dir)

def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ("yes", "true", "t", "y", "1"):
        return True
    elif v.lower() in ("no", "false", "f", "n", "0"):
        return False
    else:
        raise argparse.ArgumentTypeError("Boolean value expected.")


def print_key_msg(s = ''):
    print('------------------------------ {}'.format(s))


def rebuild_list_with_idx(l, l_idx):

    return [
        l[i_idx]
        for i_idx in l_idx
    ]

def get_idx_equal(l, val):

    return [
        i
        for i in range(len(l))
        if l[i] == val
    ]