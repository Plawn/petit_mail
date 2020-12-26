import logging
import os
from dataclasses import dataclass
from typing import Optional

import minio

from .interface import TemplateData, TemplateDB


@dataclass
class MinioInfos:
    host: str
    passkey: str
    accesskey: str
    bucket_name: str


class MinioTemplateDB(TemplateDB):
    def __init__(self, minio_creds: MinioInfos, logger: Optional[logging.Logger] = None):
        super().__init__(minio_creds, logger=logger)
        self.bucket_name = minio_creds.bucket_name
        self.minio_instance = minio.Minio(
            minio_creds.host, minio_creds.accesskey, minio_creds.passkey)

    @staticmethod
    def get_creds_form() -> MinioInfos:
        return MinioInfos

    def init(self):
        NAME = 'temp.html'
        filenames = (
            obj.object_name for obj in self.minio_instance.list_objects(self.bucket_name, recursive=True)
        )
        for filename in filenames:
            self.logger.info(f'pulling {filename}')
            doc = self.minio_instance.get_object(
                self.bucket_name, filename)
            # kinda ugly i have to admit
            with open(NAME, 'wb') as file_data:
                for d in doc.stream(32 * 1024):
                    file_data.write(d)

            with open(NAME, 'r') as f:
                self.add_template_from_text(
                    filename, f.read(), filename.startswith('common')
                )
            self.logger.info(f'Pulled {filename}')

        os.remove(NAME)
