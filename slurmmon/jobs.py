# Copyright (c) 2013-2014
# Harvard FAS Research Computing
# All rights reserved.

"""slurmmon job handling"""


import sys, re
import slurmmon
from slurmmon import config, util, lazydict


#sacct format; you can change _sacct_format_readable at will, but changing _sacct_format_parsable will break the code
_sacct_format_parsable = 'User    ,JobID    ,JobName   ,State,Partition   ,NCPUS,NNodes,CPUTime   ,TotalCPU   ,UserCPU   ,SystemCPU   ,ReqMem,MaxRSS,Submit,Start,End,NodeList'.replace(' ','')
_sacct_format_readable = 'User%-12,JobID%-15,JobName%20,State,Partition%18,NCPUS,NNodes,CPUTime%13,TotalCPU%13,UserCPU%13,SystemCPU%13,ReqMem,MaxRSS,Submit,Start,End,NodeList%-500'.replace(' ','')


keys_sacct = (
	'User',
	'JobID',
	'JobName',
	'State',
	'Partition',
	'NCPUS',
	'NNodes',
	'CPUTime',
	'TotalCPU',
	'UserCPU',
	'SystemCPU',
	'ReqMem',
	'MaxRSS',
	'Submit',
	'Start',
	'End',
	'NodeList',
)


#--- a representation of a Job

scontrol_key_value_translations = {
	#translate scontrol key/value pairs to those used by the Job (which match 
	#sacct's as closely as possible, so this is also basically a translation to 
	#sacct key/value
	
	'UserID':
		lambda k, v: ('User', v.split('(')[0]),
	'JobState':
		lambda k, v: ('State', v),
	'Name':
		lambda k, v: ('JobName', v),
	'NumNodes':
		lambda k, v: ('NNodes', v),
	'NumCPUs':
		lambda k, v: ('NCPUS', v),
	'MinMemoryNode':
		lambda k, v: ('ReqMem_bytes_per_node', slurmmon.slurmmemory_to_kB(v)),
	'MinMemoryCPU':
		lambda k, v: ('ReqMem_bytes_per_core', slurmmon.slurmmemory_to_kB(v)),
}

class x_scontrol(lazydict.Extension):
	source = ('JobID',)
	target = (
		'User',
		'JobName',
		'State',
		'Partition',
		'NNodes',
		'NCPUS',
		'ReqMem_bytes_per_node',
		'ReqMem_bytes_per_core',
	)
	def __call__(self, JobID):
		try:
			scontroltext = _yield_raw_scontrol_job_text_blocks(jobs=[JobID]).next()
		except util.ShError, e:
			#if it's from an unrecognized JobID, then this extension can do nothing
			if hasattr(e, 'stderr') and e.stderr.startswith('slurm_load_jobs error: Invalid job id specified'):
				return [None]*len(x_scontrol.target)
		except StopIteration:
			#the single iteration yielded nothing
			#(I doubt this every actually happens -- the above `Invalid job id' happens)
			return [None]*len(x_scontrol.target)

		#the final values (initialize to None)
		d = dict.fromkeys(self.target)

		try:
			for kv in scontroltext.split():
				k, v = kv.split('=',1)
				try:
					k, v = scontrol_key_value_translations[k](k, v)
				except KeyError:
					pass
				d[k] = v
		except Exception, e:
			##hiding the actual error only makes things difficult
			#raise Exception("unable to parse scontrol job text [%r]: %r\n" % (saccttext, e))
			raise

		##debug
		#if True:
		#	for k, v in d.items():
		#		print 'scontrol value: %s=%s' % (k, v)

		return [ d[k] for k in x_scontrol.target ]

class x_sacct(lazydict.Extension):
	source = ('JobID',)
	target = (
		'User',
		'JobName',
		'State',
		'Partition',
		'NCPUS',
		'NNodes',
		'CPUTime',
		'TotalCPU',
		'UserCPU',
		'SystemCPU',
		'MaxRSS_kB',
		'ReqMem_bytes_per_core',
		'ReqMem_bytes_per_node',
		'NodeList_str',
	)
	def __call__(self, JobID):
		try:
			saccttext = _yield_raw_sacct_job_text_blocks(jobs=[JobID]).next()
		except StopIteration:
			return [None]*len(self.target)
		
		#the final values (initialize to None)
		d = dict.fromkeys(self.target)

		try:
			for line in saccttext.split('\n'):
				line = line.strip()
				if line=='':
					continue
		

				#the step (or whater line this is) value
				dstep = dict(zip(keys_sacct,line.split('|')))

				#convert JobID to just the base id, and set an extra JobStep variable with the step key
				dstep['JobStep'] = ''
				if '.' in dstep['JobID']:
					dstep['JobID'], dstep['JobStep'] = dstep['JobID'].split('.')
		
				if dstep['JobStep']=='':
					#this is the main job line (the top one)

					#these things should be present in this main line and better than any data in the job steps
					
					d['User'] = dstep['User']
					d['JobName'] = dstep['JobName']
					d['State'] = dstep['State']
					d['Partition'] = dstep['Partition']
					d['NCPUS'] = int(dstep['NCPUS'])
					d['NNodes'] = int(dstep['NNodes'])
					d['CPUTime'] = slurmmon.slurmtime_to_seconds(dstep['CPUTime'])
					d['TotalCPU'] = slurmmon.slurmtime_to_seconds(dstep['TotalCPU'])
					d['UserCPU'] = slurmmon.slurmtime_to_seconds(dstep['UserCPU'])
					d['SystemCPU'] = slurmmon.slurmtime_to_seconds(dstep['SystemCPU'])
					d['NodeList_str'] = dstep['NodeList']

					continue
				else:
					#these are the job steps after the main entry

					#ReqMem
					if dstep['ReqMem'].endswith('Mn'):
						dstep['ReqMem_bytes_per_node'] = int(dstep['ReqMem'][:-2])*1024**2
						if d['ReqMem_bytes_per_node'] is not None:
							d['ReqMem_bytes_per_node'] = max(d['ReqMem_bytes_per_node'], dstep['ReqMem_bytes_per_node'])
						##assume consistency, i.e. that nothing set this
						#d['ReqMem_bytes_per_core'] = None
					elif dstep['ReqMem'].endswith('Mc'):
						dstep['ReqMem_bytes_per_core'] = int(dstep['ReqMem'][:-2])*1024**2
						if d['ReqMem_bytes_per_core'] is not None:
							d['ReqMem_bytes_per_cored'] = max(d['ReqMem_bytes_per_core'], dstep['ReqMem_bytes_per_core'])
						##assume consistency, i.e. that nothing set this
						#d['ReqMem_bytes_per_node'] = None
						
					#MaxRSS
					if dstep['MaxRSS'] is not None:
						d['MaxRSS_kB'] = max(d['MaxRSS_kB'], slurmmon.slurmmemory_to_kB(dstep['MaxRSS']))
		except Exception, e:
			##hiding the actual error only makes things difficult
			#raise Exception("unable to parse sacct job text [%r]: %r\n" % (saccttext, e))
			raise

		return tuple(d[k] for k in self.target)

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
		return max(CPUTime - TotalCPU, 0),

class x_JobScript(lazydict.Extension):
	source= ('JobID',)
	target = ('JobScript',)
	def __call__(self, JobID):
		return config.get_job_script(JobID),

class x_JobScriptPreview(lazydict.Extension):
	source = ('JobScript',)
	target = ('JobScriptPreview',)
	def __call__(self, JobScript):
		return slurmmon.job_script_preview(JobScript),

class x_SacctReport(lazydict.Extension):
	source= ('JobID',)
	target = ('SacctReport',)
	def __call__(self, JobID):
		shv = ['sacct', '--format', _sacct_format_readable, '-j', JobID]
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

		'NodeList_str'
		#str, the compact represntation, e.g. host[18301-18302,18308,20208]

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
		x_scontrol(),
		x_sacct(),
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
	return job

def update(job):
	try:
		job.pop('State')
	except KeyError:
		pass
	else:
		job['State']
	return job



#--- job retrieval

def _yield_raw_sacct_job_lines(state='COMPLETED', users=None, jobs=None, starttime=None, endtime=None):
	"""Return an iterator that yields lines from sacct."""
	shv = ['sacct',  '--noheader', '--parsable2', '--format', _sacct_format_parsable]
	
	if state is not None:
		shv.extend(['--state', state])
	
	if jobs is not None:
		shv.extend(['--jobs', ','.join(jobs)])
	
	if users is not None:
		shv.extend(['--user', ','.join(users)])
	else:
		shv.extend(['--allusers'])

	if starttime is not None:
		shv.extend(['--starttime', starttime.strftime('%m/%d-%H:%M')])
	
	if endtime is not None:
		shv.extend(['--endtime', endtime.strftime('%m/%d-%H:%M')])
	
	return util.runsh_i(shv)

def _yield_raw_sacct_job_text_blocks(state='COMPLETED', users=None, jobs=None, starttime=None, endtime=None):
	"""Yields multi-line strings of sacct text for each job.

	state can, in theory, be any string accepted by sacct --state.
	However, this has only been tested with state='COMPLETED' -- there will probably be ValueErrors with anything else.
	
	starttime and endtime should be datetime objects.
	"""
	
	#this will be the text that's yielded
	text = ''

	for line in _yield_raw_sacct_job_lines(state=state, users=users, jobs=jobs, starttime=starttime, endtime=endtime):
		if line.startswith('|'):
			text += line
		else:
			if text!='': yield text
			text = line
	
	if text!='':
		yield text

def _yield_raw_scontrol_job_text_blocks(jobs=None):
	"""Yields strings of scontrol text for each job.

	These are just single-line, not text blocks as the name implies, but it's 
	named that way for consistency (the names should be changed, consistently).
	"""
	shv = ['scontrol', '--oneliner', 'show', 'job' ]
	
	if jobs is not None:
		shv.extend(jobs)
	
	return util.runsh_i(shv)

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

			User,JobID,JobName,State,Partition,NCPUS,NNodes,CPUTime,TotalCPU,UserCPU,SystemCPU,ReqMem,MaxRSS,Submit,Start,End,NodeList = line.split('|')
			
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
				job['NodeList_str'] = NodeList

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
				MaxRSS_kB = slurmmon.slurmmemory_to_kB(MaxRSS)
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
