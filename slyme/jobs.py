'''
Copyright (c) 2014
Harvard FAS Research Computing
All rights reserved.


Created on May 6, 2014

@author: Aaron Kitzmiller
'''

class Job(object):
    """
    A job to be submitted to the JobManager
    """
    
    def __init__(self):
        pass
    
    def addJobParameters(self,parameters):
        """
        Takes a dict of raw job parameters (e.g. {mem : '20G', t : '300'})
        """
        pass
    
    def addCommand(self,cmd):
        """
        Adds a string command line to the job.  Multiple lines can be added.
        Strings with newlines will be multiple commands
        """
        pass
    
    def setName(self,name):
        """
        Sets the job name
        """
        pass
    
    def setMemory(self,memory,percore=False):
        """
        Sets the memory parameter
        """
        pass
    
    def setTime(self,time):
        """
        Sets the time parameter
        """
        pass
    
    def setQueue(self,queue):
        """
        Sets the Slurm partition
        """
        pass
    
    def setNodes(self,nodes):
        """
        Sets the node count for the submission (-N)
        """
        pass
    
    def setTasks(self,tasks):
        """
        Sets the task count for the submission (-n)
        """
        pass
    
    def setStdOut(self,stdout):
        """
        Sets the standard out file name
        """
        pass
    
    def setStdErr(self,stderr):
        """
        Sets the standard err file name
        """
        pass
    
    def setMailType(self,mailtype):
        """
        Sets the mail-type parameter
        """
        pass
    
    def setMailUser(self,mailuser):
        """
        Sets the mail user parameter
        """
        pass
    
    def getStatus(self):
        """
        Returns job status.  Returns NOT SUBMITTED if the job has not yet been
        submitted.
        """
        pass
    
    def isDone(self):
        """
        Returns true if job has been submitted and the status is either 
        COMPLETED, CANCELLED, or FAILED
        """
        pass
    
    def setScriptDir(self,dir):
        """
        Set path to which a job script should be written.  Defaults to "."
        """
        pass
    
    
    
        
    

class SlurmJobManager(object):
    """
    Manages interactions between Job constructs and the Slurm system
    """
    
    def __init__(self):
        pass
    
    def newJob(self):
        """
        Returns a new Job object.  Ensures that the correct Job class is returned
        """
        pass
    
    def getJobStatus(self,job):
        """
        Returns the status text for the specified job.  If the job has not
        yet been submitted, NOT SUBMITTED will be returned
        """
        pass
    
    def submitJob(self,job):
        """
        Uses sbatch to submit the job.  This job manager is assigned to the Job
        indicating that it has been submitted and allowing status checks on the
        Job object itself.
        """
        pass
    
    def runJob(self,job):
        """
        Uses srun to submit the job.  This function doesn't return until the 
        job is completed.
        
        A JobReport is returned?
        """
        pass
    
    def getStatus(self,**kwargs):
        """
        Uses squeue to return status based on the parameters received (e.g.
        partition='general')
        """
        pass
    
    def generateScript(self,job):
        """
        Creates a script from a job
        """
        pass
         