# Copyright (c) 2013-2014
# Harvard FAS Research Computing
# All rights reserved.

"""unit tests"""

import sys, os
import unittest, mock

import slyme
from slyme import util, jobs

from dio import buffer_out
from dio.coreutils import head

import settings


#only look at this number of results
limit = 10

#expect all job queries to return at least this number of jobs
min_job_count = 1

#some jobs that can be expected to be in the system
users = ['slurmmon',]
partitions = ['general', 'interact']

#a JobID that is no longer in scontrol but is in sacct
#the job must be COMPLETED
old_JobID = '77454'


class JobsTestCase(unittest.TestCase):
	#--- history

	def test_history_with_default_scope(self):
		results = []

		jobs.history(
			out=head(n=limit,
				out=buffer_out(
					out=results
				)
			)
		)

		self.assertTrue(len(results) >= min_job_count)

	def test_history_with_filter_single_values(self):
		user = users[0]
		partition = partitions[0]

		results = []

		jobs.history(filter_d={
				'User': user,
				'Partition': partition,
			},
			out=head(n=limit,
				out=buffer_out(
					out=results
				)
			)
		)

		for j in results:
			self.assertEqual(j['User'], user)
			self.assertEqual(j['Partition'], partition)

	def test_history_with_filter_lists(self):
		results = []

		jobs.history(filter_d={
				'User': users,
				'Partition': partitions,
			},
			out=head(n=limit,
				out=buffer_out(
					out=results
				)
			)
		)

		for j in results:
			self.assertTrue(j['User'] in users)
			self.assertTrue(j['Partition'] in partitions)


	#--- jobs (live jobs)


	#--- lookup by JobID

	def test_scontrol_invalid_JobID(self):
		#mock sacct to make sure that doesn't pick up the job either
		with mock.patch('slyme.jobs._yield_raw_sacct_text_per_job') as m:
			m.return_value = open('/dev/null','r')

			j = jobs.Job(JobID='1')  #assuming JobID 1 has aged out of scontrol
			self.assertRaises(KeyError, j.__getitem__, 'User')

	def test_scontrol_to_sacct_failback(self):
		j = jobs.Job(JobID=old_JobID)
		self.assertEqual(j['State'], 'COMPLETED')

	def test_SacctReport(self):
		j = jobs.Job(JobID=old_JobID)
		assert 'COMPLETED' in j['SacctReport']


if __name__=='__main__':
	unittest.main()
