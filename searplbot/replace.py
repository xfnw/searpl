import re


class MultiReplace:
    def __init__(self, rep):
        self.r = {re.escape(k): v for k, v in rep.items()}
        self.p = re.compile("|".join(self.r.keys()))

    def replace(self, inp):
        return self.p.sub(lambda x: self.r[x.group(0)], inp)
