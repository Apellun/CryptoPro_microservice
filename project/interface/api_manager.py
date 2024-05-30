import json
import requests
from typing import Optional, List, Dict
from project.interface import exceptions
from project.interface.utils.const import HTTPMethodsStr, APIEndpoints, Const


class ApiManager:
    def __init__(self, host: str, port: int):
        self.api_host = host
        self.api_port = port

    @staticmethod
    def _check_response_code(response: requests.Response) -> Optional[bool]:#<Response [400]> {"message":"Организация с таким ИНН или именем уже существует в базе [Crypto API]"}
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
            api_host=self.api_host, api_port=self.api_port,
            endpoint=endpoint
        )
        # headers = {
        #     'Content-Type': 'application/json'
        # }
        try:
            if request_body:
                res = requests.request(
                    method,
                    url,
                    # headers=headers,
                    data=json.dumps(request_body)
                )
            else:
                res = requests.request(
                    method,
                    url,
                    # headers=headers,
                )
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            raise exceptions.APIConnectionError

        if self._check_response_code(res):
            if res.content:
                try:
                    return res.json()
                except Exception:
                    raise exceptions.EmptyResponseError

    def get_org_list(self) -> requests.Response:
        return self._send_request(
            endpoint=APIEndpoints.organizations_endpoint,
            method=HTTPMethodsStr.get
        )

    def get_org_keys(self, org_inn: str) -> requests.Response:
        return self._send_request(
            endpoint=APIEndpoints.get_org_edit_endpoint(org_inn),
            method=HTTPMethodsStr.get
        )

    def get_all_orgs_keys(self) -> requests.Response:
        return self._send_request(
            endpoint=APIEndpoints.organizations_endpoint,
            method=HTTPMethodsStr.get
        )

    def update_server_settings(self, server_host: str, server_port: str)\
            -> requests.Response:
        return self._send_request(
            request_body={
                Const.host_index: server_host,
                Const.port_index: int(server_port)
            },
            endpoint=APIEndpoints.server_settings_endpoint,
            method=HTTPMethodsStr.put
        )

    def add_org(self, org_inn: str, org_name: Optional[str] = None)\
            -> requests.Response:
        return self._send_request(
            request_body={
                Const.org_inn_index: org_inn,
                Const.org_name_index: org_name
            },
            endpoint=APIEndpoints.organizations_endpoint,
            method=HTTPMethodsStr.post
        )

    def update_org(self, old_inn: str, new_org_details: Dict) -> requests.Response:
        return self._send_request(
            request_body={
                Const.org_inn_index: new_org_details[Const.org_inn_index],
                Const.org_name_index: new_org_details[Const.org_name_index]
            },
            endpoint=APIEndpoints.get_org_edit_endpoint(old_inn),
            method=HTTPMethodsStr.put
        )

    def delete_org(self, org_inn: str) -> requests.Response:
        return self._send_request(
            endpoint=APIEndpoints.get_org_edit_endpoint(org_inn),
            method=HTTPMethodsStr.delete
        )

    def update_org_keys(self, org_inn: str, new_keys: List[Optional[object]] = None)\
            -> requests.Response:
        return self._send_request(
            request_body={
                Const.key_list_index: new_keys
            },
            endpoint=APIEndpoints.get_org_edit_endpoint(org_inn),
            method=HTTPMethodsStr.patch
        )


manager = ApiManager(Const.api_host, Const.api_port)