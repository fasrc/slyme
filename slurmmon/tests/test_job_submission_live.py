# Copyright (c) 2013-2014
# Harvard FAS Research Computing
# All rights reserved.

"""unit tests

This requires a clone of https://github.com/fasrc/slurm_utils, for its example_jobs.
"""

import sys, os, errno
import unittest, mock

try:
	import slurmmon
except ImportError:
	sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
	import slurmmon
from slurmmon import jobs

#dependency on slurm_utils
slurm_utils_example_jobs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../../../slurm_utils/example_jobs/'))
print "changing directory to:", slurm_utils_example_jobs_dir
try:
	os.chdir(slurm_utils_example_jobs_dir)
except OSError, e:
	if e.errno == errno.ENOENT:
		sys.stderr.write("*** ERROR *** In order for these tests to work, you need to clone slurm_utils (https://github.com/fasrc/slurm_utils) as a neighbor to this repo, since this runs jobs out of its example_jobs directory.\n")
		sys.exit(0)
	raise


class SubmissionTestCase(unittest.TestCase):
	def test_just_batch_script(self):
		pass


if __name__=='__main__':
	unittest.main()
