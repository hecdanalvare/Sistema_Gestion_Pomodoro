# Archivo: SesionPomodoro.py
# Clase principal de la propuesta: lleva el ciclo Estudio -> Descanso
# y cada 4 pomodoros toca un descanso largo

from Temporizador import Temporizador


class SesionPomodoro:
    def __init__(self, configuracion, historial, ciclos_para_largo=4):
        self.__configuracion = configuracion
        self.__historial = historial
        self.__estado_actual = "Estudio"
        self.__ciclos_completados = 0
        self.__ciclos_para_largo = ciclos_para_largo
        self.__bloque_actual = None  # el temporizador del bloque que va corriendo (o pausado)
        self.__materia_actual = "General"

    def consultar_estado_actual(self):
        return self.__estado_actual

    def consultar_ciclos_completados(self):
        return self.__ciclos_completados

    def consultar_materia_actual(self):
        return self.__materia_actual

    def cambiar_materia(self, nombre_materia):
        if nombre_materia.strip() == "":
            raise ValueError("Debe escoger una materia")
        self.__materia_actual = nombre_materia

    # los descansos no son de ninguna materia
    def materia_para_registro(self):
        if self.__estado_actual == "Estudio":
            return self.__materia_actual
        return "-"

    def hay_bloque_pausado(self):
        return self.__bloque_actual is not None

    def consultar_tiempo_pausado(self):
        if self.__bloque_actual is None:
            return "--:--"
        return self.__bloque_actual.tiempo_en_pantalla()

    def crear_bloque(self):
        # segun el estado se toma el tiempo de la configuracion
        if self.__estado_actual == "Estudio":
            minutos = self.__configuracion.consultar_tiempo_estudio()
        elif self.__estado_actual == "Descanso":
            minutos = self.__configuracion.consultar_tiempo_descanso()
        else:
            minutos = self.__configuracion.consultar_tiempo_descanso_largo()

        return Temporizador(minutos * 60, self.__estado_actual, self.__configuracion.consultar_espera())

    # devuelve el bloque que toca; si no hay uno empezado se crea
    def preparar_bloque(self):
        if self.__bloque_actual is None:
            self.__bloque_actual = self.crear_bloque()
        return self.__bloque_actual

    # se llama cuando el temporizador llega a cero
    # devuelve la sesion que se guardo para que la interfaz la mande al Excel
    def terminar_bloque(self):
        bloque = self.__bloque_actual
        self.__bloque_actual = None
        minutos = bloque.consultar_duracion() // 60
        sesion = self.__historial.registrar_sesion(self.__estado_actual, minutos, True, self.materia_para_registro())
        if self.__estado_actual == "Estudio":
            self.__ciclos_completados += 1
        self.cambiar_estado()
        return sesion

    # version de consola (parcial 2)
    def iniciar_sesion(self):
        if self.__bloque_actual is not None:
            print("Continuando el bloque que estaba pausado...")
        bloque = self.preparar_bloque()

        completado = bloque.ejecutar_conteo()
        if completado:
            self.terminar_bloque()
        else:
            print("Puede continuarlo con la opcion 1 o saltarlo con la opcion 2")
        return completado

    def cambiar_estado(self):
        if self.__estado_actual == "Estudio":
            if self.__ciclos_completados > 0 and self.__ciclos_completados % self.__ciclos_para_largo == 0:
                self.__estado_actual = "Descanso largo"
            else:
                self.__estado_actual = "Descanso"
        else:
            self.__estado_actual = "Estudio"
        print("Siguiente bloque:", self.__estado_actual)

    def saltar_bloque(self):
        # si se salta un bloque a medias se guarda como incompleto (si alcanzo al menos 1 min)
        sesion = None
        if self.__bloque_actual is not None:
            minutos = self.__bloque_actual.segundos_cumplidos() // 60
            if minutos > 0:
                sesion = self.__historial.registrar_sesion(self.__estado_actual, minutos, False, self.materia_para_registro())
            self.__bloque_actual = None
        print("Se salto el bloque de", self.__estado_actual)
        if self.__estado_actual == "Estudio":
            # si no termino el estudio no se gana el descanso largo
            self.__estado_actual = "Descanso"
            print("Siguiente bloque:", self.__estado_actual)
        else:
            self.cambiar_estado()
        return sesion

    # bota el bloque empezado; el siguiente se crea con los tiempos actuales
    def reiniciar_bloque(self):
        self.__bloque_actual = None

    def reiniciar_sesion(self):
        self.__estado_actual = "Estudio"
        self.__ciclos_completados = 0
        self.__bloque_actual = None
        print("Sesion reiniciada, se empieza otra vez por Estudio")


# prueba rapida de la clase (en modo demo para que no tarde)
if __name__ == "__main__":
    from ConfiguracionPomodoro import ConfiguracionPomodoro
    from HistorialSesiones import HistorialSesiones

    config = ConfiguracionPomodoro(2, 1)
    config.cambiar_modo_demo()
    historial = HistorialSesiones()
    sesion = SesionPomodoro(config, historial)
    sesion.cambiar_materia("Calculo")

    # asi lo usa la interfaz: avanzar de a un segundo hasta que termine
    for i in range(8):
        bloque = sesion.preparar_bloque()
        while not bloque.avanzar_segundo():
            pass
        sesion.terminar_bloque()

    print("Ciclos completados:", sesion.consultar_ciclos_completados())
    print("Bloque que sigue:", sesion.consultar_estado_actual())
    historial.mostrar_resumen()
