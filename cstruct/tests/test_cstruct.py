#!/usr/bin/python
#*****************************************************************************
#
# Copyright (c) 2013 Andrea Bonomi <andrea.bonomi@gmail.com>
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

from unittest import (TestCase, main)
import cstruct
import sys

MBR_DATA =  b'\xebH\x90\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03\x02\xff\x00\x00\x80a\xcb\x04\x00\x00\x08\xfa\x80\xca\x80\xeaS|\x00\x001\xc0\x8e\xd8\x8e\xd0\xbc\x00 \xfb\xa0@|<\xfft\x02\x88\xc2R\xbey}\xe84\x01\xf6\xc2\x80tT\xb4A\xbb\xaaU\xcd\x13ZRrI\x81\xfbU\xaauC\xa0A|\x84\xc0u\x05\x83\xe1\x01t7f\x8bL\x10\xbe\x05|\xc6D\xff\x01f\x8b\x1eD|\xc7\x04\x10\x00\xc7D\x02\x01\x00f\x89\\\x08\xc7D\x06\x00pf1\xc0\x89D\x04f\x89D\x0c\xb4B\xcd\x13r\x05\xbb\x00p\xeb}\xb4\x08\xcd\x13s\n\xf6\xc2\x80\x0f\x84\xf0\x00\xe9\x8d\x00\xbe\x05|\xc6D\xff\x00f1\xc0\x88\xf0@f\x89D\x041\xd2\x88\xca\xc1\xe2\x02\x88\xe8\x88\xf4@\x89D\x081\xc0\x88\xd0\xc0\xe8\x02f\x89\x04f\xa1D|f1\xd2f\xf74\x88T\nf1\xd2f\xf7t\x04\x88T\x0b\x89D\x0c;D\x08}<\x8aT\r\xc0\xe2\x06\x8aL\n\xfe\xc1\x08\xd1\x8al\x0cZ\x8at\x0b\xbb\x00p\x8e\xc31\xdb\xb8\x01\x02\xcd\x13r*\x8c\xc3\x8e\x06H|`\x1e\xb9\x00\x01\x8e\xdb1\xf61\xff\xfc\xf3\xa5\x1fa\xff&B|\xbe\x7f}\xe8@\x00\xeb\x0e\xbe\x84}\xe88\x00\xeb\x06\xbe\x8e}\xe80\x00\xbe\x93}\xe8*\x00\xeb\xfeGRUB \x00Geom\x00Hard Disk\x00Read\x00 Error\x00\xbb\x01\x00\xb4\x0e\xcd\x10\xac<\x00u\xf4\xc3\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80\x00\x02\x00\x83\xfe?\x86\x01\x00\x00\x00\xc6\x17!\x00\x00\x00\x01\x87\x8e\xfe\xff\xff\xc7\x17!\x00M\xd3\xde\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00U\xaa'

class Position(cstruct.CStruct):
    __byte_order__ = cstruct.LITTLE_ENDIAN
    __struct__ = """
        unsigned char head;
        unsigned char sector;
        unsigned char cyl;
    """

class Partition(cstruct.CStruct):
    __byte_order__ = cstruct.LITTLE_ENDIAN
    __struct__ = """
        unsigned char status;       /* 0x80 - active */
        struct Position start;
        unsigned char partition_type;
        struct Position end;
        unsigned int start_sect;    /* starting sector counting from 0 */
        unsigned int sectors;       /* nr of sectors in partition */
    """


class MBR(cstruct.CStruct):
    __byte_order__ = cstruct.LITTLE_ENDIAN
    __struct__ = """
        char unused[440];
        unsigned char disk_signature[4];
        unsigned char usualy_nulls[2];
        struct Partition partitions[4];
        char signature[2];
    """


class TestCStruct(TestCase):

    def test_len(self):
        mbr = MBR()
        self.assertEqual(len(mbr), 512)
        self.assertEqual(mbr.size, 512)

    def test_unpack(self):
        mbr = MBR()
        mbr.unpack(MBR_DATA)
        if sys.version_info >= (3, 0):
            self.assertEqual(mbr.signature[0], 0x55)
            self.assertEqual(mbr.signature[1], 0xaa)
        else:
            self.assertEqual(mbr.signature[0], '\x55')
            self.assertEqual(mbr.signature[1], '\xaa')
        self.assertEqual(mbr.partitions[0].start.head, 0)
        self.assertEqual(mbr.partitions[0].end.head, 0xfe)
        self.assertEqual(mbr.partitions[1].start_sect, 0x2117c7)

    def test_pack(self):
        mbr = MBR(MBR_DATA)
        d = mbr.pack()
        self.assertEqual(MBR_DATA, d)
        mbr.partitions[3].start.head = 123
        d1 = mbr.pack()
        mbr1 = MBR(d1)
        self.assertEqual(mbr1.partitions[3].start.head, 123)

    def test_init(self):
        p = Position(head=254, sector=63, cyl=134)
        mbr = MBR(MBR_DATA)
        self.assertEqual(mbr.partitions[0].end, p)

    def test_none(self):
        mbr = MBR()
        self.assertEqual(mbr.partitions[0].end.sector, 0)
        mbr.unpack(None)
        self.assertEqual(mbr.partitions[0].end.head, 0)

    def test_clear(self):
        mbr = MBR()
        mbr.unpack(MBR_DATA)
        self.assertEqual(mbr.partitions[0].end.head, 0xfe)
        mbr.clear()
        self.assertEqual(mbr.partitions[0].end.head, 0x00)

if __name__ == '__main__':
    main()

