import h5py
import glob
import os
import datetime
import numpy as np
from scipy.io import readsav

def GDATA_SSFR(fname, varnames):
    #{{{
    #print '+'*50
    #print 'Reading SSFR data...'
    f = readsav(fname)
    datasets = []
    for varname in varnames:
        try:
            datasets.append(f[varname][...])
        except KeyError:
            print('Error: Wrong variable name! (GDATA_SSFR in pre_ssfr.py)')
            #print '-'*50
            exit()
    #print 'Reading complete!'
    #print '-'*50
    return datasets
    #}}}

def TIME_STAMP_SSFR(delta_hour, dtime0=datetime.datetime(2014, 9, 19, 0, 0, 0)):
    #{{{
    dtime = dtime0 + datetime.timedelta(hours=delta_hour)
    time_stamp = dtime.strftime('%Y-%m-%d-%H-%M-%S')
    return time_stamp
    #}}}

def TMHR2DATETIME(delta_hour, dtime0=datetime.datetime(2014, 9, 19, 0, 0, 0)):
    #{{{
    dtime = dtime0 + datetime.timedelta(hours=delta_hour)
    return dtime
    #}}}

def GDATA_SSFR_NAT(fname, wvl=500.0):
    #{{{
    f = readsav(fname)
    time_sec = f.utl*3600.0

    index_z = np.argmin(np.abs(f.wlz-wvl))
    index_n = np.argmin(np.abs(f.wln-wvl))
    spec_zen = f.spc_zen[index_z, :] * f.crz
    spec_nad = f.spc_nad[index_n, :]

    return time_sec, spec_zen, spec_nad
    #}}}

def GDATA_SSFR_SPEC(fname, time_sec0):
    #{{{
    f = readsav(fname)
    time = f.utl*3600.0
    index = np.argmin(np.abs(time-time_sec0))
    time_sec = time[index]
    spec_zen = f.spc_zen[:, index] * f.crz[index]
    spec_nad = f.spc_nad[:, index]
    return time_sec, f.wlz, spec_zen, f.wln, spec_nad
    #}}}

if __name__ == '__main__':
    print('I am pre_ssfr.py.')
