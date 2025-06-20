#!/usr/bin/env python3
from bot.helper.ext_utils.status_utils import (
    MirrorStatus,
    get_readable_file_size,
    get_readable_time,
)


class DDLStatus:
    def __init__(self, obj, size, message, gid, upload_details):
        self.__obj = obj
        self.__size = size
        self.__gid = gid
        self.upload_details = upload_details
        self.message = message
        # Access the private listener attribute from DDLUploader
        self.listener = getattr(obj, "_DDLUploader__listener", None)
        self.tool = "ddl"

    def processed_bytes(self):
        return get_readable_file_size(self.__obj.processed_bytes)

    def size(self):
        return get_readable_file_size(self.__size)

    def status(self):
        return MirrorStatus.STATUS_UPLOADING

    def name(self):
        return self.__obj.name

    def progress(self):
        try:
            progress_raw = self.__obj.processed_bytes / self.__size * 100
        except Exception:
            progress_raw = 0
        return f"{round(progress_raw, 2)}%"

    def speed(self):
        return f"{get_readable_file_size(self.__obj.speed)}/s"

    def eta(self):
        try:
            seconds = (self.__size - self.__obj.processed_bytes) / self.__obj.speed
            return get_readable_time(seconds)
        except Exception:
            return "-"

    def gid(self) -> str:
        return self.__gid

    def download(self):
        return self.__obj

    def eng(self):
        return self.__obj.engine
