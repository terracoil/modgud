
from modgud.domain.ports.guard_checker_port import GuardCheckerPort
from modgud.infrastructure.adapters.guard_service_adapter import GuardServiceAdapter

class GuardServiceAdapter(GuardCheckerPort):
    def __init__(self, impl: GuardService | None = None):
        self._impl = impl or GuardService()

    def checker(self, ):
        return self._impl.checker()


    def validate_inputs(self, guards, args, kwargs, on_error, log_enabled):
        return self._impl.validate_inputs(guards, args, kwargs, on_error, log_enabled)

