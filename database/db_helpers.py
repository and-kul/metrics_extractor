from src_file import SrcFile
import psycopg2


def add_new_project(conn, url, project_name) -> int:
    """
    Inserts new project to the database
    :param conn: open psycopg2 db connection
    :param url: git URL of the project
    :param project_name: project name
    :return: new project_id
    """
    insert_project_sql = """INSERT INTO projects(url, name) VALUES(%s, %s) RETURNING id;"""

    cur = conn.cursor()
    cur.execute(insert_project_sql, (url, project_name))
    project_id = cur.fetchone()[0]

    conn.commit()
    cur.close()
    return project_id


def add_new_src_file(conn, src_file: SrcFile) -> int:
    """
    Inserts new file to the database
    :param conn: open psycopg2 db connection
    :param src_file: SrcFile to be added
    :return: new file_id
    """
    insert_file_sql = """INSERT INTO files(project_id, path, language_name,
        cloc_blank_lines, cloc_comment_lines, cloc_code_lines)
        VALUES (%s, %s, %s, %s, %s, %s) RETURNING id;"""

    cur = conn.cursor()
    cur.execute(insert_file_sql, (src_file.project_id, src_file.path, src_file.language,
                                  src_file.cloc_metrics.blank, src_file.cloc_metrics.comment,
                                  src_file.cloc_metrics.code))
    file_id = cur.fetchone()[0]
    src_file.id = file_id

    conn.commit()
    cur.close()
    return file_id
