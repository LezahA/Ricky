#!/usr/bin/python3

import os
import sys
import random
from asis.ventanaChat import ventanaChat
from PyQt6.QtWidgets import QApplication, QLabel
from PyQt6.QtCore import Qt, QTimer, QPoint, QSize
from PyQt6.QtGui import QGuiApplication, QPixmap, QCursor
from config.configLoader import cargarConfig, getConfig

# Cargar configuracion de personaje
cargarConfig()
character = getConfig("character")
class Asistente:
    def __init__(self, label):
        self.label = label

        # Chat activo (Falso por defecto)
        self.chatActivo = False

        # Imágenes de la animación ACTUAL
        self.imagenes = []
        self.indice = 0
        self.timer = None
        self.timerMovimiento = None  # timer movimiento

        # Inicializar colisiones
        self.colisionIzquierda = False
        self.colisionDerecha = False
        self.colisionArriba = False
        self.colisionAbajo = False

        # Dirección aleatoria
        self.direccionAncho = random.randint(1, 2)
        self.direccionAltura = random.randint(1, 2)

        # Velocidad de animacion
        self.vAnimacion = 245

    def siguienteImagen(self):
        self.indice = (self.indice + 1) % len(self.imagenes)
        self.label.setPixmap(self.imagenes[self.indice])

    # Funcion a parte para procesar las imagenes y solo invocarla en el resto de funciones
    def cargarAnimacion(self, ruta_completa):
        # LIMPIAR imágenes anteriores
        self.imagenes.clear()

        # Directorio de sprites
        sprites = os.listdir(ruta_completa)
        print(f"Cargando animación: {ruta_completa}")
        # Procesamiento de sprites segun la cantidad existente en el directorio
        for i in range(1, len(sprites)+1):
            ruta = f"{ruta_completa}{i}.png"  
            #print(ruta) descomentar solo para comprobar la carga individual de los sprites
            if os.path.exists(ruta):
                pixmap = QPixmap(ruta)
                if not pixmap.isNull():
                    self.imagenes.append(pixmap)
        
        if not self.imagenes:
            print(f" :/ No hay imágenes en {ruta_completa}")
            return False
        
        self.indice = 0
        # Cargar tamaño de asistente acorde al primer sprite de la primera animacion que ejecuta
        self.label.setPixmap(self.imagenes[0])
        return True

    def asisIdle(self):
        ruta = f"./personajes/{character}/idle/"
        if self.cargarAnimacion(ruta):
            self.iniciarAnimacion(self.vAnimacion) # Velocidad para caminar

    def walkR(self):
        ruta = f"./personajes/{character}/walkR/"
        if self.cargarAnimacion(ruta):
            self.iniciarAnimacion(self.vAnimacion)  # Velocidad para caminar

    def walkL(self):
        ruta = f"./personajes/{character}/walkL/"
        if self.cargarAnimacion(ruta):
            self.iniciarAnimacion(self.vAnimacion)  # Velocidad para caminar

    def pensar(self):
        ruta = f"./personajes/{character}/pensar/"
        if self.cargarAnimacion(ruta):
            self.iniciarAnimacion(self.vAnimacion) # Velocidad para caminar

    def hablar(self):
        ruta = f",/personajes/{character}/hablar/"
        if self.cargarAnimacion(ruta):
            self.iniciarAnimacion(self.vAnimacion) # Velocidad para caminar

    def jump(self):
        ruta = f"./personajes/{character}/jump/"
        if self.cargarAnimacion(ruta):
            self.iniciarAnimacion(self.vAnimacion) # Velocidad para caminar

    def iniciarAnimacion(self, intervalo):
        # Iniciar timer de animación
        if self.timer:
            self.timer.stop()
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.siguienteImagen)
        self.timer.start(intervalo)

    def mover(self, velocidad):
        # Parar movimiento anterior
        if self.timerMovimiento:
            self.timerMovimiento.stop()

        # Verificar si hay un chat abierto (detenerlo por si acaso)
        if self.chatActivo:
            self.parar()
            return 

        # Movimiento aleatorio
        self.modoMovimiento = random.choice(['diagonal', 'rectoH', 'rectoV'])
        self.pasosRestantes = random.randint(30, 35)

        # Verificar Colision Derecha
        if self.colisionDerecha == True:
            self.direccionAncho = 2
            self.colisionDerecha = False
        # Verificar Colision Izquierda
        elif self.colisionIzquierda == True:
            self.direccionAncho = 1
            self.colisionIzquierda = False
        else:
            self.direccionAncho = random.randint(1, 2)

        # Verificar Colision Arriba
        if self.colisionArriba == True:
            self.direccionAltura = 2
            self.colisionArriba = False
        # Verificar Colision Abajo
        elif self.colisionAbajo == True:
            self.direccionAltura = 1
            self.colisionAbajo = False
        else:
            self.direccionAltura = random.randint(1, 2)

        # Walk según dirección
        if self.direccionAncho == 1:
            self.walkR()
        else:
            self.walkL()

        def paso():
            # Obtener tamaño de pantalla
            pantalla = QGuiApplication.primaryScreen()

            # Para esperar
            espera=random.randint(1, 2)
            if self.pasosRestantes <= 0: 
                # Intento de bailar (idle) entre cambio de modos de movimiento
                self.timerMovimiento.stop()
                self.asisIdle()
                # Comprobar si hay chat activo
                if self.chatActivo == True:
                    self.parar()
                    return
                else:
                    # Continuar movimiento
                    QTimer.singleShot(4000, lambda: self.mover(velocidad))
                    self.modoMovimiento = random.choice(['diagonal', 'rectoH', 'rectoV'])
                    self.pasosRestantes = random.randint(30, 35)
                        
            self.pasosRestantes -= 1
            
            # Offsets según modo
            match self.modoMovimiento:
                case 'rectoH':
                    if self.direccionAncho == 1:
                        offset_x = velocidad
                    else:
                        offset_x = -velocidad
                    offset_y = 0

                case 'rectoV':
                    offset_x = 0
                    if self.direccionAltura == 1:
                        offset_y = -velocidad
                    else:
                        offset_y = velocidad

                case 'diagonal':  # Movimiento diagonal o por defecto

                    if self.direccionAncho == 1 and self.direccionAltura == 1:
                        offset_x = velocidad
                        offset_y = -velocidad

                    if self.direccionAncho == 1 and self.direccionAltura == 2:
                        offset_x = velocidad
                        offset_y = velocidad

                    if self.direccionAncho == 2 and self.direccionAltura == 1:
                        offset_x = -velocidad
                        offset_y = -velocidad

                    if self.direccionAncho == 2 and self.direccionAltura == 2:
                        offset_x = -velocidad
                        offset_y = velocidad
            
            nuevaX = self.label.x() + offset_x
            nuevaY = self.label.y() + offset_y

            # Colisiones
            if (nuevaX + self.label.width() > pantalla.size().width()):

                # Cambiar variable de colision
                self.colisionDerecha = True

                print("Colisión")
                
                # alejar del borde (5-10px)
                separacion = random.randint(5, 10)
                self.label.move(pantalla.size().width() - self.label.width() - separacion, self.label.y())

                # Parar movimiento
                self.timerMovimiento.stop()

                # jump o idle (animación SIGUE corriendo en teoria)
                if espera == 1:
                    #self.jump() por el momento mientras no hay animación
                    self.asisIdle()
                    print("Jump 4s ")

                else:
                    self.asisIdle()
                    print("Idle 4s ")

                # INVERSO direcciones
                self.direccionAncho = 2 # Izquierda

                # PAUSAR 4s y girar al opuesto
                QTimer.singleShot(4000, lambda: self.mover(velocidad))
                return

            if (nuevaX < 0):

                # Cambiar variable de colision
                self.colisionIzquierda = True

                print("Colisión")
                
                # Parar movimiento
                self.timerMovimiento.stop()

                # jump o idle (animación SIGUE corriendo en teoria)
                if espera == 1:
                    # self.jump() para mientras no hay animación
                    self.asisIdle()

                else:
                    self.asisIdle()

                # INVERSO direcciones
                self.direccionAncho = 1 # Derecha

                # pausar 4s y girar al opuesto
                QTimer.singleShot(4000, lambda: self.mover(velocidad))
                return

            if (nuevaY + self.label.height() > pantalla.size().height()):

                # Cambiar variable de colision
                self.colisionAbajo = True

                print("Colisión")
                
                # Parar movimiento
                self.timerMovimiento.stop()

                # jump o idle (animación SIGUE corriendo en teoria)
                if espera == 1:
                    # self.jump() para mientras no hay animación
                    self.asisIdle()

                else:
                    self.asisIdle()

                # INVERSO direcciones
                self.direccionAltura = 1 # Arriba

                # pausar 4s y girar al opuesto
                QTimer.singleShot(4000, lambda: self.mover(velocidad))
                return

            if (nuevaY < 0):

                # Cambiar variable de colision
                self.colisionArriba = True

                print("Colisión")
                
                # Parar movimiento
                self.timerMovimiento.stop()

                # jump o idle (animación sigue corriendo en teoria)
                if espera == 1:
                    # self.jump()
                    self.asisIdle()
                else:
                    self.asisIdle()

                # INVERSO direcciones
                self.direccionAltura = 2 # Abajo

                # pausar 4s y girar al opuesto
                QTimer.singleShot(4000, lambda: self.mover(velocidad))
                return

            self.label.move(nuevaX, nuevaY)
       
        self.timerMovimiento = QTimer()
        self.timerMovimiento.timeout.connect(paso)
        self.timerMovimiento.start(100)

    # Funcion para detener asistente
    def parar(self):
        if self.timerMovimiento:
            self.timerMovimiento.stop()
            self.timerMovimiento = None
            