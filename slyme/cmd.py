'''
Created on Jan 24, 2015

@author: akitzmiller
'''
import re, os
import tempfile
import subprocess, socket
import time, datetime
from hex import Command, ShellRunner, DefaultFileLogger, RunLog, RunHandler

SBATCH_NOSUBMIT_OPTIONS =  ['usage','help']

class SbatchCommand(Command):
    """
    Modifications specific to Sbatch, including script generation
    and setting dependencies
    """
    def __init__(self,scriptpath="./"):
        """
        Set a script path, so that *.sbatch scripts can be written.  Default is cwd.
        """
        self.scriptpath = scriptpath
        
    def composeCmdString(self):
        # If options like --help or --usage are set, use parent for command processing
        for option in SBATCH_NOSUBMIT_OPTIONS:

            if option in self.cmdparametervalues and self.cmdparametervalues[option]:
                return super(self.__class__,self).composeCmdString() 


        cmdstring = "#!/bin/bash\n"
        
        # Determines if the argument pattern is an optional one
        optionalargre = re.compile("\?.+?\?")
        
        # Determines if the argument pattern has quoting of the <VALUE>
        quotecheckre = re.compile("(\S)<VALUE>(\S)")                
        
        # Go through the parameter defs in order and 
        # for any parameter with a value, substitute the value into the 
        # "pattern"
        
        # Sort the parameterdef keys based on pdef.order
        sortednames = sorted(self.parameterdefs.iterkeys(),key=lambda name: int(self.parameterdefs[name].order))
        scriptname = None
        commands = []
        for pname in sortednames:
            pdef = self.parameterdefs[pname]
            if pname in self.cmdparametervalues:
                value = self.cmdparametervalues[pname]
                
                if value == False:
                    continue
                
                # Process scriptname
                if pname == "scriptname":
                    scriptname = value
                    continue
                
                # Process command(s)
                if pname == "command":
                    if isinstance(value,basestring):
                        commands.append(value + "\n")
                    else:
                        if not isinstance(value,list):
                            value = [value]
                        for command in value:
                            if isinstance(command,Command):
                                commands.append("%s\n" % command.composeCmdString())
                            elif isinstance(command,basestring):
                                commands.append(command + "\n")
                            else:
                                raise Exception("Why are you using %s as an sbatch command?" % command.__class__.__name__)
                    continue
                
                # If <VALUE> is surrounded by something (e.g. single quotes)
                # then we should make sure that char is escaped in the value
                quotestring = None
                match = quotecheckre.search(pdef.pattern)
                if match is not None:
                    if len(match.groups()) == 2:
                        if match.group(1) == match.group(2):
                            quotestring = match.group(1)
                            
                # Do some courtesy escaping
                if isinstance(value,basestring) and quotestring is not None:
                    # Remove existing escapes
                    value = value.replace("\\" + quotestring,quotestring)
                    # Escape the quote
                    value = value.replace(quotestring,"\\" + quotestring)
                    
                
                # Substitute the value into the pattern
                if optionalargre.search(pdef.pattern) is not None:
                    
                    # This is the case of a switch with an optional argument
                    if value == True:
                        # Adding the switch with no argument
                        cmdstring += "#SBATCH %s\n" % optionalargre.sub("",pdef.pattern)
                    else:
                        # Remove the question marks and substitute the VALUE
                        cmdstring += "#SBATCH %s\n" % pdef.pattern.replace("?","").replace("<VALUE>",value)
                        
                else:
                    if value == True:
                        cmdstring += "#SBATCH %s\n" % pdef.pattern
                    else:
                        cmdstring += "#SBATCH %s\n" % pdef.pattern.replace("<VALUE>",value)
                   
        cmdstring += "\n".join(commands)
        scriptfile = None                         
        if scriptname is None:
            # Generate a tempfile scriptname
            scriptfile = tempfile.NamedTemporaryFile(mode='w',suffix='.sbatch', dir=self.scriptpath,delete=False)
            scriptname = scriptfile.name
        else:
            if scriptname.startswith("/"):
                scriptfile = open(scriptname,'w')
            else:
                scriptname = os.path.join(self.scriptpath,scriptname)
                scriptfile = open(scriptname,'w')
        scriptfile.write(cmdstring)
        scriptfile.close()
               
        newcmdstring = ' '.join([self.bin,scriptname])
        return newcmdstring.encode('ascii','ignore')
    
class SlurmRunner(ShellRunner):
    """
    ShellRunner class that gets job ids instead of pids and uses squeue
    to determine status
    """
    def __init__(self,logpath=None,verbose=0,usevenv=False):
        super(self.__class__,self).__init__(logpath=logpath,verbose=verbose,usevenv=usevenv)

    def getSlurmStatus(self,jobid):
        checkcmd = "squeue -j %s --format=%%T -h" % jobid
        if self.verbose > 1: 
            print "checkcmd %s" % checkcmd
        p = subprocess.Popen(checkcmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        (out,err) = p.communicate()
        out = out.strip()
        err = err.strip()
        if self.verbose > 1:
            print "squeue out %s err %s" % (out,err)
        if out is not None and out != "":
            # It's still running
            return out
        else:
            # Get the result from sacct
            sacctcmd = "sacct -j %s.batch --format=State -n" % jobid
            p = subprocess.Popen(sacctcmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            (out,err) = p.communicate()
            out = out.strip()
            err = err.strip()
            if self.verbose > 1:
                print "sacct out is %s" % out
            return out
        
    def checkStatus(self,runlog=None,proc=None):
        """
        Checks the status of processes using squeue.
        Runlog must have a job id in it 
        """
        if runlog is None:
            raise Exception("Cannot checkStatus without runlog")
        
        # If it's a "help" or "usage" run, just use the parent checkStatus
        for option in SBATCH_NOSUBMIT_OPTIONS:
            if "--%s" % option in runlog["cmdstring"]:
                return super(self.__class__,self).checkStatus(runlog,proc)
       
        result = self.getSlurmStatus(runlog["jobid"]) 
        if result in ["CANCELLED","COMPLETED","FAILED","TIMEOUT","NODE_FAIL","SPECIAL_EXIT"]:
            return result
        else:
            return None
                 
    def getCmdString(self,cmd):
        """
        If the command parameter of the sbatch command is a Command object,
        it is converted into a string here.
        
        If it is an array, the commands are joined by newline into a string
        """
        if hasattr(cmd,"command") and isinstance(cmd.command, Command):
            cmd.command = cmd.command.composeCmdString()
            return super(self.__class__,self).getCmdString(cmd)
        elif isinstance(cmd,list):
            cmdarr = []
            for c in cmd:
                if hasattr(c,"command") and isinstance(c.command, Command):
                    c.command = c.command.composeCmdString()
                    cmdarr.append(c.command.composeCmdString())
                cmdarr.append(super(self.__class__,self).getCmdString(cmd))
            return "\n".join(cmdarr)
        else:
            return super(self.__class__,self).getCmdString(cmd)
                
            
            
        
    def run(self,cmds,runhandler=None,runsetname=None,stdoutfile=None,stderrfile=None,logger=None):
        """
        Runs a Command and returns a RunHandler.
        Mostly calls parent run 
        """
        if logger is None:
            logger = self.logger
        if runsetname is None:
            runsetname = logger.getRunsetName()
        if runhandler is None:
            runhandler = RunHandler(logger,runsetname)
            
            
        if not isinstance(cmds,list):
            cmds = [cmds]
            
                    
        hostname = socket.gethostname().split('.',1)[0]
        
        pid = os.fork()
        if pid == 0:
            for cmd in cmds:
                
                # For options like "help" and "usage", the parent method should be called if the value is True
                for option in SBATCH_NOSUBMIT_OPTIONS:
                    if cmd.getArgValue(option):
                        super(self.__class__,self).run(cmd,runhandler,runsetname,stdoutfile=stdoutfile,stderrfile=stderrfile,logger=logger)
                        os._exit(0)
                
                if isinstance(cmd,SbatchCommand):
                    if cmd.output:
                        stdoutfile = cmd.output
                    else:
                        stdoutfile = logger.getStdOutFileName()
                        cmd.output = stdoutfile
                    if cmd.error:
                        stderrfile = cmd.error
                    else:
                        stderrfile = logger.getStdErrFileName()
                        cmd.error = stderrfile
                        
                cmdstring = self.getCmdString(cmd)                                      
                        
                # Since stdout and stderr are taken care of by the sbatch script,
                # we use subprocess.PIPE here                    
                proc = subprocess.Popen(cmdstring,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                (out,err) = proc.communicate()
                if err:
                    raise Exception("sbatch submission failed %s" % err)
                
                jobid = out.split()[-1]
                
                starttime = datetime.datetime.now()
                runset = []
                runlog = RunLog( jobid=jobid,
                                 cmdstring=cmdstring,
                                 starttime=starttime,
                                 hostname=hostname,
                                 stdoutfile=stdoutfile,
                                 stderrfile=stderrfile,
                                 runner="%s.%s" % (self.__module__, self.__class__.__name__)
                )
                runset.append(runlog)
                if self.verbose > 0:
                    print runlog
            logger.saveRunSet(runset, runsetname)
            os._exit(0)
        else:
            # Wait until the runset file has been written
            ready = False
            while not ready:
                time.sleep(2)
                try:
                    logger.getRunSet(runsetname)
                    ready = True
                except Exception:
                    pass
        return runhandler    

