from abc import ABC, abstractmethod  # Importa herramientas para definir clases abstractas y métodos obligatorios
import re  # Importa expresiones regulares para validar formatos de correo y teléfono
from excepciones import DatoInvalidoError, ParametroFaltanteError  # Importa excepciones personalizadas del dominio


class EntidadBase(ABC):
    """Clase abstracta base para entidades generales del sistema."""  # Define la plantilla común de las entidades

    def __init__(self, id_entidad: str) -> None:
        if not id_entidad or not str(id_entidad).strip():  # Verifica que el ID no venga vacío ni solo con espacios
            raise ParametroFaltanteError("El identificador de la entidad es obligatorio.")  # Lanza error si falta el ID
        self._id = str(id_entidad).strip()  # Guarda el ID limpio como atributo protegido

    @property
    def id(self) -> str:
        return self._id  # Expone el ID de solo lectura mediante propiedad

    @abstractmethod
    def resumen(self) -> str:
        """Retorna una representación resumida de la entidad."""  # Obliga a las subclases a implementar su propio resumen


class Cliente(EntidadBase):
    """Representa un cliente con encapsulación de datos y validaciones estrictas."""  # Hereda de EntidadBase

    def __init__(self, id_cliente: str, nombre: str, correo: str, telefono: str) -> None:
        super().__init__(id_cliente)  # Inicializa y valida el ID en EntidadBase
        self._nombre = ""  # Inicializa atributo protegido para el nombre
        self._correo = ""  # Inicializa atributo protegido para el correo
        self._telefono = ""  # Inicializa atributo protegido para el teléfono

        self.nombre = nombre  # Asigna el nombre pasando por su setter de validación
        self.correo = correo  # Asigna el correo pasando por su setter de validación
        self.telefono = telefono  # Asigna el teléfono pasando por su setter de validación

    @property
    def nombre(self) -> str:
        return self._nombre  # Retorna el nombre encapsulado

    @nombre.setter
    def nombre(self, valor: str) -> None:
        if valor is None or not str(valor).strip():  # Comprueba que el nombre no esté vacío
            raise ParametroFaltanteError("El nombre del cliente es obligatorio.")  # Falla si no se envió nombre
        limpio = str(valor).strip()  # Elimina espacios sobrantes en los extremos
        if len(limpio) < 3:  # Exige una longitud mínima razonable
            raise DatoInvalidoError("El nombre del cliente debe tener al menos 3 caracteres.")  # Rechaza nombres muy cortos
        self._nombre = limpio  # Guarda el nombre validado

    @property
    def correo(self) -> str:
        return self._correo  # Retorna el correo encapsulado

    @correo.setter
    def correo(self, valor: str) -> None:
        if valor is None or not str(valor).strip():  # Comprueba que el correo no esté vacío
            raise ParametroFaltanteError("El correo electrónico del cliente es obligatorio.")  # Falla si falta el correo
        limpio = str(valor).strip()  # Limpia espacios alrededor del correo
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", limpio):  # Valida estructura básica usuario@dominio.ext
            raise DatoInvalidoError(f"Correo electrónico inválido: '{limpio}'.")  # Lanza error si el formato no coincide
        self._correo = limpio  # Guarda el correo validado

    @property
    def telefono(self) -> str:
        return self._telefono  # Retorna el teléfono encapsulado

    @telefono.setter
    def telefono(self, valor: str) -> None:
        if valor is None or not str(valor).strip():  # Comprueba que el teléfono no esté vacío
            raise ParametroFaltanteError("El teléfono del cliente es obligatorio.")  # Falla si falta el teléfono
        digitos = re.sub(r"[\s\-+()]", "", str(valor))  # Quita guiones, espacios, paréntesis y signos +
        if not digitos.isdigit() or len(digitos) < 7:  # Verifica que solo queden dígitos y al menos 7 caracteres
            raise DatoInvalidoError(f"Teléfono inválido: '{valor}'. Debe tener al menos 7 dígitos.")  # Error si no es válido
        self._telefono = digitos  # Guarda el teléfono limpio

    def resumen(self) -> str:
        return f"Cliente[{self.id}] {self._nombre} | Correo: {self._correo} | Tel: {self._telefono}"  # Formatea resumen