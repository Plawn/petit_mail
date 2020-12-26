from dataclasses import dataclass

from . import utils
from .interface import TemplateDB


@dataclass
class LocalInfos:
    folder: str


class LocalTemplateDB(TemplateDB):
    def __init__(self, infos: LocalInfos, logger=None):
        super().__init__(infos, logger=logger)
        self.folder = infos.folder

    @staticmethod
    def get_creds_form() -> LocalInfos:
        return LocalInfos

    def init(self):
        for full_path in utils.iterate_over_folder(self.folder):
            try:
                filename = full_path.replace(self.folder + '/', '')
                with open(full_path, 'r') as f:
                    self.logger.info(f'opening {filename}')
                    self.add_template_from_text(
                        filename, f.read(), filename.startswith('common'))
                    self.logger.info(f'opened {filename}')
            except:
                self.logger.error(f'failed {full_path}')
        return self
