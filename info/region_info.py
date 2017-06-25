from info.file_info import FileInfo
from region_type import RegionType


class RegionInfo:
    def __init__(self, region_type: RegionType = None, short_name: str = None):
        self.region_type = region_type
        self.short_name = short_name
        self.outer_region: RegionInfo = None

        self.file_info: FileInfo = None
        self.id: int = None

        self.total_lines: int = None
        self.own_code_lines: int = None  # preprocessor lines (in C/C++) are also code lines
        self.own_comment_lines: int = None
        self.total_code_lines: int = None
        self.total_comment_lines: int = None

        self.ccn_sum: int = None  # sum of cyclomatic complexity for all functions inside
        self.n_functions: int = None
