from configparser import ConfigParser


class Config:
    config_filename = 'config.ini'
    log_filename = None
    parser = ConfigParser()
    parser.read(config_filename)

    @classmethod
    def get_todo_file_path(cls, section='todo'):
        return cls.parser[section]['path']

    @classmethod
    def get_cloc_path(cls, section='cloc'):
        """ get path to the cloc program executable (like cloc-1.72.exe for Windows)"""
        return cls.parser[section]['path']

    @classmethod
    def get_python27_path(cls, section='python27'):
        return cls.parser[section]['path']

    @classmethod
    def get_metrixpp_path(cls, section='metrix++'):
        return cls.parser[section]['path']

    @classmethod
    def get_path_for_temp_metrixpp_db(cls, section='metrix++'):
        return cls.parser[section]['db_file']

    @classmethod
    def get_postgresql_conn_parameters(cls, section='postgresql'):
        # get section, default to postgresql
        db = {}
        if cls.parser.has_section(section):
            params = cls.parser.items(section)
            for param in params:
                db[param[0]] = param[1]
        else:
            raise Exception('Section {0} not found in the {1} file'.format(section, cls.config_filename))

        return db
