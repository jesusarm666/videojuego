import pygame
from config import *

class Plataforma(pygame.sprite.Sprite):
    def __init__(self, x, y, ancho, alto, tipo="normal"):
        super().__init__()
        self.image = pygame.Surface((ancho, alto))
        self.image.fill(AZUL)  # Color temporal
        # Agregar borde para mejor visibilidad
        pygame.draw.rect(self.image, BLANCO, self.image.get_rect(), 2)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.tipo = tipo  # normal, atravesable, movil, temporal
        
        # Para plataformas móviles
        self.movil = tipo == "movil"
        self.velocidad = 2
        self.distancia_recorrida = 0
        self.direccion = 1  # 1 derecha, -1 izquierda
        self.distancia_maxima = 200  # Píxeles que se mueve
        
        # Para plataformas temporales
        self.temporal = tipo == "temporal"
        self.tiempo_visible = 180  # 3 segundos
        self.visible = True
        
    def actualizar(self):
        if self.movil:
            self.rect.x += self.velocidad * self.direccion
            self.distancia_recorrida += self.velocidad
            
            if self.distancia_recorrida >= self.distancia_maxima:
                self.direccion *= -1
                self.distancia_recorrida = 0
                
        elif self.temporal and self.visible:
            self.tiempo_visible -= 1
            if self.tiempo_visible <= 0:
                self.visible = False
                self.image.set_alpha(0)  # Hacer invisible 