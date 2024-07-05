import enum
import gzip
import bz2
import pickle

from colc.common import internal_problem

from ._object import Object


class Compression(enum.Enum):
    NONE = 'none'
    GZIP = 'gz'
    BZ2 = 'bz2'


def encode(obj: Object, compression: Compression = Compression.NONE) -> bytes:
    try:
        encoded = pickle.dumps(obj)
    except Exception as e:
        internal_problem('pickle error', e)

    try:
        if compression == Compression.GZIP:
            encoded = gzip.compress(encoded)
        if compression == Compression.BZ2:
            encoded = bz2.compress(encoded)
    except Exception as e:
        internal_problem('compression error', e)

    return encoded
