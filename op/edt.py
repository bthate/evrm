# This file is placed in the Public Domain.

"edit"

def edit(o, setter, skip=False):
    try:
        setter = vars(setter)
    except (TypeError, ValueError):
        pass
    if not setter:
        setter = {}
    count = 0
    for key, v in setter.items():
        if skip and v == "":
            continue
        count += 1
        if v in ["True", "true"]:
            o[key] = True
        elif v in ["False", "false"]:
            o[key] = False
        else:
            o[key] = v
    return count

def merge(o, d):
    for k, v in d.items():
        if not v:
            continue
        if k in o:
            if isinstance(o[k], dict):
                continue
            o[k] = o[k] + v
        else:
            o[k] = v

def overlay(o, d, keys=None, skip=None):
    for k, v in d.items():
        if keys and k not in keys:
            continue
        if skip and k in skip:
            continue
        if v:
            o[k] = v
