# Copyright (c) 2013-2014
# Harvard FAS Research Computing
# All rights reserved.

"""slyme configuration"""


import os, socket
from slyme import util
#(pygments import attempts are below)


#make it work out of the box both for FASRC and in general
FASRC = socket.gethostname().endswith('.rc.fas.harvard.edu')

#we also have dev and prod environments
FASRC_ENV = 'dev'  #'dev' or 'prod'
try:
	with open('/etc/slurm/slurm.conf','r') as f:
		for line in f.readlines():
			if line.startswith('ControlMachine'):
				if line.split('=')[1].strip()=='slurm-test':
					FASRC_ENV='dev'
					break
				if line.split('=')[1].strip()=='holy-slurm01':
					FASRC_ENV='prod'
					break
except IOError:
	pass


#--- whitespace reporting

def filter_whitespace_cpu_job(job):
	"""Approve or veto a job as a cpu waster.

	This should return False if the job should be excluded from the report, or
	True otherwise.  job is a slyme.jobs.Job.  Note that other slyme
	configuration and functionality take care of the main job characteristics.
	This is just an opportunity to account for users, partitions, etc. that are
	incorrectly being flagged or otherwise have been given a "pass".
	"""
	if FASRC:
		return \
		job['Partition'] != 'gpgpu' and \
		job['User'] != 'dnelson'

	else:
		return True

def filter_whitespace_cpu_node(job):
	return True

def whitespace_report_top_html():
	"""Return extra html to include at the top of the whitespace report.

	For example, links to the allocation vs untilization plots from
	slyme-ganglia.
	"""
	if FASRC:
		return """\
		<img src="http://status.rc.fas.harvard.edu/ganglia/holyoke_compute/graph.php?r=week&z=xlarge&g=holyoke_compute&s=by+name&mc=2&g=allocation_vs_utilization_cpu_report" />
		"""
	else:
		return ""


#--- misc

#syntax highlighting
try:
	from pygments import highlight
	from pygments.lexers import BashLexer
	from pygments.formatters import HtmlFormatter

	lexer = BashLexer()
	formatter = HtmlFormatter()

	syntax_highlight_css = formatter.get_style_defs('.highlight')
	def syntax_highlight(sh):
		return highlight(sh, lexer, formatter)
except ImportError:
	syntax_highlight_css = ''
	def syntax_highlight(sh):
		return '<pre>%s</pre>' % sh

def get_job_script(JobID):
	"""Return the job payload script, or raise NotImplemented if unavailable.

	Return None if there is no job script.
	"""
	if FASRC:
		#at FASRC, we have our slurmctld prolog store the script in a database
		if FASRC_ENV=='prod':
			defaults_file = os.path.abspath(os.path.join(__file__, '..', 'local', 'my.cnf.get_job_script.prod'))
		else:
			defaults_file = os.path.abspath(os.path.join(__file__, '..', 'local', 'my.cnf.get_job_script.dev'))
		shv = ['mysql', '--defaults-file=%s' % defaults_file, '-BNr', '-e', 'select script from jobscripts where id_job = %d;' % int(JobID)]
		stdout = util.runsh(shv)
		if stdout=='': return None
		return stdout
	else:
		raise NotImplementedError("job script retrieval requires implementation in config.py")

def job_script_line_is_interesting(line):
	"""Return whether or not the line of text is worthwhile as a job script preview.

	The given line will be stripped of leading and trailing whitespace and will
	not be the empty string or a comment.
	"""
	for s in (
		'wait',
		'echo',
		'cd',
		'mkdir', '/bin/mkdir',
		'cp', '/bin/cp',
		'rm', '/bin/rm',
		'mv', '/bin/mv',
		'rsync', '/usr/bin/rsync',
		'tar', '/bin/tar',
		'gzip', '/bin/gzip',
		):
		if line==s or line.startswith(s+' '):
			return False
	return True
