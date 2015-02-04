'''
Copyright (c) 2014
Harvard FAS Research Computing
All rights reserved.
Created on May 6, 2014
@author: John Brunelle
@author: Aaron Kitzmiller
'''

# from util import runsh_i
import logging
import re
from datetime import datetime
from slyme.util import runsh_i


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
        

    
