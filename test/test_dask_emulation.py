#
#    ICRAR - International Centre for Radio Astronomy Research
#    (c) UWA - The University of Western Australia, 2018
#    Copyright by UWA (in the framework of the ICRAR)
#    All rights reserved
#
#    This library is free software; you can redistribute it and/or
#    modify it under the terms of the GNU Lesser General Public
#    License as published by the Free Software Foundation; either
#    version 2.1 of the License, or (at your option) any later version.
#
#    This library is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#    Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public
#    License along with this library; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston,
#    MA 02111-1307  USA
#
import json
import unittest

import numpy as np
from six.moves import reduce  # @UnresolvedImport

from dlg import delayed
from dlg import tool
from dlg.utils import terminate_or_kill

def add(x, y):
    return x + y

def add_list(numbers):
    return reduce(add, numbers)

def subtract(x, y):
    return x - y

def subtract_list(numbers):
    return reduce(subtract, numbers)

def multiply(x, y):
    return x * y

def divide(x, y):
    return x / y

def partition(x):
    return x / 2, x - x / 2

def sum_with_args(a, *args):
    """Returns a + kwargs['b'], or only a if no 'b' is found in kwargs"""
    return a + sum(args)

def sum_with_kwargs(a, **kwargs):
    """Returns a + kwargs['b'], or only a if no 'b' is found in kwargs"""
    b = kwargs.pop('b', 0)
    return a + b

def sum_with_args_and_kwarg(a, *args, **kwargs):
    """Returns a + kwargs['b'], or only a if no 'b' is found in kwargs"""
    b = kwargs.pop('b', 0)
    return a + sum(args) + b

class MyType(object):
    """A type that is serializable but not convertible to JSON"""
    def __init__(self, x):
        self.x = x
        self.array = np.zeros(1)
try:
    json.dumps(MyType(1))
    assert False, "Should fail to serialize to JSON"
except:
    pass

def sum_with_user_defined_default(a, b=MyType(10)):
    return a + b.x

class TestDelayed(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)
        self.dmProcess = tool.start_process('nm')

    def tearDown(self):
        terminate_or_kill(self.dmProcess, 5)
        unittest.TestCase.tearDown(self)

    def test_simple(self):
        """This creates the following graph

        1 --|
            |-- add --> the_sum --------|
        2 --|                           |                                       |--> part1 --|
                                        |--> divide --> division -->partition --|            |--> add -> final
        4 --|                           |                                       |--> part2 --|
            |-- substract --> the_sub --|
        3 --|
        """
        the_sum = delayed(add)(1., 2.)
        the_sub = delayed(subtract)(4., 3.)
        division = delayed(divide)(the_sum, the_sub)
        parts = delayed(partition, nout=2)(division)
        result = delayed(add)(*parts).compute()
        self.assertEqual(3., result)

    def test_args_as_lists(self):
        """Like test_simple, but some arguments are passed down as lists"""
        one, two, three, four = delayed(1.), delayed(2.), delayed(3.), delayed(4.)
        the_sum = delayed(add_list)([one, two])
        the_sub = delayed(subtract_list)([four, three])
        division = delayed(divide)(the_sum, the_sub)
        parts = delayed(partition, nout=2)(division)
        result = delayed(add)(*parts).compute()
        self.assertEqual(3., result)

    def test_with_args(self):
        """Tests that delayed() works correctly with kwargs"""
        self.assertEqual(delayed(sum_with_args)(1).compute(), 1)
        self.assertEqual(delayed(sum_with_args)(1, 20).compute(), 21)
        self.assertEqual(delayed(sum_with_args)(1, 20, 30).compute(), 51)

    def test_with_kwargs(self):
        """Tests that delayed() works correctly with args and kwargs"""
        self.assertEqual(delayed(sum_with_kwargs)(1).compute(), 1)
        self.assertEqual(delayed(sum_with_kwargs)(1, b=20).compute(), 21)
        self.assertEqual(delayed(sum_with_kwargs)(1, b=20, x=-111).compute(), 21)

    def test_with_args_and_kwargs(self):
        """Tests that delayed() works correctly with kwargs"""
        self.assertEqual(delayed(sum_with_args_and_kwarg)(1).compute(), 1)
        self.assertEqual(delayed(sum_with_args_and_kwarg)(1, 20, b=100, x=-1000).compute(), 121)
        self.assertEqual(delayed(sum_with_args_and_kwarg)(1, 20, 30, b=100, x=-2000).compute(), 151)

    def test_with_user_defined_default(self):
        """Tests that delayed() works with default values that are not json-dumpable"""
        self.assertEquals(delayed(sum_with_user_defined_default)(1).compute(), 11)
        self.assertEquals(delayed(sum_with_user_defined_default)(1, MyType(20)).compute(), 21)

    def test_with_noniterable_nout_1(self):
        """Tests that using nout=1 works as expected with non-iterable objects"""
        # Simple call
        self.assertEquals(delayed(add, nout=1)(1, 2).compute(), 3)
        self.assertEquals(delayed(add, nout=1)(1, 2)[0].compute(), 3)

        # Compute a delayed that uses a delayed with nout=1
        addition = delayed(add, nout=1)(1, 2)
        self.assertEquals(delayed(add)(addition[0], 3).compute(), 6)

        # Like above, but the first delayed also uses nout=1
        self.assertEquals(delayed(add, nout=1)(addition[0], 3).compute(), 6)
        self.assertEquals(delayed(add, nout=1)(addition[0], 3)[0].compute(), 6)

        # Iterate over single result, which itself is not iterable
        results = []
        for x in delayed(add, nout=1)(1, 2):
            results.append(delayed(add)(x, 3).compute())
        self.assertListEqual(results, [6])

        # Like above, but use the delayed result in another delayed function
        results = []
        for x in delayed(add, nout=1)(1, 2):
            results.append(delayed(add)(x, 3).compute())
        self.assertListEqual(results, [6])

    def test_with_iterable_nout_1(self):
        """Tests that using nout=1 works as expected with iterable objects"""
        # Like last test above, but result is actually iterable
        results = []
        listify = lambda _x: [_x]
        for x in delayed(listify, nout=1)(2):
            results.append(delayed(add_list)(x).compute())
        self.assertListEqual(results, [2])