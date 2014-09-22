# Copyright (c) 2013-2014
# Harvard FAS Research Computing
# All rights reserved.

"""unit tests"""

import sys, os, datetime
import unittest

import slyme

import settings


class TestCase(unittest.TestCase):
	def test_slurm_time_interval_to_seconds(self):
		for tstr, t in (
			('4-18:29:01', 412141),
			('05:03:43', 18223),
			('01:09.666', 70),
			('00:09.666', 10),
			):
			t2 = int(round(slyme.slurm_time_interval_to_seconds(tstr)))
			self.assertEqual(t2, t,
				"%s != %s, instead got %s" % (tstr, t, t2)
			)

	def test_datetime_to_slurm_timestamp(self):
		tstr = '2013-04-18T11:36:17'
		t = 1366299377.618821
		td = datetime.datetime.fromtimestamp(t)

		tstr2 = slyme.datetime_to_slurm_timestamp(td)
		self.assertEqual(tstr2, tstr,
			"%s != %s, instead got %s" % (td, tstr, tstr2)
		)


if __name__=='__main__':
	unittest.main()
