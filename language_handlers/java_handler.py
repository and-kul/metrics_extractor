import subprocess
from typing import Collection

from database import db_helpers
from info.file_info import FileInfo
from info.function_info import FunctionInfo
from info.project_info import ProjectInfo
from language_handlers.base_handler import BaseHandler


class JavaHandler(BaseHandler):
    def __init__(self, project_info: ProjectInfo, conn):
        super().__init__(project_info, conn)
        self.metrixpp_collect_performed: bool = False

    def get_metrixpp_xml_for_file(self, file_info: FileInfo) -> str:
        completed_process = subprocess.run([self.config.get_python27_path(), self.config.get_metrixpp_path(),
                                            'view', '--format=xml', '--nest-regions',
                                            '--db-file={0}'.format(self.config.get_path_for_temp_metrixpp_db()),
                                            '--log-level=WARNING', '--',
                                            file_info.path], stdout=subprocess.PIPE, encoding='utf-8')
        if completed_process.returncode != 0:
            print("ERROR: metrix++ view crashed. Status code {0}".format(completed_process.returncode))
            exit(1)
        print("metrix++ view finished")

        return completed_process.stdout


    def handle_one_file(self, file_info: FileInfo):
        if not self.metrixpp_collect_performed:
            self.invoke_metrixpp_collect()
            self.metrixpp_collect_performed = True

        from language_handlers.metrixpp_parser import parse_metrixpp_xml
        db_helpers.add_new_file(self.conn, file_info)
        metrixpp_xml = self.get_metrixpp_xml_for_file(file_info)
        print(file_info.path)
        regions = parse_metrixpp_xml(metrixpp_xml)

        for region_info in regions:
            region_info.file_info = file_info

        for region_info in reversed(regions):
            if region_info.is_inside_some_function:
                continue
            if isinstance(region_info, FunctionInfo):
                db_helpers.add_new_function(self.conn, region_info)
            else:
                db_helpers.add_new_region(self.conn, region_info)
        return


    def invoke_metrixpp_collect(self):
        ret = subprocess.call([self.config.get_python27_path(), self.config.get_metrixpp_path(),
                               'collect', '--std.code.lines.total', '--std.code.lines.code',
                               '--std.code.lines.preprocessor',
                               '--std.code.lines.comments', '--std.code.complexity.cyclomatic',
                               '--db-file={0}'.format(self.config.get_path_for_temp_metrixpp_db()),
                               '--log-level=WARNING', '--', self.project_info.name])
        if ret != 0:
            print("ERROR: metrix++ collect crashed. Status code {0}".format(ret))
            exit(1)
        print("metrix++ collect finished")


    def handle_files(self, files: Collection[FileInfo]):
        if not self.metrixpp_collect_performed:
            self.invoke_metrixpp_collect()
            self.metrixpp_collect_performed = True

        for file_info in files:
            self.handle_one_file(file_info)
        return
