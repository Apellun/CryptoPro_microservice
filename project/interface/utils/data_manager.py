class DataManager: #TODO: refactor to simple methods
    @staticmethod
    def get_org_string(org_inn: str, org_name: str = None) -> str:
        return f"{org_inn} ({org_name})" if org_name else f"{org_inn}"

    @staticmethod
    def get_org_inn(org_str: str) -> str:
        return org_str.split(' ')[0]


data_manager = DataManager()