# Copyright (c) 2013-2014
# Harvard FAS Research Computing
# All rights reserved.

"""slurmmon job handling"""


import sys, re
import slurmmon
from slurmmon import config, util, lazydict


#sacct format; you can change _sacct_format_readable at will, but changing _sacct_format_parsable will break the code
_sacct_format_parsable = 'User    ,JobID    ,JobName   ,State,Partition   ,NCPUS,NNodes,CPUTime   ,TotalCPU   ,UserCPU   ,SystemCPU   ,ReqMem,MaxRSS,Start,End,NodeList'.replace(' ','')
_sacct_format_readable = 'User%-12,JobID%-15,JobName%20,State,Partition%18,NCPUS,NNodes,CPUTime%13,TotalCPU%13,UserCPU%13,SystemCPU%13,ReqMem,MaxRSS,Start,End,NodeList%-500'.replace(' ','')


#--- a representation of a Job

class x_ReqMem_bytes_total_from_per_core(lazydict.Extension):
	source = ('ReqMem_bytes_per_core', 'NCPUS',)
	target = ('ReqMem_bytes_total')
	def __call__(self, ReqMem_bytes_per_core, NCPUS):
		return ReqMem_bytes_per_core * NCPUS,

class x_ReqMem_bytes_total_from_per_node(lazydict.Extension):
	source = ('ReqMem_bytes_per_node', 'NNodes',)
	target = ('ReqMem_bytes_total')
	def __call__(self, ReqMem_bytes_per_node, NNodes):
		return ReqMem_bytes_per_node * NNodes,

class x_CPU_Efficiency(lazydict.Extension):
	source = ('TotalCPU', 'CPUTime',)
	target = ('CPU_Efficiency',)
	def __call__(self, TotalCPU, CPUTime):
		if TotalCPU != 0 and CPUTime != 0:
			return float(TotalCPU)/CPUTime,
		return None,

class x_CPU_Wasted(lazydict.Extension):
	source = ('TotalCPU', 'CPUTime',)
	target = ('CPU_Wasted',)
	def __call__(self, TotalCPU, CPUTime):
		return max(self['CPUTime'] - self['TotalCPU'], 0),

class x_JobScript(lazydict.Extension):
	source= ('JobID',)
	target = ('JobScript',)
	def __call__(self, JobID):
		return config.get_job_script(self['JobID']),

class x_JobScriptPreview(lazydict.Extension):
	source = ('JobScript',)
	target = ('JobScriptPreview',)
	def __call__(self, JobScript):
		return slurmmon.job_script_preview(JobScript, self),

class x_SacctReport(lazydict.Extension):
	source= ('JobID',)
	target = ('SacctReport',)
	def __call__(self, JobID):
		shv = ['sacct', '--format', _sacct_format_readable, '-j', self['JobID']]
		return util.runsh(shv).rstrip(),

class Job(lazydict.LazyDict):
	"""A representation of a slurm job, mainly in sacct context.

	Attributes are named to match sacct's variables very closely.
	Plus, some derived attributes are added, and some are clarified or made consistent, e.g. MaxRSS becomes MaxRSS_kB.
	It only represents overall jobs, not steps.
	For variables that are step-specific, the value here for the job is the maximum for any given step.

	Currently, this is all geared towards getting data about completed jobs.
	In particular, it is not meant for job control.
	"""

	keys = [
		#=== data from sacct

		#--- info from main job account line

		'JobID',
		#str, but currently always representing an integer (no ".STEP_ID")
		
		'User',
		#str
		
		'JobName',
		#str
		
		'State',
		#str
		
		'Partition',
		#str
		
		'NCPUS',
		#int
		
		'NNodes',
		#int

		'CPUTime',
		#seconds, float
		
		'TotalCPU',
		#seconds, float
		
		'UserCPU',
		#seconds, float
		
		'SystemCPU',
		#seconds, float

		#--- max of any main job account line or any steps

		'MaxRSS_kB',
		#bytes in kB, int
		
		'ReqMem_bytes_per_node',
		#bytes, int, or None if not used
		
		'ReqMem_bytes_per_core',
		#bytes, int, or None if not used


		#=== derived data

		'ReqMem_bytes_total',
		#bytes, int, or None if not used
		#a computation combining the appropriate request per resource and number of resources

		'CPU_Efficiency',
		#float, should be in the range [0.0,1.0), but nothing guarantees that
		
		'CPU_Wasted',
		#seconds, float


		#=== other
		
		'JobScript',
		#the text of the job payload script

		'JobScriptPreview',
		#a one-line, (hopefully) representative preview of the JobScript

		'SacctReport',
		#an sacct report, formatted for humans and containing headers
	]

	extensions = [
		x_ReqMem_bytes_total_from_per_core(),
		x_ReqMem_bytes_total_from_per_node(),
		x_CPU_Efficiency(),
		x_CPU_Wasted(),
		x_JobScript(),
		x_JobScriptPreview(),
		x_SacctReport(),
	]

	def __str__(self):
		try:
			return '<JobID %s>' % self['JobID']
		except KeyError:
			return '<JobID n/a (obj id %s)>' % id(self)  #subject to change


#--- commands

re_sbatch_output = re.compile('Submitted batch job (\d+)\n')

def submit(job):
	"""Submit the given job.

	The given job must have a JobScript, which may have `#SBATCH' lines.

	This modifies the job:
		* sets its JobID
	"""
	if not job.has_key('JobScript'):
		raise Exception("*** ERROR *** cannot submit job [%s], it has no JobScript" % j)

	stdout = util.runsh(['sbatch'], job['JobScript'])
	try:
		job['JobID'] = re_sbatch_output.match(stdout).group(1)
	except (AttributeError, IndexError):
		raise Exception("*** ERROR *** unexpected output from sbatch: %s" % repr(stdout))


#--- job retrieval

def _yield_raw_sacct_job_lines(state='COMPLETED', starttime=None, endtime=None):
	"""Return an iterator that yields lines from sacct."""
	shv = ['sacct', '--allusers', '--noheader', '--parsable2', '--format', _sacct_format_parsable]
	if state is not None:
		shv.extend(['--state', state])
	if starttime is not None:
		shv.extend(['--starttime', starttime.strftime('%m/%d-%H:%M')])
	if endtime is not None:
		shv.extend(['--endtime', endtime.strftime('%m/%d-%H:%M')])
	return util.runsh_i(shv)

def _yield_raw_sacct_job_text_blocks(state='COMPLETED', starttime=None, endtime=None):
	"""Yields multi-line strings of sacct text for each job.

	state can, in theory, be any string accepted by sacct --state.
	However, this has only been tested with state='COMPLETED' -- there will probably be ValueErrors with anything else.
	
	starttime and endtime should be datetime objects.
	"""
	
	#this will be the text that's yielded
	text = ''

	for line in _yield_raw_sacct_job_lines(state=state, starttime=starttime, endtime=endtime):
		if line.startswith('|'):
			text += line
		else:
			if text!='': yield text
			text = line
	
	if text!='':
		yield text

def load_data_from_sacct_text_block(job, saccttext):
	"""Load data into job from a multi-line, parsable sacct block of text.
	
	This does not respect the internal laziness setting -- everything 
	possible is loaded.
	"""
	try:
		for line in saccttext.split('\n'):
			line = line.strip()
			if line=='':
				continue

			User,JobID,JobName,State,Partition,NCPUS,NNodes,CPUTime,TotalCPU,UserCPU,SystemCPU,ReqMem,MaxRSS,Start,End,NodeList = line.split('|')
			
			#convert JobID to just the base id, and set an extra JobStep variable with the step key
			JobStep = ''
			if '.' in JobID:
				JobID, JobStep = JobID.split('.')
	
			if JobStep=='':
				#this is the main job line

				#these things should be present in this main line and better than any data in the job steps
				job['JobID'] = JobID
				job['User'] = User
				job['JobName'] = JobName
				job['State'] = State
				job['Partition'] = Partition
				job['NCPUS'] = int(NCPUS)
				job['NNodes'] = int(NNodes)
				job['CPUTime'] = slurmmon.slurmtime_to_seconds(CPUTime)
				job['TotalCPU'] = slurmmon.slurmtime_to_seconds(TotalCPU)
				job['UserCPU'] = slurmmon.slurmtime_to_seconds(UserCPU)
				job['SystemCPU'] = slurmmon.slurmtime_to_seconds(SystemCPU)

				continue
			else:
				#these are the job steps after the main entry

				#ReqMem
				if ReqMem.endswith('Mn'):
					ReqMem_bytes_per_node = int(ReqMem[:-2])*1024**2
					if job.has_key('ReqMem_bytes_per_node'):
						ReqMem_bytes_per_node = max(job['ReqMem_bytes_per_node'], ReqMem_bytes_per_node)
					job['ReqMem_bytes_per_node'] = ReqMem_bytes_per_node
					job['ReqMem_bytes_per_core'] = None
				elif ReqMem.endswith('Mc'):
					ReqMem_bytes_per_core = int(ReqMem[:-2])*1024**2
					if job.has_key('ReqMem_bytes_per_core'):
						ReqMem_bytes_per_core = max(job['ReqMem_bytes_per_core'], ReqMem_bytes_per_core)
					job['ReqMem_bytes_per_node'] = None
					job['ReqMem_bytes_per_core'] = ReqMem_bytes_per_core
					
				#MaxRSS
				MaxRSS_kB = slurmmon.MaxRSS_to_kB(MaxRSS)
				if job.has_key('MaxRSS_kB'):
					MaxRSS_kB = max(job['MaxRSS_kB'], MaxRSS_kB)
				job['MaxRSS_kB'] = MaxRSS_kB

	except Exception, e:
		raise Exception("unable to parse sacct job text [%r]: %r\n" % (saccttext, e))

def get_jobs(state='COMPLETED', starttime=None, endtime=None, filter=lambda j: True):
	"""Yield Job objects that match the given parameters."""
	for saccttext in _yield_raw_sacct_job_text_blocks(state=state, starttime=starttime, endtime=endtime):
		j = Job()
		load_data_from_sacct_text_block(j, saccttext)
		if filter(j):
			yield j

def get_jobs_running_on_host(hostname):
	"""Return jobs running on the given host."""
	shv = ['squeue', '-o', '%A %u %C %D', '--noheader', '-w', hostname]
	stdout = util.runsh(shv).strip()
	for line in stdout.split('\n'):
		line = line.strip()
		try:
			JobID, User, NCPUS, NNodes = line.split()
			
			j = Job()
			j['JobID'] = JobID
			j['User'] = User
			j['NCPUS'] = NCPUS
			j['NNodes'] = NNodes

			yield j

		except Exception, e:
			sys.stderr.write("*** ERROR *** unable to parse squeue job text [%r]: %s\n" % (line, e))


#--- utilities

def job_html_report(job, syntax_highlight_css=config.syntax_highlight_css, syntax_highlight=config.syntax_highlight):
	"""Return a full html page report on the given job."""
	html = '<html>'
	html += '<head><title>%s</title>' % job['JobID']
	html += '<style>\n%s\n</style>' % syntax_highlight_css
	html += '</head>'
	html += '<body><h1>%s</h1><hr />' % job['JobID']
	html += config.syntax_highlight(job['JobScript'])
	html += '<br /><hr /><br />'
	html += '\n<pre>%s</pre>\n' % job['SacctReport']
	html += '<br />'
	html += '</body></html>'
	return html
