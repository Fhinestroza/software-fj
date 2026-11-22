"""Modelos del dominio: Cliente, Servicio (abstracto), servicios especializados y Reserva."""
import math  # Para comprobar que los costos calculados sean finitos
import re  # Para validar el formato del correo
from abc import ABC, abstractmethod  # Herramientas para clases abstractas
from excepciones import (  # Excepciones y validadores propios
    ValidacionError, ServicioNoDisponibleError, EstadoReservaError,
    validar_numero, validar_booleano, validar_texto, normalizar_id,
)


class Entidad(ABC):
    """Clase abstracta base: toda entidad del sistema debe describirse a sí misma."""

    @abstractmethod
    def descripcion(self):
        """Devuelve un texto que describe la entidad."""


class Cliente(Entidad):
    """Cliente de Software FJ con datos validados y encapsulados."""

    def __init__(self, id_cliente, nombre, correo):
        self.__id = normalizar_id(id_cliente, "ID de cliente")  # Atributo privado
        self.__nombre = validar_texto(nombre, "Nombre")  # Atributo privado
        correo = validar_texto(correo, "Correo")  # Primero se valida el tipo
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", correo):  # Formato básico
            raise ValidacionError(f"Correo inválido: {correo!r}.")
        self.__correo = correo  # Se guarda solo si es válido

    @property
    def id(self):  # Acceso de solo lectura al ID
        return self.__id

    @property
    def nombre(self):  # Acceso de solo lectura al nombre
        return self.__nombre

    @property
    def correo(self):  # Acceso de solo lectura al correo
        return self.__correo

    def descripcion(self):
        return f"Cliente {self.id}: {self.nombre} <{self.correo}>"


class Servicio(Entidad):
    """Clase abstracta de servicio: define el contrato que cumplen los servicios."""

    def __init__(self, nombre, tarifa, disponible=True):
        self.nombre = validar_texto(nombre, "Nombre del servicio")  # Texto válido
        self.tarifa = validar_numero(tarifa, "Tarifa")  # Número finito > 0
        self.disponible = validar_booleano(disponible, "Disponibilidad")  # Solo bool

    @abstractmethod
    def calcular_costo(self, duracion, **opciones):
        """Cada servicio calcula su costo de forma distinta (polimorfismo)."""

    def _verificar_costo(self, costo):
        """Comprueba que el costo final sea un número finito antes de usarlo."""
        if not math.isfinite(costo):
            raise ValidacionError("El costo calculado no es un número finito.")
        return round(costo, 2)  # Redondeo a dos decimales

    def descripcion(self):
        return f"{self.nombre} (tarifa {self.tarifa})"


class ReservaSala(Servicio):
    """Servicio 1: alquiler de salas por hora; 10 % de descuento desde 4 horas."""

    def calcular_costo(self, duracion, **opciones):
        horas = validar_numero(duracion, "Duración (horas)")  # Valida la duración
        costo = self.tarifa * horas  # Costo base
        if horas >= 4:  # Descuento por uso prolongado
            costo *= 0.90
        return self._verificar_costo(costo)


class AlquilerEquipo(Servicio):
    """Servicio 2: alquiler de equipos por día; seguro opcional del 5 %."""

    def calcular_costo(self, duracion, seguro=False, **opciones):
        dias = validar_numero(duracion, "Duración (días)")  # Valida los días
        seguro = validar_booleano(seguro, "Seguro")  # El seguro debe ser bool
        costo = self.tarifa * dias  # Costo base
        if seguro:  # Recargo por seguro
            costo *= 1.05
        return self._verificar_costo(costo)


class Asesoria(Servicio):
    """Servicio 3: asesoría especializada por hora con impuesto configurable."""

    def calcular_costo(self, duracion, impuesto=0.19, **opciones):
        horas = validar_numero(duracion, "Duración (horas)")  # Valida las horas
        # El impuesto se valida ANTES de calcular: "19%" lanza ValidacionError, no TypeError
        impuesto = validar_numero(impuesto, "Impuesto", permitir_cero=True)
        if impuesto >= 1:  # Se espera una fracción, por ejemplo 0.19
            raise ValidacionError("El impuesto debe expresarse como fracción menor que 1.")
        costo = self.tarifa * horas * (1 + impuesto)  # Costo con impuesto
        return self._verificar_costo(costo)


class Reserva(Entidad):
    """Reserva con estados: PENDIENTE -> CONFIRMADA -> PROCESADA, o CANCELADA."""

    PENDIENTE, CONFIRMADA, PROCESADA, CANCELADA = "PENDIENTE", "CONFIRMADA", "PROCESADA", "CANCELADA"

    def __init__(self, id_reserva, cliente, servicio, duracion, **opciones):
        self.id = normalizar_id(id_reserva, "ID de reserva")  # ID normalizado
        if not isinstance(cliente, Cliente):  # Verifica el tipo del cliente
            raise ValidacionError("El cliente no es válido.")
        if not isinstance(servicio, Servicio):  # Verifica el tipo del servicio
            raise ValidacionError("El servicio no es válido.")
        self.cliente, self.servicio = cliente, servicio  # Relaciones
        self.duracion, self.opciones = duracion, opciones  # Datos de la reserva
        self.costo = servicio.calcular_costo(duracion, **opciones)  # Calcula y valida
        self.estado = self.PENDIENTE  # Estado inicial

    def confirmar(self):
        if self.estado != self.PENDIENTE:  # Solo se confirma desde PENDIENTE
            raise EstadoReservaError(f"No se puede confirmar una reserva {self.estado}.")
        if not self.servicio.disponible:  # El servicio debe seguir libre
            raise ServicioNoDisponibleError(f"'{self.servicio.nombre}' no está disponible.")
        self.servicio.disponible = False  # Se bloquea el servicio
        self.estado = self.CONFIRMADA

    def procesar(self):
        if self.estado != self.CONFIRMADA:  # Solo se procesa desde CONFIRMADA
            raise EstadoReservaError(f"No se puede procesar una reserva {self.estado}.")
        self.estado = self.PROCESADA

    def cancelar(self):
        if self.estado in (self.PROCESADA, self.CANCELADA):  # Estados finales
            raise EstadoReservaError(f"No se puede cancelar una reserva {self.estado}.")
        if self.estado == self.CONFIRMADA:  # Libera el servicio bloqueado
            self.servicio.disponible = True
        self.estado = self.CANCELADA

    def descripcion(self):
        return (f"Reserva {self.id} | {self.cliente.nombre} | {self.servicio.nombre} | "
                f"costo ${self.costo:,.2f} | {self.estado}")
