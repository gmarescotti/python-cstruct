#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""C-style structs for Python

Convert C struct definitions into Python classes with methods for
serializing/deserializing.
The usage is very simple: create a class subclassing cstruct.CStruct
and add a C struct definition as a string in the __struct__ field.
The C struct definition is parsed at runtime and the struct format string
is generated. The class offers the method "unpack" for deserializing
a string of bytes into a Python object and the method "pack" for
serializing the values into a string.

Example:
The following program reads the DOS partition information from a disk.

#!/usr/bin/env python
import cstruct

class Position(cstruct.CStruct):
    __byte_order__ = cstruct.LITTLE_ENDIAN
    __struct__ = \"\"\"
        unsigned char head;
        unsigned char sector;
        unsigned char cyl;
    \"\"\"

class Partition(cstruct.CStruct):
    __byte_order__ = cstruct.LITTLE_ENDIAN
    __struct__ = \"\"\"
        unsigned char status;       /* 0x80 - active */
        struct Position start;
        unsigned char partition_type;
        struct Position end;
        unsigned int start_sect;    /* starting sector counting from 0 */
        unsigned int sectors;       /* nr of sectors in partition */
    \"\"\"

    def print_info(self):
        print("bootable: %s" % ((self.status & 0x80) and "Y" or "N"))
        print("partition_type: %02X" % self.partition_type)
        print("start: head: %X sectory: %X cyl: %X" % (self.start.head, self.start.sector, self.start.cyl))
        print("end: head: %X sectory: %X cyl: %X" % (self.end.head, self.end.sector, self.end.cyl))
        print("starting sector: %08X" % self.start_sect)
        print("size MB: %s" % (self.sectors / 2 / 1024))

class MBR(cstruct.CStruct):
    __byte_order__ = cstruct.LITTLE_ENDIAN
    __struct__ = \"\"\"
        char unused[440];
        unsigned char disk_signature[4];
        unsigned char usualy_nulls[2];
        struct Partition partitions[4];
        char signature[2];
    \"\"\"

    def print_info(self):
        print("disk signature: %s" % "".join(["%02X" % x for x in self.disk_signature]))
        print("usualy nulls: %s" % "".join(["%02X" % x for x in self.usualy_nulls]))
        for i, partition in enumerate(self.partitions):
            print("")
            print("partition: %s" % i)
            partition.print_info()

disk = "mbr"
with open(disk, "rb") as f:
    mbr = MBR()
    data = f.read(len(mbr))
    mbr.unpack(data)
    mbr.print_info()

"""

#*****************************************************************************
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
#*****************************************************************************

__author__  = 'Andrea Bonomi <andrea.bonomi@gmail.com>'
__license__ = 'MIT'
__version__ = '1.9'
__date__ = '15 August 2013'

import re
import struct
import sys
import hashlib
from collections import namedtuple

__all__ = [
    'LITTLE_ENDIAN',
    'BIG_ENDIAN',
    'CStruct',
    'define',
    'typedef',
    'factory'
]

# little-endian, std. size & alignment
LITTLE_ENDIAN = '<'
# big-endian, std. size & alignment
BIG_ENDIAN = '>'
# native order, size & alignment
NATIVE_ORDER = '@'

C_TYPE_TO_FORMAT = {
    'char':                 's',
    'signed char':          'b',
    'unsigned char':        'B',
    'short':                'h',
    'short int':            'h',
    'ushort':               'H',
    'unsigned short':       'H',
    'unsigned short int':   'H',
    'int':                  'i',
    'unsigned int':         'I',
    'long':                 'l',
    'long int':             'l',
    'unsigned long':        'L',
    'unsigned long int':    'L',
    'long long':            'q',
    'unsigned long long':   'Q',
    'float':                'f',
    'double':               'd',
    'void *':               'P',
    'int8':                 'b',
    'int8_t':               'b',
    'uint8':                'B',
    'uint8_t':              'B',
    'int16':                'h',
    'int16_t':              'h',
    'uint16':               'H',
    'uint16_t':             'H',
    'int32':                'i',
    'int32_t':              'i',
    'uint32':               'I',
    'uint32_t':             'I',
    'int64':                'q',
    'int64_t':              'q',
    'uint64':               'Q',
    'uint64_t':             'Q',
}

STRUCTS = {
}

DEFINES = {
}

TYPEDEFS = {
}

def define(key, value):
    """
    Add a definition that can be used in the C struct
    """
    DEFINES[key] = value

def typedef(type_, alias):
    """
    Define an alias for a data type
    """
    TYPEDEFS[alias] = type_

FieldType = namedtuple('FieldType', [ 'vtype', 'vlen', 'vfmt', 'prefixed_vfmt', 'flexible_array' ])

def factory(__struct__, __name__=None, **kargs):
    """
    Return a new class mapping a C struct definition.

    :param __struct__:     definition of the struct (or union) in C syntax
    :param __name__:       (optional) name of the new class. If empty, a name based on the __struct__ hash is generated
    :param __byte_order__: (optional) byte order, valid values are LITTLE_ENDIAN, BIG_ENDIAN, NATIVE_ORDER
    :param _is_union__:    (optional) True for union, False for struct (default)
    :returns:              CStruct subclass
    """
    kargs = dict(kargs)
    kargs['__struct__'] = __struct__
    if __name__ is None: # Anonymous struct
        __name__ = 'CStruct%s' % hashlib.sha1(__struct__.encode('utf-8')).hexdigest()
        kargs['__anonymous__'] = True
    kargs['__name__'] = __name__
    return type(__name__, (CStruct,), kargs)

def parse_struct(__struct__, __fields__=None, __is_union__=False, __byte_order__=None, **kargs):
    __is_union__ = bool(__is_union__)
    # naive C struct parsing
    fmt = []
    fields = []
    fields_types = {}
    # remove the comments
    st = __struct__.replace("*/","*/\n")
    st = "  ".join(re.split("/\*.*\*/",st))
    st = "\n".join([s.split("//")[0] for s in st.split("\n")])
    st = st.replace("\n", " ")
    flexible_array = False
    for line_s in st.split(";"):
        line_s = line_s.strip()
        if line_s:
            line = line_s.split()
            if len(line) < 2:
                raise Exception("Error parsing: " + line_s)
            # flexible array member must be the last member of such a struct
            if flexible_array:
                raise Exception("Flexible array member must be the last member of such a struct")
            vtype = line[0].strip()
            # signed/unsigned/struct
            if vtype == 'unsigned' or vtype == 'signed' or vtype == 'struct' and len(line) > 2:
                vtype = vtype + " " + line[1].strip()
                del line[0]
            vname = line[1]
            # short int, long int, or long long
            if vname == 'int' or vname == 'long':
                vtype = vtype + " " + vname
                del line[0]
                vname = line[1]
            # void *
            if vname.startswith("*"):
                vname = vname[1:]
                vtype = 'void *'
            # parse length
            vlen = 1
            if "[" in vname:
                t = vname.split("[")
                if len(t) != 2:
                    raise Exception("Error parsing: " + line_s)
                vname = t[0].strip()
                vlen = t[1]
                vlen = vlen.split("]")[0].strip()
                if not vlen:
                    flexible_array = True
                    vlen = 0
                else:
                    try:
                        vlen = int(vlen)
                    except:
                        vlen = DEFINES.get(vlen, None)
                        if vlen is None:
                            raise
                        else:
                            vlen = int(vlen)
            while vtype in TYPEDEFS:
                vtype = TYPEDEFS[vtype]
            if vtype.startswith('struct '):
                vtype = vtype[7:]
                t = STRUCTS.get(vtype, None)
                if t is None:
                    raise Exception("Unknow struct \"" + vtype + "\"")
                vtype = t
                ttype = "c"
                vlen = vtype.size * vlen
            else:
                ttype = C_TYPE_TO_FORMAT.get(vtype, None)
                if ttype is None:
                    raise Exception("Unknow type \"" + vtype + "\"")
            fields.append(vname)
            vfmt = (str(vlen) if vlen > 1 or flexible_array else '') + ttype
            prefixed_vfmt = (__byte_order__ + vfmt) if __byte_order__ is not None else vfmt
            fields_types[vname] = FieldType(vtype, vlen, vfmt, prefixed_vfmt, flexible_array)
            fmt.append(vfmt)

    if __is_union__: # C union
        # Calculate the union size as size of its largest element
        size = max([struct.calcsize(x.prefixed_vfmt) for x in fields_types.values()])
        fmt = '%ds' % size
    else: # C struct
        fmt = "".join(fmt)
        # Calculate the struct size
        size = struct.calcsize(fmt)

    # Add the byte order as prefix
    if __byte_order__ is not None:
        fmt = __byte_order__ + fmt

    # Prepare the result
    result = {
        '__fmt__': fmt,
        '__fields__': fields,
        '__fields_types__': fields_types,
        '__size__': size,
        '__is_union__': __is_union__,
        '__byte_order__': __byte_order__
    }

    # Add the missing fields to the class
    for field in __fields__ or []:
        if field not in dict:
            result[field] = None
    return result

class CStructMeta(type):

    def __new__(mcs, name, bases, dict):
        __struct__ = dict.get("__struct__", None)
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

EMPTY_BYTES_STRING = bytes()
if sys.version_info < (3, 0):
    CHAR_ZERO = bytes('\0')
else:
    CHAR_ZERO = bytes('\0', 'ascii')

class CStruct(_CStructParent):
    """
    Convert C struct definitions into Python classes.

    __struct__ = definition of the struct (or union) in C syntax
    __byte_order__ = (optional) byte order, valid values are LITTLE_ENDIAN, BIG_ENDIAN, NATIVE_ORDER
    __is_union__ = (optional) True for union definitions, False for struct definitions (default)

    The following fields are generated from the C struct definition
    __fmt__ = struct format string
    __size__ = lenght of the structure in bytes
    __fields__ = list of structure fields
    __fields_types__ = dictionary mapping field names to types
    Every fields defined in the structure is added to the class

    """

    def __init__(self, string=None, **kargs):
        if string is not None:
            self.unpack(string)
        else:
            try:
                self.unpack(string)
            except:
                pass
        for key, value in kargs.items():
            setattr(self, key, value)

    def unpack(self, string):
        """
        Unpack the string containing packed C structure data
        """
        if string is None:
            string = CHAR_ZERO * self.__size__
        if not self.__is_union__:
            data = struct.unpack_from(self.__fmt__, string, 0)
        i = 0
        for field in self.__fields__:
            field_type = self.__fields_types__[field]
            if field_type.flexible_array: # TODO
                raise NotImplementedError("Flexible array member are not supported")
            if field_type.vtype == 'char': # string
                if self.__is_union__:
                    setattr(self, field, struct.unpack_from(field_type.prefixed_vfmt, string, 0)[0])
                else:
                    setattr(self, field, data[i])
                i = i + 1
            elif isinstance(field_type.vtype, CStructMeta):
                num = int(field_type.vlen / field_type.vtype.size)
                if num == 1: # single struct
                    sub_struct = field_type.vtype()
                    if self.__is_union__:
                        sub_struct.unpack(string)
                    else:
                        sub_struct.unpack(EMPTY_BYTES_STRING.join(data[i:i+sub_struct.size]))
                    setattr(self, field, sub_struct)
                    i = i + sub_struct.size
                else: # multiple struct
                    sub_structs = []
                    for j in range(0, num):
                        sub_struct = field_type.vtype()
                        if self.__is_union__:
                            sub_struct.unpack(string[j*sub_struct.size:(j+1)*sub_struct.size])
                        else:
                            sub_struct.unpack(EMPTY_BYTES_STRING.join(data[i:i+sub_struct.size]))
                        i = i + sub_struct.size
                        sub_structs.append(sub_struct)
                    setattr(self, field, sub_structs)
            elif field_type.vlen == 1:
                if self.__is_union__:
                    setattr(self, field, struct.unpack_from(field_type.prefixed_vfmt, string, 0)[0])
                else:
                    setattr(self, field, data[i])
                i = i + field_type.vlen
            else:
                if self.__is_union__:
                    setattr(self, field, list(struct.unpack_from(field_type.prefixed_vfmt, string, 0)[0]))
                else:
                    setattr(self, field, list(data[i:i+field_type.vlen]))
                i = i + field_type.vlen

    def pack(self):
        """
        Pack the structure data into a string
        """
        data = []
        for field in self.__fields__:
            field_type = self.__fields_types__[field]
            if field_type.flexible_array: # TODO
                raise NotImplementedError("Flexible array member are not supported")
            if field_type.vtype == 'char': # string
                data.append(getattr(self, field))
            elif isinstance(field_type.vtype, CStructMeta):
                num = int(field_type.vlen / field_type.vtype.size)
                if num == 1: # single struct
                    v = getattr(self, field, field_type.vtype())
                    v = v.pack()
                    if sys.version_info >= (3, 0):
                        v = ([bytes([x]) for x in v])
                    data.extend(v)
                else: # multiple struct
                    values = getattr(self, field, [])
                    for j in range(0, num):
                        try:
                            v = values[j]
                        except:
                            v = field_type.vtype()
                        v = v.pack()
                        if sys.version_info >= (3, 0):
                            v = ([bytes([x]) for x in v])
                        data.extend(v)
            elif field_type.vlen == 1:
                data.append(getattr(self, field))
            else:
                v = getattr(self, field)
                v = v[:field_type.vlen] + [0] * (field_type.vlen - len(v))
                data.extend(v)
        return struct.pack(self.__fmt__, *data)

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

    def __repr__(self):
        return self.__str__()

