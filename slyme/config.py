'''
Copyright (c) 2014
Harvard FAS Research Computing
All rights reserved.

Created on May 6, 2014

@author: aaronkitzmiller

Parses the Slurm config file to get information about the cluster.
Also sets up the package logger.
'''

import re
import logging.config
import os
import sys

# If logging setup is in the environment, use it.  Otherwise, default to 
# console stderr at ERROR level
LOG_LEVEL       = os.environ.get('SLYME_LOG_LEVEL')
if LOG_LEVEL is None:
    LOG_LEVEL = 'ERROR'
LOG_HANDLER      = os.environ.get('SLYME_LOG_HANDLER')
if LOG_HANDLER is None:
    LOG_HANDLER = 'console'

# Logging configuration
LOGGING = {
    'version' : 1,
    'disable_existing_loggers' : False,
    'formatters' : {
        'default' : {
            'format' : "%(asctime)s %(levelname)s %(name)s %(message)s"
        },
        'brief' : {
            'format' : "%(message)s"
        }
    },
    'handlers' : {
        'console' : {
            'class' : 'logging.StreamHandler',
            'level' : LOG_LEVEL,
            'stream': 'ext://sys.stdout',
            'formatter' : 'brief'
        }
    },
    'loggers' : {
        'slyme' : {
            'level' : LOG_LEVEL,
            'handlers' : [LOG_HANDLER],
            'propagate' : True
        }
    }
}


logging.config.dictConfig(LOGGING)
logger = logging.getLogger('slyme')


class SlurmConfig(dict):
    '''
    Object that maintains the data from the slurm.conf file.  
    '''


    def __init__(self, fname="/etc/slurm/slurm.conf"):
        '''
        Constructs the object using the given slurm.conf file name
        
        If there are backslashes at the end of the line it's concatenated
        to the next one.
        
        NodeName lines are not saved because of the stupid DEFAULT stuff.  
        Maybe someday.
        '''
        logger.debug("Initializing SlurmConfig using %s" % fname)
        currline = ''
        m = re.compile(r'([^=]+)\s*=\s*(.*)') #Used to extract name=value 
        n = re.compile(r'(\S+)\s+(.*)')       #Parse values on PartitionName
        with open(fname,'rt') as f:
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
                        if 'Partitions' not in self:
                            self['Partitions'] = {}
                        self['Partitions'][pname] = pvalue
                    else:                            
                        self[name] = value
                else:
                    logger.error("Slurm config file %s has strange line '%s'" % (fname,currline))
                
                currline = ''
                

# configFile = os.environ.get('SLURM_CONF')
# if configFile is None:
#     configFile = "/etc/slurm/slurm.conf"
#      
# SLURMCONFIG = SlurmConfig(configFile)

                
                
                
                
                
                    
            
            
            
        
        
        