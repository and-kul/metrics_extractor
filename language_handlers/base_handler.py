from abc import ABC, abstractmethod
from config import Config
from info.file_info import FileInfo
from info.project_info import ProjectInfo
from typing import Collection


class BaseHandler(ABC):
    def __init__(self, project_info: ProjectInfo, conn):
        """
        Create new language handler
        :param project_info: ProjectInfo object
        :param conn: open db connection
        """
        self.project_info = project_info
        self.conn = conn
        self.config = Config()

    @abstractmethod
    def handle_one_file(self, file_info: FileInfo):
        pass

    @abstractmethod
    def handle_files(self, files: Collection[FileInfo]):
        pass
