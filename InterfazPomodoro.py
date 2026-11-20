# Archivo: InterfazPomodoro.py
# Frontend: toda la ventana del programa hecha con tkinter.
# Esta clase no toca el Excel directamente, para eso llama al GestorExcel (backend)

import os
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
from Materia import Materia
from Cronometro import Cronometro


class InterfazPomodoro:
    colores = {"Estudio": "#c0392b", "Descanso": "#27ae60", "Descanso largo": "#16a085", "Libre": "#2c6fbb"}

    def __init__(self, ventana, sesion, configuracion, historial, gestor, estadisticas):
        self.ventana = ventana
        self.sesion = sesion
        self.configuracion = configuracion
        self.historial = historial
        self.gestor = gestor
        self.estadisticas = estadisticas

        self.ventana.title("Sistema de Gestion de Tiempo Pomodoro")
        self.ventana.geometry("820x700")
        self.ventana.resizable(False, False)

        self.materias = []      # lista de objetos Materia
        self.medidor = None     # el Temporizador o Cronometro que se esta usando
        self.en_marcha = False
        self.id_after = None    # para poder cancelar el .after() cuando se pausa

        self.crear_menu()
        self.crear_zona_reloj()
        self.crear_zona_opciones()
        self.crear_zona_historial()

        # si cierran con la X tambien se pregunta si hay un bloque corriendo
        self.ventana.protocol("WM_DELETE_WINDOW", self.salir)

        self.cargar_datos()
        self.cargar_tabla()
        self.actualizar_pantalla()

    # ------------------------------------------------------------------
    # construccion de la ventana
    # ------------------------------------------------------------------

    def crear_menu(self):
        # BARRA DE MENU
        self.barra_menu = tk.Menu(self.ventana)

        self.menu_archivo = tk.Menu(self.barra_menu, tearoff=0)
        self.menu_archivo.add_command(label="Abrir Excel...", command=self.abrir_archivo)
        self.menu_archivo.add_command(label="Guardar copia como...", command=self.guardar_como)
        self.menu_archivo.add_separator()
        self.menu_archivo.add_command(label="Salir", command=self.salir)
        self.barra_menu.add_cascade(label="Archivo", menu=self.menu_archivo)

        self.menu_herramientas = tk.Menu(self.barra_menu, tearoff=0)
        self.menu_herramientas.add_command(label="Configurar tiempos", command=self.abrir_configuracion)
        self.menu_herramientas.add_command(label="Estadisticas", command=self.abrir_estadisticas)
        self.menu_herramientas.add_separator()
        self.menu_herramientas.add_command(label="Eliminar materia seleccionada", command=self.eliminar_materia)
        self.menu_herramientas.add_command(label="Borrar todo el historial", command=self.borrar_historial)
        self.barra_menu.add_cascade(label="Herramientas", menu=self.menu_herramientas)

        self.menu_ayuda = tk.Menu(self.barra_menu, tearoff=0)
        self.menu_ayuda.add_command(label="Acerca de", command=self.acerca_de)
        self.barra_menu.add_cascade(label="Ayuda", menu=self.menu_ayuda)

        self.ventana.config(menu=self.barra_menu)

    def crear_zona_reloj(self):
        self.marco_reloj = tk.Frame(self.ventana, padx=20, pady=10)
        self.marco_reloj.grid(row=0, column=0, sticky="n")

        self.etiqueta_estado = tk.Label(self.marco_reloj, text="Estudio", font=("Arial", 18, "bold"))
        self.etiqueta_estado.pack(pady=(10, 0))

        self.etiqueta_reloj = tk.Label(self.marco_reloj, text="25:00", font=("Consolas", 64, "bold"))
        self.etiqueta_reloj.pack()

        self.etiqueta_info = tk.Label(self.marco_reloj, text="", font=("Arial", 11))
        self.etiqueta_info.pack(pady=5)

        # botones
        self.marco_botones = tk.Frame(self.marco_reloj)
        self.marco_botones.pack(pady=15)

        self.boton_iniciar = tk.Button(self.marco_botones, text="Iniciar", width=12, font=("Arial", 11, "bold"),
                                       command=self.iniciar_pausar)
        self.boton_iniciar.grid(row=0, column=0, padx=5)

        self.boton_saltar = tk.Button(self.marco_botones, text="Saltar", width=12, font=("Arial", 11),
                                      command=self.saltar)
        self.boton_saltar.grid(row=0, column=1, padx=5)

        self.boton_reiniciar = tk.Button(self.marco_botones, text="Reiniciar", width=12, font=("Arial", 11),
                                         command=self.reiniciar)
        self.boton_reiniciar.grid(row=0, column=2, padx=5)

    def crear_zona_opciones(self):
        self.marco_opciones = tk.Frame(self.ventana, padx=15, pady=15, relief="groove", borderwidth=2)
        self.marco_opciones.grid(row=0, column=1, sticky="n", pady=15)

        # Radiobutton para escoger el modo
        tk.Label(self.marco_opciones, text="Modo", font=("Arial", 11, "bold")).grid(row=0, column=0, sticky="w")
        self.modo = tk.StringVar(value="Pomodoro")
        tk.Radiobutton(self.marco_opciones, text="Pomodoro (estudio / descanso)", variable=self.modo,
                       value="Pomodoro", command=self.cambiar_modo).grid(row=1, column=0, columnspan=2, sticky="w")
        tk.Radiobutton(self.marco_opciones, text="Cronometro libre", variable=self.modo,
                       value="Libre", command=self.cambiar_modo).grid(row=2, column=0, columnspan=2, sticky="w")

        # Combobox con las materias
        tk.Label(self.marco_opciones, text="Materia", font=("Arial", 11, "bold")).grid(row=3, column=0, sticky="w",
                                                                                    pady=(15, 0))
        self.materia = tk.StringVar()
        self.lista_materias = ttk.Combobox(self.marco_opciones, textvariable=self.materia, state="readonly", width=27)
        self.lista_materias.grid(row=4, column=0, columnspan=2, sticky="w")

        # Entry para agregar una materia nueva
        tk.Label(self.marco_opciones, text="Nueva materia").grid(row=5, column=0, sticky="w", pady=(10, 0))
        self.entrada_materia = tk.Entry(self.marco_opciones, width=20)
        self.entrada_materia.grid(row=6, column=0, sticky="w")
        tk.Button(self.marco_opciones, text="Agregar", command=self.agregar_materia).grid(row=6, column=1, padx=5)

        # Checkbuttons
        self.modo_demo = tk.BooleanVar(value=False)
        tk.Checkbutton(self.marco_opciones, text="Modo demo (1 min = 1 seg)", variable=self.modo_demo,
                       command=self.cambiar_demo).grid(row=7, column=0, columnspan=2, sticky="w", pady=(15, 0))
        self.sonido = tk.BooleanVar(value=True)
        tk.Checkbutton(self.marco_opciones, text="Sonido al terminar un bloque",
                       variable=self.sonido).grid(row=8, column=0, columnspan=2, sticky="w")

        # botones que abren las ventanas secundarias
        tk.Button(self.marco_opciones, text="Configurar tiempos", width=24,
                  command=self.abrir_configuracion).grid(row=9, column=0, columnspan=2, pady=(15, 3))
        tk.Button(self.marco_opciones, text="Ver estadisticas", width=24,
                  command=self.abrir_estadisticas).grid(row=10, column=0, columnspan=2)

    def crear_zona_historial(self):
        self.marco_historial = tk.Frame(self.ventana, padx=15)
        self.marco_historial.grid(row=1, column=0, columnspan=2, sticky="we", pady=(5, 0))

        tk.Label(self.marco_historial, text="Historial de sesiones", font=("Arial", 12, "bold")).grid(row=0, column=0,
                                                                                                   sticky="w")
        # TREEVIEW
        columnas = ("id", "fecha", "hora", "materia", "tipo", "minutos", "estado", "nota")
        self.tabla = ttk.Treeview(self.marco_historial, columns=columnas, show="headings", height=9)

        self.tabla.heading("id", text="#")
        self.tabla.heading("fecha", text="Fecha")
        self.tabla.heading("hora", text="Hora")
        self.tabla.heading("materia", text="Materia")
        self.tabla.heading("tipo", text="Tipo")
        self.tabla.heading("minutos", text="Minutos")
        self.tabla.heading("estado", text="Estado")
        self.tabla.heading("nota", text="Nota")

        self.tabla.column("id", width=40, anchor="center")
        self.tabla.column("fecha", width=90, anchor="center")
        self.tabla.column("hora", width=55, anchor="center")
        self.tabla.column("materia", width=120)
        self.tabla.column("tipo", width=105)
        self.tabla.column("minutos", width=65, anchor="center")
        self.tabla.column("estado", width=85, anchor="center")
        self.tabla.column("nota", width=190)

        # colores por tipo de bloque
        self.tabla.tag_configure("Estudio", background="#fbe3e0")
        self.tabla.tag_configure("Descanso", background="#e2f5e9")
        self.tabla.tag_configure("Descanso largo", background="#d9f2ee")
        self.tabla.tag_configure("Libre", background="#e1ecf8")

        self.tabla.grid(row=1, column=0, columnspan=3)

        barra = ttk.Scrollbar(self.marco_historial, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=barra.set)
        barra.grid(row=1, column=3, sticky="ns")

        self.etiqueta_total = tk.Label(self.marco_historial, text="", font=("Arial", 10))
        self.etiqueta_total.grid(row=2, column=0, sticky="w", pady=8)

        self.boton_editar = tk.Button(self.marco_historial, text="Editar sesion", width=15,
                                      command=self.abrir_edicion)
        self.boton_editar.grid(row=2, column=1, sticky="e", pady=8)

        self.boton_eliminar = tk.Button(self.marco_historial, text="Eliminar sesion", width=15,
                                        command=self.eliminar_sesion)
        self.boton_eliminar.grid(row=2, column=2, sticky="e", pady=8, padx=(8, 0))

    # ------------------------------------------------------------------
    # datos (se piden al backend)
    # ------------------------------------------------------------------

    def cargar_datos(self):
        try:
            self.gestor.preparar_archivo()

            estudio, descanso = self.gestor.leer_configuracion()
            try:
                self.configuracion.establecer_tiempos(estudio, descanso)
            except ValueError:
                messagebox.showwarning("Configuracion", "Los tiempos guardados en el Excel no son validos, "
                                                        "se usan 25 y 5 minutos")
                self.configuracion.restablecer_por_defecto()

            self.materias.clear()
            for nombre, meta in self.gestor.leer_materias():
                try:
                    self.materias.append(Materia(nombre, meta))
                except ValueError:
                    print("Materia invalida en el Excel:", nombre)

            self.historial.cargar_sesiones(self.gestor.leer_sesiones())
        except (ValueError, PermissionError) as error:
            messagebox.showerror("Error con el archivo", str(error))

        self.actualizar_lista_materias()
        nombre = os.path.basename(self.gestor.consultar_archivo())
        self.ventana.title(f"Sistema de Gestion de Tiempo Pomodoro - {nombre}")

    def actualizar_lista_materias(self):
        nombres = []
        for materia in self.materias:
            nombres.append(materia.consultar_nombre())
        if len(nombres) == 0:
            nombres.append("General")
        self.lista_materias["values"] = nombres
        if self.materia.get() not in nombres:
            self.lista_materias.current(0)

    def agregar_materia(self):
        try:
            nueva = Materia(self.entrada_materia.get())
        except ValueError as error:
            messagebox.showerror("Materia no valida", str(error))
            return

        for materia in self.materias:
            if materia.consultar_nombre().lower() == nueva.consultar_nombre().lower():
                messagebox.showwarning("Materia repetida", "Esa materia ya esta en la lista")
                return

        try:
            self.gestor.guardar_materia(nueva.consultar_nombre(), nueva.consultar_meta())
        except (ValueError, PermissionError) as error:
            messagebox.showerror("Error", str(error))
            return

        self.materias.append(nueva)
        self.actualizar_lista_materias()
        self.materia.set(nueva.consultar_nombre())
        self.entrada_materia.delete(0, tk.END)

    def eliminar_materia(self):
        nombre = self.materia.get()
        if nombre == "General":
            messagebox.showwarning("Materia", "La materia General no se puede eliminar")
            return
        if not messagebox.askyesno("Eliminar materia", f"Eliminar la materia '{nombre}'?\n"
                                                       "Las sesiones que ya tiene no se borran"):
            return
        try:
            self.gestor.eliminar_materia(nombre)
        except (ValueError, PermissionError) as error:
            messagebox.showerror("Error", str(error))
            return
        for materia in self.materias:
            if materia.consultar_nombre() == nombre:
                self.materias.remove(materia)
                break
        self.actualizar_lista_materias()

    def guardar_en_excel(self, sesion):
        try:
            self.gestor.guardar_sesion(sesion)
        except (ValueError, PermissionError) as error:
            messagebox.showerror("No se pudo guardar", str(error))
        self.agregar_a_tabla(sesion)
        self.actualizar_total()

    # ------------------------------------------------------------------
    # tabla del historial
    # ------------------------------------------------------------------

    def valores_de_sesion(self, sesion):
        if sesion["completada"]:
            estado = "Completa"
        else:
            estado = "Incompleta"
        return (sesion["id"], sesion["fecha"], sesion["hora"], sesion["materia"], sesion["tipo"],
                sesion["duracion"], estado, sesion["nota"])

    def agregar_a_tabla(self, sesion):
        # el iid de cada fila es el id de la sesion, asi es facil encontrarla despues
        self.tabla.insert("", tk.END, iid=str(sesion["id"]), values=self.valores_de_sesion(sesion),
                          tags=(sesion["tipo"],))
        self.tabla.see(str(sesion["id"]))

    def cargar_tabla(self):
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        for sesion in self.historial.consultar_historial():
            self.agregar_a_tabla(sesion)
        self.actualizar_total()

    def actualizar_total(self):
        resumen = self.estadisticas.resumen_general()
        self.etiqueta_total.config(text=f"Sesiones: {resumen['sesiones']}   |   "
                                        f"Estudio total: {resumen['minutos_estudio']} min   |   "
                                        f"Pomodoros completos: {resumen['pomodoros']}")

    def sesion_seleccionada(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showerror("Error", "Primero seleccione una sesion de la tabla")
            return None
        return int(seleccion[0])

    def eliminar_sesion(self):
        id_sesion = self.sesion_seleccionada()
        if id_sesion is None:
            return
        if not messagebox.askyesno("Eliminar", f"Seguro que quiere eliminar la sesion #{id_sesion}?"):
            return
        try:
            self.gestor.eliminar_sesion(id_sesion)
            self.historial.eliminar_sesion(id_sesion)
        except (ValueError, PermissionError) as error:
            messagebox.showerror("No se pudo eliminar", str(error))
            return
        self.tabla.delete(str(id_sesion))
        self.actualizar_total()
        self.actualizar_pantalla()

    def borrar_historial(self):
        if self.en_marcha:
            messagebox.showwarning("Historial", "Pause o reinicie el bloque primero")
            return
        if not messagebox.askyesno("Borrar historial", "Se van a borrar TODAS las sesiones del Excel.\n"
                                                       "Esto no se puede deshacer. Continuar?"):
            return
        try:
            self.gestor.eliminar_todas_las_sesiones()
        except (ValueError, PermissionError) as error:
            messagebox.showerror("Error", str(error))
            return
        self.historial.limpiar_historial()
        self.sesion.reiniciar_sesion()
        self.cargar_tabla()
        self.detener()
        self.boton_iniciar.config(text="Iniciar")
        self.actualizar_pantalla()

    # ------------------------------------------------------------------
    # menu archivo (filedialog)
    # ------------------------------------------------------------------

    def abrir_archivo(self):
        if self.en_marcha:
            messagebox.showwarning("Abrir", "Pause o reinicie el bloque antes de cambiar de archivo")
            return
        ruta = filedialog.askopenfilename(title="Abrir un registro de Pomodoro",
                                          filetypes=[("Archivos de Excel", "*.xlsx")])
        if not ruta:
            return  # el usuario cancelo
        try:
            self.gestor.cambiar_archivo(ruta)
        except (ValueError, PermissionError) as error:
            messagebox.showerror("No se pudo abrir", str(error))
            return

        # se carga todo lo del archivo nuevo y la sesion empieza de cero
        self.sesion.reiniciar_sesion()
        self.medidor = None
        self.boton_iniciar.config(text="Iniciar")
        self.cargar_datos()
        self.cargar_tabla()
        self.actualizar_pantalla()
        messagebox.showinfo("Archivo abierto", "Se cargo el archivo " + os.path.basename(ruta))

    def guardar_como(self):
        ruta = filedialog.asksaveasfilename(title="Guardar copia del registro", defaultextension=".xlsx",
                                            filetypes=[("Archivos de Excel", "*.xlsx")])
        if not ruta:
            return
        try:
            self.gestor.guardar_copia(ruta)
            self.gestor.cambiar_archivo(ruta)  # se sigue trabajando sobre la copia, como en clase
        except (ValueError, PermissionError) as error:
            messagebox.showerror("No se pudo guardar", str(error))
            return
        self.ventana.title(f"Sistema de Gestion de Tiempo Pomodoro - {os.path.basename(ruta)}")
        messagebox.showinfo("Archivo guardado", "Se guardo la copia y ahora se trabaja sobre ella")

    def acerca_de(self):
        messagebox.showinfo("Acerca de", "Sistema de Gestion de Tiempo Pomodoro\n"
                                         "Programacion II - Parcial 3\n"
                                         "Hector Danilo Alvarez Arenas\n\n"
                                         "Bloques de 25 min de estudio y 5 de descanso.\n"
                                         "Cada 4 pomodoros hay un descanso largo.")

    def salir(self):
        if self.en_marcha:
            if not messagebox.askyesno("Salir", "Hay un bloque corriendo y no se va a guardar. Salir igual?"):
                return
        self.ventana.destroy()

    # ------------------------------------------------------------------
    # ventanas secundarias (Toplevel)
    # ------------------------------------------------------------------

    def nueva_ventana(self, titulo, tamano):
        ventana2 = tk.Toplevel(self.ventana)
        ventana2.title(titulo)
        if tamano is not None:
            ventana2.geometry(tamano)  # si no se le da tamano, se acomoda sola al contenido
        ventana2.resizable(False, False)
        ventana2.transient(self.ventana)  # que quede encima de la principal
        ventana2.grab_set()               # y que no se pueda tocar la principal mientras este abierta
        return ventana2

    def abrir_configuracion(self):
        self.ventana_config = self.nueva_ventana("Configurar tiempos", "300x175")
        marco = tk.Frame(self.ventana_config, padx=20, pady=15)
        marco.pack()

        tk.Label(marco, text="Minutos de estudio:").grid(row=0, column=0, sticky="w", pady=5)
        self.entrada_estudio = tk.Entry(marco, width=8)
        self.entrada_estudio.insert(0, str(self.configuracion.consultar_tiempo_estudio()))
        self.entrada_estudio.grid(row=0, column=1, pady=5)

        tk.Label(marco, text="Minutos de descanso:").grid(row=1, column=0, sticky="w", pady=5)
        self.entrada_descanso = tk.Entry(marco, width=8)
        self.entrada_descanso.insert(0, str(self.configuracion.consultar_tiempo_descanso()))
        self.entrada_descanso.grid(row=1, column=1, pady=5)

        tk.Label(marco, text="(entre 1 y 120, el descanso mas corto)", fg="gray").grid(row=2, column=0, columnspan=2)
        tk.Button(marco, text="Guardar", width=12, command=self.guardar_configuracion).grid(row=3, column=0,
                                                                                         columnspan=2, pady=12)

    def guardar_configuracion(self):
        try:
            estudio = int(self.entrada_estudio.get())
            descanso = int(self.entrada_descanso.get())
        except ValueError:
            messagebox.showerror("Dato no valido", "Escriba los minutos como numeros enteros", parent=self.ventana_config)
            return

        try:
            self.configuracion.establecer_tiempos(estudio, descanso)
            self.gestor.guardar_configuracion(estudio, descanso)
        except (ValueError, PermissionError) as error:
            messagebox.showerror("Dato no valido", str(error), parent=self.ventana_config)
            return

        self.ventana_config.destroy()
        if self.modo.get() == "Pomodoro" and self.sesion.hay_bloque_pausado():
            messagebox.showinfo("Configuracion", "Tiempos guardados. Se aplican desde el siguiente bloque")
        else:
            messagebox.showinfo("Configuracion", "Tiempos guardados")
        self.actualizar_pantalla()

    def abrir_edicion(self):
        id_sesion = self.sesion_seleccionada()
        if id_sesion is None:
            return
        sesion = self.historial.buscar_sesion(id_sesion)
        self.id_editando = id_sesion

        self.ventana_edicion = self.nueva_ventana(f"Editar sesion #{id_sesion}", "340x260")
        marco = tk.Frame(self.ventana_edicion, padx=20, pady=15)
        marco.pack()

        tk.Label(marco, text=f"{sesion['tipo']} de {sesion['duracion']} min",
                 font=("Arial", 11, "bold")).grid(row=0, column=0, columnspan=2)
        tk.Label(marco, text=f"{sesion['fecha']} a las {sesion['hora']}", fg="gray").grid(row=1, column=0,
                                                                                          columnspan=2, pady=(0, 10))

        tk.Label(marco, text="Materia:").grid(row=2, column=0, sticky="w")
        nombres = ["-"]
        for materia in self.materias:
            nombres.append(materia.consultar_nombre())
        self.materia_edicion = tk.StringVar(value=sesion["materia"])
        ttk.Combobox(marco, textvariable=self.materia_edicion, values=nombres, state="readonly",
                     width=20).grid(row=2, column=1, pady=4)

        tk.Label(marco, text="Nota:").grid(row=3, column=0, sticky="w")
        self.entrada_nota = tk.Entry(marco, width=23)
        self.entrada_nota.insert(0, sesion["nota"])
        self.entrada_nota.grid(row=3, column=1, pady=4)

        self.completada_edicion = tk.BooleanVar(value=sesion["completada"])
        tk.Checkbutton(marco, text="Sesion completa", variable=self.completada_edicion).grid(row=4, column=0,
                                                                                            columnspan=2, pady=4)

        tk.Button(marco, text="Guardar cambios", width=15, command=self.guardar_edicion).grid(row=5, column=0,
                                                                                            columnspan=2, pady=10)

    def guardar_edicion(self):
        nota = self.entrada_nota.get().strip()
        try:
            sesion = self.historial.actualizar_sesion(self.id_editando, self.materia_edicion.get(), nota,
                                                      self.completada_edicion.get())
            self.gestor.actualizar_sesion(sesion)
        except (ValueError, PermissionError) as error:
            messagebox.showerror("No se pudo guardar", str(error), parent=self.ventana_edicion)
            return

        self.tabla.item(str(self.id_editando), values=self.valores_de_sesion(sesion))
        self.ventana_edicion.destroy()
        self.actualizar_total()
        self.actualizar_pantalla()

    def abrir_estadisticas(self):
        ventana_est = self.nueva_ventana("Estadisticas", None)
        marco = tk.Frame(ventana_est, padx=20, pady=15)
        marco.pack(fill="both")

        resumen = self.estadisticas.resumen_general()
        tk.Label(marco, text="Resumen general", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=4,
                                                                                sticky="w")
        datos = [
            ("Sesiones guardadas:", resumen["sesiones"]),
            ("Minutos de estudio:", resumen["minutos_estudio"]),
            ("Minutos de descanso:", resumen["minutos_descanso"]),
            ("Pomodoros completos:", resumen["pomodoros"]),
            ("Materia mas estudiada:", resumen["materia_top"]),
        ]
        fila = 1
        for texto, valor in datos:
            tk.Label(marco, text=texto).grid(row=fila, column=0, columnspan=2, sticky="w")
            tk.Label(marco, text=str(valor), font=("Arial", 10, "bold")).grid(row=fila, column=2, columnspan=2,
                                                                             sticky="w")
            fila += 1

        tk.Label(marco, text="Hoy por materia (meta diaria)", font=("Arial", 12, "bold")).grid(row=fila, column=0,
                                                                                            columnspan=4, sticky="w",
                                                                                            pady=(15, 5))
        fila += 1
        for i, titulo in enumerate(["Materia", "Hoy", "Meta", "Avance"]):
            tk.Label(marco, text=titulo, fg="gray").grid(row=fila, column=i, sticky="w", padx=(0, 15))
        fila += 1

        hoy = self.estadisticas.minutos_por_materia(solo_hoy=True)
        for materia in self.materias:
            minutos = hoy.get(materia.consultar_nombre(), 0)
            tk.Label(marco, text=materia.consultar_nombre()).grid(row=fila, column=0, sticky="w")
            tk.Label(marco, text=f"{minutos} min").grid(row=fila, column=1, sticky="w")
            tk.Label(marco, text=f"{materia.consultar_meta()} min").grid(row=fila, column=2, sticky="w")
            tk.Label(marco, text=f"{materia.porcentaje_meta(minutos)} %").grid(row=fila, column=3, sticky="w")
            fila += 1

        tk.Button(marco, text="Cerrar", width=10, command=ventana_est.destroy).grid(row=fila, column=0, columnspan=4,
                                                                                   pady=15)

    # ------------------------------------------------------------------
    # temporizador
    # ------------------------------------------------------------------

    def obtener_medidor(self):
        # polimorfismo: puede ser un Temporizador o un Cronometro,
        # los dos se manejan igual con avanzar_segundo()
        if self.modo.get() == "Pomodoro":
            return self.sesion.preparar_bloque()
        if self.medidor is None:
            self.medidor = Cronometro(120 * 60)  # el cronometro libre llega maximo a 2 horas
        return self.medidor

    def iniciar_pausar(self):
        if self.en_marcha:
            self.pausar()
            return

        try:
            self.sesion.cambiar_materia(self.materia.get())
        except ValueError as error:
            messagebox.showerror("Falta la materia", str(error))
            return

        self.medidor = self.obtener_medidor()
        self.en_marcha = True
        self.boton_iniciar.config(text="Pausar")
        self.id_after = self.ventana.after(self.configuracion.consultar_espera_ms(), self.contar)

    def contar(self):
        # se llama solita cada segundo (o mas rapido en modo demo)
        if not self.en_marcha:
            return
        termino = self.medidor.avanzar_segundo()
        self.actualizar_pantalla()
        if termino:
            self.finalizar_bloque()
        else:
            self.id_after = self.ventana.after(self.configuracion.consultar_espera_ms(), self.contar)

    def pausar(self):
        self.en_marcha = False
        if self.id_after is not None:
            self.ventana.after_cancel(self.id_after)
            self.id_after = None
        self.boton_iniciar.config(text="Continuar")

    def detener(self):
        self.pausar()
        self.boton_iniciar.config(text="Iniciar")

    def avisar(self, titulo, mensaje):
        if self.sonido.get():
            self.ventana.bell()
        messagebox.showinfo(titulo, mensaje)

    def finalizar_bloque(self):
        self.detener()
        if self.modo.get() == "Pomodoro":
            sesion = self.sesion.terminar_bloque()
            self.guardar_en_excel(sesion)
            self.actualizar_pantalla()
            self.avisar("Bloque terminado", f"Termino el bloque de {sesion['tipo']}.\n"
                                            f"Sigue: {self.sesion.consultar_estado_actual()}")
        else:
            self.terminar_libre()
            self.avisar("Cronometro", "Se llego al limite de 2 horas del cronometro")

    def terminar_libre(self):
        minutos = self.medidor.consultar_tiempo_transcurrido() // 60
        if minutos > 0:
            sesion = self.historial.registrar_sesion("Libre", minutos, True, self.materia.get())
            self.guardar_en_excel(sesion)
        else:
            messagebox.showinfo("Cronometro", "No alcanzo ni un minuto, no se guarda")
        self.medidor = None
        self.actualizar_pantalla()

    def saltar(self):
        if self.modo.get() == "Libre":
            if self.medidor is None:
                return
            self.detener()
            self.terminar_libre()
            return

        self.detener()
        sesion = self.sesion.saltar_bloque()
        if sesion is not None:
            self.guardar_en_excel(sesion)
        self.actualizar_pantalla()

    def reiniciar(self):
        self.detener()
        if self.modo.get() == "Pomodoro":
            self.sesion.reiniciar_bloque()
        else:
            self.medidor = None
        self.actualizar_pantalla()

    def cambiar_modo(self):
        if self.en_marcha:
            messagebox.showwarning("Modo", "Pause o reinicie el bloque antes de cambiar de modo")
            if self.modo.get() == "Pomodoro":
                self.modo.set("Libre")
            else:
                self.modo.set("Pomodoro")
            return
        self.medidor = None
        self.boton_iniciar.config(text="Iniciar")
        if self.modo.get() == "Libre":
            self.boton_saltar.config(text="Terminar")
        else:
            self.boton_saltar.config(text="Saltar")
        self.actualizar_pantalla()

    def cambiar_demo(self):
        self.configuracion.establecer_modo_demo(self.modo_demo.get())

    def actualizar_pantalla(self):
        if self.modo.get() == "Pomodoro":
            estado = self.sesion.consultar_estado_actual()
            if self.sesion.hay_bloque_pausado():
                tiempo = self.sesion.consultar_tiempo_pausado()
            else:
                tiempo = self.sesion.crear_bloque().tiempo_en_pantalla()
            color = InterfazPomodoro.colores[estado]
        else:
            estado = "Cronometro libre"
            if self.medidor is None:
                tiempo = "00:00"
            else:
                tiempo = self.medidor.tiempo_en_pantalla()
            color = InterfazPomodoro.colores["Libre"]

        self.etiqueta_estado.config(text=estado, fg=color)
        self.etiqueta_reloj.config(text=tiempo, fg=color)
        self.etiqueta_info.config(text=f"Pomodoros hoy: {self.estadisticas.pomodoros_de_hoy()}   |   "
                                       f"Minutos de estudio hoy: {self.estadisticas.minutos_de_hoy()}")
