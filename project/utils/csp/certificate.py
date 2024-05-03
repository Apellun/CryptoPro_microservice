from datetime import datetime
from enum import Enum
from project.utils.csp.basic_constraints import CspBasicConstraints
from project.utils.csp.extended_key_usage import CspExtendedKeyUsage


class CspEncodingType(Enum):
    CAPICOM_ENCODE_ANY = 0xffffffff
    CAPICOM_ENCODE_BASE64 = 0
    CAPICOM_ENCODE_BINARY = 1


class CspCertInfoType(Enum):
    """Returns the display name of the certificate subject."""
    CAPICOM_CERT_INFO_SUBJECT_SIMPLE_NAME = 0
    """Returns the display name of the issuer of the certificate."""
    CAPICOM_CERT_INFO_ISSUER_SIMPLE_NAME = 1
    """Returns the email address of the certificate subject."""
    CAPICOM_CERT_INFO_SUBJECT_EMAIL_NAME = 2
    """Returns the email address of the issuer of the certificate."""
    CAPICOM_CERT_INFO_ISSUER_EMAIL_NAME = 3
    """Returns the UPN of the certificate subject."""
    CAPICOM_CERT_INFO_SUBJECT_UPN = 4
    """Returns the UPN of the issuer of the certificate."""
    CAPICOM_CERT_INFO_ISSUER_UPN = 5
    """Returns the DNS name of the certificate subject."""
    CAPICOM_CERT_INFO_SUBJECT_DNS_NAME = 6
    """Returns the DNS name of the issuer of the certificate."""
    CAPICOM_CERT_INFO_ISSUER_DNS_NAME = 7


class CspCertificate:
    def __init__(self, certificate):
        self._cert = certificate

    @property
    def cert(self):
        return self._cert

    def BasicConstraints(self) -> CspBasicConstraints:
        return CspBasicConstraints(self._cert.BasicConstraints())

    def Export(
        self, enc_type: CspEncodingType = CspEncodingType.CAPICOM_ENCODE_BASE64
    ) -> str:
        return self._cert.Export(enc_type)

    def ExtendedKeyUsage(self) -> CspExtendedKeyUsage:
        return self._cert.ExtendedKeyUsage()

    def GetInfo(self, info_type: CspCertInfoType) -> str:
        return self._cert.GetInfo(info_type.value)

    def HasPrivateKey(self) -> bool:
        return self._cert.HasPrivateKey()

    def Import(self, encoded_cert: str):
        self._cert.Import(encoded_cert)

    def IsValid(self) -> bool:
        return self._cert.IsValid().Result

    def KeyUsage(self):
        return self._cert.KeyUsage()

    def PublicKey(self):
        return self._cert.PublicKey()

    def Extensions(self):
        return self._cert.Extensions

    def AdditionalStore(self):
        return self._cert.AdditionalStore

    def FindPrivateKey(self):
        return self._cert.FindPrivateKey

    @property
    def IssuerName(self) -> str:
        return self._cert.IssuerName

    @property
    def PrivateKey(self):
        return self._cert.PrivateKey

    @property
    def SerialNumber(self) -> str:
        return self._cert.SerialNumber

    @property
    def SubjectName(self) -> str:
        return self._cert.SubjectName

    @property
    def Thumbprint(self) -> str:
        return self._cert.Thumbprint

    @property
    def ValidFromDate(self):
        return datetime.fromtimestamp(
            self._cert.ValidFromDate.timestamp(),
            tz=self._cert.ValidToDate.tzinfo
        )

    @property
    def ValidToDate(self) -> datetime:
        return datetime.fromtimestamp(
            self._cert.ValidToDate.timestamp(),
            tz=self._cert.ValidToDate.tzinfo
        )

    @property
    def Version(self) -> int:
        return self._cert.Version

    @property
    def SubjectDnsName(self) -> str:
        name = CspCertInfoType.CAPICOM_CERT_INFO_SUBJECT_DNS_NAME
        return self.GetInfo(name)

    @property
    def IssuerDnsName(self) -> str:
        dns_name = CspCertInfoType.CAPICOM_CERT_INFO_ISSUER_DNS_NAME
        return self.GetInfo(dns_name)

    def __str__(self) -> str:
        valid_to = self.ValidToDate.strftime("%d.%m.%Y")
        return (
            f"{self.SubjectDnsName}, {self.IssuerDnsName}, "
            f"до {valid_to} | {self.SubjectName}"
        )
