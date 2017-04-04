import os
import numpy as np
import glob
import datetime
from PIL import Image
from pytesseract import image_to_string

def AVI2PNG(fname_avi, fdir_out_png, fps=2, verbose=False):

    if os.path.isdir(fdir_out_png):
        if verbose:
            print('Warning [AVI2PNG]: %s already exists!' % (fdir_out_png))
            print('Warning [AVI2PNG]: deleting all files under %s ...' % (fdir_out_png))
        os.system('rm -rf %s/*' % (fdir_out_png))
    else:
        if verbose:
            print('Message [AVI2PNG]: creating %s ...' % (fdir_out_png))
        os.system('mkdir -p %s' % (fdir_out_png))

    os.system('ffmpeg -loglevel quiet -i %s -vf fps=%d %s/%%07d.png' % (fname_avi, fps, fdir_out_png))

    N = len(glob.glob('%s/*png' % fdir_out_png))

    if N > 0:
        print 'Message [AVI2PNG]: %s conversion [AVI->PNG] is complete.' % (fname_avi)
    else:
        print 'Error [AVI2PNG]: %s cannot be converted.' % (fname_avi)

def GTIME_IMAGE(fname, cropRegion, upscaleN=20, iterN=4):
    img = Image.open(fname)
    img = img.crop(cropRegion)
    width, height = img.size
    for i in xrange(iterN):
        img = img.convert('L')
        img = img.resize((width*upscaleN, height*upscaleN), Image.BICUBIC)

    img    = img.convert('L')
    img    = img.resize((width*upscaleN, height*upscaleN), Image.ANTIALIAS)
    string = image_to_string(img, config='digits')
    return string

def RENAME_PNG(fdir_in, fdir_out, cropRegion, dtime_s, fps=2):

    fnames = sorted(glob.glob('%s/*.png' % fdir_in))
    NFile  = len(fnames)

    jday_fps_ref = np.zeros(NFile, dtype=np.float64) # Julian Day calculated from FPS (frame per second)
    jday_ocr_tmp = np.zeros(NFile, dtype=np.float64) # Julian Day from OCR by tesseract (tmp)

    # first iteration to get time stamp from OCR
    for i in range(NFile):
        jday_fps_ref[i] = ((dtime_s + datetime.timedelta(seconds=1.0/fps*i)) - datetime.datetime(1, 1, 1)).total_seconds() / 86400.0 + 1.0

        fname     = fnames[i]
        rawString = GTIME_IMAGE(fname, cropRegion)
        newString = rawString.replace(' ', '')
        try:
            dtime = datetime.datetime.strptime(newString, '%Y-%m-%d%H:%M:%S')
            jday_ocr_tmp[i] = (dtime-datetime.datetime(1, 1, 1)).total_seconds() / 86400.0 + 1.0
        except ValueError:
            jday_ocr_tmp[i] = np.nan

    import h5py
    f = h5py.File('test.h5', 'w')
    f['jday_fps_ref'] = jday_fps_ref
    f['jday_ocr_tmp'] = jday_ocr_tmp
    f.close()

    import matplotlib.pyplot as plt
    plt.plot(np.arange(NFile), jday_ocr_tmp)
    plt.show()

    exit()

    fnames_new = []
    for fname in fnames:
        rawString = GTIME_IMAGE(fname, cropRegion)
        newString = rawString.replace(' ', '')

        time_s = newString
        try:
            dtime = datetime.datetime.strptime('%s %s' % (date_s, time_s), '%Y-%m-%d %H:%M:%S')
            fname_new = '%s/%7.7d_%s_%s_fine.png' % (fdir_out, startN, date_s, newString)
            # re-check good
            if len(fnames_new)>=1 and ('bad' not in fnames_new[-1]):
                time_s0 = fnames_new[-1].split('_')[-2]
                dtime0  = datetime.datetime.strptime('%s %s' % (date_s, time_s0), '%Y-%m-%d %H:%M:%S')
                if (dtime-dtime0).total_seconds() in [0, 1]:
                    fname_new = '%s/%7.7d_%s_%s_good.png' % (fdir_out, startN, date_s, newString)

        except ValueError:
            fname_new = '%s/%7.7d_%s_bad.png' % (fdir_out, startN, date_s)

        # save some bad
        if 'bad' in fname_new and len(fnames_new)>2:
            if ('bad' not in fnames_new[-1]) and ('bad' not in fnames_new[-2]):
                time_s1 = fnames_new[-1].split('_')[-2]
                time_s2 = fnames_new[-2].split('_')[-2]
                if time_s1 == time_s2:
                    dtime0 = datetime.datetime.strptime('%s %s' % (date_s, time_s1), '%Y-%m-%d %H:%M:%S')
                    newString = (dtime0+datetime.timedelta(seconds=1)).strftime('%H:%M:%S')
                else:
                    dtime0 = datetime.datetime.strptime('%s %s' % (date_s, time_s1), '%Y-%m-%d %H:%M:%S')
                    newString = dtime0.strftime('%H:%M:%S')
                fname_new = '%s/%7.7d_%s_%s_okay.png' % (fdir_out, startN, date_s, newString)

        os.system('cp %s %s' % (fname, fname_new))

        startN += 1
        fnames_new.append(fname_new)
    return startN

def MAIN_CAM(init, dtime_s, dtime_e, fdir_cam_data='/argus/field/arise/video'):

    fnames_n_all = sorted(glob.glob('%s/Nadir*.avi' % (fdir_cam_data)))
    fnames_n = []
    for fname in fnames_n_all:
        dtime_str = fname[-23:-4]
        dtime     = datetime.datetime.strptime(dtime_str, '%Y-%m-%d-%H-%M-%S')
        if (dtime >= dtime_s) and (dtime <= dtime_e):
            fnames_n.append(fname)

    fnames_f = []
    fnames_f_all = sorted(glob.glob('%s/Forward*.avi' % (fdir_cam_data)))
    for fname in fnames_f_all:
        dtime_str = fname[-23:-4]
        dtime     = datetime.datetime.strptime(dtime_str, '%Y-%m-%d-%H-%M-%S')
        if (dtime >= dtime_s) and (dtime <= dtime_e):
            fnames_f.append(fname)

    # use ffmpeg to convert AVI video to PNG image
    for fname in fnames_n:
        dtime_str      = fname[-23:-4]
        dtime          = datetime.datetime.strptime(dtime_str, '%Y-%m-%d-%H-%M-%S')
        filename       = fname.split('/')[-1][:-4]
        fdir_out_png   = '%s/%s' % (init.fdir_ncam_graph, filename)
        cropRegion     = (134, 1926, 258, 1944)
        RENAME_PNG(fdir_out_png, init.fdir_ncam_graph, cropRegion, dtime)
        #  AVI2PNG(fname, fdir_out_png)
    exit()

    for fname in fnames_f:
        filename   = fname.split('/')[-1][:-4]
        fdir_out   = '%s/%s' % (init.fdir_fcam_graph, filename)
        cropRegion = (151, 1064, 274, 1077)
        #  AVI2PNG(fname, fdir_out)

    exit()

if __name__ == '__main__':
    from pre_vid import ANIM_INIT
    #  date = datetime.datetime(2014, 9, 4)
    #  date = datetime.datetime(2014, 9, 7)
    #  date = datetime.datetime(2014, 9, 9)
    #  date = datetime.datetime(2014, 9, 10)
    #  date = datetime.datetime(2014, 9, 16)
    #  date = datetime.datetime(2014, 9, 17)
    #  date = datetime.datetime(2014, 9, 19)
    #  date = datetime.datetime(2014, 9, 21)
    date = datetime.datetime(2014, 9, 24)
    dtime_s = datetime.datetime(2014, 9, 24, 23, 40)
    dtime_e = datetime.datetime(2014, 9, 25,  0, 10)


    init = ANIM_INIT(date)
    MAIN_CAM(init, dtime_s, dtime_e)
