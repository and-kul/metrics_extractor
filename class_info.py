class ClassInfo:
    def __init__(self, short_name):
        self.offset = None
        self.id = None
        self.short_name = short_name
        self.total_lines = None
        self.own_code_lines = None
        self.own_comment_lines = None
        self.outer_class_info = None
