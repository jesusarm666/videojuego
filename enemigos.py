import pygame
import math
from config import *

class Enemigo(pygame.sprite.Sprite):
    def __init__(self, x, y, tipo="normal"):
        super().__init__()
        # Crear un rectángulo temporal como sprite
        self.image = pygame.Surface((32, 32))
        self.image.fill(ROJO)  # Color temporal
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        # Propiedades básicas
        self.tipo = tipo
        self.vida = 100
        self.daño = 10
        self.velocidad = 2
        self.direccion = 1  # 1 derecha, -1 izquierda
        
        # Configuración según tipo
        if tipo == "volador":
            self.vida = 50
            self.daño = 5
            self.velocidad = 3
            self.altura_vuelo = 100
            self.posicion_inicial_y = y
        elif tipo == "tanque":
            self.vida = 200
            self.daño = 20
            self.velocidad = 1
        elif tipo == "saltador":
            self.vida = 75
            self.daño = 15
            self.velocidad = 2
            self.tiempo_salto = 0
            self.saltando = False
            self.velocidad_y = 0  # Agregar velocidad vertical inicial
    
    def actualizar(self, jugador, plataformas):
        if self.tipo == "normal":
            # Movimiento básico de lado a lado
            self.rect.x += self.velocidad * self.direccion
            
            # Cambiar dirección al tocar plataformas
            for plataforma in plataformas:
                if self.rect.colliderect(plataforma.rect):
                    if self.direccion > 0:
                        self.rect.right = plataforma.rect.left
                    else:
                        self.rect.left = plataforma.rect.right
                    self.direccion *= -1
                    break
            
        elif self.tipo == "volador":
            # Movimiento en patrón de vuelo
            self.rect.x += self.velocidad * self.direccion
            self.rect.y = self.posicion_inicial_y + math.sin(pygame.time.get_ticks() * 0.005) * self.altura_vuelo
            
            # Cambiar dirección al tocar plataformas
            for plataforma in plataformas:
                if self.rect.colliderect(plataforma.rect):
                    if self.direccion > 0:
                        self.rect.right = plataforma.rect.left
                    else:
                        self.rect.left = plataforma.rect.right
                    self.direccion *= -1
                    break
            
        elif self.tipo == "tanque":
            # Movimiento lento pero constante hacia el jugador
            if jugador.rect.x > self.rect.x:
                self.rect.x += self.velocidad
            else:
                self.rect.x -= self.velocidad
                
        elif self.tipo == "saltador":
            # Movimiento con saltos periódicos
            if not self.saltando:
                self.tiempo_salto += 1
                if self.tiempo_salto >= 60:  # Salta cada segundo
                    self.saltando = True
                    self.velocidad_y = -10
                    self.tiempo_salto = 0
            
            # Aplicar gravedad
            if self.saltando:
                self.velocidad_y += GRAVEDAD
                self.rect.y += self.velocidad_y
                
                # Verificar colisión con plataformas
                for plataforma in plataformas:
                    if self.rect.colliderect(plataforma.rect):
                        if self.velocidad_y > 0:
                            self.rect.bottom = plataforma.rect.top
                            self.velocidad_y = 0
                            self.saltando = False
                        elif self.velocidad_y < 0:
                            self.rect.top = plataforma.rect.bottom
                            self.velocidad_y = 0
            
            # Movimiento horizontal
            self.rect.x += self.velocidad * self.direccion
            
            # Cambiar dirección al tocar plataformas
            for plataforma in plataformas:
                if self.rect.colliderect(plataforma.rect):
                    if self.direccion > 0:
                        self.rect.right = plataforma.rect.left
                    else:
                        self.rect.left = plataforma.rect.right
                    self.direccion *= -1
                    break
    
    def recibir_daño(self, cantidad):
        self.vida -= cantidad
        return self.vida <= 0
    
    def atacar(self, jugador):
        if self.rect.colliderect(jugador.rect):
            return jugador.recibir_daño(self.daño)
        return False 