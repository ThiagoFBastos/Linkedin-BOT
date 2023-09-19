from unidecode import unidecode
from random import randrange

class Match:
    def __init__(self, words):
        self._prefix = {}
        self._MOD = 2 ** 61 - 1
        self._P = randrange(2, self._MOD - 2)

        for k, w in enumerate(words):
            h = 0
            for i, c in enumerate(w):
                h = (h * self._P + ord(c)) % self._MOD
                self._prefix[h] = max(self._prefix.get(h, -1), -1 if i < len(w) - 1 else k)

    def get_patterns(self, text):
        text = ' '.join([w for w in unidecode(text).lower().split(' ') if not w.isspace()])

        pat = set()
        L = len(text)
        h = [0] * (L + 1)
        pt = [0] * (L + 1)

        pt[0] = 1

        for i, c in enumerate(text):
            pt[i + 1] = pt[i] * self._P % self._MOD
            h[i + 1] = (h[i] * self._P + ord(c)) % self._MOD

        query = lambda l, r: (h[r + 1] - h[l] * pt[r - l + 1] % self._MOD + self._MOD) % self._MOD

        hi = 0

        for i in range(L):
            contains = False

            if hi < i: hi = i

            while hi < L and query(i, hi) in self._prefix:
                hi += 1
                contains = True

            if not contains: continue

            cur_hash = query(i, hi - 1)
            pat.add(self._prefix[cur_hash])

            hi += 1

        pat.discard(-1)

        return pat

            

        
