import os
import datetime
import glob
import h5py

class ANIM_INIT:

    def __init__(self, date, local_dir='/argus/home/chen/work/01_anim/new/data'):

        self.date   = date
        self.date_s = date.strftime('%Y-%m-%d')

        # main directory
        self.fdir = '%s/%s' % (local_dir, self.date_s)

        # sub-main directory
        self.fdir_trk  = '%s/trk'  % self.fdir
        self.fdir_cam  = '%s/cam'  % self.fdir
        self.fdir_ssfr = '%s/ssfr' % self.fdir
        self.fdir_kt19 = '%s/kt19' % self.fdir
        self.fdir_join = '%s/join' % self.fdir
        self.fdir_vid  = '%s/vid' % self.fdir

        # sub-main graph directory
        self.fdir_fcam_graph     = '%s/graph/forward'     % self.fdir_cam
        self.fdir_ncam_graph     = '%s/graph/nadir'       % self.fdir_cam
        self.fdir_trk_graph      = '%s/graph'             % self.fdir_trk
        self.fdir_ssfr_graph     = '%s/graph'             % self.fdir_ssfr
        self.fdir_kt19_graph     = '%s/graph'             % self.fdir_kt19
        self.fdir_join_graph     = '%s/graph'             % self.fdir_join
        self.fdir_vid_graph      = '%s/graph'             % self.fdir_vid

        # sub-main data directory
        self.fdir_trk_data   = '%s/data'  % self.fdir_trk
        self.fdir_ssfr_data  = '%s/data'  % self.fdir_ssfr
        self.fdir_kt19_data  = '%s/data'  % self.fdir_kt19

        # create directories
        if os.path.exists(self.fdir):
            print('Warning [ANIM_INIT]: %s already exists!' % self.fdir)
            self.fname_ssfr      = '%s/ssfr.out' % self.fdir_ssfr_data
            self.fname_kt19      = '%s/temp.txt' % self.fdir_kt19_data
            self.fname_trk       = '%s/trk.hsk'  % self.fdir_trk_data
            self.fname_map       = '%s/map.h5'   % self.fdir_trk_data
            self.fname_map_tiff  = '%s/map.tiff'   % self.fdir_trk_data
        else:
            print('Message [ANIM_INIT]: creating directories...')
            os.system('mkdir -p %s' % self.fdir)
            os.system('mkdir -p %s' % self.fdir_trk)
            os.system('mkdir -p %s' % self.fdir_cam)
            os.system('mkdir -p %s' % self.fdir_ssfr)
            os.system('mkdir -p %s' % self.fdir_kt19)
            os.system('mkdir -p %s' % self.fdir_join)
            os.system('mkdir -p %s' % self.fdir_vid)

            os.system('mkdir -p %s' % self.fdir_fcam_graph)
            os.system('mkdir -p %s' % self.fdir_ncam_graph)
            os.system('mkdir -p %s' % self.fdir_trk_graph)
            os.system('mkdir -p %s' % self.fdir_ssfr_graph)
            os.system('mkdir -p %s' % self.fdir_kt19_graph)
            os.system('mkdir -p %s' % self.fdir_join_graph)
            os.system('mkdir -p %s' % self.fdir_vid_graph)

            os.system('mkdir -p %s' % self.fdir_trk_data)
            os.system('mkdir -p %s' % self.fdir_ssfr_data)
            os.system('mkdir -p %s' % self.fdir_kt19_data)
            print('Message [ANIM_INIT]: directories created.')
            print('Please add data into corresponding directory manually...')
            print('--------------------------------------------------------')
            print('file name of trk.hsk under %s;' % self.fdir_trk_data)
            print('file name of map.tiff under %s;' % self.fdir_trk_data)
            print('file name of ssfr.out under %s;' % self.fdir_ssfr_data)
            print('file name of temp.txt under %s;' % self.fdir_kt19_data)
            print('--------------------------------------------------------')
            print('and then rerun this program.')
            exit()

def MAIN_TEST(init, dtime_s, dtime_e):

    index  = 1
    while dtime_s <= dtime_e:
        dtime_s += datetime.timedelta(seconds=1)
        index  += 1

        time_stamp0 = dtime_s.strftime('%Y-%m-%d-%H-%M-%S')

        N_ssfr    = len(glob.glob('%s/*%s*.png' % (init.fdir_ssfr_graph, time_stamp0)))
        N_forward = len(glob.glob('%s/*%s*.png' % (init.fdir_fcam_graph, time_stamp0)))
        N_nadir   = len(glob.glob('%s/*%s*.png' % (init.fdir_ncam_graph, time_stamp0)))
        N_track   = len(glob.glob('%s/*%s*.png' % (init.fdir_trk_graph , time_stamp0)))

        if (N_forward!=1) | (N_nadir!=1) | (N_track!=1) | (N_ssfr!=1):
            print(index, time_stamp0)
            print(N_forward, N_nadir, N_track, N_ssfr)
            print('-'*66)

def MAIN_VIDEO(init, dtime_s, dtime_e, format_str='yuv420p', frame_rate=30):

    time_stamp_s = dtime_s.strftime('%Y-%m-%d_%H:%M:%S')
    time_stamp_e = dtime_e.strftime('%Y-%m-%d_%H:%M:%S')
    os.system("ffmpeg -loglevel quiet -y -framerate %d -pattern_type glob -i '%s/*.png' -vf scale=1920:1080 -c:v libx264 -pix_fmt %s %s_%s.mp4" % (frame_rate, init.fdir_join_graph, format_str, time_stamp_s, time_stamp_e))
    exit()

    N = len(glob.glob('%s/*.png' % init.fdir_vid_graph))
    if N > 0:
        os.system('rm -rf %s' % init.fdir_vid_graph)
        os.system('mkdir -p %s' % init.fdir_vid_graph)

    N0 = 0
    while dtime_s <= dtime_e:
        time_stamp = dtime_s.strftime('%Y-%m-%d_%H:%M:%S')
        os.system('cp %s/*%s*.png %s/' % (init.fdir_join_graph, time_stamp, init.fdir_vid_graph))
        N0 += 1
        dtime_s += datetime.timedelta(seconds=1)

    N00 = len(glob.glob('%s/*.png' % init.fdir_vid_graph))
    if N0 == N00:
        #os.system("ffmpeg -loglevel quiet -framerate 30 -pattern_type glob -i '%s/*.png' -c:v libx264 -pix_fmt %s %s_%s.mp4" % (init.fdir_vid_graph, format_str, time_stamp_s, time_stamp_e))
        os.system("ffmpeg -loglevel quiet -y -framerate 30 -pattern_type glob -i '%s/*.png' -vf scale=1920:1080 -c:v libx264 -pix_fmt %s %s_%s.mp4" % (init.fdir_vid_graph, format_str, time_stamp_s, time_stamp_e))


if __name__ == '__main__':

    #date = datetime.datetime(2014, 9, 4)
    #date = datetime.datetime(2014, 9, 7)
    #date = datetime.datetime(2014, 9, 9)
    #date = datetime.datetime(2014, 9, 16)
    #date = datetime.datetime(2014, 9, 17)
    #date = datetime.datetime(2014, 9, 19)

    # --- 2014-09-10 ---
    #  date = datetime.datetime(2014, 9, 10)
    #  init = ANIM_INIT(date)
    #  dtime_s = datetime.datetime(2014, 9, 10, 19,  5, 0)
    #  dtime_e = datetime.datetime(2014, 9, 10, 23, 55, 0)
    #  MAIN_VIDEO(init, dtime_s, dtime_e, format_str='yuv420p')

    # --- 2014-09-21 ---
    #  date = datetime.datetime(2014, 9, 21)
    #  init = ANIM_INIT(date)
    #  dtime_s = datetime.datetime(2014, 9, 21, 18, 30, 0)
    #  dtime_e = datetime.datetime(2014, 9, 21, 23, 10, 0)
    #  MAIN_VIDEO(init, dtime_s, dtime_e, format_str='yuv420p')

    # --- 2014-09-24 ---
    #  date = datetime.datetime(2014, 9, 24)
    #  init = ANIM_INIT(date)
    #  dtime_s = datetime.datetime(2014, 9, 24, 21, 10, 0)
    #  dtime_e = datetime.datetime(2014, 9, 25,  0, 50, 0)
    #  MAIN_VIDEO(init, dtime_s, dtime_e, format_str='yuv420p')

    # --- 2014-10-02 ---
    date = datetime.datetime(2014, 10, 2)
    init = ANIM_INIT(date)
    dtime_s = datetime.datetime(2014, 10, 3, 1, 0, 0)
    dtime_e = datetime.datetime(2014, 10, 3, 1, 33, 36)
    MAIN_VIDEO(init, dtime_s, dtime_e, format_str='yuv420p', frame_rate=60)
    exit()

    # --- 2014-09-11 ---
    # date = datetime.datetime(2014, 9, 11)
    # init = ANIM_INIT(date)
    # dtime_s = datetime.datetime(2014, 9, 11, 20, 30, 0)
    # dtime_e = datetime.datetime(2014, 9, 11, 23, 0, 0)
    # MAIN_VIDEO(init, dtime_s, dtime_e, format_str='yuv420p')

    # --- 2014-09-13 ---
    # date = datetime.datetime(2014, 9, 13)
    # init = ANIM_INIT(date)
    # dtime_s = datetime.datetime(2014, 9, 13, 19, 30, 0)
    # dtime_e = datetime.datetime(2014, 9, 13, 23, 0, 0)
    # MAIN_VIDEO(init, dtime_s, dtime_e, format_str='yuv420p')

    #+++++++++++++++++++ test ++++++++++++++++++
    #MAIN_TEST(init, dtime_s, dtime_e)
    #-------------------------------------------
