import target_io
import target_driver
import numpy as np
import sys
import time

argList = sys.argv

if(len(argList)>2):
	start = int(argList[1])
	stop = int(argList[2])
elif(len(argList)>1):
	start = int(argList[1])
	stop = start
else:
	start = 292836
	stop = 292836
print argList
print start, stop


for i in range(start,stop+1):
   runN = i

   channelsPerPacket=1
   filename = "/Users/mileswinter/target5and7data/run"+str(runN)+".fits"
   for Nasic in range(1):
	for Nchannel in range(14,15):
        #for Nchannel in range(2,3):
                
                startTime = time.time()

		reader = target_io.EventFileReader(filename)
		nEvents = reader.GetNEvents()
		#Do this once, so we can determine the number of samples in the waveform:
	        rawdata = reader.GetEventPacket(0,0)
	        packet = target_driver.DataPacket()
	        packet.Assign(rawdata, reader.GetPacketSize())
	        wf = packet.GetWaveform(0)
		nSamples = wf.GetSamples()

		print "Writing Events For Run:", runN, " Asic: ",Nasic," Channel: ",Nchannel
                print "Number of events: ", nEvents, ", Length of the waveform: ", nSamples

		limit=2000000
		startEvents=0
		if(nEvents>limit):
			print "Plot only first %d events!" % limit
			nEvents=limit
  

                #name output file and create array to hold samples
                outfile = "runFiles/sampleFileAllBlocks_run"+str(runN)+"ASIC"+str(Nasic)+"CH"+str(Nchannel)+".npz"
                run = np.ones(nEvents,dtype=int)*runN
                asic = np.ones(nEvents,dtype=int)*Nasic
                channel = np.ones(nEvents,dtype=int)*Nchannel
                event = np.zeros(nEvents,dtype=int)
                block = np.zeros(nEvents,dtype=int)
                phase = np.zeros(nEvents,dtype=int)
                samples = np.zeros((nEvents,nSamples),dtype=int)
	        for ievt in range(startEvents,nEvents):
			if(ievt%100==0):
				sys.stdout.write('\r')
				sys.stdout.write("[%-100s] %.1f%%" % ('='*int((ievt-startEvents)*100.0/(nEvents-startEvents)) , (ievt-startEvents)*100.0/(nEvents-startEvents)))
				sys.stdout.flush()
	                rawdata = reader.GetEventPacket(ievt,Nasic*16/channelsPerPacket+Nchannel/channelsPerPacket)
                        packet = target_driver.DataPacket()
	                packet.Assign(rawdata, reader.GetPacketSize())
			#blockNumber=(packet.GetRow()*64 + packet.GetColumn())
                        blockNumber = (packet.GetColumn()*8+packet.GetRow())
                        #print 'row: ',packet.GetRow(),' column: ',packet.GetColumn(),' Wrong ID: ', blockNumber, ' Correct ID: ',correctNumber
			blockPhase=(packet.GetBlockPhase() )
                        #print " E ",ievt, " B ",blockNumber," P ",blockPhase," R ",packet.GetRow()*64," C ",packet.GetColumn()
                        #offset = blockPhase - int(int(blockPhase)/8)*8
                        #print blockPhase
	                wf = packet.GetWaveform(Nchannel%channelsPerPacket)
                        event[ievt] = int(ievt)
                        block[ievt] = int(blockNumber)
                        phase[ievt] = int(blockPhase)
                        #print blockNumber,'  ', blockPhase
		        for sample in range(nSamples):
                                samples[ievt,sample] = int(wf.GetADC(sample))

                #store data with associated keywords
                #######################################################################
                #LOADING DATA: use np.load('path/filename.npz')                       #
                #List of keywords: run, asic, channel, event, block, phase, samples   #
                #EXAMPLE: my_data = np.load('path/filename.npz')                      #
                #Now call keyword: phase = my_data['phase']                           #
                #######################################################################
                np.savez_compressed(outfile,run=run, asic=asic, channel=channel, event=event, block=block, phase=phase, samples=samples)

                sys.stdout.write('\n')
                print "Writing Complete: Saving to",outfile
                print "Job Time: ", time.time()- startTime, "seconds."
                sys.stdout.write('\n')
	
