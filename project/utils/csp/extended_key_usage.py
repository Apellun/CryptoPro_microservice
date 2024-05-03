class CspExtendedKeyUsage:
    def __init__(self, key_obj):
        self._obj = key_obj

    @property
    def EKUs(self):
        return self._obj.EKUs

    @property
    def IsCritical(self) -> bool:
        return self._obj.IsCritical

    @property
    def IsPresent(self) -> bool:
        return self._obj.IsPresent
