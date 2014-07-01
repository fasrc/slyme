# Copyright (c) 2013-2014
# Harvard FAS Research Computing
# All rights reserved.

"""unit tests

This requires a clone of https://github.com/fasrc/slurm_utils, for its example_jobs.
"""

import sys, os, time, errno
import unittest, mock

import slyme
from slyme import util, jobs


#dependency on slurm_utils
slurm_utils_example_jobs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../slurm_utils/example_jobs/'))
print "changing directory to:", slurm_utils_example_jobs_dir
try:
	os.chdir(slurm_utils_example_jobs_dir)
except OSError, e:
	if e.errno == errno.ENOENT:
		sys.stderr.write("*** ERROR *** In order for these tests to work, you need to clone slurm_utils (https://github.com/fasrc/slurm_utils) as a neighbor to this repo, since this runs jobs out of its example_jobs directory.\n")
		sys.exit(0)
	raise


class WorkflowTestCase(unittest.TestCase):
	def test_batch_script_workflow_serial_hello_world(self):
		j = jobs.Job(JobScript=open('hello_world.sbatch').read())

		t_start = time.time()

		#submit the job
		jobs.submit(j)
		
		self.assertTrue(isinstance(int(j['JobID']), int),
			"submitting a job did not result in a JobID that can be parsed as an int"
		)
		self.assertEqual(j['State'], 'PENDING',
			"newly submitted job is not PENDING"
		)

		#wait for it to finish
		while j['State'] != 'COMPLETED':
			jobs.update(j)
			time.sleep(0.5)

		t_end = time.time()

		#something only found in sacct
		self.assertTrue(j['CPUTime'] >= 0.0)  #(it's so short it usually actually is 00:00:00 in sacct)
		self.assertTrue(j['CPUTime'] < t_end-t_start)


if __name__=='__main__':
	unittest.main()
