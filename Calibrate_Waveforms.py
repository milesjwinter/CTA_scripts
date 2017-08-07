#------------------------------------------------------------------------#
#  Author: Miles Winter                                                  #
#  Date: 07-07-2017                                                      #
#  Project: CTA                                                          #
#  Desc: Calibrate raw waveforms with pedestal subtraction               #
#  Note: Need h5py installed: pip install --upgrade h5py                 #
#        Documentation at http://www.h5py.org/                           #
#------------------------------------------------------------------------#

#import modules
import numpy as np
import h5py
import os, sys
import time

start_time = time.time()

#Run details
runs = [320246]                  #Run number(s) of data to calibrate
indir = './run_files/'           #Directory with run files
outdir = './ped_sub_waveforms/'  #Output directory for calibrated waveforms

#Pedestal database details
ped_database_name = 'pedestal_database.h5'


#------------------------------------------------------------------------#

#Check if output directory exists
try:
        os.mkdir(outdir)
        print "Output directory doesn't exist. Making it now..."
        print "Writing output to %s "%outdir
except:
        print "Writing output to %s "%outdir

#Load pedestal waveform directory
f = h5py.File(ped_database_name,'r')

#Loop through each asic
for Nasic in xrange(1):
    #Loop through each channel
    for Nchannel in xrange(14,15):

        print "loading pedestal woveforms for Asic %s Channel %s"%(Nasic,Nchannel)
        ped_group = f['Asic%s/Channel%s'%(Nasic,Nchannel)]

        #Loop through each run
        for Nrun in runs:

            #create output file for calibrated samples
            outfile = outdir+"calibrated_samples_Run"+str(Nrun)+"_ASIC"+str(Nasic)+"_CH"+str(Nchannel)+".npz"
            
            print 'Processing Run ',Nrun,' Asic ',Nasic,' Channel ',Nchannel
            #Load samples
            data = np.load(indir+"/sampleFileAllBlocks_run"+str(Nrun)+"ASIC"+str(Nasic)+"CH"+str(Nchannel)+".npz")
            run = np.array(data['run'],dtype=int)
            asic = np.array(data['asic'],dtype=int)
            channel = np.array(data['channel'],dtype=int)
            event = np.array(data['event'],dtype=int)
            block = np.array(data['block'],dtype=int)
            phase = np.array(data['phase'],dtype=int)
            raw_samples = np.array(data['samples'],dtype=int)
            del data

            #loop through all waveform and perform pedestal subtraction
            samp_size = raw_samples.shape
            samples = np.zeros(samp_size)
            Nevents = len(event)
            for i in xrange(Nevents):
                if(i%100==0):
                    sys.stdout.write('\r')
                    sys.stdout.write("[%-100s] %.1f%%" % ('='*int((i)*100./(Nevents)) , (i)*100./(Nevents)))
                    sys.stdout.flush()

                b = block[i]
                #p = phase[i] #use this for backplane
                p = phase[i]/8 #use this for testerboard
                #p = (phase[i]-4)/8 #or use this for testerboard
                pedestal = ped_group['Block%s/Phase%s'%(b,p)] 
                samples[i,:] = raw_samples[i]-pedestal

            sys.stdout.write('\n')   
 
            #save calibrated samples to compressed numpy array
            #To load data, use np.load('path/filename.npz')['keyword'] 
            #List of keywords: run, asic, channel, event, block, phase, samples
            #EXAMPLE: blockphase = np.load('path/filename.npz')['phase']
            print 'Calibration complete: Compressing numpy array '
            np.savez_compressed(outfile,run=run,asic=asic,channel=channel,event=event,block=block,phase=phase,samples=samples)
            print 'Calibrated waveforms written to %s'%outfile
f.close()   

print 'job time: ',time.time()-start_time        
