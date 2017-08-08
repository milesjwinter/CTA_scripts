#!/usr/bin/env python

import run_control
import target_driver
import LED
import target_io
import numpy as np
from LED import *
import IO
import logRegisters
import logging
import subprocess
import os
import time
from threading import Timer

kBufferDepth = 50000 #should accomodate up to 50000 events and comply with available memory space for most event sizes
std_my_ip = "192.168.1.2"
std_kNPacketsPerEvent = 64 #One per channel
thresh=[750,900,900,850,700,850,850,700,700,800,800,600,900,900,900,850]

"""
The function runs the system with LED on with external or internal trigger
tester: tester board object
module: module object (FEE)
frequency: freq in Hz of LED flasher
trigger: {0 : 'external', 1 : 'internal', 2 : external without signal (so just noise test)}, 3 : internal trigger without LED (to find dark noise)
runDuration: how long the run is in seconds
"""

def activateMAX1230(module, adcList):
        value = np.uint32(0)
        for i in adcList:
                value|=(0x1 << 8+i)
        value|=(0x1 << 31)
        print "Writing value: ", hex(value), "to register."
        module.WriteRegister(0x15, value)

def readTemperature(module):
        adcList=[0,1,2,3]
        value = np.uint32(0)
        activateMAX1230(module, adcList)
        time.sleep(0.1)
        value = module.ReadRegister(0x34)[1]

        temperature=np.zeros(2)
        temperature[0] = np.uint32( (value >> 16) & 0xfff )/8.0
        temperature[1] = np.uint32( (value) & 0xfff )/8.0
        return temperature

def writeTemperature(module,runID,tempFile):
    print "READING MODULE TEMPERATURE:"
    temp = readTemperature(module)
    f = open(tempFile,'a')
    f.write("{}\t{}\t{}\t{}".format(runID,time.time(),temp[0],temp[1]))
    f.write("\n")
    f.close()
    print "The temperatures on the secondary board are: ", temp[0], "C and", temp[1], "C"

def temp_sleep_schedule(module,runDuration,temp_interval,runID,temp_file):
    print "Start taking data for", runDuration, "seconds."
    starttime = time.time()
    for i in range(runDuration/temp_interval):
        Timer(i*temp_interval,writeTemperature,args=[module,runID,temp_file]).start()
    time.sleep(runDuration)
    print "Stop taking data after", time.time()-starttime, "seconds."

def LEDPulseWaveforms(tester,module,frequency,trigger,runDuration, groupList=[1], numBlock=2, deadtime=12500, triggerDly=580, my_ip=std_my_ip, kNPacketsPerEvent=std_kNPacketsPerEvent,thresh=thresh, outputDir="output/",local_rsync=True, log_temp=True, temp_file='temperature_log.txt', temp_interval=60, wasted_time=0):


	outRunList=[]
	outFileList=[]


	ld=LED()
	hostname = run_control.getHostName()
	outdirname = run_control.getDataDirname(hostname)
	runID = run_control.incrementRunNumber(outdirname)

        #Check if remote data directory is mounted
        print "Checking if remote output directory is mounted"
        if os.path.ismount(os.environ['HOME']+'/target5and7data')==True:
            print "Output directory is mounted"
            #Check rsync preference and make local output directory if neccessary
            if local_rsync==True:
                print "Writing data with rsync enabled"
                print "Checking if local output directory exists"
                outdirname = os.environ['HOME']+'/test_suite/local_outputDir'
                try:
                        os.mkdir(outdirname)
                        print "No local output directory found: making it now..."
                except:
                        print "local output directory found"
            else:
                outdirname = outputDir
        #Stop if the remote directory isn't mounted
        else:
            print "Cannot connect to the remote output directory!"
            print 'Make sure ',os.environ['HOME']+'/target5and7data',' is mounted!'
            print 'Stopping Data Taking'
            raise SystemExit

	outFile = "%s/run%d.fits" % (outdirname,runID)
        outLogFile = "%s/run%d.log" % (outdirname,runID)
	outRunList.append(runID)
	outFileList.append(outFile)
	print "Writing to: %s" % outFile
#	numblock = 2
	#if multiple channels depend on FPGA settings
	kPacketSize = 22 + numBlock*64 #you can read it on wiresharks

	#the listener listens for data coming between the testerboard and computer and writesthe data  to a ringbuffer
	#Set up IO
	buf, writer, listener = IO.setUp(my_ip, kBufferDepth, kNPacketsPerEvent, kPacketSize, outFile)

	#used to switch on the LED
	if( trigger==0):
		ld.setLED(frequency,1,1) #run with trigger output enabled.
	elif( trigger==1):
		ld.setLED(frequency,0,1) #run only with flash enabled.
	elif( trigger==2):	
		ld.setLED(frequency,1,0) #run only with trigger enabled to record noise waveforms.
	elif( trigger==3):
		ld.LEDoff() #Turn LED off, run with internal trigger to record noise waveforms.
	elif( trigger==4):
		ld.setLED(frequency,1,0) #run only with trigger enabled to record noise waveforms.
	elif( trigger==9):
		ld.LEDoff() #Turn LED off, run with internal trigger to record noise waveforms.
	elif( trigger==10):
		ld.setLED(frequency,0,1) #run only with flash enabled.

	time.sleep(1)
	print "Trigger: ", trigger
	if( trigger>=9):
		print "Start taking software triggers."	
	
		module.WriteSetting("Row",5)
		module.WriteSetting("Column",0)
		if(trigger==9):
			tester.EnableSoftwareTrigger(True)
			writer.StartWatchingBuffer(buf)
		
			starttime = time.time()
			for i in range(int(runDuration*frequency) ):
		
				tester.SendSoftwareTrigger()
				time.sleep(1.0/(2.0*frequency) )
		
			endtime = time.time()
			print "Stop taking data after", endtime-starttime, "seconds."
			writer.StopWatchingBuffer()
			tester.EnableSoftwareTrigger(False)

		if(trigger==10):
			print "Start sync output!"
		#	tester.EnableExternalTrigger(True) #data is produced
			module.WriteSetting("TACK_EnableTrigger", 0x10000)
			module.WriteSetting("ExtTriggerDirection", 0x1)
			writer.StartWatchingBuffer(buf)
			time.sleep(20)
			writer.StopWatchingBuffer()
		#	tester.EnableExternalTrigger(False) #stop producing data
			print "Finished sync output!"
			module.WriteSetting("TACK_EnableTrigger", 0x0)
			module.WriteSetting("ExtTriggerDirection", 0x0)
	 	logRegisters.logRegister(module, outdirname, runID)


	else:
		if (trigger%2)==0: #for external trigger
			##module.WriteSetting("TriggerDelay",93) #to tell the FPGA how far to look back in time in order to see the actual trigger (acounting for the time it took everything to communicate)
			module.WriteSetting("TriggerDelay",triggerDly) #to tell the FPGA how far to look back in time in order to see the actual trigger (acounting for the time it took everything to communicate)
			#Read the ASIC temperature:
			temperature = 0 #module.ReadSetting("ADC0_Temperature1")
			value = module.ReadRegister(52)
			print "Temperature: ", temperature, "Register: ", value
			hexValue = "0x%08x" % value[1]
				
			time.sleep(1)

			writer.StartWatchingBuffer(buf) #here the ring buffer is observed, but no data is coming in yet
			tester.EnableExternalTrigger(True) #data is produced
                        if log_temp==True:
                            print 'Taking data with temperature logging'
                            temp_sleep_schedule(module,runDuration,temp_interval,runID,temp_file)
                        else:
                            print "Start taking data for", runDuration, "seconds."
                            starttime = time.time()
                            time.sleep(runDuration)
                            endtime = time.time()
                            print "Stop taking data after", endtime-starttime, "seconds."

			tester.EnableExternalTrigger(False) #stop producing data
			writer.StopWatchingBuffer() #stops looking at the ring buffer			
	 		logRegisters.logRegister(module, outdirname, runID)
			
	###		outRunList[outRunList.index([runID])].append(["EXT"])
		elif (trigger%2)==1: #for internal trigger
			tester.SetTriggerModeAndType(0b00, 0b00) #makes sure the internal trigger is used
			tester.SetTriggerDeadTime(deadtime) #deadtime is the time the trigger is disabled after it has sent out data
			
	
			module.WriteSetting("TriggerDelay",triggerDly) #to tell the FPGA how far to look back in time in order to see the actual trigger (acounting for the time it took everything to communicate)
			for asic in range(4):
				for group in range(4):
					module.WriteASICSetting("Thresh_{}".format(group), asic, int(thresh[asic*4+group]), True) #sets the trigger threshold that has been determined in another test
					tester.EnableTrigger(asic,group,False)
			#this loop enables the trigger for the groups icluded in grouplist
			starttime = time.time()
			for trgroup in groupList:
				asic=int(trgroup)/4
				group=int(trgroup)%4
				print "Enable trigger for:", asic, group 
				tester.EnableTrigger(asic,group,True)
			#print "Start taking data for", runDuration, "seconds."
	
	
			writer.StartWatchingBuffer(buf) #starts watching the ring buffer
			time.sleep(runDuration)
			writer.StopWatchingBuffer()
	###		outRunList[outRunList.index([runID])].append(groupList)
			#switch off all trigger again
			for trgroup in groupList:
				asic=int(trgroup)/4
				group=int(trgroup)%4 
				tester.EnableTrigger(asic,group,False)
			endtime = time.time()
			print "Stop taking data after", endtime-starttime, "seconds."
		
 			logRegisters.logRegister(module, outdirname, runID)
	
		#Turns off LED, but only if on before!
	if(trigger<3):
		ld.LEDoff()
	ld.close()
	IO.stopData(listener, writer)
	
        #Perform rsync if required
        if local_rsync==True:
            print "Starting RSYNC: moving run files to "+outputDir
            cmd = "rsync -tvrq --remove-source-files --omit-dir-times {0}/*.fits {0}/*.log {1}".format(outdirname, outputDir)
            p = subprocess.Popen(cmd, shell=True, stdin=None, stdout=None, stderr=None, close_fds=True)
            #p.wait()

        if log_temp==True:
            listener.StartListening()
            print 'Data taking disabled: sleeping for {}'.format(wasted_time)
            temp_sleep_schedule(module,wasted_time,temp_interval,runID,temp_file)
            listener.StopListening()

	return outRunList, outFileList
