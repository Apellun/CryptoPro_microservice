from abc import ABC, abstractmethod

from project.utils.csp.certificate import CspCertificate


class DmcCsp(ABC):
    @abstractmethod
    def certificates(
        self, include_invalid: bool = False
    ) -> list[CspCertificate]:
        raise NotImplementedError

    @abstractmethod
    def sign(
        self, data: str, cert: CspCertificate, detached: bool = False
    ) -> str:
        raise NotImplementedError

    @abstractmethod
    def cert(self, thumbprint: str) -> CspCertificate:
        raise NotImplementedError
