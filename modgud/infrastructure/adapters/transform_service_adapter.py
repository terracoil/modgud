
from modgud.domain.ports.ast_transformer_port import AstTransformerPort
from modgud.infrastructure.adapters.transform_service_adapter import TransformServiceAdapter

class TransformServiceAdapter(AstTransformerPort):
    def __init__(self, impl: TransformService | None = None):
        self._impl = impl or TransformService()

    def transformer(self, ):
        return self._impl.transformer()


    def transform_to_implicit_return(self, func, func_name):
        return self._impl.transform_to_implicit_return(func, func_name)

