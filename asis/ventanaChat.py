#!/usr/bin/python3

import os
import sys
import json
import asyncio
from cerebro.cerebroChat import responder
from PyQt6.QtCore import Qt, QCoreApplication, QEvent
from config.configLoader import cargarConfig, getConfig
from PyQt6.QtGui import QCursor, QGuiApplication, QFont, QFontDatabase
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QTextEdit, QPushButton, QHBoxLayout

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

class ventanaChat(QWidget):

    # Ventana de chat tipo diálogo - REUTILIZABLE EN EJECUCION
    def __init__(self, asistente=None):
        super().__init__()
        self.asistente = asistente
        self.setup_ui()
    
    def setup_ui(self):
        self.setWindowTitle("Aun estoy pensando que nombre darle...")
        self.setFixedSize(400, 500)
        self.setStyleSheet(f"""
            ventanaChat {{
                background-color: {fondo};
                border: 2px solid {fondo};
                border-radius: 15px;
            }}
        """)
        
        layout = QVBoxLayout(self)
        
        header = QLabel("Habla con Ricky")
        header.setFont(cargarFuente())
        header.setStyleSheet(f"""
            color: {titulo};
            padding: 7px;
        """)
        layout.addWidget(header)
        
        self.chat_list = QListWidget()
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
        
        input_layout = QHBoxLayout()
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
        input_layout.addWidget(self.input_text)
        
        self.boton_send = QPushButton("Enviar")
        self.boton_send.setMaximumWidth(100)
        self.boton_send.setStyleSheet(f"""
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
        self.boton_send.clicked.connect(self.enviarMensaje)
        input_layout.addWidget(self.boton_send)
        
        layout.addLayout(input_layout)
        
        self.input_text.installEventFilter(self)
    
    def eventFilter(self, obj, event):
        # Capturar Enter para enviar con QEvent.Type.KeyPress
        if event.type() == QEvent.Type.KeyPress:
            if event.key() == Qt.Key.Key_Return:
                self.enviarMensaje()
                return True
        return False
    
    def enviarMensaje(self):
        mensaje = self.input_text.toPlainText().strip()
        if not mensaje:
            return
        # Agregar mensaje a la lista, limpiar input y habilitar boton de enviar
        self.chat_list.addItem(f"usuario: {mensaje}")
        self.input_text.clear()
        self.boton_send.setEnabled(True)
        # Mostrar respuesta
        self.mostrarRespuesta(asyncio.run(responder(mensaje)))
    
    def mostrarRespuesta(self, respuesta):
        self.chat_list.addItem(f"asistente: {respuesta}")
        self.boton_send.setEnabled(False)
        self.chat_list.scrollToBottom()
    
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