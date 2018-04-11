# Python script for XRStools written by C.Sahle and adapted for XRS scans
# taken in September for ID20 beamrun with T.Moorsom + B.Mishra
import os
import matplotlib
matplotlib.use('Qt4Agg')
from matplotlib import pyplot as plt
import numpy as np
from XRStools import xrs_read, roifinder_and_gui, xrs_extraction

#######################################################################
#Define the pixels for different q regions
#######################################################################
lowq = range(24)
#lowq.extend(range(36,60))
medq = range(24,48)
highq = range(60,72)
ALLq = range(72)
#Define regions for each detector from list of ROIS, can be used to
#plot individual detector data.
VD = range(12)
VU = range(12,24)
VB = range(24,36)
HR = range(36,48)
HL = range(48,60)
HB = range(60,72)

#######################################################################
# USER INPUTS
#######################################################################
sample_name = 'HTC250_run1' #name of the sample for saving
QVALUE = range(36)             #'lowq','medq' or 'highq'
compensation_elastic = 21   #first elastic scan for compensating for detector drift
elastic_scans = [21,23,25]     #NIXS scans
NIXS_scans = [22,24,26]        #elastic scans
SPECfname='hydra2'          #The SPEC file
EDFprefix='/edf2/'          #The edf path
path = '/Users/lukehiggins/OneDrive - University of Leeds/_HIGGINS-PhD_/__XAS__/__RAW-DATA__/ID20-ESRF/'
#path = 'D:/OneDrive for Business/_HIGGINS-PhD_/__XAS__/__RAW-DATA__/ID20-ESRF/'
########################################################################################################
#sanity check


# Hydrochar
#Define Hydra object
noodle = xrs_read.Hydra(path, SPECfname,EDFprefix)

# define ROIs from a saved H5 ROI file.
roifinder = roifinder_and_gui.roi_finder()
roifinder.roi_obj.loadH5(path+'rois/'+sample_name+'_zoom.H5')
noodle.set_roiObj(roifinder.roi_obj)

# set scaling - not used at the moment
scaling = np.zeros(72)
scaling[lowq] = 4.3
scaling[medq] = 4.3
scaling[highq]= 4.4

#load the scans from the ROIs
#method can be sum, row or pixel - What is the difference?
noodle.get_compensation_factor(compensation_elastic, method='sum')
noodle.load_scan(elastic_scans, method='sum', direct=True, scan_type='elastic')
noodle.load_scan(NIXS_scans, method='sum', direct=True, scan_type='CK')
noodle.get_spectrum_new(method='sum', include_elastic=False)

#plotting the Results
plt.figure() #clear the figure
# plt.plot(noodle.eloss, np.sum(noodle.signals[:,lowq],axis=1),label='Low q')
# plt.plot(noodle.eloss, np.sum(noodle.signals[:,medq],axis=1), label = 'Med q')
# plt.plot(noodle.eloss, np.sum(noodle.signals[:,highq],axis=1), label = 'High q')
# plt.plot(noodle.eloss, np.sum(noodle.signals[:,QVALUE],axis=1),label='Chosen ROIs')
# plt.plot(noodle.eloss, np.sum(noodle.signals[:,range(36)],axis=1),label='36 ROIs')
# plt.plot(noodle.eloss, np.sum(noodle.signals[:,range(48)],axis=1),label='48 ROIs')
# plt.plot(noodle.eloss, np.sum(noodle.signals[:,VD],axis=1),label='VD')
# plt.plot(noodle.eloss, np.sum(noodle.signals[:,VU],axis=1), label = 'VU')
# plt.plot(noodle.eloss, np.sum(noodle.signals[:,VB],axis=1), label = 'VB')
# plt.plot(noodle.eloss, np.sum(noodle.signals[:,HR],axis=1),label='HR')
# plt.plot(noodle.eloss, np.sum(noodle.signals[:,HL],axis=1), label = 'HL')
# plt.plot(noodle.eloss, np.sum(noodle.signals[:,HB],axis=1), label = 'HB')
# plt.plot(noodle.eloss, np.sum(noodle.signals[:,range(72)],axis=1),label='Hydrochar')
plt.show() #launch the figure
plt.legend() #shows the legend


"""Begin the Carbon Extraction Here - to run uncomment the first line of Step 1 and do the two
following lines manually. Then Once you have a good fit to the edge using the Hartree Fock method, do
step 2. Do step one for each q region and decide whether they can be summed up before doing step 2! """
## Extraction
noodle.get_tths(rvd=-39.0, rvu=79.0, rvb=120.88, rhr=30.5, rhl=41.0, rhb=116.0, order=[0, 1, 2, 3, 4, 5])
noodle_ex = xrs_extraction.edge_extraction(noodle,['C'],[1.0],{'C':['K']})

# STEP 1: C edge Extraction run the bottom two rows of code out of the macro.
#noodle_ex.analyzerAverage(QVALUE, errorweighing=False) #uncomment!
#noodle_ex.removeCorePearsonAv('C','K',[75.0,278.0],[295.0,310.0],weights=[2,1],HFcore_shift=-5.0, guess= [-1.07743447e+03, 8.42895443e+02, 4.99035465e+01, 3193e+01, -3.80090286e-07, 2.73774370e-03, 5.11920401e+03],scaling=1.32)
#noodle_ex.save_average_Sqw(path+'fit_data/'+sample_name+'_lq.dat', emin=00.0, emax=395.0, normrange=[280.,320.])

# STEP 2: C edge averaging of Q's
# normrange=[280.,310.]
# assert type(normrange) is list and len(normrange) is 2, "normrange has to be a list of length two!"
#
# #Sum the q's together
# noodle_ex.analyzerAverage(QVALUE, errorweighing=False)
#
# #copy your values from step 1 into here
# noodle_ex.removeCorePearsonAv('C','K',[265,283],[309.5,310.9],weights=[2,1],HFcore_shift=8.0,
# guess= [-1.07743447e+03, 8.42895443e+02, 4.99035465e+01, 3193e+01, -3.80090286e-07, 2.73774370e-03, 5.11920401e+03],
# scaling=1.53)
#
# data_cs = np.zeros((len(noodle_ex.eloss),3))
# data_cs[:,0] = noodle_ex.eloss
# data_cs[:,1] = noodle_ex.sqwav
# data_cs[:,2] = noodle_ex.sqwaverr
# inds = np.where(np.logical_and(data_cs[:,0]>=normrange[0],data_cs[:,0]<=normrange[1]))[0]
# norm = np.trapz(data_cs[inds,1],data_cs[inds,0])
# data_cs[:,1] /= norm
# data_cs[:,2] /= norm
#
# #smoothing - avoid if possible
# def smooth(y, box_pts):
#     box = np.ones(box_pts)/box_pts
#     y_smooth = np.convolve(y, box, mode='same')
#     return y_smooth
# merged_data_smooth = smooth(data_cs[:,1],3)
#
# #plot the data
# plt.clf()
# plt.plot(data_cs[:,0],data_cs[:,1],label='merged-cs')
# plt.show()
# plt.legend()
#
# #Save the scan
# noodle_ex.save_average_Sqw(path+'fit_data/merged/'+sample_name+'.dat', emin=275, emax=310, normrange=[275.,310.])
# print('Finished the Merge')
