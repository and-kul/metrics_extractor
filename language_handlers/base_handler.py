from abc import ABC, abstractmethod


class BaseHandler(ABC):
    def __init__(self, conn, generic_src_files):
        """
        Create new language handler
        :param conn: open db connection
        :param generic_src_files: enumerable collection of SrcFile
        """
        self.conn = conn
        self.src_files = self.filter_my_src_files(generic_src_files)

    @staticmethod
    @abstractmethod
    def filter_my_src_files(generic_src_files):
        pass

    @abstractmethod
    def handle(self):
        pass
