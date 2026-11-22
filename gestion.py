"""Gestor central: administra clientes, servicios y reservas y registra los eventos."""
from excepciones import (
    ClienteError, ReservaError, ValidacionError, logger, normalizar_id,
)
from modelos import Cliente, Servicio, Reserva


class GestorFJ:
    """Coordina el sistema; usa diccionarios indexados por ID normalizado."""

    def __init__(self):
        self.clientes = {}  # id -> Cliente
        self.servicios = {}  # nombre -> Servicio
        self.reservas = {}  # id -> Reserva

    def registrar_cliente(self, id_cliente, nombre, correo):
        cliente = Cliente(id_cliente, nombre, correo)  # Puede lanzar ValidacionError
        if cliente.id in self.clientes:  # Evita clientes duplicados
            raise ClienteError(f"El cliente {cliente.id} ya existe.")
        self.clientes[cliente.id] = cliente
        logger.info("Cliente registrado: %s", cliente.descripcion())
        return cliente

    def agregar_servicio(self, servicio):
        if not isinstance(servicio, Servicio):  # Solo acepta servicios válidos
            raise ValidacionError("Objeto de servicio inválido.")
        self.servicios[servicio.nombre] = servicio
        logger.info("Servicio agregado: %s", servicio.descripcion())

    def crear_reserva(self, id_reserva, id_cliente, nombre_servicio, duracion, **opciones):
        id_reserva = normalizar_id(id_reserva, "ID de reserva")  # Normaliza ANTES de buscar duplicados
        if id_reserva in self.reservas:
            raise ReservaError(f"La reserva {id_reserva} ya existe.")
        cliente = self.clientes.get(normalizar_id(id_cliente, "ID de cliente"))
        if cliente is None:
            raise ClienteError(f"Cliente {id_cliente!r} no registrado.")
        servicio = self.servicios.get(nombre_servicio)
        if servicio is None:
            raise ReservaError(f"Servicio {nombre_servicio!r} no existe.")
        reserva = Reserva(id_reserva, cliente, servicio, duracion, **opciones)
        self.reservas[reserva.id] = reserva
        logger.info("Reserva creada: %s", reserva.descripcion())
        return reserva

    def _obtener(self, id_reserva):
        """Busca una reserva por ID normalizado o lanza ReservaError."""
        reserva = self.reservas.get(normalizar_id(id_reserva, "ID de reserva"))
        if reserva is None:
            raise ReservaError(f"Reserva {id_reserva!r} no encontrada.")
        return reserva

    def confirmar(self, id_reserva):
        reserva = self._obtener(id_reserva)
        reserva.confirmar()
        logger.info("Reserva confirmada: %s", reserva.descripcion())
        return reserva

    def procesar(self, id_reserva):
        reserva = self._obtener(id_reserva)
        reserva.procesar()
        logger.info("Reserva procesada: %s", reserva.descripcion())
        return reserva

    def cancelar(self, id_reserva):
        reserva = self._obtener(id_reserva)
        reserva.cancelar()
        logger.info("Reserva cancelada: %s", reserva.descripcion())
        return reserva
