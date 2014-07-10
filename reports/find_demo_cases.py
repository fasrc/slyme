#!/usr/bin/env python

# Copyright (c) 2013-2014
# Harvard FAS Research Computing
# All rights reserved.

"""inspect the data to find good examples for demos"""

import os

import slyme
from slyme import util, jobs

MOCK = True


def users_in_both_historical_and_live():
	"""Yield tuples (User, # Jobs Historical, # Jobs Live).
	
	Only yields a user if both job counts are greater than zero.
	"""

	UsersHistorical = {}
	for j in jobs.get_jobs_historical():
		try:
			UsersHistorical[j['User']] += 1
		except KeyError:
			UsersHistorical[j['User']] = 1

	UsersLive = {}
	for j in jobs.get_jobs_live():
		#if j['User'] == User:
		#	print j['JobID']
		
		try:
			UsersLive[j['User']] += 1
		except KeyError:
			UsersLive[j['User']] = 1
	
	for User in set(UsersHistorical.keys()).intersection(set(UsersLive.keys())):
		yield (User, UsersHistorical[User], UsersLive[User])


if __name__=='__main__':
	if MOCK:
		from mock import MagicMock
		
		slyme.jobs._yield_raw_scontrol_text_per_job = MagicMock(
			return_value=open(os.path.join(os.path.dirname(slyme.__file__), 'tests', '_mock_data', 'scontrol_bulk_parsable.out'))
		)

		slyme.jobs._yield_raw_sacct_lines = MagicMock(
			return_value=open(os.path.join(os.path.dirname(slyme.__file__), 'tests', '_mock_data', 'sacct_bulk_parsable.out'))
		)

	print "---"
	print "Users with both historical and live jobs"
	print "(User, # jobs historical, # jobs live)"
	for x in users_in_both_historical_and_live():
		print x
