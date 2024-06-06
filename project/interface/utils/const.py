class Const:
    MAIN_WINDOW_HEIGHT = 600
    MAIN_WINDOW_GEOMETRY = (100, 100, 600, 400)

    org_list_margins = (0, 0, 0, 0)
    org_list_layout_spacing = 10
    org_list_button_spacing = 5
    org_list_button_size = (16, 16)
    org_list_layout_label_index = 1
    org_list_layout_buttons_index = 0
    org_list_buttons_edit_index = 1
    org_list_buttons_delete_index = 0

    BROWSE_KEYS_SPACING = 15
    BROWSE_KEYS_MARGINS = (0, 0, 0, 0)
    BROWSE_KEYS_KEY_LAYOUT_STRETCH = 1

    checked_checkbox_state = 2
    unchecked_checkbox_state = 0

    inn_validation_pattern = r"^\d{10,12}$"

    org_inn_index = "inn"
    org_name_index = "name"
    updated_org_index = "updated_org"
    previous_org_index = "previous_org"
    widget_index = "widget"
    key_thumbprint_index = "thumbprint"
    key_list_index = "keys"
    host_index = "host"
    port_index = "port"


class HTTPMethods:
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"


class APIEndpoints:
    ORGANIZATIONS_ENDPOINT = "organizations"
    SERVER_SETTINGS_ENDPOINT = "server_settings"

    @staticmethod
    def get_org_edit_endpoint(org_inn: str) -> str:
        return f"organizations/{org_inn}"

    @staticmethod
    def get_full_address(api_host: str, api_port: int, endpoint: str):
        return f"http://{api_host}:{api_port}/{endpoint}"