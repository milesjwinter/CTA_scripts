#!/usr/bin/env python

import tuneModule
import getSerial
import sqlSetTrimTest
import runInit
import LEDPulseWFs
import powerCycle
import lowSideLoopTD
import triggerThresh
import pickThresh
import time
import datetime
import run_control
import os, sys
import analyzeLowSideLoop
import prepareLog
import csv
import analyzeTriggerThreshScan
import plot_waves
import logging
import numpy as np
#from UtilsModuleT7 import *

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

logFormat = "%(module)s :: %(funcName)s : %(message)s"
logging.basicConfig(format=logFormat, level=logging.DEBUG)

moduleID = int(moduleID)



dataset = "testing"
assocRun = "runList.txt"
assocFile = "fileList.txt"

runListFile = open(assocRun,'w')
fileListFile = open(assocFile,'w')



#Begin power cycle
bps = powerCycle.powerCycle()



#Begin initialization
module, tester = runInit.Init()
#ReadTemp(module)
firstRun=0

#Begin LED Flasher Test with internal trigger
if(internalTrigger):
	trigger = 1
	runDuration=3
	consThresh, messedUpPick = pickThresh.pickThresh(testDir, testDirFinal, deadtime=12500)
	print "Pick thresh output"
	print consThresh
	for j in range(0,16):
	
		outRunList, outFileList = LEDPulseWFs.LEDPulseWaveforms(tester,module,frequency,trigger,runDuration, groupList=[j], thresh=consThresh, outputDir=outputDir)
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
		outRunList, outFileList = LEDPulseWFs.LEDPulseWaveforms(tester,module,frequency,trigger,runDuration, groupList=[j],thresh=consThresh, outputDir=outputDir)
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
numBlock=4
delay=0
frequency = 200 #in Hz


if(softwareTrigger):

	#trigger values are: 0 = external with LED on, 2=external with LED OFF, # 1=internal with LED ON, 3=internal with LED OFF, 9=software trgger with LED OFF, 10=software trigger with LED ON
	trigger = 9
	
	runDuration = 1 # in s
	for Vped in VpedList:
		tuneModule.getTunedWrite(moduleID,module,Vped, numBlock=numBlock, HV_ON=0)
		outRunList, outFileList = LEDPulseWFs.LEDPulseWaveforms(tester,module,frequency,trigger,runDuration, numBlock=numBlock,outputDir=outputDir)
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
	'''
	runInit.Close(module, tester)
	bps = powerCycle.powerCycle()
	module, tester = runInit.Init()
	runDuration = 0.001 # in s
	trigger = 10
	for Vped in VpedList:
		tuneModule.getTunedWrite(moduleID,module,Vped, numBlock=numBlock, HV_ON=1)
		outRunList, outFileList = LEDPulseWFs.LEDPulseWaveforms(tester,module,frequency,trigger,runDuration, numBlock=numBlock,outputDir=outputDir)
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
	'''
		
if(externalTrigger):
#	runInit.Close(module, tester)
	#VpedList=[1006, 1056,1106,1156,1206,1256,1306,1356,1406]
	#VpedList = [945, 1106, 1273, 1437, 1601, 1765, 1929]
        #VpedList = [ 125, 289, 453, 617, 781, 945, 1109, 1273, 1437, 1601, 1765, 1929, 2093, 2257, 2421, 2585, 2749, 2913, 3077, 3241, 3405, 3569, 3733, 3897, 4061]
        #VpedList = [ 206,  356,  506,  656,  806,  956, 1106, 1256, 1406, 1556, 1706, 1856, 2006, 2156, 2306, 2456, 2606, 2756, 2906, 3056, 3206, 3356, 3506, 3656]
	VpedList=[1556]
	numBlock=8	
	delay= 656  #604
	runDuration = 200#512 #1200
	Vped = 1556
        frequency = 200 #in Hz

	#This is a dummy run, just to get the temperature stable
	tuneModule.getTunedWrite(moduleID, FPM, module, Vped, numBlock=numBlock)
	for i in range(1):
                trigger = 2
		outRunList, outFileList = LEDPulseWFs.LEDPulseWaveforms(
                                          tester,
                                          module,
                                          frequency,
                                          trigger,
                                          runDuration,
                                          numBlock=numBlock,
                                          triggerDly=delay,
                                          outputDir=outputDir,
                                          local_rsync=True,
                                          log_temp=False,
                                          temp_file='temperature_log.txt',
                                          temp_interval=60,
                                          wasted_time=0)
                
                trigger = 0
                outRunList, outFileList = LEDPulseWFs.LEDPulseWaveforms(
                                          tester,
                                          module,
                                          frequency,
                                          trigger,
                                          runDuration,
                                          numBlock=numBlock,
                                          triggerDly=delay,
                                          outputDir=outputDir,
                                          local_rsync=True,
                                          log_temp=False,
                                          temp_file='temperature_log.txt',
                                          temp_interval=60,
                                          wasted_time=0)#780)
                
#	bps = powerCycle.powerCycle()
#	module, tester = runInit.Init()
	#Now take calibration data:
        '''
	for Vped in VpedList:
		tuneModule.getTunedWrite(moduleID,module,Vped, numBlock=numBlock, HV_ON=0)
		for i in range(1):
			outRunList, outFileList = LEDPulseWFs.LEDPulseWaveforms(tester,module,frequency,trigger,runDuration, numBlock=numBlock, triggerDly=delay, outputDir=outputDir)
        
	runInit.Close(module, tester)
	bps = powerCycle.powerCycle()
	module, tester = runInit.Init()
	
	Vped = 1106
        '
	#Again: Start with a dummy run
	tuneModule.getTunedWrite(moduleID,module,Vped, numBlock=numBlock, HV_ON=0)
	trigger = 2
	for i in range(1):
		outRunList, outFileList = LEDPulseWFs.LEDPulseWaveforms(tester,module,frequency,trigger,runDuration, numBlock=numBlock, triggerDly=delay, outputDir=outputDir)
	#Now take real data:
        
	for i in range(10):
		outRunList, outFileList = LEDPulseWFs.LEDPulseWaveforms(tester,module,frequency,trigger,runDuration, numBlock=numBlock, triggerDly=delay, outputDir=outputDir)
	'''


runInit.Close(module, tester)

powerCycle.powerOff(bps)

runListFile.close()
fileListFile.close()

print "Suite finished"



