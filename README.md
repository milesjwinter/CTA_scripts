# CTA scripts
Various analysis scripts for CTA

## Calibrate_Waveforms.py
Perform pedestal subtraction on waveforms written out with write_events_faster.py. Requires an existing hd5f database with pedestal waveform values, which can be generated with Make_Ped_Waveforms.py. Outputs a compressed numpy arrays (.npz) for each run. 
## LEDPulseWFs.py
Updated version of LEDPulseWFs.py for use in the dark box w/ testerboard.
## LEDPulseWFs_rsync_standalone.py    
Updated version of LEDPulseWFs.py for use in the dark box w/ adapter board.
## Make_Ped_Waveforms.py     
Calculates individual pedestal waveforms for all 4 asics, all 16 channels, all 512 blocks,and all 32 phases and generates an hd5f database that can be passed to Calibrate_Waveforms.py. Requires input calibration data written out with write_events_faster.py. 
## Pedestal_Charge_Spec.py   
Calculates the charge spectrum for run(s) calibrated with Calibrate_Waveforms.py. Outputs a compress numpy array (.npz) for each run. The position and length of the integration region need to be set on a case-by-case basis. 
## Plot_charge_spectrum.py      
Generates plots for the charge spectrum data calculated with Pedestal_Charge_Spec.py. Analysis cuts need to be set on a case-by-case basis.
## dark_count_rate.py
Calculates the dark count rate by comparing the maximum amplitude spectrums of calibration data with HV on/off. 
## justDataTaking.py
Updated version of justDataTaking.py for use in the dark box w/ testerboard.
## justDataTaking_rsync_standalone.py
Updated version of justDataTaking.py for use in the dark box w/ adapter board.
## write_average_faster.py
Calculate average pedestal waveforms directly from .fits files. Outputs a compressed numpy arrays (.npz) for each run. 
## write_events_faster.py
write out individual waveform data directly from .fits files. Outputs a compressed numpy arrays (.npz) for each run.
         

