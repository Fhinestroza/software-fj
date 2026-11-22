"""Simulación de 14 operaciones válidas e inválidas para demostrar la robustez del sistema."""
from excepciones import SoftwareFJError, logger
from modelos import ReservaSala, AlquilerEquipo, Asesoria
from gestion import GestorFJ


def ejecutar(numero, titulo, accion):
    """Ejecuta una operación; captura errores propios e inesperados y el programa continúa."""
    print(f"\n[{numero:02d}] {titulo}")
    try:
        resultado = accion()  # Intenta la operación
        print("   OK ->", resultado.descripcion() if hasattr(resultado, "descripcion") else resultado)
    except SoftwareFJError as e:  # Errores controlados del dominio
        print(f"   ERROR CONTROLADO ({type(e).__name__}): {e}")
        logger.error("[%02d] %s: %s", numero, type(e).__name__, e)
    except Exception as e:  # Cualquier error inesperado también se registra
        print(f"   ERROR INESPERADO ({type(e).__name__}): {e}")
        logger.critical("[%02d] Inesperado %s: %s", numero, type(e).__name__, e)
    finally:  # Se ejecuta siempre, haya o no error
        print("   (operación finalizada)")


def simular():
    g = GestorFJ()  # Instancia del sistema
    g.agregar_servicio(ReservaSala("Sala A", 50000))
    g.agregar_servicio(AlquilerEquipo("Portátil", 30000))
    g.agregar_servicio(Asesoria("Asesoría TI", 80000))

    ejecutar(1, "Registrar cliente válido", lambda: g.registrar_cliente("C1", "Ana Gómez", "ana@correo.com"))
    ejecutar(2, "Registrar cliente con correo inválido", lambda: g.registrar_cliente("C2", "Luis", "luis.correo"))
    ejecutar(3, "Registrar cliente duplicado", lambda: g.registrar_cliente(" c1 ", "Ana", "ana@correo.com"))
    ejecutar(4, "Reserva de sala 5 h (descuento 10 %)", lambda: g.crear_reserva("R1", "C1", "Sala A", 5))
    ejecutar(5, "Confirmar R1", lambda: g.confirmar("R1"))
    ejecutar(6, "Reserva duplicada ' r1 ' (ID normalizado)", lambda: g.crear_reserva(" r1 ", "C1", "Sala A", 2))
    ejecutar(7, "Reserva de sala ya ocupada", lambda: (g.crear_reserva("R2", "C1", "Sala A", 2), g.confirmar("R2"))[1])
    ejecutar(8, "Tarifa/duración booleana (True)", lambda: g.crear_reserva("R3", "C1", "Portátil", True))
    ejecutar(9, "Duración NaN", lambda: g.crear_reserva("R4", "C1", "Asesoría TI", float("nan")))
    ejecutar(10, "Impuesto de texto '19%'", lambda: g.crear_reserva("R5", "C1", "Asesoría TI", 2, impuesto="19%"))
    ejecutar(11, "Asesoría exitosa 3 h con IVA 19 %", lambda: g.crear_reserva("R6", "C1", "Asesoría TI", 3))
    ejecutar(12, "Equipo 2 días con seguro", lambda: g.crear_reserva("R7", "C1", "Portátil", 2, seguro=True))
    ejecutar(13, "Procesar R1 y luego intentar cancelarla", lambda: (g.procesar("R1"), g.cancelar("R1"))[1])
    ejecutar(14, "Cancelación válida de R6", lambda: g.cancelar("R6"))

    print("\n=== RESUMEN FINAL ===")
    for r in g.reservas.values():
        print(" ", r.descripcion())
    return g


if __name__ == "__main__":
    simular()
