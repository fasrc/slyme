#!/usr/bin/env python

# Copyright (c) 2013-2014
# Harvard FAS Research Computing
# All rights reserved.

"""a demo user-oriented report"""

import sys, os

import slyme
from slyme import util, jobs

MOCK = True


if __name__=='__main__':
	try:
		User = sys.argv[1]
	except IndexError:
		sys.stderr.write("*** ERROR *** usage: %s USERNAME\n" % os.path.basename(__file__))
		sys.exit(1)
	
	if MOCK:
		from mock import MagicMock
		
		slyme.jobs._yield_raw_scontrol_text_per_job = MagicMock(
			return_value=open(os.path.join(os.path.dirname(slyme.__file__), 'tests', '_mock_data', 'scontrol_bulk_parsable.out'))
		)

		slyme.jobs._yield_raw_sacct_lines = MagicMock(
			return_value=open(os.path.join(os.path.dirname(slyme.__file__), 'tests', '_mock_data', 'sacct_bulk_parsable.out'))
		)


	#--- job history

	for j in jobs.get_jobs_historical():
		if j['User']==User:
			print j


	#--- live jobs

	for j in jobs.get_jobs_live():
		if j['User']==User:
			print j
