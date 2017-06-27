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
    fmt = "%(filename)24s[LINE:%(lineno)4d]# %(levelname)-8s [%(asctime)s]  %(message)s"

    logging.basicConfig(level=level, filename=log_filename, format=fmt)


def make_project_name_from_url(url: str) -> str:
    if url.endswith(".git"):
        project_name = url[url.rfind("/") + 1: url.rfind(".git")]
    else:
        project_name = url[url.rfind("/") + 1:]
    return project_name


def git_clone(project_info: ProjectInfo):
    logging.info("Project \"{0}\": git clone started".format(project_info.name))

    # clone project to local directory ./<project_name>
    ret = subprocess.call(['git', 'clone', project_info.url, project_info.name])
    if ret != 0:
        print("ERROR: git clone crashed. Status code {0}".format(ret))
        exit(1)
    logging.info("Project \"{0}\": git clone finished".format(project_info.name))
    print("Project \"{0}\": git clone finished".format(project_info.name))


def remove_local_project_directory(project_info: ProjectInfo):
    logging.info("Project \"{0}\": removing project directory...".format(project_info.name))
    shutil.rmtree(project_info.name, ignore_errors=False, onerror=handle_remove_readonly)
    logging.info("Project \"{0}\": project directory has been removed".format(project_info.name))
    print("Project \"{0}\": project directory has been removed".format(project_info.name))


def get_cloc_json_for_project(project_info: ProjectInfo) -> str:
    logging.info("Project \"{0}\": cloc started".format(project_info.name))
    completed_process = subprocess.run([Config.get_cloc_path(), '--json', '--by-file', project_info.name],
                                       stdout=subprocess.PIPE, encoding='utf-8')
    if completed_process.returncode != 0:
        logging.error("Project \"{0}\": cloc crashed. Status code = {1}"
                      .format(project_info.name, completed_process.returncode))
        print("ERROR: Project \"{0}\": cloc crashed. Status code = {1}"
                      .format(project_info.name, completed_process.returncode))
        exit(1)
    logging.info("Project \"{0}\": cloc finished".format(project_info.name))
    return completed_process.stdout


def remove_preprocessor_directives(filename: str):
    file = open(filename, "rt")
    lines = file.readlines()
    file.close()

    if_synonyms = ("#if", "#ifdef", "#ifndef")
    else_synonyms = ("#elif", "#else")

    nesting_level = 0
    inside_bad_area = False
    bad_area_start: int
    target_nesting_level: int

    lines_to_remove = set()  # lines numbers to remove

    for i in range(0, len(lines)):
        line = lines[i]
        line = line.lstrip()

        if inside_bad_area and line.startswith("#endif") and target_nesting_level == nesting_level:
            inside_bad_area = False
            lines_to_remove |= set(range(bad_area_start, i))

        if line.startswith("#endif"):
            nesting_level -= 1

        if line.startswith(if_synonyms):
            nesting_level += 1
            continue

        if line.startswith(else_synonyms) and not inside_bad_area:
            inside_bad_area = True
            bad_area_start = i + 1
            target_nesting_level = nesting_level
            continue

    new_file = open(filename, "wt")
    for i in range(0, len(lines)):
        if i not in lines_to_remove:
            new_file.write(lines[i])

    new_file.close()
    return





def analyze_project(project_info: ProjectInfo):
    cloc_json = get_cloc_json_for_project(project_info)
    conn = None

    try:
        conn_params = Config.get_postgresql_conn_parameters()
        conn = psycopg2.connect(**conn_params)

        project_id = db_helpers.add_new_project(conn, project_info)
        logging.info("Project \"{0}\": project_id = {1}".format(project_info.name, project_id))

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

        # todo call removing preprocessor directives procedure
        # for file_info in all_files:
        #     if file_info.language in ("C#", "C", "C++", "C/C++ Header"):
        #         remove_preprocessor_directives(file_info.path)

        handler_provider = HandlerProvider(project_info, conn)

        for file_info in all_files:
            language_handler = handler_provider.get_handler_for_language(file_info.language)
            if language_handler is None:
                logging.info("Handler for {0} not found".format(file_info.path))
            else:
                logging.info("Start handling file {0}".format(file_info.path))
                language_handler.handle_one_file(file_info)
                logging.info("OK")

    except psycopg2.DatabaseError as error:
        print("analyze_project() crashed")
        print(error)
    finally:
        if conn is not None:
            conn.close()
        logging.info("connection_closed")

    logging.info("Project \"{0}\": analyze_project() successfully finished".format(project_info.name))
    print("Project \"{0}\": analyze_project() successfully finished".format(project_info.name))


def handle_one_project(url: str):
    project_name = make_project_name_from_url(url)
    project_info: ProjectInfo = ProjectInfo(url, project_name)

    logging.info("Project \"{0}\": start processing".format(project_info.name))
    print("Project \"{0}\": start processing".format(project_info.name))

    git_clone(project_info)
    analyze_project(project_info)
    remove_local_project_directory(project_info)




def main():
    init_logging(logging.INFO)

    # todo_file = open(Config.get_todo_file_path(), 'rt')
    # for line in todo_file:
    #     if line.isspace():
    #         continue
    #     handle_one_project(line.strip())

    project_info = ProjectInfo("blabla", "tensorflow")
    analyze_project(project_info)
    #remove_local_project_directory(project_info)

    exit(0)


if __name__ == "__main__":
    main()
