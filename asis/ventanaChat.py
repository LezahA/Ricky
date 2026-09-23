#!/usr/bin/python3

import os
import sys
import json
import threading
from cerebro.cerebroChat import responder
from config.configLoader import cargarConfig, getConfig
from PyQt6.QtGui import QCursor, QGuiApplication, QFont, QFontDatabase, QColor, QBrush, QPixmap
from PyQt6.QtCore import Qt, QCoreApplication, QEvent, QObject, pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QTextEdit, QPushButton, QHBoxLayout, QListWidgetItem
# Probando para mientras ----------------------------------------------------------
import warnings
# Silencia las advertencias de limpieza de scikit-learn/loky al cerrar
warnings.filterwarnings("ignore", category=UserWarning, module=".*resource_tracker")
# ---------------------------------------------------------------------------------
# Cargar configuracion de chat
cargarConfig()
perfil = getConfig("perfil")

# Ruta del archivo del perfil
rutaPerfil = f"./perfiles/{perfil}.json"
if not os.path.exists(rutaPerfil):
    print(f"El perfil {perfil} no existe :(")
else:
    with open(rutaPerfil, 'r') as f:
        datos = json.load(f)
        titulo = datos["titulo"]
        fondo = datos["fondo"]
        fondoChat = datos["fondoChat"]
        input = datos["input"]
        boton = datos["boton"]
        botonHover = datos["botonHover"]
        respuestaFondo = datos["respuestaFondo"]
    print("Perfil encontrado :)")

# Funcion para cargar fuente
def cargarFuente():
    # Cargar fuente para titulo...
    print("buscando ruta de fuente...")

    # Comprobar si existe
    print("existe: ", os.path.exists("perfiles/marykate-1.ttf"))    
    rutaFuente = "perfiles/marykate-1.ttf"  

    # Procesar la fuente
    if not os.path.exists(rutaFuente):
        print(f"La ruta {rutaFuente} no existe :(")
    else:
        print("Fuente encontrada :)")

        print("rutaFuente:", rutaFuente)

        fuenteId = QFontDatabase.addApplicationFont(rutaFuente)
        #print("fuenteId:", fuenteId)

        if fuenteId != -1:
            familias = QFontDatabase.applicationFontFamilies(fuenteId)
            #print("familias:", familias)

            if familias:
                nombreFamilia = familias[0]
                #print("nombreFamilia:", nombreFamilia)

                fuente = QFont(nombreFamilia)  # crear fuente con nombre
                fuente.setPointSize(22)
                print("Fuente cargada :)")
            else:
                print("No se pudo obtener la familia de la fuente")
        else:
            print(f"Error al cargar la fuente {rutaFuente}")

    return fuente

# Crear comunicador entre hilo principal y cerebroChat
class Comunicador(QObject):
    # Definir signal tipo string
    respuestaLista = pyqtSignal(str)

class ventanaChat(QWidget):

    # Ventana de chat tipo diálogo - REUTILIZABLE EN EJECUCION
    def __init__(self, asistente=None):
        super().__init__()
        self.asistente = asistente
        self.setup_ui()
    
    def setup_ui(self):
        # Sobreponer chat
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)

        # Transparencia
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.setWindowTitle("Aun estoy pensando que nombre darle...")
        self.setFixedSize(400, 500)
        self.setStyleSheet(f"""
            ventanaChat {{
                border-radius: 15px;
            }}
        """)

        # Layout Principal
        layout = QVBoxLayout(self)

        # Layout botones
        layoutBotones = QHBoxLayout()
        layoutBotones.setSpacing(10)

        # label para botones
        botonCerrar = QPushButton()
        botonRegresar = QPushButton()

        # Tamaño de botones
        botonCerrar.setFixedSize(30, 30)
        botonRegresar.setFixedSize(30, 30)

        # Cosa de css para los botones
        botonCerrar.setStyleSheet(
            """
            QPushButton {
                background-image: url('./perfiles/botones/cerrar.png');
                background-color: transparent;
                border: none;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.2); /* Efecto visual al pasar el mouse */
                border-radius: 5px;
            }
        """
        )

        botonRegresar.setStyleSheet(
            """
            QPushButton {
                background-image: url('./perfiles/botones/regresar.png');
                background-color: transparent;
                border: none;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.2);
                border-radius: 5px;
            }
        """
        )

        # Agregar botones al layout
        layoutBotones.addWidget(botonCerrar)
        layoutBotones.addWidget(botonRegresar)
        # Stretch a la derecha
        layoutBotones.addStretch()
        # Conectar botones
        botonRegresar.clicked.connect(self.close)
        botonCerrar.clicked.connect(sys.exit)

        layout.addLayout(layoutBotones)

        # header encabezado
        header = QLabel("Habla con Ricky")
        header.setFont(cargarFuente())
        header.setStyleSheet(f"""
            color: {titulo};
            background-color: {fondo};
            padding: 7px;
            border: 2px solid {fondo};
            border-radius: 15px;
        """)
        layout.addWidget(header)
        
        self.chat_list = QListWidget()
        # Para salto de linea
        self.chat_list.setWordWrap(True)
        self.chat_list.setResizeMode(QListWidget.ResizeMode.Adjust)

        self.chat_list.setStyleSheet(f"""
            QListWidget {{
                background: {fondoChat};
                border: 1px solid {fondoChat};
                border-radius: 11px;
                padding: 10px;
                color: #000000;
            }}
        """)
        layout.addWidget(self.chat_list)
        
        # Layout input
        inputLayout = QHBoxLayout()
        # Barra input
        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("¿Cuál es tu pregunta?")
        self.input_text.setMaximumHeight(65)
        self.input_text.setStyleSheet(f"""
            QTextEdit {{
                border: 1px solid {input};
                background: {input};
                border-radius: 7px;
                padding: 8px;
                font-size: 14px;
                color: #000000;
            }}
        """)
        inputLayout.addWidget(self.input_text)

        # Boton enviar
        self.botonEnviar = QPushButton("Enviar")
        # Tamaño
        self.botonEnviar.setMaximumWidth(100)
        self.botonEnviar.setStyleSheet(f"""
            QPushButton {{
                background: {boton};
                color: #ffffff;
                border-radius: 15px;
                padding: 10px;
                font-weight: bold;
                height: 40px;
            }}
            QPushButton:hover {{
                background: {botonHover};
            }}
        """)

        # Agregar boton al layout
        inputLayout.addWidget(self.botonEnviar)

        # Conectar a funcion de enviarMensaje
        self.botonEnviar.clicked.connect(self.enviarMensaje)

        layout.addLayout(inputLayout)
        
        self.input_text.installEventFilter(self)
    
    def eventFilter(self, obj, event):
        # Capturar Enter para enviar con QEvent.Type.KeyPress
        if event.type() == QEvent.Type.KeyPress:
            if event.key() == Qt.Key.Key_Return:
                # Probar enviar mensaje con asistente pensando
                self.enviarMensaje(self.asistente)
                return True
        return False
    
    def enviarMensaje(self, asistente):
        # Establecer boton habilitado
        self.botonEnviar.setEnabled(False)

        mensaje = self.input_text.toPlainText().strip()
        if not mensaje:
            return
        # Agregar mensaje a la lista, limpiar input y habilitar boton de enviar
        self.chat_list.addItem(mensaje)
        self.input_text.clear()

        # asistente en modo pensar
        self.asistente.pensar()

        # Iniciar comunicación entre hilos
        self.comunicador = Comunicador()
        # Conectar con la funcion de mostrar respuesta
        self.comunicador.respuestaLista.connect(self.mostrarRespuesta)

        # Funcion para procesar respuesta
        def responderSegundoPlano():
            # Ejecuta el modelo sin congelar el resto de la interfaz...FUNCIONO
            respuestaRicky = responder(mensaje)

            # manda respuesta al hilo principal
            self.comunicador.respuestaLista.emit(respuestaRicky)
        
        # Ejecutar la tarea en un hilo secundario
        hiloResponder = threading.Thread(target=responderSegundoPlano, daemon=True)
        hiloResponder.start()

    def mostrarRespuesta(self, respuesta):
        # Fondo respuesta
        itemRespuesta = QListWidgetItem(respuesta)
        itemRespuesta.setBackground(QBrush(QColor(f"{respuestaFondo}")))

        self.botonEnviar.setEnabled(True)

        # Agregar respuesta
        self.chat_list.addItem(itemRespuesta)
        self.chat_list.scrollToBottom()

        # asistente en modo hablar
        self.asistente.hablar()
    
    def mostrarJuntoA(self, asistente):
        # si sobrepasa x de pantalla de la computadora
        # basicamente es el calculo de posicion actual + width de asistente + width de ventana + 10
        if asistente.x() + asistente.width() + self.width() + 10 > QGuiApplication.primaryScreen().availableGeometry().width():
            x = asistente.x() - self.width() - 15
        else:
            x = asistente.x() + asistente.width() + 10
        y = asistente.y()
        self.move(x, y)
        self.show()
        self.visible = True

    def closeEvent(self, event):
        # Cerrar chat y volver a mover
        self.visible = False  # Invisible = False
        self.asistente.chatActivo = False # Chat activo = False
        if self.asistente and hasattr(self.asistente, 'mover'):
            self.asistente.mover(4)  # reanudar movimiento
        
        event.accept()