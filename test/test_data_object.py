"""
"""

from dfms.data_object import AbstractDataObject, AppDataObject, StreamDataObject, FileDataObject, ComputeStreamChecksum, ComputeFileChecksum, ContainerDataObject
from dfms.events.event_broadcaster import LocalEventBroadcaster
from dfms.events.pyro.pyro_event_broadcaster import PyroEventBroadcaster
from Pyro.EventService.Server import EventServiceStarter
from Pyro.naming import NameServerStarter 
import Pyro.core

import os, unittest, threading, socket

try:
    from crc32c import crc32
except:
    from binascii import crc32

ONE_MB = 1024 ** 2

class SumupContainerChecksum(AppDataObject):
    """
    A dummy component that sums up checksums of all children of the host
    ContainerDataObject (CDO), and then set the CDO's checksum as the sum
    """
    def appInitialize(self, **kwargs):
        self._bufsize = 4 * 1024 ** 2

    def get_file_checksum(self, filename):
        fo = open(filename, "r")
        buf = fo.read(self._bufsize)
        crc = 0
        while (buf != ""):
            crc = crc32(buf, crc)
            buf = fo.read(self._bufsize)
        fo.close()
        return crc

    def run(self, producer, **kwargs):
        if (isinstance(producer, ContainerDataObject)):
            c = 0
            for child in producer._children:
                c += self.get_file_checksum(child._fnm)
            producer.checksum = c
        else:
            raise Exception("Not a container data object!")

class TestDataObject(unittest.TestCase):


    def _eventThread(self, eventservice, host):
        eventservice.start(host)    
    
    def _nameThread(self, nameservice):
        nameservice.start()
    
    def setUp(self):
        """
        library-specific setup
        """
        self._test_do_sz = 16 # MB
        self._test_block_sz =  2 # MB
        self._test_num_blocks = self._test_do_sz / self._test_block_sz
        self._test_block = str(bytearray(os.urandom(self._test_block_sz * ONE_MB)))        

    def tearDown(self):
        """
        library-specific shutdown
        """
        pass

    def TestEventHandler(self, event):
        #print
        print "Test event from {0}: {1} = {2}".format(event.oid, event.type, event.status)
        #print event.source

    def test_write_FileDataObject(self):
        """
        Test an AbstractDataObject and a simple AppDataObject (for checksum calculation)
        """        
        Pyro.config.PYRO_HOST = 'localhost'
        nameservice = NameServerStarter()
        eventservice = EventServiceStarter()
        
        nameThread = threading.Thread(None, self._nameThread, 'namethread', (nameservice,))
        nameThread.setDaemon(True)
        nameThread.start()
        nameservice.waitUntilStarted()
        
        eventThread = threading.Thread(None, self._eventThread, 'eventthread', (eventservice, Pyro.config.PYRO_HOST ))
        eventThread.setDaemon(True)
        eventThread.start()
        eventservice.waitUntilStarted()
        
        eventbc = PyroEventBroadcaster()
        
        dobA = FileDataObject('oid:A', 'uid:A', eventbc=eventbc, subs=[self.TestEventHandler], file_length = self._test_do_sz * ONE_MB)
        dobB = ComputeFileChecksum('oid:B', 'uid:B', eventbc=eventbc, subs=[self.TestEventHandler])
        dobA.addConsumer(dobB)

        dobA.open()

        test_crc = 0
        for i in range(self._test_num_blocks):
            dobA.write(None, chunk = self._test_block)
            test_crc = crc32(self._test_block, test_crc)

        dobA.close()
        self.assertTrue((test_crc == dobA.checksum and 0 != test_crc),
                        msg = "test_crc = {0}, dob_crc = {1}".format(test_crc, dobA.checksum))

    def test_write_StreamDataObject(self):
        """
        Test an AbstractDataObject and a simple AppDataObject (for checksum calculation)
        """
        eventbc=LocalEventBroadcaster()
        
        dobA = StreamDataObject('oid:A', 'uid:A', eventbc=eventbc)
        dobB = ComputeStreamChecksum('oid:B', 'uid:B', eventbc=eventbc)
        dobA.addConsumer(dobB)

        dobA.open()

        test_crc = 0
        for i in range(self._test_num_blocks):
            dobA.write(None, chunk = self._test_block)
            test_crc = crc32(self._test_block, test_crc)

        dobA.close()
        self.assertTrue((test_crc == dobA.checksum and 0 != test_crc),
                        msg = "test_crc = {0}, dob_crc = {1}".format(test_crc, dobA.checksum))

    def test_join(self):
        """
        Using the container data object to implement a join/barrier dataflow

        -->A1(a1)--->|
        -->A2(a2)--->|-->B(b)
        -->A3(a3)--->|

        """
        eventbc = LocalEventBroadcaster()
        
        filelen = self._test_do_sz * ONE_MB
        dobAList = []
        #create file data objects
        dobA1 = FileDataObject('oid:A1', 'uid:A1', eventbc=eventbc, subs=[self.TestEventHandler],
                               file_length=filelen)
        dobA2 = FileDataObject('oid:A2', 'uid:A2', eventbc=eventbc, subs=[self.TestEventHandler],
                               file_length=filelen)
        dobA3 = FileDataObject('oid:A3', 'uid:A3', eventbc=eventbc, subs=[self.TestEventHandler],
                               file_length=filelen)
        dobAList.append(dobA1)
        dobAList.append(dobA2)
        dobAList.append(dobA3)

        # create CRC component attached to the file data object
        dob_a1 = ComputeFileChecksum('oid:a1', 'uid:a1',
                                     eventbc=eventbc, subs=[self.TestEventHandler])
        dobA1.addConsumer(dob_a1)
        dob_a2 = ComputeFileChecksum('oid:a2', 'uid:a2',
                                     eventbc=eventbc, subs=[self.TestEventHandler])
        dobA2.addConsumer(dob_a2)
        dob_a3 = ComputeFileChecksum('oid:a3', 'uid:a3',
                                     eventbc=eventbc, subs=[self.TestEventHandler])
        dobA3.addConsumer(dob_a3)

        dobB = ContainerDataObject('oid:B', 'uid:B', eventbc=eventbc)
        for dobA in dobAList:
            dobA.parent = dobB
            dobB.addChild(dobA)

        dob_b = SumupContainerChecksum('oid:b', 'uid:b',
                                       eventbc=eventbc, subs=[self.TestEventHandler])
        dobB.addConsumer(dob_b)

        for dobA in dobAList: # this should be parallel for
            dobA.open()
            #test_crc = 0
            for i in range(self._test_num_blocks):
                dobA.write(None, chunk = self._test_block)
                #test_crc = crc32(self._test_block, test_crc)
            dobA.close()

        sum_crc = 0
        for dobA in dobAList:
            sum_crc += dobA.checksum

        self.assertTrue((sum_crc == dobB.checksum and 0 != sum_crc),
                        msg = "sum_crc = {0}, dob_crc = {1}".format(sum_crc, dobB.checksum))

if __name__ == '__main__':
    unittest.main()

