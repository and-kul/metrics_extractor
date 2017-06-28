from typing import List, Union

from lxml import etree

from info.function_info import FunctionInfo
from info.region_info import RegionInfo
from info.region_type import RegionType


def get_subregions(region_element: etree.ElementBase) -> List[etree.ElementBase]:
    return region_element.findall("./subregions/subregion")


def fill_region_info(region_info: RegionInfo, region_element: etree.ElementBase):
    info_element = region_element.find("./info")
    region_info.region_type = RegionType[info_element.get("type").capitalize()]
    region_info.short_name = info_element.get("name")
    region_info.total_lines = int(info_element.get("line_end")) + 1 - (int(info_element.get("line_begin")))

    std_code_lines_element = region_element.find("./data/std.code.lines")
    region_info.own_code_lines = int(std_code_lines_element.get("code")) \
                                 + int(std_code_lines_element.get("preprocessor"))
    region_info.own_comment_lines = int(std_code_lines_element.get("comments"))

    region_info.total_code_lines = region_info.own_code_lines
    region_info.total_comment_lines = region_info.own_comment_lines
    region_info.ccn_sum = 0
    region_info.n_functions = 0
    return


def create_region_info(region_element: etree.ElementBase) -> RegionInfo:
    region_info = RegionInfo()
    fill_region_info(region_info, region_element)
    return region_info


def create_function_info(region_element: etree.ElementBase) -> FunctionInfo:
    function_info = FunctionInfo()
    fill_region_info(function_info, region_element)

    std_code_complexity_element = region_element.find("./data/std.code.complexity")

    # metrixpp ccn is always mistaken by -1
    cyclomatic_complexity = int(std_code_complexity_element.get("cyclomatic")) + 1

    function_info.cyclomatic_complexity = cyclomatic_complexity
    function_info.ccn_sum = cyclomatic_complexity
    function_info.n_functions = 1

    return function_info


def extract_info_recursively(region_element: etree.ElementBase, outer_region: Union[RegionInfo, None],
                             regions: List[RegionInfo]):
    info_element = region_element.find("./info")
    if info_element.get("type") == "function":
        current_region_info = create_function_info(region_element)
    else:
        current_region_info = create_region_info(region_element)

    if (outer_region is not None) and (outer_region.is_inside_some_function or isinstance(outer_region, FunctionInfo)):
        current_region_info.is_inside_some_function = True

    for inner_region in get_subregions(region_element):
        extract_info_recursively(inner_region, current_region_info, regions)

    current_region_info.outer_region = outer_region

    if outer_region is not None:
        outer_region.total_code_lines += current_region_info.total_code_lines
        outer_region.total_comment_lines += current_region_info.total_comment_lines
        outer_region.ccn_sum += current_region_info.ccn_sum
        outer_region.n_functions += current_region_info.n_functions
    regions.append(current_region_info)
    return


def parse_metrixpp_xml(metrixpp_xml: str) -> List[RegionInfo]:
    from xml.sax.saxutils import escape
    try:
        root = etree.fromstring(metrixpp_xml)
    except etree.XMLSyntaxError:
        # escaping in XML attributes < > and & because Metrix++ doesn't do it (who knows why)
        troubles = (
            "operator<<", "operator>>", "operator<", "operator>", "operator<=",
            "operator>=", "operator&", "operator&&", "operator <", "operator >",
            "operator <=", "operator >=", "operator <<", "operator >>", "operator &")
        for trouble in troubles:
            metrixpp_xml = metrixpp_xml.replace(trouble, escape(trouble))
        root = etree.fromstring(metrixpp_xml)

    global_region_element = root.find("./data/file-data/regions/region")
    regions = []
    extract_info_recursively(global_region_element, None, regions)
    return regions
