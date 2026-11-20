# Archivo: Cronometro.py
# Clase hija 2 de MedidorTiempo: cuenta hacia arriba (modo de estudio libre)

from MedidorTiempo import MedidorTiempo


class Cronometro(MedidorTiempo):
    def __init__(self, limite_segundos=60, espera=1):
        super().__init__(limite_segundos, espera)
        self.__tiempo_transcurrido = 0

    def consultar_tiempo_transcurrido(self):
        return self.__tiempo_transcurrido

    def detener_cronometro(self):
        self.pausar()
        print(f"\nCronometro detenido en {self.formato_tiempo(self.__tiempo_transcurrido)}")

    def reiniciar(self):
        super().reiniciar()
        self.__tiempo_transcurrido = 0

    # polimorfismo: aqui el segundo se suma
    def avanzar_segundo(self):
        if self.__tiempo_transcurrido < self.consultar_duracion():
            self.__tiempo_transcurrido += 1
        return self.__tiempo_transcurrido >= self.consultar_duracion()

    def tiempo_en_pantalla(self):
        return self.formato_tiempo(self.__tiempo_transcurrido)

    def porcentaje_avance(self):
        return self.__tiempo_transcurrido * 100 / self.consultar_duracion()

    # version de consola: cuenta hacia arriba hasta el limite
    def ejecutar_conteo(self):
        self.iniciar()
        limite = self.consultar_duracion()
        print(f"\n--- Cronometro hasta {self.formato_tiempo(limite)} ---  (Ctrl+C para detener)")

        try:
            while self.__tiempo_transcurrido < limite:
                print("Tiempo transcurrido:", self.tiempo_en_pantalla(), end="\r")
                self.esperar_segundo()
                self.avanzar_segundo()
        except KeyboardInterrupt:
            self.detener_cronometro()
            return False

        self.pausar()
        print("Tiempo transcurrido:", self.tiempo_en_pantalla())
        print("Se llego al limite del cronometro")
        return True


# prueba rapida de la clase
if __name__ == "__main__":
    crono1 = Cronometro(5)
    print("Tiempo inicial:", crono1.consultar_tiempo_transcurrido())
    crono1.ejecutar_conteo()
    print("Tiempo final:", crono1.consultar_tiempo_transcurrido(), "segundos")
    crono1.reiniciar()
    print("Despues de reiniciar:", crono1.consultar_tiempo_transcurrido())
