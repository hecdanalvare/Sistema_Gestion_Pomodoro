# Archivo: MenuPomodoro.py
# Menu de consola. Recibe los objetos creados en main.py y llama sus metodos

from Cronometro import Cronometro


class MenuPomodoro:
    def __init__(self, sesion, configuracion, historial):
        self.__sesion = sesion
        self.__configuracion = configuracion
        self.__historial = historial
        self.__opciones = {
            1: "Iniciar / continuar bloque",
            2: "Saltar al siguiente bloque",
            3: "Cronometro libre",
            4: "Configurar tiempos",
            5: "Restablecer tiempos por defecto (25/5)",
            6: "Activar / desactivar modo demo",
            7: "Ver historial",
            8: "Borrar historial y reiniciar sesion",
            9: "Salir"
        }

    def mostrar_menu(self):
        estado = self.__sesion.consultar_estado_actual()
        if self.__sesion.hay_bloque_pausado():
            estado = estado + " (pausado en " + self.__sesion.consultar_tiempo_pausado() + ")"

        if self.__configuracion.consultar_modo_demo():
            demo = "SI"
        else:
            demo = "NO"

        print("\n=========== RELOJ POMODORO ===========")
        print(f"Bloque actual: {estado}")
        print(f"Pomodoros: {self.__sesion.consultar_ciclos_completados()} | Estudio: "
              f"{self.__configuracion.consultar_tiempo_estudio()} min | Descanso: "
              f"{self.__configuracion.consultar_tiempo_descanso()} min | Demo: {demo}")
        print("--------------------------------------")
        for numero, texto in self.__opciones.items():
            print(f"{numero}. {texto}")

    def pedir_entero(self, mensaje):
        dato = input(mensaje).strip()
        if dato == "":
            raise ValueError("No escribio nada")
        if not dato.lstrip("-").isdigit():
            raise ValueError(f"'{dato}' no es un numero entero")
        return int(dato)

    def usar_cronometro(self):
        limite = self.pedir_entero("Limite del cronometro en minutos (1-120): ")
        if limite < 1 or limite > 120:
            raise ValueError("El limite del cronometro debe estar entre 1 y 120 minutos")

        crono = Cronometro(limite * 60, self.__configuracion.consultar_espera())
        completo = crono.ejecutar_conteo()

        minutos = crono.consultar_tiempo_transcurrido() // 60
        if minutos > 0:
            self.__historial.registrar_sesion("Libre", minutos, completo)
        else:
            print("No alcanzo ni un minuto, no se guarda en el historial")

    def configurar_tiempos(self):
        print("Tiempos actuales:", self.__configuracion.consultar_tiempo_estudio(), "min de estudio y",
              self.__configuracion.consultar_tiempo_descanso(), "min de descanso")
        estudio = self.pedir_entero("Minutos de estudio: ")
        descanso = self.pedir_entero("Minutos de descanso: ")
        self.__configuracion.establecer_tiempos(estudio, descanso)
        print("Tiempos actualizados")

    def borrar_todo(self):
        respuesta = input("Seguro que quiere borrar el historial? (s/n): ").strip().lower()
        if respuesta == "s":
            self.__historial.limpiar_historial()
            self.__sesion.reiniciar_sesion()
        else:
            print("No se borro nada")

    def ejecutar_opcion(self, opcion):
        if opcion == 1:
            self.__sesion.iniciar_sesion()
        elif opcion == 2:
            self.__sesion.saltar_bloque()
        elif opcion == 3:
            self.usar_cronometro()
        elif opcion == 4:
            self.configurar_tiempos()
        elif opcion == 5:
            self.__configuracion.restablecer_por_defecto()
            print("Tiempos restablecidos: 25 min estudio / 5 min descanso")
        elif opcion == 6:
            if self.__configuracion.cambiar_modo_demo():
                print("Modo demo activado: cada minuto dura 1 segundo")
            else:
                print("Modo demo desactivado: tiempo real")
        elif opcion == 7:
            self.__historial.mostrar_resumen()
        elif opcion == 8:
            self.borrar_todo()
        else:
            raise ValueError(f"La opcion {opcion} no existe, elija entre 1 y 9")

    def ejecutar(self):
        print("Bienvenido al sistema de gestion de tiempo Pomodoro")
        opcion = 0
        while opcion != 9:
            self.mostrar_menu()
            try:
                opcion = self.pedir_entero("Elija una opcion: ")
                if opcion != 9:
                    self.ejecutar_opcion(opcion)
            except ValueError as error:
                print("Error:", error)
        print("Hasta luego, buen estudio")
