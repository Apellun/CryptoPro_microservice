from typing import Dict, Optional
from PySide6.QtWidgets import QWidget
from project.interface.utils.const import Const


class DataManager:
    @staticmethod
    def get_org_updated_dict(
            new_org_name: str, new_inn: str,
            old_inn: str, widget: QWidget
    ) -> Dict[str, Optional[Dict | str | QWidget]]:
        return {
                Const.updated_org_index: {
                    Const.org_name_index: new_org_name,
                    Const.org_inn_index: new_inn},
                Const.previous_org_index: old_inn,
                Const.widget_index: widget
        }

    @staticmethod
    def get_org_string(org: Dict) -> str:
        name = org.get(Const.org_name_index, None)
        if name:
            return f"{
                org[Const.org_inn_index]
            } ({
                org[Const.org_name_index]
            })"
        return f"{org[Const.org_inn_index]}"

    @staticmethod
    def get_org_inn(org_str: str) -> str:
        return org_str.split(' ')[0]


data_manager = DataManager()