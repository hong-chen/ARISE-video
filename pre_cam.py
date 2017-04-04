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

def RENAME_PNG(fdir_in, fdir_out, cropRegion, fps=2, dtime_ref=datetime.datetime(1, 1, 1), sec_threshold=1.5):

    fnames = sorted(glob.glob('%s/*.png' % fdir_in))
    NFile  = len(fnames)

    XX = np.arange(NFile)

    jsec_ocr = np.zeros(NFile, dtype=np.float64) # Julian seconds from OCR by tesseract
    # first iteration to get time stamp from OCR
    for i in XX:
        fname     = fnames[i]
        rawString = GTIME_IMAGE(fname, cropRegion)
        newString = rawString.replace(' ', '')
        try:
            dtime = datetime.datetime.strptime(newString, '%Y-%m-%d%H:%M:%S')
            jsec_ocr[i] = (dtime-dtime_ref).total_seconds()
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
        AVI2PNG(fname, fdir_out_png)
        RENAME_PNG(fdir_out_png, init.fdir_ncam_graph, cropRegion, dtime_ref=dtime)

    for fname in fnames_f:
        dtime_str      = fname[-23:-4]
        dtime          = datetime.datetime.strptime(dtime_str, '%Y-%m-%d-%H-%M-%S')
        filename       = fname.split('/')[-1][:-4]
        fdir_out_png   = '%s/%s' % (init.fdir_fcam_graph, filename)
        cropRegion     = (151, 1064, 274, 1077)
        AVI2PNG(fname, fdir_out_png)
        RENAME_PNG(fdir_out_png, init.fdir_fcam_graph, cropRegion, dtime_ref=dtime)

def CAL_ZSCORE(X, c=7.5):
    """
    cite: Zou and Zeng 2006
    "A quality control precedure for GPS radio occulation data"
    """
    n    = X.size
    M    = np.median(X)
    MAD  = np.median(np.abs(X-M))
    w    = (X - M)/(c*MAD)
    w[w>1.0] = 1.0
    X_bi = M + np.sum((X-M) * (1.0-w**2)**2) / np.sum((1.0-w**2)**2)
    BSD  = (n * np.sum((X-M)**2 * (1.0-w**2)**4))**0.5 / np.abs(np.sum((1.0-w**2)*(1.0-5.0*w**2)))
    Z    = (X-X_bi)/BSD
    return Z

if __name__ == '__main__':
    from pre_vid import ANIM_INIT
    #  date = datetime.datetime(2014, 9, 4)
    #  date = datetime.datetime(2014, 9, 7)
    #  date = datetime.datetime(2014, 9, 9)

    # --- 2014-09-10 ---
    #  date = datetime.datetime(2014, 9, 10)
    #  dtime_s = datetime.datetime(2014, 9, 10, 19, 0)
    #  dtime_e = datetime.datetime(2014, 9, 11,  0, 0)

    #  date = datetime.datetime(2014, 9, 16)
    #  date = datetime.datetime(2014, 9, 17)
    #  date = datetime.datetime(2014, 9, 19)

    # --- 2014-09-21 ---
    #  date = datetime.datetime(2014, 9, 21)
    #  dtime_s = datetime.datetime(2014, 9, 21, 18, 0)
    #  dtime_e = datetime.datetime(2014, 9, 22,  0, 0)

    # --- 2014-09-24 ---
    date = datetime.datetime(2014, 9, 24)
    dtime_s = datetime.datetime(2014, 9, 24, 21, 0)
    dtime_e = datetime.datetime(2014, 9, 25,  1, 0)


    init = ANIM_INIT(date)
    MAIN_CAM(init, dtime_s, dtime_e)
