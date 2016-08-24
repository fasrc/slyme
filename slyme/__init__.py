# Copyright (c) 2013-2014
# Harvard FAS Research Computing
# All rights reserved.

"""
slyme -- Slurm pYthon Modules based on the Executables

The main class, Slurm, is a collection of static cllass methods for interacting
with a Slurm system.

"""
import os
import copy
import re
from datetime import datetime
from hex import Command
from jobreports import JobReport,JobStep
from util import runsh_i

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
    squeue = None
    scancel = None
    sbatch = None
    
    _sacct_format_parsable = \
        'JobID  ,User      ,JobName    ,State    ,Partition  ,NCPUS  ,\
         NNodes ,CPUTime   ,TotalCPU   ,UserCPU  ,SystemCPU  ,ReqMem ,MaxRSS,\
         Start  ,End       ,NodeList   ,Elapsed  ,MaxVMSize  ,AveVMSize'.replace(' ','')

    @classmethod
    def initcmds(cls):
        """
        I'd like to initialize these at compile time, but I can't.  This is called
        by the functions that use the slurm commands.
        """
        if Slurm.squeue is None or Slurm.sbatch is None or Slurm.scancel is None:
            Slurm.squeue = Command.load("squeue",path=os.path.join(os.path.dirname(__file__),"conf/14.03.8"))
            Slurm.sbatch = Command.load("sbatch",path=os.path.join(os.path.dirname(__file__),"conf/14.03.8"))
            Slurm.scancel = Command.load("scancel",path=os.path.join(os.path.dirname(__file__),"conf/14.03.8"))
    
    
    @classmethod
    def getJobStatus(cls,jobid):
        """
        Uses squeue, then sacct to determine job status.  Status value is 
        returned.
        """
        Slurm.initcmds()
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
        Slurm.initcmds()
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
        Slurm.initcmds()
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
    def slurmtime_to_seconds(cls,tstr):
        """Convert a slurm time to seconds, a float.
        
        Slurm times are MM:SS.SSS, HH:MM:SS, D-HH:MM:SS, etc.
        """
        t = 0.0
        if tstr.strip() == "":
            return t
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
    def MaxRSS_to_kB(cls,MaxRSS):
        """Convert the MaxRSS string to bytes, an int.
        
        MaxRSS is the string from `sacct'.  This just assumes slurm is using powers 
        of 10**3, at least until kB, like it is for other memory stats.
        """
        
        # Handle this weird thing in the sacct lines that are not .batch
        if MaxRSS=='16?':
            return 0
        MaxRSS_kB = None
        for s,e in (('K',0), ('M',1), ('G',2), ('T',3), ('P',4)):
            if MaxRSS.endswith(s):
                MaxRSS_kB = int(round(float(MaxRSS[:-1])*1000**e))  #(float because it's often given that way)
                break
        if MaxRSS_kB is None:
            if MaxRSS=='0':
                return 0
            raise Exception("un-parsable MaxRSS [%r]" % MaxRSS)
        return MaxRSS_kB
    
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
        
    @classmethod
    def _yield_raw_sacct_job_text_blocks(cls,**kwargs):
        """
        Yields multi-line strings of sacct text for each job.
        """
        logger.debug("yielding sacct text with args %s" % kwargs)
        
        # If an command line executor is defined in the arguments, use that
        # otherwise, use runsh_i
        executor = runsh_i
        if 'execfunc' in kwargs:
            executor = kwargs['execfunc']
                        
        
        shv = ['sacct', '--noheader', '--parsable2', '--format', Slurm._sacct_format_parsable]            
        
        # Set of parameters that can't be passed along because they would 
        # interfere with JobStep creation
        badparams = ['brief','helpformat','help','long','format','parsable',\
                     'parsable2','usage','verbose','version']
        
        # Command switches without an argument
        boolean = ['allusers', 'completion', 'duplicates','allclusters','truncate']
        
        if kwargs is not None:
            # Throw exception if it's in the badparams list
            if any(key in badparams for key in kwargs):
                raise Exception("The following sacct parameters can not be used when fetching jobs: %s" % ','.join(badparams))
            
            # Go through the kwargs and append to the command
            for key, value in kwargs.iteritems():
                
                key = key.strip()
                
                # If it's a boolean, just take the key
                if key in boolean:
                    shv.extend(['--%s' % key])
                else:
                    shv.extend(['--%s' % key, value])
                            
                    
        #this will be the text that's yielded
        text = ''
    
        #for line in open('_fake_data/sacct_alljobs_parsable.out').readlines():
        # Execute the sacct command
        #print("Executing with %s" % execfunc)
        for line in executor(shv):
            logger.debug("Command output line %s" % line)
            if line.startswith('|'):
                text += line
            else:
                if text!='': yield text
                text = line
        
        if text!='':
            yield text
            
    @classmethod
    def getJobReports(cls,**kwargs):
        """
        Yield JobReport objects that match the given parameters.  
        
        Each row in the output is used to create a JobStep.  Once the job steps
        are collected, a JobReport is created and yielded.  Assumes that 
        jobsteps come out in sequence (though it doesn't matter which one is
        first.
        """
        
        # Regular expression for testing for state "CANCELLED by <uid>"
        cancelledbyre = re.compile(r'CANCELLED by (\d+)')
        
        jobsteps = []
        currentjobid = None
        for saccttext in Slurm._yield_raw_sacct_job_text_blocks(**kwargs):
            for line in saccttext.split('\n'):
                line = line.strip()
                if line=='':
                    continue
                
                # Parse the sacct output
                # If there is a ValueError, there is probably a pipe in the 
                # command string
                JobID = User = JobName = State = Partition = NCPUS = NNodes = CPUTime = \
                        TotalCPU = UserCPU = SystemCPU = ReqMem = MaxRSS = Start = End = \
                        NodeList = Elapsed = MaxVMSize = AveVMSize = None
                try:

                    JobID,User,JobName,State,Partition,NCPUS,NNodes,CPUTime,\
                        TotalCPU,UserCPU,SystemCPU,ReqMem,MaxRSS,Start,End,\
                        NodeList,Elapsed,MaxVMSize,AveVMSize = line.split("|")
                    logger.debug("User %s, JobID %s" % (User,JobID))
                except ValueError, e:
                    print "unable to parse sacct job text [%r]: %r\n" % (saccttext, e)
                    
                    # Probably due to pipes in the JobName, so try alternate parsing strategy
                    # result = re.match(r'([^\|]+)\|([^\|]+)\|(.*?)\|(BOOT_FAIL|CANCELLED|COMPLETED|FAILED|NODE_FAIL|PREEMPTED|TIMEOUT)\|(.*)',line)
                    result = re.match(r'(.*?)\|(BOOT_FAIL|CANCELLED|COMPLETED|FAILED|NODE_FAIL|PREEMPTED|TIMEOUT)\|(.*)',line)
                    if result is not None:
                        fields = result.group(1).split('|')
                        JobID   = fields[0]
                        User    = fields[1]
                        JobName = "".join(fields[2:])
                        State   = result.group(2)
                        remainder = result.group(3)
                        Partition,NCPUS,NNodes,CPUTime, \
                            TotalCPU,UserCPU,SystemCPU,ReqMem,MaxRSS,Start,End,\
                            NodeList,Elapsed,MaxVMSize,AveVMSize = remainder.split("|")
                    else:
                        print "Second attempt to parse sacct job text failed.  Giving up on this one."
                        continue
                
                # Convert JobID to just the base id, and set an extra 
                # JobStepName variable with the step key
                JobStepName = ''
                if '.' in JobID:
                    JobID, JobStepName = JobID.split('.')
                
                if currentjobid is None:
                    currentjobid = JobID
                    
                # If this is a new JobID, yield the last one
                if JobID != currentjobid:
                    logger.debug("---New JobID %s" % JobID)
                    currentjobid = JobID
                    yield JobReport(jobsteps)
                    jobsteps = []
    
                j = JobStep()
                j.JobID         = JobID
                j.JobStepName   = JobStepName
                j.User          = User
                j.JobName       = JobName
                
                m1 = cancelledbyre.match(State)
                CancelledBy = None
                if m1 is not None:
                    CancelledBy = m1.group(1)
                    State = 'CANCELLED'
                
                j.State         = State
                j.CancelledBy   = CancelledBy
                j.Partition     = Partition
                j.NCPUS         = int(NCPUS)
                j.NNodes        = int(NNodes)
                j.CPUTime       = Slurm.slurmtime_to_seconds(CPUTime)
                j.TotalCPU      = Slurm.slurmtime_to_seconds(TotalCPU)
                j.UserCPU       = Slurm.slurmtime_to_seconds(UserCPU)
                j.SystemCPU     = Slurm.slurmtime_to_seconds(SystemCPU)
                j.Elapsed       = Slurm.slurmtime_to_seconds(Elapsed)
                
                starttime = None
                if Start and Start != 'Unknown':
                    starttime = datetime.strptime(Start,"%Y-%m-%dT%H:%M:%S")
                j.Start         = starttime
                
                endtime = None
                if End and End != 'Unknown':
                    endtime = datetime.strptime(End,"%Y-%m-%dT%H:%M:%S")
                j.End           = endtime
                
                j.NodeList      = NodeList

                #these are the job steps after the main entry

                #ReqMem
                j.ReqMem_bytes = 0

                if ReqMem.endswith('Mn'):
                    ReqMem_bytes_per_node = int(ReqMem[:-2])*1024**2
                    j.ReqMem_bytes_per_node = ReqMem_bytes_per_node
                    j.ReqMem_bytes          = ReqMem_bytes_per_node
                    j.ReqMem_bytes_per_core = None
                    j.ReqMem_MB_total       = int(ReqMem[:-2])
                elif ReqMem.endswith('Mc'):
                    ReqMem_bytes_per_core = int(ReqMem[:-2])*1024**2
                    j.ReqMem_bytes_per_node = None
                    j.ReqMem_bytes_per_core = ReqMem_bytes_per_core
                    j.ReqMem_bytes          = ReqMem_bytes_per_core
                    j.ReqMem_MB_total       = int(ReqMem[:-2]) * int(NCPUS)
                elif ReqMem.endswith('Gn'):
                    ReqMem_bytes_per_node = int(round(float(ReqMem[:-2])*1024**3))
                    j.ReqMem_bytes_per_node = ReqMem_bytes_per_node
                    j.ReqMem_bytes_per_core = None
                    j.ReqMem_bytes          = ReqMem_bytes_per_node
                    j.ReqMem_MB_total       = int(round(float(ReqMem[:-2]) * int(NCPUS)))
                elif ReqMem.endswith('Gc'):
                    ReqMem_bytes_per_core = int(round(float(ReqMem[:-2])*1024**3))
                    j.ReqMem_bytes_per_node = None
                    j.ReqMem_bytes_per_core = ReqMem_bytes_per_core
                    j.ReqMem_bytes          = ReqMem_bytes_per_core
                    j.ReqMem_MB_total       = int(round(float(ReqMem[:-2]) * int(NCPUS)))
                elif ReqMem.endswith('Tn'):
                    ReqMem_bytes_per_node = int(round(float(ReqMem[:-2])*1024**4))
                    j.ReqMem_bytes_per_node = ReqMem_bytes_per_node
                    j.ReqMem_bytes_per_core = None
                    j.ReqMem_bytes          = ReqMem_bytes_per_node
                    j.ReqMem_MB_total       = int(round(float(ReqMem[:-2]) * int(NCPUS)))
                elif ReqMem.endswith('Tc'):
                    ReqMem_bytes_per_core = int(round(float(ReqMem[:-2])*1024**4))
                    j.ReqMem_bytes_per_node = None
                    j.ReqMem_bytes_per_core = ReqMem_bytes_per_core
                    j.ReqMem_bytes          = ReqMem_bytes_per_core
                    j.ReqMem_MB_total       = int(round(float(ReqMem[:-2]) * int(NCPUS)))
                    
                #MaxRSS
                j.MaxRSS_kB = 0
                j.MaxRSS_MB = 0
                if MaxRSS:
                    j.MaxRSS_kB = Slurm.MaxRSS_to_kB(MaxRSS)
                    j.MaxRSS_MB = j.MaxRSS_kB / 1024

                # MaxVMSize
                j.MaxVMSize_MB = 0
                if MaxVMSize:
                    j.MaxVMSize_MB = Slurm.MaxRSS_to_kB(MaxVMSize) / 1024
                    
                # AveVMSize
                j.AveVMSize_MB = 0
                if AveVMSize:
                    j.AveVMSize_MB = Slurm.MaxRSS_to_kB(AveVMSize) / 1024
                
                jobsteps.append(j)
                    

        # Send off the final JobReport
        yield JobReport(jobsteps)    
