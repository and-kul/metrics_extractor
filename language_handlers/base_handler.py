from abc import ABC, abstractmethod
from config import Config


class BaseHandler(ABC):
    def __init__(self, project_name: str, conn, generic_src_files):
        """
        Create new language handler
        :param project_name: project name
        :param conn: open db connection
        :param generic_src_files: enumerable collection of SrcFile
        """
        self.project_name = project_name
        self.conn = conn
        self.src_files = self.filter_my_src_files(generic_src_files)
        self.config = Config()

    @staticmethod
    @abstractmethod
    def filter_my_src_files(generic_src_files):
        pass

    @abstractmethod
    def handle(self):
        pass
