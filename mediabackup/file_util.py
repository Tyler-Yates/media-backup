# Taken from https://github.com/arthurvr/image-extensions
import os
from datetime import datetime

import exifread

IMAGE_EXTENSIONS = frozenset([
    "ase",
    "art",
    "bmp",
    "blp",
    "cd5",
    "cit",
    "cpt",
    "cr2",
    "cut",
    "dds",
    "dib",
    "djvu",
    "egt",
    "exif",
    "gif",
    "gpl",
    "grf",
    "icns",
    "ico",
    "iff",
    "jng",
    "jpeg",
    "jpg",
    "jfif",
    "jp2",
    "jps",
    "lbm",
    "max",
    "miff",
    "mng",
    "msp",
    "nef",
    "nitf",
    "ota",
    "pbm",
    "pc1",
    "pc2",
    "pc3",
    "pcf",
    "pcx",
    "pdn",
    "pgm",
    "PI1",
    "PI2",
    "PI3",
    "pict",
    "pct",
    "pnm",
    "pns",
    "ppm",
    "psb",
    "psd",
    "pdd",
    "psp",
    "px",
    "pxm",
    "pxr",
    "qfx",
    "raw",
    "rle",
    "sct",
    "sgi",
    "rgb",
    "int",
    "bw",
    "tga",
    "tiff",
    "tif",
    "vtf",
    "xbm",
    "xcf",
    "xpm",
    "3dv",
    "amf",
    "ai",
    "awg",
    "cgm",
    "cdr",
    "cmx",
    "dxf",
    "e2d",
    "egt",
    "eps",
    "fs",
    "gbr",
    "odg",
    "svg",
    "stl",
    "vrml",
    "x3d",
    "sxd",
    "v2d",
    "vnd",
    "wmf",
    "emf",
    "art",
    "xar",
    "png",
    "webp",
    "jxr",
    "hdp",
    "wdp",
    "cur",
    "ecw",
    "iff",
    "lbm",
    "liff",
    "nrrd",
    "pam",
    "pcx",
    "pgf",
    "sgi",
    "rgb",
    "rgba",
    "bw",
    "int",
    "inta",
    "sid",
    "ras",
    "sun",
    "tga",
    "heic",
    "heif",
    "rw2",
    "dng"
])

# Taken from https://gist.github.com/aaomidi/0a3b5c9bd563c9e012518b495410dc0e
VIDEO_EXTENSIONS = frozenset(
    [
        "webm",
        "mkv",
        "flv",
        "vob",
        "ogv",
        "ogg",
        "rrc",
        "gifv",
        "mng",
        "mov",
        "avi",
        "qt",
        "wmv",
        "yuv",
        "rm",
        "asf",
        "amv",
        "mp4",
        "m4p",
        "m4v",
        "mpg",
        "mp2",
        "mpeg",
        "mpe",
        "mpv",
        "m4v",
        "svi",
        "3gp",
        "3g2",
        "mxf",
        "roq",
        "nsv",
        "flv",
        "f4v",
        "f4p"
        "f4a",
        "f4b",
        "mod",
    ]
)

FILE_PATH_PARTS_TO_IGNORE = frozenset(
    [".stversions"]
)


def is_image(file_path: str) -> bool:
    for image_extension in IMAGE_EXTENSIONS:
        if file_path.lower().endswith(image_extension):
            return True
    return False


def is_video(file_path: str) -> bool:
    for video_extension in VIDEO_EXTENSIONS:
        if file_path.lower().endswith(video_extension):
            return True
    return False


def should_ignore_file(file_path: str) -> bool:
    for file_path_part in FILE_PATH_PARTS_TO_IGNORE:
        if file_path_part in file_path.lower():
            return True
    return False


def get_file_date(absolute_file_path: str) -> datetime:
    with open(absolute_file_path, mode='rb') as input_file:
        # noinspection PyTypeChecker
        tags = exifread.process_file(input_file)
        date_taken = tags.get('EXIF DateTimeOriginal', None)

    if date_taken:
        date_taken = datetime.strptime(str(date_taken), '%Y:%m:%d %H:%M:%S')
        return date_taken

    modified_time = datetime.utcfromtimestamp(os.path.getmtime(absolute_file_path))
    creation_time = datetime.utcfromtimestamp(os.path.getctime(absolute_file_path))
    oldest_time = min(modified_time, creation_time)
    return oldest_time
