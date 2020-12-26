from typing import Dict, Type

from .interface import TemplateData, TemplateDB
from .local_implem import LocalTemplateDB
from .minio_implem import MinioInfos, MinioTemplateDB

engines: Dict[str, Type[TemplateDB]] = {
    's3': MinioTemplateDB,
    'local': LocalTemplateDB,
}


def add_engine(name: str, engine: Type[TemplateDB]) -> None:
    engines[name] = engine
