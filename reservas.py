from datetime import datetime  # Permite generar marcas de tiempo para cada entrada del log
from pathlib import Path  # Maneja rutas de archivos de forma multiplataforma sin usar base de datos
from entidades import Cliente  # Importa la clase Cliente
from excepciones import (  # Importa las excepciones del sistema
    CalculoInconsistenteError,
    DatoInvalidoError,
    ErrorSoftwareFJ,
    OperacionReservaError,
    ParametroFaltanteError,
)
from servicios import Servicio  # Importa la clase abstracta Servicio


class LoggerEventos:
    """Registra eventos y errores en un archivo de texto sin usar base de datos."""  # Persistencia liviana en log

    def __init__(self, ruta_log: str = "software_fj.log") -> None:
        self.ruta_log = Path(ruta_log)  # Define la ruta del archivo de registro

    def registrar(self, nivel: str, mensaje: str) -> None:
        marca_tiempo = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Obtiene fecha y hora actual
        linea = f"[{marca_tiempo}] [{nivel}] {mensaje}\n"  # Construye la línea formateada del log
        with self.ruta_log.open("a", encoding="utf-8") as archivo:  # Abre el archivo en modo agregar (append)
            archivo.write(linea)  # Escribe el evento o error y cierra automáticamente el archivo al salir del bloque


class Reserva:
    """Integra cliente, servicio, duración y estado, con manejo de ciclo de vida."""  # Modela una reserva

    ESTADOS_VALIDOS = ("PENDIENTE", "CONFIRMADA", "CANCELADA", "PROCESADA")  # Estados permitidos de la reserva

    def __init__(
        self,
        id_reserva: str,
        cliente: Cliente,
        servicio: Servicio,
        duracion: float,
        descuento_pct: float = 0.0,
        impuesto_pct: float = 0.0,
    ) -> None:
        if not id_reserva or not str(id_reserva).strip():  # Verifica que el ID de reserva exista
            raise ParametroFaltanteError("El ID de la reserva es obligatorio.")
        if not isinstance(cliente, Cliente):  # Valida que el cliente sea una instancia de Cliente
            raise DatoInvalidoError("Debe asignarse una instancia válida de Cliente.")
        if not isinstance(servicio, Servicio):  # Valida que el servicio sea una instancia de Servicio
            raise DatoInvalidoError("Debe asignarse una instancia válida de Servicio.")

        servicio.validar_disponibilidad()  # Comprueba disponibilidad del servicio antes de cotizar/crear
        costo = servicio.calcular_costo(duracion, descuento_pct=descuento_pct, impuesto_pct=impuesto_pct)  # Calcula total
        if costo <= 0:  # Verifica que el costo final sea positivo
            raise CalculoInconsistenteError("El costo de la reserva debe ser mayor a cero.")

        self.id_reserva = str(id_reserva).strip()  # Guarda ID limpio de reserva
        self.cliente = cliente  # Asocia objeto Cliente
        self.servicio = servicio  # Asocia objeto Servicio
        self.duracion = float(duracion)  # Guarda duración solicitada
        self.costo_total = costo  # Guarda el costo calculado
        self.estado = "PENDIENTE"  # Inicia toda reserva nueva en estado PENDIENTE

    def confirmar(self) -> None:
        if self.estado == "CANCELADA":  # Impide confirmar una reserva ya cancelada
            raise OperacionReservaError(f"No se puede confirmar la reserva {self.id_reserva}: está cancelada.")
        if self.estado == "PROCESADA":  # Impide confirmar una reserva ya procesada
            raise OperacionReservaError(f"La reserva {self.id_reserva} ya fue procesada.")
        self.servicio.validar_disponibilidad()  # Revisa que el servicio siga disponible
        self.servicio.disponible = False  # Bloquea la disponibilidad mientras se confirma la reserva
        self.estado = "CONFIRMADA"  # Actualiza estado a CONFIRMADA

    def cancelar(self, motivo: str = "Cancelación solicitada") -> None:
        if self.estado == "PROCESADA":  # No permite cancelar una reserva ya finalizada/procesada
            raise OperacionReservaError(f"No se puede cancelar la reserva {self.id_reserva}: ya está procesada.")
        if self.estado == "CANCELADA":  # Evita cancelar dos veces la misma reserva
            raise OperacionReservaError(f"La reserva {self.id_reserva} ya se encuentra cancelada.")
        if self.estado == "CONFIRMADA":  # Si estaba confirmada, libera el servicio
            self.servicio.disponible = True
        self.estado = "CANCELADA"  # Cambia estado a CANCELADA

    def procesar(self) -> str:
        if self.estado != "CONFIRMADA":  # Exige que la reserva esté confirmada antes de procesarla
            raise OperacionReservaError(
                f"Solo se pueden procesar reservas CONFIRMADAS. Estado actual de {self.id_reserva}: {self.estado}."
            )
        self.estado = "PROCESADA"  # Marca la reserva como procesada
        self.servicio.disponible = True  # Libera el servicio tras completar el procesamiento
        return (
            f"Reserva {self.id_reserva} procesada para {self.cliente.nombre} "
            f"({self.servicio.nombre}) por ${self.costo_total:.2f}."
        )

    def __str__(self) -> str:
        return (
            f"Reserva[{self.id_reserva}] Estado={self.estado} | Cliente={self.cliente.nombre} | "
            f"Servicio={self.servicio.codigo} | Duración={self.duracion} | Total=${self.costo_total:.2f}"
        )


class SistemaSoftwareFJ:
    """Gestor en memoria mediante listas y registro en archivo de logs."""  # Coordina clientes, servicios y reservas

    def __init__(self, ruta_log: str = "software_fj.log") -> None:
        self.clientes: list[Cliente] = []  # Lista interna en memoria de clientes
        self.servicios: list[Servicio] = []  # Lista interna en memoria de servicios
        self.reservas: list[Reserva] = []  # Lista interna en memoria de reservas
        self.logger = LoggerEventos(ruta_log)  # Instancia encargada de escribir logs

    def registrar_cliente(self, id_cliente: str, nombre: str, correo: str, telefono: str) -> Cliente:
        try:
            if any(c.id == id_cliente for c in self.clientes):  # Evita IDs duplicados en la lista de clientes
                raise DatoInvalidoError(f"Ya existe un cliente con ID '{id_cliente}'.")
            cliente = Cliente(id_cliente, nombre, correo, telefono)  # Crea y valida el objeto Cliente
        except ErrorSoftwareFJ as exc:
            self.logger.registrar("ERROR", f"Fallo al registrar cliente '{id_cliente}': {exc}")  # Registra el error
            raise OperacionReservaError(f"No se pudo completar el registro del cliente '{id_cliente}'.") from exc  # Encadena
        except Exception as exc:
            self.logger.registrar("CRITICO", f"Error inesperado registrando cliente '{id_cliente}': {exc}")  # Log crítico
            raise OperacionReservaError("Error interno al registrar cliente.") from exc  # Encadena excepción genérica
        else:
            self.clientes.append(cliente)  # Agrega el cliente válido solo si no hubo excepciones
            self.logger.registrar("INFO", f"Cliente registrado: {cliente.resumen()}")  # Registra éxito en el log
            return cliente
        finally:
            self.logger.registrar("AUDITORIA", f"Intento de registro de cliente ID='{id_cliente}' finalizado.")  # Auditoría

    def agregar_servicio(self, servicio: Servicio) -> Servicio:
        try:
            if not isinstance(servicio, Servicio):  # Verifica que sea un servicio válido
                raise DatoInvalidoError("El objeto proporcionado no es un Servicio válido.")
            if any(s.codigo == servicio.codigo for s in self.servicios):  # Evita códigos duplicados
                raise DatoInvalidoError(f"Ya existe un servicio con código '{servicio.codigo}'.")
        except ErrorSoftwareFJ as exc:
            self.logger.registrar("ERROR", f"Fallo al agregar servicio: {exc}")  # Registra el error en el log
            raise  # Re-lanza la excepción controlada
        else:
            self.servicios.append(servicio)  # Guarda el servicio en la lista en memoria
            self.logger.registrar("INFO", f"Servicio agregado: {servicio.describir()}")  # Registra alta exitosa
            return servicio
        finally:
            codigo = getattr(servicio, "codigo", "DESCONOCIDO")  # Obtiene código de forma segura si falló antes
            self.logger.registrar("AUDITORIA", f"Intento de alta de servicio '{codigo}' finalizado.")  # Auditoría

    def buscar_cliente(self, id_cliente: str) -> Cliente:
        for c in self.clientes:  # Recorre la lista de clientes registrados
            if c.id == id_cliente:
                return c  # Retorna el cliente encontrado
        raise DatoInvalidoError(f"Cliente con ID '{id_cliente}' no encontrado.")  # Error si no existe

    def buscar_servicio(self, codigo_servicio: str) -> Servicio:
        for s in self.servicios:  # Recorre la lista de servicios registrados
            if s.codigo == codigo_servicio:
                return s  # Retorna el servicio encontrado
        raise DatoInvalidoError(f"Servicio con código '{codigo_servicio}' no encontrado.")  # Error si no existe

    def crear_y_ejecutar_reserva(
        self,
        id_reserva: str,
        id_cliente: str,
        codigo_servicio: str,
        duracion: float,
        descuento_pct: float = 0.0,
        impuesto_pct: float = 0.0,
        confirmar_y_procesar: bool = True,
    ) -> Reserva:
        try:
            cliente = self.buscar_cliente(id_cliente)  # Busca el cliente por ID
            servicio = self.buscar_servicio(codigo_servicio)  # Busca el servicio por código
            reserva = Reserva(  # Construye la reserva y valida disponibilidad + costo
                id_reserva=id_reserva,
                cliente=cliente,
                servicio=servicio,
                duracion=duracion,
                descuento_pct=descuento_pct,
                impuesto_pct=impuesto_pct,
            )
            if confirmar_y_procesar:  # Ejecuta confirmación y procesamiento inmediato si se solicita
                reserva.confirmar()
                detalle = reserva.procesar()
                self.logger.registrar("INFO", detalle)
            else:
                self.logger.registrar("INFO", f"Reserva creada en estado {reserva.estado}: {reserva}")  # Deja pendiente
        except ErrorSoftwareFJ as exc:
            self.logger.registrar("ERROR", f"Error en reserva '{id_reserva}': {exc}")  # Registra el error
            raise OperacionReservaError(f"Fallo en la operación de reserva '{id_reserva}'.") from exc  # Encadena causa
        except Exception as exc:
            self.logger.registrar("CRITICO", f"Error no previsto en reserva '{id_reserva}': {exc}")  # Registra fallo grave
            raise OperacionReservaError(f"Error inesperado en reserva '{id_reserva}'.") from exc  # Encadena causa
        else:
            self.reservas.append(reserva)  # Añade la reserva a la lista en memoria si todo salió bien
            return reserva
        finally:
            self.logger.registrar("AUDITORIA", f"Ciclo de operación de reserva '{id_reserva}' cerrado.")  # Auditoría