# Archivo: main.py
# Programa principal: solo se importan las clases, se crean los objetos y se ejecuta

from ConfiguracionPomodoro import ConfiguracionPomodoro
from HistorialSesiones import HistorialSesiones
from SesionPomodoro import SesionPomodoro
from MenuPomodoro import MenuPomodoro

try:
    configuracion = ConfiguracionPomodoro(25, 5)
    historial = HistorialSesiones()
    sesion = SesionPomodoro(configuracion, historial)
    menu = MenuPomodoro(sesion, configuracion, historial)

    menu.ejecutar()
except KeyboardInterrupt:
    print("\nPrograma cerrado con Ctrl+C")
except Exception as error:
    print("Ocurrio un error inesperado:", error)
finally:
    print("Fin del programa")
