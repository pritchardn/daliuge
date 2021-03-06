#
#    ICRAR - International Centre for Radio Astronomy Research
#    (c) UWA - The University of Western Australia, 2017
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
"""Applications used as examples, for testing, or in simple situations"""

import time
import numpy as np
import six.moves.cPickle as pickle

from .. import droputils
from ..drop import BarrierAppDROP, ContainerDROP
from ..meta import dlg_float_param, dlg_string_param
from ..meta import dlg_bool_param, dlg_int_param
from ..meta import dlg_component, dlg_batch_input
from ..meta import dlg_batch_output, dlg_streaming_input


class NullBarrierApp(BarrierAppDROP):
    compontent_meta = dlg_component('NullBarrierApp', 'Null Barrier.',
                                    [dlg_batch_input('binary/*', [])],
                                    [dlg_batch_output('binary/*', [])],
                                    [dlg_streaming_input('binary/*')])

    """A BarrierAppDrop that doesn't perform any work"""
    def run(self):
        pass


##
# @brief SleepApp\n
# @details A simple APP that sleeps the specified amount of time (0 by default).
# This is mainly useful (and used) to test graph translation and structure
# without executing real algorithms. Very useful for debugging.
# @par EAGLE_START
# @param gitrepo $(GIT_REPO)
# @param version $(PROJECT_VERSION)
# @param category PythonApp
# @param[in] param/sleepTime/5/Integer/readwrite
#     \~English the number of seconds to sleep\n
# @param[in] param/appclass/dlg.apps.simple.SleepApp/String/readonly
#     \~English Application class\n

# @par EAGLE_END
class SleepApp(BarrierAppDROP):
    """A BarrierAppDrop that sleeps the specified amount of time (0 by default)"""
    compontent_meta = dlg_component('SleepApp', 'Sleep App.',
                                    [dlg_batch_input('binary/*', [])],
                                    [dlg_batch_output('binary/*', [])],
                                    [dlg_streaming_input('binary/*')])

    sleepTime = dlg_float_param('sleep time', 0)

    def initialize(self, **kwargs):
        super(SleepApp, self).initialize(**kwargs)

    def run(self):
        time.sleep(self.sleepTime)


##
# @brief CopyApp\n
# @details A simple APP that copies its inputs into its outputs.
# All inputs are copied into all outputs in the order they were declared in
# the graph. If an input is a container (e.g. a directory) it copies the
# content recursively.
# @par EAGLE_START
# @param gitrepo $(GIT_REPO)
# @param version $(PROJECT_VERSION)
# @param category PythonApp
# @param[in] param/appclass/dlg.apps.simple.CopyApp/String/readonly
#     \~English Application class\n

# @par EAGLE_END
class CopyApp(BarrierAppDROP):
    """
    A BarrierAppDrop that copies its inputs into its outputs.
    All inputs are copied into all outputs in the order they were declared in
    the graph.
    """
    compontent_meta = dlg_component('CopyApp', 'Copy App.',
                                    [dlg_batch_input('binary/*', [])],
                                    [dlg_batch_output('binary/*', [])],
                                    [dlg_streaming_input('binary/*')])

    def run(self):
        self.copyAll()

    def copyAll(self):
        for inputDrop in self.inputs:
            self.copyRecursive(inputDrop)

    def copyRecursive(self, inputDrop):
        if isinstance(inputDrop, ContainerDROP):
            for child in inputDrop.children:
                self.copyRecursive(child)
        else:
            for outputDrop in self.outputs:
                droputils.copyDropContents(inputDrop, outputDrop)


class SleepAndCopyApp(SleepApp, CopyApp):
    """A combination of the SleepApp and the CopyApp. It sleeps, then copies"""

    def run(self):
        SleepApp.run(self)
        CopyApp.run(self)


##
# @brief RandomArrayApp\n
# @details A testing APP that does not take any input and produces a random array of
# type int64, if integer is set to True, else of type float64.
# size indicates the number of elements ranging between the values low and high. 
# The resulting array will be send to all connected output apps.
# @par EAGLE_START
# @param gitrepo $(GIT_REPO)
# @param version $(PROJECT_VERSION)
# @param category PythonApp
# @param[in] param/size/100/Integer/readwrite
#     \~English the siz of the array\n
# @param[in] param/integer/True/Boolean/readwrite
#     \~English Generate integer array?\n
# @param[in] param/low/0/float/readwrite
#     \~English low value of range in array [inclusive]\n
# @param[in] param/high/1/float/readwrite
#     \~English high value of range of array [exclusive]\n
# @param[in] param/appclass/dlg.apps.simple.RandomArrayApp/String/readonly
#     \~English Application class\n
# @param[out] port/array
#     \~English Port carrying the averaged array.
# @par EAGLE_END
class RandomArrayApp(BarrierAppDROP):
    """
    A BarrierAppDrop that generates an array of random numbers. It does
    not require any inputs and writes the generated array to all of its
    outputs.

    Keywords:

    integer:  bool [True], generate integer array
    low:      float, lower boundary (will be converted to int for integer arrays)
    high:     float, upper boundary (will be converted to int for integer arrays)
    size:     int, number of array elements
    """
    compontent_meta = dlg_component('RandomArrayApp', 'Random Array App.',
                                    [dlg_batch_input('binary/*', [])],
                                    [dlg_batch_output('binary/*', [])],
                                    [dlg_streaming_input('binary/*')])
    
    # default values
    integer = dlg_bool_param('integer', True)
    low = dlg_float_param('low', 0)
    high = dlg_float_param('high', 100)
    size = dlg_int_param('size', 100)
    marray = []

    def initialize(self, **kwargs):
        super(RandomArrayApp, self).initialize(**kwargs)

    def run(self):
        # At least one output should have been added
        outs = self.outputs
        if len(outs) < 1:
            raise Exception(
                'At least one output should have been added to %r' % self)
        self.generateRandomArray()
        for o in outs:
            d = pickle.dumps(self.marray)
            o.len = len(d)
            o.write(pickle.dumps(self.marray))

    def generateRandomArray(self):
        if self.integer:
            # generate an array of self.size integers with numbers between
            # slef.low and self.high
            marray = np.random.randint(int(self.low), int(self.high), size=(self.size))
        else:
            # generate an array of self.size floats with numbers between
            # self.low and self.high
            marray = (np.random.random(size=self.size) + self.low) * self.high
        self.marray = marray
    
    def _getArray(self):
        return self.marray


##
# @brief AverageArrays\n
# @details A testing APP that takes multiple numpy arrays on input and calculates
# the mean or the median, depending on the value provided in the method parameter. 
# Users can add as many producers to the input array port as required and the resulting array
# will also be send to all connected output apps.
# @par EAGLE_START
# @param gitrepo $(GIT_REPO)
# @param version $(PROJECT_VERSION)
# @param category PythonApp
# @param[in] param/method/mean/string/readwrite
#     \~English the methd used for averaging\n
# @param[in] param/appclass/dlg.apps.simple.AverageArraysApp/String/readonly
#     \~English Application class\n
# @param[in] port/array
#     \~English Port for the input array(s).
# @param[out] port/array
#     \~English Port carrying the averaged array.
# @par EAGLE_END
class AverageArraysApp(BarrierAppDROP):
    """
    A BarrierAppDrop that averages arrays received on input. It requires
    multiple inputs and writes the generated average vector to all of its
    outputs.
    The input arrays are assumed to have the same number of elements and
    the output array will also have that same number of elements.

    Keywords:

    method:  string <['mean']|'median'>, use mean or median as method.
    """
    compontent_meta = dlg_component('RandomArrayApp', 'Random Array App.',
                                    [dlg_batch_input('binary/*', [])],
                                    [dlg_batch_output('binary/*', [])],
                                    [dlg_streaming_input('binary/*')])

    # default values
    methods = ['mean', 'median']
    method = dlg_string_param('method', methods[0])
    marray = []

    def initialize(self, **kwargs):
        super(AverageArraysApp, self).initialize(**kwargs)

    def run(self):
        # At least one output should have been added

        outs = self.outputs
        if len(outs) < 1:
            raise Exception(
                'At least one output should have been added to %r' % self)
        self.getInputArrays()
        avg = self.averageArray()
        for o in outs:
            d = pickle.dumps(avg)
            o.len = len(d)
            o.write(d)  # average across inputs
    
    def getInputArrays(self):
        """
        Create the input array from all inputs received. Shape is
        (<#inputs>, <#elements>), where #elements is the length of the
        vector received from one input.
        """
        ins = self.inputs
        if len(ins) < 1:
            raise Exception(
                'At least one input should have been added to %r' % self)

        marray = [pickle.loads(droputils.allDropContents(inp)) for inp in ins]
        self.marray = marray


    def averageArray(self):
        
        method_to_call = getattr(np, self.method)
        return method_to_call(self.marray, axis=0)

##
# @brief HelloWorldApp\n
# @details A simple APP that implements the standard Hello World in DALiuGE.
# It allows to change 'World' with some other string and it also permits
# to connect the single output port to multiple sinks, which will all receive 
# the same message. App does not require any input.
# @par EAGLE_START
# @param gitrepo $(GIT_REPO)
# @param version $(PROJECT_VERSION)
# @param category PythonApp
# @param[in] param/greet/World/String/readwrite
#     \~English What appears after 'Hello '\n
# @param[in] param/appclass/dlg.apps.simple.HelloWorldApp/String/readonly
#     \~English Application class\n
# @param[out] port/hello
#     \~English The port carrying the message produced by the app.
# @par EAGLE_END
class HelloWorldApp(BarrierAppDROP):
    """
    An App that writes 'Hello World!' or 'Hello <greet>!' to all of
    its outputs.

    Keywords:
    greet:   string, [World], whom to greet.
    """
    compontent_meta = dlg_component('HelloWorldApp', 'Hello World App.',
                                    [dlg_batch_input('binary/*', [])],
                                    [dlg_batch_output('binary/*', [])],
                                    [dlg_streaming_input('binary/*')])

    greet = dlg_string_param('greet', 'World')

    def run(self):
        self.greeting = 'Hello %s' % self.greet

        outs = self.outputs
        if len(outs) < 1:
            raise Exception(
                'At least one output should have been added to %r' % self)
        for o in outs:
            o.len = len(self.greeting.encode())
            o.write(self.greeting.encode())  # greet across all outputs
