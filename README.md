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
- `GTIME_IMAGE(fname, cropRegion, upscaleN=20, iterN=4)`
- `RENAME_PNG(fdir_in, fdir_out, cropRegion, fps=2, dtime_ref=datetime.datetime(1, 1, 1), sec_threshold=1.5)`


------------

#### `pre_trk.py`

------------
