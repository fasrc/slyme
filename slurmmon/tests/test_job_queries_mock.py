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
from slurmmon import jobs


class SacctTestCase(unittest.TestCase):
	##this takes a long time and doesn't do anything useful yet
	#def test_sacct_bulk(self):
	#	with mock.patch('slurmmon.jobs._yield_raw_sacct_job_lines') as m:
	#		m.return_value = open(os.path.join(os.path.dirname(__file__), '_mock_data', 'sacct_bulk_COMPLETED_day_parsable.out'))
	#
	#		for j in jobs.get_jobs():
	#			print j
	
	def test_saccount_single(self):
		with mock.patch('slurmmon.jobs._yield_raw_sacct_job_lines') as m:
			m.return_value = open(os.path.join(os.path.dirname(__file__), '_mock_data', 'sacct_single_COMPLETED_parsable.out'))

			for j in jobs.get_jobs():
				print j


if __name__=='__main__':
	unittest.main()
