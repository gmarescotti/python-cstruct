#!/usr/bin/env python
#*****************************************************************************
#
# Copyright (c) 2018 Andrea Bonomi <andrea.bonomi@gmail.com>
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

from unittest import TestCase, main
import cstruct
import sys

class VariableLength(cstruct.CStruct):
    __byte_order__ = cstruct.LITTLE_ENDIAN
    __struct__ = """
        uint16_t a;
        uint8_t b;
        uint8_t length;
        uint8_t data[];
    """


class TestVariableLength(TestCase):

    def test_zero(self):
        with self.assertRaises(NotImplementedError):
            t = VariableLength()
            self.assertEqual(len(t), 4)
            self.assertEqual(t.size, 4)
            self.assertEqual(len(t.data), 0)
            t.a = 1234
            t.b = 5
            t.pack()
            #x = t.unpack(b'\xd2\x04\x05\x00')
            #print(t.a)
            # self.assertEqual(t.pack(), b'\xd2\x04\x05\x00')
            #t.length = 3
            #t.data = [ 1, 2, 3]
            #self.assertRaises(t.pack(), NotImplementedError)

if __name__ == '__main__':
    main()

