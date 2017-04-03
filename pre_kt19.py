import h5py
import glob
import os
import datetime
import numpy as np

def PLT_KT19(statements, testMode=True):
    #{{{
    init, time_sec0 = statements
    dtime0   = init.date + datetime.timedelta(seconds=time_sec0)
    dtime0_s = dtime0.strftime('%Y-%m-%d_%H:%M:%S')

    time_sec, zenT, nadT = GDATA_KT19(init.fname_kt19)
    fig = plt.figure(figsize=(12, 5))
    ax1 = fig.add_subplot(111)
    ax1.scatter(time_sec/3600.0, nadT, c='b', s=2)
    ax1.scatter(time_sec/3600.0, zenT, c='r', s=2)
    ax1.set_xlim([17.83, 23.83])
    ax1.set_ylim([-20, 5])
    plt.show()
    exit()

    index0 = np.argmin(np.abs(time_sec-time_sec0))
    if abs(time_sec[index0]-time_sec0)>0.1:
        print 'Error [PLT_KT19]: %s is not avaiable.' % dtime0_s
        return

    logic = (time_sec >= time_sec0-1800.0) & (time_sec <= time_sec0+1800.0)
    xx    = time_sec[logic]
    yy_z  = zenT[logic]
    yy_n  = nadT[logic]

    rcParams['font.size'] = 22
    fig = plt.figure(figsize=(12, 3))
    ax1 = fig.add_subplot(111)
    ax1.xaxis.set_major_locator(FixedLocator(time_sec0+np.arange(-1800.0, 1801.0, 360.0)))
    ax1.set_xticklabels(['UTC-0.5h', '', '', '', '', 'UTC', '', '', '', '', 'UTC+0.5h'])
    ax1.set_xlim([time_sec0-1800.000001, time_sec0+1800.000001])
    ax1.scatter(xx, yy_n, c='b', edgecolor='none', alpha=0.8, label='Nadir' , s=2)
    ax1.scatter(xx, yy_z, c='r', edgecolor='none', alpha=0.8, label='Zenith', s=2)
    ax1.axvline(time_sec0, linewidth=1.0, linestyle='--', color='k')

    plt.legend(fontsize=19, loc='upper left', fancybox=False, framealpha=0.6)
    ax1.set_ylabel('Temperature [$\mathrm{^\circ C}$]')

    if testMode:
        plt.show()
        exit()
    else:
        plt.savefig('%s/ssfr_%.7d_%s.png' % (init.fdir_ssfr_graph_tmp, index, time_stamp))
        plt.close(fig)
    #}}}

def GDATA_KT19(fname, skip_header=35):
    #{{{
    data     = np.genfromtxt(fname, delimiter=',', skip_header=skip_header)
    time_sec = data[:, 0]
    zenT     = data[:, 1]
    nadT     = data[:, 2]
    zenT[zenT<-273.15] = np.nan
    nadT[nadT<-273.15] = np.nan
    return time_sec, zenT, nadT
    #}}}

if __name__ == '__main__':

    import matplotlib as mpl
    #mpl.use('Agg')
    import matplotlib.pyplot as plt
    from mpl_toolkits.basemap import Basemap
    from matplotlib import rcParams
    from matplotlib.ticker import FixedLocator

    from pre_vid import ANIM_INIT
    #date = datetime.datetime(2014, 9, 4)
    #date = datetime.datetime(2014, 9, 7)
    #date = datetime.datetime(2014, 9, 9)
    date = datetime.datetime(2014, 9, 16)
    #date = datetime.datetime(2014, 9, 17)
    #date = datetime.datetime(2014, 9, 19)

    init = ANIM_INIT(date)
    init.fname_kt19 = '%s/temp.txt' % init.fdir_kt19_data
    statements = [init, 20.0*3600.0]
    PLT_KT19(statements, testMode=True)
    #tmhr, zenT, nadT = GDATA_KT19(init.fname_kt19)
