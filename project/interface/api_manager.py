import json
import requests
from typing import Optional, List, Dict
from project.interface import exceptions


class ApiManager:
    def __init__(self, host: str, port: int):
        self.api_host = host
        self.api_port = port

    @staticmethod
    def _check_response_code(response: requests.Response) -> Optional[bool]:#<Response [400]> {"message":"Организация с таким ИНН или именем уже существует в базе [Crypto API]"}
        if response.status_code == 200:
            return True
        elif response.status_code == 500:
            raise exceptions.InternalServerError
        elif response.status_code == 400:
            if response.text.startswith('{"message":"Организация'): #TODO: change to code validation
                raise exceptions.OrgDataIntegrityError(response.text)
        raise exceptions.ResponseCodeError(response.status_code, response.reason)

    def _send_request(self, method: str, endpoint: str = None,
                      request_body: Optional[Dict] = None)\
            -> requests.Response:
        url = f"http://{self.api_host}:{self.api_port}/{endpoint}"
        headers = {
            'Content-Type': 'application/json'
        }
        try:
            if request_body:
                res = requests.request(
                    method,
                    url,
                    headers=headers,
                    data=json.dumps(request_body)
                )
            else:
                res = requests.request(
                    method,
                    url,
                    headers=headers,
                )
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            raise exceptions.ServerConnectionError

        if self._check_response_code(res):
            if res.content:
                try:
                    return res.json()
                except Exception:
                    raise exceptions.EmptyResponseError

    def get_org_list(self) -> requests.Response:
        return self._send_request(
            endpoint="organizations",
            method="GET"
        )

    def get_org_keys(self, org_inn: str) -> requests.Response:
        return self._send_request(
            endpoint=f"organizations/{org_inn}",
            method="GET"
        )

    def get_all_orgs_keys(self) -> requests.Response:
        return self._send_request(
            endpoint=f"organizations/",
            method="GET"
        )

    def update_server_settings(self, server_host: str, server_port: str)\
            -> requests.Response:
        return self._send_request(
            request_body={
                "host": server_host,
                "port": int(server_port)
            },
            endpoint="server_settings/",
            method="PUT"
        )

    def add_org(self, org_inn: str, org_name: Optional[str] = None)\
            -> requests.Response:
        return self._send_request(
            request_body={
                "inn": org_inn,
                "name": org_name
            },
            endpoint="organizations/",
            method="POST"
        )

    def update_org(self, old_inn: str, new_org_details: Dict) -> requests.Response:
        return self._send_request(
            request_body={
                "inn": new_org_details["inn"],
                "name": new_org_details["name"]
            },
            endpoint=f"organizations/{old_inn}",
            method="PUT"
        )

    def delete_org(self, org_inn: str) -> requests.Response:
        return self._send_request(
            endpoint=f"organizations/{org_inn}",
            method="DELETE"
        )

    def update_org_keys(self, org_inn: str, new_keys: List[Optional[object]] = None)\
            -> requests.Response:
        return self._send_request(
            request_body={
                "keys": new_keys
            },
            endpoint=f"organizations/{org_inn}",
            method="PATCH"
        )


manager = ApiManager("localhost", 9080)