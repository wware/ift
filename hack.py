#!/usr/bin/env python
# python -m doctest hack.py

import math

SAMPLE_RATE = 44100.
DT = 1. / SAMPLE_RATE
RETENTION_RATIO = 1024
RETENTION_RATE = SAMPLE_RATE / RETENTION_RATIO
RETENTION_PERIOD = RETENTION_RATIO * DT

# fixed point numbers
BITS32 = 0xFFFFFFFF
SIGN32 = 0x80000000
FRACBITS = 16
FRACTION = 1 << FRACBITS
FRACMASK = FRACTION - 1


def FIXED(flt):
    """
    >>> FIXED(2.)
    131072
    """
    assert isinstance(flt, float)
    return int(round(flt * FRACTION)) & BITS32

def FIXFMT(f):
    x = ''
    if f & (1 << 31):
        x = '-'
        f = (1 << 32) - f
    return x + str((1. * f) / FRACTION)

def FIXADD(fix1, fix2):
    """
    >>> def test(x, y, z):
    ...     assert (FIXED(x) + FIXED(y)) & BITS32 == FIXED(z), (FIXED(x), FIXED(y), FIXED(z))
    ...
    >>> test(1., 2., 3.)
    >>> test(-1., -2., -3.)
    """
    return (fix1 + fix2) & BITS32

def FIXSUB(fix1, fix2):
    return (fix1 - fix2) & BITS32

def FIXNEG(fix):
    """
    >>> FIXNEG(FIXED(-12.)) - ((1 << 32) - FIXNEG(FIXED(12.)))
    0
    """
    return (-fix) & BITS32

def FIXMULT(fix1, fix2):
    """
    >>> def test(x, y, z):
    ...     assert FIXMULT(FIXED(x), FIXED(y)) == FIXED(z), (FIXED(x), FIXED(y), FIXED(z))
    ...
    >>> test(12., 13., 156.)
    >>> test(-1., -2., 2.)
    """
    def parts(fix):
        assert isinstance(fix, (int, long))
        if fix & SIGN32:
            return (-1, fix - BITS32 - 1)
        else:
            return (1, fix)
    s1, f1 = parts(fix1)
    s2, f2 = parts(fix2)
    unsigned_prod = (f1 * f2) >> FRACBITS
    assert unsigned_prod < (1 << 32)
    if s1 * s2 > 0:
        return unsigned_prod
    else:
        return (1 << 32) - unsigned_prod


TABLE_BITS = 12
_table_size = 1 << TABLE_BITS
_sine_table = [
    FIXED(math.sin(2 * math.pi * i / _table_size))
    for i in xrange(_table_size)
]

BUFBITS = 10
BUFSIZE = 1 << BUFBITS

class Sinusoid(object):
    def __init__(self):
        self._a = self._ph = FIXED(0.)
        self._da = self._dph = FIXED(0.)

    def set(self, a, freq):
        self._da = FIXSUB(a, self._a) >> BUFBITS
        # phase is in cycles, not radians
        self._dph = freq >> BUFBITS

    def iterate(self, buf):
        assert BUFSIZE == len(buf)
        a, ph = self._a, self._ph
        for i in range(BUFSIZE):
            table_index = (ph & FRACMASK) >> (FRACBITS - TABLE_BITS)
            assert 0 <= table_index < _table_size
            sample = FIXMULT(a, _sine_table[table_index])
            buf[i] = FIXADD(buf[i], sample)
            a, ph = FIXADD(a, self._da), FIXADD(ph, self._dph)
        self._a, self._ph = a, ph


name = ('C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'G#', 'A', 'Bb', 'B', "C'")
notes = {
    name[i]: 440 * (2.0**((i-9)/12.))
    for i in range(13)
}

s = Sinusoid()
s.set(FIXED(1.), FIXED(notes['C']))
buf = BUFSIZE * [0]
s.iterate(buf)
import pprint
pprint.pprint(buf)

