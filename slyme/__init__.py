# Copyright (c) 2013-2014
# Harvard FAS Research Computing
# All rights reserved.

"""slyme -- Slurm pYthon Modules based on the Executables"""


from slyme import config


#--- misc

def slurmtime_to_seconds(tstr):
	"""Convert a slurm time to seconds, a float.
	
	Slurm times are MM:SS.SSS, HH:MM:SS, D-HH:MM:SS, etc.
	"""
	t = 0.0
	rest = tstr

	l = rest.split('-')
	if len(l)==1:
		rest = l[0]
	elif len(l)==2:
		t += int(l[0]) * 86400
		rest = l[1]
	else:
		raise ValueError("unable to parse time [%s]" % tstr)
	
	l = rest.split(':')
	if len(l)==2:
		t += 60 * int(l[0])
		t += float(l[1])
	elif len(l)==3:
		t +=  int(l[0]) * 3600
		t +=  int(l[1]) * 60
		t +=  int(l[2])
	else:
		raise ValueError("unable to parse time [%s]" % tstr)
	
	return t

def slurmmemory_to_kB(mem):
	"""Convert the memory string to bytes, an int.
	
	mem is a string such as MaxRSS from `sacct'.  This just assumes slurm is 
	using powers of 10**3, at least until kB, like it is for other memory 
	stats.
	"""
	mem_kB = None
	for s,e in (('K',0), ('M',1), ('G',2), ('T',3), ('P',4)):
		if mem.endswith(s):
			mem_kB = int(round(float(mem[:-1])*1000**e))  #(float because it's often given that way)
			break
	if mem_kB is None:
		if mem=='0':
			return 0
		raise Exception("un-parsable mem [%r]" % mem)
	return mem_kB

def AllocMem_to_kB(AllocMem):
	"""Convert the AllocMem string to bytes, an int.

	AllocMem is a string from `scontrol show node'. Since, comparing to 
	/proc/meminfo, RealMemory MB is 10**3 kB (and NOT 2**10 kB), this assumes 
	slurm is treating AllocMem the same.
	"""
	try:
		return int(AllocMem)*1000
	except (ValueError,TypeError):
		raise Exception("un-parsable MaxRSS [%r]" % MaxRSS)

def job_script_preview(JobScript):
	"""Return a representative line from the JobScript.
	
	This may return the empty string.
	"""
	txt = JobScript
	line = ''
	while txt!='':
		txt, line = [ s.strip() for s in txt.rsplit('\n',1) ]
		if line=='' or line.startswith('#'):
			continue
		if config.job_script_line_is_interesting(line):
			return line
	return line


if __name__=='__main__':
	#check slurmtime_to_seconds()
	for tstr, t in (
		('4-18:29:01', 412141),
		('05:03:43', 18223),
		('01:09.666', 70),
		('00:09.666', 10),
		):
		t2 = int(round(slurmtime_to_seconds(tstr)))
		assert t2 == t, "%s != %s, instead got %s" % (tstr, t, t2)
