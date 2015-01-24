# Copyright (c) 2013-2014
# Harvard FAS Research Computing
# All rights reserved.

"""
slyme -- Slurm pYthon Modules based on the Executables

The main class, Slurm, is a collection of static class methods for interacting
with a Slurm system.

"""

import copy
import re

from hex import Command
from jobreports import JobReport

#--- setup logging
import logging
#(logging.NullHandler was introduced in 2.7, and this code is 2.6 compatible)
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
logger = logging.getLogger('slyme')
logger.addHandler(NullHandler())


DEFAULT_SLURM_CONF_FILE = '/etc/slurm/slurm.conf'

#--- misc
class Slurm(object):
    """
    Collection of static methods for interacting with a Slurm system
    """
    conf = None
    squeue = Command.load("squeue",path="conf/default/squeue.json")
    sbatch = Command.load("sbatch",path="conf/default/sbatch.json")
    scancel = Command.load("scancel",path="conf/default/scancel.json")
    
    @classmethod
    def getJobStatus(cls,jobid):
        """
        Uses squeue, then sacct to determine job status.  Status value is 
        returned.
        """
        squeue = copy.deepcopy(Slurm.squeue)
        squeue.reset()
        squeue.jobs = jobid
        squeue.noheader = True
        squeue.format = "%%T"
        [returncode,stdout,stderr] = squeue.run()
        if stdout is not None and stdout.strip() != "":
            logger.info("Status of jobid %s is %s" % (str(jobid),stdout))
            return stdout
        else:
            """
            Try sacct if squeue doesn't return anything
            """
            sacct = copy.deepcopy(Slurm.sacct)
            sacct.reset()
            sacct.jobs = "%s.batch" % jobid
            sacct.format = "State"
            sacct.noheader = True
            [returncode,stdout,stderr] = sacct.run()
            if returncode != 0:
                raise Exception("sacct failed %s" % sacct.composeCmdString())
            logger.info("Status of jobid %s is %s" % (str(jobid),stdout))
            return stdout

    
    @classmethod
    def getConfigValue(cls,key):
        """
        Get a slurm.conf value.  Calls loadConfig if needed.
        """
        if Slurm.conf is None:
            Slurm.loadConfig()
        if key not in Slurm.conf:
            raise Exception("Slurm config has no key %s" % key)
        return Slurm.conf[key]
        
    
    @classmethod
    def loadConfig(cls,conffile=DEFAULT_SLURM_CONF_FILE):
        '''
        Constructs the object using the given slurm.conf file name.
        If this is called more than once, the values will be reloaded.
        
        If there are backslashes at the end of the line it's concatenated
        to the next one.
        
        NodeName lines are not saved because of the stupid DEFAULT stuff.  
        Maybe someday.
        '''
        logger.debug("Initializing Slurm config using %s" % conffile)
        Slurm.conf = dict()
        currline = ''
        m = re.compile(r'([^=]+)\s*=\s*(.*)') #Used to extract name=value 
        n = re.compile(r'(\S+)\s+(.*)')       #Parse values on PartitionName
        with open(conffile,'rt') as f:
            for line in f:
                line = line.rstrip().lstrip()
                if line.startswith('#') or line.isspace() or not line:
                    continue
            
                # Concatenate lines with escaped line ending
                if line.endswith('\\'):
                    logger.debug("Concatenating line %s" % line)
                    currline += line.rstrip('\\')
                    continue
                
                currline += line
                
                # Skip nodename lines
                if currline.startswith('NodeName'):
                    currline = ''
                    continue
                
                # Split on first equal
                result = m.match(currline)
                if result is not None:
                    name = result.group(1)
                    value = result.group(2)
                    
                    # For PartitionName lines, we need to extract the name 
                    # and add it to the Partitions list
                    if name == 'PartitionName':
                        result2 = n.match(value)
                        if result2 is None:
                            logger.info("Bad PartitionName value %s.  Skipping." \
                                % value)
                            continue
                        pname = result2.group(1)
                        pvalue = result2.group(2)
                        if 'Partitions' not in Slurm.conf:
                            Slurm.conf['Partitions'] = dict()
                        Slurm.conf['Partitions'][pname] = pvalue
                    else:                            
                        Slurm.conf[name] = value
                else:
                    logger.error("Slurm config file %s has strange line '%s'" % (conffile,currline))
                
                currline = ''
    
    @classmethod
    def killJob(cls,jobid):
        """
        Uses scancel to kill the specified job
        """
        scancel = copy.deepcopy(Slurm.scancel)
        scancel.jobid = jobid
        [returncode,stdout,stderr] = scancel.run()
        if returncode != 0:
            raise Exception("scancel command failed %s" % stderr)
        
    
    @classmethod
    def submitJob(cls,command,**kwargs):
        """
        Uses SbatchCommand to submit a job.  The following environment variables
        are used to set parameters first.
        
        Any slurm parameters that are set as keyword args will override the 
        environment variables.
        """
        sbatch = copy.deepcopy(Slurm.sbatch)
        sbatch.command = command
                
        for arg,value in kwargs.iteritems():
            if arg == "scriptpath":
                sbatch.scriptpath = value
            else:
                sbatch.setArgValue(arg,value)
        logger.info("sbatch command %s" % sbatch)
        
        
        [returncode,stdout,stderr] = sbatch.run()
        
        if returncode != 0:
            raise Exception("sbatch command failed: %s" % stderr)
        
        jobid = stdout.split()[-1]
        return jobid
    
    @classmethod
    def getJobReports(cls,**kwargs):
        return JobReport.fetch(**kwargs)
    
    @classmethod
    def slurm_time_interval_to_seconds(cls,tstr):
        """Convert a slurm time interval to seconds, a float.
    
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
    
    @classmethod
    def datetime_to_slurm_timestamp(cls,td):
        """Convert a datetime to a string format slurm understands.
    
        This uses the YYYY-MM-DDTHH:MM:SS format, one of many understood
        by slurm.
        """
        return td.strftime('%Y-%m-%dT%H:%M:%S')
    
    @classmethod
    def slurmmemory_to_kB(cls,mem):
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
    
    @classmethod
    def AllocMem_to_kB(cls,AllocMem):
        """Convert the AllocMem string to bytes, an int.
    
        AllocMem is a string from `scontrol show node'. Since, comparing to
        /proc/meminfo, RealMemory MB is 10**3 kB (and NOT 2**10 kB), this assumes
        slurm is treating AllocMem the same.
        """
        try:
            return int(AllocMem)*1000
        except (ValueError,TypeError):
            raise Exception("un-parsable AllocMem [%r]" % AllocMem)
    