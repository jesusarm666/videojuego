import pygame
from config import *

class Plataforma(pygame.sprite.Sprite):
    def __init__(self, x, y, ancho, alto, tipo="normal"):
        super().__init__()

        # ------------------------------
        # ESTILO VISUAL GEOMETRY DASH
        # ------------------------------
        self.image = pygame.Surface((ancho, alto), pygame.SRCALPHA)

        # Color sólido estilo "Geometry Dash"
        color_plat = (30, 144, 255) if tipo != "movil" else (255, 140, 0)

        # Relleno sólido
        self.image.fill(color_plat)

        # Borde blanco grueso
        pygame.draw.rect(self.image, BLANCO, self.image.get_rect(), 4)

        # Rectángulo de colisión
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.tipo = tipo  # normal, atravesable, movil, temporal

        # ------------------------------------
        # PLATAFORMA MÓVIL
        # ------------------------------------
        self.movil = tipo == "movil"
        self.velocidad = 2
        self.distancia_recorrida = 0
        self.direccion = 1  # 1 derecha, -1 izquierda
        self.distancia_maxima = 200  # Píxeles que se mueve

        # ------------------------------------
        # PLATAFORMA TEMPORAL
        # ------------------------------------
        self.temporal = tipo == "temporal"
        self.tiempo_visible = 180  # 3 segundos
        self.visible = True

        # Última variación en x (usada por main para arrastrar entidades encima)
        self.last_dx = 0

    # =======================================================
    # ACTUALIZACIÓN DE LA PLATAFORMA
    # =======================================================
    def actualizar(self):
        # Resetear last_dx en cada frame
        self.last_dx = 0

        # -------------------------
        # MOVIMIENTO DE PLATAFORMA
        # -------------------------
        if self.movil:
            dx = self.velocidad * self.direccion

            self.rect.x += dx
            self.last_dx = dx

            # Sumar la distancia recorrida
            self.distancia_recorrida += abs(dx)

            # Cambiar dirección al llegar al límite
            if self.distancia_recorrida >= self.distancia_maxima:
                self.direccion *= -1
                self.distancia_recorrida = 0

            # No permitir que salga del mundo
            if self.rect.left < 0:
                self.rect.left = 0
                self.direccion = 1

            if self.rect.right > ANCHO_NIVEL:
                self.rect.right = ANCHO_NIVEL
                self.direccion = -1

        # -------------------------
        # PLATAFORMA TEMPORAL
        # -------------------------
        elif self.temporal and self.visible:
            self.tiempo_visible -= 1
            if self.tiempo_visible <= 0:
                self.visible = False
                self.image.set_alpha(0)  # Hacer invisible

    # =======================================================
    # ¿UNA ENTIDAD ESTÁ ENCIMA DE LA PLATAFORMA?
    # =======================================================
    def entidad_encima(self, entidad):
        feet_y = entidad.rect.bottom

        # Pequeño margen para evitar fallos de píxeles
        if abs(feet_y - self.rect.top) <= 4:
            # Solapamiento horizontal
            if entidad.rect.right > self.rect.left and entidad.rect.left < self.rect.right:
                return True

        return False
