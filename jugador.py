# jugador.py
import pygame
from config import *

class Jugador(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        # Visual estilo Geometry Dash
        self.image = pygame.Surface((32, 64), pygame.SRCALPHA)
        self.image.fill(VERDE)
        pygame.draw.rect(self.image, BLANCO, (0, 0, 32, 64), 4)

        self.rect = self.image.get_rect(topleft=(x, y))

        # Física
        self.velocidad_x = 0
        self.velocidad_y = 0
        self.en_suelo = False
        self.saltos_restantes = 2

        # Estado
        self.vida = 100
        self.experiencia = 0
        self.monedas = 0

        # Invulnerabilidad
        self.invulnerable = 0

        # Habilidades / cooldowns
        self.ataque_cooldown = 0
        self.rage_activo = False
        self.madera_dura_activa = False

    def actualizar(self, plataformas):
        # Gravedad
        self.velocidad_y += GRAVEDAD
        if self.velocidad_y > VELOCIDAD_CAIDA_MAX:
            self.velocidad_y = VELOCIDAD_CAIDA_MAX

        # Movimiento horizontal (A/D sigue igual)
        teclas = pygame.key.get_pressed()
        self.velocidad_x = 0
        if teclas[pygame.K_a]:
            self.velocidad_x = -VELOCIDAD_JUGADOR
        if teclas[pygame.K_d]:
            self.velocidad_x = VELOCIDAD_JUGADOR

        # Aplicar movimiento
        self.rect.x += self.velocidad_x
        self.rect.y += self.velocidad_y

        # Tope superior del mundo
        if self.rect.top < 0:
            self.rect.top = 0
            self.velocidad_y = 0

        # Colisiones con plataformas (MISMA LÓGICA)
        self.en_suelo = False
        for plataforma in plataformas:
            if self.rect.colliderect(plataforma.rect):

                # Desde arriba (caer sobre plataforma)
                if self.velocidad_y > 0 and self.rect.bottom - plataforma.rect.top < 30:
                    self.rect.bottom = plataforma.rect.top
                    self.velocidad_y = 0
                    self.en_suelo = True
                    self.saltos_restantes = 2

                # Desde abajo
                elif self.velocidad_y < 0:
                    self.rect.top = plataforma.rect.bottom
                    self.velocidad_y = 0

                # Laterales
                elif self.velocidad_x > 0:
                    self.rect.right = plataforma.rect.left
                elif self.velocidad_x < 0:
                    self.rect.left = plataforma.rect.right

        # Cooldowns
        if self.invulnerable > 0:
            self.invulnerable -= 1
        if self.ataque_cooldown > 0:
            self.ataque_cooldown -= 1

    def saltar(self):
        # Doble salto permitido (misma lógica)
        if self.saltos_restantes > 0:
            self.velocidad_y = FUERZA_SALTO
            self.saltos_restantes -= 1
            self.en_suelo = False

    def recibir_daño(self, cantidad):
        if self.invulnerable == 0:
            self.vida -= cantidad
            self.invulnerable = FPS
            if self.vida <= 0:
                self.vida = 0
                return "muerto"
            return "daño"
        return False

    def recoger_moneda(self):
        self.monedas += 1
        self.experiencia += 5

    def atacar(self, lista_enemigos):
        """
        Ataque básico: área frontal. Devuelve la lista de enemigos alcanzados.
        Tecla de ataque: J
        No modifica la lista por sí mismo (main.py debe eliminar los enemigos retornados).
        """
        if self.ataque_cooldown > 0:
            return []

        # establecer cooldown
        self.ataque_cooldown = FPS // 2

        # área de ataque frontal relativa al jugador
        ancho_rango = 80
        alto_rango = self.rect.height + 20
        rango = pygame.Rect(self.rect.centerx - ancho_rango//2, self.rect.top - 10, ancho_rango, alto_rango)

        alcanzados = [e for e in lista_enemigos if rango.colliderect(e.rect)]

        return alcanzados
