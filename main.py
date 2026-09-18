#!/usr/bin/python3

import sys
from asis.asistente import Asistente
from PyQt6.QtCore import Qt, QPoint, QSize
from PyQt6.QtWidgets import QApplication, QLabel
from PyQt6.QtGui import QCursor, QGuiApplication, QIcon
from asis.ventanaChat import ventanaChat, cargarFuente

class WidgetPrincipal(QLabel):
    # Constructor
    def __init__(self):
        super().__init__()
        
        # Configuracion de ventana
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)

        # Establecer icono
        self.setWindowIcon(QIcon("./perfiles/icon.png"))

        # Variable para drag
        self.drag_position = QPoint()
        
        # Asistente
        self.asis = Asistente(self)
        self.asis.mover(4) # Aqui va el parametro de velocidad

        # Ventana de chat
        self.chat = None
        
    # Funciones mouse click izquierdo y chat click derecho
    def mousePressEvent(self, event):
        # Inicio del arrastre si es izquierda
        if event.button() == Qt.MouseButton.LeftButton: 
            # Guardar posicion
            self.drag_position = event.globalPosition().toPoint() - self.pos()
            # Cambiar cursor
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
        # Abrir ventana de chat
        elif event.button() == Qt.MouseButton.RightButton:

            # Detener asistente (o intentarlo...)
            self.asis.parar()
            self.asis.asisIdle()

            # Establecer chat activo
            self.asis.chatActivo = True

            # Abrir chat
            if not self.chat:
                self.chat = ventanaChat(self.asis)
            self.chat.mostrarJuntoA(self)

    def mouseMoveEvent(self, event):
        # Arrastre mouse
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
    
    def mouseReleaseEvent(self, event):
        # Final del arrastre mouse
        if event.button() == Qt.MouseButton.LeftButton:
            self.setCursor(Qt.CursorShape.ArrowCursor)

if __name__ == "__main__":
    # Configuraciones iniciales
    app = QApplication(sys.argv)
    fuenteTitulo = cargarFuente()
    widget = WidgetPrincipal()
    widget.show()
    sys.exit(app.exec())
