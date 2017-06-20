import subprocess

from function_info import FunctionInfo
from database import db_helpers
from language_handlers.base_handler import BaseHandler
from src_file import SrcFile
from lxml import etree
from class_info import ClassInfo


class JavaHandler(BaseHandler):
    @staticmethod
    def filter_my_src_files(generic_src_files):
        return JavaHandler.filter_java_src_files(generic_src_files)

    @staticmethod
    def filter_java_src_files(generic_src_files):
        return [src_file for src_file in generic_src_files if src_file.language == "Java"]

    def get_metrixpp_xml_for_file(self, src_file: SrcFile) -> etree.Element:
        completed_process = subprocess.run([self.config.get_python27_path(), self.config.get_metrixpp_path(),
                                            'view', '--format=xml', '--nest-regions',
                                            '--db-file={0}'.format(self.config.get_path_for_temp_metrixpp_db()),
                                            '--log-level=WARNING', '--',
                                            src_file.path], stdout=subprocess.PIPE, encoding='utf-8')
        if completed_process.returncode != 0:
            print("ERROR: metrix++ view crashed. Status code {0}".format(completed_process.returncode))
            exit(1)
        print("metrix++ view finished")

        return etree.fromstring(completed_process.stdout)



    def handle_one_src_file(self, src_file):
        if src_file.path != "gson/gson/src/main/java/com/google/gson/internal/LinkedTreeMap.java":
            return
        db_helpers.add_new_src_file(self.conn, src_file)
        metrixpp_xml = self.get_metrixpp_xml_for_file(src_file)

        class_subregions = metrixpp_xml.findall(".//info[@type='class']/..")
        current_class_id = 0
        from_offset_to_class_info = {}

        for class_subregion in class_subregions:
            info_element = class_subregion.find("./info")
            class_info = ClassInfo(info_element.get("name"))
            class_info.offset = info_element.get("offset_begin")
            current_class_id += 1
            class_info.id = current_class_id
            from_offset_to_class_info[class_info.offset] = class_info
            class_info.total_lines = int(info_element.get("line_end") + 1 - int(info_element.get("line_begin")))

            std_code_lines_element = class_subregion.find("./data/std.code.lines")
            class_info.own_code_lines = int(std_code_lines_element.get("code"))
            class_info.own_comment_lines = int(std_code_lines_element.get("comments"))
            if std_code_lines_element.get("preprocessor") != 0:
                print("ALERT: preprocessor != 0, class {0}".format(class_info.short_name))
                print("ALERT: preprocessor != 0, class {0}".format(class_info.short_name))

        for class_subregion in class_subregions:
            parent_subregion = class_subregion.getparent().getparent()  # two times
            parent_info_element = parent_subregion.find("./info")
            # if parent_info_element.get("type") == "class":









        for subregion_element in class_subregions:
            info_element = subregion_element.find("./info")
            func_info = FunctionInfo(subregion_element)




        pass

    def invoke_metrixpp_collect(self):
        ret = subprocess.call([self.config.get_python27_path(), self.config.get_metrixpp_path(),
                               'collect', '--std.code.lines.total', '--std.code.lines.code',
                               '--std.code.lines.preprocessor',
                               '--std.code.lines.comments', '--std.code.complexity.cyclomatic',
                               '--db-file={0}'.format(self.config.get_path_for_temp_metrixpp_db()),
                               '--log-level=WARNING', '--', self.project_name])
        if ret != 0:
            print("ERROR: metrix++ collect crashed. Status code {0}".format(ret))
            exit(1)
        print("metrix++ collect finished")

    def handle(self):
        self.invoke_metrixpp_collect()
        for src_file in self.src_files:
            self.handle_one_src_file(src_file)
        pass
