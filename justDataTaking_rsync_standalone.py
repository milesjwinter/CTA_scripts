#!/usr/bin/env python

import tuneModule
#import getSerial
import runInit_standalone
#import LEDPulseWFs_standalone
import LEDPulseWFs_rsync_standalone
import lowSideLoopTD
import triggerThresh
import pickThresh
import time
import datetime
import run_control
import os
import sys
import analyzeLowSideLoop
import prepareLog
import csv
import analyzeTriggerThreshScan
import plot_waves
import logging
import numpy as np

internalTrigger=0
externalTrigger=1
softwareTrigger=0

def refreshFile(inFile, inFileName):
	inFile.close()
	inFile = open(inFileName,'a')
	return inFile	

argList = sys.argv

print argList

name = None
purpose = "General test."
logLevel = None
emailAddress = None


##outputDir = "/Users/tmeures/test_suite/output_photon/"
outputDir = "/Users/mileswinter/target5and7data/"
#outputDir = "outputIndividual/"
print "Checking if output directory exists and is mounted"
try:
	os.mkdir (outputDir)
except:
	print "Output-directory already exists."

#Check if remote data directory is mounted
if os.path.ismount(os.environ['HOME']+'/target5and7data')==True:
    print "Output-directory is mounted"
else:
    print "Cannot connect to the remote output directory!"
    print 'Make sure ',os.environ['HOME']+'/target5and7data',' is mounted!'
    print 'EXITING'
    raise SystemExit


testDir = outputDir
testDirFinal = '/Users/mileswinter/target5and7data/test_suite_output/FEE116FPM4.12/'
if(len(argList)<4):
	print "Not enough input arguments!"
	name = "General"
	logLevel = 3
	logToFile= 0
	purpose = "test"
else:
	name = argList[1]
#	purpose = argList[2]
	logLevel = int(argList[2])
	logToFile = int(argList[3])
	purpose = " ".join(str(x) for x in argList[4:len(argList)])

#moduleID,FPM = getSerial.getSerial()
moduleID=116
FPM=[4,9]

logFormat = "%(module)s :: %(funcName)s : %(msecs)d : %(message)s"
logging.basicConfig(format=logFormat, level=logging.DEBUG)

moduleID = int(moduleID)

#Initialize looging and produce neede file outputs.
###dataset, testDir, assocRun, assocFile, moduleID, FPM, purpose, user, logFileName, testDirFinal, fitsDir = prepareLog.prepareLog(moduleID, FPM, name, purpose, logLevel, logToFile, outputDir)
##dataset = "20160713_0736"

#original_stdout =  sys.stdout
#sys.stdout = logFile 



dataset = "testing"
assocRun = "runList.txt"
assocFile = "fileList.txt"

runListFile = open(assocRun,'w')
fileListFile = open(assocFile,'w')



#Begin power cycle



#Begin initialization
module, tester = runInit_standalone.Init()
Vped = 1106

firstRun=0

#Begin tuning


Vped = 1106
#tuneModule.getTunedWrite(moduleID,module,Vped)




#finds a conservative Thresh value for each trigger pixel in the module


frequency = 1000


#Begin LED Flasher Test with internal trigger
if(internalTrigger):
	trigger = 1
	runDuration=3
	consThresh, messedUpPick = pickThresh.pickThresh(testDir, testDirFinal, deadtime=12500)
	print "Pick thresh output"
	print consThresh
	for j in range(0,16):
	
		outRunList, outFileList = LEDPulseWFs_standalone.LEDPulseWaveforms(tester,module,frequency,trigger,runDuration, groupList=[j], thresh=consThresh, outputDir=outputDir)
		runListFile.write("Flasher with internal trigger, group: %d\n" % j)
		fileListFile.write("Flasher with internal trigger, group: %d\n" % j)
		runListFile = refreshFile(runListFile, assocRun)
		fileListFile = refreshFile(fileListFile, assocFile)
		for i in outRunList:
			runListFile.write("%d\n" % i)
		for i in outFileList:
			fileListFile.write("%s\n" % i)
		runListFile = refreshFile(runListFile, assocRun)
		fileListFile = refreshFile(fileListFile, assocFile)
	
	#	plot_waves.plot_events(outRunList, testDir, dataset, group=j)



#Begin noise test with internal trigger
	trigger = 3
	runDuration = 10
	for j in range(0,16):
		outRunList, outFileList = LEDPulseWFs_standalone.LEDPulseWaveforms(tester,module,frequency,trigger,runDuration, groupList=[j],thresh=consThresh, outputDir=outputDir)
		runListFile.write("Noise with internal trigger, group: %d\n" % j)
		fileListFile.write("Noise with internal trigger, group: %d\n" % j)
		runListFile = refreshFile(runListFile, assocRun)
		fileListFile = refreshFile(fileListFile, assocFile)
		for i in outRunList:
			runListFile.write("%d\n" % i)
		for i in outFileList:
			fileListFile.write("%s\n" % i)
		runListFile = refreshFile(runListFile, assocRun)
		fileListFile = refreshFile(fileListFile, assocFile)
	 
	#	plot_waves.plot_events(outRunList, testDir, dataset, group=j)
	
#Begin noise test with external trigger

VpedList = [1106]
numBlock=2
delay=0

if(softwareTrigger):

	trigger = 9
	
	runDuration = 6
	for Vped in VpedList:
		tuneModule.getTunedWrite(moduleID,module,Vped, numBlock=numBlock)
		outRunList, outFileList = LEDPulseWFs_standalone.LEDPulseWaveforms(tester,module,frequency,trigger,runDuration, numBlock=numBlock,outputDir=outputDir)
		if(firstRun==0): firstRun = outRunList[0]
		runListFile.write("Software trigger\n")
		fileListFile.write("Software trigger\n")
		runListFile = refreshFile(runListFile, assocRun)
		fileListFile = refreshFile(fileListFile, assocFile)
		for i in outRunList:
			runListFile.write("%d\n" % i)
		for i in outFileList:
			fileListFile.write("%s\n" % i)
		runListFile = refreshFile(runListFile, assocRun)
		fileListFile = refreshFile(fileListFile, assocFile)
	


if(externalTrigger):
        frequency = 200 #200 #in Hz
        numBlock=8
        delay= 656 #320 #356 #720+32 #308+48 #1004  #604
        runDuration = 15 #1200
        Vped = 1106 #1106
        #VpedList=[1556]  #[1106]
        #VpedList = np.arange(206,3507,150)
        #VpedList=np.ones(4,dtype=int)*1106
        
        tuneModule.getTunedWrite(moduleID, FPM, module,Vped, numBlock=numBlock)
	#consThresh, messedUpPick, third_thing = pickThresh.pickThresh(testDir, testDirFinal, deadtime=12500)

        VpedList=np.ones(2,dtype=int)*1106
	for Vped in VpedList:
		#tuneModule.getTunedWrite(moduleID, FPM, module,Vped, numBlock=numBlock)
                print "DELAY: ",delay
		trigger = 2
		outRunList, outFileList = LEDPulseWFs_rsync_standalone.LEDPulseWaveforms(
                                          tester,
                                          module,
                                          frequency,
                                          trigger,
                                          runDuration, 
                                          numBlock=numBlock, 
                                          triggerDly=delay, 
                                          outputDir=outputDir,
                                          local_rsync=True, 
                                          log_temp=True, 
                                          temp_file='temperature_log.txt', 
                                          temp_interval=5,
                                          wasted_time=0)
                #delay = delay + 400
        '''
        VpedList=np.ones(2,dtype=int)*1556
        Vped = 1556
        tuneModule.getTunedWrite(moduleID, FPM, module,Vped, numBlock=numBlock)
        for Vped in VpedList:
                #tuneModule.getTunedWrite(moduleID, FPM, module,Vped, numBlock=numBlock)
                trigger = 2
                outRunList, outFileList = LEDPulseWFs_standalone.LEDPulseWaveforms(tester,module,frequency,trigger,runDuration, numBlock=numBlock, triggerDly=delay, outputDir=outputDir)
        
        VpedList = np.arange(206,3507,150)
        runDuration = 30
        for Vped in VpedList:
                tuneModule.getTunedWrite(moduleID, FPM, module,Vped, numBlock=numBlock)
                trigger = 2
                outRunList, outFileList = LEDPulseWFs_standalone.LEDPulseWaveforms(tester,module,frequency,trigger,runDuration, numBlock=numBlock, triggerDly=delay, outputDir=outputDir, local_rsync=True)


	
	for Vped in VpedList:
	
		tuneModule.getTunedWrite(moduleID,module,Vped, numBlock=numBlock)
		trigger = 2
		runDuration = 200
		outRunList, outFileList = LEDPulseWFs_standalone.LEDPulseWaveforms(tester,module,frequency,trigger,runDuration, numBlock=numBlock, triggerDly=delay, outputDir=outputDir)

	Vped=1106
	tuneModule.getTunedWrite(moduleID,module,Vped, numBlock=numBlock)

	trigger = 0
	runDuration = 600
	outRunList, outFileList = LEDPulseWFs_standalone.LEDPulseWaveforms(tester,module,frequency,trigger,runDuration, numBlock=numBlock, triggerDly=delay, outputDir=outputDir)

	Vped=1106
	tuneModule.getTunedWrite(moduleID,module,Vped, numBlock=numBlock)

	trigger = 0
	runDuration = 600
	outRunList, outFileList = LEDPulseWFs_standalone.LEDPulseWaveforms(tester,module,frequency,trigger,runDuration, numBlock=numBlock, triggerDly=delay, outputDir=outputDir)

	for Vped in VpedList:
	
		tuneModule.getTunedWrite(moduleID,module,Vped, numBlock=numBlock)
		trigger = 2
		runDuration = 200
		outRunList, outFileList = LEDPulseWFs_standalone.LEDPulseWaveforms(tester,module,frequency,trigger,runDuration, numBlock=numBlock, triggerDly=delay, outputDir=outputDir)
	


	'''





runInit_standalone.Close(module, tester)


runListFile.close()
fileListFile.close()

print "Suite finished"



