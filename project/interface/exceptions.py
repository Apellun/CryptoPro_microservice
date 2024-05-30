from project.interface.utils.text import MainText


class APIConnectionError(Exception):
    def __init__(self):
        message = MainText.api_connection_error
        super().__init__(message)


class EmptyResponseError(Exception):
    def __init__(self):
        message = MainText.empty_response_error
        super().__init__(message)


class ResponseCodeError(Exception):
    def __init__(self, code, response_message):
        message = MainText.get_response_code_error(
            code, response_message
        )
        super().__init__(message)


class InternalAPIError(Exception):
    def __init__(self):
        message = MainText.internal_api_error
        super().__init__(message)


class OrgDataIntegrityError(Exception):
    def __init__(self, message):
        super().__init__(message)