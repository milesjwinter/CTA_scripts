"""
Miles Winter
Charge spectrum 
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import time
import sys

start_time = time.time()

#Gaussian
def gauss_function(x, a, x0, sigma):
    return a*np.exp(-(x-x0)**2/(2.*sigma**2))

#Run information
runs = np.arange(320247,320251,1)
Ncells = 8*32
window_start = 180
window_stop = 200
low_window_size = 4
up_window_size = 4
fixed_position = 153
fit_size = 10
nPhases = 4


#Loop through each run
for run_num in runs:
    print "Loading calibrated waveforms: Run ",run_num
    #Loop through each asic
    for Nasic in range(1):
        #Loop through each channel
        for Nchannel in range(14,15): 
           
            #Load samples
            data = np.load("base_cal_runs/base_cal_samples_Run"+str(run_num)+"_ASIC"+str(Nasic)+"_CH"+str(Nchannel)+".npz")
            run = data['run']
            asic = data['asic']
            channel = data['channel']
            event = data['event']
            block = data['block']
            phase = data['phase']
            samples = data['samples']
            del data
            
            #initialize a few variables and temp arrays
            Nevents = len(event)         #num of events in samples
            charge = np.zeros(Nevents)
            position = np.zeros(Nevents,dtype=int)
            amplitude = np.zeros(Nevents)
            ped_max = np.zeros(Nevents)
            ped_min = np.zeros(Nevents)
            fit_charge = np.zeros(Nevents,dtype=int)
            fit_position = np.zeros(Nevents,dtype=int)
            fit_amplitude = np.zeros(Nevents)
            fit_width = np.zeros(Nevents)
       
            #Correct samples with pedestal subtraction in mV.
            pedestal = np.mean(samples[:,:128],axis=1)
            pedestal = pedestal.reshape(len(pedestal),1)
            corr_samples = samples-pedestal
            
            #Loop through all events in samples
            print "Generating Charge Spectrum: Asic ",Nasic," Channel ", Nchannel
            for i in range(Nevents): 
                if(i%100==0):
                    sys.stdout.write('\r')
                    sys.stdout.write("[%-100s] %.1f%%" % ('='*int((i)*100./(Nevents)) , (i)*100./(Nevents)))
                    sys.stdout.flush()
                    
                #determine pulse position
                position[i] = window_start+np.argmax(corr_samples[i,window_start:window_stop])
                amplitude[i] = corr_samples[i,position[i]]
                start_integrate = position[i]-low_window_size
                stop_integrate = position[i]+up_window_size
                if start_integrate<0:
                    start_integrate = 0
                if stop_integrate > Ncells:
                    stop_integrate = Ncells
                 
                charge[i] = np.sum(corr_samples[i,start_integrate:stop_integrate])
                ped_max[i] = np.amax(corr_samples[i,:128])
                ped_min[i] = np.amin(corr_samples[i,:128])
            
                
                if amplitude[i]>5.:                     
                    try:                
                        fit_start =  position[i]-fit_size
                        fit_stop =  position[i]+fit_size
                        x = np.arange(fit_start,fit_stop,1)
                        y = corr_samples[i,fit_start:fit_stop]
                        popt, pcov = curve_fit(gauss_function, x, y, p0 = [amplitude[i], position[i], sigma])
                        points = np.arange(0,Ncells,1)
                        start_int = int(popt[1]-low_window_size)
                        stop_int = int(popt[1]+up_window_size)
                        fit_charge[i] = np.sum(corr_samples[i,start_int:stop_int])
                        fit_amplitude[i] = popt[0]
                        fit_position[i] = popt[1]
                        fit_width[i] = popt[2]
        
                    except RuntimeError:
                        fit_charge[i]=0
                else:
                    fit_charge[i] = np.sum(corr_samples[i,start_integrate:stop_integrate])                        
                
                   
	    sys.stdout.write('\n')
	    print 'Run: ',run_num, ' job time: ', time.time() - start_time
	    
	    #Store results in a text file
	    print "Saving charge spectrum for run ",run_num," to external file"
            outfile = "charge_spectrum_files/ped_sub_charge_spectrum_Run"+str(run_num)+"_ASIC"+str(Nasic)+"_CH"+str(Nchannel)+".npz"
            np.savez_compressed(outfile, 
                                run=run, 
                                asic=asic, 
                                channel=channel, 
                                event=event, 
                                block=block, 
                                phase=phase, 
                                charge=charge, 
                                position=position, 
                                amplitude=amplitude, 
                                fit_width=fit_width,
                                fit_charge=fit_charge, 
                                fit_position=fit_position, 
                                fit_amplitude=fit_amplitude,
                                ped_max=ped_max, 
                                ped_min=ped_min)
	    print 'Analysis complete: job time ', time.time() - start_time

