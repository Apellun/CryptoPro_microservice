class MainText:
    main_window_title = 'Привязка ключей к ИНН'
    browse_keys_tab_title = "Доступные ключи"
    org_list_tab_title = "Список организаций"
    server_details_tab_title = "Настройки сервера"

    success_title = "Успешно"
    success_message = "Настройки успешно изменены."
    error_title = "Ошибка"
    error_message = "Неизвестная ошибка"
    in_progress_title = "Подождите"
    in_progress_message = "Сохраняем настройки..."
    process_finished = "Настройки успешно сохранены"
    confirm_action = "Подтвердите действие"
    continue_action = "Продолжить"
    discard_action = "Отмена"

    inn_validation_error = "Некорерктный ИНН, проверьте правильность заполнения."
    api_connection_error = "Ошибка подключения к API."
    empty_response_error = "Пустой ответ от API."
    internal_api_error = "Ошибка API."

    @staticmethod
    def get_response_code_error(code: int, response_message: str):
        return f"Неправильный запрос к API:\n{code}:{response_message}."


class BrowseKeysText:
    org_label = "Организация:"
    browse_keys_label = "Доступные ключи:"
    refresh_keys_button = "Обновить список доступных ключей"
    bind_key_button = "Использовать выбранные ключи для организации"


class OrgListText:
    add_org_button = "Добавить организацию"

    @staticmethod
    def get_confirm_delete_message(org_inn: str) -> str:
        return f"Удалить организацию с ИНН {org_inn}?"


class ConfigureServerText:
    host_label = "Адрес:"
    port_label = "Порт:"
    save_button = "Сохранить"
    empty_field_error = "Значения полей не могут быть пустыми."
    port_validation_error = 'Убедитесь, что в поле "порт" только цифры'


class AddOrgText:
    inn_label = "Новый ИНН:"
    org_name_label = "Название организации:"
    add_org_button = "Добавить организацию"
    org_added = "Организация успешно добавлена."
    empty_inn_error = "Поле 'ИНН' не может быть пустым."


