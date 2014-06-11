"""
Copyright (c) 2014
Harvard FAS Research Computing
All rights reserved.

Created on May 6, 2014

@author: Aaron Kitzmiller

What I want to be able to do is this:

>>> bowtie = Command.fetch('http://www.www.com/bowtie/2.3.1/cmd.json')
>>> result = BashRunner.run(bowtie,"--arg1"="yes",--arg2="2", inputfile="myinputfile.fasta", outputfile="myoutput.fasta")
>>> print result.stdout
>>> print result.stderr
>>> Outputfile should be a stream that you can read from while it's running
>>>
>>> srun = Command.fetch('/n/sw/cmddefs/srun/cmd.json')
>>> srun.args = {mem=2000,t=1000,partition="serial_requeue"}
>>> result = BashRunner.run(srun,cmd=bowtie)

>>> 
>>> sbatch = Command.fetch('/n/sw/cmddefs/sbatch/cmd/json')
>>> result = SlurmRunner.run(sbatch,cmd=bowtie,mem=20000,t=10000,n=4)
>>> 
>>> 


"""

class ParameterDef(object):
    """
    An object used to supply parameter definitions to Commands.  These can be 
    used to validate command parameters, generate help text and drive form
    elements.  Commands don't have to have these.
    """
    
    def __init__(self,
                 name,
                 switches,
                 type='string',
                 required=False,
                 help="",
                 default=None,
                 choices=None):
        pass
    
    
class Command(object):
    
    def __init__(self,rawcmdstring="",
                 parameterdefs=None,
                 binary="",
                 args=[],
                 config="",
                 helpswitch=""):
        """
        Create a Command object.
        
        Commands can be created in 3 modes.
        
        Command String Mode initiates a Command using a command line string.
        In this situation, the command is passed as a string and run as is via 
        the shell.  No validation is used.
        
        Config Mode initializes a Command using a command configuration file.
        When in Config Mode, parameterdefs and rawcmdstring cannot be passed to
        the constructor; parameterdefs are obtained from the config.  Arguments 
        are defined by the args array.  A specific binary can be passed in, but 
        generally, the unadorned binary from the config is used.  Details of the
        configuration file structure and parsing can be found in the CommandConfig
        class notes.
        
        Manual mode initializes a Command using ParameterDef objects and a 
        string representing the binary.
        
        Note that arguments for the Command can be set later, at run time.
        
        
        
        ParameterDefs are optional, but if included, will be used to validate the 
        command.
        """
        pass
    
    def getCmdString(self,**kwargs):
        """
        Returns a suitable command string based on the supplied arguments.
        
        If args is used, it should be a dictionary of arguments keyed by argument
        name or switch.
        
        If the rawcmdstring is set and no args are supplied, it uses that.
        If the rawcmdstring is set and args are supplied, they are concatenated
        to the string and returned.
        If the rawcmdstring is not set, the binary and parameterdefs are used
        to construct the string.  ParameterDefs are used in order to construct
        the command string.
        """
        pass
    
    def getHelp(self):
        """
        Returns the command help string using a combination of the binary and 
        the help switch or the parameter called 'help'.
        """
        pass
    
    

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
         