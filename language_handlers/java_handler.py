from language_handlers.base_handler import BaseHandler
from database import db_helpers


class JavaHandler(BaseHandler):
    @staticmethod
    def filter_my_src_files(generic_src_files):
        return JavaHandler.filter_java_src_files(generic_src_files)

    @staticmethod
    def filter_java_src_files(generic_src_files):
        return [src_file for src_file in generic_src_files if src_file.language == "Java"]

    def handle_one_src_file(self, src_file):
        db_helpers.add_new_src_file(self.conn, src_file)
        pass

    def handle(self):
        for src_file in self.src_files:
            self.handle_one_src_file(src_file)
        pass






