__all__ = [
    # pympfr class: thin wrapper around mpfr_t type
    'pympfr',

    # global functions for getting and setting default precision
    'get_default_precision', 'set_default_precision',

    # constants giving limits on the precision
    'MPFR_PREC_MIN', 'MPFR_PREC_MAX',
    ]


import ctypes
import ctypes.util

################################################################################
# Platform dependent values

# To do: get these values directly by parsing or processing gmp.h
# It might be possible to use cpp directly to do this.

# set to value of __GMP_MP_SIZE_T_INT in gmp.h (should be 0 or 1)
__GMP_MP_SIZE_T_INT = 0

# set to True if __GMP_SHORT_LIMB is defined in gmp.h
__GMP_SHORT_LIMB_DEFINED = False

# set to True if _LONG_LONG_LIMB is defined in gmp.h
_LONG_LONG_LIMB_DEFINED = False

# set to True if your system uses a type smaller than int for an enum
# that includes negative values.  gcc usually uses int unless the
# -fshort-enums is specified.  On some platforms, -fshort-enums is the
# default.
_SHORT_ENUMS = False

################################################################################
# Types

# mpfr_prec_t: type used for representing a precision
# mpfr_exp_t: type used for representing exponents of mpfr_t instances
# mpfr_sign_t: type used for representing the sign
# mpfr_rnd_t: type used for rounding modes
# mpfr_t: type used for mpfr floating-point variables
#   mp_limb_t: internal type used for the digits

if __GMP_MP_SIZE_T_INT == 1:
    mpfr_exp_t = mpfr_prec_t = ctypes.c_uint
else:
    mpfr_exp_t = mpfr_prec_t = ctypes.c_ulong

mpfr_sign_t = ctypes.c_int

if __GMP_SHORT_LIMB_DEFINED:
    mp_limb_t = ctypes.c_uint
elif _LONG_LONG_LIMB_DEFINED:
    mp_limb_t = ctypes.c_ulonglong
else:
    mp_limb_t = ctypes.c_long

if _SHORT_ENUMS:
    mpfr_rnd_t = ctypes.c_byte
else:
    mpfr_rnd_t = ctypes.c_int

class __mpfr_struct(ctypes.Structure):
    _fields_ = [
        ("_mpfr_prec", mpfr_prec_t),
        ("_mpfr_sign", mpfr_sign_t),
        ("_mpfr_exp", mpfr_exp_t),
        ("_mpfr_d", ctypes.POINTER(mp_limb_t))
        ]

mpfr_t = __mpfr_struct * 1

################################################################################
# Limits

# limits on precision
MPFR_PREC_MIN = 2
MPFR_PREC_MAX = mpfr_prec_t(-1).value >> 1

################################################################################
# Wrap functions from the library

mpfr = ctypes.cdll.LoadLibrary(ctypes.util.find_library('mpfr'))

# 5.1 Initialization Functions

mpfr.mpfr_init2.argtypes = [mpfr_t, mpfr_prec_t]
mpfr.mpfr_init2.restype = None

mpfr.mpfr_clear.argtypes = [mpfr_t]
mpfr.mpfr_clear.restype = None

mpfr.mpfr_init.argtypes = [mpfr_t]
mpfr.mpfr_init.restype = None

mpfr.mpfr_set_default_prec.argtypes = [mpfr_prec_t]
mpfr.mpfr_set_default_prec.restype = None

mpfr.mpfr_get_default_prec.argtypes = []
mpfr.mpfr_get_default_prec.restype = mpfr_prec_t

mpfr.mpfr_set_prec.argtypes = [mpfr_t, mpfr_prec_t]
mpfr.mpfr_set_prec.restype = None

mpfr.mpfr_get_prec.argtypes = [mpfr_t]
mpfr.mpfr_get_prec.restype = mpfr_prec_t

################################################################################
# pympfr: a thin wrapper around the mpfr_t type that takes care of
# initialization and clearing.

def set_default_precision(precision):
    if not MPFR_PREC_MIN <= precision <= MPFR_PREC_MAX:
        raise ValueError("Precision out of range")
    mpfr.mpfr_set_default_prec(precision)

def get_default_precision():
    return mpfr.mpfr_get_default_prec()

class pympfr(object):
    def __init__(self, precision=None):
        # if reinitializing, clear first
        if hasattr(self, '_as_parameter_'):
            self._clear()

        value = mpfr_t()
        if precision is None:
            mpfr.mpfr_init(value)
        else:
            if not MPFR_PREC_MIN <= precision <= MPFR_PREC_MAX:
                raise ValueError("Precision out of range")
            mpfr.mpfr_init2(value, precision)
        self._as_parameter_ = value

    def _clear(self):
        mpfr.mpfr_clear(self._as_parameter_)
        del self._as_parameter_

    @property
    def precision(self):
        return mpfr.mpfr_get_prec(self)

    @precision.setter
    def precision(self, precision):
        if not MPFR_PREC_MIN <= precision <= MPFR_PREC_MAX:
            raise ValueError("Precision out of range")
        mpfr.mpfr_set_prec(self, precision)

    def __del__(self):
        if hasattr(self, '_as_parameter_'):
            self._clear()
