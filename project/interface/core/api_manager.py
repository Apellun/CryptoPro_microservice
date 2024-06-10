import json
import requests
from typing import Optional, List, Dict
from project.interface.core import exceptions
from project.interface.utils.const import HTTPMethods, APIEndpoints
from project.interface.config import API_HOST, API_PORT


class ApiManager:
    def __init__(self, host: str, port: int):
        self.api_host = host
        self.api_port = port

    @staticmethod
    def _validate_response_code(response: requests.Response) -> Optional[bool]:#<Response [400]> {"message":"Организация с таким ИНН или именем уже существует в базе [Crypto API]"}
        if response.status_code == 200:
            return True
        elif response.status_code == 500:
            raise exceptions.InternalAPIError
        elif response.status_code == 400: #422!!!
            if response.text.startswith('{"message":"Организация'): #TODO: change to code validation
                raise exceptions.OrgDataIntegrityError(response.text)
        raise exceptions.ResponseCodeError(response.status_code, response.reason)

    def _send_request(self, method: str, endpoint: str = None,
                      request_body: Optional[Dict] = None)\
            -> requests.Response:
        url = APIEndpoints.get_full_address(
            api_host=self.api_host,
            api_port=self.api_port,
            endpoint=endpoint
        )
        data = json.dumps(request_body) if request_body else None
        try:
            res = requests.request(
                method,
                url,
                data=data
            )
            if self._validate_response_code(res):
                return res.json()
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            raise exceptions.APIConnectionError
        except Exception: #TODO: find the response exception + add base exception
            raise exceptions.EmptyResponseError

    def get_orgs_list(self) -> requests.Response:
        return self._send_request(
            endpoint=APIEndpoints.ORGANIZATIONS_ENDPOINT,
            method=HTTPMethods.GET
        )

    def get_org_keys(self, org_inn: str) -> requests.Response:
        return self._send_request(
            endpoint=APIEndpoints.get_org_edit_endpoint(org_inn),
            method=HTTPMethods.GET
        )

    def get_all_orgs_keys(self) -> requests.Response:
        return self._send_request(
            endpoint=APIEndpoints.ORGANIZATIONS_ENDPOINT,
            method=HTTPMethods.GET
        )

    def update_server_settings(self, server_host: str, server_port: str)\
            -> requests.Response:
        return self._send_request(
            request_body={
                "host": server_host,
                "port": int(server_port)
            },
            endpoint=APIEndpoints.SERVER_SETTINGS_ENDPOINT,
            method=HTTPMethods.PUT
        )

    def add_org(self, org_inn: str, org_name: Optional[str] = None)\
            -> requests.Response:
        return self._send_request(
            request_body={
                "inn": org_inn,
                "name": org_name
            },
            endpoint=APIEndpoints.ORGANIZATIONS_ENDPOINT,
            method=HTTPMethods.POST
        )

    def update_org(self, old_inn: str, new_inn: str, new_name: str
                   ) -> requests.Response:
        return self._send_request(
            request_body={
                "inn": new_inn,
                "name": new_name
            },
            endpoint=APIEndpoints.get_org_edit_endpoint(old_inn),
            method=HTTPMethods.PUT
        )

    def update_org_keys(self, org_inn: str, new_keys: List[Optional[str]] = None)\
            -> requests.Response:
        return self._send_request(
            request_body={
                "keys": new_keys
            },
            endpoint=APIEndpoints.get_org_edit_endpoint(org_inn),
            method=HTTPMethods.PATCH
        )

    def delete_org(self, org_inn: str) -> requests.Response:
        return self._send_request(
            endpoint=APIEndpoints.get_org_edit_endpoint(org_inn),
            method=HTTPMethods.DELETE
        )


api_manager = ApiManager(API_HOST, API_PORT)