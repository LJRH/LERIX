# Python script for XRStools written by C.Sahle and adapted for XRS scans
# Adapted Script to run LERIX followed by XRStools
import os
import matplotlib
matplotlib.use('Qt4Agg')
from matplotlib import pyplot as plt
from matplotlib.widgets import Cursor, Slider, Button
import numpy as np
import LERIX
from XRStools import xrs_read, roifinder_and_gui, xrs_extraction

#######################################################################
# USER INPUTS - ALWAYS CHANGE PATH & SAMPLE NAME
#######################################################################
sample_name = 'DC1-MI' #name of the sample for saving
path = 'D:/DATA/XRS/20ID-APS/Final/Nov2017/Soil-DC1-MI/' #folder containing the LERIX files
#path = '/Users/lukehiggins/OneDrive - University of Leeds/_HIGGINS-PhD_/__XAS__/__RAW-DATA__/20ID-APS/Other/NaBicarb'
H5=False #boolean, write a H5 file containing the data?
nixs_name='nixs'
wide_name='wide'
elastic_name='elastic' #chosen name for elastic scans
scan_numbers='all' #'all' or a list of the scans [0,1,2]
########################################################################################################
noodle = LERIX.Lerix()
noodle.load_scan(path,nixs_name,wide_name,elastic_name,scan_numbers,H5,path,sample_name)
noodle.plot_data() #chooses which analyzers we want to put into XRStools by saving a csv file

# set scaling - used when a wide scan is implemented, but LERIX can't do this yet
# scaling = np.zeros(72)
# scaling[lowq] = 4.3
# scaling[medq] = 4.3
# scaling[highq]= 4.4

# """Begin the Carbon Extraction Here - to run uncomment the first line of Step 1 and do the two
# following lines manually. Then Once you have a good fit to the edge using the Hartree Fock method"""
# noodle_ex = xrs_extraction.edge_extraction(noodle,['C'],[1.0],{'C':['K']})
# noodle_ex.analyzerAverage(noodle.chosen_analyzers, errorweighing=False) #uncomment!
# noodle_ex.LERIX_HFextraction('C','K',[260.0,280.0],[295.0,400.0],weights=[2,1],HFcore_shift=8.0,scaling=1.79)
#
# noodle_ex.removeCorePearsonAv('C','K',[278.0,283.0],[295.0,400.0],weights=[2,1],HFcore_shift=8.0,scaling=3)
#
# #Saving - need to create a directory called 'fit_data'
# directory = path+'extracted_data/'
# if not os.path.exists(directory):
#     os.makedirs(directory)
# noodle_ex.save_average_Sqw(directory+sample_name+'_'+str(noodle.chosen_analyzers)+'.dat', emin=0.0, emax=395.0, normrange=[280.,400.])
