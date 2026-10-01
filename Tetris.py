import random
import tkinter as tk


COLUMNAS = 10
FILAS = 20
TAMANO_CELDA = 27

COLORES = {
	"I": "#39c6d8",
	"O": "#f2c14e",
	"T": "#bd8cff",
	"S": "#69d18b",
	"Z": "#f06c75",
	"J": "#5c91f2",
	"L": "#f39a55",
}

PIEZAS = {
	"I": [(0, 1), (1, 1), (2, 1), (3, 1)],
	"O": [(0, 0), (1, 0), (0, 1), (1, 1)],
	"T": [(1, 0), (0, 1), (1, 1), (2, 1)],
	"S": [(1, 0), (2, 0), (0, 1), (1, 1)],
	"Z": [(0, 0), (1, 0), (1, 1), (2, 1)],
	"J": [(0, 0), (0, 1), (1, 1), (2, 1)],
	"L": [(2, 0), (0, 1), (1, 1), (2, 1)],
}


def crear_rotaciones(coordenadas):
	rotaciones = []
	for _ in range(4):
		min_x = min(x for x, _ in coordenadas)
		min_y = min(y for _, y in coordenadas)
		rotaciones.append(sorted((x - min_x, y - min_y) for x, y in coordenadas))
		coordenadas = [(y, -x) for x, y in coordenadas]
	return rotaciones


ROTACIONES = {nombre: crear_rotaciones(celdas) for nombre, celdas in PIEZAS.items()}


class Tetris:
	def __init__(self):
		self.ventana = tk.Tk()
		self.ventana.title("Tetris")
		self.ventana.configure(bg="#10191e")
		self.ventana.resizable(False, False)
		self.ventana.bind("<Key>", self.al_presionar_tecla)

		self._crear_interfaz()
		self.reiniciar()
		self.ventana.after(self._intervalo_caida(), self._actualizar)

	def _crear_interfaz(self):
		encabezado = tk.Frame(self.ventana, bg="#10191e", padx=22, pady=16)
		encabezado.pack(fill="x")
		tk_titulo = tk.Label(
			encabezado,
			text="TETRIS",
			font=("Segoe UI", 22, "bold"),
			fg="#e9f1f3",
			bg="#10191e",
		)
		tk_titulo.pack(anchor="w")
		tk_subtitulo = tk.Label(
			encabezado,
			text="Ordena las piezas. Completa filas.",
			font=("Segoe UI", 10),
			fg="#91a5ad",
			bg="#10191e",
		)
		tk_subtitulo.pack(anchor="w", pady=(2, 0))

		contenido = tk.Frame(self.ventana, bg="#10191e", padx=22)
		contenido.pack(pady=(0, 22))
		ancho = COLUMNAS * TAMANO_CELDA
		alto = FILAS * TAMANO_CELDA
		self.tablero = tk.Canvas(
			contenido,
			width=ancho,
			height=alto,
			bg="#0a1115",
			bd=0,
			highlightthickness=1,
			highlightbackground="#30434b",
		)
		self.tablero.pack(side="left")

		lateral = tk.Frame(contenido, bg="#10191e", width=190)
		lateral.pack(side="left", fill="y", padx=(16, 0))
		lateral.pack_propagate(False)

		self.puntuacion_var = tk.StringVar()
		self.filas_var = tk.StringVar()
		self.nivel_var = tk.StringVar()
		self._crear_panel_puntuacion(lateral)
		self._crear_panel_siguiente(lateral)
		self._crear_panel_controles(lateral)

		self.boton_pausa = tk.Button(
			lateral,
			text="Pausar",
			command=self.alternar_pausa,
			font=("Segoe UI", 10, "bold"),
			fg="#10191e",
			bg="#39c6d8",
			activebackground="#70d9e5",
			activeforeground="#10191e",
			bd=0,
			cursor="hand2",
			pady=8,
		)
		self.boton_pausa.pack(fill="x", pady=(14, 7))
		self.boton_reiniciar = tk.Button(
			lateral,
			text="Reiniciar",
			command=self.reiniciar,
			font=("Segoe UI", 10, "bold"),
			fg="#e9f1f3",
			bg="#26363d",
			activebackground="#354a53",
			activeforeground="#ffffff",
			bd=0,
			cursor="hand2",
			pady=8,
		)
		self.boton_reiniciar.pack(fill="x")

	def _crear_panel_puntuacion(self, padre):
		panel = tk.Frame(padre, bg="#19262c", padx=12, pady=11)
		panel.pack(fill="x")
		for titulo, variable in (
			("PUNTOS", self.puntuacion_var),
			("FILAS", self.filas_var),
			("NIVEL", self.nivel_var),
		):
			tk.Label(
				panel,
				text=titulo,
				font=("Segoe UI", 8, "bold"),
				fg="#91a5ad",
				bg="#19262c",
			).pack(anchor="w")
			tk.Label(
				panel,
				textvariable=variable,
				font=("Segoe UI", 17, "bold"),
				fg="#f2f6f7",
				bg="#19262c",
			).pack(anchor="w", pady=(0, 7))

	def _crear_panel_siguiente(self, padre):
		panel = tk.Frame(padre, bg="#19262c", padx=12, pady=11)
		panel.pack(fill="x", pady=(12, 0))
		tk.Label(
			panel,
			text="SIGUIENTE",
			font=("Segoe UI", 8, "bold"),
			fg="#91a5ad",
			bg="#19262c",
		).pack(anchor="w", pady=(0, 8))
		self.vista_previa = tk.Canvas(
			panel,
			width=4 * TAMANO_CELDA,
			height=3 * TAMANO_CELDA,
			bg="#10191e",
			bd=0,
			highlightthickness=0,
		)
		self.vista_previa.pack(anchor="center")

	def _crear_panel_controles(self, padre):
		panel = tk.Frame(padre, bg="#10191e", padx=1, pady=12)
		panel.pack(fill="x")
		tk.Label(
			panel,
			text="CONTROLES",
			font=("Segoe UI", 8, "bold"),
			fg="#91a5ad",
			bg="#10191e",
		).pack(anchor="w", pady=(0, 7))
		for texto in (
			"← / →   Mover",
			"↓   Bajar",
			"↑ / X   Girar",
			"ESPACIO   Caída rápida",
			"P   Pausar",
			"R   Reiniciar",
		):
			tk.Label(
				panel,
				text=texto,
				font=("Segoe UI", 9),
				fg="#d0dcdf",
				bg="#10191e",
			).pack(anchor="w", pady=2)

	def reiniciar(self):
		self.matriz = [[None for _ in range(COLUMNAS)] for _ in range(FILAS)]
		self.puntuacion = 0
		self.filas_completadas = 0
		self.nivel = 1
		self.pausado = False
		self.fin_del_juego = False
		self.bolsa = []
		self.cola = []
		self._llenar_cola()
		self.pieza_actual = self._siguiente_pieza()
		self.boton_pausa.configure(text="Pausar")
		self._actualizar_indicadores()
		self._dibujar()

	def _llenar_cola(self):
		while len(self.cola) < 5:
			if not self.bolsa:
				self.bolsa = list(PIEZAS)
				random.shuffle(self.bolsa)
			self.cola.append(self.bolsa.pop())

	def _siguiente_pieza(self):
		pieza = {"tipo": self.cola.pop(0), "giro": 0, "x": 3, "y": 0}
		self._llenar_cola()
		return pieza

	def _choca(self, pieza):
		for x, y in ROTACIONES[pieza["tipo"]][pieza["giro"]]:
			columna = pieza["x"] + x
			fila = pieza["y"] + y
			if columna < 0 or columna >= COLUMNAS or fila >= FILAS or fila < 0:
				return True
			if self.matriz[fila][columna] is not None:
				return True
		return False

	def _mover(self, dx, dy, sumar_punto=False):
		candidata = {
			**self.pieza_actual,
			"x": self.pieza_actual["x"] + dx,
			"y": self.pieza_actual["y"] + dy,
		}
		if self._choca(candidata):
			return False
		self.pieza_actual = candidata
		if sumar_punto:
			self.puntuacion += 1
			self._actualizar_indicadores()
		self._dibujar()
		return True

	def _girar(self):
		giro = (self.pieza_actual["giro"] + 1) % 4
		for ajuste in (0, -1, 1, -2, 2):
			candidata = {
				**self.pieza_actual,
				"giro": giro,
				"x": self.pieza_actual["x"] + ajuste,
			}
			if not self._choca(candidata):
				self.pieza_actual = candidata
				self._dibujar()
				return

	def _caida_rapida(self):
		caidas = 0
		while self._mover(0, 1):
			caidas += 1
		self.puntuacion += caidas * 2
		self._fijar_pieza()

	def _fijar_pieza(self):
		for x, y in ROTACIONES[self.pieza_actual["tipo"]][self.pieza_actual["giro"]]:
			columna = self.pieza_actual["x"] + x
			fila = self.pieza_actual["y"] + y
			if fila < 0:
				self.fin_del_juego = True
				self._dibujar()
				return
			self.matriz[fila][columna] = self.pieza_actual["tipo"]

		filas_llenas = [fila for fila in self.matriz if all(celda is not None for celda in fila)]
		cantidad = len(filas_llenas)
		if cantidad:
			self.matriz = [[None] * COLUMNAS for _ in range(cantidad)] + [
				fila for fila in self.matriz if not all(celda is not None for celda in fila)
			]
			self.filas_completadas += cantidad
			self.puntuacion += (0, 100, 300, 500, 800)[cantidad] * self.nivel
			self.nivel = 1 + self.filas_completadas // 10

		self.pieza_actual = self._siguiente_pieza()
		if self._choca(self.pieza_actual):
			self.fin_del_juego = True
		self._actualizar_indicadores()
		self._dibujar()

	def _actualizar_indicadores(self):
		self.puntuacion_var.set(str(self.puntuacion))
		self.filas_var.set(str(self.filas_completadas))
		self.nivel_var.set(str(self.nivel))

	def _intervalo_caida(self):
		return max(90, 520 - (self.nivel - 1) * 35)

	def _actualizar(self):
		if not self.pausado and not self.fin_del_juego:
			if not self._mover(0, 1):
				self._fijar_pieza()
		self.ventana.after(self._intervalo_caida(), self._actualizar)

	def alternar_pausa(self):
		if self.fin_del_juego:
			return
		self.pausado = not self.pausado
		self.boton_pausa.configure(text="Continuar" if self.pausado else "Pausar")
		self._dibujar()

	def al_presionar_tecla(self, evento):
		tecla = evento.keysym.lower()
		if tecla == "r":
			self.reiniciar()
			return
		if tecla == "p":
			self.alternar_pausa()
			return
		if self.pausado or self.fin_del_juego:
			return
		if tecla == "left":
			self._mover(-1, 0)
		elif tecla == "right":
			self._mover(1, 0)
		elif tecla == "down":
			if not self._mover(0, 1, sumar_punto=True):
				self._fijar_pieza()
		elif tecla in ("up", "x"):
			self._girar()
		elif tecla == "space":
			self._caida_rapida()

	def _dibujar_celda(self, lienzo, x, y, color, tamano=TAMANO_CELDA):
		margen = 2
		lienzo.create_rectangle(
			x + margen,
			y + margen,
			x + tamano - margen,
			y + tamano - margen,
			fill=color,
			outline="#10191e",
			width=2,
		)

	def _dibujar(self):
		self.tablero.delete("all")
		for columna in range(COLUMNAS + 1):
			x = columna * TAMANO_CELDA
			self.tablero.create_line(x, 0, x, FILAS * TAMANO_CELDA, fill="#172329")
		for fila in range(FILAS + 1):
			y = fila * TAMANO_CELDA
			self.tablero.create_line(0, y, COLUMNAS * TAMANO_CELDA, y, fill="#172329")

		for fila, linea in enumerate(self.matriz):
			for columna, tipo in enumerate(linea):
				if tipo:
					self._dibujar_celda(
						self.tablero,
						columna * TAMANO_CELDA,
						fila * TAMANO_CELDA,
						COLORES[tipo],
					)

		if not self.fin_del_juego:
			for x, y in ROTACIONES[self.pieza_actual["tipo"]][self.pieza_actual["giro"]]:
				self._dibujar_celda(
					self.tablero,
					(self.pieza_actual["x"] + x) * TAMANO_CELDA,
					(self.pieza_actual["y"] + y) * TAMANO_CELDA,
					COLORES[self.pieza_actual["tipo"]],
				)

		self._dibujar_siguiente()
		if self.pausado or self.fin_del_juego:
			mensaje = "FIN DEL JUEGO" if self.fin_del_juego else "PAUSA"
			self.tablero.create_rectangle(
				20,
				FILAS * TAMANO_CELDA // 2 - 35,
				COLUMNAS * TAMANO_CELDA - 20,
				FILAS * TAMANO_CELDA // 2 + 35,
				fill="#10191e",
				outline="#39c6d8",
				width=2,
			)
			self.tablero.create_text(
				COLUMNAS * TAMANO_CELDA // 2,
				FILAS * TAMANO_CELDA // 2,
				text=mensaje,
				fill="#f2f6f7",
				font=("Segoe UI", 15, "bold"),
			)

	def _dibujar_siguiente(self):
		self.vista_previa.delete("all")
		tipo = self.cola[0]
		celdas = ROTACIONES[tipo][0]
		ancho = max(x for x, _ in celdas) + 1
		alto = max(y for _, y in celdas) + 1
		offset_x = (4 * TAMANO_CELDA - ancho * TAMANO_CELDA) // 2
		offset_y = (3 * TAMANO_CELDA - alto * TAMANO_CELDA) // 2
		for x, y in celdas:
			self._dibujar_celda(
				self.vista_previa,
				offset_x + x * TAMANO_CELDA,
				offset_y + y * TAMANO_CELDA,
				COLORES[tipo],
			)

	def ejecutar(self):
		self.ventana.mainloop()


if __name__ == "__main__":
	Tetris().ejecutar()
