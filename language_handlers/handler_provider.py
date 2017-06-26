from typing import Union, Type

from info.project_info import ProjectInfo
from language_handlers.base_handler import BaseHandler
from language_handlers.metrixpp_handler import MetrixppHandler


class HandlerProvider:

    from_language_to_handler_class = {
        "Java": MetrixppHandler,
        "C#": MetrixppHandler
    }


    def __init__(self, project_info: ProjectInfo, conn):
        self.project_info = project_info
        self.conn = conn
        self.__handlers_pool = {}


    def get_handler_for_language(self, language: str) -> Union[BaseHandler, None]:
        if language in self.__handlers_pool:
            return self.__handlers_pool[language]
        else:
            if language not in HandlerProvider.from_language_to_handler_class:
                return None
            else:
                handler_class: Type[BaseHandler] = HandlerProvider.from_language_to_handler_class[language]
                self.__handlers_pool[language] = handler_class(self.project_info, self.conn)
                return self.__handlers_pool[language]


