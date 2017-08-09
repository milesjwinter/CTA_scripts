import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator
import time
import sys
from scipy.stats import gaussian_kde

start_time = time.time()

#run parameters and temp arrays
#runs = np.arange(320247,320251,1)
runs = [320247]
total_charge = np.array([])
total_position = np.array([])
total_amplitude = np.array([])
total_ped_max = np.array([])
select_range = np.arange(180,200,1)
Ncells = 256
 
#Loop through each run
for run_num in runs:
    print "Loading charge spectrum: Run ",run_num
    #Loop through each asic
    for Nasic in range(1):
        #Loop through each channel
        for Nchannel in range(14,15):

            #Load charge spectrum
            infile = "../charge_spectrum_files/ped_sub_charge_spectrum_Run"+str(run_num)+"_ASIC"+str(Nasic)+"_CH"+str(Nchannel)+".npz"
            data = np.load(infile)
            run = data['run']
            asic = data['asic']
            channel = data['channel']
            event = data['event']
            block = data['block']
            phase = data['phase']
            charge = data['charge']
            position = data['position']
            amplitude = data['amplitude']
            ped_max = data['ped_max']
            ped_min = data['ped_min']
            del data

            print "Number of Events: ",len(event)

	    temp_charge = np.array([])
	    temp_position = np.array([])
	    temp_amplitude = np.array([])
            temp_ped_max = np.array([])

            Nevents = len(event)
            print "Applying data cuts: Asic ",Nasic," Channel ", Nchannel
	    for i in range(Nevents):
                if(i%100==0):
                    sys.stdout.write('\r')
                    sys.stdout.write("[%-100s] %.1f%%" % ('='*int((i)*100./(Nevents)) , (i)*100./(Nevents)))
                    sys.stdout.flush()
                if charge[i] > -100.:
                    if ped_max[i]<=10.:
                        if position[i] in select_range:
                            
			    temp_charge = np.append(temp_charge,charge[i])
			    temp_position = np.append(temp_position,position[i])
			    temp_amplitude = np.append(temp_amplitude,amplitude[i])
			    temp_ped_max = np.append(temp_ped_max,ped_max[i])

            sys.stdout.write('\n')
            total_charge = np.append(total_charge,temp_charge)
            total_position = np.append(total_position,temp_position)
            total_amplitude = np.append(total_amplitude,temp_amplitude)
            total_ped_max = np.append(total_ped_max,temp_ped_max)

print 'Analysis complete: job time ', time.time() - start_time
minorLocator = AutoMinorLocator()


fig, ax = plt.subplots(figsize=(14,7))
plt.hist(total_charge,bins=np.arange(-60,800,4),edgecolor='k')
plt.title('Charge Spectrum',fontsize=24)
plt.xlabel('Charge (ADC$\cdot$ns)',fontsize=20)
plt.ylabel('Counts',fontsize=20)
ax.xaxis.set_minor_locator(minorLocator)
ax.yaxis.set_minor_locator(minorLocator)
plt.tick_params(which='major', length=7, width=2)
plt.tick_params(which='minor', length=4)
plt.minorticks_on()
plt.grid('off')
plt.show()


fig, ax = plt.subplots(figsize=(14,7))
plt.hist(total_position,bins=np.arange(0,Ncells,1),edgecolor='k')
plt.title('Position of Max Pulse Height',fontsize=24)
plt.xlabel('Time (ns)',fontsize=20)
plt.ylabel('Counts',fontsize=20)
plt.xlim([0,Ncells])
plt.xticks(np.arange(0,Ncells+2, 32.0))
ax.xaxis.set_minor_locator(minorLocator)
ax.yaxis.set_minor_locator(minorLocator)
plt.tick_params(which='major', length=7, width=2)
plt.tick_params(which='minor', length=4)
plt.minorticks_on()
plt.grid('off')
plt.show()


fig, ax = plt.subplots(figsize=(14,7))
plt.hist(total_amplitude*0.609,bins=np.arange(-10,100,2*0.609),edgecolor='k')
plt.title('Maximum Pulse Amplitude',fontsize=24)
plt.xlabel('Amplitude (ADC)',fontsize=20)
plt.ylabel('Counts',fontsize=20)
ax.xaxis.set_minor_locator(minorLocator)
ax.yaxis.set_minor_locator(minorLocator)
plt.tick_params(which='major', length=7, width=2)
plt.tick_params(which='minor', length=4)
plt.minorticks_on()
plt.grid('off')
plt.show()


