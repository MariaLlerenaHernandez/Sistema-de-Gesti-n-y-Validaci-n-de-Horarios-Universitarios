"""
Excepciones de dominio propias del sistema. Se traducen a respuestas
HTTP estructuradas en app/core/error_handlers.py
"""


class DomainError(Exception):
    """Error base de reglas de negocio."""

    def __init__(self, message: str, code: str = "DOMAIN_ERROR"):
        self.message = message
        self.code = code
        super().__init__(message)


class EntidadNoEncontradaError(DomainError):
    def __init__(self, entidad: str, identificador):
        super().__init__(
            f"{entidad} con identificador '{identificador}' no fue encontrado.",
            code="ENTIDAD_NO_ENCONTRADA",
        )


class EntidadDuplicadaError(DomainError):
    def __init__(self, entidad: str, campo: str, valor):
        super().__init__(
            f"Ya existe {entidad} con {campo} = '{valor}'.",
            code="ENTIDAD_DUPLICADA",
        )


class ReferenciaInvalidaError(DomainError):
    def __init__(self, mensaje: str):
        super().__init__(mensaje, code="REFERENCIA_INVALIDA")


class ArchivoInvalidoError(DomainError):
    def __init__(self, mensaje: str):
        super().__init__(mensaje, code="ARCHIVO_INVALIDO")


class ValidacionHorarioError(DomainError):
    def __init__(self, mensaje: str):
        super().__init__(mensaje, code="VALIDACION_HORARIO")
