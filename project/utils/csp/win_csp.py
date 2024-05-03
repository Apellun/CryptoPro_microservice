from base64 import b64encode
from win32com.client import Dispatch
from project.utils.csp.certificate import CspCertificate
from project.utils.csp.certificates import CspCertificates, CspFindCriteria
from project.utils.csp.protocol import DmcCsp
import pythoncom


def pythoncom_wrapper(func):
    def wrapper(*args, **kwargs):
        pythoncom.CoInitialize()
        try:
            return func(*args, **kwargs)
        finally:
            pythoncom.CoUninitialize()
    return wrapper


class WinCspManager(DmcCsp):
    @property
    def _certs(self) -> CspCertificates:
        store = Dispatch("CAdESCOM.Store")
        store.Open(2, "MY", 0)
        certs = CspCertificates(store.Certificates)
        store.Close()
        return certs

    @pythoncom_wrapper
    def certificates(
        self, include_invalid: bool = False
    ) -> list[CspCertificate]: # список доступных сертификатов
        certs = self._certs
        if include_invalid:
            return [cert for cert in certs]
        return [cert for cert in certs if cert.IsValid()]

    @pythoncom_wrapper
    def cert(self, thumbprint: str) -> CspCertificate | None:
        certs = self._certs
        certs = certs.Find(
            CspFindCriteria.CAPICOM_CERTIFICATE_FIND_SHA1_HASH,
            thumbprint
        ) # сертификат по отпечатку
        if not certs:
            return None
        return certs[0]

    @staticmethod
    def _get_signer(cert: CspCertificate):
        cp_signer = Dispatch("CAdESCOM.CPSigner")
        cp_signer.Certificate = cert.cert
        return cp_signer

    @staticmethod
    def _get_signed():
        signed_data = Dispatch("CAdESCOM.CadesSignedData")
        signed_data.ContentEncoding = 1
        return signed_data

    @staticmethod
    def _encode_data(data: str) -> str:
        return b64encode(data.encode("utf-8")).decode("utf-8")

    @staticmethod
    def _strip(data: str) -> str:
        data_no_newline = data.replace("\n", "")
        final_data = data_no_newline.replace("\r", "")
        return final_data

    @pythoncom_wrapper
    def sign(
        self, data: str, cert: CspCertificate, detached: bool = False
    ) -> str: #подписать
        cp_signer = self._get_signer(cert)

        cp_signed = self._get_signed()
        cp_signed.Content = self._encode_data(data)
        signed_data = cp_signed.SignCades(cp_signer, 1, detached)

        final_data = self._strip(signed_data)
        return final_data
