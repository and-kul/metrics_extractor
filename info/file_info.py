from cloc_file_metrics import ClocFileMetrics
from info.project_info import ProjectInfo


class FileInfo:
    def __init__(self, path: str, language: str):
        self.id: int = None
        self.project_info: ProjectInfo = None
        self.path = path
        self.language = language
        self.cloc_metrics: ClocFileMetrics = None
