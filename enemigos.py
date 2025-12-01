# enemigos.py
import pygame
import math
from config import *

class Enemigo(pygame.sprite.Sprite):
    def __init__(self, x, y, tipo="normal", agresividad=1.0):
        super().__init__()

        # Visual geométrico (no cambia la lógica)
        tamaño = 32
        self.image = pygame.Surface((tamaño, tamaño), pygame.SRCALPHA)
        color = ROJO
        if tipo == "volador":
            color = (200, 80, 200)
        elif tipo == "tanque":
            color = (200, 150, 50)
        elif tipo == "saltador":
            color = (80, 200, 80)
        pygame.draw.rect(self.image, color, (0, 0, tamaño, tamaño), border_radius=6)
        pygame.draw.rect(self.image, BLANCO, (0, 0, tamaño, tamaño), 3, border_radius=6)

        self.rect = self.image.get_rect(topleft=(x, y))
        self.x_inicial = self.rect.x

        # Tipo y física
        self.tipo = tipo
        self.direccion = 1
        self.base_velocidad = 2
        self.velocidad = 2
        self.velocidad_y = 0
        self.en_suelo = False
        self.daño = 10

        # Agresividad (>=1.0). No rompe la lógica previa.
        self.agresividad = max(1.0, float(agresividad))
        self.alerta = False

        # Configuración por tipo (base)
        if tipo == "normal":
            self.base_velocidad = 2
            self.velocidad = self.base_velocidad

        elif tipo == "volador":
            self.base_velocidad = 3
            self.velocidad = self.base_velocidad
            self.altura = 60
            self.y_inicial = y
            self.patrol_min_x = max(0, self.x_inicial - 220)
            self.patrol_max_x = min(ANCHO_NIVEL, self.x_inicial + 220)

        elif tipo == "tanque":
            self.base_velocidad = 1
            self.velocidad = self.base_velocidad

        elif tipo == "saltador":
            self.base_velocidad = 2
            self.velocidad = self.base_velocidad
            self.tiempo_salto = 0
            self.saltando = False
            self.vel_salto = -12
            self.salto_interval = 60  # frames entre saltos (se reduce si está alerta)

    def hay_plataforma_debajo(self, plataformas, desplaz_x=0):
        foot_x = self.rect.midbottom[0] + desplaz_x
        foot_y = self.rect.bottom + 4
        for p in plataformas:
            if p.rect.collidepoint(foot_x, foot_y):
                return True
        return False

    def _actualizar_alerta(self, jugador):
        distancia = abs(jugador.rect.centerx - self.rect.centerx)
        rango_agg = DISTANCIA_DETECCION * self.agresividad
        self.alerta = distancia <= rango_agg

    def actualizar(self, jugador, plataformas):
        # Actualiza alerta y ajusta comportamiento temporalmente (sin cambiar base_velocidad)
        self._actualizar_alerta(jugador)
        velocidad_actual = self.base_velocidad
        if self.alerta:
            velocidad_actual = min(self.base_velocidad * (1.0 + 0.35 * (self.agresividad - 1.0)), self.base_velocidad * 2.0)

        if self.tipo == "normal":
            self.mov_normal(plataformas, velocidad_actual)
        elif self.tipo == "volador":
            self.mov_volador(plataformas, velocidad_actual)
        elif self.tipo == "tanque":
            self.mov_tanque(jugador, plataformas, velocidad_actual)
        elif self.tipo == "saltador":
            if self.alerta:
                interval = max(18, int(self.salto_interval / (1.0 + 0.5 * (self.agresividad - 1.0))))
            else:
                interval = self.salto_interval
            self.mov_saltador(plataformas, velocidad_actual, interval)

        # límites del nivel
        if self.rect.left < 0:
            self.rect.left = 0
            self.direccion = 1
        if self.rect.right > ANCHO_NIVEL:
            self.rect.right = ANCHO_NIVEL
            self.direccion = -1
        if self.rect.top < 0:
            self.rect.top = 0

        if self.tipo != "volador" and self.rect.bottom > ALTO_PANTALLA:
            self.rect.bottom = ALTO_PANTALLA
            self.velocidad_y = 0
            self.saltando = False

    def mov_normal(self, plataformas, velocidad_actual):
        desplaz = int(velocidad_actual) * self.direccion
        if not self.hay_plataforma_debajo(plataformas, desplaz_x=desplaz):
            self.direccion *= -1
            return
        self.rect.x += desplaz
        for p in plataformas:
            if self.rect.colliderect(p.rect):
                if self.direccion > 0:
                    self.rect.right = p.rect.left
                else:
                    self.rect.left = p.rect.right
                self.direccion *= -1
                break

    def mov_volador(self, plataformas, velocidad_actual):
        self.rect.x += int(velocidad_actual) * self.direccion
        if getattr(self, "patrol_min_x", None) is not None and self.rect.x < self.patrol_min_x:
            self.rect.x = self.patrol_min_x
            self.direccion = 1
        if getattr(self, "patrol_max_x", None) is not None and self.rect.x > self.patrol_max_x:
            self.rect.x = self.patrol_max_x
            self.direccion = -1
        self.rect.y = self.y_inicial + math.sin(pygame.time.get_ticks() * 0.004) * getattr(self, "altura", 60)
        for p in plataformas:
            if self.rect.colliderect(p.rect):
                self.direccion *= -1
                break

    def mov_tanque(self, jugador, plataformas, velocidad_actual):
        if jugador.rect.centerx > self.rect.centerx:
            desplaz = int(velocidad_actual)
        else:
            desplaz = -int(velocidad_actual)
        if not self.hay_plataforma_debajo(plataformas, desplaz_x=desplaz):
            self.direccion *= -1
            return
        self.rect.x += desplaz
        for p in plataformas:
            if self.rect.colliderect(p.rect):
                self.rect.bottom = p.rect.top
                break

    def mov_saltador(self, plataformas, velocidad_actual, salto_interval):
        desplaz = int(velocidad_actual) * self.direccion
        if not getattr(self, "saltando", False):
            self.tiempo_salto += 1
            if self.tiempo_salto >= salto_interval:
                if self.hay_plataforma_debajo(plataformas, desplaz_x=0):
                    self.velocidad_y = self.vel_salto
                    self.saltando = True
                self.tiempo_salto = 0

        if getattr(self, "saltando", False):
            self.velocidad_y += GRAVEDAD
            self.rect.y += self.velocidad_y
            for p in plataformas:
                if self.rect.colliderect(p.rect):
                    if self.velocidad_y > 0 and self.rect.bottom - p.rect.top < 30:
                        self.rect.bottom = p.rect.top
                        self.velocidad_y = 0
                        self.saltando = False
                    elif self.velocidad_y < 0:
                        self.rect.top = p.rect.bottom
                        self.velocidad_y = 0

        if not self.hay_plataforma_debajo(plataformas, desplaz_x=desplaz):
            self.direccion *= -1
            return
        self.rect.x += desplaz

    def atacar(self, jugador):
        if self.rect.colliderect(jugador.rect):
            return jugador.recibir_daño(self.daño)
        return False
