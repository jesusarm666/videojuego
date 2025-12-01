# moneda.py
import pygame
from config import *

class Moneda(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        tamaño = 24
        self.image = pygame.Surface((tamaño, tamaño), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 215, 0), (tamaño//2, tamaño//2), tamaño//2)
        pygame.draw.circle(self.image, BLANCO, (tamaño//2, tamaño//2), tamaño//2, 2)
        self.rect = self.image.get_rect(center=(x, y))

    def recoger(self, jugador):
        jugador.recoger_moneda()
        # no hacemos self.kill() por si manejas colecciones manualmente
