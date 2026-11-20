# Archivo: Temporizador.py
# Clase hija 1 de MedidorTiempo: cuenta regresiva para los bloques del pomodoro

from MedidorTiempo import MedidorTiempo


class Temporizador(MedidorTiempo):
    tipos_validos = ["Estudio", "Descanso", "Descanso largo"]

    def __init__(self, duracion_segundos=1500, tipo_bloque="Estudio", espera=1):
        super().__init__(duracion_segundos, espera)

        if tipo_bloque not in Temporizador.tipos_validos:
            raise ValueError(f"Tipo de bloque no valido: {tipo_bloque}")

        self.__tipo_bloque = tipo_bloque
        self.__tiempo_restante = duracion_segundos

    def consultar_tipo_bloque(self):
        return self.__tipo_bloque

    def consultar_tiempo_restante(self):
        return self.__tiempo_restante

    def segundos_cumplidos(self):
        return self.consultar_duracion() - self.__tiempo_restante

    # se sobrescribe reiniciar para que tambien vuelva el tiempo al inicio
    def reiniciar(self):
        super().reiniciar()
        self.__tiempo_restante = self.consultar_duracion()

    # polimorfismo: aqui el segundo se resta
    def avanzar_segundo(self):
        if self.__tiempo_restante > 0:
            self.__tiempo_restante -= 1
        return self.__tiempo_restante == 0

    def tiempo_en_pantalla(self):
        return self.formato_tiempo(self.__tiempo_restante)

    def porcentaje_avance(self):
        return self.segundos_cumplidos() * 100 / self.consultar_duracion()

    # version de consola: cuenta hacia atras
    # si se presiona Ctrl+C se pausa y queda guardado donde iba
    def ejecutar_conteo(self):
        self.iniciar()
        print(f"\n--- {self.__tipo_bloque}: {self.tiempo_en_pantalla()} ---  (Ctrl+C para pausar)")

        try:
            while self.__tiempo_restante > 0:
                print("Tiempo restante:", self.tiempo_en_pantalla(), end="\r")
                self.esperar_segundo()
                self.avanzar_segundo()
        except KeyboardInterrupt:
            self.pausar()
            print(f"\nBloque pausado en {self.tiempo_en_pantalla()}")
            return False

        self.pausar()
        print("Tiempo restante: 00:00")
        print(f"Termino el bloque de {self.__tipo_bloque}")
        return True


# prueba rapida de la clase
if __name__ == "__main__":
    temp_estudio = Temporizador(5, "Estudio")
    print("Tipo de bloque:", temp_estudio.consultar_tipo_bloque())
    temp_estudio.avanzar_segundo()
    temp_estudio.avanzar_segundo()
    print("Despues de 2 segundos:", temp_estudio.tiempo_en_pantalla(), "-", temp_estudio.porcentaje_avance(), "%")
    temp_estudio.ejecutar_conteo()

    try:
        temp_malo = Temporizador(60, "Siesta")
    except ValueError as e:
        print("Error:", e)
