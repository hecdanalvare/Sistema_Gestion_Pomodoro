# Archivo: MedidorTiempo.py
# Clase padre. De aqui heredan Temporizador y Cronometro

import time


class MedidorTiempo:
    def __init__(self, duracion_segundos=60, espera=1):
        # la duracion tiene que ser un entero positivo, si no se lanza el error
        if type(duracion_segundos) != int or duracion_segundos <= 0:
            raise ValueError("La duracion debe ser un numero entero mayor a cero")

        self.__duracion_segundos = duracion_segundos
        self.__espera = espera  # lo que dura cada "segundo" (1 normal, mucho menos en modo demo)
        self.__en_marcha = False

    def iniciar(self):
        self.__en_marcha = True

    def pausar(self):
        self.__en_marcha = False

    def reiniciar(self):
        self.__en_marcha = False
        print("Medidor reiniciado")

    # metodos para consultar los atributos privados
    def consultar_duracion(self):
        return self.__duracion_segundos

    def consultar_estado(self):
        return self.__en_marcha

    def consultar_espera(self):
        return self.__espera

    # estos dos los heredan las hijas y los usan igual, no se sobrescriben
    def formato_tiempo(self, segundos):
        minutos = segundos // 60
        seg = segundos % 60
        return f"{minutos:02d}:{seg:02d}"

    def esperar_segundo(self):
        time.sleep(self.__espera)

    # ---- metodos que cada hija hace a su manera (polimorfismo) ----

    # avanza un segundo y devuelve True cuando ya se acabo el conteo
    # (la interfaz grafica lo llama cada segundo con .after())
    def avanzar_segundo(self):
        return True

    # lo que se muestra en el reloj
    def tiempo_en_pantalla(self):
        return self.formato_tiempo(self.__duracion_segundos)

    # cuanto va del conteo, de 0 a 100 (para la barra de progreso)
    def porcentaje_avance(self):
        return 0

    # version de consola del conteo (la del parcial 2)
    def ejecutar_conteo(self):
        print("Medicion general de", self.formato_tiempo(self.__duracion_segundos))
        return True


# prueba rapida de la clase
if __name__ == "__main__":
    medidor1 = MedidorTiempo(150)
    print("Duracion:", medidor1.consultar_duracion(), "segundos =", medidor1.formato_tiempo(150))

    medidor1.iniciar()
    print("En marcha?", medidor1.consultar_estado())
    medidor1.pausar()
    print("En marcha?", medidor1.consultar_estado())
    medidor1.ejecutar_conteo()

    try:
        medidor_malo = MedidorTiempo(-10)
    except ValueError as e:
        print("Error:", e)
