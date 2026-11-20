# Archivo: Materia.py
# Cada sesion de estudio se asocia a una materia (Calculo, Fisica, Programacion...)
# y cada materia tiene una meta de minutos de estudio al dia


class Materia:
    def __init__(self, nombre, meta_minutos=60):
        self.__nombre = self.validar_nombre(nombre)
        self.__meta_minutos = 60
        self.cambiar_meta(meta_minutos)

    def validar_nombre(self, nombre):
        if type(nombre) != str:
            raise ValueError("El nombre de la materia debe ser texto")
        nombre = nombre.strip()
        if len(nombre) < 2 or len(nombre) > 30:
            raise ValueError("El nombre de la materia debe tener entre 2 y 30 letras")
        if nombre.isdigit():
            raise ValueError("El nombre de la materia no puede ser solo numeros")
        # primera letra en mayuscula para que no queden "calculo" y "Calculo" distintos
        return nombre[0].upper() + nombre[1:]

    def consultar_nombre(self):
        return self.__nombre

    def consultar_meta(self):
        return self.__meta_minutos

    def cambiar_meta(self, meta_minutos):
        if type(meta_minutos) != int or meta_minutos < 10 or meta_minutos > 600:
            raise ValueError("La meta diaria debe ser un entero entre 10 y 600 minutos")
        self.__meta_minutos = meta_minutos

    def porcentaje_meta(self, minutos_estudiados):
        # cuanto lleva de la meta del dia (maximo 100)
        porcentaje = minutos_estudiados * 100 / self.__meta_minutos
        if porcentaje > 100:
            porcentaje = 100
        return round(porcentaje)


# prueba rapida de la clase
if __name__ == "__main__":
    calculo = Materia("calculo integral", 90)
    print(calculo.consultar_nombre(), "- meta:", calculo.consultar_meta(), "min")
    print("Con 45 min lleva el", calculo.porcentaje_meta(45), "% de la meta")
    print("Con 200 min lleva el", calculo.porcentaje_meta(200), "% de la meta")

    for nombre, meta in [("", 60), ("1234", 60), ("Fisica", 5), ("Fisica", "dos")]:
        try:
            Materia(nombre, meta)
        except ValueError as e:
            print(f"({nombre!r}, {meta!r}) -> Error: {e}")
