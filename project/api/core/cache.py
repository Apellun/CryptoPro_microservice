from datetime import datetime, timedelta
from typing import Optional, List
from sqlalchemy.exc import MissingGreenlet
from project.api.core.db.models import Organization, Key


class ApiCache:
    def __init__(self):
        self.org_cache = None
        self.key_cache = None

    def add_to_org_cache(self, org_inn: int, org: Organization) -> None:
        if not self.org_cache:
            self.org_cache = {}
        self.org_cache[org_inn] = (org, datetime.now())
        self.add_to_key_cache(org_inn, org.keys)

    def get_cached_keys(self, org_inn: int) -> List[Optional[Key]]:
        if self.key_cache:
            org_keys_cache = self.key_cache.get(org_inn, None)
            if org_keys_cache and datetime.now() - org_keys_cache[1] < timedelta(minutes=15):
                return org_keys_cache[0]

    def add_to_key_cache(self, org_inn: int, keys: List[Optional[Key]]):
        if not self.key_cache:
            self.key_cache = {}
        self.key_cache[org_inn] = (keys, datetime.now())


api_cache = ApiCache()