# Copyright (c) 2013-2014
# Harvard FAS Research Computing
# All rights reserved.

"""general utilities"""


import os, select, subprocess, socket


#--- basic resource utilization

def get_hostname():
	"""Return the short hostname of the current host."""
	return socket.gethostname().split('.',1)[0]

def get_cpu():
	"""Return the CPU capacity and usage on this host.
	
	The returns a two-item list:
	[total number of cores (int), number of running tasks (int)]
	
	This is just a normal resource computation, independent of Slurm.
	The number of running tasks is from the 4th colum of /proc/loadavg;
	it's decremented by one in order to account for this process asking for it.
	"""
	#running processes
	with open('/proc/loadavg','r') as f:
		#e.g. 52.10 52.07 52.04 53/2016 54847 -> 53-1 = 52
		used = max(int(f.read().split()[3].split('/')[0]) - 1, 0)
	
	with open('/proc/cpuinfo','r') as f:
		total = 0
		for l in f.readlines():
			if l.startswith('processor'):
				total += 1
	
	return total, used

def get_mem():
	"""Return the memory capacity and usage on this host.
	
	This returns a two-item list:
	[total memory in kB (int), used memory in kB (int)]

	This is just a normal resource computation, independent of Slurm.
	The used memory does not count Buffers, Cached, and SwapCached.
	"""
	with open('/proc/meminfo','r') as f:
		total = 0
		free = 0

		for line in f.readlines():
			fields = line.split()
			if fields[0]=='MemTotal:':
				total = int(fields[1])
			if fields[0] in ('MemFree:', 'Buffers:', 'Cached:', 'SwapCached'):
				free += int(fields[1])

		used = total - free

		return total, used


#--- subprocess handling

def shquote(text):
	"""Return the given text as a single, safe string in sh code.

	Note that this leaves literal newlines alone; sh and bash are fine with 
	that, but other tools may require special handling.
	"""
	return "'%s'" % text.replace("'", r"'\''")

def sherrcheck(sh=None, stderr=None, returncode=None, verbose=True):
	"""Raise an exception if the parameters indicate an error.

	This raises an Exception if stderr is non-empty, even if returncode is 
	zero.  Set verbose to False to keep sh and stderr from appearing in the 
	Exception.
	"""
	if (returncode is not None and returncode!=0) or (stderr is not None and stderr!=''):
		msg = "shell code"
		if verbose: msg += " [%s]" % repr(sh)
		if returncode is not None:
			if returncode>=0:
				msg += " failed with exit status [%d]" % returncode
			else:
				msg += " killed by signal [%d]" % -returncode
		if stderr is not None:
			if verbose: msg += ", stderr is [%s]" % repr(stderr)
		raise Exception(msg)

def runsh(sh, inputstr=None):
	"""Run shell code and return stdout.

	This raises an Exception if exit status is non-zero or stderr is non-empty.
	"""
	if type(sh)==type(''):
		shell=True
	else:
		shell=False
	
	if inputstr is None:
		stdin = open('/dev/null', 'r')
		communicate_args = ()
	else:
		stdin = subprocess.PIPE
		communicate_args = (inputstr,)

	p = subprocess.Popen(
		sh,
		shell=shell,
		stdin=stdin,
		stdout=subprocess.PIPE,
		stderr=subprocess.PIPE
	)
	stdout, stderr = p.communicate(*communicate_args)
	sherrcheck(sh, stderr, p.returncode)
	return stdout

def runsh_i(sh):
	"""Run shell code and yield stdout lines.
	
	This raises an Exception if exit status is non-zero or stderr is non-empty. 
	Be sure to fully iterate this or you will probably leave orphans.
	"""
	BLOCK_SIZE = 4096
	if type(sh)==type(''):
		shell=True
	else:
		shell=False
	p = subprocess.Popen(
		sh,
		shell=shell,
		stdin=open('/dev/null', 'r'),
		stdout=subprocess.PIPE,
		stderr=subprocess.PIPE
	)
	stdoutDone, stderrDone = False, False
	stdout = ''
	stderr = ''
	while not (stdoutDone and stderrDone):
		rfds, ignored, ignored2 = select.select([p.stdout.fileno(), p.stderr.fileno()], [], [])
		if p.stdout.fileno() in rfds:
			s = os.read(p.stdout.fileno(), BLOCK_SIZE)
			if s=='':
				stdoutDone = True
			else:
				i = 0
				j = s.find('\n')
				while j!=-1:
					yield stdout + s[i:j+1]
					stdout = ''
					i = j+1
					j = s.find('\n',i)
				stdout += s[i:]
		if p.stderr.fileno() in rfds:
			s = os.read(p.stderr.fileno(), BLOCK_SIZE)
			if s=='':
				stderrDone = True
			else:
				stderr += s
	if stdout!='':
		yield stdout
	sherrcheck(sh, stderr, p.wait())


if __name__=='__main__':
	pass
