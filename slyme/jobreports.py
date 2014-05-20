'''
Copyright (c) 2014
Harvard FAS Research Computing
All rights reserved.


Created on May 6, 2014

@author: John Brunelle
@author: Aaron Kitzmiller
'''

# from util import runsh_i
from importlib import import_module # Used to import the command executor
import logging
import re
from datetime import datetime
from slyme.util import slurmtime_to_seconds,MaxRSS_to_kB,runsh_i


logger = logging.getLogger('slyme')


class JobStep(object):
    '''
    Individual job step row from sacct output
    '''


    def __init__(self):
        '''
        Constructor
        '''
                
    def __getitem__(self, index):
        logger.debug("Looking for %s in JobStep" % index)
        if index in self.__dict__:
            return self.__dict__[index]
        else:
            return None



class JobReport(object):
    '''
    Object that represents sacct output for a given jobid. Information is 
    stored as one or more JobSteps.  Attribute accessors retrieve the overall
    information for the JobSteps
    
    The fetch() class method retrieves JobReport objects using a call to sacct
    
    The following field transformations are done to the sacct output:
    
    JobID
      JobIDs that contain an additional job step qualifier are split into the 
      JobID number and the JobStepName.  As a result JobID always returns the
      numerical value
      
    ReqMem
      The ReqMem field is converted to 3 separate fields:
         ReqMem_bytes is the number of bytes requested
         ReqMem_bytes_per_node is populated with ReqMem_bytes if the ReqMem output ended with 'Mn'
         ReqMem_bytes_per_core is populated with ReqMem_bytes if the ReqMem output ended with 'Mc'
         
    Start
      The Start is converted to a python datetime
      
    End
      The End is converted to a python datetime
      
    State
      Mostly this is left as is with the exception of "CANCELLED by <uid>" entries
      The uid is parsed out and moved to the CancelledBy field
      
    MaxRSS
      This is converted to a kilobyte value and stored in MaxRSS_kB.  The JobReport
      iterates through the JobSteps and returns the largest value.
      
    CPUTime,UserCPU,SystemCPU,TotalCPU
      These values are converted to seconds from the text representation.  Values
      may include decimals
      
    '''
    
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

        'ReqMem_bytes',
        #bytes, int, or None if not used
        
        'Start',
        #Start time 
        
        'End',
        #End time
        
        'NodeList',
        #List of nodes used
        
        'Elapsed',
        #Time of the job

        #=== derived data

        'ReqMem_bytes_total',
        #bytes, int, or None if not used
        #a computation combining the appropriate request per resource and number of resources

        'CPU_Efficiency',
        #float, should be in the range [0.0,1.0), but nothing guarantees that
        
        'CPU_Wasted',
        #seconds, float
        
        'CancelledBy',
        #If State is CANCELLED by (uid), this is the uid

    ]
    
    @classmethod
    def fetch(cls,**kwargs):
        factory = SacctFactory()
        jobreports = factory.fetch(**kwargs)
        return jobreports
                    

    def __init__(self,jobsteps=[]):
        '''
        Constructor.  Takes an array of job steps
        '''
        self.jobsteps = jobsteps
        
        
    def __getattr__(self, name):
        """
        __getattr__ just calls __getitem__ 
        """
        if name in JobReport.keys:            
            return self.get_value_for_index(name)
        else:
            # Gotta do this for getattr calls that are looking
            # for methods, etc.
            return super(JobReport,self).__getattribute__(name)
    
    
    def __getitem__(self, index):
        '''
        Get the value from the correct JobStep
        '''        
        return self.get_value_for_index(index)
        
    
    def get_value_for_index(self,index):
        # If no jobsteps return None
        if self.jobsteps is None or len(self.jobsteps) == 0:
            logger.debug("No job steps")
            return None
        
        # We can cache values for large JobStep arrays
        if index in self.__dict__:
            return __dict__[index]
        
        # If there is a getter function, use it
        funcname = "get_%s" % index
        try:            
            f =  getattr(self,funcname)            
            if callable(f):
                return f()
        except AttributeError:
            pass
        
        # Return the first non-null thing you find
        for js in self.jobsteps:
            logger.debug("Checking jobstep against index %s" % index)
            if js[index] is not None and js[index] != '':
                logger.debug("Got %s" % index)
                return js[index]
                
                
    def get_JobName(self):
        for js in self.jobsteps:
            if js.JobName and js.JobName != 'batch':
                return js.JobName
            
    def get_MaxRSS_kB(self):
        """
        Gets the max value from the jobsteps
        """
        max = -1
        for js in self.jobsteps:
            if js.MaxRSS_kB > max:
                max = js.MaxRSS_kB
        return max
    
    def get_NCPUS(self):
        """
        Gets the max value from the jobsteps
        """
        max = 0
        for js in self.jobsteps:
            if js.NCPUS > max:
                max = js.NCPUS
        return max
    
    def get_CPUTime(self):
        """
        Sums the CPUTime of the individual job steps
        """
        cputime = 0
        for js in self.jobsteps:
            cputime += js.CPUTime
        return cputime
        

class SacctFactory(object):
    '''
    Generates the JobSteps from sacct output
    '''
    
    _sacct_format_parsable = 'JobID    ,User    ,JobName   ,State,Partition   ,NCPUS,NNodes,CPUTime   ,TotalCPU   ,UserCPU   ,SystemCPU   ,ReqMem,MaxRSS,Start,End,NodeList,Elapsed'.replace(' ','')
    
    def _yield_raw_sacct_job_text_blocks(self,**kwargs):
        """
        Yields multi-line strings of sacct text for each job.
        """
        logger.debug("yielding sacct text with args %s" % kwargs)
        
        # If an command line executor is defined in the arguments, use that
        # otherwise, use runsh_i
        executor = runsh_i
        if 'execfunc' in kwargs:
            executor = kwargs['execfunc']
                        
        
        shv = ['sacct', '--noheader', '--parsable2', '--format', self._sacct_format_parsable]            
        
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
                    shv.extend('--%s' % key)
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
            

    def fetch(self,**kwargs):
        """
        Yield Job objects that match the given parameters.  
        
        Each row in the output is used to create a JobStep.  Once the job steps
        are collected, a JobReport is created and yielded.  Assumes that 
        jobsteps come out in sequence (though it doesn't matter which one is
        first.
        """
        
        # Regular expression for testing for state "CANCELLED by <uid>"
        cancelledbyre = re.compile(r'CANCELLED by (\d+)')
        
        jobsteps = []
        currentjobid = None
        for saccttext in self._yield_raw_sacct_job_text_blocks(**kwargs):
            try:
                for line in saccttext.split('\n'):
                    line = line.strip()
                    if line=='':
                        continue
    
                    JobID,User,JobName,State,Partition,NCPUS,NNodes,CPUTime,\
                        TotalCPU,UserCPU,SystemCPU,ReqMem,MaxRSS,Start,End,NodeList = line.split('|')
                    logger.debug("User %s, JobID %s" % (User,JobID))
                    
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
                    j.CPUTime       = slurmtime_to_seconds(CPUTime)
                    j.TotalCPU      = slurmtime_to_seconds(TotalCPU)
                    j.UserCPU       = slurmtime_to_seconds(UserCPU)
                    j.SystemCPU     = slurmtime_to_seconds(SystemCPU)
                    
                    starttime = None
                    if Start:
                        starttime = datetime.strptime(Start,"%Y-%m-%dT%H:%M:%S")
                    j.Start         = starttime
                    
                    endtime = None
                    if End and End != 'Unknown':
                        endtime = datetime.strptime(End,"%Y-%m-%dT%H:%M:%S")
                    j.End           = endtime
                    
                    j.NodeList      = NodeList

                    #these are the job steps after the main entry

                    #ReqMem
                    if ReqMem.endswith('Mn'):
                        ReqMem_bytes_per_node = int(ReqMem[:-2])*1024**2
                        j.ReqMem_bytes_per_node = ReqMem_bytes_per_node
                        j.ReqMem_bytes          = ReqMem_bytes_per_node
                        j.ReqMem_bytes_per_core = None
                    elif ReqMem.endswith('Mc'):
                        ReqMem_bytes_per_core = int(ReqMem[:-2])*1024**2
                        j.ReqMem_bytes_per_node = None
                        j.ReqMem_bytes_per_core = ReqMem_bytes_per_core
                        j.ReqMem_bytes          = ReqMem_bytes_per_core
                        
                    #MaxRSS
                    j.MaxRSS_kB = 0
                    if MaxRSS:
                        j.MaxRSS_kB = MaxRSS_to_kB(MaxRSS)
    
                    jobsteps.append(j)
                    
            except Exception, e:
                raise Exception("unable to parse sacct job text [%r]: %r\n" % (saccttext, e))

        # Send off the final JobReport
        yield JobReport(jobsteps)



