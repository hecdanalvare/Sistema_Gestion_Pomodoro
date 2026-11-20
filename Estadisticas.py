# Archivo: Estadisticas.py
# Saca los numeros del historial: minutos por materia, lo de hoy, totales

from datetime import datetime


class Estadisticas:
    def __init__(self, historial):
        self.__historial = historial

    def es_estudio(self, sesion):
        # el cronometro libre tambien cuenta como estudio
        return sesion["tipo"] == "Estudio" or sesion["tipo"] == "Libre"

    def minutos_por_materia(self, solo_hoy=False):
        hoy = datetime.now().strftime("%Y-%m-%d")
        resultado = {}
        for sesion in self.__historial.consultar_historial():
            if not self.es_estudio(sesion):
                continue
            if solo_hoy and sesion["fecha"] != hoy:
                continue
            materia = sesion["materia"]
            if materia in resultado:
                resultado[materia] += sesion["duracion"]
            else:
                resultado[materia] = sesion["duracion"]
        return resultado

    def minutos_de_hoy(self):
        total = 0
        for minutos in self.minutos_por_materia(solo_hoy=True).values():
            total += minutos
        return total

    def pomodoros_de_hoy(self):
        hoy = datetime.now().strftime("%Y-%m-%d")
        contador = 0
        for sesion in self.__historial.consultar_historial():
            if sesion["tipo"] == "Estudio" and sesion["completada"] and sesion["fecha"] == hoy:
                contador += 1
        return contador

    def materia_mas_estudiada(self):
        por_materia = self.minutos_por_materia()
        if len(por_materia) == 0:
            return "Ninguna todavia"
        mejor = ""
        mayor = -1
        for materia, minutos in por_materia.items():
            if minutos > mayor:
                mayor = minutos
                mejor = materia
        return mejor

    def resumen_general(self):
        total_estudio = 0
        total_descanso = 0
        for sesion in self.__historial.consultar_historial():
            if self.es_estudio(sesion):
                total_estudio += sesion["duracion"]
            else:
                total_descanso += sesion["duracion"]
        return {
            "sesiones": len(self.__historial.consultar_historial()),
            "minutos_estudio": total_estudio,
            "minutos_descanso": total_descanso,
            "pomodoros": self.__historial.contar_pomodoros(),
            "materia_top": self.materia_mas_estudiada()
        }


# prueba rapida de la clase
if __name__ == "__main__":
    from HistorialSesiones import HistorialSesiones

    historial = HistorialSesiones()
    historial.registrar_sesion("Estudio", 25, materia="Calculo")
    historial.registrar_sesion("Descanso", 5, materia="Calculo")
    historial.registrar_sesion("Estudio", 25, materia="Fisica")
    historial.registrar_sesion("Libre", 40, materia="Calculo")

    estadisticas = Estadisticas(historial)
    print("Por materia:", estadisticas.minutos_por_materia())
    print("Minutos de hoy:", estadisticas.minutos_de_hoy())
    print("Pomodoros de hoy:", estadisticas.pomodoros_de_hoy())
    print("Resumen:", estadisticas.resumen_general())
