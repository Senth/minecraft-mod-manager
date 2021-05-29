from __future__ import annotations

from enum import Enum
from typing import List, Union


class Actions(Enum):
    install = "install"
    update = "update"
    configure = "configure"
    list = "list"

    @staticmethod
    def from_name(name: str) -> Union[Actions, None]:
        for action in Actions:
            if action.value == name.lower():
                return action
        return None

    @staticmethod
    def get_all_names_as_list() -> List[str]:
        names: List[str] = []
        for action in Actions:
            names.append(action.value)
        return names
