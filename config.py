from configparser import ConfigParser


class Config:
    def __init__(self, filename='config.ini'):
        self.filename = filename
        # create a parser
        self.parser = ConfigParser()
        # read config file
        self.parser.read(filename)

    def get_cloc_path(self, section='cloc'):
        """ get path to the cloc program executable (like cloc-1.72.exe for Windows)"""
        return self.parser[section]['path']

    def get_postgresql_conn_parameters(self, section='postgresql'):
        # get section, default to postgresql
        db = {}
        if self.parser.has_section(section):
            params = self.parser.items(section)
            for param in params:
                db[param[0]] = param[1]
        else:
            raise Exception('Section {0} not found in the {1} file'.format(section, self.filename))

        return db
