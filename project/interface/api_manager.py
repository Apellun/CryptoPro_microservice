import json
import requests
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from project.interface import exceptions


class ApiManager:
    def __init__(self):
        self.api_host = "localhost"
        self.api_port = 8080

        self.inn_to_key_cash = None
        self.org_cash = None

    @staticmethod
    def _check_response_code(response):
        if response.status_code == 200:
            return True
        elif response.status_code == 500:
            raise exceptions.InternalServerError()
        elif response.status_code == 400:
            if response.reason == "Организация с таким ИНН или названием уже существует в базе.":
                raise exceptions.OrgDataIntegrityError(response.reason)
        else:
            raise exceptions.ResponseCodeError(response.status_code, response.reason)

    def _send_request(self, endpoint: str, method: str, request_body: Optional[Dict] = None, request_params: Optional[List] = None):
        url = f"http://{self.api_host}:{self.api_port}{endpoint}"

        if request_params:
            url += "/?"
            num_params = len(request_params)
            for i in range(num_params):
                url += f"{request_params[i]['name']}={request_params[i]['value']}"
                if i < num_params - 1:
                    url += "&"

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
                except Exception as e:
                    raise exceptions.EmptyResponseError

    def get_org_list(self):
        if not self.org_cash:
            response = self._send_request(
                endpoint="/get_org_list",
                method="GET"
            )
            self.org_cash = response
            return response
        else:
            return self.org_cash

    def _get_org_id(self, org_inn: int):
        for org in self.org_cash:
            if org["inn"] == org_inn:
                return org["id"]

    def get_org_keys(self, org_inn: str):
        if self.inn_to_key_cash:
            org_cash = self.inn_to_key_cash.get(org_inn, None)
            if org_cash:
                if datetime.now() - org_cash[1] < timedelta(minutes=15):
                    return self.inn_to_key_cash[org_inn][0]

        org_id = self._get_org_id(int(org_inn))

        response = self._send_request(
            request_params=[{"name": "org_id", "value": org_id}],
            endpoint="/get_org_keys",
            method="GET"
        )
        if not self.inn_to_key_cash:
            self.inn_to_key_cash = {}
        self.inn_to_key_cash[org_inn] = [response, datetime.now()]
        return response

    def update_server_settings(self, server_host: str, server_port: str):
        return self._send_request(
            request_body={
                "host": server_host,
                "port": int(server_port)
            },
            endpoint="/update_server_settings",
            method="PUT"
        )

    def add_org(self, org_inn: str, org_name: Optional[str] = None):
        response = self._send_request(
            request_body={
                "inn": int(org_inn),
                "name": org_name
            },
            endpoint="/add_org",
            method="POST"
        )
        if not self.org_cash:
            self.org_cash = []
        self.org_cash.append(response)

    def add_org_keys(self, org_inn: str, new_keys: Optional[List[str]] = None):
        org_id = self._get_org_id(int(org_inn))

        response = self._send_request(
            request_params=[
                {"name": "org_id",
                 "value": org_id}
            ],
            request_body={
                "keys": new_keys
            },
            endpoint="/add_org_keys",
            method="PUT"
        )
        if not self.inn_to_key_cash:
            self.inn_to_key_cash = {}
        # else:
        #     for inn, keys in self.inn_to_key_cash.items(): #TODO: ???
        #         if inn != org_inn:
        #             for key in keys[0]:
        #                 if key["key"] in new_keys:
        #                     keys[0].remove(key)
        self.inn_to_key_cash[org_inn] = [response["keys"], datetime.now()]

    def delete_org_keys(self, org_inn: str, keys: Optional[List[str]] = None):
        org_id = self._get_org_id(int(org_inn))

        response = self._send_request(
            request_params=[
                {"name": "org_id",
                 "value": org_id}
            ],
            request_body={
                "keys": keys
            },
            endpoint="/delete_org_keys",
            method="PUT"
        )
        if not self.inn_to_key_cash:
            self.inn_to_key_cash = {}
        self.inn_to_key_cash[org_inn] = [response["keys"], datetime.now()]


manager = ApiManager() #TODO: pass api address