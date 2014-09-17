#!/usr/bin/env python

# Copyright (c) 2013-2014
# Harvard FAS Research Computing
# All rights reserved.

"""a demo user-oriented report"""

import sys, os

import slyme
from slyme.jobs import history

from dio import buffer_out
from dio.coreutils import head


SHOW = 150


if __name__=='__main__':
	try:
		User = sys.argv[1]
	except IndexError:
		sys.stderr.write("*** ERROR *** usage: %s USERNAME\n" % os.path.basename(__file__))
		sys.exit(1)


	#--- job history

	jobs = []

	history(
		out=head(n=SHOW,
			out=buffer_out(
				out=jobs
			)
		)
	)

	for job in jobs:
		print job['JobID'], job['User'], job.get('JobScriptPreview', 'n/a')
