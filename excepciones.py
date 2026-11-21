# Jerarquía de excepciones personalizadas para el dominio de Software FJ.
# Permite distinguir errores de validación, parámetros, disponibilidad, reservas y cálculos.

class ErrorSoftwareFJ(Exception):
    """Excepción base del sistema para agrupar cualquier error controlado del dominio."""  # Heredamos de Exception para crear una familia propia de errores


class DatoInvalidoError(ErrorSoftwareFJ):
    """Se lanza cuando un dato tiene formato, rango o tipo incorrecto."""  # Error de validación de contenido/formato


class ParametroFaltanteError(ErrorSoftwareFJ):
    """Se lanza cuando falta un dato o parámetro obligatorio."""  # Error por campos vacíos, nulos o ausentes


class ServicioNoDisponibleError(ErrorSoftwareFJ):
    """Se lanza cuando un servicio no está disponible para ser reservado o confirmado."""  # Error de estado del servicio


class OperacionReservaError(ErrorSoftwareFJ):
    """Se lanza cuando falla el registro, confirmación, cancelación o procesamiento."""  # Error en el flujo de operaciones


class CalculoInconsistenteError(ErrorSoftwareFJ):
    """Se lanza cuando un valor numérico o fórmula produce un resultado inválido."""  # Error en tarifas, duraciones o porcentajes