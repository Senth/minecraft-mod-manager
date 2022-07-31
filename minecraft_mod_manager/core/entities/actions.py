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
        return next(
            (action for action in Actions if action.value == name.lower()), None
        )

    @staticmethod
    def get_all_names_as_list() -> List[str]:
        return [action.value for action in Actions]
