'''
Created on May 7, 2014

@author: aaronkitzmiller
'''
from __future__ import print_function
import unittest
import os, sys
from slyme import JobReport



class FakeRunSh:
    """
    Imitation runsh_i that uses predefined text
    """
    def __init__(self,text):
        self.text = text
        
    def runsh_i(self,args=[]):
        """
        Splits the text into lines and yields each line as though it were a 
        command output
        """       
        lines = self.text.splitlines()
        for line in lines:
            yield line
    

currentrunsh = None

class Test(unittest.TestCase):
        
    def setUp(self):
        pass
    
    def tearDown(self):
        pass

    def test_JobReportParsing(self):  
        """
        Parses text files generated from selected sacct output
        """
        
        text="""
10048462|akitzmiller|bash|CANCELLED by 0|interact|1|1|02:08:33|08:01.433|06:47.955|01:13.477|2000Mn|2409232K|2014-05-01T11:43:26|2014-05-01T13:51:59|holy2a18206
10053213|akitzmiller|bash|COMPLETED|interact|1|1|01:04:49|13:29.616|11:09.280|02:20.336|20000Mn|468500K|2014-05-01T13:52:30|2014-05-01T14:57:19|holy2a18206
10058675|akitzmiller|bash|CANCELLED by 100278|bigmem|0|2|00:00:00|00:00:00|00:00:00|00:00:00|300000Mn||2014-05-01T17:26:17|2014-05-01T17:26:17|None assigned
10101624|akitzmiller|agalmatest.sbatch|FAILED|bigmem|8|1|00:30:08|03:37.192|02:57.685|00:39.506|300000Mn||2014-05-04T10:34:55|2014-05-04T10:38:41|holybigmem08
10101624.batch||batch|FAILED||1|1|00:03:46|03:37.192|02:57.685|00:39.506|300000Mn|2407896K|2014-05-04T10:34:55|2014-05-04T10:38:41|holybigmem08
10102688|akitzmiller|dusage.sbatch|FAILED|general|4|1|00:01:12|00:00.367|00:00.103|00:00.263|1000Mc||2014-05-02T10:53:11|2014-05-02T10:53:29|holy2a02102
10102688.batch||batch|FAILED||1|1|00:00:18|00:00.367|00:00.103|00:00.263|1000Mc|4260K|2014-05-02T10:53:11|2014-05-02T10:53:29|holy2a02102
10102746|akitzmiller|dusage.sbatch|FAILED|general|4|1|00:00:16|00:00.232|00:00.089|00:00.142|1000Mc||2014-05-02T11:01:08|2014-05-02T11:01:12|holy2a05206
10102746.batch||batch|FAILED||1|1|00:00:04|00:00.232|00:00.089|00:00.142|1000Mc|14340K|2014-05-02T11:01:08|2014-05-02T11:01:12|holy2a05206
10102801|akitzmiller|bash|COMPLETED|interact|1|1|03:24:41|00:18.743|00:08.706|00:10.036|2000Mn|26968K|2014-05-02T11:05:42|2014-05-02T14:30:23|holy2a18206
10213033|akitzmiller|bash|COMPLETED|interact|1|1|01:27:02|00:03.319|00:01.623|00:01.695|2000Mn|5656K|2014-05-05T14:20:40|2014-05-05T15:47:42|holy2a18208
10384435|akitzmiller|agalmatest.sbatch|FAILED|general|8|1|00:01:36|00:01.590|00:01.220|00:00.369|30000Mn||2014-05-09T16:01:53|2014-05-09T16:02:05|holy2a04307
10384435.batch||batch|FAILED||1|1|00:00:12|00:01.590|00:01.220|00:00.369|30000Mn|7068K|2014-05-09T16:01:53|2014-05-09T16:02:05|holy2a04307
10703867|akitzmiller|bash|COMPLETED|interact|1|1|00:07:46|00:01.874|00:01.564|00:00.309|1000Mn|33084K|2014-05-14T14:08:31|2014-05-14T14:16:17|holy2a18205
"""        
        currentrunsh = FakeRunSh(text)
        
        jobreports = JobReport.fetch(execfunc = currentrunsh.runsh_i)
        
        # *** Test for JobReport with single JobStep (10048462 is an interactive job) ***
        jr = jobreports.next()
        
        # Both attribute and index access work
        self.assertEqual(jr.JobID, '10048462', "Incorrect JobID %s" % jr.JobID)
        self.assertEqual(jr["JobID"], '10048462', "Incorrect JobID %s" % jr.JobID)
        
        # Fields are correct values, including calculateds
        self.assertEqual(jr.User, 'akitzmiller', "Incorrect User %s" % jr.User)
        self.assertEqual(jr.JobName, 'bash', "Incorrect JobName %s" % jr.JobName)
        self.assertEqual(jr.NCPUS, 1, "Incorrect NCPUS %s" % jr.NCPUS)
        self.assertEqual(jr.NNodes, 1, "Incorrect NNodes %s" % jr.NNodes)
        self.assertEqual(jr.ReqMem_bytes, 2097152000, "Incorrect ReqMem_bytes %s" % jr.ReqMem_bytes)
        self.assertEqual(jr.MaxRSS_kB, 2409232, "Incorrect MaxRSS_kB %s" % jr.MaxRSS_kB)
        self.assertEqual(jr.Start.month, 5, "Incorrect Start.month %s" % jr.Start.month)
        self.assertEqual(jr.Start.day, 1, "Incorrect Start.day %s" % jr.Start.day)
        self.assertEqual(jr.Start.year, 2014, "Incorrect Start.year %s" % jr.Start.year)
        self.assertEqual(jr.Start.hour, 11, "Incorrect Start.hour %s" % jr.Start.hour)
        self.assertEqual(jr.Start.minute, 43, "Incorrect Start.minute %s" % jr.Start.minute)
        self.assertEqual(jr.Start.second, 26, "Incorrect Start.second %s" % jr.Start.second)
        self.assertEqual(jr.End.hour, 13, "Incorrect End.hour %s" % jr.End.hour)
        self.assertEqual(jr.NodeList, "holy2a18206", "Incorrect NodeList %s" % jr.NodeList)
        
        self.assertEqual(jr.State, "CANCELLED", "Incorrect State %s" % jr.State)
        self.assertEqual(jr.CancelledBy, "0", "Incorrect CancelledBy %s" % jr.CancelledBy)
        
        # TODO: Time elements.  These should probably be converted to seconds
        
        
        # *** Test for JobReport with typical two JobStep batch form ***
        jobreports.next()
        jobreports.next()
        jr = jobreports.next()
        
        # Check JobID
        self.assertEqual(jr.JobID, '10101624', "Incorrect JobID %s" % jr.JobID)
        # JobName should not be null
        self.assertEqual(jr.JobName, 'agalmatest.sbatch', "Incorrect JobName %s" % jr.JobName)
        # Partition should not be null
        self.assertEqual(jr.Partition, 'bigmem', "Incorrect Partition %s" % jr.Partition)
        # MaxRSS should not be null
        self.assertEqual(jr.MaxRSS_kB, 2407896, "Incorrect MaxRSS_kB %s" % jr.MaxRSS_kB)
       
        #for jobreport in jobreports:
            #print("JobID is %s" % jobreport["JobID"])



if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
