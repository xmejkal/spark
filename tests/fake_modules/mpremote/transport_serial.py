"""Fake `mpremote.transport_serial` for the bench goldens (P1007): QUIET_MPREMOTE patches this method and never reaches it."""


class SerialTransport:
    def enter_raw_repl(self, *args, **kwargs):
        pass
