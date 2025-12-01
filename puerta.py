# puerta.py
import pygame
import time
from config import *

class Puerta(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        ancho = 48
        alto = 80
        self.surface = pygame.Surface((ancho, alto), pygame.SRCALPHA)
        self.color_cerrada = (80, 80, 140)
        self.color_abierta = (60, 200, 80)
        self.surface.fill(self.color_cerrada)
        pygame.draw.rect(self.surface, BLANCO, self.surface.get_rect(), 3)
        self.image = self.surface.copy()
        self.rect = self.image.get_rect(topleft=(x, y))

        self.abierta = False
        self._transicion_activa = False
        self._transicion_inicio = 0.0
        self._transicion_duracion = 0.6

    def abrir(self):
        if not self.abierta:
            self.abierta = True
            self.surface.fill(self.color_abierta)
            pygame.draw.rect(self.surface, BLANCO, self.surface.get_rect(), 3)
            self.image = self.surface.copy()

    def iniciar_transicion(self):
        if not self._transicion_activa:
            self._transicion_activa = True
            self._transicion_inicio = time.time()
            self.surface.fill(self.color_abierta)
            pygame.draw.rect(self.surface, BLANCO, self.surface.get_rect(), 3)
            self.image = self.surface.copy()

    def actualizar_animacion(self):
        if not self._transicion_activa:
            return False
        tiempo = time.time() - self._transicion_inicio
        # efecto pulse
        factor = 1.0 + 0.08 * (1.0 - abs((tiempo / self._transicion_duracion) * 2 - 1))
        tamaño = (int(self.surface.get_width() * factor), int(self.surface.get_height() * factor))
        img = pygame.transform.smoothscale(self.surface, tamaño)
        x = self.rect.centerx - img.get_width() // 2
        y = self.rect.centery - img.get_height() // 2
        self.image_anim = (img, (x, y))
        if tiempo >= self._transicion_duracion:
            self._transicion_activa = False
            self.image = self.surface.copy()
            self.image_anim = None
            return False
        return True

    def dibujar_anim(self, pantalla, cam_x):
        if getattr(self, "image_anim", None):
            img, pos = self.image_anim
            pantalla.blit(img, (pos[0] - cam_x, pos[1]))
            return True
        pantalla.blit(self.image, (self.rect.x - cam_x, self.rect.y))
        return False

    def colisiona_con(self, jugador):
        """
        Nuevo comportamiento de colisión:
        - Si el rect del jugador colisiona con la puerta, y
        - La base del jugador (pies) está en contacto razonable con la parte superior de la puerta,
          o el jugador está caminando sobre la plataforma donde está la puerta,
        entonces retornar True (activar salida).
        Esto es más tolerante y permite tocar la puerta sin requerir un salto hacia abajo exacto.
        """
        if not self.rect.colliderect(jugador.rect):
            return False

        pies_diff = jugador.rect.bottom - self.rect.top
        # si los pies del jugador están muy cerca o por encima (pequeño margen), considerar toque estable
        if pies_diff >= -8 and pies_diff <= 16:
            # permitir activar tanto si en_suelo True como si el jugador está sobre la plataforma
            if getattr(jugador, "velocidad_y", 0) >= -1:  # si no está subiendo bruscamente
                return True

        # Además, si el jugador empuja desde un lateral y su centro y base coinciden con la puerta, permitir activación
        centro_x = jugador.rect.centerx
        if self.rect.left <= centro_x <= self.rect.right:
            if jugador.rect.bottom > self.rect.top - 6:
                return True

        return False
