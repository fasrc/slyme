# Copyright (c) 2013-2014
# Harvard FAS Research Computing
# All rights reserved.

"""unit tests"""

import sys, os
import unittest, mock
from contextlib import nested  #deprecated in 2.7, but we're requiring only 2.6

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
	
	def test_scontrol_vs_sacct_single(self):
		j_scontrol = jobs.Job(JobID='77454')  #(JobID doesn't matter, since data is mocked)
		with mock.patch('slurmmon.jobs._yield_raw_scontrol_job_text_blocks') as m:
			#have scontrol return mock data for one job
			m.return_value = open(os.path.join(os.path.dirname(__file__), '_mock_data', 'scontrol_single_parallel_RUNNING.out'))
	
			j_scontrol['User']
			j_scontrol['JobName']
			j_scontrol['State']
			#(don't try anything that's not guaranteed to be here from scontrol, since not trying to test sacct yet)

		j_sacct = jobs.Job(JobID='77454')  #(JobID doesn't matter, since data is mocked)
		with nested(
			mock.patch('slurmmon.jobs._yield_raw_scontrol_job_text_blocks'),
		    mock.patch('slurmmon.jobs._yield_raw_sacct_job_lines')
			) as (m1, m2):
		
			#have scontrol return no data, so queries fall back on sacct
			m1.return_value = open('/dev/null','r')
			#have sacct return mock data for one job
			m2.return_value = open(os.path.join(os.path.dirname(__file__), '_mock_data', 'sacct_single_parallel_COMPLETED_parsable.out'))
			
			for k in jobs.Job.keys:
				if k not in ('JobScript', 'JobScriptPreview', 'SacctReport'):  #these are too verbose
					try:
						v = j_sacct[k]
					except KeyError:
						v = 'N/A'
					#print '%s: %s' % (k, v)


if __name__=='__main__':
	unittest.main()
