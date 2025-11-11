import pygame
from config import *

class Jugador(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Crear un rectángulo temporal como sprite
        self.image = pygame.Surface((32, 64))
        self.image.fill(VERDE)  # Color temporal
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        # Física
        self.velocidad_x = 0
        self.velocidad_y = 0
        self.en_suelo = False
        self.saltos_restantes = 2  # Para doble salto
        
        # Estado
        self.vida = 100
        self.experiencia = 0
        self.monedas = 0
        self.invulnerable = False
        self.tiempo_invulnerable = 0
        
        # Habilidades
        self.ataque_cooldown = 0
        self.rage_activo = False
        self.madera_dura_activa = False
        
    def actualizar(self, plataformas):
        # Gravedad
        self.velocidad_y += GRAVEDAD
        if self.velocidad_y > VELOCIDAD_CAIDA_MAX:
            self.velocidad_y = VELOCIDAD_CAIDA_MAX
            
        # Movimiento horizontal con teclas
        teclas = pygame.key.get_pressed()
        self.velocidad_x = 0
        if teclas[pygame.K_a]:
            self.velocidad_x = -VELOCIDAD_JUGADOR
        if teclas[pygame.K_d]:
            self.velocidad_x = VELOCIDAD_JUGADOR
        
        # Actualizar posición
        self.rect.x += self.velocidad_x
        self.rect.y += self.velocidad_y
        
        # Colisiones con plataformas
        self.en_suelo = False
        for plataforma in plataformas:
            if self.rect.colliderect(plataforma.rect):
                # Colisión desde arriba
                if self.velocidad_y > 0:
                    self.rect.bottom = plataforma.rect.top
                    self.velocidad_y = 0
                    self.en_suelo = True
                    self.saltos_restantes = 2
                # Colisión desde abajo
                elif self.velocidad_y < 0:
                    self.rect.top = plataforma.rect.bottom
                    self.velocidad_y = 0
                # Colisión lateral
                elif self.velocidad_x > 0:
                    self.rect.right = plataforma.rect.left
                elif self.velocidad_x < 0:
                    self.rect.left = plataforma.rect.right
        
        # Actualizar cooldowns
        if self.ataque_cooldown > 0:
            self.ataque_cooldown -= 1
        if self.tiempo_invulnerable > 0:
            self.tiempo_invulnerable -= 1
            if self.tiempo_invulnerable == 0:
                self.invulnerable = False
    
    def saltar(self):
        if self.saltos_restantes > 0:
            self.velocidad_y = FUERZA_SALTO
            self.saltos_restantes -= 1
            self.en_suelo = False
    
    def atacar(self):
        if self.ataque_cooldown == 0:
            self.ataque_cooldown = 20  # 20 frames de cooldown
            return True
        return False
    
    def activar_rage(self):
        if self.experiencia >= 50 and not self.rage_activo:
            self.rage_activo = True
            self.experiencia -= 50
            return True
        return False
    
    def activar_madera_dura(self):
        if self.experiencia >= 100 and not self.madera_dura_activa:
            self.madera_dura_activa = True
            self.invulnerable = True
            self.tiempo_invulnerable = 180  # 3 segundos
            self.experiencia -= 100
            return True
        return False
    
    def recibir_daño(self, cantidad):
        if not self.invulnerable and not self.madera_dura_activa:
            self.vida -= cantidad
            self.invulnerable = True
            self.tiempo_invulnerable = 60  # 1 segundo de invulnerabilidad
            return True
        return False
    
    def recolectar_moneda(self):
        self.monedas += 1
    
    def recolectar_experiencia(self, cantidad):
        self.experiencia += cantidad 