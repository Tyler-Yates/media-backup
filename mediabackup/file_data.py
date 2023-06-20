import os
import zlib
from datetime import datetime
from functools import cached_property

from mediabackup import file_util


class FileData:
    def __init__(self, absolute_path: str):
        self.absolute_path = absolute_path
        self.file_name = os.path.basename(self.absolute_path)

    def __str__(self):
        return f"[{self.absolute_path}, Size: {self.size}, Checksum: {self.checksum}," \
               f" is_photo: {self.is_image}, is_video: {self.is_video}"

    def __repr__(self):
        return self.__str__()

    @cached_property
    def checksum(self) -> str:
        result = 0
        with open(self.absolute_path, "rb") as input_file:
            for line in input_file:
                result = zlib.crc32(line, result)
        return "%X" % (result & 0xFFFFFFFF)

    @cached_property
    def size(self) -> int:
        return os.path.getsize(self.absolute_path)

    @cached_property
    def modified_time(self) -> datetime:
        return datetime.utcfromtimestamp(os.path.getmtime(self.absolute_path))

    @cached_property
    def is_image(self) -> bool:
        return file_util.is_image(self.absolute_path)

    @cached_property
    def is_video(self) -> bool:
        return file_util.is_video(self.absolute_path)
