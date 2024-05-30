class Const:
    main_window_min_height = 600
    main_window_geometry = (100, 100, 600, 400)

    org_list_margins = (0, 0, 0, 0)
    org_list_layout_spacing = 10
    org_list_button_spacing = 5
    org_list_button_size = (16, 16)
    org_list_layout_label_index = 1
    org_list_layout_buttons_index = 0
    org_list_buttons_edit_index = 1
    org_list_buttons_delete_index = 0

    browse_keys_spacing = 15
    browse_keys_margins = (0, 0, 0, 0)
    browse_keys_key_layout_stretch = 1
    browse_keys_key_widget_label_index = 1
    browse_keys_key_widget_checkbox_index = 0
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

    api_host = "localhost"
    api_port = 9080


class HTTPMethodsStr:
    get = "GET"
    post = "POST"
    put = "PUT"
    patch = "PATCH"
    delete = "DELETE"


class APIEndpoints:
    organizations_endpoint = "organizations"
    server_settings_endpoint = "server_settings"

    @staticmethod
    def get_org_edit_endpoint(org_inn: str) -> str:
        return f"organizations/{org_inn}"

    @staticmethod
    def get_full_address(api_host: str, api_port: int, endpoint: str):
        return f"http://{api_host}:{api_port}/{endpoint}"