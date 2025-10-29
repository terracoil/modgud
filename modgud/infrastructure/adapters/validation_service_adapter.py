
from modgud.domain.ports.validation_service_port import ValidationServicePort
from modgud.infrastructure.adapters.validation_service_adapter import ValidationServiceAdapter

class ValidationServiceAdapter(ValidationServicePort):
    def __init__(self, impl: ValidationService | None = None):
        self._impl = impl or ValidationService()

    def get_error_message(self, message_key, **kwargs):
        return self._impl.get_error_message(message_key, kwargs)


    def create_guard_function(self, validation_logic, error_message):
        return self._impl.create_guard_function(validation_logic, error_message)

