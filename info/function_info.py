from info.region_info import RegionInfo
from info.region_type import RegionType


class FunctionInfo(RegionInfo):
    def __init__(self, short_name: str = None):
        super().__init__(RegionType.Function, short_name)
        self.cyclomatic_complexity: int = None
