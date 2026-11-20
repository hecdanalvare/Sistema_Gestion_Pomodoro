# Archivo: GestorExcel.py
# Backend: todo lo que tiene que ver con el archivo de Excel (openpyxl) esta aqui.
# Crear el archivo, leer, escribir, actualizar y eliminar registros.
# El archivo tiene 3 hojas: Sesiones, Materias y Configuracion

from zipfile import BadZipFile
from openpyxl import Workbook
from openpyxl import load_workbook
from openpyxl.utils.exceptions import InvalidFileException


class GestorExcel:
    encabezados_sesiones = ["ID", "Fecha", "Hora", "Materia", "Tipo", "Minutos", "Completada", "Nota"]
    encabezados_materias = ["Materia", "Meta diaria (min)"]
    encabezados_configuracion = ["Opcion", "Valor"]

    def __init__(self, nombre_archivo="Registro_Pomodoro.xlsx"):
        self.__nombre_archivo = nombre_archivo

    def consultar_archivo(self):
        return self.__nombre_archivo

    # ---------------- crear / abrir el archivo ----------------

    def preparar_archivo(self):
        # si el archivo no existe se crea con sus 3 hojas
        try:
            libro = load_workbook(self.__nombre_archivo)
        except FileNotFoundError:
            libro = Workbook()
            hoja = libro.active
            hoja.title = "Sesiones"
            hoja.append(GestorExcel.encabezados_sesiones)
            self.crear_hojas_faltantes(libro)
            self.guardar_libro(libro)
            libro.close()
            print("Se creo el archivo", self.__nombre_archivo)
            return

        # si existe pero le falta alguna hoja, se la agrega
        if self.crear_hojas_faltantes(libro):
            self.guardar_libro(libro)
        libro.close()

    def crear_hojas_faltantes(self, libro):
        cambio = False
        if "Sesiones" not in libro.sheetnames:
            hoja = libro.create_sheet("Sesiones")
            hoja.append(GestorExcel.encabezados_sesiones)
            cambio = True
        if "Materias" not in libro.sheetnames:
            hoja = libro.create_sheet("Materias")
            hoja.append(GestorExcel.encabezados_materias)
            hoja.append(["General", 60])
            cambio = True
        if "Configuracion" not in libro.sheetnames:
            hoja = libro.create_sheet("Configuracion")
            hoja.append(GestorExcel.encabezados_configuracion)
            hoja.append(["Tiempo estudio", 25])
            hoja.append(["Tiempo descanso", 5])
            cambio = True
        return cambio

    def abrir_libro(self, crear_si_falta=True):
        try:
            return load_workbook(self.__nombre_archivo)
        except FileNotFoundError:
            if not crear_si_falta:
                raise ValueError("No se encontro el archivo " + self.__nombre_archivo)
            # si borraron el archivo con el programa abierto, se vuelve a crear
            self.preparar_archivo()
            return load_workbook(self.__nombre_archivo)
        except (InvalidFileException, BadZipFile, KeyError):
            raise ValueError("El archivo esta danado o no es un archivo de Excel")

    def guardar_libro(self, libro, ruta=None):
        if ruta is None:
            ruta = self.__nombre_archivo
        try:
            libro.save(ruta)
        except PermissionError:
            # pasa cuando el archivo esta abierto en Excel
            raise PermissionError("No se pudo guardar. Cierre el archivo en Excel e intente otra vez")

    # para cuando el usuario abre otro Excel desde el menu
    def cambiar_archivo(self, ruta):
        anterior = self.__nombre_archivo
        self.__nombre_archivo = ruta
        try:
            libro = self.abrir_libro(crear_si_falta=False)
        except ValueError:
            self.__nombre_archivo = anterior
            raise
        if "Sesiones" not in libro.sheetnames:
            libro.close()
            self.__nombre_archivo = anterior
            raise ValueError("Ese Excel no tiene la hoja 'Sesiones', no es un archivo de este programa")
        self.crear_hojas_faltantes(libro)
        self.guardar_libro(libro)
        libro.close()

    def guardar_copia(self, ruta):
        libro = self.abrir_libro()
        self.guardar_libro(libro, ruta)
        libro.close()

    # ---------------- sesiones (CRUD) ----------------

    def leer_sesiones(self):
        libro = self.abrir_libro()
        hoja = libro["Sesiones"]
        sesiones = []
        for fila in hoja.iter_rows(min_row=2, values_only=True):
            if fila[0] is None:
                continue  # fila vacia
            try:
                sesion = {
                    "id": int(fila[0]),
                    "fecha": self.texto_fecha(fila[1]),
                    "hora": self.texto_hora(fila[2]),
                    "materia": str(fila[3]),
                    "tipo": str(fila[4]),
                    "duracion": int(fila[5]),
                    "completada": fila[6] == "Si",
                    "nota": fila[7] if fila[7] is not None else ""
                }
                sesiones.append(sesion)
            except (ValueError, TypeError, IndexError):
                print("Se salto una fila con datos raros:", fila)
        libro.close()
        return sesiones

    # si alguien abre el archivo en Excel y lo guarda, Excel puede convertir la fecha y la hora
    # en objetos de fecha; aqui se vuelven a dejar como texto
    def texto_fecha(self, valor):
        if hasattr(valor, "strftime"):
            return valor.strftime("%Y-%m-%d")
        return str(valor)

    def texto_hora(self, valor):
        if hasattr(valor, "strftime"):
            return valor.strftime("%H:%M")
        return str(valor)

    def guardar_sesion(self, sesion):
        libro = self.abrir_libro()
        hoja = libro["Sesiones"]
        hoja.append(self.sesion_a_fila(sesion))
        self.guardar_libro(libro)
        libro.close()

    def sesion_a_fila(self, sesion):
        if sesion["completada"]:
            completada = "Si"
        else:
            completada = "No"
        return [sesion["id"], sesion["fecha"], sesion["hora"], sesion["materia"], sesion["tipo"],
                sesion["duracion"], completada, sesion["nota"]]

    def buscar_fila(self, hoja, id_sesion):
        # devuelve el numero de fila del Excel donde esta esa sesion
        for numero in range(2, hoja.max_row + 1):
            if hoja.cell(row=numero, column=1).value == id_sesion:
                return numero
        raise ValueError(f"La sesion {id_sesion} no esta en el Excel")

    def actualizar_sesion(self, sesion):
        libro = self.abrir_libro()
        hoja = libro["Sesiones"]
        numero = self.buscar_fila(hoja, sesion["id"])
        for columna, valor in enumerate(self.sesion_a_fila(sesion), start=1):
            hoja.cell(row=numero, column=columna, value=valor)
        self.guardar_libro(libro)
        libro.close()

    def eliminar_sesion(self, id_sesion):
        libro = self.abrir_libro()
        hoja = libro["Sesiones"]
        numero = self.buscar_fila(hoja, id_sesion)
        hoja.delete_rows(numero)
        self.guardar_libro(libro)
        libro.close()

    def eliminar_todas_las_sesiones(self):
        libro = self.abrir_libro()
        hoja = libro["Sesiones"]
        if hoja.max_row > 1:
            hoja.delete_rows(2, hoja.max_row - 1)
        self.guardar_libro(libro)
        libro.close()

    # ---------------- materias ----------------

    def leer_materias(self):
        libro = self.abrir_libro()
        hoja = libro["Materias"]
        materias = []
        for fila in hoja.iter_rows(min_row=2, values_only=True):
            if fila[0] is None:
                continue
            try:
                materias.append((str(fila[0]), int(fila[1])))
            except (ValueError, TypeError):
                materias.append((str(fila[0]), 60))
        libro.close()
        return materias

    def guardar_materia(self, nombre, meta):
        libro = self.abrir_libro()
        hoja = libro["Materias"]
        hoja.append([nombre, meta])
        self.guardar_libro(libro)
        libro.close()

    def eliminar_materia(self, nombre):
        libro = self.abrir_libro()
        hoja = libro["Materias"]
        for numero in range(2, hoja.max_row + 1):
            if hoja.cell(row=numero, column=1).value == nombre:
                hoja.delete_rows(numero)
                self.guardar_libro(libro)
                libro.close()
                return
        libro.close()
        raise ValueError(f"La materia {nombre} no esta en el Excel")

    # ---------------- configuracion ----------------

    def leer_configuracion(self):
        libro = self.abrir_libro()
        hoja = libro["Configuracion"]
        datos = {"Tiempo estudio": 25, "Tiempo descanso": 5}
        for fila in hoja.iter_rows(min_row=2, values_only=True):
            if fila[0] in datos:
                try:
                    datos[fila[0]] = int(fila[1])
                except (ValueError, TypeError):
                    pass  # si alguien escribio algo raro se deja el valor por defecto
        libro.close()
        return datos["Tiempo estudio"], datos["Tiempo descanso"]

    def guardar_configuracion(self, estudio, descanso):
        libro = self.abrir_libro()
        hoja = libro["Configuracion"]
        if hoja.max_row > 1:
            hoja.delete_rows(2, hoja.max_row - 1)
        hoja.append(["Tiempo estudio", estudio])
        hoja.append(["Tiempo descanso", descanso])
        self.guardar_libro(libro)
        libro.close()


# prueba rapida de la clase (usa un archivo aparte para no danar el real)
if __name__ == "__main__":
    import os

    gestor = GestorExcel("prueba_gestor.xlsx")
    gestor.preparar_archivo()

    gestor.guardar_sesion({"id": 1, "fecha": "2026-11-20", "hora": "08:00", "materia": "Calculo",
                           "tipo": "Estudio", "duracion": 25, "completada": True, "nota": ""})
    gestor.guardar_sesion({"id": 2, "fecha": "2026-11-20", "hora": "08:30", "materia": "-",
                           "tipo": "Descanso", "duracion": 5, "completada": True, "nota": ""})
    print("Leidas:", gestor.leer_sesiones())

    gestor.actualizar_sesion({"id": 1, "fecha": "2026-11-20", "hora": "08:00", "materia": "Fisica",
                              "tipo": "Estudio", "duracion": 25, "completada": False, "nota": "se fue la luz"})
    gestor.eliminar_sesion(2)
    print("Despues de actualizar y borrar:", gestor.leer_sesiones())

    gestor.guardar_materia("Calculo", 90)
    print("Materias:", gestor.leer_materias())
    gestor.guardar_configuracion(50, 10)
    print("Configuracion:", gestor.leer_configuracion())

    try:
        gestor.eliminar_sesion(99)
    except ValueError as e:
        print("Error:", e)

    os.remove("prueba_gestor.xlsx")
