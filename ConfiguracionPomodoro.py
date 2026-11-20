# Archivo: ConfiguracionPomodoro.py
# Guarda los tiempos del pomodoro (encapsulados) y valida lo que ingresa el usuario


class ConfiguracionPomodoro:
    MINIMO = 1
    MAXIMO = 120  # mas de 2 horas seguidas ya no es un pomodoro

    def __init__(self, tiempo_estudio=25, tiempo_descanso=5):
        self.__tiempo_estudio = 25
        self.__tiempo_descanso = 5
        self.__modo_demo = False
        self.establecer_tiempos(tiempo_estudio, tiempo_descanso)

    def validar_minutos(self, minutos, nombre):
        if type(minutos) != int:
            raise ValueError(f"El tiempo de {nombre} debe ser un numero entero")
        if minutos < self.MINIMO or minutos > self.MAXIMO:
            raise ValueError(f"El tiempo de {nombre} debe estar entre {self.MINIMO} y {self.MAXIMO} minutos")

    # metodo para modificar los tiempos (solo cambia si los dos son validos)
    def establecer_tiempos(self, estudio, descanso):
        self.validar_minutos(estudio, "estudio")
        self.validar_minutos(descanso, "descanso")
        if descanso >= estudio:
            raise ValueError("El descanso tiene que ser mas corto que el estudio")

        self.__tiempo_estudio = estudio
        self.__tiempo_descanso = descanso

    def restablecer_por_defecto(self):
        self.__tiempo_estudio = 25
        self.__tiempo_descanso = 5

    # modo demo: 1 minuto pasa en 1 segundo, para poder mostrarlo en clase
    def cambiar_modo_demo(self):
        self.__modo_demo = not self.__modo_demo
        return self.__modo_demo

    # para el Checkbutton de la interfaz, que manda True o False
    def establecer_modo_demo(self, activo):
        self.__modo_demo = bool(activo)

    # metodos para consultar
    def consultar_tiempo_estudio(self):
        return self.__tiempo_estudio

    def consultar_tiempo_descanso(self):
        return self.__tiempo_descanso

    def consultar_tiempo_descanso_largo(self):
        return self.__tiempo_descanso * 3

    def consultar_modo_demo(self):
        return self.__modo_demo

    def consultar_espera(self):
        if self.__modo_demo:
            return 1 / 60
        return 1

    # lo mismo pero en milisegundos, que es lo que pide .after() de tkinter
    def consultar_espera_ms(self):
        return int(self.consultar_espera() * 1000)


# prueba rapida de la clase
if __name__ == "__main__":
    config = ConfiguracionPomodoro()
    print(f"Estudio: {config.consultar_tiempo_estudio()} min | Descanso: {config.consultar_tiempo_descanso()} min")

    config.establecer_tiempos(50, 10)
    print(f"Estudio: {config.consultar_tiempo_estudio()} min | Descanso: {config.consultar_tiempo_descanso()} min")

    datos_malos = [(-5, 5), (30, 0), (500, 5), ("25", 5), (10, 20)]
    for estudio, descanso in datos_malos:
        try:
            config.establecer_tiempos(estudio, descanso)
        except ValueError as e:
            print(f"({estudio}, {descanso}) -> Error: {e}")

    print("Los tiempos no cambiaron:", config.consultar_tiempo_estudio(), config.consultar_tiempo_descanso())
