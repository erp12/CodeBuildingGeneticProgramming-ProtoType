from collections import defaultdict
from typing import Sequence

import numpy as np


def escape(s: str) -> str:
    return s.encode("unicode_escape").decode("utf-8")


def median_absolute_deviation(x: np.array) -> float:
    """Return the MAD.

    Parameters
    ----------
    x : array-like, shape = (n,)

    """
    return np.median(np.abs(x - np.median(x))).item()


def damerau_levenshtein_distance(a: Sequence, b: Sequence) -> int:
    """Damerau Levenshtein Distance that works for both strings and lists.
    https://en.wikipedia.org/wiki/Damerau%E2%80%93Levenshtein_distance.
    This implemenation is heavily inspired by the implementation in the
    jellyfish package. https://github.com/jamesturk/jellyfish
    """
    a_is_str = isinstance(a, str)
    b_is_str = isinstance(b, str)
    if a_is_str or b_is_str:
        assert a_is_str and b_is_str

    len1 = len(a)
    len2 = len(b)
    infinite = len1 + len2

    da = defaultdict(int)
    score = [[0] * (len2 + 2) for x in range(len1 + 2)]
    score[0][0] = infinite
    for i in range(0, len1 + 1):
        score[i + 1][0] = infinite
        score[i + 1][1] = i
    for i in range(0, len2 + 1):
        score[0][i + 1] = infinite
        score[1][i + 1] = i

    for i in range(1, len1 + 1):
        db = 0
        for j in range(1, len2 + 1):
            i1 = da[b[j - 1]]
            j1 = db
            cost = 1
            if a[i - 1] == b[j - 1]:
                cost = 0
                db = j

            score[i + 1][j + 1] = min(score[i][j] + cost,
                                      score[i + 1][j] + 1,
                                      score[i][j + 1] + 1,
                                      score[i1][j1] + (i - i1 - 1) + 1 + (j - j1 - 1))
        da[a[i - 1]] = i
    return score[len1 + 1][len2 + 1]
