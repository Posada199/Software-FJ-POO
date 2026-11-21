from abc import ABC, abstractmethod  # Permite crear clases abstractas y métodos obligatorios
from excepciones import (  # Importa las excepciones específicas para validar servicios y cálculos
    CalculoInconsistenteError,
    DatoInvalidoError,
    ParametroFaltanteError,
    ServicioNoDisponibleError,
)


class Servicio(ABC):
    """Clase abstracta base para los servicios ofrecidos por Software FJ."""  # Define interfaz común y lógica base

    def __init__(self, codigo: str, nombre: str, tarifa_base: float, disponible: bool = True) -> None:
        if not codigo or not str(codigo).strip():  # Valida que el código del servicio exista
            raise ParametroFaltanteError("El código del servicio es obligatorio.")  # Error si falta código
        if not nombre or not str(nombre).strip():  # Valida que el nombre del servicio exista
            raise ParametroFaltanteError("El nombre del servicio es obligatorio.")  # Error si falta nombre
        self._codigo = str(codigo).strip()  # Guarda código normalizado
        self._nombre = str(nombre).strip()  # Guarda nombre normalizado
        self._tarifa_base = 0.0  # Inicializa tarifa base antes de validarla con el setter
        self.tarifa_base = tarifa_base  # Valida y asigna la tarifa base inicial
        self._disponible = bool(disponible)  # Define si el servicio está disponible para reservar

    @property
    def codigo(self) -> str:
        return self._codigo  # Devuelve el código del servicio

    @property
    def nombre(self) -> str:
        return self._nombre  # Devuelve el nombre del servicio

    @property
    def tarifa_base(self) -> float:
        return self._tarifa_base  # Devuelve la tarifa base actual

    @tarifa_base.setter
    def tarifa_base(self, valor: float) -> None:
        try:
            monto = float(valor)  # Convierte la tarifa a número decimal flotante
        except (TypeError, ValueError) as exc:
            raise DatoInvalidoError("La tarifa base debe ser un valor numérico.") from exc  # Encadena error de conversión
        if monto <= 0:  # Impide tarifas cero o negativas
            raise CalculoInconsistenteError("La tarifa base debe ser mayor que cero.")  # Error de inconsistencia numérica
        self._tarifa_base = monto  # Guarda la tarifa válida

    @property
    def disponible(self) -> bool:
        return self._disponible  # Indica si el servicio está libre

    @disponible.setter
    def disponible(self, estado: bool) -> None:
        self._disponible = bool(estado)  # Actualiza el estado de disponibilidad como booleano

    def validar_disponibilidad(self) -> None:
        if not self._disponible:  # Verifica si el servicio está ocupado o deshabilitado
            raise ServicioNoDisponibleError(  # Lanza excepción si no puede usarse
                f"El servicio '{self._nombre}' ({self._codigo}) no está disponible actualmente."
            )

    @abstractmethod
    def validar_parametros(self, duracion: float, **kwargs) -> None:
        """Valida parámetros específicos de cada tipo de servicio."""  # Cada subclase define sus reglas de duración

    @abstractmethod
    def describir(self) -> str:
        """Describe las características del servicio."""  # Cada subclase formatea su descripción de forma polimórfica

    @abstractmethod
    def _calcular_subtotal(self, duracion: float, **kwargs) -> float:
        """Calcula el subtotal base según la lógica del servicio."""  # Calcula subtotal antes de descuentos o impuestos

    # --- Variantes sobrecargadas de cálculo de costo ---
    def calcular_costo(self, duracion: float, descuento_pct: float = 0.0, impuesto_pct: float = 0.0, **kwargs) -> float:
        """Calcula el costo total admitiendo descuento e impuesto opcionales."""  # Variante general con parámetros opcionales
        self.validar_parametros(duracion, **kwargs)  # Valida duración y parámetros extra del servicio
        subtotal = self._calcular_subtotal(duracion, **kwargs)  # Obtiene el subtotal según el tipo de servicio
        return self._aplicar_ajustes(subtotal, descuento_pct=descuento_pct, impuesto_pct=impuesto_pct)  # Aplica ajustes

    def calcular_costo_con_descuento(self, duracion: float, descuento_pct: float, **kwargs) -> float:
        """Variante enfocada en aplicar un porcentaje de descuento."""  # Calcula aplicando solo descuento
        return self.calcular_costo(duracion, descuento_pct=descuento_pct, impuesto_pct=0.0, **kwargs)

    def calcular_costo_con_impuesto(self, duracion: float, impuesto_pct: float, **kwargs) -> float:
        """Variante enfocada en aplicar un porcentaje de impuesto."""  # Calcula aplicando solo impuesto
        return self.calcular_costo(duracion, descuento_pct=0.0, impuesto_pct=impuesto_pct, **kwargs)

    def _aplicar_ajustes(self, subtotal: float, descuento_pct: float = 0.0, impuesto_pct: float = 0.0) -> float:
        try:
            desc = float(descuento_pct)  # Convierte el descuento a flotante
            imp = float(impuesto_pct)  # Convierte el impuesto a flotante
        except (TypeError, ValueError) as exc:
            raise CalculoInconsistenteError("Los porcentajes de descuento/impuesto deben ser numéricos.") from exc  # Encadena

        if subtotal < 0:  # Evita subtotales negativos
            raise CalculoInconsistenteError("El subtotal no puede ser negativo.")
        if not (0.0 <= desc < 100.0):  # Valida que el descuento esté en un rango porcentual válido
            raise CalculoInconsistenteError("El porcentaje de descuento debe estar entre 0 y 99.9.")
        if imp < 0.0:  # Evita impuestos negativos
            raise CalculoInconsistenteError("El porcentaje de impuesto no puede ser negativo.")

        con_descuento = subtotal * (1.0 - desc / 100.0)  # Resta el porcentaje de descuento al subtotal
        total = con_descuento * (1.0 + imp / 100.0)  # Suma el porcentaje de impuesto sobre el monto con descuento
        if total < 0:  # Verifica coherencia final del total
            raise CalculoInconsistenteError("El total calculado es inconsistente (menor que cero).")
        return round(total, 2)  # Redondea a dos decimales para presentación monetaria


class ReservaSala(Servicio):
    """Servicio de reserva de salas (duración en horas)."""  # Subclase especializada en salas

    def __init__(self, codigo: str, nombre: str, tarifa_hora: float, capacidad: int, disponible: bool = True) -> None:
        super().__init__(codigo, nombre, tarifa_hora, disponible=disponible)  # Inicializa atributos base de Servicio
        if capacidad is None or int(capacidad) <= 0:  # Verifica que la sala tenga capacidad positiva
            raise DatoInvalidoError("La capacidad de la sala debe ser mayor que cero.")
        self._capacidad = int(capacidad)  # Guarda capacidad máxima de personas

    def validar_parametros(self, duracion: float, **kwargs) -> None:
        try:
            horas = float(duracion)  # Convierte la duración a horas
        except (TypeError, ValueError) as exc:
            raise DatoInvalidoError("La duración en horas debe ser numérica.") from exc  # Encadena error de tipo
        if horas <= 0 or horas > 24:  # Restringe la reserva de sala a un rango de 0.5 a 24 horas
            raise CalculoInconsistenteError("La reserva de sala debe durar entre 0.5 y 24 horas.")

    def _calcular_subtotal(self, duracion: float, **kwargs) -> float:
        return self._tarifa_base * float(duracion)  # Multiplica tarifa por hora por la cantidad de horas

    def describir(self) -> str:
        estado = "Disponible" if self._disponible else "No disponible"  # Traduce estado booleano a texto
        return (
            f"[Sala] {self._codigo} - {self._nombre} | Cap: {self._capacidad} personas | "
            f"Tarifa/h: ${self._tarifa_base:.2f} | {estado}"
        )


class AlquilerEquipo(Servicio):
    """Servicio de alquiler de equipos tecnológicos (duración en días)."""  # Subclase especializada en alquiler de equipos

    def __init__(self, codigo: str, nombre: str, tarifa_dia: float, tipo_equipo: str, disponible: bool = True) -> None:
        super().__init__(codigo, nombre, tarifa_dia, disponible=disponible)  # Inicializa atributos comunes
        if not tipo_equipo or not str(tipo_equipo).strip():  # Exige especificar el tipo de equipo
            raise ParametroFaltanteError("El tipo de equipo es obligatorio.")
        self._tipo_equipo = str(tipo_equipo).strip()  # Guarda el tipo de equipo limpio

    def validar_parametros(self, duracion: float, **kwargs) -> None:
        try:
            dias = float(duracion)  # Convierte la duración a días
        except (TypeError, ValueError) as exc:
            raise DatoInvalidoError("La duración en días debe ser numérica.") from exc  # Encadena error de tipo
        if dias < 1 or dias > 365:  # Valida que el alquiler esté entre 1 y 365 días
            raise CalculoInconsistenteError("El alquiler de equipo debe ser de 1 a 365 días.")

    def _calcular_subtotal(self, duracion: float, **kwargs) -> float:
        dias = float(duracion)  # Obtiene número de días
        recargo = 15.0 if dias == 1 else 0.0  # Aplica recargo fijo de $15 si es alquiler de un solo día
        return (self._tarifa_base * dias) + recargo  # Calcula subtotal diario más recargo si aplica

    def describir(self) -> str:
        estado = "Disponible" if self._disponible else "No disponible"  # Estado legible del equipo
        return (
            f"[Equipo] {self._codigo} - {self._nombre} ({self._tipo_equipo}) | "
            f"Tarifa/día: ${self._tarifa_base:.2f} | {estado}"
        )


class AsesoriaEspecializada(Servicio):
    """Servicio de asesoría técnica especializada (duración en horas)."""  # Subclase especializada en asesorías

    def __init__(self, codigo: str, nombre: str, tarifa_hora: float, especialidad: str, disponible: bool = True) -> None:
        super().__init__(codigo, nombre, tarifa_hora, disponible=disponible)  # Inicializa clase padre
        if not especialidad or not str(especialidad).strip():  # Verifica que se indique la especialidad
            raise ParametroFaltanteError("La especialidad de la asesoría es obligatoria.")
        self._especialidad = str(especialidad).strip()  # Guarda especialidad limpia

    def validar_parametros(self, duracion: float, **kwargs) -> None:
        try:
            horas = float(duracion)  # Convierte la duración a horas
        except (TypeError, ValueError) as exc:
            raise DatoInvalidoError("Las horas de asesoría deben ser numéricas.") from exc  # Encadena error de tipo
        if horas < 1 or horas > 200:  # Limita la asesoría entre 1 y 200 horas
            raise CalculoInconsistenteError("La asesoría especializada debe ser de 1 a 200 horas.")

    def _calcular_subtotal(self, duracion: float, **kwargs) -> float:
        return self._tarifa_base * float(duracion)  # Calcula costo base por horas de asesoría

    def describir(self) -> str:
        estado = "Disponible" if self._disponible else "No disponible"  # Estado legible de la asesoría
        return (
            f"[Asesoría] {self._codigo} - {self._nombre} [{self._especialidad}] | "
            f"Tarifa/h: ${self._tarifa_base:.2f} | {estado}"
        )