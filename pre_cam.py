import os
import numpy as np
import glob
import datetime
from PIL import Image
from pytesseract import image_to_string

def AVI2PNG(fname_avi, fdir_out):
    #{{{
    """
    -i: input
    """
    fdir_out_tmp = '%s/%s' % (fdir_out, fname_avi.split('/')[-1].split('.')[0])
    if os.path.exists(fdir_out_tmp):
        print 'Warning [AVI2PNG]: %s already exists!' % (fdir_out_tmp)
        print 'Warning [AVI2PNG]: deleting image under %s ...' % (fdir_out_tmp)
        os.system('rm -rf %s/*' % (fdir_out_tmp))
    else:
        os.system('mkdir -p %s' % (fdir_out_tmp))

    os.system("ffmpeg -loglevel quiet -i %s -vf fps=2 %s/%%07d.png" % (fname_avi, fdir_out_tmp))

    N = len(glob.glob('%s/*png' % fdir_out_tmp))

    if N > 0:
        print 'Message [AVI2PNG]: %s conversion [AVI->PNG] is complete.' % (fname_avi)
    else:
        print 'Error [AVI2PNG]: %s cannot be converted.' % (fname_avi)
    #}}}

def GTIME_IMAGE(fname, cropRegion, upscaleN=20, iterN=4):
    #{{{
    img = Image.open(fname)
    img = img.crop(cropRegion)
    width, height = img.size
    for i in xrange(iterN):
        img = img.convert('L')
        img = img.resize((width*upscaleN, height*upscaleN), Image.BICUBIC)

    img = img.convert('L')
    img = img.resize((width*upscaleN, height*upscaleN), Image.ANTIALIAS)
    string = image_to_string(img, config='digits')
    return string
    #}}}

def RENAME_PNG(fdir_in, fdir_out, cropRegion=(221, 1064, 274, 1077), date_s='2014-09-19', startN=1):
    #{{{
    fnames = sorted(glob.glob('%s/*.png' % fdir_in))
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
    #}}}

def MAIN_CAM(init, fdir_cam_data='/argus/field/arise/video'):
    # ffmpeg convert AVI video to PNG image
    # + {{{
    for cam_tag in ['Nadir', 'Forward']:
        print 'Message [MAIN_CAM]: Processing %s data on %s...' % (cam_tag, init.date_s)
        fnames = sorted(glob.glob('%s/%s*%s*.avi' % (fdir_cam_data, cam_tag, init.date_s)))
        if cam_tag == 'Nadir':
            for fname in fnames:
                AVI2PNG(fname, init.fdir_ncam_graph)
        elif cam_tag == 'Forward':
            for fname in fnames:
                AVI2PNG(fname, init.fdir_fcam_graph)
    # - }}}

    # rename and copy the image according to the time stamp in video
    ## + {{{
    #for cam_tag in ['Nadir', 'Forward']:
        #if cam_tag == 'Nadir':
            #NFile = len(glob.glob('%s/*.png' % init.fdir_ncam_graph))
            #if NFile > 0:
                #os.system('rm -rf %s/*.png' % init.fdir_ncam_graph)
            #if init.date_s in ['2014-09-07', '2014-09-09', '2014-09-16', '2014-09-17', '2014-09-19']:
                #cropRegion = (203, 1926, 258, 1944)
            #else:
                #exit('Error [MAIN_CAM]: date of %s has NOT been implemented.' % init.date_s)
            #startN = 0
            #for fdir_in in sorted(glob.glob('%s/%s*' % (init.fdir_ncam_graph, cam_tag))):
                #startN = RENAME_PNG(fdir_in, init.fdir_ncam_graph, startN=startN, date_s=init.date_s, cropRegion=cropRegion)
        #elif cam_tag == 'Forward':
            #NFile = len(glob.glob('%s/*.png' % init.fdir_fcam_graph))
            #if NFile > 0:
                #os.system('rm -rf %s/*.png' % init.fdir_fcam_graph)
            #if init.date_s in ['2014-09-07', '2014-09-09', '2014-09-16', '2014-09-17', '2014-09-19']:
                #cropRegion = (221, 1064, 274, 1077)
            #else:
                #exit('Error [MAIN_CAM]: date of %s has NOT been implemented.' % init.date_s)
            #startN = 0
            #for fdir_in in sorted(glob.glob('%s/%s*' % (init.fdir_fcam_graph, cam_tag))):
                #startN = RENAME_PNG(fdir_in, init.fdir_fcam_graph, startN=startN, date_s=init.date_s, cropRegion=cropRegion)
    ## - }}}

if __name__ == '__main__':
    from pre_vid import ANIM_INIT
    #date = datetime.datetime(2014, 9, 4)
    #date = datetime.datetime(2014, 9, 7)
    #date = datetime.datetime(2014, 9, 9)
    #date = datetime.datetime(2014, 9, 10)
    #date = datetime.datetime(2014, 9, 16)
    #date = datetime.datetime(2014, 9, 17)
    #date = datetime.datetime(2014, 9, 19)
    #date = datetime.datetime(2014, 9, 21)
    date = datetime.datetime(2014, 9, 24)


    init = ANIM_INIT(date)
    MAIN_CAM(init)
