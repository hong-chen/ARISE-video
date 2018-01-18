import datetime
import glob
import os
import numpy as np
from scipy.io import readsav
from pre_trk import GDATA_TRK
from pre_kt19 import GDATA_KT19
from pre_ssfr import GDATA_SSFR_NAT, GDATA_SSFR_SPEC

def PLT_JOIN(statements, testMode=False):

    init, time_sec0 = statements

    dtime0    = init.date+datetime.timedelta(seconds=time_sec0)
    dtime0_s  = dtime0.strftime('%Y-%m-%d_%H:%M:%S')

    rcParams['font.size'] = 12
    fig = plt.figure(figsize=(11, 3.5))
    gs  = gridspec.GridSpec(5, 9)
    ax1 = plt.subplot(gs[1:5, 0:3])
    ax2 = plt.subplot(gs[1:5, 3:6])
    ax3 = plt.subplot(gs[1:5, 6:9])

    # flight track
    fnames      = sorted(glob.glob('%s/*%s*.png' % (init.fdir_trk_graph, dtime0_s)))
    NFile       = len(fnames)
    ax1.axis('off')
    if NFile > 0:
        fname = fnames[0]
    else:
        fname = None

    if fname != None:
        image_data  = mpimg.imread(fname)
        ax1.imshow(image_data)
        ax1.set_title('Flight Track', fontsize=14)

    ax1.axis('off')

    # forward camera
    fnames_good = sorted(glob.glob('%s/*%s*_good.png' % (init.fdir_fcam_graph, dtime0_s)))
    Ngood       = len(fnames_good)
    fnames_bad  = sorted(glob.glob('%s/*%s*_bad.png' % (init.fdir_fcam_graph, dtime0_s)))
    Nbad        = len(fnames_bad)

    if Ngood > 0:
        fname = fnames_good[0]
        ax2.set_title('Forward Camera', fontsize=14)
    elif Nbad > 0:
        fname = fnames_bad[0]
        ax2.set_title('Forward Camera', fontsize=14, color='dimgray')
    else:
        fname = None

    if fname != None:
        image_data  = mpimg.imread(fname)
        ax2.imshow(image_data)

    ax2.axis('off')

    # nadir camera
    fnames_good = sorted(glob.glob('%s/*%s*_good.png' % (init.fdir_ncam_graph, dtime0_s)))
    Ngood       = len(fnames_good)
    fnames_bad  = sorted(glob.glob('%s/*%s*_bad.png' % (init.fdir_ncam_graph, dtime0_s)))
    Nbad        = len(fnames_bad)

    if Ngood > 0:
        fname = fnames_good[0]
        ax3.set_title('Nadir Camera', fontsize=14)
    elif Nbad > 0:
        fname = fnames_bad[0]
        ax3.set_title('Nadir Camera', fontsize=14, color='dimgray')
    else:
        fname = None

    if fname != None:
        image_data  = mpimg.imread(fname)
        if init.date_s == '2014-09-04':
            ax3.imshow(image_data, origin='lower')
        else:
            ax3.imshow(image_data)

    ax3.axis('off')

    if False:
        # ssfr time series
        time_sec, spec_zen, spec_nad = GDATA_SSFR_NAT(init.fname_ssfr)
        logic = (time_sec >= time_sec0-720.0) & (time_sec <= time_sec0+720.0)
        xx    = time_sec[logic]
        yy_z  = spec_zen[logic]
        yy_n  = spec_nad[logic]
        ax4.xaxis.set_major_locator(FixedLocator(time_sec0+np.arange(-720.0, 721.0, 180.0)))
        ax4.set_xticklabels(['', '', '-0.1h', '', 'UTC', '', '+0.1h', '', ''])
        ax4.set_xlim([time_sec0-720.000001, time_sec0+720.000001])
        ax4.set_ylim([0, 1.2])
        ax4.scatter(xx, yy_n, c='b', edgecolor='none', alpha=0.8, label='$\mathrm{F\\uparrow}$'  , s=5)
        ax4.scatter(xx, yy_z, c='r', edgecolor='none', alpha=0.8, label='$\mathrm{F\downarrow}$', s=5)
        ax4.legend(fontsize=10, loc='upper right', framealpha=0.5, markerscale=2)
        ax4.axvline(time_sec0, linewidth=1.0, linestyle=':', color='k')
        ax4.set_ylabel('Irradiance [$\mathrm{W m^{-2} nm^{-1}}$]', fontsize=12)
        ax4.set_title('SSFR (0.5$\mathrm{\mu m}$)', fontsize=14)

        # ssfr spectra
        time_sec, wvl_zen, spec_zen, wvl_nad, spec_nad = GDATA_SSFR_SPEC(init.fname_ssfr, time_sec0)
        ax8.xaxis.set_major_locator(FixedLocator(np.arange(200, 2201, 400)))
        ax8.set_xlim([200, 2200])
        ax8.set_ylim([0, 1.2])
        if np.abs(time_sec-time_sec0)<2.0:
            ax8.scatter(wvl_nad, spec_nad, c='b', edgecolor='none', alpha=0.8, label='$\mathrm{F\\uparrow}$'  , s=5)
            ax8.scatter(wvl_zen, spec_zen, c='r', edgecolor='none', alpha=0.8, label='$\mathrm{F\downarrow}$', s=5)
            ax8.legend(fontsize=10, loc='upper right', framealpha=0.5, markerscale=2)
        ax8.set_xlabel('Wavelength [nm]', fontsize=12)
        #ax8.set_ylabel('Irradiance [$\mathrm{W m^{-2} nm^{-1}}$]', fontsize=12)
        ax8.yaxis.set_ticklabels([])
        ax8.set_title('SSFR Spectra', fontsize=14)

        # kt-19 time series
        time_sec, zenT, nadT = GDATA_KT19(init.fname_kt19)
        logic_n = (time_sec >= time_sec0-720.0) & (time_sec <= time_sec0+720.0)
        xx_n    = time_sec[logic_n]
        yy_n    = nadT[logic_n]

        logic_z = (time_sec >= time_sec0-720.0) & (time_sec <= time_sec0+720.0) & (zenT>-20.0)
        xx_z    = time_sec[logic_z]
        yy_z    = zenT[logic_z]

        ax6.xaxis.set_major_locator(FixedLocator(time_sec0+np.arange(-720.0, 721.0, 180.0)))
        ax6.set_xticklabels(['', '', '-0.1h', '', 'UTC', '', '+0.1h', '', ''])
        ax6.set_xlim([time_sec0-720.000001, time_sec0+720.000001])
        ax6.set_ylim([-20, 5])
        ax6.scatter(xx_n, yy_n, c='b', edgecolor='none', alpha=0.8, label='Nadir' , s=2)
        if logic_z.sum() > 0:
            ax6.scatter(xx_z, yy_z, c='r', edgecolor='none', alpha=0.8, label='Zenith', s=2)
        ax6.legend(fontsize=10, loc='upper right', framealpha=0.5, markerscale=3)
        ax6.axvline(time_sec0, linewidth=1.0, linestyle=':', color='k')
        ax6.set_ylabel('Temperature [$\mathrm{^\circ C}$]', fontsize=12, rotation=270, labelpad=16)
        ax6.yaxis.tick_right()
        ax6.yaxis.set_ticks_position('both')
        ax6.yaxis.set_label_position('right')
        ax6.set_title('KT-19', fontsize=14)

    fig.suptitle("%s UTC" % (dtime0.strftime('%Y-%m-%d %H:%M:%S')), fontsize=20, y=0.96)

    time_trk, lon_trk, lat_trk, alt_trk = GDATA_TRK(init.fname_trk)
    index = np.argmin(np.abs(time_trk - time_sec0))
    if time_trk[index]-time_sec0<1.0:
        lon_trk0 = lon_trk[index]
        lat_trk0 = lat_trk[index]
        alt_trk0 = alt_trk[index]

        fig.text(0.5, 0.84, '(%.4fh, %7.2f$^\circ$, %5.2f$^\circ$, %4dm)' % (time_sec0/3600.0, lon_trk0, lat_trk0, alt_trk0), fontsize=16, ha='center')

    fname_graph = '%s/join_%s.png' % (init.fdir_join_graph, dtime0_s)
    if testMode:
        plt.savefig('test.png', bbox_inches=None)
        plt.show()
        exit()
    plt.savefig(fname_graph, bbox_inches=None)
    print('%s is complete.' % fname_graph)
    plt.close(fig)

def PLT_JOIN_BACKUP(statements, testMode=False):

    init, time_sec0 = statements

    dtime0    = init.date+datetime.timedelta(seconds=time_sec0)
    dtime0_s  = dtime0.strftime('%Y-%m-%d_%H:%M:%S')

    rcParams['font.size'] = 12
    fig = plt.figure(figsize=(12, 7.5))
    gs  = gridspec.GridSpec(6, 9)
    ax1 = plt.subplot(gs[0:3, 0:3])
    ax2 = plt.subplot(gs[0:3, 3:6])
    ax3 = plt.subplot(gs[0:3, 6:9])
    ax4 = plt.subplot(gs[3:6, 0:3])
    ax6 = plt.subplot(gs[3:6, 6:9])
    ax8 = plt.subplot(gs[3:6, 3:6])

    # flight track
    fnames      = sorted(glob.glob('%s/*%s*.png' % (init.fdir_trk_graph, dtime0_s)))
    NFile       = len(fnames)
    ax1.axis('off')
    if NFile > 0:
        fname = fnames[0]
    else:
        fname = None

    if fname != None:
        image_data  = mpimg.imread(fname)
        ax1.imshow(image_data)
        ax1.set_title('Flight Track', fontsize=14)

    ax1.axis('off')

    # forward camera
    fnames_good = sorted(glob.glob('%s/*%s*_good.png' % (init.fdir_fcam_graph, dtime0_s)))
    Ngood       = len(fnames_good)
    fnames_bad  = sorted(glob.glob('%s/*%s*_bad.png' % (init.fdir_fcam_graph, dtime0_s)))
    Nbad        = len(fnames_bad)

    if Ngood > 0:
        fname = fnames_good[0]
        ax2.set_title('Forward Camera', fontsize=14)
    elif Nbad > 0:
        fname = fnames_bad[0]
        ax2.set_title('Forward Camera', fontsize=14, color='dimgray')
    else:
        fname = None

    if fname != None:
        image_data  = mpimg.imread(fname)
        ax2.imshow(image_data)

    ax2.axis('off')

    # nadir camera
    fnames_good = sorted(glob.glob('%s/*%s*_good.png' % (init.fdir_ncam_graph, dtime0_s)))
    Ngood       = len(fnames_good)
    fnames_bad  = sorted(glob.glob('%s/*%s*_bad.png' % (init.fdir_ncam_graph, dtime0_s)))
    Nbad        = len(fnames_bad)

    if Ngood > 0:
        fname = fnames_good[0]
        ax3.set_title('Nadir Camera', fontsize=14)
    elif Nbad > 0:
        fname = fnames_bad[0]
        ax3.set_title('Nadir Camera', fontsize=14, color='dimgray')
    else:
        fname = None

    if fname != None:
        image_data  = mpimg.imread(fname)
        if init.date_s == '2014-09-04':
            ax3.imshow(image_data, origin='lower')
        else:
            ax3.imshow(image_data)

    ax3.axis('off')

    # ssfr time series
    time_sec, spec_zen, spec_nad = GDATA_SSFR_NAT(init.fname_ssfr)
    logic = (time_sec >= time_sec0-720.0) & (time_sec <= time_sec0+720.0)
    xx    = time_sec[logic]
    yy_z  = spec_zen[logic]
    yy_n  = spec_nad[logic]
    ax4.xaxis.set_major_locator(FixedLocator(time_sec0+np.arange(-720.0, 721.0, 180.0)))
    ax4.set_xticklabels(['', '', '-0.1h', '', 'UTC', '', '+0.1h', '', ''])
    ax4.set_xlim([time_sec0-720.000001, time_sec0+720.000001])
    ax4.set_ylim([0, 1.2])
    ax4.scatter(xx, yy_n, c='b', edgecolor='none', alpha=0.8, label='$\mathrm{F\\uparrow}$'  , s=5)
    ax4.scatter(xx, yy_z, c='r', edgecolor='none', alpha=0.8, label='$\mathrm{F\downarrow}$', s=5)
    ax4.legend(fontsize=10, loc='upper right', framealpha=0.5, markerscale=2)
    ax4.axvline(time_sec0, linewidth=1.0, linestyle=':', color='k')
    ax4.set_ylabel('Irradiance [$\mathrm{W m^{-2} nm^{-1}}$]', fontsize=12)
    ax4.set_title('SSFR (0.5$\mathrm{\mu m}$)', fontsize=14)
    #}}}

    # ssfr spectra
    time_sec, wvl_zen, spec_zen, wvl_nad, spec_nad = GDATA_SSFR_SPEC(init.fname_ssfr, time_sec0)
    ax8.xaxis.set_major_locator(FixedLocator(np.arange(200, 2201, 400)))
    ax8.set_xlim([200, 2200])
    ax8.set_ylim([0, 1.2])
    if np.abs(time_sec-time_sec0)<2.0:
        ax8.scatter(wvl_nad, spec_nad, c='b', edgecolor='none', alpha=0.8, label='$\mathrm{F\\uparrow}$'  , s=5)
        ax8.scatter(wvl_zen, spec_zen, c='r', edgecolor='none', alpha=0.8, label='$\mathrm{F\downarrow}$', s=5)
        ax8.legend(fontsize=10, loc='upper right', framealpha=0.5, markerscale=2)
    ax8.set_xlabel('Wavelength [nm]', fontsize=12)
    #ax8.set_ylabel('Irradiance [$\mathrm{W m^{-2} nm^{-1}}$]', fontsize=12)
    ax8.yaxis.set_ticklabels([])
    ax8.set_title('SSFR Spectra', fontsize=14)
    #}}}

    # kt-19 time series
    time_sec, zenT, nadT = GDATA_KT19(init.fname_kt19)
    logic_n = (time_sec >= time_sec0-720.0) & (time_sec <= time_sec0+720.0)
    xx_n    = time_sec[logic_n]
    yy_n    = nadT[logic_n]

    logic_z = (time_sec >= time_sec0-720.0) & (time_sec <= time_sec0+720.0) & (zenT>-20.0)
    xx_z    = time_sec[logic_z]
    yy_z    = zenT[logic_z]

    ax6.xaxis.set_major_locator(FixedLocator(time_sec0+np.arange(-720.0, 721.0, 180.0)))
    ax6.set_xticklabels(['', '', '-0.1h', '', 'UTC', '', '+0.1h', '', ''])
    ax6.set_xlim([time_sec0-720.000001, time_sec0+720.000001])
    ax6.set_ylim([-20, 5])
    ax6.scatter(xx_n, yy_n, c='b', edgecolor='none', alpha=0.8, label='Nadir' , s=2)
    if logic_z.sum() > 0:
        ax6.scatter(xx_z, yy_z, c='r', edgecolor='none', alpha=0.8, label='Zenith', s=2)
    ax6.legend(fontsize=10, loc='upper right', framealpha=0.5, markerscale=3)
    ax6.axvline(time_sec0, linewidth=1.0, linestyle=':', color='k')
    ax6.set_ylabel('Temperature [$\mathrm{^\circ C}$]', fontsize=12, rotation=270, labelpad=16)
    ax6.yaxis.tick_right()
    ax6.yaxis.set_ticks_position('both')
    ax6.yaxis.set_label_position('right')
    ax6.set_title('KT-19', fontsize=14)

    fig.suptitle("%s UTC" % (dtime0.strftime('%Y-%m-%d %H:%M:%S')), fontsize=20, y=0.96)

    time_trk, lon_trk, lat_trk, alt_trk = GDATA_TRK(init.fname_trk)
    index = np.argmin(np.abs(time_trk - time_sec0))
    if time_trk[index]-time_sec0<1.0:
        lon_trk0 = lon_trk[index]
        lat_trk0 = lat_trk[index]
        alt_trk0 = alt_trk[index]

        fig.text(0.5, 0.90, '(%.4fh, %7.2f$^\circ$, %5.2f$^\circ$, %4dm)' % (time_sec0/3600.0, lon_trk0, lat_trk0, alt_trk0), fontsize=16, ha='center')

    if testMode:
        plt.show()
        exit()
    fname_graph = '%s/join_%s.png' % (init.fdir_join_graph, dtime0_s)
    plt.savefig(fname_graph)
    print('%s is complete.' % fname_graph)
    plt.close(fig)

def PLT_JOIN_V7(statements, testMode=False):

    init, time_sec0 = statements

    dtime0    = init.date+datetime.timedelta(seconds=time_sec0)
    dtime0_s  = dtime0.strftime('%Y-%m-%d_%H:%M:%S')

    rcParams['font.size'] = 12
    fig = plt.figure(figsize=(12, 7.5))
    gs  = gridspec.GridSpec(6, 9)
    ax1 = plt.subplot(gs[0:3, 0:3])
    ax2 = plt.subplot(gs[0:3, 3:6])
    ax3 = plt.subplot(gs[0:3, 6:9])
    ax4 = plt.subplot(gs[3:6, 0:3])
    ax6 = plt.subplot(gs[3:6, 6:9])
    ax8 = plt.subplot(gs[3:6, 3:6])

    # flight track
    fnames      = sorted(glob.glob('%s/*%s*.png' % (init.fdir_trk_graph, dtime0_s)))
    NFile       = len(fnames)
    ax1.axis('off')
    if NFile > 0:
        fname = fnames[0]
    else:
        fname = None

    if fname != None:
        image_data  = mpimg.imread(fname)
        ax1.imshow(image_data)
        ax1.set_title('Flight Track', fontsize=14)

    ax1.axis('off')

    # forward camera
    fnames_good = sorted(glob.glob('%s/*%s*_good.png' % (init.fdir_fcam_graph, dtime0_s)))
    Ngood       = len(fnames_good)
    fnames_bad  = sorted(glob.glob('%s/*%s*_bad.png' % (init.fdir_fcam_graph, dtime0_s)))
    Nbad        = len(fnames_bad)

    if Ngood > 0:
        fname = fnames_good[0]
        ax2.set_title('Forward Camera', fontsize=14)
    elif Nbad > 0:
        fname = fnames_bad[0]
        ax2.set_title('Forward Camera', fontsize=14, color='dimgray')
    else:
        fname = None

    if fname != None:
        image_data  = mpimg.imread(fname)
        ax2.imshow(image_data)

    ax2.axis('off')

    # nadir camera
    fnames_good = sorted(glob.glob('%s/*%s*_good.png' % (init.fdir_ncam_graph, dtime0_s)))
    Ngood       = len(fnames_good)
    fnames_bad  = sorted(glob.glob('%s/*%s*_bad.png' % (init.fdir_ncam_graph, dtime0_s)))
    Nbad        = len(fnames_bad)

    if Ngood > 0:
        fname = fnames_good[0]
        ax3.set_title('Nadir Camera', fontsize=14)
    elif Nbad > 0:
        fname = fnames_bad[0]
        ax3.set_title('Nadir Camera', fontsize=14, color='dimgray')
    else:
        fname = None

    if fname != None:
        image_data  = mpimg.imread(fname)
        if init.date_s == '2014-09-04':
            ax3.imshow(image_data, origin='lower')
        else:
            ax3.imshow(image_data)

    ax3.axis('off')

    if False:
        # ssfr time series
        time_sec, spec_zen, spec_nad = GDATA_SSFR_NAT(init.fname_ssfr)
        logic = (time_sec >= time_sec0-720.0) & (time_sec <= time_sec0+720.0)
        xx    = time_sec[logic]
        yy_z  = spec_zen[logic]
        yy_n  = spec_nad[logic]
        ax4.xaxis.set_major_locator(FixedLocator(time_sec0+np.arange(-720.0, 721.0, 180.0)))
        ax4.set_xticklabels(['', '', '-0.1h', '', 'UTC', '', '+0.1h', '', ''])
        ax4.set_xlim([time_sec0-720.000001, time_sec0+720.000001])
        ax4.set_ylim([0, 1.2])
        ax4.scatter(xx, yy_n, c='b', edgecolor='none', alpha=0.8, label='$\mathrm{F\\uparrow}$'  , s=5)
        ax4.scatter(xx, yy_z, c='r', edgecolor='none', alpha=0.8, label='$\mathrm{F\downarrow}$', s=5)
        ax4.legend(fontsize=10, loc='upper right', framealpha=0.5, markerscale=2)
        ax4.axvline(time_sec0, linewidth=1.0, linestyle=':', color='k')
        ax4.set_ylabel('Irradiance [$\mathrm{W m^{-2} nm^{-1}}$]', fontsize=12)
        ax4.set_title('SSFR (0.5$\mathrm{\mu m}$)', fontsize=14)

        # ssfr spectra
        time_sec, wvl_zen, spec_zen, wvl_nad, spec_nad = GDATA_SSFR_SPEC(init.fname_ssfr, time_sec0)
        ax8.xaxis.set_major_locator(FixedLocator(np.arange(200, 2201, 400)))
        ax8.set_xlim([200, 2200])
        ax8.set_ylim([0, 1.2])
        if np.abs(time_sec-time_sec0)<2.0:
            ax8.scatter(wvl_nad, spec_nad, c='b', edgecolor='none', alpha=0.8, label='$\mathrm{F\\uparrow}$'  , s=5)
            ax8.scatter(wvl_zen, spec_zen, c='r', edgecolor='none', alpha=0.8, label='$\mathrm{F\downarrow}$', s=5)
            ax8.legend(fontsize=10, loc='upper right', framealpha=0.5, markerscale=2)
        ax8.set_xlabel('Wavelength [nm]', fontsize=12)
        #ax8.set_ylabel('Irradiance [$\mathrm{W m^{-2} nm^{-1}}$]', fontsize=12)
        ax8.yaxis.set_ticklabels([])
        ax8.set_title('SSFR Spectra', fontsize=14)

        # kt-19 time series
        time_sec, zenT, nadT = GDATA_KT19(init.fname_kt19)
        logic_n = (time_sec >= time_sec0-720.0) & (time_sec <= time_sec0+720.0)
        xx_n    = time_sec[logic_n]
        yy_n    = nadT[logic_n]

        logic_z = (time_sec >= time_sec0-720.0) & (time_sec <= time_sec0+720.0) & (zenT>-20.0)
        xx_z    = time_sec[logic_z]
        yy_z    = zenT[logic_z]

        ax6.xaxis.set_major_locator(FixedLocator(time_sec0+np.arange(-720.0, 721.0, 180.0)))
        ax6.set_xticklabels(['', '', '-0.1h', '', 'UTC', '', '+0.1h', '', ''])
        ax6.set_xlim([time_sec0-720.000001, time_sec0+720.000001])
        ax6.set_ylim([-20, 5])
        ax6.scatter(xx_n, yy_n, c='b', edgecolor='none', alpha=0.8, label='Nadir' , s=2)
        if logic_z.sum() > 0:
            ax6.scatter(xx_z, yy_z, c='r', edgecolor='none', alpha=0.8, label='Zenith', s=2)
        ax6.legend(fontsize=10, loc='upper right', framealpha=0.5, markerscale=3)
        ax6.axvline(time_sec0, linewidth=1.0, linestyle=':', color='k')
        ax6.set_ylabel('Temperature [$\mathrm{^\circ C}$]', fontsize=12, rotation=270, labelpad=16)
        ax6.yaxis.tick_right()
        ax6.yaxis.set_ticks_position('both')
        ax6.yaxis.set_label_position('right')
        ax6.set_title('KT-19', fontsize=14)

    fig.suptitle("%s UTC" % (dtime0.strftime('%Y-%m-%d %H:%M:%S')), fontsize=20, y=0.96)

    time_trk, lon_trk, lat_trk, alt_trk = GDATA_TRK(init.fname_trk)
    index = np.argmin(np.abs(time_trk - time_sec0))
    if time_trk[index]-time_sec0<1.0:
        lon_trk0 = lon_trk[index]
        lat_trk0 = lat_trk[index]
        alt_trk0 = alt_trk[index]

        fig.text(0.5, 0.90, '(%.4fh, %7.2f$^\circ$, %5.2f$^\circ$, %4dm)' % (time_sec0/3600.0, lon_trk0, lat_trk0, alt_trk0), fontsize=16, ha='center')

    if testMode:
        plt.show()
        exit()
    fname_graph = '%s/join_%s.png' % (init.fdir_join_graph, dtime0_s)
    plt.savefig(fname_graph)
    print('%s is complete.' % fname_graph)
    plt.close(fig)

def PLT_JOIN_V6(statements, testMode=False):

    init, time_sec0 = statements

    dtime0    = init.date+datetime.timedelta(seconds=time_sec0)
    dtime0_s  = dtime0.strftime('%Y-%m-%d_%H:%M:%S')

    rcParams['font.size'] = 12
    fig = plt.figure(figsize=(12, 7.5))
    gs  = gridspec.GridSpec(6, 9)
    ax1 = plt.subplot(gs[0:3, 0:3])
    ax2 = plt.subplot(gs[0:3, 3:6])
    ax3 = plt.subplot(gs[0:3, 6:9])
    ax4 = plt.subplot(gs[3:6, 0:3])
    ax6 = plt.subplot(gs[3:6, 6:9])
    ax8 = plt.subplot(gs[3:6, 3:6])

    # flight track
    #{{{
    fnames      = sorted(glob.glob('%s/*%s*.png' % (init.fdir_trk_graph, dtime0_s)))
    NFile       = len(fnames)
    fnames_old  = sorted(glob.glob('%s/*%s*.png' % (init.fdir_trk_graph, (dtime0_s.replace('_', '-')).replace(':', '-'))))
    Nold        = len(fnames_old)
    ax1.axis('off')
    if NFile > 0:
        fname = fnames[0]
    elif Nold > 0:
        fname = fnames_old[0]
    else:
        fname = None

    if fname != None:
        image_data  = mpimg.imread(fname)
        ax1.imshow(image_data)
        ax1.set_title('Flight Track', fontsize=14)

    ax1.axis('off')
    #}}}

    # forward camera
    #{{{
    if init.date_s=='2014-09-07' and time_sec0>=86400.0:
        dtime0_s_cam = (dtime0-datetime.timedelta(seconds=86400)).strftime('%Y-%m-%d_%H:%M:%S')
        fnames_good = sorted(glob.glob('%s/*%s*_good.png' % (init.fdir_fcam_graph, dtime0_s_cam)))
        Ngood       = len(fnames_good)
        fnames_fine = sorted(glob.glob('%s/*%s*_fine.png' % (init.fdir_fcam_graph, dtime0_s_cam)))
        Nfine       = len(fnames_fine)
        fnames_okay = sorted(glob.glob('%s/*%s*_okay.png' % (init.fdir_fcam_graph, dtime0_s_cam)))
        Nokay       = len(fnames_okay)
        fnames_old  = sorted(glob.glob('%s/*%s*.png' % (init.fdir_fcam_graph, (dtime0_s_cam.replace('_', '-')).replace(':', '-'))))
        Nold        = len(fnames_old)
    else:
        fnames_good = sorted(glob.glob('%s/*%s*_good.png' % (init.fdir_fcam_graph, dtime0_s)))
        Ngood       = len(fnames_good)
        fnames_fine = sorted(glob.glob('%s/*%s*_fine.png' % (init.fdir_fcam_graph, dtime0_s)))
        Nfine       = len(fnames_fine)
        fnames_okay = sorted(glob.glob('%s/*%s*_okay.png' % (init.fdir_fcam_graph, dtime0_s)))
        Nokay       = len(fnames_okay)
        fnames_old  = sorted(glob.glob('%s/*%s*.png' % (init.fdir_fcam_graph, (dtime0_s.replace('_', '-')).replace(':', '-'))))
        Nold        = len(fnames_old)

    if Ngood > 0:
        fname = fnames_good[0]
        ax2.set_title('Forward Camera', fontsize=14)
    elif Nfine > 0:
        fname = fnames_fine[0]
        ax2.set_title('Forward Camera', fontsize=14, color='orange')
    elif Nokay > 0:
        fname = fnames_okay[0]
        ax2.set_title('Forward Camera', fontsize=14, color='red')
    elif Nold  > 0:
        fname = fnames_old[0]
        ax2.set_title('Forward Camera', fontsize=14, color='dimgray')
    else:
        fname = None

    if fname != None:
        image_data  = mpimg.imread(fname)
        ax2.imshow(image_data)

    ax2.axis('off')
    #}}}

    # nadir camera
    #{{{
    if init.date_s=='2014-09-07' and time_sec0>=86400.0:
        dtime0_s_cam = (dtime0-datetime.timedelta(seconds=86400)).strftime('%Y-%m-%d_%H:%M:%S')
        fnames_good = sorted(glob.glob('%s/*%s*_good.png' % (init.fdir_ncam_graph, dtime0_s_cam)))
        Ngood       = len(fnames_good)
        fnames_fine = sorted(glob.glob('%s/*%s*_fine.png' % (init.fdir_ncam_graph, dtime0_s_cam)))
        Nfine       = len(fnames_fine)
        fnames_okay = sorted(glob.glob('%s/*%s*_okay.png' % (init.fdir_ncam_graph, dtime0_s_cam)))
        Nokay       = len(fnames_okay)
        fnames_old  = sorted(glob.glob('%s/*%s*.png' % (init.fdir_ncam_graph, (dtime0_s_cam.replace('_', '-')).replace(':', '-'))))
        Nold        = len(fnames_old)
    else:
        fnames_good = sorted(glob.glob('%s/*%s*_good.png' % (init.fdir_ncam_graph, dtime0_s)))
        Ngood       = len(fnames_good)
        fnames_fine = sorted(glob.glob('%s/*%s*_fine.png' % (init.fdir_ncam_graph, dtime0_s)))
        Nfine       = len(fnames_fine)
        fnames_okay = sorted(glob.glob('%s/*%s*_okay.png' % (init.fdir_ncam_graph, dtime0_s)))
        Nokay       = len(fnames_okay)
        fnames_old  = sorted(glob.glob('%s/*%s*.png' % (init.fdir_ncam_graph, (dtime0_s.replace('_', '-')).replace(':', '-'))))
        Nold        = len(fnames_old)

    if Ngood > 0:
        fname = fnames_good[0]
        ax3.set_title('Nadir Camera', fontsize=14)
    elif Nfine > 0:
        fname = fnames_fine[0]
        ax3.set_title('Nadir Camera', fontsize=14, color='orange')
    elif Nokay > 0:
        fname = fnames_okay[0]
        ax3.set_title('Nadir Camera', fontsize=14, color='red')
    elif Nold > 0:
        fname = fnames_old[0]
        ax3.set_title('Nadir Camera', fontsize=14, color='dimgray')
    else:
        fname = None

    if fname != None:
        image_data  = mpimg.imread(fname)
        if init.date_s == '2014-09-04':
            ax3.imshow(image_data, origin='lower')
        else:
            ax3.imshow(image_data)

    ax3.axis('off')
    #}}}

    # ssfr time series
    #{{{
    time_sec, spec_zen, spec_nad = GDATA_SSFR_NAT(init.fname_ssfr)
    logic = (time_sec >= time_sec0-720.0) & (time_sec <= time_sec0+720.0)
    xx    = time_sec[logic]
    yy_z  = spec_zen[logic]
    yy_n  = spec_nad[logic]
    ax4.xaxis.set_major_locator(FixedLocator(time_sec0+np.arange(-720.0, 721.0, 180.0)))
    ax4.set_xticklabels(['', '', '-0.1h', '', 'UTC', '', '+0.1h', '', ''])
    ax4.set_xlim([time_sec0-720.000001, time_sec0+720.000001])
    ax4.set_ylim([0, 1.2])
    ax4.scatter(xx, yy_n, c='b', edgecolor='none', alpha=0.8, label='$\mathrm{F\\uparrow}$'  , s=5)
    ax4.scatter(xx, yy_z, c='r', edgecolor='none', alpha=0.8, label='$\mathrm{F\downarrow}$', s=5)
    ax4.legend(fontsize=10, loc='upper right', framealpha=0.5, markerscale=2)
    ax4.axvline(time_sec0, linewidth=1.0, linestyle=':', color='k')
    ax4.set_ylabel('Irradiance [$\mathrm{W m^{-2} nm^{-1}}$]', fontsize=12)
    ax4.set_title('SSFR (0.5$\mathrm{\mu m}$)', fontsize=14)
    #}}}

    # ssfr spectra
    #{{{
    time_sec, wvl_zen, spec_zen, wvl_nad, spec_nad = GDATA_SSFR_SPEC(init.fname_ssfr, time_sec0)
    ax8.xaxis.set_major_locator(FixedLocator(np.arange(200, 2201, 400)))
    ax8.set_xlim([200, 2200])
    ax8.set_ylim([0, 1.2])
    if np.abs(time_sec-time_sec0)<2.0:
        ax8.scatter(wvl_nad, spec_nad, c='b', edgecolor='none', alpha=0.8, label='$\mathrm{F\\uparrow}$'  , s=5)
        ax8.scatter(wvl_zen, spec_zen, c='r', edgecolor='none', alpha=0.8, label='$\mathrm{F\downarrow}$', s=5)
        ax8.legend(fontsize=10, loc='upper right', framealpha=0.5, markerscale=2)
    ax8.set_xlabel('Wavelength [nm]', fontsize=12)
    #ax8.set_ylabel('Irradiance [$\mathrm{W m^{-2} nm^{-1}}$]', fontsize=12)
    ax8.yaxis.set_ticklabels([])
    ax8.set_title('SSFR Spectra', fontsize=14)
    #}}}

    # kt-19 time series
    #{{{
    time_sec, zenT, nadT = GDATA_KT19(init.fname_kt19)
    logic_n = (time_sec >= time_sec0-720.0) & (time_sec <= time_sec0+720.0)
    xx_n    = time_sec[logic_n]
    yy_n    = nadT[logic_n]

    logic_z = (time_sec >= time_sec0-720.0) & (time_sec <= time_sec0+720.0) & (zenT>-20.0)
    xx_z    = time_sec[logic_z]
    yy_z    = zenT[logic_z]

    ax6.xaxis.set_major_locator(FixedLocator(time_sec0+np.arange(-720.0, 721.0, 180.0)))
    ax6.set_xticklabels(['', '', '-0.1h', '', 'UTC', '', '+0.1h', '', ''])
    ax6.set_xlim([time_sec0-720.000001, time_sec0+720.000001])
    ax6.set_ylim([-20, 5])
    ax6.scatter(xx_n, yy_n, c='b', edgecolor='none', alpha=0.8, label='Nadir' , s=2)
    if logic_z.sum() > 0:
        ax6.scatter(xx_z, yy_z, c='r', edgecolor='none', alpha=0.8, label='Zenith', s=2)
    ax6.legend(fontsize=10, loc='upper right', framealpha=0.5, markerscale=3)
    ax6.axvline(time_sec0, linewidth=1.0, linestyle=':', color='k')
    ax6.set_ylabel('Temperature [$\mathrm{^\circ C}$]', fontsize=12, rotation=270, labelpad=16)
    ax6.yaxis.tick_right()
    ax6.yaxis.set_ticks_position('both')
    ax6.yaxis.set_label_position('right')
    ax6.set_title('KT-19', fontsize=14)
    #}}}

    fig.suptitle("%s UTC" % (dtime0.strftime('%Y-%m-%d %H:%M:%S')), fontsize=20, y=0.96)

    time_trk, lon_trk, lat_trk, alt_trk = GDATA_TRK(init.fname_trk)
    index = np.argmin(np.abs(time_trk - time_sec0))
    if time_trk[index]-time_sec0<1.0:
        lon_trk0 = lon_trk[index]
        lat_trk0 = lat_trk[index]
        alt_trk0 = alt_trk[index]

        fig.text(0.5, 0.90, '(%.4fh, %7.2f$^\circ$, %5.2f$^\circ$, %4dm)' % (time_sec0/3600.0, lon_trk0, lat_trk0, alt_trk0), fontsize=16, ha='center')

    if testMode:
        plt.show()
        exit()
    fname_graph = '%s/join_%s.png' % (init.fdir_join_graph, dtime0_s)
    plt.savefig(fname_graph)
    print('%s is complete.' % fname_graph)
    plt.close(fig)

def PLT_JOIN_V5(statements, testMode=False):

    init, time_sec0 = statements

    dtime0    = init.date+datetime.timedelta(seconds=time_sec0)
    dtime0_s  = dtime0.strftime('%Y-%m-%d_%H:%M:%S')

    rcParams['font.size'] = 12
    fig = plt.figure(figsize=(14, 8))
    gs  = gridspec.GridSpec(13, 20)
    ax1 = plt.subplot(gs[0:7, 0:6])
    ax2 = plt.subplot(gs[1:6, 6:13])
    ax3 = plt.subplot(gs[1:6, 13:20])
    ax4 = plt.subplot(gs[7:13, 0:6])
    ax6 = plt.subplot(gs[7:10, 7:13])
    ax7 = plt.subplot(gs[10:13, 7:13])
    ax8 = plt.subplot(gs[7:13, 14:20])

    # flight track
    #{{{
    fnames      = sorted(glob.glob('%s/*%s*.png' % (init.fdir_trk_graph, dtime0_s)))
    NFile       = len(fnames)
    fnames_old  = sorted(glob.glob('%s/*%s*.png' % (init.fdir_trk_graph, (dtime0_s.replace('_', '-')).replace(':', '-'))))
    Nold        = len(fnames_old)
    ax1.axis('off')
    if NFile > 0:
        fname = fnames[0]
    elif Nold > 0:
        fname = fnames_old[0]
    else:
        fname = None

    if fname != None:
        image_data  = mpimg.imread(fname)
        ax1.imshow(image_data)
        ax1.set_title('Flight Track', fontsize=14)

    ax1.axis('off')
    #}}}

    # forward camera
    #{{{
    fnames_good = sorted(glob.glob('%s/*%s*_good.png' % (init.fdir_fcam_graph, dtime0_s)))
    Ngood       = len(fnames_good)
    fnames_fine = sorted(glob.glob('%s/*%s*_fine.png' % (init.fdir_fcam_graph, dtime0_s)))
    Nfine       = len(fnames_fine)
    fnames_okay = sorted(glob.glob('%s/*%s*_okay.png' % (init.fdir_fcam_graph, dtime0_s)))
    Nokay       = len(fnames_okay)
    fnames_old  = sorted(glob.glob('%s/*%s*.png' % (init.fdir_fcam_graph, (dtime0_s.replace('_', '-')).replace(':', '-'))))
    Nold        = len(fnames_old)
    if Ngood > 0:
        fname = fnames_good[0]
        ax2.set_title('Forward Camera', fontsize=14)
    elif Nfine > 0:
        fname = fnames_fine[0]
        ax2.set_title('Forward Camera', fontsize=14, color='orange')
    elif Nokay > 0:
        fname = fnames_okay[0]
        ax2.set_title('Forward Camera', fontsize=14, color='red')
    elif Nold  > 0:
        fname = fnames_old[0]
        ax2.set_title('Forward Camera', fontsize=14, color='dimgray')
    else:
        fname = None

    if fname != None:
        image_data  = mpimg.imread(fname)
        ax2.imshow(image_data)

    ax2.axis('off')
    #}}}

    # nadir camera
    #{{{
    fnames_good = sorted(glob.glob('%s/*%s*_good.png' % (init.fdir_ncam_graph, dtime0_s)))
    Ngood       = len(fnames_good)
    fnames_fine = sorted(glob.glob('%s/*%s*_fine.png' % (init.fdir_ncam_graph, dtime0_s)))
    Nfine       = len(fnames_fine)
    fnames_okay = sorted(glob.glob('%s/*%s*_okay.png' % (init.fdir_ncam_graph, dtime0_s)))
    Nokay       = len(fnames_okay)
    fnames_old  = sorted(glob.glob('%s/*%s*.png' % (init.fdir_ncam_graph, (dtime0_s.replace('_', '-')).replace(':', '-'))))
    Nold        = len(fnames_old)
    if Ngood > 0:
        fname = fnames_good[0]
        ax3.set_title('Nadir Camera', fontsize=14)
    elif Nfine > 0:
        fname = fnames_fine[0]
        ax3.set_title('Nadir Camera', fontsize=14, color='orange')
    elif Nokay > 0:
        fname = fnames_okay[0]
        ax3.set_title('Nadir Camera', fontsize=14, color='red')
    elif Nold > 0:
        fname = fnames_old[0]
        ax3.set_title('Nadir Camera', fontsize=14, color='dimgray')
    else:
        fname = None

    if fname != None:
        image_data  = mpimg.imread(fname)
        ax3.imshow(image_data)

    ax3.axis('off')
    #}}}

    # ssfr time series
    #{{{
    time_sec, spec_zen, spec_nad = GDATA_SSFR_NAT(init.fname_ssfr)
    logic = (time_sec >= time_sec0-720.0) & (time_sec <= time_sec0+720.0)
    xx    = time_sec[logic]
    yy_z  = spec_zen[logic]
    yy_n  = spec_nad[logic]
    ax4.xaxis.set_major_locator(FixedLocator(time_sec0+np.arange(-720.0, 721.0, 180.0)))
    ax4.set_xticklabels(['-0.2h', '', '-0.1h', '', 'UTC', '', '+0.1h', '', '+0.2h'])
    ax4.set_xlim([time_sec0-720.000001, time_sec0+720.000001])
    ax4.set_ylim([0, 1.2])
    ax4.scatter(xx, yy_n, c='b', edgecolor='none', alpha=0.8, label='$\mathrm{F\\uparrow}$'  , s=5)
    ax4.scatter(xx, yy_z, c='r', edgecolor='none', alpha=0.8, label='$\mathrm{F\downarrow}$', s=5)
    ax4.legend(fontsize=10, loc='upper right', framealpha=0.5, markerscale=2)
    ax4.axvline(time_sec0, linewidth=1.0, linestyle=':', color='k')
    ax4.set_ylabel('Irradiance [$\mathrm{W m^{-2} nm^{-1}}$]', fontsize=12)
    ax4.set_title('SSFR (0.5$\mathrm{\mu m}$)', fontsize=14)
    #}}}

    # kt-19 time series
    #{{{
    time_sec, zenT, nadT = GDATA_KT19(init.fname_kt19)
    logic = (time_sec >= time_sec0-720.0) & (time_sec <= time_sec0+720.0)
    xx    = time_sec[logic]
    yy_z  = zenT[logic]
    yy_n  = nadT[logic]

    ax6.xaxis.set_major_locator(FixedLocator(time_sec0+np.arange(-720.0, 721.0, 180.0)))
    ax6.set_xlim([time_sec0-720.000001, time_sec0+720.000001])
    #ax6.set_ylim([-20, 5])
    ax6.scatter(xx, yy_n, c='b', edgecolor='none', alpha=0.8, label='Nadir' , s=2)
    ax6.axvline(time_sec0, linewidth=1.0, linestyle=':', color='k')
    ax6.legend(fontsize=10, loc='upper right', framealpha=0.5, markerscale=3)
    #ax6.set_ylabel('Temperature [$\mathrm{^\circ C}$]', fontsize=12)
    ax6.set_title('KT-19', fontsize=14)
    ax6.spines['bottom'].set_visible(False)

    ax6.xaxis.tick_top()
    ax6.tick_params(labeltop='off')

    ax7.xaxis.tick_bottom()

    ax7.spines['top'].set_visible(False)
    ax7.xaxis.set_major_locator(FixedLocator(time_sec0+np.arange(-720.0, 721.0, 180.0)))
    ax7.set_xlim([time_sec0-720.000001, time_sec0+720.000001])
    ax7.scatter(xx, yy_z, c='r', edgecolor='none', alpha=0.8, label='Zenith', s=2)
    ax7.axvline(time_sec0, linewidth=1.0, linestyle=':', color='k')
    ax7.legend(fontsize=10, loc='upper right', framealpha=0.5, markerscale=3)
    ax7.set_xticklabels(['-0.2h', '', '-0.1h', '', 'UTC', '', '+0.1h', '', '+0.2h'])
    #}}}

    # ssfr spectra
    #{{{
    time_sec, wvl_zen, spec_zen, wvl_nad, spec_nad = GDATA_SSFR_SPEC(init.fname_ssfr, time_sec0)
    ax8.xaxis.set_major_locator(FixedLocator(np.arange(200, 2201, 400)))
    ax8.set_xlim([200, 2200])
    ax8.set_ylim([0, 1.2])
    if np.abs(time_sec-time_sec0)<2.0:
        ax8.scatter(wvl_nad, spec_nad, c='b', edgecolor='none', alpha=0.8, label='$\mathrm{F\\uparrow}$'  , s=5)
        ax8.scatter(wvl_zen, spec_zen, c='r', edgecolor='none', alpha=0.8, label='$\mathrm{F\downarrow}$', s=5)
        ax8.legend(fontsize=10, loc='upper right', framealpha=0.5, markerscale=2)
    ax8.set_xlabel('Wavelength [nm]', fontsize=12)
    ax8.set_ylabel('Irradiance [$\mathrm{W m^{-2} nm^{-1}}$]', fontsize=12)
    ax8.set_title('SSFR Spectra', fontsize=14)
    #}}}

    fig.suptitle("%s UTC" % (dtime0.strftime('%Y-%m-%d %H:%M:%S')), fontsize=20, y=0.96)

    time_trk, lon_trk, lat_trk, alt_trk = GDATA_TRK(init.fname_trk)
    index = np.argmin(np.abs(time_trk - time_sec0))
    if time_trk[index]-time_sec0<1.0:
        lon_trk0 = lon_trk[index]
        lat_trk0 = lat_trk[index]
        alt_trk0 = alt_trk[index]

        fig.text(0.5, 0.90, '(%.4fh, %7.2f$^\circ$, %5.2f$^\circ$, %4dm)' % (time_sec0/3600.0, lon_trk0, lat_trk0, alt_trk0), fontsize=16, ha='center')

    if testMode:
        plt.show()
        exit()
    fname_graph = '%s/join_%s.png' % (init.fdir_join_graph, dtime0_s)
    plt.savefig(fname_graph)
    print('%s is complete.' % fname_graph)
    plt.close(fig)

def PLT_JOIN_V4(statements, testMode=False):

    init, time_sec0 = statements

    dtime0    = init.date+datetime.timedelta(seconds=time_sec0)
    dtime0_s  = dtime0.strftime('%Y-%m-%d_%H:%M:%S')

    rcParams['font.size'] = 12
    fig = plt.figure(figsize=(14, 8))
    gs  = gridspec.GridSpec(11, 17)
    ax1 = plt.subplot(gs[0:6, 0:5])
    ax2 = plt.subplot(gs[0:6, 5:11])
    ax3 = plt.subplot(gs[0:6, 11:17])
    ax4 = plt.subplot(gs[6:11, 0:5])
    ax6 = plt.subplot(gs[6:11, 6:11])
    ax8 = plt.subplot(gs[6:11, 12:17])

    # flight track
    #{{{
    fnames      = sorted(glob.glob('%s/*%s*.png' % (init.fdir_trk_graph, dtime0_s)))
    NFile       = len(fnames)
    fnames_old  = sorted(glob.glob('%s/*%s*.png' % (init.fdir_trk_graph, (dtime0_s.replace('_', '-')).replace(':', '-'))))
    Nold        = len(fnames_old)
    ax1.axis('off')
    if NFile > 0:
        fname = fnames[0]
    elif Nold > 0:
        fname = fnames_old[0]
    else:
        fname = None

    if fname != None:
        image_data  = mpimg.imread(fname)
        ax1.imshow(image_data)
        ax1.set_title('Flight Track', fontsize=14)

    ax1.axis('off')
    #}}}

    # forward camera
    #{{{
    fnames_good = sorted(glob.glob('%s/*%s*_good.png' % (init.fdir_fcam_graph, dtime0_s)))
    Ngood       = len(fnames_good)
    fnames_fine = sorted(glob.glob('%s/*%s*_fine.png' % (init.fdir_fcam_graph, dtime0_s)))
    Nfine       = len(fnames_fine)
    fnames_okay = sorted(glob.glob('%s/*%s*_okay.png' % (init.fdir_fcam_graph, dtime0_s)))
    Nokay       = len(fnames_okay)
    fnames_old  = sorted(glob.glob('%s/*%s*.png' % (init.fdir_fcam_graph, (dtime0_s.replace('_', '-')).replace(':', '-'))))
    Nold        = len(fnames_old)
    if Ngood > 0:
        fname = fnames_good[0]
        ax2.set_title('Forward Camera', fontsize=14)
    elif Nfine > 0:
        fname = fnames_fine[0]
        ax2.set_title('Forward Camera', fontsize=14, color='orange')
    elif Nokay > 0:
        fname = fnames_okay[0]
        ax2.set_title('Forward Camera', fontsize=14, color='red')
    elif Nold  > 0:
        fname = fnames_old[0]
        ax2.set_title('Forward Camera', fontsize=14, color='dimgray')
    else:
        fname = None

    if fname != None:
        image_data  = mpimg.imread(fname)
        ax2.imshow(image_data)

    ax2.axis('off')
    #}}}

    # nadir camera
    #{{{
    fnames_good = sorted(glob.glob('%s/*%s*_good.png' % (init.fdir_ncam_graph, dtime0_s)))
    Ngood       = len(fnames_good)
    fnames_fine = sorted(glob.glob('%s/*%s*_fine.png' % (init.fdir_ncam_graph, dtime0_s)))
    Nfine       = len(fnames_fine)
    fnames_okay = sorted(glob.glob('%s/*%s*_okay.png' % (init.fdir_ncam_graph, dtime0_s)))
    Nokay       = len(fnames_okay)
    fnames_old  = sorted(glob.glob('%s/*%s*.png' % (init.fdir_ncam_graph, (dtime0_s.replace('_', '-')).replace(':', '-'))))
    Nold        = len(fnames_old)
    if Ngood > 0:
        fname = fnames_good[0]
        ax3.set_title('Nadir Camera', fontsize=14)
    elif Nfine > 0:
        fname = fnames_fine[0]
        ax3.set_title('Nadir Camera', fontsize=14, color='orange')
    elif Nokay > 0:
        fname = fnames_okay[0]
        ax3.set_title('Nadir Camera', fontsize=14, color='red')
    elif Nold > 0:
        fname = fnames_old[0]
        ax3.set_title('Nadir Camera', fontsize=14, color='dimgray')
    else:
        fname = None

    if fname != None:
        image_data  = mpimg.imread(fname)
        ax3.imshow(image_data)

    ax3.axis('off')
    #}}}

    # ssfr time series
    #{{{
    time_sec, spec_zen, spec_nad = GDATA_SSFR_NAT(init.fname_ssfr)
    logic = (time_sec >= time_sec0-720.0) & (time_sec <= time_sec0+720.0)
    xx    = time_sec[logic]
    yy_z  = spec_zen[logic]
    yy_n  = spec_nad[logic]
    ax4.xaxis.set_major_locator(FixedLocator(time_sec0+np.arange(-720.0, 721.0, 180.0)))
    ax4.set_xticklabels(['-0.2h', '', '-0.1h', '', 'UTC', '', '+0.1h', '', '+0.2h'])
    ax4.set_xlim([time_sec0-720.000001, time_sec0+720.000001])
    ax4.set_ylim([0, 1.2])
    ax4.scatter(xx, yy_n, c='b', edgecolor='none', alpha=0.8, label='$\mathrm{F\\uparrow}$'  , s=5)
    ax4.scatter(xx, yy_z, c='r', edgecolor='none', alpha=0.8, label='$\mathrm{F\downarrow}$', s=5)
    ax4.legend(fontsize=10, loc='upper right', framealpha=0.5, markerscale=2)
    ax4.axvline(time_sec0, linewidth=1.0, linestyle=':', color='k')
    ax4.set_ylabel('Irradiance [$\mathrm{W m^{-2} nm^{-1}}$]', fontsize=12)
    ax4.set_title('SSFR (0.5$\mathrm{\mu m}$)', fontsize=14)
    #}}}

    # kt-19 time series
    #{{{
    time_sec, zenT, nadT = GDATA_KT19(init.fname_kt19)
    logic = (time_sec >= time_sec0-720.0) & (time_sec <= time_sec0+720.0)
    xx    = time_sec[logic]
    yy_z  = zenT[logic]
    yy_n  = nadT[logic]

    ax6.xaxis.set_major_locator(FixedLocator(time_sec0+np.arange(-720.0, 721.0, 180.0)))
    ax6.set_xticklabels(['-0.2h', '', '-0.1h', '', 'UTC', '', '+0.1h', '', '+0.2h'])
    ax6.set_xlim([time_sec0-720.000001, time_sec0+720.000001])
    ax6.set_ylim([-20, 5])
    ax6.scatter(xx, yy_n, c='b', edgecolor='none', alpha=0.8, label='Nadir' , s=2)
    ax6.scatter(xx, yy_z, c='r', edgecolor='none', alpha=0.8, label='Zenith', s=2)
    ax6.legend(fontsize=10, loc='upper right', framealpha=0.5, markerscale=3)
    ax6.axvline(time_sec0, linewidth=1.0, linestyle=':', color='k')
    ax6.set_ylabel('Temperature [$\mathrm{^\circ C}$]', fontsize=12)
    ax6.set_title('KT-19', fontsize=14)
    #}}}

    # ssfr spectra
    #{{{
    time_sec, wvl_zen, spec_zen, wvl_nad, spec_nad = GDATA_SSFR_SPEC(init.fname_ssfr, time_sec0)
    ax8.xaxis.set_major_locator(FixedLocator(np.arange(200, 2201, 400)))
    ax8.set_xlim([200, 2200])
    ax8.set_ylim([0, 1.2])
    if np.abs(time_sec-time_sec0)<2.0:
        ax8.scatter(wvl_nad, spec_nad, c='b', edgecolor='none', alpha=0.8, label='$\mathrm{F\\uparrow}$'  , s=5)
        ax8.scatter(wvl_zen, spec_zen, c='r', edgecolor='none', alpha=0.8, label='$\mathrm{F\downarrow}$', s=5)
        ax8.legend(fontsize=10, loc='upper right', framealpha=0.5, markerscale=2)
    ax8.set_xlabel('Wavelength [nm]', fontsize=12)
    ax8.set_ylabel('Irradiance [$\mathrm{W m^{-2} nm^{-1}}$]', fontsize=12)
    ax8.set_title('SSFR Spectra', fontsize=14)
    #}}}

    fig.suptitle("%s UTC" % (dtime0.strftime('%Y-%m-%d %H:%M:%S')), fontsize=20, y=0.96)

    time_trk, lon_trk, lat_trk, alt_trk = GDATA_TRK(init.fname_trk)
    index = np.argmin(np.abs(time_trk - time_sec0))
    if time_trk[index]-time_sec0<1.0:
        lon_trk0 = lon_trk[index]
        lat_trk0 = lat_trk[index]
        alt_trk0 = alt_trk[index]

        fig.text(0.5, 0.90, '(%.4fh, %7.2f$^\circ$, %5.2f$^\circ$, %4dm)' % (time_sec0/3600.0, lon_trk0, lat_trk0, alt_trk0), fontsize=16, ha='center')

    if testMode:
        plt.show()
        exit()
    fname_graph = '%s/join_%s.png' % (init.fdir_join_graph, dtime0_s)
    plt.savefig(fname_graph)
    print('%s is complete.' % fname_graph)
    plt.close(fig)

def PLT_JOIN_V3(statements, testMode=False):

    init, time_sec0 = statements

    dtime0    = init.date+datetime.timedelta(seconds=time_sec0)
    dtime0_s  = dtime0.strftime('%Y-%m-%d_%H:%M:%S')

    rcParams['font.size'] = 12
    fig = plt.figure(figsize=(14, 8))
    gs  = gridspec.GridSpec(6, 9)
    ax1 = plt.subplot(gs[0:3, 0:3])
    ax2 = plt.subplot(gs[0:3, 3:6])
    ax3 = plt.subplot(gs[0:3, 6:9])
    ax4 = plt.subplot(gs[3:6, 0:3])
    ax6 = plt.subplot(gs[3:6, 3:6])
    ax8 = plt.subplot(gs[3:6, 6:9])

    # flight track
    #{{{
    fnames = sorted(glob.glob('%s/*%s*.png' % (init.fdir_trk_graph, dtime0_s)))
    NFile  = len(fnames)
    ax1.axis('off')
    if NFile > 0:
        fname = fnames[0]
        image_data  = mpimg.imread(fname)
        ax1.imshow(image_data)
        ax1.set_title('Flight Track', fontsize=14)
    ax1.axis('off')
    #}}}

    # forward camera
    #{{{
    fnames_good = sorted(glob.glob('%s/*%s*_good.png' % (init.fdir_fcam_graph, dtime0_s)))
    Ngood       = len(fnames_good)
    fnames_fine = sorted(glob.glob('%s/*%s*_fine.png' % (init.fdir_fcam_graph, dtime0_s)))
    Nfine       = len(fnames_fine)
    fnames_okay = sorted(glob.glob('%s/*%s*_okay.png' % (init.fdir_fcam_graph, dtime0_s)))
    Nokay       = len(fnames_okay)
    if Ngood > 0:
        fname = fnames_good[0]
        ax2.set_title('Forward Camera', fontsize=14)
    elif Nfine > 0:
        fname = fnames_fine[0]
        ax2.set_title('Forward Camera', fontsize=14, color='red')
    elif Nokay > 0:
        fname = fnames_okay[0]
        ax2.set_title('Forward Camera', fontsize=14, color='darkred')
    else:
        fname = None

    if fname != None:
        image_data  = mpimg.imread(fname)
        ax2.imshow(image_data)

    ax2.axis('off')
    #}}}

    # nadir camera
    #{{{
    fnames_good = sorted(glob.glob('%s/*%s*_good.png' % (init.fdir_ncam_graph, dtime0_s)))
    Ngood       = len(fnames_good)
    fnames_fine = sorted(glob.glob('%s/*%s*_fine.png' % (init.fdir_ncam_graph, dtime0_s)))
    Nfine       = len(fnames_fine)
    fnames_okay = sorted(glob.glob('%s/*%s*_okay.png' % (init.fdir_ncam_graph, dtime0_s)))
    Nokay       = len(fnames_okay)
    if Ngood > 0:
        fname = fnames_good[0]
        ax3.set_title('Nadir Camera', fontsize=14)
    elif Nfine > 0:
        fname = fnames_fine[0]
        ax3.set_title('Nadir Camera', fontsize=14, color='red')
    elif Nokay > 0:
        fname = fnames_okay[0]
        ax3.set_title('Nadir Camera', fontsize=14, color='darkred')
    else:
        fname = None

    if fname != None:
        image_data  = mpimg.imread(fname)
        ax3.imshow(image_data)

    ax3.axis('off')
    #}}}

    # ssfr
    #{{{
    time_sec, spec_zen, spec_nad = GDATA_SSFR_NAT(init.fname_ssfr)
    logic = (time_sec >= time_sec0-720.0) & (time_sec <= time_sec0+720.0)
    xx    = time_sec[logic]
    yy_z  = spec_zen[logic]
    yy_n  = spec_nad[logic]
    ax4.xaxis.set_major_locator(FixedLocator(time_sec0+np.arange(-720.0, 721.0, 180.0)))
    ax4.set_xticklabels(['UTC-0.2h', '', '', '', 'UTC', '', '', '', 'UTC+0.2h'])
    ax4.set_xlim([time_sec0-720.000001, time_sec0+720.000001])
    ax4.set_ylim([0, 1.2])
    ax4.scatter(xx, yy_n, c='b', edgecolor='none', alpha=0.8, label='Nadir' , s=5)
    ax4.scatter(xx, yy_z, c='r', edgecolor='none', alpha=0.8, label='Zenith', s=5)
    ax4.axvline(time_sec0, linewidth=1.0, linestyle=':', color='k')
    ax4.set_ylabel('Irradiance [$\mathrm{W m^{-2} nm^{-1}}$]', fontsize=12)
    ax4.set_title('SSFR (0.5$\mathrm{\mu m}$)', fontsize=14)
    #}}}

    # kt-19
    #{{{
    time_sec, zenT, nadT = GDATA_KT19(init.fname_kt19)
    logic = (time_sec >= time_sec0-720.0) & (time_sec <= time_sec0+720.0)
    xx    = time_sec[logic]
    yy_z  = zenT[logic]
    yy_n  = nadT[logic]

    ax6.xaxis.set_major_locator(FixedLocator(time_sec0+np.arange(-720.0, 721.0, 180.0)))
    ax6.set_xticklabels(['UTC-0.2h', '', '', '', 'UTC', '', '', '', 'UTC+0.2h'])
    ax6.set_xlim([time_sec0-720.000001, time_sec0+720.000001])
    ax6.set_ylim([-20, 5])
    ax6.scatter(xx, yy_n, c='b', edgecolor='none', alpha=0.8, label='Nadir' , s=2)
    ax6.scatter(xx, yy_z, c='r', edgecolor='none', alpha=0.8, label='Zenith', s=2)
    ax6.axvline(time_sec0, linewidth=1.0, linestyle=':', color='k')
    ax6.set_ylabel('Temperature [$\mathrm{^\circ C}$]', fontsize=12)
    ax6.set_title('KT-19', fontsize=14)
    #}}}

    #fig.text(0.68, 0.408, '$\mathrm{F\\uparrow}$'  , fontsize=12, ha='center', backgroundcolor='b', color='white', alpha=0.8)
    #fig.text(0.68, 0.454, '$\mathrm{F\downarrow}$', fontsize=12, ha='center', backgroundcolor='r', color='white', alpha=0.8)
    #fig.text(0.68, 0.176, 'Nadir ', fontsize=12, ha='center', backgroundcolor='b', color='white')
    #fig.text(0.68, 0.222, 'Zenith', fontsize=12, ha='center', backgroundcolor='r', color='white')

    fig.suptitle("%s UTC" % (dtime0.strftime('%Y-%m-%d %H:%M:%S')), fontsize=20, y=0.99)

    time_trk, lon_trk, lat_trk, alt_trk = GDATA_TRK(init.fname_trk)
    index = np.argmin(np.abs(time_trk - time_sec0))
    if time_trk[index]-time_sec0<1.0:
        lon_trk0 = lon_trk[index]
        lat_trk0 = lat_trk[index]
        alt_trk0 = alt_trk[index]

        fig.text(0.5, 0.93, '(%.4fh, %7.2f$^\circ$, %5.2f$^\circ$, %4dm)' % (time_sec0/3600.0, lon_trk0, lat_trk0, alt_trk0), fontsize=16, ha='center')

    if testMode:
        plt.show()
        exit()
    fname_graph = '%s/join_%s.png' % (init.fdir_join_graph, dtime0_s)
    plt.savefig(fname_graph)
    print('%s is complete.' % fname_graph)
    plt.close(fig)

def PLT_JOIN_V2(statements, testMode=False):

    init, time_sec0 = statements

    dtime0    = init.date+datetime.timedelta(seconds=time_sec0)
    dtime0_s  = dtime0.strftime('%Y-%m-%d_%H:%M:%S')

    rcParams['font.size'] = 14
    fig = plt.figure(figsize=(12, 8))
    gs  = gridspec.GridSpec(7, 9)
    ax1 = plt.subplot(gs[0:3, 0:3])
    ax2 = plt.subplot(gs[0:3, 3:6])
    ax3 = plt.subplot(gs[0:3, 6:9])
    ax4 = plt.subplot(gs[3:5, :-3])
    ax5 = plt.subplot(gs[3:5, -2:])
    ax6 = plt.subplot(gs[5:7, :-3])
    ax7 = plt.subplot(gs[5:7, -2:])

    # flight track
    #{{{
    fnames = sorted(glob.glob('%s/*%s*.png' % (init.fdir_trk_graph, dtime0_s)))
    NFile  = len(fnames)
    ax1.axis('off')
    if NFile > 0:
        fname = fnames[0]
        image_data  = mpimg.imread(fname)
        ax1.imshow(image_data)
        ax1.set_title('Flight Track', fontsize=14)
    ax1.axis('off')
    #}}}

    # forward camera
    #{{{
    fnames_good = sorted(glob.glob('%s/*%s*_good.png' % (init.fdir_fcam_graph, dtime0_s)))
    Ngood       = len(fnames_good)
    fnames_fine = sorted(glob.glob('%s/*%s*_fine.png' % (init.fdir_fcam_graph, dtime0_s)))
    Nfine       = len(fnames_fine)
    fnames_okay = sorted(glob.glob('%s/*%s*_okay.png' % (init.fdir_fcam_graph, dtime0_s)))
    Nokay       = len(fnames_okay)
    if Ngood > 0:
        fname = fnames_good[0]
        ax2.set_title('Forward Camera', fontsize=14)
    elif Nfine > 0:
        fname = fnames_fine[0]
        ax2.set_title('Forward Camera', fontsize=14, color='red')
    elif Nokay > 0:
        fname = fnames_okay[0]
        ax2.set_title('Forward Camera', fontsize=14, color='darkred')
    else:
        fname = None

    if fname != None:
        image_data  = mpimg.imread(fname)
        ax2.imshow(image_data)

    ax2.axis('off')
    #}}}

    # nadir camera
    #{{{
    fnames_good = sorted(glob.glob('%s/*%s*_good.png' % (init.fdir_ncam_graph, dtime0_s)))
    Ngood       = len(fnames_good)
    fnames_fine = sorted(glob.glob('%s/*%s*_fine.png' % (init.fdir_ncam_graph, dtime0_s)))
    Nfine       = len(fnames_fine)
    fnames_okay = sorted(glob.glob('%s/*%s*_okay.png' % (init.fdir_ncam_graph, dtime0_s)))
    Nokay       = len(fnames_okay)
    if Ngood > 0:
        fname = fnames_good[0]
        ax3.set_title('Nadir Camera', fontsize=14)
    elif Nfine > 0:
        fname = fnames_fine[0]
        ax3.set_title('Nadir Camera', fontsize=14, color='red')
    elif Nokay > 0:
        fname = fnames_okay[0]
        ax3.set_title('Nadir Camera', fontsize=14, color='darkred')
    else:
        fname = None

    if fname != None:
        image_data  = mpimg.imread(fname)
        ax3.imshow(image_data)

    ax3.axis('off')
    #}}}

    # ssfr
    #{{{
    time_sec, spec_zen, spec_nad = GDATA_SSFR_NAT(init.fname_ssfr)
    logic = (time_sec >= time_sec0-720.0) & (time_sec <= time_sec0+720.0)
    xx    = time_sec[logic]
    yy_z  = spec_zen[logic]
    yy_n  = spec_nad[logic]
    ax4.xaxis.set_major_locator(FixedLocator(time_sec0+np.arange(-720.0, 721.0, 180.0)))
    ax4.set_xlim([time_sec0-720.000001, time_sec0+720.000001])
    ax4.set_ylim([-0.1, 1.2])
    ax4.scatter(xx, yy_n, c='b', edgecolor='none', alpha=0.8, label='Nadir' , s=5)
    ax4.scatter(xx, yy_z, c='r', edgecolor='none', alpha=0.8, label='Zenith', s=5)
    ax4.axvline(time_sec0, linewidth=1.0, linestyle=':', color='k')
    ax4.set_ylabel('Irradiance [$\mathrm{W m^{-2} nm^{-1}}$]', fontsize=10)
    ax4.set_xticklabels([], visible=False)

    width  = 180.0 # unit: second
    height = 0.6   # unit: Wm^{-2}nm^{-1}
    logic  = (xx>time_sec0-width/2.0) & (xx<=time_sec0+width/2.0)

    index0 = np.argmin(np.abs(xx-time_sec0))
    x0 = time_sec0 - width/2.0
    y0 = np.nanmean(yy_n[logic][yy_n[logic]>0.01]) - height/2.0
    ax4.add_patch(patches.Rectangle((x0, y0), width, height, fill=False, ec='g', lw=1.5))

    ax5.scatter(xx[logic], yy_n[logic], c='b', edgecolor='none', alpha=0.8, s=8)
    ax5.scatter(xx[logic], yy_z[logic], c='r', edgecolor='none', alpha=0.8, s=8)
    ax5.xaxis.set_major_locator(FixedLocator([time_sec0-width/2.0, time_sec0, time_sec0+width/2.0]))

    tmhr0 = time_sec0/3600.0
    ax5.axvline(time_sec0, color='k', ls=':', lw=1.0)
    ax5.set_xlim([x0, x0+width])
    ax5.set_ylim([y0, y0+height])

    ax5.set_xticklabels([], visible=False)
    ax5.spines['bottom'].set_color('g')
    ax5.spines['top'].set_color('g')
    ax5.spines['left'].set_color('g')
    ax5.spines['right'].set_color('g')
    ax5.tick_params(axis='x', colors='g')
    ax5.tick_params(axis='y', colors='g')

    ax4.set_title('SSFR (0.5$\mathrm{\mu m}$)', fontsize=14, y=0.8, x=0.05, ha='left')
    #}}}

    # kt-19
    #{{{
    time_sec, zenT, nadT = GDATA_KT19(init.fname_kt19)
    logic = (time_sec >= time_sec0-720.0) & (time_sec <= time_sec0+720.0)
    xx    = time_sec[logic]
    yy_z  = zenT[logic]
    yy_n  = nadT[logic]

    ax6.xaxis.set_major_locator(FixedLocator(time_sec0+np.arange(-720.0, 721.0, 180.0)))
    ax6.set_xticklabels(['UTC-0.2h', '', 'UTC-0.1h', '', 'UTC', '', 'UTC+0.1h', '', 'UTC+0.2h'])
    ax6.set_xlim([time_sec0-720.000001, time_sec0+720.000001])
    ax6.set_ylim([-20, 5])
    ax6.scatter(xx, yy_n, c='b', edgecolor='none', alpha=0.8, label='Nadir' , s=2)
    ax6.scatter(xx, yy_z, c='r', edgecolor='none', alpha=0.8, label='Zenith', s=2)
    ax6.axvline(time_sec0, linewidth=1.0, linestyle=':', color='k')
    ax6.set_ylabel('Temperature [$\mathrm{^\circ C}$]', fontsize=10)

    width  = 180.0 # unit: second
    height = 12.0   # unit: degree Celcius
    logic  = (xx>time_sec0-width/2.0) & (xx<=time_sec0+width/2.0)

    index0 = np.argmin(np.abs(xx-time_sec0))
    x0 = time_sec0 - width/2.0
    y0 = np.nanmean(yy_n[index0-100:index0+100]) - height/2.0
    ax6.add_patch(patches.Rectangle((x0, y0), width, height, fill=False, ec='g', lw=1.5))

    ax7.scatter(xx[logic], yy_n[logic], c='b', edgecolor='none', alpha=0.8, s=4)
    ax7.scatter(xx[logic], yy_z[logic], c='r', edgecolor='none', alpha=0.8, s=4)
    ax7.xaxis.set_major_locator(FixedLocator([time_sec0-width/2.0, time_sec0, time_sec0+width/2.0]))

    tmhr0 = time_sec0/3600.0
    ax7.set_xticklabels(['-0.05h', 'UTC', '+0.05h'])
    ax7.axvline(time_sec0, color='k', ls=':', lw=1.0)
    ax7.set_xlim([x0, x0+width])
    ax7.set_ylim([y0, y0+height])

    ax7.spines['bottom'].set_color('g')
    ax7.spines['top'].set_color('g')
    ax7.spines['left'].set_color('g')
    ax7.spines['right'].set_color('g')
    ax7.xaxis.label.set_color('g')
    ax7.yaxis.label.set_color('g')
    ax7.tick_params(axis='x', colors='g')
    ax7.tick_params(axis='y', colors='g')

    ax6.set_title('KT-19', fontsize=14, y=0.8, x=0.05, ha='left')

    fig.text(0.68, 0.408, '$\mathrm{F\\uparrow}$'  , fontsize=12, ha='center', backgroundcolor='b', color='white', alpha=0.8)
    fig.text(0.68, 0.454, '$\mathrm{F\downarrow}$', fontsize=12, ha='center', backgroundcolor='r', color='white', alpha=0.8)

    fig.text(0.68, 0.176, 'Nadir ', fontsize=12, ha='center', backgroundcolor='b', color='white')
    fig.text(0.68, 0.222, 'Zenith', fontsize=12, ha='center', backgroundcolor='r', color='white')

    fig.suptitle("%s UTC" % (dtime0.strftime('%Y-%m-%d %H:%M:%S')), fontsize=20, y=0.99)

    time_trk, lon_trk, lat_trk, alt_trk = GDATA_TRK(init.fname_trk)
    index = np.argmin(np.abs(time_trk - time_sec0))
    if time_trk[index]-time_sec0<1.0:
        lon_trk0 = lon_trk[index]
        lat_trk0 = lat_trk[index]
        alt_trk0 = alt_trk[index]

        fig.text(0.5, 0.93, '(%.4fh, %7.2f$^\circ$, %5.2f$^\circ$, %4dm)' % (time_sec0/3600.0, lon_trk0, lat_trk0, alt_trk0), fontsize=16, ha='center')

    fname_graph = '%s/join_%s.png' % (init.fdir_join_graph, dtime0_s)
    plt.savefig(fname_graph)
    print('%s is complete.' % fname_graph)
    plt.close(fig)

def PLT_JOIN_V1(statements, testMode=False):

    init, time_sec0 = statements

    dtime0    = init.date+datetime.timedelta(seconds=time_sec0)
    dtime0_s  = dtime0.strftime('%Y-%m-%d_%H:%M:%S')

    rcParams['font.size'] = 14
    fig = plt.figure(figsize=(12, 8))
    gs  = gridspec.GridSpec(7, 9)
    ax1 = plt.subplot(gs[0:3, 0:3])
    ax2 = plt.subplot(gs[0:3, 3:6])
    ax3 = plt.subplot(gs[0:3, 6:9])
    ax4 = plt.subplot(gs[3:5, :-3])
    ax5 = plt.subplot(gs[3:5, -2:])
    ax6 = plt.subplot(gs[5:7, :-3])
    ax7 = plt.subplot(gs[5:7, -2:])

    # flight track
    #{{{
    fnames = sorted(glob.glob('%s/*%s*.png' % (init.fdir_trk_graph, dtime0_s)))
    NFile  = len(fnames)
    ax1.axis('off')
    if NFile > 0:
        fname = fnames[0]
        image_data  = mpimg.imread(fname)
        ax1.imshow(image_data)
        ax1.set_title('Flight Track', fontsize=14)
    ax1.axis('off')
    #}}}

    # forward camera
    #{{{
    fnames_good = sorted(glob.glob('%s/*%s*_good.png' % (init.fdir_fcam_graph, dtime0_s)))
    Ngood       = len(fnames_good)
    fnames_fine = sorted(glob.glob('%s/*%s*_fine.png' % (init.fdir_fcam_graph, dtime0_s)))
    Nfine       = len(fnames_fine)
    fnames_okay = sorted(glob.glob('%s/*%s*_okay.png' % (init.fdir_fcam_graph, dtime0_s)))
    Nokay       = len(fnames_okay)
    if Ngood > 0:
        fname = fnames_good[0]
        ax2.set_title('Forward Camera', fontsize=14)
    elif Nfine > 0:
        fname = fnames_fine[0]
        ax2.set_title('Forward Camera', fontsize=14, color='red')
    elif Nokay > 0:
        fname = fnames_okay[0]
        ax2.set_title('Forward Camera', fontsize=14, color='darkred')
    else:
        fname = None

    if fname != None:
        image_data  = mpimg.imread(fname)
        ax2.imshow(image_data)

    ax2.axis('off')
    #}}}

    # nadir camera
    #{{{
    fnames_good = sorted(glob.glob('%s/*%s*_good.png' % (init.fdir_ncam_graph, dtime0_s)))
    Ngood       = len(fnames_good)
    fnames_fine = sorted(glob.glob('%s/*%s*_fine.png' % (init.fdir_ncam_graph, dtime0_s)))
    Nfine       = len(fnames_fine)
    fnames_okay = sorted(glob.glob('%s/*%s*_okay.png' % (init.fdir_ncam_graph, dtime0_s)))
    Nokay       = len(fnames_okay)
    if Ngood > 0:
        fname = fnames_good[0]
        ax3.set_title('Nadir Camera', fontsize=14)
    elif Nfine > 0:
        fname = fnames_fine[0]
        ax3.set_title('Nadir Camera', fontsize=14, color='red')
    elif Nokay > 0:
        fname = fnames_okay[0]
        ax3.set_title('Nadir Camera', fontsize=14, color='darkred')
    else:
        fname = None

    if fname != None:
        image_data  = mpimg.imread(fname)
        ax3.imshow(image_data)

    ax3.axis('off')
    #}}}

    # ssfr
    #{{{
    time_sec, spec_zen, spec_nad = GDATA_SSFR_NAT(init.fname_ssfr)
    logic = (time_sec >= time_sec0-720.0) & (time_sec <= time_sec0+720.0)
    xx    = time_sec[logic]
    yy_z  = spec_zen[logic]
    yy_n  = spec_nad[logic]
    ax4.xaxis.set_major_locator(FixedLocator(time_sec0+np.arange(-720.0, 721.0, 180.0)))
    ax4.set_xlim([time_sec0-720.000001, time_sec0+720.000001])
    ax4.set_ylim([-0.1, 1.2])
    ax4.scatter(xx, yy_n, c='b', edgecolor='none', alpha=0.8, label='Nadir' , s=5)
    ax4.scatter(xx, yy_z, c='r', edgecolor='none', alpha=0.8, label='Zenith', s=5)
    ax4.axvline(time_sec0, linewidth=1.0, linestyle=':', color='k')
    ax4.set_ylabel('Irradiance [$\mathrm{W m^{-2} nm^{-1}}$]')
    ax4.set_xticklabels([], visible=False)

    width  = 180.0 # unit: second
    height = 0.6   # unit: Wm^{-2}nm^{-1}
    logic  = (xx>time_sec0-width/2.0) & (xx<=time_sec0+width/2.0)

    index0 = np.argmin(np.abs(xx-time_sec0))
    x0 = time_sec0 - width/2.0
    y0 = np.nanmean(yy_n[logic][yy_n[logic]>0.01]) - height/2.0
    ax4.add_patch(patches.Rectangle((x0, y0), width, height, fill=False, ec='g', lw=1.5))

    ax5.scatter(xx[logic], yy_n[logic], c='b', edgecolor='none', alpha=0.8, s=8)
    ax5.scatter(xx[logic], yy_z[logic], c='r', edgecolor='none', alpha=0.8, s=8)
    ax5.xaxis.set_major_locator(FixedLocator([time_sec0-width/2.0, time_sec0, time_sec0+width/2.0]))

    tmhr0 = time_sec0/3600.0
    ax5.axvline(time_sec0, color='k', ls=':', lw=1.0)
    ax5.set_xlim([x0, x0+width])
    ax5.set_ylim([y0, y0+height])

    ax5.set_xticklabels([], visible=False)
    ax5.spines['bottom'].set_color('g')
    ax5.spines['top'].set_color('g')
    ax5.spines['left'].set_color('g')
    ax5.spines['right'].set_color('g')
    ax5.tick_params(axis='x', colors='g')
    ax5.tick_params(axis='y', colors='g')

    ax4.set_title('SSFR', fontsize=14, y=0.8, x=0.08)
    #}}}

    # kt-19
    #{{{
    time_sec, zenT, nadT = GDATA_KT19(init.fname_kt19)
    logic = (time_sec >= time_sec0-720.0) & (time_sec <= time_sec0+720.0)
    xx    = time_sec[logic]
    yy_z  = zenT[logic]
    yy_n  = nadT[logic]

    ax6.xaxis.set_major_locator(FixedLocator(time_sec0+np.arange(-720.0, 721.0, 180.0)))
    ax6.set_xticklabels(['UTC-0.2h', '', 'UTC-0.1h', '', 'UTC', '', 'UTC+0.1h', '', 'UTC+0.2h'])
    ax6.set_xlim([time_sec0-720.000001, time_sec0+720.000001])
    ax6.set_ylim([-20, 5])
    ax6.scatter(xx, yy_n, c='b', edgecolor='none', alpha=0.8, label='Nadir' , s=2)
    ax6.scatter(xx, yy_z, c='r', edgecolor='none', alpha=0.8, label='Zenith', s=2)
    ax6.axvline(time_sec0, linewidth=1.0, linestyle=':', color='k')
    ax6.set_ylabel('Temperature [$\mathrm{^\circ C}$]')

    width  = 180.0 # unit: second
    height = 12.0   # unit: degree Celcius
    logic  = (xx>time_sec0-width/2.0) & (xx<=time_sec0+width/2.0)

    index0 = np.argmin(np.abs(xx-time_sec0))
    x0 = time_sec0 - width/2.0
    y0 = np.nanmean(yy_n[index0-100:index0+100]) - height/2.0
    ax6.add_patch(patches.Rectangle((x0, y0), width, height, fill=False, ec='g', lw=1.5))

    ax7.scatter(xx[logic], yy_n[logic], c='b', edgecolor='none', alpha=0.8, s=4)
    ax7.scatter(xx[logic], yy_z[logic], c='r', edgecolor='none', alpha=0.8, s=4)
    ax7.xaxis.set_major_locator(FixedLocator([time_sec0-width/2.0, time_sec0, time_sec0+width/2.0]))

    tmhr0 = time_sec0/3600.0
    ax7.set_xticklabels(['-0.05h', 'UTC', '+0.05h'])
    ax7.axvline(time_sec0, color='k', ls=':', lw=1.0)
    ax7.set_xlim([x0, x0+width])
    ax7.set_ylim([y0, y0+height])

    ax7.spines['bottom'].set_color('g')
    ax7.spines['top'].set_color('g')
    ax7.spines['left'].set_color('g')
    ax7.spines['right'].set_color('g')
    ax7.xaxis.label.set_color('g')
    ax7.yaxis.label.set_color('g')
    ax7.tick_params(axis='x', colors='g')
    ax7.tick_params(axis='y', colors='g')

    ax6.set_title('KT-19', fontsize=14, y=0.8, x=0.08)
    #}}}


    fig.suptitle("%s UTC" % dtime0.strftime('%Y-%m-%d %H:%M:%S'), fontsize=20, y=0.99)

    time_trk, lon_trk, lat_trk, alt_trk = GDATA_TRK(init.fname_trk)
    index = np.argmin(np.abs(time_trk - time_sec0))
    if time_trk[index]-time_sec0<1.0:
        lon_trk0 = lon_trk[index]
        lat_trk0 = lat_trk[index]
        alt_trk0 = alt_trk[index]

        fig.text(0.5, 0.93, '(%7.2f$^\circ$, %5.2f$^\circ$, %4dm)' % (lon_trk0, lat_trk0, alt_trk0), fontsize=16, ha='center')

    fname_graph = '%s/join_%s.png' % (init.fdir_join_graph, dtime0_s)
    plt.savefig(fname_graph)
    print('%s is complete.' % fname_graph)
    plt.close(fig)

def MAIN_JOIN(init, time_sec_s, time_sec_e, ncpu=12):
    #{{{
    import multiprocessing as mp
    time_sec = np.arange(time_sec_s, time_sec_e+1)
    inits = [init]*time_sec.size

    pool = mp.Pool(processes=ncpu)
    pool.outputs = pool.map(PLT_JOIN, zip(inits, time_sec))
    pool.close()
    pool.join()
    #}}}

if __name__ == '__main__':
    import matplotlib as mpl
    mpl.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.gridspec as gridspec
    from matplotlib.ticker import FixedLocator
    from matplotlib import rcParams
    import matplotlib.image as mpimg
    import matplotlib.patches as patches
    from pre_vid import ANIM_INIT

    # --- 2014-09-10 ---
    #  date = datetime.datetime(2014, 9, 10)
    #  init = ANIM_INIT(date)
    #  time_sec_s = (19.0+ 5.0/60.0)*3600.0
    #  time_sec_e = (23.0+55.0/60.0)*3600.0
    #  MAIN_JOIN(init, time_sec_s, time_sec_e, ncpu=12)

    # --- 2014-09-11 ---
    date = datetime.datetime(2014, 9, 11)
    init = ANIM_INIT(date)
    time_sec_s = (20.0 + 30.0/60.0)*3600.0
    time_sec_e = (23.0 + 0.0/60.0)*3600.0
    MAIN_JOIN(init, time_sec_s, time_sec_e, ncpu=14)

    # --- 2014-09-13 ---
    date = datetime.datetime(2014, 9, 13)
    init = ANIM_INIT(date)
    time_sec_s = (19.0 + 30.0/60.0)*3600.0
    time_sec_e = (23.0 + 0.0/60.0)*3600.0
    MAIN_JOIN(init, time_sec_s, time_sec_e, ncpu=14)
    exit()

    # --- 2014-09-21 ---
    #  date = datetime.datetime(2014, 9, 21)
    #  init = ANIM_INIT(date)
    #  time_sec_s = (18.0+30.0/60.0)*3600.0
    #  time_sec_e = (23.0+10.0/60.0)*3600.0
    #  MAIN_JOIN(init, time_sec_s, time_sec_e, ncpu=12)

    # --- 2014-09-24 ---
    #  date = datetime.datetime(2014, 9, 24)
    #  init = ANIM_INIT(date)
    #  time_sec_s = (21.0+10.0/60.0)*3600.0
    #  time_sec_e = (24.0+50.0/60.0)*3600.0
    #  MAIN_JOIN(init, time_sec_s, time_sec_e, ncpu=12)

    # --- 2014-10-02 ---
    # date = datetime.datetime(2014, 10, 2)
    # init = ANIM_INIT(date)
    # time_sec_s = (24.0)*3600.0
    # time_sec_e = (28.0)*3600.0
    # MAIN_JOIN(init, time_sec_s, time_sec_e, ncpu=12)

    # ============= one frame test ===============
    # date = datetime.datetime(2014, 9, 13)
    # init = ANIM_INIT(date)
    # PLT_JOIN([init, 22.5*3600.0], testMode=True)
    # exit()
    # ============================================
