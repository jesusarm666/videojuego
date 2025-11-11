import pygame
import sys
from config import *
from jugador import Jugador
from plataformas import Plataforma
from enemigos import Enemigo

class Juego:
    def __init__(self):
        pygame.init()
        self.pantalla = pygame.display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA))
        pygame.display.set_caption("Wood Will Rise")
        self.reloj = pygame.time.Clock()
        self.estado_actual = ESTADO_MENU
        self.ejecutando = True
        
        # Grupos de sprites
        self.todos_sprites = pygame.sprite.Group()
        self.plataformas = pygame.sprite.Group()
        self.enemigos = pygame.sprite.Group()
        
        # Crear jugador
        self.jugador = Jugador(100, ALTO_PANTALLA - 200)
        self.todos_sprites.add(self.jugador)
        
        # Crear plataformas y enemigos de prueba
        self.crear_plataformas_prueba()
        self.crear_enemigos_prueba()
        
    def crear_plataformas_prueba(self):
        # Plataforma base
        plataforma_base = Plataforma(0, ALTO_PANTALLA - 40, ANCHO_PANTALLA, 40)
        self.plataformas.add(plataforma_base)
        self.todos_sprites.add(plataforma_base)
        
        # Plataformas flotantes
        plataformas = [
            (300, 500, 200, 20),
            (600, 400, 200, 20),
            (900, 300, 200, 20),
            (1200, 400, 200, 20),
        ]
        
        for x, y, ancho, alto in plataformas:
            plataforma = Plataforma(x, y, ancho, alto)
            self.plataformas.add(plataforma)
            self.todos_sprites.add(plataforma)
    
    def crear_enemigos_prueba(self):
        # Crear diferentes tipos de enemigos
        enemigos = [
            (400, 450, "normal"),
            (700, 350, "volador"),
            (1000, 250, "tanque"),
            (1300, 350, "saltador")
        ]
        
        for x, y, tipo in enemigos:
            enemigo = Enemigo(x, y, tipo)
            self.enemigos.add(enemigo)
            self.todos_sprites.add(enemigo)
        
    def manejar_eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.ejecutando = False
                
            if evento.type == pygame.KEYDOWN:
                # Tecla ESC para pausar/reanudar
                if evento.key == pygame.K_ESCAPE:
                    if self.estado_actual == ESTADO_JUGANDO:
                        self.estado_actual = ESTADO_PAUSA
                    elif self.estado_actual == ESTADO_PAUSA:
                        self.estado_actual = ESTADO_JUGANDO
                
                # Tecla ESPACIO para iniciar juego desde el menú
                if evento.key == pygame.K_SPACE and self.estado_actual == ESTADO_MENU:
                    self.estado_actual = ESTADO_JUGANDO
                
                # Tecla R para reiniciar
                if evento.key == pygame.K_r:
                    if self.estado_actual in [ESTADO_MUERTE, ESTADO_NIVEL_COMPLETADO]:
                        self.estado_actual = ESTADO_JUGANDO
                
                # Controles del jugador
                if self.estado_actual == ESTADO_JUGANDO:
                    if evento.key == pygame.K_w:
                        self.jugador.saltar()
                    elif evento.key == pygame.K_x:
                        self.jugador.atacar()
                    elif evento.key == pygame.K_c:
                        self.jugador.activar_rage()
                    elif evento.key == pygame.K_v:
                        self.jugador.activar_madera_dura()

    def actualizar(self):
        if self.estado_actual == ESTADO_JUGANDO:
            # Actualizar plataformas
            for plataforma in self.plataformas:
                plataforma.actualizar()
            
            # Actualizar enemigos
            for enemigo in self.enemigos:
                enemigo.actualizar(self.jugador, self.plataformas)
                # Verificar si el enemigo ataca al jugador
                if enemigo.atacar(self.jugador):
                    # Efecto visual de daño
                    self.jugador.image.fill(ROJO)
                else:
                    self.jugador.image.fill(VERDE)
            
            # Actualizar jugador
            self.jugador.actualizar(self.plataformas)
            
            # Mantener jugador en pantalla
            if self.jugador.rect.left < 0:
                self.jugador.rect.left = 0
            if self.jugador.rect.right > ANCHO_PANTALLA:
                self.jugador.rect.right = ANCHO_PANTALLA
            if self.jugador.rect.top < 0:
                self.jugador.rect.top = 0
            if self.jugador.rect.bottom > ALTO_PANTALLA:
                self.jugador.rect.bottom = ALTO_PANTALLA
                
            # Verificar muerte
            if self.jugador.vida <= 0:
                self.estado_actual = ESTADO_MUERTE

    def dibujar(self):
        self.pantalla.fill(NEGRO)
        
        if self.estado_actual == ESTADO_MENU:
            # Dibujar menú principal
            fuente_titulo = pygame.font.Font(None, 74)
            fuente_instrucciones = pygame.font.Font(None, 36)
            
            # Título
            texto_titulo = fuente_titulo.render("Wood Will Rise", True, BLANCO)
            rect_titulo = texto_titulo.get_rect(center=(ANCHO_PANTALLA/2, ALTO_PANTALLA/3))
            self.pantalla.blit(texto_titulo, rect_titulo)
            
            # Instrucciones
            texto_instrucciones = fuente_instrucciones.render("Presiona ESPACIO para comenzar", True, BLANCO)
            rect_instrucciones = texto_instrucciones.get_rect(center=(ANCHO_PANTALLA/2, ALTO_PANTALLA/2))
            self.pantalla.blit(texto_instrucciones, rect_instrucciones)
            
            # Controles
            controles = [
                "Controles:",
                "W - Saltar",
                "A - Izquierda",
                "D - Derecha",
                "X - Atacar",
                "C - Rage Mode",
                "V - Madera Dura"
            ]
            
            for i, texto in enumerate(controles):
                texto_control = fuente_instrucciones.render(texto, True, BLANCO)
                rect_control = texto_control.get_rect(center=(ANCHO_PANTALLA/2, ALTO_PANTALLA/2 + 50 + i*30))
                self.pantalla.blit(texto_control, rect_control)
            
        elif self.estado_actual == ESTADO_JUGANDO:
            # Dibujar todos los sprites
            self.todos_sprites.draw(self.pantalla)
            
            # Dibujar UI
            fuente = pygame.font.Font(None, 36)
            # Vida
            texto_vida = fuente.render(f"Vida: {self.jugador.vida}", True, BLANCO)
            self.pantalla.blit(texto_vida, (10, 10))
            # Monedas
            texto_monedas = fuente.render(f"Monedas: {self.jugador.monedas}", True, BLANCO)
            self.pantalla.blit(texto_monedas, (10, 50))
            # Experiencia
            texto_exp = fuente.render(f"XP: {self.jugador.experiencia}", True, BLANCO)
            self.pantalla.blit(texto_exp, (10, 90))
            
        elif self.estado_actual == ESTADO_PAUSA:
            # Dibujar menú de pausa
            fuente_titulo = pygame.font.Font(None, 74)
            fuente_instrucciones = pygame.font.Font(None, 36)
            
            # Título
            texto_titulo = fuente_titulo.render("PAUSA", True, BLANCO)
            rect_titulo = texto_titulo.get_rect(center=(ANCHO_PANTALLA/2, ALTO_PANTALLA/3))
            self.pantalla.blit(texto_titulo, rect_titulo)
            
            # Instrucciones
            texto_instrucciones = fuente_instrucciones.render("Presiona ESC para continuar", True, BLANCO)
            rect_instrucciones = texto_instrucciones.get_rect(center=(ANCHO_PANTALLA/2, ALTO_PANTALLA/2))
            self.pantalla.blit(texto_instrucciones, rect_instrucciones)
            
        elif self.estado_actual == ESTADO_MUERTE:
            # Dibujar pantalla de muerte
            fuente_titulo = pygame.font.Font(None, 74)
            fuente_instrucciones = pygame.font.Font(None, 36)
            
            # Título
            texto_titulo = fuente_titulo.render("¡HAS MUERTO!", True, ROJO)
            rect_titulo = texto_titulo.get_rect(center=(ANCHO_PANTALLA/2, ALTO_PANTALLA/3))
            self.pantalla.blit(texto_titulo, rect_titulo)
            
            # Instrucciones
            texto_instrucciones = fuente_instrucciones.render("Presiona R para reiniciar", True, BLANCO)
            rect_instrucciones = texto_instrucciones.get_rect(center=(ANCHO_PANTALLA/2, ALTO_PANTALLA/2))
            self.pantalla.blit(texto_instrucciones, rect_instrucciones)
            
        pygame.display.flip()

    def ejecutar(self):
        while self.ejecutando:
            self.manejar_eventos()
            self.actualizar()
            self.dibujar()
            self.reloj.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    juego = Juego()
    juego.ejecutar() 