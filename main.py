from excepciones import ErrorSoftwareFJ  # Importa la excepción base para capturar cualquier error controlado del sistema
from reservas import SistemaSoftwareFJ  # Importa el gestor principal en memoria y su logger
from servicios import AlquilerEquipo, AsesoriaEspecializada, ReservaSala  # Importa los tres servicios especializados


def ejecutar_simulacion() -> None:
    sistema = SistemaSoftwareFJ(ruta_log="software_fj.log")  # Inicializa el sistema sin base de datos y con archivo log

    operaciones = [  # Lista de 12 operaciones de prueba cubriendo casos válidos, inválidos y fallidos
        # 1. Cliente válido
        ("OP-01 Registro cliente válido", lambda: sistema.registrar_cliente("C01", "Laura Gómez", "laura@fj.com", "3105551234")),
        # 2. Cliente inválido (correo mal formado)
        ("OP-02 Cliente con correo inválido", lambda: sistema.registrar_cliente("C02", "Carlos Ruiz", "correo-no-valido", "3115559988")),
        # 3. Cliente válido
        ("OP-03 Segundo cliente válido", lambda: sistema.registrar_cliente("C03", "Andrés Pérez", "andres@empresa.co", "3124447766")),
        # 4. Servicio válido: Reserva de sala
        ("OP-04 Alta servicio ReservaSala", lambda: sistema.agregar_servicio(ReservaSala("SAL-1", "Sala Conferencias A", 80.0, 20))),
        # 5. Servicio válido: Alquiler de equipo
        ("OP-05 Alta servicio AlquilerEquipo", lambda: sistema.agregar_servicio(AlquilerEquipo("EQ-1", "Laptop Workstation", 45.0, "Portátil"))),
        # 6. Servicio válido: Asesoría especializada
        ("OP-06 Alta servicio AsesoriaEspecializada", lambda: sistema.agregar_servicio(AsesoriaEspecializada("ASE-1", "Arquitectura Cloud", 120.0, "DevOps/Cloud"))),
        # 7. Servicio inválido (tarifa negativa -> cálculo inconsistente)
        ("OP-07 Servicio con tarifa inválida", lambda: sistema.agregar_servicio(ReservaSala("SAL-BAD", "Sala Rota", -50.0, 10))),
        # 8. Reserva exitosa con variante de cálculo (descuento + impuesto)
        ("OP-08 Reserva exitosa de sala", lambda: sistema.crear_y_ejecutar_reserva("R01", "C01", "SAL-1", duracion=3, descuento_pct=10, impuesto_pct=19)),
        # 9. Reserva exitosa de asesoría
        ("OP-09 Reserva exitosa de asesoría", lambda: sistema.crear_y_ejecutar_reserva("R02", "C03", "ASE-1", duracion=4, impuesto_pct=19)),
        # 10. Reserva fallida por cliente inexistente
        ("OP-10 Reserva con cliente inexistente", lambda: sistema.crear_y_ejecutar_reserva("R03", "C99", "EQ-1", duracion=2)),
        # 11. Reserva fallida por duración inconsistente (0 días en alquiler de equipo)
        ("OP-11 Reserva con duración inválida", lambda: sistema.crear_y_ejecutar_reserva("R04", "C01", "EQ-1", duracion=0)),
        # 12. Cancelación válida de una reserva pendiente
        ("OP-12 Crear y cancelar reserva", lambda: _crear_y_cancelar(sistema)),
    ]

    for descripcion, accion in operaciones:  # Ejecuta cada operación secuencialmente
        print(f"\n--- {descripcion} ---")  # Muestra el encabezado de la operación actual
        try:
            resultado = accion()  # Ejecuta la función asociada a la operación
        except ErrorSoftwareFJ as exc:
            print(f"[MANEJADO] {type(exc).__name__}: {exc}")  # Informa el error controlado sin detener la simulación
            if exc.__cause__ is not None:  # Verifica si existe una excepción original encadenada (`raise ... from ...`)
                print(f"   ↳ Causa encadenada ({type(exc.__cause__).__name__}): {exc.__cause__}")  # Muestra la causa raíz
        else:
            print(f"[OK] {resultado}")  # Muestra el resultado cuando la operación no lanzó excepciones
        finally:
            print("   (Bloque finally ejecutado; sistema operativo)")  # Confirma que el sistema sigue activo

    print("\n=== RESUMEN FINAL EN MEMORIA ===")  # Imprime totales almacenados en listas en memoria
    print(f"Clientes registrados: {len(sistema.clientes)}")
    print(f"Servicios registrados: {len(sistema.servicios)}")
    print(f"Reservas registradas: {len(sistema.reservas)}")
    print("Revisa el archivo 'software_fj.log' para ver el historial de eventos y errores.")


def _crear_y_cancelar(sistema: SistemaSoftwareFJ) -> str:
    reserva = sistema.crear_y_ejecutar_reserva(  # Crea la reserva R05 dejándola en estado PENDIENTE
        "R05", "C01", "EQ-1", duracion=2, confirmar_y_procesar=False
    )
    reserva.cancelar("Cambio de cronograma del cliente")  # Cancela la reserva recién creada
    sistema.logger.registrar("INFO", f"Reserva {reserva.id_reserva} cancelada correctamente.")  # Registra cancelación
    return str(reserva)  # Retorna representación en texto de la reserva cancelada


if __name__ == "__main__":
    ejecutar_simulacion()  # Inicia la simulación solo cuando el archivo se ejecuta directamente