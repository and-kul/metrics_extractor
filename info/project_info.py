class ProjectInfo:
    def __init__(self, url: str, name: str):
        self.id: int = None
        self.url = url
        self.name = name
        self.files_analyzed = 0
        self.files_with_errors = 0
        self.files_with_preprocessor_directives_changed = 0
        self.files_with_raw_strings_changed = 0
