#------------------------------------------------------------------------#
#  Author: Miles Winter                                                  #
#  Date: 07-07-2017                                                      #
#  Project: CTA                                                          #
#  Desc: Calculate average pedestal waveforms from calibration           #
#        data and create a database for storage                          #
#  Note: Need h5py installed: pip install --upgrade h5py                 #
#        Documentation at http://www.h5py.org/                           #
#------------------------------------------------------------------------#

#import modules
import numpy as np
import h5py
import os, pwd, sys


#Output file name of the pedestal waveform database
outfile = "pedestal_database.h5"

#Run details
runs = [320254]          #Run number(s) of calibration data
indir = "./run_files/"   #Directory with run files
Nblocks = 8              #Number of blocks read out
Ncells = Nblocks*32      #Total number of cells
nPhases = 4              #Number of phases


#------------------------------------------------------------------------#


#Check if filename already exists
if os.path.isfile(outfile)==True:
    print 'The file %s already exists!'%outfile
    answers = {"yes","no"}
    choice = ''
    while True:
	choice = raw_input("Would you like to overwrite it? (yes/no) ")
	if choice in answers:
	    break
	else:
	    print "Not an acceptable input, try again %s!"%pwd.getpwuid(os.getuid()).pw_name
    if choice == 'no':
        print 'EXITING'
	raise SystemExit

#Create database to hold average pedestal waveforms
f = h5py.File(outfile,"w")

#Loop through each asic
for Nasic in xrange(1):
    #Loop through each channel
    for Nchannel in xrange(14,15):
        print "Processing Asic %s Channel %s"%(Nasic,Nchannel)

        #create arrays to hold pedestals
        avg_pedestal = np.zeros((512,nPhases,Ncells))
        counts = np.zeros((512,nPhases))

        #Loop through each run
        for run_num in runs:
            print "Loading raw waveforms: Run ",run_num

            #Load samples
            infile = indir+"sampleFileAllBlocks_run"+str(run_num)+"ASIC"+str(Nasic)+"CH"+str(Nchannel)+".npz"
            data = np.load(infile)
            event = data['event']
            asic = data['asic']
            channel = data['channel']
            block = data['block']
            phase = data['phase']
            samples = np.array(data['samples'],dtype='float32')
            del data

            Nevents = len(event)           
            for q in xrange(Nevents):
                if(q%100==0):
                    sys.stdout.write('\r')
                    sys.stdout.write("[%-100s] %.1f%%" % ('='*int((q)*100./(Nevents)) , (q)*100./(Nevents)))
                    sys.stdout.flush()

                b = block[q]
                #p = phase[q]  #use this for backplane
                #p = (phase[q]-4)/8  #use this for testerboard
                p = phase[q]/8     #or use this for testerboard
                if np.amin(samples[q])>100.:  #Reject events with data spikes
                    avg_pedestal[b,p,:] += samples[q,:]
                    counts[b,p] += 1.

            sys.stdout.write('\n')

        #Create database branches and adding pedestal waveforms
        print "Adding pedestal waveforms for Asic %s Channel %s to database"%(Nasic,Nchannel)
	for b in xrange(512):
	    for p in xrange(nPhases):
                branch_label = 'Asic%s/Channel%s/Block%s/Phase%s'%(Nasic,Nchannel,b,p)
                branch_data = f.create_dataset(branch_label, (Ncells,), dtype='f')
		if counts[b,p]>0.:
		    branch_data[:] = np.round(avg_pedestal[b,p,:]/counts[b,p],decimals=2)
                #else:
                #    branch_data[:] = np.zeros(Ncells)
f.close()
