from enum import IntEnum
from project.utils.csp.certificate import CspCertificate


class CspFindCriteria(IntEnum):
    """Returns certificates matching a specified SHA1 hash."""
    CAPICOM_CERTIFICATE_FIND_SHA1_HASH = 0
    """Returns certificates whose subject name exactly 
    or partially matches a specified subject name."""
    CAPICOM_CERTIFICATE_FIND_SUBJECT_NAME = 1
    """Returns certificates whose issuer name exactly 
    or partially matches a specified issuer name."""
    CAPICOM_CERTIFICATE_FIND_ISSUER_NAME = 2
    """Returns certificates whose root subject name exactly 
    or partially matches a specified root subject name."""
    CAPICOM_CERTIFICATE_FIND_ROOT_NAME = 3
    """Returns certificates whose template name 
    matches a specified template name."""
    CAPICOM_CERTIFICATE_FIND_TEMPLATE_NAME = 4
    """Returns certificates that have an extension 
    that matches a specified extension."""
    CAPICOM_CERTIFICATE_FIND_EXTENSION = 5
    """Returns certificates that have an extended property 
    whose property identifier matches a specified property identifier."""
    CAPICOM_CERTIFICATE_FIND_EXTENDED_PROPERTY = 6
    """Returns certificates in the store that have either 
    an enhanced key usage extension or property 
    combined with a usage identifier."""
    CAPICOM_CERTIFICATE_FIND_APPLICATION_POLICY = 7
    """Returns certificates containing a specified policy OID."""
    CAPICOM_CERTIFICATE_FIND_CERTIFICATE_POLICY = 8
    """Returns certificates whose time is valid."""
    CAPICOM_CERTIFICATE_FIND_TIME_VALID = 9
    """Returns certificates whose time is not yet valid."""
    CAPICOM_CERTIFICATE_FIND_TIME_NOT_YET_VALID = 10
    """Returns certificates whose time has expired."""
    CAPICOM_CERTIFICATE_FIND_TIME_EXPIRED = 11
    """Returns certificates containing a key that 
    can be used in the specified manner."""
    CAPICOM_CERTIFICATE_FIND_KEY_USAGE = 12


class CspCertificates:
    def __init__(self, certs_store):
        self._certs = certs_store
        self._c = 1

    @property
    def certs(self):
        return self._certs

    @staticmethod
    def _get_certs_list(certs) -> list[CspCertificate]:
        result = []
        if certs.Count == 0:
            return result

        for i in range(1, certs.Count + 1):
            cert_item = certs.Item(i)
            result.append(CspCertificate(cert_item))
        return result

    def Find(
        self, find_type: CspFindCriteria, criteria: str,
        find_valid_only: bool = False
    ) -> list[CspCertificate]:
        found_certs = self._certs.Find(find_type, criteria, find_valid_only)
        return self._get_certs_list(found_certs)

    @property
    def Count(self) -> int:
        return self._certs.Count

    def Item(self, index: int) -> CspCertificate:
        cert = self._certs.Item(index)
        return CspCertificate(cert)

    def __iter__(self):
        self._c = 1
        return self

    def __next__(self):
        if self._c > self.Count:
            raise StopIteration
        item = self.Item(self._c)
        self._c += 1
        return item
