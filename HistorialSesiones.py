# Archivo: HistorialSesiones.py
# Guarda cada bloque terminado en una lista de diccionarios
# (en el parcial 3 cada sesion tiene id, fecha y materia para poder guardarla en Excel)

from datetime import datetime


class HistorialSesiones:
    def __init__(self):
        self.__registro = []

    def siguiente_id(self):
        # el id nuevo es el mayor que haya + 1, asi no se repite aunque se borren sesiones
        mayor = 0
        for sesion in self.__registro:
            if sesion["id"] > mayor:
                mayor = sesion["id"]
        return mayor + 1

    def registrar_sesion(self, tipo_bloque, duracion_minutos, completada=True, materia="General", nota=""):
        if type(duracion_minutos) != int or duracion_minutos <= 0:
            raise ValueError("No se guardan sesiones de 0 minutos o con duracion invalida")

        ahora = datetime.now()
        sesion = {
            "id": self.siguiente_id(),
            "fecha": ahora.strftime("%Y-%m-%d"),
            "hora": ahora.strftime("%H:%M"),
            "materia": materia,
            "tipo": tipo_bloque,
            "duracion": duracion_minutos,
            "completada": completada,
            "nota": nota
        }
        self.__registro.append(sesion)
        print(f"Se guardo en el historial: {tipo_bloque} de {duracion_minutos} min ({materia})")
        return sesion

    # cuando se abre el programa las sesiones vienen del Excel
    def cargar_sesiones(self, lista_sesiones):
        self.__registro.clear()
        for sesion in lista_sesiones:
            self.__registro.append(sesion)

    def consultar_historial(self):
        return self.__registro

    def buscar_sesion(self, id_sesion):
        for sesion in self.__registro:
            if sesion["id"] == id_sesion:
                return sesion
        raise ValueError(f"No existe una sesion con id {id_sesion}")

    def actualizar_sesion(self, id_sesion, materia, nota, completada):
        sesion = self.buscar_sesion(id_sesion)
        sesion["materia"] = materia
        sesion["nota"] = nota
        sesion["completada"] = completada
        return sesion

    def eliminar_sesion(self, id_sesion):
        sesion = self.buscar_sesion(id_sesion)
        self.__registro.remove(sesion)

    def contar_pomodoros(self):
        # un pomodoro = un bloque de estudio que se termino completo
        contador = 0
        for sesion in self.__registro:
            if sesion["tipo"] == "Estudio" and sesion["completada"]:
                contador += 1
        return contador

    # resumen para la version de consola
    def mostrar_resumen(self):
        print("\n------ HISTORIAL DE SESIONES ------")
        if len(self.__registro) == 0:
            print("Todavia no hay sesiones guardadas")
            return

        total_estudio = 0
        total_descanso = 0

        for i, sesion in enumerate(self.__registro, start=1):
            if sesion["completada"]:
                estado = "completa"
            else:
                estado = "incompleta"
            print(f"{i}. [{sesion['fecha']} {sesion['hora']}] {sesion['tipo']} - {sesion['materia']} - "
                  f"{sesion['duracion']} min ({estado})")

            if sesion["tipo"] == "Descanso" or sesion["tipo"] == "Descanso largo":
                total_descanso += sesion["duracion"]
            else:
                total_estudio += sesion["duracion"]

        print("-" * 35)
        print("Minutos de estudio:", total_estudio)
        print("Minutos de descanso:", total_descanso)
        print("Pomodoros completos:", self.contar_pomodoros())

    def limpiar_historial(self):
        self.__registro.clear()
        print("Historial borrado")


# prueba rapida de la clase
if __name__ == "__main__":
    historial = HistorialSesiones()
    historial.registrar_sesion("Estudio", 25, materia="Calculo")
    historial.registrar_sesion("Descanso", 5)
    s = historial.registrar_sesion("Estudio", 12, False, "Fisica")
    historial.actualizar_sesion(s["id"], "Fisica", "me distraje con el celular", False)
    historial.mostrar_resumen()

    historial.eliminar_sesion(2)
    print("Despues de borrar la 2:", [x["id"] for x in historial.consultar_historial()])
    print("Siguiente id:", historial.siguiente_id())

    for prueba in [0, "25"]:
        try:
            historial.registrar_sesion("Estudio", prueba)
        except ValueError as e:
            print("Error:", e)
    try:
        historial.buscar_sesion(99)
    except ValueError as e:
        print("Error:", e)
