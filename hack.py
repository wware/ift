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
def FIXED(flt):
    """
    >>> FIXED(2.)
    131072
    """
    assert isinstance(flt, float)
    return int(round(flt * FRACTION)) & BITS32

def FIXADD(fix1, fix2):
    """
    >>> def test(x, y, z):
    ...     assert (FIXED(x) + FIXED(y)) & BITS32 == FIXED(z), (FIXED(x), FIXED(y), FIXED(z))
    ...
    >>> test(1., 2., 3.)
    >>> test(-1., -2., -3.)
    """
    return (fix1 + fix2) & BITS32

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
        signed_prod = unsigned_prod


_table_size = 4096
_sine_table = [
    FIXED(math.sin(2 * math.pi * i / _table_size))
    for i in xrange(_table_size)
]

class Sinusoid(object):
    def __init__(self):
        self._ampl = self._phase = FIXED(0.)
        self._da = self._dph = FIXED(0.)

    def set(self, da, dph):
        self._da = da
	self._dph = dph

    def iterate(self, buf):
        for i in range(RETENTION_RATIO):
	    x = buf[i]
	    a, ph = self._a, self._ph
	    new_a, new_ph = a + self._da, ph + self._dph
            table_index = int((a & FRACBITS) * _table_size) / >> FRACBITS
	    assert 0 <= table_index < _table_size
	    sval = _sine_table
