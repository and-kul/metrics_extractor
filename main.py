import errno
import json
import os
import shutil
import stat
import subprocess
from datetime import datetime
from typing import List

import logging

import psycopg2

from config import Config
from database import db_helpers
from info.project_info import ProjectInfo
from language_handlers.handler_provider import HandlerProvider
from info.file_info import FileInfo
from cloc_file_metrics import ClocFileMetrics


def handle_remove_readonly(func, path, exc):
    excvalue = exc[1]
    if excvalue.errno == errno.EACCES:
        os.chmod(path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)  # 0777
        func(path)
    else:
        raise Exception("ERROR: Problem with removing")


class LanguageStat:
    def __init__(self, language):
        self.language = language
        self.files = 0
        self.functions = 0
        self.code_lines = 0
        self.ccn = 0

    def add_cloc_info(self, cloc_files, cloc_blank_lines, cloc_comment_lines, cloc_code_lines):
        self.cloc_files = cloc_files
        self.cloc_blank_lines = cloc_blank_lines
        self.cloc_comment_lines = cloc_comment_lines
        self.cloc_code_lines = cloc_code_lines

    def get_metrics_tuple_for_db(self):
        return (self.code_lines, self.cloc_code_lines, self.cloc_comment_lines, self.cloc_blank_lines, self.functions,
                self.ccn / self.functions, self.code_lines / self.functions, self.files, self.cloc_files)


def init_logging(level=logging.INFO):
    datetime_fmt = "%Y-%m-%d %H_%M_%S"
    now = datetime.now()
    log_filename = os.path.join('log', now.strftime(datetime_fmt) + '.log')
    Config.log_filename = log_filename
    fmt = "%(filename)-16s[LINE:%(lineno)4d]# %(levelname)-8s [%(asctime)s]  %(message)s"

    logging.basicConfig(level=level, filename=log_filename, format=fmt)


def main():
    init_logging(logging.INFO)

    url = input("Enter URL to the GitHub repository: ")
    config = Config()

    if url.endswith(".git"):
        project_name = url[url.rfind("/") + 1: url.rfind(".git")]
    else:
        project_name = url[url.rfind("/") + 1:]

    logging.warning("Start processing of project: {0}".format(project_name))
    print("Start processing of project: {0}".format(project_name))

    project_info: ProjectInfo = ProjectInfo(url, project_name)

    # clone project to local directory ./<project_name>
    ret = subprocess.call(['git', 'clone', url, project_name])
    if ret != 0:
        print("ERROR: git clone crashed. Status code {0}".format(ret))
        exit(1)
    logging.warning("git clone finished")

    cloc_json = subprocess.getoutput([config.get_cloc_path(), '--json', '--by-file', project_name])
    # if ret != 0:
    #     print("ERROR: cloc crashed. Status code {0}".format(ret))
    #     exit(1)
    logging.info("cloc finished")

    conn = None

    try:
        # get PostgreSQL connection parameters
        conn_params = config.get_postgresql_conn_parameters()
        # connect to the PostgreSQL database
        conn = psycopg2.connect(**conn_params)

        project_id = db_helpers.add_new_project(conn, project_info)
        logging.info("project_id = {0}".format(project_id))

        cloc_results = json.loads(cloc_json)

        all_files: List[FileInfo] = []

        for file_element in cloc_results:
            if file_element in ["header", "SUM"]:
                continue
            file_info = FileInfo(file_element, cloc_results[file_element]["language"])
            file_info.project_info = project_info
            cloc_file_metrics = ClocFileMetrics(cloc_results[file_element]["blank"],
                                                cloc_results[file_element]["comment"],
                                                cloc_results[file_element]["code"])
            file_info.cloc_metrics = cloc_file_metrics
            all_files.append(file_info)

        handler_provider = HandlerProvider(project_info, conn)

        for file_info in all_files:
            language_handler = handler_provider.get_handler_for_language(file_info.language)
            if language_handler is None:
                logging.info("Handler for {0} not fount".format(file_info.path))
            else:
                logging.info("Start handling file {0}".format(file_info.path))
                language_handler.handle_one_file(file_info)
                logging.info("OK")


    except psycopg2.DatabaseError as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
        logging.info("connection_closed")

    shutil.rmtree(project_name, ignore_errors=False, onerror=handle_remove_readonly)

    logging.warning("Success: project {0}".format(project_name))
    print("success")
    exit(0)


if __name__ == "__main__":
    main()
