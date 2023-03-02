import re

from .singleton import singleton


@singleton
class Makefile:

    def __init__(self, path):
        self.path = path
        self.makefile = None
        self.UPROGS = None
        self._UPROGS = None
        self.reset()

    def reset(self):
        with open(self.path) as f:
            self.makefile = f.read()
        self.UPROGS = re.search("UPROGS *=(?:.*\\\\\n)*", self.makefile).group().split("\n")
        self._UPROGS = set(self.UPROGS[1:-1])

    def add_UPROGS(self, *args):
        for f in args:
            self._UPROGS.add(f"\t$U/_{re.sub('.c$', '', f)}\\")

    def remove_UPROGS(self, *args):
        for f in args:
            self._UPROGS.remove(f"\t$U/_{re.sub('.c$', '', f)}\\")

    def update_UPROGS(self):
        if self._UPROGS != set(self.UPROGS[1:-1]):
            with open(self.path, 'w') as f:
                f.write(self.makefile.replace(
                    "\n".join(self.UPROGS),
                    "\n".join([self.UPROGS[0], *self._UPROGS, self.UPROGS[-1]])
                ))
            return True
        else:
            return False

    def update(self):
        return self.update_UPROGS()
