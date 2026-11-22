"""Excepciones personalizadas, validaciones y registro de errores (logs) de Software FJ."""
import logging  # Módulo estándar para registrar eventos en archivo
import math  # Se usa math.isfinite para rechazar NaN e infinitos

# Configuración del archivo de logs: guarda fecha, nivel y mensaje de cada evento
logging.basicConfig(
    filename="logs_software_fj.log",  # Archivo donde se guardan los registros
    level=logging.INFO,  # Se registran eventos desde nivel INFO hacia arriba
    format="%(asctime)s | %(levelname)s | %(message)s",  # Formato de cada línea
    encoding="utf-8",  # Codificación para tildes y ñ
)
logger = logging.getLogger("software_fj")  # Logger único compartido por todos los módulos


class SoftwareFJError(Exception):
    """Excepción base: todas las excepciones del sistema heredan de ella."""


class ValidacionError(SoftwareFJError):
    """Se lanza cuando un dato de entrada es inválido (tipo, rango o formato)."""


class ClienteError(SoftwareFJError):
    """Se lanza por problemas con clientes (duplicados, inexistentes)."""


class ServicioNoDisponibleError(SoftwareFJError):
    """Se lanza cuando el servicio no está disponible o ya está ocupado."""


class ReservaError(SoftwareFJError):
    """Se lanza por problemas generales con reservas (duplicadas, inexistentes)."""


class EstadoReservaError(SoftwareFJError):
    """Se lanza cuando se intenta una transición de estado no permitida."""


def validar_numero(valor, nombre, permitir_cero=False):
    """Valida un número real finito: rechaza bool, texto, NaN, infinito y negativos."""
    # bool es subclase de int en Python, por eso se excluye de forma explícita
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise ValidacionError(f"{nombre} debe ser numérico, no {type(valor).__name__}.")
    if not math.isfinite(valor):  # Rechaza nan, inf y -inf
        raise ValidacionError(f"{nombre} debe ser un número finito.")
    if valor < 0 or (valor == 0 and not permitir_cero):  # Rango permitido
        raise ValidacionError(f"{nombre} debe ser mayor que cero.")
    return valor  # Devuelve el valor ya validado


def validar_booleano(valor, nombre):
    """Exige un booleano real; evita que bool('False') se interprete como True."""
    if not isinstance(valor, bool):
        raise ValidacionError(f"{nombre} debe ser True o False.")
    return valor


def validar_texto(valor, nombre):
    """Exige un texto no vacío y devuelve la versión sin espacios en los extremos."""
    if not isinstance(valor, str) or not valor.strip():
        raise ValidacionError(f"{nombre} debe ser un texto no vacío.")
    return valor.strip()


def normalizar_id(valor, nombre="ID"):
    """Normaliza identificadores: sin espacios extremos y en mayúscula (R1 == ' r1 ')."""
    return validar_texto(valor, nombre).upper()
