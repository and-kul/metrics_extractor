from info.file_info import FileInfo
from info.function_info import FunctionInfo
from info.project_info import ProjectInfo
from info.region_info import RegionInfo


def add_new_project(conn, project_info: ProjectInfo) -> int:
    """
    Inserts new project to the database, updating project_info.id
    :param conn: open psycopg2 db connection
    :param project_info: project to be added
    :return: new project_id
    """
    insert_project_sql = """INSERT INTO projects(url, name) VALUES(%s, %s) RETURNING id;"""

    cur = conn.cursor()
    cur.execute(insert_project_sql, (project_info.url, project_info.name))
    project_id = cur.fetchone()[0]
    project_info.id = project_id

    conn.commit()
    cur.close()
    return project_id


def add_new_file(conn, file_info: FileInfo) -> int:
    """
    Inserts new file to the database, updating file_info.id
    :param conn: open psycopg2 db connection
    :param file_info: file to be added
    :return: new file_id
    """
    insert_file_sql = """INSERT INTO files(project_id, path, language_name,
        cloc_blank_lines, cloc_comment_lines, cloc_code_lines)
        VALUES (%s, %s, %s, %s, %s, %s) RETURNING id;"""

    cur = conn.cursor()
    cur.execute(insert_file_sql, (file_info.project_info.id, file_info.path, file_info.language,
                                  file_info.cloc_metrics.blank, file_info.cloc_metrics.comment,
                                  file_info.cloc_metrics.code))
    file_id = cur.fetchone()[0]
    file_info.id = file_id

    conn.commit()
    cur.close()
    return file_id


def add_new_function(conn, function_info: FunctionInfo) -> int:
    """
    Inserts new function to the database, updating function_info.id
    :param conn: open psycopg2 db connection
    :param function_info: function to be added
    :return: new function_id
    """
    insert_function_sql = """INSERT INTO functions(region_id, short_name, total_lines, code_lines, comment_lines,
        cyclomatic_complexity) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id;"""

    cur = conn.cursor()
    cur.execute(insert_function_sql, (function_info.outer_region.id, function_info.short_name,
                                      function_info.total_lines,
                                      function_info.total_code_lines,  # todo: or own_code_lines ?
                                      function_info.total_comment_lines,  # todo: or own_comment_lines ?
                                      function_info.cyclomatic_complexity))
    function_id = cur.fetchone()[0]
    function_info.id = function_id

    conn.commit()
    cur.close()
    return function_id


def add_new_region(conn, region_info: RegionInfo) -> int:
    """
    Inserts new region to the database, updating region_info.id
    :param conn: open psycopg2 db connection
    :param region_info: region to be added
    :return: new region_id
    """
    insert_region_sql = """INSERT INTO regions(file_id, region_type, short_name,
        outer_region_id, total_lines, code_lines,
        comment_lines, average_cyclomatic_complexity,
        average_code_lines_per_function, n_functions)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id;"""

    average_cyclomatic_complexity = region_info.ccn_sum / region_info.n_functions if region_info.n_functions != 0 else 0
    average_code_lines_per_function = None  # todo
    outer_region_id = region_info.outer_region.id if region_info.outer_region is not None else None

    cur = conn.cursor()
    cur.execute(insert_region_sql, (region_info.file_info.id, region_info.region_type.name, region_info.short_name,
                                    outer_region_id, region_info.total_lines, region_info.total_code_lines,
                                    region_info.total_comment_lines, average_cyclomatic_complexity,
                                    average_code_lines_per_function, region_info.n_functions))
    region_id = cur.fetchone()[0]
    region_info.id = region_id

    conn.commit()
    cur.close()
    return region_id


