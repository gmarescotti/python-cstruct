#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2013-2019 Andrea Bonomi <andrea.bonomi@gmail.com>
#
# Published under the terms of the MIT license.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#

from .base import STRUCTS
import hashlib
from .c_parser import (parse_struct, Tokens)

__all__ = [
    'CStructMeta',
    'AbstractCStruct'
]

class CStructMeta(type):

    def __new__(mcs, name, bases, dict):
        __struct__ = dict.get("__struct__", None)
        dict['__cls__'] = bases[0]
        # Parse the struct
        if __struct__ is not None:
            dict.update(parse_struct(**dict))
        # Create the new class
        new_class = type.__new__(mcs, name, bases, dict)
        # Register the class
        if __struct__ is not None and not dict.get('__anonymous__'):
            STRUCTS[name] = new_class
        return new_class

    def __len__(cls):
        return cls.__size__

    @property
    def size(cls):
        """ Structure size (in bytes) """
        return cls.__size__

# Workaround for Python 2.x/3.x metaclass, thanks to
# http://mikewatkins.ca/2008/11/29/python-2-and-3-metaclasses/#using-the-metaclass-in-python-2-x-and-3-x
_CStructParent = CStructMeta('_CStructParent', (object, ), {})


class AbstractCStruct(_CStructParent):

    def __init__(self, buffer=None, **kargs):
        if buffer is not None:
            self.unpack(buffer)
        else:
            try:
                self.unpack(buffer)
            except:
                pass
        for key, value in kargs.items():
            setattr(self, key, value)

    @classmethod
    def parse(cls, __struct__, __name__=None, **kargs):
        """
        Return a new class mapping a C struct/union definition.

        :param __struct__:     definition of the struct (or union) in C syntax
        :param __name__:       (optional) name of the new class. If empty, a name based on the __struct__ hash is generated
        :param __byte_order__: (optional) byte order, valid values are LITTLE_ENDIAN, BIG_ENDIAN, NATIVE_ORDER
        :param __is_union__:   (optional) True for union, False for struct (default)
        :returns:              cls subclass
        """
        kargs = dict(kargs)
        if not isinstance(__struct__, Tokens):
            __struct__ = Tokens(__struct__)
        kargs['__struct__'] = __struct__
        if __name__ is None: # Anonymous struct
            __name__ = cls.__name__ + '_' + hashlib.sha1(str(__struct__).encode('utf-8')).hexdigest()
            kargs['__anonymous__'] = True
        kargs['__name__'] = __name__
        return type(__name__, (cls,), kargs)

    def unpack(self, buffer):
        """
        Unpack bytes containing packed C structure data

        :param buffer: bytes or binary stream to be unpacked
        """
        if hasattr(buffer, 'read'):
            buffer = buffer.read(self.__size__)
            if not buffer:
                return False
        return self.unpack_from(buffer)

    def unpack_from(self, buffer, offset=0): # pragma: no cover
        """
        Unpack bytes containing packed C structure data

        :param buffer: bytes to be unpacked
        :param offset: optional buffer offset
        """
        return NotImplemented

    def pack(self): # pragma: no cover
        """
        Pack the structure data into bytes
        """
        return NotImplemented

    def clear(self):
        self.unpack(None)

    def __len__(self):
        """ Structure size (in bytes) """
        return self.__size__

    @property
    def size(self):
        """ Structure size (in bytes) """
        return self.__size__

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and self.__dict__ == other.__dict__)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        result = []
        for field in self.__fields__:
            result.append(field + "=" + str(getattr(self, field, None)))
        return type(self).__name__ + "(" + ", ".join(result) + ")"

    def __repr__(self): # pragma: no cover
        return self.__str__()


