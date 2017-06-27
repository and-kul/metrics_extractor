import subprocess
from typing import Collection, List, Set

import logging

from config import Config
from database import db_helpers
from info.file_info import FileInfo
from info.function_info import FunctionInfo
from info.project_info import ProjectInfo
from language_handlers.base_handler import BaseHandler


class MetrixppHandler(BaseHandler):
    already_collected_projects = set()

    @classmethod
    def metrixpp_collect_performed_for(cls, project_info: ProjectInfo) -> bool:
        return project_info in cls.already_collected_projects

    def __init__(self, project_info: ProjectInfo, conn):
        super().__init__(project_info, conn)
        self.error_filenames = None

    @staticmethod
    def get_metrixpp_xml_for_file(file_info: FileInfo) -> str:
        completed_process = subprocess.run([Config.get_python27_path(), Config.get_metrixpp_path(),
                                            'view', '--format=xml', '--nest-regions',
                                            '--db-file={0}'.format(Config.get_path_for_temp_metrixpp_db()),
                                            '--log-level=WARNING', '--',
                                            file_info.path], stdout=subprocess.PIPE, encoding='utf-8')
        if completed_process.returncode != 0:
            print("ERROR: metrix++ view crashed. Status code {0}".format(completed_process.returncode))
            exit(1)
        logging.info("metrix++ view finished")

        return completed_process.stdout

    def handle_one_file(self, file_info: FileInfo):
        if not self.metrixpp_collect_performed_for(self.project_info):
            self.invoke_metrixpp_collect()

        if file_info.path in self.error_filenames:
            logging.error("ERROR: file \"{0}\" was skipped due to metrix++ collect warning".format(file_info.path))
            print("ERROR: file \"{0}\" was skipped due to metrix++ collect warning".format(file_info.path))
            return

        from language_handlers.metrixpp_parser import parse_metrixpp_xml
        db_helpers.add_new_file(self.conn, file_info)
        metrixpp_xml = self.get_metrixpp_xml_for_file(file_info)
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


    @staticmethod
    def get_error_file_set(collect_stdout: str) -> Set[str]:
        lines = collect_stdout.split("\n")
        result = set()
        for line in lines:
            if "warning: Non-matching" not in line:
                continue
            result.add(line[:line.find(":")])
        return result


    def invoke_metrixpp_collect(self):
        logging.info("metrix++ collect started")
        completed_process = subprocess.run([Config.get_python27_path(), Config.get_metrixpp_path(),
                                            'collect', '--std.code.lines.total', '--std.code.lines.code',
                                            '--std.code.lines.preprocessor',
                                            '--std.code.lines.comments', '--std.code.complexity.cyclomatic',
                                            '--db-file={0}'.format(Config.get_path_for_temp_metrixpp_db()),
                                            '--log-level=WARNING', '--', self.project_info.name],
                                           stdout=subprocess.PIPE, encoding='utf-8')
        if completed_process.returncode != 0:
            print("ERROR: metrix++ collect crashed. Status code {0}".format(completed_process.returncode))
            exit(1)

        self.error_filenames = self.get_error_file_set(completed_process.stdout)

        self.already_collected_projects.add(self.project_info)
        logging.info("metrix++ collect finished")

    def handle_files(self, files: Collection[FileInfo]):
        if not self.metrixpp_collect_performed_for(self.project_info):
            self.invoke_metrixpp_collect()

        for file_info in files:
            self.handle_one_file(file_info)
        return
