class CspBasicConstraints:
    def __init__(self, basic_constraint):
        self._bs = basic_constraint

    @property
    def IsCertificateAuthority(self) -> bool:
        return self._bs.IsCertificateAuthority

    @property
    def IsCritical(self) -> bool:
        return self._bs.IsCritical

    @property
    def IsPathLenConstraintPresent(self) -> bool:
        return self._bs.IsPathLenConstraintPresent

    @property
    def IsPresent(self) -> bool:
        return self._bs.IsPresent

    @property
    def PathLenConstraint(self) -> int:
        return self._bs.PathLenConstraint
