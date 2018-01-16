import os
import numpy as np
import glob
import datetime
from PIL import Image
from pytesseract import image_to_string
from scipy import stats

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
        print('Message [AVI2PNG]: %s conversion [AVI->PNG] is complete.' % (fname_avi))
    else:
        print('Error [AVI2PNG]: %s cannot be converted.' % (fname_avi))

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

def RENAME_PNG(fdir_in, fdir_out, dtime_ref, cropRegion, fps=2, sec_threshold=1.5, sec_vid_len=3600.0):

    fnames = sorted(glob.glob('%s/*.png' % fdir_in))
    NFile  = len(fnames)

    XX = np.arange(NFile)

    jsec_ocr = np.zeros(NFile, dtype=np.float64) # Julian seconds from OCR by tesseract
    # get time stamp from OCR
    for i in XX:
        fname     = fnames[i]
        rawString = GTIME_IMAGE(fname, cropRegion)
        newString = rawString.replace(' ', '')
        try:
            dtime = datetime.datetime.strptime(newString, '%Y-%m-%d%H:%M:%S')
            jsec_ocr0 = (dtime-dtime_ref).total_seconds()

            if np.abs(jsec_ocr0) > sec_vid_len:

                dateStr       = dtime_ref.strftime('%Y-%m-%d')
                timeStr       = dtime.strftime('%H:%M:%S')
                dtime_new     = datetime.datetime.strptime(dateStr+timeStr, '%Y-%m-%d%H:%M:%S')
                jsec_ocr0_new = (dtime_new-dtime_ref).total_seconds()

                if -1.0 < (jsec_ocr0_new-jsec_ocr[i-1]) < 2.0:
                    jsec_ocr[i] = jsec_ocr0_new
                else:
                    jsec_ocr[i] = np.nan

            else:
                jsec_ocr[i] = jsec_ocr0

        except ValueError:
            jsec_ocr[i] = np.nan

    jsec_ref  = 1.0/fps*XX

    logic_nan = np.isnan(jsec_ocr)
    indices_nan_yes = np.where(logic_nan)[0]
    indices_nan_not = np.where(np.logical_not(logic_nan))[0]

    # find outliers in jsec_ocr[indices_nan_not]
    diff_raw  = jsec_ocr[indices_nan_not]-jsec_ref[indices_nan_not]
    diff_int  = np.int_(diff_raw)
    diff_int_unique, indices = np.unique(diff_int, return_inverse=True)
    counts    = np.bincount(indices)
    index_max = np.argmax(counts)
    diff0     = diff_int_unique[index_max]
    diff      = diff_raw - diff0
    indices_outlier = indices_nan_not[np.where(np.abs(diff)>sec_threshold)[0]]
    jsec_ocr[indices_outlier] = np.nan

    logic_nan = np.isnan(jsec_ocr)
    indices_nan_yes = np.where(logic_nan)[0]
    indices_nan_not = np.where(np.logical_not(logic_nan))[0]

    slope, intercept, r_value, p_value, std_err = stats.linregress(XX[indices_nan_not], jsec_ocr[indices_nan_not])
    jsec_ocr[indices_nan_yes] = np.round(slope*XX[indices_nan_yes] + intercept, decimals=0)

    for i in XX:
        fname  = fnames[i]
        ID_str = fname.split('/')[-1][:-4]
        dtimeString = (dtime_ref+datetime.timedelta(seconds=jsec_ocr[i])).strftime('%Y-%m-%d_%H:%M:%S')
        if i in indices_nan_yes:
            fname_new = '%s/%s_%s_bad.png' % (fdir_out, dtimeString, ID_str)
        else:
            fname_new = '%s/%s_%s_good.png' % (fdir_out, dtimeString, ID_str)

        os.system('cp %s %s' % (fname, fname_new))

def MAIN_CAM(init, dtime_s, dtime_e, fdir_cam_data='/argus/field/arise/video'):

    # for tag in ['Nadir', 'Forward']:
    for tag in ['Nadir']:
        fnames_all = sorted(glob.glob('%s/%s*.avi' % (fdir_cam_data, tag)))
        for fname in fnames_all:
            dtime_str = fname[-23:-4]
            dtime     = datetime.datetime.strptime(dtime_str, '%Y-%m-%d-%H-%M-%S')

            if (dtime >= dtime_s) and (dtime <= dtime_e):
                filename_no_ext = fname.split('/')[-1][:-4]
                if tag == 'Nadir':
                    fdir_out     = init.fdir_ncam_graph
                    fdir_out_png = '%s/%s' % (fdir_out, filename_no_ext)
                    cropRegion   = (134, 1926, 258, 1944)
                elif tag == 'Forward':
                    fdir_out     = init.fdir_fcam_graph
                    fdir_out_png = '%s/%s' % (fdir_out, filename_no_ext)
                    cropRegion   = (151, 1064, 274, 1077)

                AVI2PNG(fname, fdir_out_png)
                RENAME_PNG(fdir_out_png, fdir_out, dtime, cropRegion)

def MODIFY_WRONG_MONTH(fdir, dtime_ref):
    """
    will be delete
    """
    fnames = sorted(glob.glob('%s/*.png' % fdir))
    for fname in fnames:
        filename  = fname.split('/')[-1]
        newString = filename[:19]
        dtime = datetime.datetime.strptime(newString, '%Y-%m-%d_%H:%M:%S')
        diff  = np.abs((dtime-dtime_ref).total_seconds())
        if diff > 86400.0*2:
            dateString = dtime_ref.strftime('%Y-%m-%d')
            filename_new = '%s_%s' % (dateString, filename[11:])
            print(filename)
            print(filename_new)
            print()
            #  os.system('mv %s %s/%s' % (fname, fdir, filename_new))

if __name__ == '__main__':
    from pre_vid import ANIM_INIT

    # --- 2014-09-10 --- (5\cu)
    # date = datetime.datetime(2014, 9, 10)
    # dtime_s = datetime.datetime(2014, 9, 10, 19, 0)
    # dtime_e = datetime.datetime(2014, 9, 11,  0, 0)
    # init = ANIM_INIT(date)
    # MAIN_CAM(init, dtime_s, dtime_e)

    # --- 2014-09-11 --- (5\cu)
    date = datetime.datetime(2014, 9, 11)
    dtime_s = datetime.datetime(2014, 9, 11, 20, 30, 0)
    dtime_e = datetime.datetime(2014, 9, 11, 23, 0, 0)
    init = ANIM_INIT(date)
    MAIN_CAM(init, dtime_s, dtime_e)

    # --- 2014-09-21 --- (5\cu)
    #  date = datetime.datetime(2014, 9, 21)
    #  dtime_s = datetime.datetime(2014, 9, 21, 18, 0)
    #  dtime_e = datetime.datetime(2014, 9, 22,  0, 0)
    #  init = ANIM_INIT(date)
    #  MAIN_CAM(init, dtime_s, dtime_e)

    # --- 2014-09-24 --- (5\cu)
    #  date = datetime.datetime(2014, 9, 24)
    #  dtime_s = datetime.datetime(2014, 9, 24, 21, 0)
    #  dtime_e = datetime.datetime(2014, 9, 25,  1, 0)
    #  init = ANIM_INIT(date)
    #  MAIN_CAM(init, dtime_s, dtime_e)

    # --- 2014-10-02 --- (5\cu)
    #  date = datetime.datetime(2014, 10, 2)
    #  dtime_s = datetime.datetime(2014, 10, 2, 23, 0)
    #  dtime_e = datetime.datetime(2014, 10, 3,  5, 0)
    #  init = ANIM_INIT(date)
    #  MAIN_CAM(init, dtime_s, dtime_e)
