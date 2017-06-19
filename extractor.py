import errno
import os
import shutil
import stat
import subprocess
import psycopg2

from_extension_to_cloc_name = {}


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


def process_lizard_xml_string(xml_string, languages_statistics):
    import xml.etree.ElementTree as ET
    root = ET.fromstring(xml_string)
    file_elements = root.findall("./measure[@type='File']/item")
    for file_element in file_elements:
        file_name = file_element.get('name')
        file_extension = file_name[file_name.rfind('.') + 1:]
        file_language = from_extension_to_cloc_name[file_extension]
        if file_language not in languages_statistics:
            languages_statistics[file_language] = LanguageStat(file_language)
        language_stat = languages_statistics[file_language]
        language_stat.files += 1
        language_stat.code_lines += int(file_element[1].text)
        language_stat.ccn += int(file_element[2].text)
        language_stat.functions += int(file_element[3].text)


def process_cloc_json_string(json_string, languages_statistics):
    import json
    cloc_results = json.loads(json_string)
    for language in languages_statistics:
        cloc_files = cloc_results[language]["nFiles"]
        cloc_blank_lines = cloc_results[language]["blank"]
        cloc_comment_lines = cloc_results[language]["comment"]
        cloc_code_lines = cloc_results[language]["code"]
        languages_statistics[language].add_cloc_info(cloc_files, cloc_blank_lines, cloc_comment_lines, cloc_code_lines)


def init():
    import json
    global from_extension_to_cloc_name
    with open("from_extension_to_cloc_name.json", "rt") as extensions_file:
        from_extension_to_cloc_name = json.load(extensions_file)
    print(from_extension_to_cloc_name)



def send_data_to_db(conn, url, project_name, languages_statistics):
    insert_project_sql = """INSERT INTO projects(url, name)
             VALUES(%s, %s) RETURNING id;"""
    insert_language_stat = """INSERT INTO statistics(project_id, language_name, code_lines, cloc_code_lines,
        comment_lines, blank_lines, functions, avg_ccn_per_function, avg_code_lines_per_function, files, cloc_files)
        VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"""

    # create a new cursor
    cur = conn.cursor()

    # insert new project info
    cur.execute(insert_project_sql, (url, project_name))
    # get the generated id back
    project_id = cur.fetchone()[0]
    print("Project id:", project_id)

    for language in languages_statistics:
        language_stat = languages_statistics[language]
        cur.execute(insert_language_stat, (project_id, language) + language_stat.get_metrics_tuple_for_db())

    # commit the changes to the database
    conn.commit()
    # close cursor
    cur.close()






def main():
    from config import Config
    # init()
    # url = input("Enter URL to the GitHub repository: ")
    config = Config()

    # if url.endswith(".git"):
    #     project_name = url[url.rfind("/") + 1: url.rfind(".git")]
    # else:
    #     project_name = url[url.rfind("/") + 1:]

    url = "https://github.com/google/gson"
    project_name = "gson"

    # ret = subprocess.call(['git', 'clone', url, project_name])
    # if ret != 0:
    #     print("ERROR: git clone crashed. Status code {0}".format(ret))
    #     exit(1)
    # print("git clone finished")

    cloc_filename = project_name + "_cloc.json"
    cloc_json = subprocess.getoutput([config.get_cloc_path(), '--json', '--by-file', project_name])
    # if ret != 0:
    #     print("ERROR: cloc crashed. Status code {0}".format(ret))
    #     exit(1)
    print("cloc finished")

    # with open(cloc_filename, 'wt') as cloc_output_file:
    #     cloc_output_file.write(cloc_json)




    from database import db_helpers
    project_id = 0
    conn = None

    try:
        # get PostgreSQL connection parameters
        conn_params = config.get_postgresql_conn_parameters()
        # connect to the PostgreSQL database
        conn = psycopg2.connect(**conn_params)

        project_id = db_helpers.add_new_project(conn, url, project_name)
        print("project_id =", project_id)

        import json
        from src_file import SrcFile
        from cloc_file_metrics import ClocFileMetrics
        cloc_results = json.loads(cloc_json)

        all_src_files = []

        for file_element in cloc_results:
            if file_element in ["header", "SUM"]:
                continue
            src_file = SrcFile(file_element, cloc_results[file_element]["language"])
            src_file.project_id = project_id
            cloc_file_metrics = ClocFileMetrics(cloc_results[file_element]["blank"],
                                                cloc_results[file_element]["comment"],
                                                cloc_results[file_element]["code"])
            src_file.cloc_metrics = cloc_file_metrics
            all_src_files.append(src_file)

        from language_handlers.java_handler import JavaHandler

        java_handler = JavaHandler(conn, all_src_files)
        java_handler.handle()

        print("hello")



    except psycopg2.DatabaseError as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()



















    # for language in languages_statistics:
    #     cloc_files = cloc_results[language]["nFiles"]
    #     cloc_blank_lines = cloc_results[language]["blank"]
    #     cloc_comment_lines = cloc_results[language]["comment"]
    #     cloc_code_lines = cloc_results[language]["code"]
    #     languages_statistics[language].add_cloc_info(cloc_files, cloc_blank_lines, cloc_comment_lines, cloc_code_lines)
    #
    # languages_statistics = {}
    #
    # # process_lizard_xml_string(lizard_xml, languages_statistics)
    #
    # process_cloc_json_string(cloc_json, languages_statistics)
    #
    # conn = None
    #
    # try:
    #     # get PostgreSQL connection parameters
    #     conn_params = config.get_postgresql_conn_parameters()
    #     # connect to the PostgreSQL database
    #     conn = psycopg2.connect(**conn_params)
    #
    #     send_data_to_db(conn, url, project_name, languages_statistics)
    #
    # except psycopg2.DatabaseError as error:
    #     print(error)
    # finally:
    #     if conn is not None:
    #         conn.close()
    #
    # # os.remove(cloc_filename)
    # # os.remove(lizard_filename)
    #
    # shutil.rmtree(project_name, ignore_errors=False, onerror=handle_remove_readonly)

    print("success")
    exit(0)


if __name__ == "__main__":
    main()
