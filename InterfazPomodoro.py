# Archivo: InterfazPomodoro.py
# Frontend: toda la ventana del programa hecha con tkinter.
# Esta clase no toca el Excel directamente, para eso llama al GestorExcel (backend)

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
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
        self.ventana.geometry("820x420")
        self.ventana.resizable(False, False)

        self.materias = []      # lista de objetos Materia
        self.medidor = None     # el Temporizador o Cronometro que se esta usando
        self.en_marcha = False
        self.id_after = None    # para poder cancelar el .after() cuando se pausa

        self.crear_zona_reloj()
        self.crear_zona_opciones()

        self.cargar_datos()
        self.actualizar_pantalla()

    # ------------------------------------------------------------------
    # construccion de la ventana
    # ------------------------------------------------------------------

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

    def guardar_en_excel(self, sesion):
        try:
            self.gestor.guardar_sesion(sesion)
        except (ValueError, PermissionError) as error:
            messagebox.showerror("No se pudo guardar", str(error))

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
