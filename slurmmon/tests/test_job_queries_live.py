# Copyright (c) 2013-2014
# Harvard FAS Research Computing
# All rights reserved.

"""unit tests"""

import sys, os
import unittest, mock

try:
	import slurmmon
except ImportError:
	sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
	import slurmmon
from slurmmon import util, jobs


#a JobID that is no longer in scontrol but is in sacct
#the job must be COMPLETED
old_JobID = '77454'

class JobsTestCase(unittest.TestCase):
	def test_scontrol_invalid_JobID(self):
		#mock sacct to make sure that doesn't pick up the job either
		with mock.patch('slurmmon.jobs._yield_raw_sacct_job_lines') as m:
			m.return_value = open('/dev/null','r')

			j = jobs.Job(JobID='1')  #assuming JobID 1 has aged out of scontrol
			self.assertRaises(KeyError, j.__getitem__, 'User')

	def test_scontrol_to_sacct_failback(self):
		j = jobs.Job(JobID=old_JobID)
		self.assertEqual(j['State'], 'COMPLETED')


if __name__=='__main__':
	unittest.main()
