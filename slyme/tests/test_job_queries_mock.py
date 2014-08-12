# Copyright (c) 2013-2014
# Harvard FAS Research Computing
# All rights reserved.

"""unit tests"""

import sys, os
import unittest, mock
from contextlib import nested  #deprecated in 2.7, but we're requiring only 2.6 so can't use the syntax the replaces it

import dio
import slyme
from slyme import jobs

import settings


class JobsTestCase(unittest.TestCase):
	def test_scontrol_bulk(self):
		with mock.patch('slyme.jobs._yield_raw_scontrol_text_per_job') as m:
			m.return_value = open(os.path.join(os.path.dirname(__file__), '_mock_data', 'scontrol_bulk_parsable.out'))

			i = 0
			for j in jobs.get_jobs_live():
				j['JobID']
				i += 1
				if i == 3: break  #takes too long to go through them all

	def test_sacct_bulk(self):
		with mock.patch('slyme.jobs._yield_raw_sacct_lines') as m:
			m.return_value = open(os.path.join(os.path.dirname(__file__), '_mock_data', 'sacct_bulk_parsable.out'))

			i = 0
			for j in jobs.get_jobs_historical():
				j['JobID']
				i += 1
				if i == 10: break  #takes too long to go through them all

	def test_scontrol_vs_sacct_single(self):
		j_scontrol = jobs.Job(JobID='77454')  #(JobID doesn't matter, since data is mocked)
		with mock.patch('slyme.jobs._yield_raw_scontrol_text_per_job') as m:
			#have scontrol return mock data for one job
			m.return_value = open(os.path.join(os.path.dirname(__file__), '_mock_data', 'scontrol_single_parallel_RUNNING.out'))

			#test that these don't raise KeyError
			j_scontrol['User']
			j_scontrol['JobName']
			j_scontrol['State']
			#(don't try anything that's not guaranteed to be here from scontrol, since not trying to test sacct yet)

		j_sacct = jobs.Job(JobID='77454')  #(JobID doesn't matter, since data is mocked)
		with nested(
			mock.patch('slyme.jobs._yield_raw_scontrol_text_per_job'),
		    mock.patch('slyme.jobs._yield_raw_sacct_text_per_job')
			) as (m1, m2):

			#have scontrol return no data, so queries fall back on sacct
			m1.return_value = open('/dev/null','r')
			#have sacct return mock data for one job
			m2.return_value = open(os.path.join(os.path.dirname(__file__), '_mock_data', 'sacct_single_parallel_COMPLETED_parsable.out'))

			#test that these don't raise KeyError
			j_sacct['User']
			j_sacct['JobName']
			j_sacct['State']

			for k in jobs.Job.keys:
				if k not in ('JobScript', 'JobScriptPreview', 'SacctReport'):  #these are too verbose
					try:
						v = j_sacct[k]
					except KeyError:
						v = 'N/A'
					#print '%s: %s' % (k, v)

	def test_jobs_processor(self):
		with mock.patch('slyme.jobs._yield_raw_sacct_lines') as m:
			m.return_value = open(os.path.join(os.path.dirname(__file__), '_mock_data', 'sacct_bulk_parsable.out'))

			self.out = []
			self.err = []
			dio.default_out = dio.buffer_out(out=self.out)
			dio.default_err = dio.buffer_out(out=self.err)

			jobs.jobs()

			i = 0
			for j in self.out:
				j['JobID']
				i += 1
				if i == 10: break  #takes too long to go through them all


if __name__=='__main__':
	unittest.main()
