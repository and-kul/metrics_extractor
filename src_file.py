class SrcFile:
    def __init__(self, path, language):
        self.id = 0
        self.project_id = 0
        self.path = path
        self.language = language
        self.cloc_metrics = None
