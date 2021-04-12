# This file is placed in the Public Domain.

"trace"

import os
import sys
import traceback

def exception(txt="", sep=" | "):
    exctype, excvalue, tb = sys.exc_info()
    trace = traceback.extract_tb(tb)
    result = []
    for elem in trace:
        if "python3" in elem[0] or "<frozen" in elem[0]:
            continue
        res = []
        for x in elem[0].split(os.sep)[::-1]:
            res.append(x)
            if x in ["botl", "botd"," mod"]:
                break
        result.append("%s %s:%s" % (".".join(res[::-1]), elem[2], elem[1]))
    res = "%s | %s: %s" % (sep.join(result), exctype, excvalue)
    exc.append(res)
    del trace
    return res

exc = []