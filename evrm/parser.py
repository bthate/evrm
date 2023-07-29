# This file is placed in the Public Domain.
#
# pylint: disable=C,I,R


"parser"


def __dir__():
    return (
            "parse",
           )


def parse(self, txt=None) -> None:
    args = []
    self.args = []
    self.cmd = self.cmd or ""
    self.gets = self.gets or {}
    self.mod = self.mod or ""
    self.opts = self.opts or ""
    self.sets = self.sets or {}
    self.otxt = txt or ""
    _nr = -1
    for spli in self.otxt.split():
        if spli.startswith("-"):
            try:
                self.index = int(spli[1:])
            except ValueError:
                self.opts += spli[1:]
            continue
        if "=" in spli:
            key, value = spli.split("=", maxsplit=1)
            if key == "mod":
                self.mod += f",{value}"
                continue
            self.sets[key] = value
            continue
        if "==" in spli:
            key, value = spli.split("==", maxsplit=1)
            self.gets[key] = value
            continue
        _nr += 1
        if _nr == 0:
            self.cmd = spli
            continue
        args.append(spli)
    if args:
        self.args = args
        self.txt = self.cmd or ""
        self.rest = " ".join(self.args)
        self.txt = self.cmd + " " + self.rest
    else:
        self.txt = self.cmd
