# Archivo: main.py
# Solo se importan las clases, se crean los objetos y se arranca la ventana

import tkinter as tk
from ConfiguracionPomodoro import ConfiguracionPomodoro
from HistorialSesiones import HistorialSesiones
from SesionPomodoro import SesionPomodoro
from Estadisticas import Estadisticas
from GestorExcel import GestorExcel
from InterfazPomodoro import InterfazPomodoro

ventana = tk.Tk()

gestor = GestorExcel("Registro_Pomodoro.xlsx")
configuracion = ConfiguracionPomodoro(25, 5)
historial = HistorialSesiones()
sesion = SesionPomodoro(configuracion, historial)
estadisticas = Estadisticas(historial)

aplicacion = InterfazPomodoro(ventana, sesion, configuracion, historial, gestor, estadisticas)
ventana.mainloop()
