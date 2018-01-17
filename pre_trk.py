import os
import numpy as np
import h5py
import datetime
import multiprocessing as mp

def XY2LONLAT(x, y, a=6378137.0, e=0.08181919, phi_c_deg=70.0, lambda_0_deg=-45.0):

    """
    This is a Python version of the MATLAB code from
    https://www.mathworks.com/matlabcentral/fileexchange/32907-polar-stereographic-coordinate-transformation--map-to-lat-lon-?
    Courtesy to Andy Bliss

    Written by Hong Chen (me@hongchen.cz)
    """

    phi_c_rad    = np.deg2rad(phi_c_deg)
    lambda_0_rad = np.deg2rad(lambda_0_deg)

    if phi_c_rad < 0.0:
        pm           = -1
        phi_c_rad    = -phi_c_rad
        lambda_0_rad = -lambda_0_rad
        x            = -x
        y            = -y
    else:
        pm = 1

    t_c = np.tan(np.pi/4.0 - phi_c_rad/2.0)/((1.0-e*np.sin(phi_c_rad))/(1.0+e*np.sin(phi_c_rad)))**(e/2.0)
    m_c = np.cos(phi_c_rad)/np.sqrt(1.0-e**2.0*(np.sin(phi_c_rad))**2.0)
    rho = np.sqrt(x**2.0+y**2.0)
    t   = rho*t_c/(a*m_c)

    chi = np.pi/2.0 - 2.0 * np.arctan(t)

    phi = chi + (e**2.0/2.0 + 5.0*e**4.0/24.0 + e**6.0/12.0 + 13.0*e**8.0/360.0)*np.sin(2.0*chi) \
              + (7.0*e**4.0/48.0 + 29.0*e**6.0/240.0 + 811.0*e**8.0/11520.0)*np.sin(4.0*chi) \
              + (7.0*e**6.0/120.0+81.0*e**8.0/1120.0)*np.sin(6.0*chi) \
              + (4279.0*e**8.0/161280.0)*np.sin(8.0*chi)

    lambda_rad = lambda_0_rad + np.arctan2(x, -y)
    phi_rad    = pm*phi
    lambda_rad = pm*lambda_rad
    lambda_rad = np.mod(lambda_rad+np.pi,2.0*np.pi)-np.pi

    phi_deg    = np.rad2deg(phi_rad)
    lambda_deg = np.rad2deg(lambda_rad)

    return lambda_deg, phi_deg

def GDATA_MAP_TIFF(fname):

    import gdal
    map_image = gdal.Open(fname)
    map_data   = map_image.ReadAsArray()
    map_width  = map_image.RasterXSize
    map_height = map_image.RasterYSize
    map_geo    = map_image.GetGeoTransform()

    XX0, YY0 = np.meshgrid(np.arange(map_width+1), np.arange(map_height+1))

    X0 = map_geo[0] + map_geo[1]*XX0  + map_geo[2]*YY0
    Y0 = map_geo[3] + map_geo[4]*XX0  + map_geo[5]*YY0

    x  = (X0[0, 1:] + X0[0, :-1])/2.0
    y  = (Y0[1:, 0] + Y0[:-1, 0])/2.0
    X, Y = np.meshgrid(x, y)

    lon, lat = XY2LONLAT(X, Y)
    rgb      = np.swapaxes(np.swapaxes(map_data, 0, 2), 0, 1)

    return lon, lat, rgb

def CDATA_MAP_H5(fname_tiff, fname_h5):

    lon, lat, rgb = GDATA_MAP_TIFF(fname_tiff)
    f = h5py.File(fname_h5, 'w')
    f['lon'] = lon
    f['lat'] = lat
    f['rgb'] = rgb
    f.close()

def GDATA_TRK(fname, skip_header=66):

    track_data = np.genfromtxt(fname, delimiter=',', skip_header=skip_header)

    time_sec = track_data[:, 0]
    lon      = track_data[:, 3]
    lat      = track_data[:, 2]
    alt      = track_data[:, 4]

    logic = (lat<-90.0)|(lat>90.0)|(lon<-180.0)|(lon>180.0)
    lon[logic] = np.nan
    lat[logic] = np.nan
    return time_sec, lon, lat, alt

def TIME_STAMP_TRK(delta_second, dtime0=datetime.datetime(2014, 9, 19, 0, 0, 0)):

    time  = dtime0 + datetime.timedelta(seconds=delta_second)
    time_stamp = time.strftime('%Y-%m-%d-%H-%M-%S')

    return time_stamp

class PLT_TRK_MAP:

    def __init__(self, statements, Nloc_inset=4, testMode=False):

        init, time_sec_s, time_sec_e = statements
        self.Nloc = Nloc_inset
        self.testMode = testMode
        if init.date_s == '2014-09-04':
            lon0 = -149.5
            lat0 = 69.7
            width0  = 800000.0
            height0 = 1200000.0
            meridians = np.arange(-180, 181, 4)
            parallels = np.arange(-90 , 91 , 2)
        elif init.date_s == '2014-09-07':
            lon0 = -144.5
            lat0 = 73.4
            width0  = 800000.0
            height0 = 800000.0
            meridians = np.arange(-180, 181, 4)
            parallels = np.arange(-90 , 91 , 2)
        elif init.date_s == '2014-09-09':
            lon0 = -142.5
            lat0 = 73.0
            width0  = 500000.0
            height0 = 620000.0
            meridians = np.arange(-180, 181, 4)
            parallels = np.arange(-90 , 91 , 1)
        elif init.date_s == '2014-09-10':
            lon0 = -138.0
            lat0 = 75.0
            width0  = 800000.0
            height0 = 800000.0
            meridians = np.arange(-180, 181, 4)
            parallels = np.arange(-90 , 91 , 1)
        elif init.date_s == '2014-09-11':
            lon0 = -134.0
            lat0 = 72.8
            width0  = 500000.0
            height0 = 500000.0
            meridians = np.arange(-180, 181, 4)
            parallels = np.arange(-90 , 91 , 1)
        elif init.date_s == '2014-09-13':
            lon0 = -134.0
            lat0 = 72.8
            width0  = 500000.0
            height0 = 500000.0
            meridians = np.arange(-180, 181, 4)
            parallels = np.arange(-90 , 91 , 1)
        elif init.date_s == '2014-09-16':
            lon0 = -140
            lat0 = 73.8
            width0  = 870000.0
            height0 = 870000.0
            meridians = np.arange(-180, 181, 6)
            parallels = np.arange(-90, 91, 2)
        elif init.date_s == '2014-09-17':
            lon0 = -153
            lat0 = 72.4
            width0  = 670000.0
            height0 = 670000.0
            meridians = np.arange(-180, 181, 4)
            parallels = np.arange(-90, 91, 2)
        elif init.date_s == '2014-09-19':
            lon0 = -137.5
            lat0 = 71.0
            width0  = 770000.0
            height0 = 770000.0
            meridians = np.arange(-180, 181, 4)
            parallels = np.arange(-90, 91, 2)
        elif init.date_s == '2014-09-21':
            lon0 = -134.0
            lat0 = 73.0
            width0  = 850000.0
            height0 = 850000.0
            meridians = np.arange(-180, 181, 4)
            parallels = np.arange(-90, 91, 2)
        elif init.date_s == '2014-09-24':
            lon0 = -134.0
            lat0 = 71.0
            width0  = 850000.0
            height0 = 850000.0
            meridians = np.arange(-180, 181, 4)
            parallels = np.arange(-90, 91, 2)
        elif init.date_s == '2014-10-02':
            lon0 = -159.0
            lat0 = 58.8
            width0  = 660000.0
            height0 = 660000.0
            meridians = np.arange(-180, 181, 4)
            parallels = np.arange(-90, 91, 2)
            Nloc_inset=2

        #++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        self.time_trk, self.lon_trk, self.lat_trk, alt_trk = GDATA_TRK(init.fname_trk)
        self.alt_trk = alt_trk / 1000.0
        #--------------------------------------------------------

        #++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        f = h5py.File(init.fname_map, 'r')
        lon_map = (f['lon'][...]).ravel()
        lat_map = (f['lat'][...]).ravel()
        rgb_map = ((f['rgb'][...]).reshape([-1, 3])/255.0)
        f.close()
        #--------------------------------------------------------

        self.fig = plt.figure(figsize=(6.3, 6))
        self.ax  = self.fig.add_subplot(111)
        self.m = Basemap(projection = 'stere',
                         lon_0  = lon0,
                         lat_0  = lat0,
                         width  = width0,
                         height = height0,
                         resolution = 'c',
                         fix_aspect = False,
                         ax = self.ax
                        )

        self.m.drawmeridians(meridians, labels=[0, 0, 0, 1], color='k', linewidth=0.8)
        self.m.drawparallels(parallels, labels=[1, 1, 0, 0], color='k', linewidth=0.8)

        x, y = self.m(lon_map, lat_map)
        logic = (x >= self.m.xmin-1) & (x <= self.m.xmax+1) & (y >= self.m.ymin-1) & (y <= self.m.ymax+1)
        lon_map = lon_map[logic]
        lat_map = lat_map[logic]
        rgb_map = rgb_map[logic, :]

        x, y = self.m(lon_map, lat_map)
        self.m.scatter(x, y, c=rgb_map, s=1.0, edgecolor='none')
        x, y = self.m(self.lon_trk, self.lat_trk)
        self.m.scatter(x[::10], y[::10], c='red', s=3, alpha=0.05)

        for self.time_sec0 in range(int(time_sec_s), int(time_sec_e)):
            self.index0= np.argmin(np.abs(self.time_trk-self.time_sec0))
            self.time0 = self.time_trk[self.index0]
            self.alt0  = self.alt_trk[self.index0]
            self.lon0  = self.lon_trk[self.index0]
            self.lat0  = self.lat_trk[self.index0]

            if abs(self.time0-self.time_sec0)<1.0:
                self.LOOP(init)

        plt.close(self.fig)

    def LOOP(self, init):

        ax0 = inset_axes(self.ax, width=2.5, height=1.33, loc=self.Nloc)
        ax0.patch.set_alpha(0.6)
        ax0.get_xaxis().set_visible(False)
        ax0.get_yaxis().set_visible(False)
        for spine in ax0.spines.values():
            spine.set_visible(False)

        ax1 = inset_axes(ax0, width='82%', height='72%', loc=9)
        ax1.patch.set_alpha(0.0)
        ax1.tick_params(axis='both', which='major', labelsize=10, direction='in')

        logic = (self.time_trk>=self.time_sec0-720.0) & (self.time_trk<=self.time_sec0+720.0)
        xx    = self.time_trk[logic]
        yy    = self.alt_trk[logic]

        ax1.xaxis.set_major_locator(FixedLocator(self.time_sec0+np.arange(-720, 721, 180)))
        ax1.set_xticklabels(['-0.2h', '', '', '', 'UTC', '', '', '', '+0.2h'])
        ax1.set_xlim([self.time_sec0-720.000001, self.time_sec0+720.000001])
        ax1.yaxis.set_major_locator(FixedLocator(np.arange(0, 9, 1)))
        if self.alt0-2.0 < 0.0:
            ax1.set_ylim([0, 4])
        else:
            ax1.set_ylim([self.alt0-2.0, self.alt0+2.0])
        ax1.axvline(self.time_sec0, color='k', linestyle=':', lw=1.0)
        ax1.plot(xx, yy, color='b', lw=0, marker='o', markersize=0.8, markeredgecolor='none', alpha=0.1)

        logic = (xx<=self.time_sec0)
        xx_r  = xx[logic]
        yy_r  = yy[logic]
        ax1.plot(xx_r, yy_r, color='b', lw=0, marker='o', markersize=0.8, markeredgecolor='none')
        ax1.plot(self.time0, self.alt0, marker='o', markerfacecolor='blue', markersize=5, markeredgecolor='none')

        x, y = self.m(self.lon_trk[:self.index0], self.lat_trk[:self.index0])
        self.m.plot(x, y, linewidth=0, marker='o', markeredgecolor='none', markersize=0.8, color='r')
        x, y = self.m(self.lon0, self.lat0)
        self.m.plot(x, y, linewidth=0, marker='o', markeredgecolor='none', markersize=6  , color='r')

        if self.testMode:
            plt.show()
            exit()

        dtime0   = init.date+datetime.timedelta(seconds=self.time_sec0)
        dtime0_s = dtime0.strftime('%Y-%m-%d_%H:%M:%S')
        fname = '%s/trk_map_%s.png' % (init.fdir_trk_graph, dtime0_s)
        plt.savefig(fname)
        print('%s is complete.' % fname)
        self.fig.axes[-1].remove()
        self.fig.axes[-1].remove()
        self.ax.lines[-1].remove()
        self.ax.lines[-1].remove()

def MAIN_TRK_MAP(init, time_sec_s, time_sec_e, ncpu=8):

    time_sec = np.arange(time_sec_s, time_sec_e+2)
    N           = time_sec.size // ncpu
    time_sec_s0 = np.array([])
    time_sec_e0 = np.array([])
    index_s  = 0
    while index_s < time_sec.size-1:
        index_e = index_s + N
        if index_e>time_sec.size-1:
            index_e = time_sec.size-1
        time_sec_s0 = np.append(time_sec_s0, time_sec[index_s])
        time_sec_e0 = np.append(time_sec_e0, time_sec[index_e])

        index_s += N

    inits = [init] * time_sec_s0.size
    mp_statements = zip(inits, time_sec_s0, time_sec_e0)

    pool = mp.Pool(processes=ncpu)
    pool.outputs = pool.map(PLT_TRK_MAP, mp_statements)
    pool.close()
    pool.join()

def TEST_TRK_MAP(init, plt_trk=False):

    time_trk, lon_trk, lat_trk, alt_trk = GDATA_TRK(init.fname_trk)
    alt_trk = alt_trk / 1000.0
    if plt_trk:
        fig = plt.figure(figsize=(10, 4))
        ax1 = fig.add_subplot(121)
        cs1 = ax1.scatter(lon_trk, lat_trk, s=3, c=time_trk/3600.0, cmap='nipy_spectral')
        plt.colorbar(cs1)

        ax2 = fig.add_subplot(122)
        m = Basemap(projection='npstere',boundinglat=55,lon_0=315,resolution='l')
        m.drawcoastlines(linewidth=0.1)
        lon, lat = m(lon_trk, lat_trk)
        cs1 = ax2.scatter(lon, lat, s=3, c=time_trk/3600.0, cmap='nipy_spectral')
        plt.show()
        exit()

if __name__ == '__main__':

    import matplotlib as mpl
    # mpl.use('Agg')
    import matplotlib.pyplot as plt
    from mpl_toolkits.basemap import Basemap
    from matplotlib import rcParams
    from matplotlib.ticker import FixedLocator
    from mpl_toolkits.axes_grid1.inset_locator import inset_axes
    from pre_vid import ANIM_INIT

    # date = datetime.datetime(2014, 9, 4)  # done
    # date = datetime.datetime(2014, 9, 7)  # done
    # date = datetime.datetime(2014, 9, 9)  # done
    # date = datetime.datetime(2014, 9, 10) # done
    # date = datetime.datetime(2014, 9, 11) # doing
    date = datetime.datetime(2014, 9, 13) # doing
    # date = datetime.datetime(2014, 9, 16) # done
    # date = datetime.datetime(2014, 9, 17) # done
    # date = datetime.datetime(2014, 9, 19) # done
    # date = datetime.datetime(2014, 9, 21) # doing
    # date = datetime.datetime(2014, 9, 24) # doing
    # date = datetime.datetime(2014, 10, 2) # doing
    # date = datetime.datetime(2014, 10, 4) # doing

    init = ANIM_INIT(date)

    # ============= test map track ================
    # step 1.a: find where to crop on NASA WorldView
    # TEST_TRK_MAP(init, plt_trk=True)
    # exit()

    # step 1.b: go to NASA WorldView and crop the region and save the image in GeoTIFF format.

    # step 1.c: upload the GeoTIFF file to the "trk" directory as "map.tiff"

    # step 1.d: convert "map.tiff" to "map.h5"
    # CDATA_MAP_H5(init.fname_map_tiff, init.fname_map)
    # exit()

    # step 1.e: find a good map center and map range and location for the altitude plot
    plt  = PLT_TRK_MAP([init, 19.8333*3600.0, 23.99*3600.0], Nloc_inset=4, testMode=True)
    exit()
    # =============================================

    #  time_sec_s = (19.0+35.0/60.0)*3600.0
    #  time_sec_e = (23.0+50.0/60.0)*3600.0
    #  time_sec_s = (23.0+50.0/60.0)*3600.0
    #  time_sec_e = (24.0+50.0/60.0)*3600.0
    #  time_sec_s = (18.48)*3600.0
    #  time_sec_e = (18.49)*3600.0
    #  time_sec_s = (22.98)*3600.0
    #  time_sec_e = (22.99)*3600.0
    #  time_sec_s = (19.0+ 5.0/60.0)*3600.0
    #  time_sec_e = (23.0+55.0/60.0)*3600.0
    #  time_sec_s = (18.0+30.0/60.0)*3600.0
    #  time_sec_e = (23.0+10.0/60.0)*3600.0
    #  time_sec_s = (21.0+10.0/60.0)*3600.0
    #  time_sec_e = (24.0+50.0/60.0)*3600.0
    time_sec_s = (19.5)*3600.0
    time_sec_e = (23.0)*3600.0

    MAIN_TRK_MAP(init, time_sec_s, time_sec_e, ncpu=12)
    exit()
