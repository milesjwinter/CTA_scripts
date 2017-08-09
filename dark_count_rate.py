import numpy as np
import os, sys, matplotlib
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.optimize import minimize
from scipy.misc import factorial

def poisson(k, lamb):
    """poisson pdf, parameter lamb is the fit parameter"""
    return (lamb**k/factorial(k)) * np.exp(-lamb)

def negLogLikelihood(params, data):
    """ the negative log-Likelohood-Function"""
    lnl = - np.sum(np.log(poisson(data, params[0])))
    return lnl


#Run information
runs = [317050,317052,317053,317054,316175,316176,316177,316178,316179]
Nblocks = 4
Ncells = Nblocks*32
start = 0
stop = 128
delta_t = float(stop-start)

all_amp_vals = np.array([])
all_cal_amp_vals = np.array([])
all_charge_vals = np.array([])
all_cal_charge_vals = np.array([])
all_pos_vals = np.array([])
all_cal_pos_vals = np.array([])
#Loop through each run
for i, run_num in enumerate(runs):
    print "Loading calibrated waveforms: Run ",run_num
    #Loop through each asic
    for Nasic in range(1):
        #Loop through each channel
        for Nchannel in range(14,15):

            #Load samples
            infile = "run_files/sampleFileAllBlocks_run"+str(run_num)+"ASIC"+str(Nasic)+"CH"+str(Nchannel)+".npz"
            data = np.load(infile)
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

            #Correct samples with pedestal subtraction in mV.
            corr_samples = samples[:,start:stop]-np.percentile(samples[:,start:stop],50.,axis=0)
            if run_num<317000:
                all_amp_vals = np.append(all_amp_vals, np.amax(corr_samples,axis=1))
                all_pos_vals = np.append(all_pos_vals, np.argmax(corr_samples,axis=1))
                all_charge_vals = np.append(all_charge_vals, np.sum(corr_samples[:,:],axis=1))
            else:
                all_cal_amp_vals = np.append(all_cal_amp_vals, np.amax(corr_samples,axis=1))
                all_cal_pos_vals = np.append(all_cal_pos_vals, np.argmax(corr_samples,axis=1))
                all_cal_charge_vals = np.append(all_cal_charge_vals, np.sum(corr_samples[:,:],axis=1))


data = all_cal_amp_vals
cut_off = np.percentile(all_cal_amp_vals,99.87)
total_counts = np.sum(all_amp_vals>=cut_off)
print total_counts
print len(all_amp_vals)
print cut_off

# minimize the negative log-Likelihood
result = minimize(negLogLikelihood, 
                  x0=np.ones(1),     
                  args=(data,),   
                  method='Powell',  
                  )
print(result)
# plot poisson-deviation with fitted parameter
x_plot = np.linspace(0, 20, 1000)
plt.figure()
plt.hist(data, bins=np.arange(15) - 0.5, normed=True)
plt.plot(x_plot, poisson(x_plot, result.x), 'r-', lw=2)
plt.show()

up_lim=50.
plt.figure()
# the bins should be of integer width, because poisson is an integer distribution
entries, bin_edges, patches = plt.hist(all_cal_amp_vals, np.arange(0,up_lim,1.0), normed=True,alpha=0.7,label='HV off')
centries, cbin_edges, cpatches = plt.hist(all_amp_vals, np.arange(0,up_lim,1.0), normed=True,alpha=0.7, label='HV on')

plt.axvline(np.percentile(all_cal_amp_vals,97.72),color='k',lw=0.9,linestyle='dotted', label='97.7th Perc.')
plt.axvline(np.percentile(all_cal_amp_vals,99.87),color='k',lw=0.9,linestyle='dashed',label='99.9th Perc.')
plt.xlabel('Max Amplitude (mV)',fontsize=20)
plt.ylabel('Counts',fontsize=20)
plt.legend()
plt.show()

cut_off = np.percentile(all_cal_amp_vals,99.87)
cut_off2 = np.percentile(all_cal_amp_vals,97.72)
total_counts = np.sum(all_amp_vals>=cut_off2)
print total_counts
print len(all_amp_vals)
print '3 sigma ',cut_off
print '2 sigma ', np.percentile(all_cal_amp_vals,97.72), ' , ', np.percentile(all_cal_amp_vals,84.13)
print '1 sigma ', np.percentile(all_cal_amp_vals,84.13)

print np.sum(all_cal_charge_vals)
print np.sum(all_charge_vals)
print (np.sum(all_charge_vals)-np.sum(all_cal_charge_vals))/(delta_t*1.e-9*47.)
print np.percentile(all_cal_charge_vals,50.),'   ',np.mean(all_cal_charge_vals)
print np.percentile(all_charge_vals,50.),'   ',np.mean(all_charge_vals)

cal_shift = np.percentile(all_cal_charge_vals,50.)
all_shift = np.percentile(all_charge_vals,50.)

print 'max ', np.amax(all_charge_vals/(47.))
print 'min ',np.amin(all_charge_vals/(47.))
mean_cal_charge = np.mean(all_cal_charge_vals/(47.))
mean_charge = np.mean(all_charge_vals/(47.))
dark_rate  = (mean_charge-mean_cal_charge)/(128.e-9)
print (mean_charge-mean_cal_charge)*47.
print 'dark charge: ',dark_rate

plt.figure()
centries, cbin_edges, cpatches = plt.hist(all_cal_charge_vals/(47.),np.arange(-35,85,1.0), normed=True,cumulative=False,alpha=0.7,label='HV off')
entries, bin_edges, patches = plt.hist(all_charge_vals/(47.), np.arange(-35,85,1.0), normed=True,cumulative=False,alpha=0.7,label='HV on')
plt.axvline(mean_cal_charge,color='k',lw=0.9,linestyle='dashed',label='Mean HV off')
plt.axvline(mean_charge,color='k',lw=0.9,linestyle='dotted',label='Mean HV on')
plt.xlim([-20,30])
plt.xlabel('PE',fontsize=20)
plt.ylabel('Counts',fontsize=20)
plt.legend()
plt.show()
