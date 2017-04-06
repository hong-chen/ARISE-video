#### `pre_cam.py`
__Dependencies__:
- [ffmpeg](https://ffmpeg.org)
- [tesseract](https://github.com/tesseract-ocr/tesseract)
  - notes: after installation, under `/usr/share/tesseract/tessdata/configs/`,
  create a file `digits` containing `tessedit_char_whitelist 0123456789:-`.
- [pytesseract](https://github.com/madmaze/pytesseract)
  - notes: when call `pytesseract.image_to_string`, add `config='digits'`

__Functions__:
- `AVI2PNG(fname_avi, fdir_out_png, fps=2, verbose=False)`
  - `fname_avi`: full path of the `avi` video file;
  - `fname_out_png`: directory where to put `png` outputs;
  - `fps=2`: frame per second `=2`;
  - `verbose=False`: verbose flag turned off.

- `GTIME_IMAGE(fname, cropRegion, upscaleN=20, iterN=4)`
  - `fname`: full path of the input image file;
  - `cropRegion`: crop region of the interested area;
  - `upscaleN=20`: increase the resolution of the crop region;
  - `iterN`: number of iteration to refine the crop region.

- `RENAME_PNG(fdir_in, fdir_out, dtime_ref, cropRegion, fps=2, sec_threshold=1.5, sec_vid_len=3600.0)`
  - `fdir_in`: directory of the input `png` files (from `ffmpeg`);
  - `fdir_out`: directory of the output renamed `png` files;
  - `dtime_ref`: reference datetime;
  - `cropRegion`: crop region of the interested area;
  - `fps=2`: frame per second `=2`;
  - `sec_threshold=1.5`: threshold in seconds `=1.5`;
  - `sec_vid_len=3600.0`: video length in seconds `=3600.0`.

- `MAIN_CAM(init, dtime_s, dtime_e, fdir_cam_data='/argus/field/arise/video')`


------------

#### `pre_trk.py`

------------
