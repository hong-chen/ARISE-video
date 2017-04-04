#### `pre_cam.py`
__Dependencies__:
- [ffmpeg](https://ffmpeg.org)
- [tesseract](https://github.com/tesseract-ocr/tesseract)
  - notes: after installation, under `/usr/share/tesseract/tessdata/configs/`,
  create a file `digits` containing `tessedit_char_whitelist 0123456789:-`.
  add '0123456789:-' to whitelist
- [pytesseract](https://github.com/madmaze/pytesseract)
  - notes: when call `pytesseract.image_to_string`, add `config='digits'`

__Functions__:



------------

#### `pre_trk.py`

------------
