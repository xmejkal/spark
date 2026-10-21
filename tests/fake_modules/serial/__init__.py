"""Fake pyserial for the bench goldens (P380): a port that opens and reads nothing, for ConsoleProbe's script."""


class SerialException(OSError):
    pass


class Serial:
    def __init__(self, *args, **kwargs):
        self.port = None

    def open(self):
        pass

    def read(self, size=1):
        return b""

    def close(self):
        pass
