'''
Created on May 7, 2014

@author: aaronkitzmiller
'''
from __future__ import print_function
import unittest
import os
import sys

SLURM_CONF_FILENAME = "slurm.conf"


class Test(unittest.TestCase):
        
    def setUp(self):
        # Write defined config file.  Currently using our conf
        conf = """ControlMachine=holy-slurm01
ControlAddr=10.31.20.139
#BackupController=sum1-slurm01
#BackupAddr=10.242.106.135

AuthType=auth/munge
CacheGroups=0
#CheckpointType=checkpoint/none
CryptoType=crypto/munge
#DisableRootJobs=NO
EnforcePartLimits=YES
Epilog=/usr/local/bin/slurm_epilog
#EpilogSlurmctld=
#FirstJobId=1
#MaxJobId=999999
#GresTypes=
#GroupUpdateForce=1
#GroupUpdateTime=600
#JobCheckpointDir=/var/slurmd/checkpoint
#JobCredentialPrivateKey=
#JobCredentialPublicCertificate=
#JobFileAppend=0
#JobRequeue=1
JobSubmitPlugins=lua
#KillOnBadExit=0
Licenses=bicepfs1:100,kovac_holyscratch:500,huttenhower:20,lumerical:10,blackhole:32,panlfs_coati_100:100,panlfs_coati_200:200,cep_100:100
#MailProg=/bin/mail
MaxJobCount=150000
MaxArraySize=10000
#MaxStepCount=40000
#MaxTasksPerNode=128
MpiDefault=none
#MpiParams=ports=#-#
#PluginDir=
#PlugStackConfig=
#PrivateData=jobs
ProctrackType=proctrack/cgroup
#Prolog=/usr/local/bin/slurm_prolog
PrologSlurmctld=/usr/local/sbin/slurmctld_prolog
#PropagatePrioProcess=0
#PropagateResourceLimits=
#PropagateResourceLimitsExcept=
RebootProgram=/usr/local/sbin/slurm_reboot
ReturnToService=1
#SallocDefaultCommand=
SlurmctldPidFile=/var/slurmd/run/slurmctld.pid
SlurmctldPort=6820-6852 #6817
SlurmdPidFile=/var/slurmd/run/slurmd.pid
SlurmdPort=6818
SlurmdSpoolDir=/var/slurmd/spool/slurmd
SlurmUser=slurm
#SlurmdUser=root
#SrunEpilog=
#SrunProlog=
StateSaveLocation=/slurm/spool
SwitchType=switch/none
#TaskEpilog=
TaskPlugin=task/none
#TaskPluginParam=
#TaskProlog=
#TopologyPlugin=topology/tree
TmpFs=/scratch
#TrackWCKey=no
#TreeWidth=
#UnkillableStepProgram=
UsePAM=1

# TIMERS
#BatchStartTimeout=10
#CompleteWait=0
EpilogMsgTime=10000
#GetEnvTimeout=2
HealthCheckInterval=500
HealthCheckProgram=/usr/local/bin/node_monitor
InactiveLimit=0
KillWait=30
MessageTimeout=100
#ResvOverRun=0
MinJobAge=300
#OverTimeLimit=0
SlurmctldTimeout=120
SlurmdTimeout=300
#UnkillableStepTimeout=60
#VSizeFactor=0
Waittime=0

# SCHEDULING
DefMemPerCPU=100
FastSchedule=2
#MaxMemPerCPU=0
#SchedulerRootFilter=1
#SchedulerTimeSlice=30
SchedulerType=sched/backfill
# default_queue_depth should be some multiple of the partition_job_depth,
# ideally number_of_partitions * partition_job_depth, but typically the main
# loop exits prematurely if you go over about 400. A partition_job_depth of
# 10 seems to work well.
SchedulerParameters=default_queue_depth=50,partition_job_depth=1,bf_interval=60,bf_continue,bf_window=2880,bf_resolution=3600,max_job_bf=50000,bf_max_job_part=50000,bf_max_job_user=10,bf_max_job_start=100,max_rpc_cnt=8#defer
SchedulerPort=7321
SelectType=select/cons_res
SelectTypeParameters=CR_Core_Memory

# JOB PRIORITY
PriorityType=priority/multifactor
PriorityDecayHalfLife=2-0
##PriorityCalcPeriod=
##PriorityFavorSmall=
PriorityMaxAge=7-0
##PriorityUsageResetPeriod=
PriorityWeightAge=1000
PriorityWeightFairshare=20000000 
PriorityWeightJobSize=0
PriorityWeightPartition=100000000 
PriorityWeightQOS=1000000000 

# JOB PREEMPTION
PreemptType=preempt/partition_prio
PreemptMode=REQUEUE

# LOGGING AND ACCOUNTING
AccountingStorageEnforce=safe
AccountingStorageHost=holy-slurm01
AccountingStorageLoc=slurm
#AccountingStoragePass=
AccountingStoragePort=6819
AccountingStorageType=accounting_storage/slurmdbd
AccountingStorageUser=slurm
AccountingStoreJobComment=YES
ClusterName=odyssey
#DebugFlags=Backfill
JobCompHost=holy-slurm01
JobCompLoc=/usr/local/sbin/slurmctld_jobcomp
#JobCompPass=password
#JobCompPort=
JobCompType=jobcomp/script
#JobCompUser=slurm
JobAcctGatherFrequency=30
JobAcctGatherType=jobacct_gather/linux
SlurmctldDebug=verbose
SlurmdDebug=verbose
SlurmctldLogFile=/var/slurmd/log/slurmctld.log
#SlurmdLogFile=
#SlurmSchedLogFile=
#SlurmSchedLogLevel=

# POWER SAVE SUPPORT FOR IDLE NODES (optional)
#SuspendProgram=
#ResumeProgram=
#SuspendTimeout=
#ResumeTimeout=
#ResumeRate=
#SuspendExcNodes=
#SuspendExcParts=
#SuspendRate=
#SuspendTime=


# -------------
# COMPUTE NODES
# -------------

NodeName=DEFAULT CPUs=64 RealMemory=516842 Sockets=4 CoresPerSocket=16 \
    ThreadsPerCore=1
# PMAGE (Program in Genetic Epidemiology and Statistical Genetics)
NodeName=pmage1
# Publicly available high memory nodes owned by Harvard RC.
NodeName=holybigmem0[1-8]

# This does not match the actual hardware specs but should get us more job slots.
NodeName=DEFAULT CPUs=64 RealMemory=264499 Sockets=4 CoresPerSocket=16 \
    ThreadsPerCore=1
# Kuang
NodeName=holy2b0510[1-8],holy2b0520[1-8],holy2b0530[1-8],holy2b0710[1-8]
# ITC
NodeName=itc01[1-2],itc02[1-2],itc03[1-2],itc04[1-2],itc05[1-2],itc06[1-2]
NodeName=itc07[1-2],itc08[1-2],itc09[1-2],itc10[1-2],itc11[1-2]
# Nelson
NodeName=nelson0[1-2]
# NNIN
NodeName=holy2b0920[1-8],holy2b0930[1-2]
# Odyssey 2
NodeName=holy2a0110[1-8],holy2a0120[1-8]
NodeName=holy2a0210[1-8],holy2a0220[1-8]
NodeName=holy2a0310[1-8],holy2a0320[1-8],holy2a0330[1-8]
NodeName=holy2a0410[1-8],holy2a0420[1-8],holy2a0430[1-8]
NodeName=holy2a0510[1-8],holy2a0520[1-8]
NodeName=holy2a0610[1-8],holy2a0620[1-8]
NodeName=holy2a0710[1-8],holy2a0720[1-8],holy2a0730[1-8]
NodeName=holy2a0810[1-8],holy2a0820[1-8],holy2a0830[1-8]
NodeName=holy2a0910[1-8],holy2a0920[1-8],holy2a0930[1-8]
NodeName=holy2a1110[1-8],holy2a1120[1-8]
NodeName=holy2a1310[1-8],holy2a1320[1-8],holy2a1330[1-8]
NodeName=holy2a1410[1-8],holy2a1420[1-8],holy2a1430[1-8]
NodeName=holy2a1510[1-8],holy2a1520[1-8]
NodeName=holy2a1610[1-8],holy2a1620[1-8]
NodeName=holy2a1710[1-8],holy2a1720[1-8],holy2a1730[1-8]
NodeName=holy2a1810[1-8],holy2a1820[1-8],holy2a1830[1-8]
NodeName=holy2a1910[1-8],holy2a1920[1-8]
NodeName=holy2a2010[1-8],holy2a2020[1-8]
NodeName=holy2a2110[1-8],holy2a2120[1-8],holy2a2130[1-8]
NodeName=holy2a2210[1-8],holy2a2220[1-8],holy2a2230[1-8]
NodeName=holy2a2310[1-8],holy2a2320[1-8]
NodeName=holy2a2410[1-8],holy2a2420[1-8]

NodeName=DEFAULT CPUs=64 RealMemory=264499 Sockets=4 CoresPerSocket=16 \
    ThreadsPerCore=1
# Zorana
NodeName=zorana0[1-2]
# NCF
NodeName=ncf270[1-8]

NodeName=DEFAULT CPUs=64 RealMemory=529247 Sockets=4 CoresPerSocket=16 \
    ThreadsPerCore=1
# Stewart
NodeName=holy2b0720[1-8],holy2b0910[1-8]

# Xie
NodeName=xie01

NodeName=DEFAULT CPUs=16 RealMemory=32768 Sockets=2 CoresPerSocket=8 \
    ThreadsPerCore=1
# sandy-rc
NodeName=sandy-rc0[1-4]

NodeName=DEFAULT CPUs=12 RealMemory=48161 Sockets=2 CoresPerSocket=6 \
    ThreadsPerCore=1
# davis
NodeName=davis0[1-4]
# leroy
NodeName=leroy0[1-4]

# kou
NodeName=kou1[1-4],kou2[1-4],kou3[1-4],kou4[1-4],kou5[1-4]

NodeName=DEFAULT CPUs=24 RealMemory=24020 Sockets=2 CoresPerSocket=6 \
    ThreadsPerCore=2
# enj
NodeName=enj[01-12]

NodeName=DEFAULT CPUS=8 RealMemory=36140 Sockets=2 CoresPerSocket=4 \
    ThreadsPerCore=1
# dae
NodeName=dae1[1-4],dae2[1-4]

NodeName=DEFAULT CPUS=12 RealMemory=96735 Sockets=2 CoresPerSocket=6 \
    ThreadsPerCore=1
# airoldi
NodeName=airoldi[02-12]

NodeName=DEFAULT CPUS=32 RealMemory=32961 Sockets=2 CoresPerSocket=8 \
    ThreadsPerCore=2 Feature=gpu
# holygpu
NodeName=holygpu[01-16]

NodeName=DEFAULT CPUS=12 RealMemory=24150 Sockets=2 CoresPerSocket=6 \
    ThreadsPerCore=1
# hp
NodeName=hp010[1-4],hp020[1-4],hp030[1-4],hp040[1-4],hp050[1-4],hp060[1-4]
NodeName=hp070[1-4],hp080[1-4],hp090[1-4],hp100[1-4],hp110[1-4],hp120[1-4]
NodeName=hp130[1-4],hp140[1-4],hp150[1-4],hp160[1-4],hp170[1-4],hp180[1-4]
NodeName=hp190[1-4],hp200[1-4],hp210[1-4],hp220[1-4],hp230[1-4],hp240[1-4]
NodeName=hp250[1-4],hp260[1-4],hp270[1-4]

# moorcroft
NodeName=moorcroft[02-04]

NodeName=DEFAULT CPUS=32 RealMemory=129015 Sockets=2 CoresPerSocket=16 \
    ThreadsPerCore=1
# regal
NodeName=regal[01-20]

NodeName=DEFAULT CPUs=8 RealMemory=32108 Sockets=2 CoresPerSocket=4 \
    ThreadsPerCore=1
# moorcroft
NodeName=hero40[01-11]
# nocera
NodeName=hero46[01-16],hero47[01-16]

# holystat nodes, all but 2 have 16 cores, holystat11 and 17 have only 8 cores
NodeName=DEFAULT CPUs=16 RealMemory=64345 Sockets=2 CoresPerSocket=8 \
    ThreadsPerCore=1
NodeName=holystat0[1-9],holystat10,holystat1[2-6],holystat1[8-9],holystat2[0-2]

NodeName=DEFAULT CPUs=8 RealMemory=64345 Sockets=2 CoresPerSocket=4 \
    ThreadsPerCore=1
NodeName=holystat11,holystat17

# seasgpu
NodeName=DEFAULT CPUs=6 RealMemory=48261 Sockets=1 CoresPerSocket=6 \
    ThreadsPerCore=1
NodeName=seasgpu0[1-9],seasgpu1[0-6]

# jenny,holymoorcroft and aag nodes
NodeName=DEFAULT CPUs=64 RealMemory=258302 Sockets=4 CoresPerSocket=16 \
    ThreadsPerCore=1
NodeName=jenny0[1-4],holymoorcroft0[1-8],aag0[1-9],aag1[0-6]

# karplus
NodeName=DEFAULT CPUs=8 RealMemory=11901 Sockets=2 CoresPerSocket=4 \
    ThreadsPerCore=1
NodeName=karplus0[1-4]

# pierce node
NodeName=DEFAULT CPUs=64 RealMemory=516842 Sockets=4 CoresPerSocket=16 \
    ThreadsPerCore=1
NodeName=holy2b09303

# wofsy
NodeName=DEFAULT CPUs=12 RealMemory=48258 Sockets=2 CoresPerSocket=6 \
    ThreadsPerCore=1
NodeName=wofsy01[1-4],wofsy02[1-4],iliad20[1-9],iliad21[0-2]

# shock
NodeName=DEFAULT CPUs=8 RealMemory=48258 Sockets=2 CoresPerSocket=4 \
    ThreadsPerCore=1
NodeName=shock0[1-9],shock10,shock11

# One shock node is not like the others.
NodeName=DEFAULT CPUs=12 RealMemory=48258 Sockets=2 CoresPerSocket=6 \
    ThreadsPerCore=1
NodeName=shock12

# hips - SEAS
NodeName=DEFAULT CPUs=32 RealMemory=129041 Sockets=4 CoresPerSocket=8 \
    ThreadsPerCore=1
NodeName=adams01

# giribet
NodeName=DEFAULT CPUs=12 RealMemory=48258 Sockets=2 CoresPerSocket=6 \
    ThreadsPerCore=1
NodeName=giribet0[1-4]

NodeName=DEFAULT CPUs=64 RealMemory=516857 Sockets=4 CoresPerSocket=8 \
    ThreadsPerCore=2
# HSPH
NodeName=hsph0[5-6]

# eldorado03-40
NodeName=DEFAULT CPUs=24 RealMemory=24020 Sockets=2 CoresPerSocket=6 \
        ThreadsPerCore=2
NodeName=eldorado0[3-9],eldorado1[0-9],eldorado2[0-9],eldorado3[0-9],eldorado40

# eldorado41-46,48,49,51,52
NodeName=DEFAULT CPUs=12 RealMemory=48258 Sockets=2 CoresPerSocket=6 \
        ThreadsPerCore=1
NodeName=eldorado4[1-6],eldorado4[8-9],eldorado5[1-2]

# eldorado47 and 50
NodeName=DEFAULT CPUs=12 RealMemory=40179 Sockets=2 CoresPerSocket=6 \
        ThreadsPerCore=1
NodeName=eldorado47,eldorado50

# ----------
# PARTITIONS
# ----------

# Airoldi
PartitionName=airoldi Priority=10 \
    AllowGroups=airoldi_lab,rc_admin \
    Nodes=airoldi[02-12]

# Aspuru-Guzik
PartitionName=aspuru-guzik Priority=10 \
    AllowGroups=aspuru-guzik_lab,rc_admin \
    Nodes=holy2a1830[1-8],\
holy2a1910[1-8],holy2a1920[1-8],\
holy2a2010[1-8],holy2a2020[1-8],\
holy2a2110[1-8],aag0[1-9],aag1[0-6]

# betley
PartitionName=betley Priority=10 \
    AllowGroups=rc_admin,betley_lab \
    Nodes=holy2a14105

# Bigmem
PartitionName=bigmem Priority=10 \
    AllowGroups=rc_admin,slurm_group_bigmem \
    Nodes=holybigmem0[1-8]

# Conte
PartitionName=conte Priority=10 \
    AllowGroups=rc_admin,zhuang_lab \
    Nodes=holy2a1410[7-8]

# Davis
PartitionName=davis Priority=10 \
    AllowGroups=rc_admin,davis_lab \
    Nodes=davis0[1-4]

# Eldorado
PartitionName=eldorado Priority=10 \
        AllowGroups=rc_admin,aspuru-guzik_lab \
        Nodes=eldorado0[3-9],eldorado1[0-9],eldorado2[0-9],eldorado3[0-9],eldorado4[0-9],eldorado5[0-2]

# Evans
PartitionName=evans Priority=10 \
    AllowGroups=evans_lab,rc_admin \
    Nodes=dae1[1-4],dae2[1-4]

# General
PartitionName=general Priority=2 MaxTime=7-0 \
    AllowGroups=rc_admin,cluster_users \
    Nodes=\
holy2a0110[1-8],holy2a0120[1-8],\
holy2a0210[1-8],holy2a0220[1-8],\
holy2a0310[1-8],holy2a0320[1-8],holy2a0330[1-8],\
holy2a0410[1-8],holy2a0420[1-8],holy2a0430[1-8],\
holy2a0510[1-8],holy2a0520[1-8],\
holy2a0610[1-8],holy2a0620[1-8],\
holy2a0710[1-8],holy2a0720[1-8],holy2a0730[1-8],\
holy2a0810[1-8],holy2a0820[1-8],holy2a0830[1-8],\
holy2a0910[1-8],holy2a0920[1-8],holy2a0930[1-8],\
holy2a1110[1-8],holy2a1120[1-8],\
holy2a1310[1-8],holy2a1320[1-8],holy2a1330[1-8],\
holy2a1410[1-5]

# giribet
PartitionName=giribet Priority=10 \
    AllowGroups=rc_admin,giribet_lab \
    Nodes=giribet0[1-4]

# GPGPU
PartitionName=gpgpu Priority=10 \
    AllowGroups=rc_admin,aspuru-guzik_lab,greenhill_lab,computefestgpu,pfister_lab,slurm_group_gpgpu \
    Nodes=holygpu[01-16]

# Hernquist
PartitionName=hernquist Priority=10 MaxTime=7-0 \
    AllowGroups=rc_admin,hernquist_lab \
    Nodes=\
holy2a2130[1-8],\
holy2a2210[1-8],holy2a2220[1-8],holy2a2230[1-8],\
holy2a2310[1-8],holy2a2320[1-8],\
holy2a2410[1-8],holy2a2420[1-7]

# Hernquist-dev, this node is not in serial_requeue as it is a development node and they will be sshing directly to it.
PartitionName=hernquist-dev Priority=10 MaxTime=7-0 \
    AllowGroups=rc_admin,hernquist_lab \
    Nodes=holy2a24208

# hips - SEAS
PartitionName=hips Priority=10 \
    AllowGroups=rc_admin,adams_lab_seas \
    Nodes=adams01

# HSPH
PartitionName=hsph Priority=10 \
    AllowGroups=rc_admin,hsph_bioinfo,slurm_group_hsph \
    Nodes=hsph0[5-6]

# Informatics-dev
PartitionName=informatics-dev Priority=10 \
    AllowGroups=rc_admin,sequencing \
    Nodes=sandy-rc[01-04]

# Interactive
#
# There are holes in the access nodes' iptables rules as well as network
# ACLs to allow the network connections required for interactive jobs. Both
# the SLURM master and the compute node the job is scheduled on initiate TCP
# connections (sourced from an ephemeral port) back to the submitting host
# (also on an ephemeral port).
#
# The network ACLs allow these connections from the MGHPCC compute nets, but
# if we ever add nodes to this partition outside of those nets, we'll need
# to have the network ACLs opened in the same manner.
PartitionName=interact Priority=10 MaxTime=3-0 \
    AllowGroups=cluster_users,rc_admin \
    Nodes=holy2a1820[5-8]

PartitionName=ishii    Priority=10 \
    AllowGroups=rc_admin,ishii_lab \
    Nodes=holy2a1730[1-8],holy2a1810[1-8]

# ITC
PartitionName=itc_cluster Priority=10 MaxTime=7-0 \
    AllowGroups=rc_admin,itc_lab,slurm_group_itc \
    Nodes=\
itc01[1-2],itc02[1-2],itc03[1-2],itc04[1-2],\
itc05[1-2],itc06[1-2],itc07[1-2],itc08[1-2],\
itc09[1-2],itc10[1-2],itc11[1-2]

# Jacobsen
PartitionName=jacobsen Priority=10 \
    AllowGroups=rc_admin,jacobsen_lab \
    Nodes=enj[01-12]

# Jenny
PartitionName=jenny Priority=10 \
    AllowGroups=rc_admin,rice_lab \
    Nodes=jenny0[1-4]

# Karplus
PartitionName=karplus Priority=10 \
    AllowGroups=rc_admin,karplus_lab \
    Nodes=karplus0[1-4],iliad211,iliad212

# Kou
PartitionName=kou Priority=10 \
    AllowGroups=rc_admin,kou \
    Nodes=kou1[1-4],kou2[1-4],kou3[1-4],kou4[1-4],kou5[1-4]

# Kuang
PartitionName=kuang Priority=20 \
    AllowGroups=rc_admin,kuang_lab,tziperman_lab,slurm_group_kuang \
    Nodes=holy2b0510[1-8],holy2b0520[1-8],holy2b0530[1-8],holy2b0710[1-8],\
holy2a1610[1-8],holy2a1620[1-8],\
holy2a1710[1-8],holy2a1720[1-8]

# Kuang HP
PartitionName=kuang_hp Priority=10 \
    AllowGroups=rc_admin,kuang_lab,tziperman_lab,stewart_lab \
    Nodes=\
hp010[1-4],hp020[1-4],hp030[1-4],hp040[1-4],hp050[1-4],hp060[1-4],\
hp070[1-4],hp080[1-4],hp090[1-4],hp100[1-4],hp110[1-4],hp120[1-4],\
hp130[1-4],hp140[1-4],hp150[1-4],hp160[1-4],hp170[1-4],hp180[1-4],\
hp190[1-4],hp200[1-4],hp210[1-4],hp220[1-4],hp230[1-4],hp240[1-4],\
hp250[1-4],hp260[1-4],hp270[1-4]

# Leroy
PartitionName=leroy Priority=10 \
    AllowGroups=rc_admin,leroy_lab \
    Nodes=leroy0[1-4]

# Meade
PartitionName=meade Priority=10 \
    AllowGroups=rc_admin,meade_lab \
    Nodes=holy2a1520[1-8]

# Mitrovica
PartitionName=mitrovica Priority=10 \
    AllowGroups=rc_admin,mitrovica_lab \
    Nodes=iliad20[1-9],iliad210

# moorcroft_amd
PartitionName=moorcroft_amd Priority=10 \
        AllowGroups=rc_admin,moorcroft_lab \
        Nodes=holymoorcroft0[1-8]

# Moorcroft 6100
PartitionName=moorcroft_6100 Priority=10 \
    AllowGroups=rc_admin,moorcroft_lab \
    Nodes=moorcroft[02-04]

# Moorcroft Hero
PartitionName=moorcroft_hero Priority=10 \
    AllowGroups=rc_admin,moorcroft_lab \
    Nodes=hero40[01-11]

# NCF
PartitionName=ncf Priority=10 \
    AllowGroups=rc_admin,luk_lab,ncfuser,tkadmin,cnl,nrg,anl,mcl,scn,vsl,\
hooley_lab,xnat,snp,sml,cnp,vcn,ncfadmin_group,\
mclaughlin_lab,sheridan_lab,ncf_users,\
pascual-leone,jwb,mrimgmt,holt_lab \
    Nodes=ncf270[1-8]

# Nelson
PartitionName=nelson Priority=10 \
    AllowGroups=rc_admin,nelson_lab \
    Nodes=nelson0[1-2]

# ni_lab -- see RT #53080
PartitionName=ni_lab Priority=10 \
    AllowGroups=rc_admin,ni_lab \
    Nodes=holy2a1820[1-4]

# NNIN
PartitionName=nnin Priority=10 \
    AllowGroups=rc_admin,nnin \
    Nodes=holy2b0920[1-8],holy2b0930[1-2]

# Nocera
PartitionName=nocera Priority=10 \
    AllowGroups=rc_admin,nocera_lab \
    Nodes=hero46[01-16],hero47[01-16]

# Pierce
PartitionName=pierce Priority=10 \
    AllowGroups=rc_admin,pierce_lab,slurm_group_pierce \
    Nodes=holy2b09303

# PMAGE (Program in Genetic Epidemiology and Statistical Genetics)
PartitionName=pmage Priority=10 \
    AllowGroups=rc_admin,kraft_lab,slurm_group_pmage \
    Nodes=pmage1

# Priority
PartitionName=priority Priority=10 \
    AllowGroups=rc_admin \
    Nodes=\
aag0[1-9],aag1[0-6],\
adams01,\
airoldi[02-12],\
dae1[1-4],dae2[1-4],\
davis0[1-4],\
eldorado0[3-9],eldorado1[0-9],eldorado2[0-9],eldorado3[0-9],eldorado4[0-9],eldorado5[0-2],\
enj[01-12],\
giribet0[1-4],\
hero40[01-11],hero46[01-16],hero47[01-16],\
holy2a0110[1-8],holy2a0120[1-8],\
holy2a0210[1-8],holy2a0220[1-8],\
holy2a0310[1-8],holy2a0320[1-8],holy2a0330[1-8],\
holy2a0410[1-8],holy2a0420[1-8],holy2a0430[1-8],\
holy2a0510[1-8],holy2a0520[1-8],\
holy2a0610[1-8],holy2a0620[1-8],\
holy2a0710[1-8],holy2a0720[1-8],holy2a0730[1-8],\
holy2a0810[1-8],holy2a0820[1-8],holy2a0830[1-8],\
holy2a0910[1-8],holy2a0920[1-8],holy2a0930[1-8],\
holy2a1110[1-8],holy2a1120[1-8],\
holy2a1310[1-8],holy2a1320[1-8],holy2a1330[1-8],\
holy2a1410[1-8],holy2a1420[1-8],holy2a1430[1-8],\
holy2a1510[1-8],holy2a1520[1-8],\
holy2a1610[1-8],holy2a1620[1-8],\
holy2a1710[1-8],holy2a1720[1-8],holy2a1730[1-8],\
holy2a1810[1-8],holy2a1820[1-8],holy2a1830[1-8],\
holy2a1910[1-8],holy2a1920[1-8],\
holy2a2010[1-8],holy2a2020[1-8],\
holy2a2110[1-8],holy2a2120[1-8],holy2a2130[1-8],\
holy2a2210[1-8],holy2a2220[1-8],holy2a2230[1-8],\
holy2a2310[1-8],holy2a2320[1-8],\
holy2a2410[1-8],holy2a2420[1-8],\
holy2b0510[1-8],holy2b0520[1-8],holy2b0530[1-8],\
holy2b0710[1-8],holy2b0720[1-8],\
holy2b0910[1-8],holy2b0920[1-8],holy2b0930[1-3],\
holybigmem0[1-8],\
holygpu[01-16],\
holymoorcroft0[1-8],\
holystat0[1-9],holystat1[0-9],holystat2[0-2],\
hp010[1-4],hp020[1-4],hp030[1-4],hp040[1-4],hp050[1-4],hp060[1-4],\
hp070[1-4],hp080[1-4],hp090[1-4],hp100[1-4],hp110[1-4],hp120[1-4],\
hp130[1-4],hp140[1-4],hp150[1-4],hp160[1-4],hp170[1-4],hp180[1-4],\
hp190[1-4],hp200[1-4],hp210[1-4],hp220[1-4],hp230[1-4],hp240[1-4],\
hp250[1-4],hp260[1-4],hp270[1-4],\
hsph0[5-6],\
iliad20[1-9],iliad21[0-2],\
itc01[1-2],itc02[1-2],itc03[1-2],itc04[1-2],\
itc05[1-2],itc06[1-2],itc07[1-2],itc08[1-2],\
itc09[1-2],itc10[1-2],itc11[1-2],\
jenny0[1-4],\
karplus0[1-4],\
kou1[1-4],kou2[1-4],kou3[1-4],kou4[1-4],kou5[1-4],\
leroy0[1-4],\
moorcroft[02-04],\
ncf270[1-8],\
nelson0[1-2],\
pmage1,\
regal[01-20],\
sandy-rc0[1-4],\
seasgpu0[1-9],seasgpu1[0-6],\
shock0[1-9],shock1[0-2],\
wofsy01[1-4],wofsy02[1-4],\
xie01,\
zorana0[1-2]

# Regal
PartitionName=regal Priority=10 \
    AllowGroups=rc_admin,slurm_group_regal \
    Nodes=regal[01-20]

# Seasgpu
PartitionName=resonance Priority=10 \
    AllowGroups=rc_admin,resonance \
    Nodes=seasgpu0[1-9],seasgpu1[0-6]

# Serial Requeue
PartitionName=serial_requeue Priority=1 \
    PreemptMode=REQUEUE MaxTime=1-0 Default=YES MaxNodes=1 \
    AllowGroups=rc_admin,cluster_users \
    Nodes=\
aag0[1-9],aag1[0-6],\
adams01,\
airoldi[02-12],\
dae1[1-4],dae2[1-4],\
davis0[1-4],\
eldorado0[3-9],eldorado1[0-9],eldorado2[0-9],eldorado3[0-9],eldorado4[0-9],eldorado5[0-2],\
enj[01-12],\
giribet0[1-4],\
holy2a0110[1-8],holy2a0120[1-8],\
holy2a0210[1-8],holy2a0220[1-8],\
holy2a0310[1-8],holy2a0320[1-8],holy2a0330[1-8],\
holy2a0410[1-8],holy2a0420[1-8],holy2a0430[1-8],\
holy2a0510[1-8],holy2a0520[1-8],\
holy2a0610[1-8],holy2a0620[1-8],\
holy2a0710[1-8],holy2a0720[1-8],holy2a0730[1-8],\
holy2a0810[1-8],holy2a0820[1-8],holy2a0830[1-8],\
holy2a0910[1-8],holy2a0920[1-8],holy2a0930[1-8],\
holy2a1110[1-8],holy2a1120[1-8],\
holy2a1310[1-8],holy2a1320[1-8],holy2a1330[1-8],\
holy2a1410[1-8],holy2a1420[1-8],holy2a1430[1-8],\
holy2a1510[1-8],holy2a1520[1-8],\
holy2a1610[1-8],holy2a1620[1-8],\
holy2a1710[1-8],\
holy2a1720[1-8],\
holy2a1730[1-8],\
holy2a1810[1-8],\
holy2a1820[1-8],\
holy2a1830[1-8],\
holy2a1910[1-8],holy2a1920[1-8],\
holy2a2010[1-8],holy2a2020[1-8],\
holy2a2110[1-8],\
holy2a2120[1-8],\
holy2a2130[1-8],\
holy2a2210[1-8],holy2a2220[1-8],holy2a2230[1-8],\
holy2a2310[1-8],holy2a2320[1-8],\
holy2a2410[1-8],holy2a2420[1-7],\
holy2b0510[1-8],holy2b0520[1-8],holy2b0530[1-8],\
holy2b0710[1-8],holy2b0720[1-8],\
holy2b0910[1-8],holy2b0920[1-8],holy2b0930[1-3],\
holybigmem0[1-8],\
holygpu[01-16],\
holymoorcroft0[1-8],\
holystat0[1-9],holystat1[0-9],holystat2[0-2],\
hero40[01-11],hero46[01-16],hero47[01-16],\
hp010[1-4],hp020[1-4],hp030[1-4],hp040[1-4],hp050[1-4],hp060[1-4],\
hp070[1-4],hp080[1-4],hp090[1-4],hp100[1-4],hp110[1-4],hp120[1-4],\
hp130[1-4],hp140[1-4],hp150[1-4],hp160[1-4],hp170[1-4],hp180[1-4],\
hp190[1-4],hp200[1-4],hp210[1-4],hp220[1-4],hp230[1-4],hp240[1-4],\
hp250[1-4],hp260[1-4],hp270[1-4],\
hsph0[5-6],\
jenny0[1-4],\
karplus0[1-4],iliad20[1-9],iliad21[0-2],\
itc01[1-2],itc02[1-2],itc03[1-2],itc04[1-2],\
itc05[1-2],itc06[1-2],itc07[1-2],itc08[1-2],\
itc09[1-2],itc10[1-2],itc11[1-2],\
kou1[1-4],kou2[1-4],kou3[1-4],kou4[1-4],kou5[1-4],\
leroy0[1-4],\
moorcroft[02-04],\
nelson0[1-2],\
pmage1,\
regal[01-20],\
sandy-rc0[1-4],\
seasgpu0[1-9],seasgpu1[0-6],\
shock0[1-9],shock1[0-2],\
wofsy01[1-4],wofsy02[1-4],\
xie01,\
zorana0[1-2]

# Shakhnovich
PartitionName=shakhnovich Priority=10 \
    AllowGroups=rc_admin,shakhnovich_lab \
    Nodes=holy2a1420[1-8],holy2a1430[1-8],holy2a1510[1-8]

# Shock
PartitionName=shock Priority=10 \
    AllowGroups=rc_admin,stewart_lab\
    Nodes=shock0[1-9],shock1[0-2]

# Stats
PartitionName=stats Priority=10 \
    AllowGroups=rc_admin,airoldi_lab,rubin_lab,bornn_lab,slurm_group_stats \
    Nodes=holystat0[1-9],holystat1[0-9],holystat2[0-2]

# Stewart
PartitionName=stewart Priority=10 \
    AllowGroups=rc_admin,stewart_lab \
    Nodes=holy2b0720[1-8],holy2b0910[1-8]

# Unrestricted
PartitionName=unrestricted Priority=2 Shared=FORCE \
    AllowGroups=rc_admin,cluster_users \
    Nodes=holy2a2120[1-8]

# Wofsy
PartitionName=wofsy Priority=10 \
    AllowGroups=rc_admin,wofsy_lab \
    Nodes=wofsy01[1-4],wofsy02[1-4]

# Xie
PartitionName=xie Priority=10 \
    Nodes=xie01 \
    AllowGroups=rc_admin,xie_lab

# Zorana
PartitionName=zorana Priority=10 \
    Nodes=zorana0[1-2] \
    AllowGroups=rc_admin,brenner_lab"""
        sconffile = open(SLURM_CONF_FILENAME, 'w')
        sconffile.write(conf)
        sconffile.close()
        
        os.environ['SLURM_CONF'] = SLURM_CONF_FILENAME
        from slyme_v1 import SLURMCONFIG
        
        self.slurmConfig = SLURMCONFIG
        

    def tearDown(self):
        try:
            os.remove(SLURM_CONF_FILENAME)
        except:
            print("Problem removing file %s" % SLURM_CONF_FILENAME, \
                file=sys.stderr)


    def test_SlurmConfig(self):        
        # Test plain entry
        self.assertEqual(self.slurmConfig["ControlMachine"], "holy-slurm01", \
            "ControlMachine value is wrong %s" % self.slurmConfig["ControlMachine"])
        # Long-ish value
        self.assertEqual(self.slurmConfig["Licenses"], \
            "bicepfs1:100,kovac_holyscratch:500,huttenhower:20,lumerical:10,blackhole:32,panlfs_coati_100:100,panlfs_coati_200:200,cep_100:100", \
            "Licenses value is wrong %s" % self.slurmConfig["Licenses"])
        # Commented value shouldn't be there
        self.assertRaises(KeyError, lambda: self.slurmConfig["BackupController"])
        
        # Partition definitions should be a dict under Partitions
        self.assertEqual(self.slurmConfig["Partitions"]["zorana"], \
            "Priority=10     Nodes=zorana0[1-2]     AllowGroups=rc_admin,brenner_lab", \
            "zorana partition is incorrect '%s'" % self.slurmConfig["Partitions"]["zorana"])
        


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
