# main.py
import pygame
import random
import time
from config import *
from jugador import Jugador
from enemigos import Enemigo
from plataformas import Plataforma
from moneda import Moneda
from puerta import Puerta
from niveles import cargar_nivel

pygame.init()
pantalla = pygame.display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA))
clock = pygame.time.Clock()

nivel_actual = 1

def reiniciar_nivel(nivel_num=1):
    plataformas, enemigos, monedas, puerta, inicio = cargar_nivel(nivel_num)
    jugador = Jugador(*inicio)
    max_platform_x = max((p.rect.right for p in plataformas), default=0)
    return jugador, plataformas, enemigos, monedas, puerta, max_platform_x

# cargar primer nivel
jugador, plataformas, enemigos, monedas, puerta_salida, max_platform_x = reiniciar_nivel(nivel_actual)

# BANDERAS Y CONTADORES
transicion_activa = False
detener_generacion = True  # usamos niveles pregenerados para distribución uniforme
monedas_totales = len(monedas)
monedas_recogidas = 0
enemigos_totales = len(enemigos)
enemigos_derrotados = 0

def generar_plataformas_adelante(plataformas, enemigos, current_max_x, jugador_x):
    if detener_generacion:
        return current_max_x
    while current_max_x - jugador_x < GENERAR_ADELANTE_DIST and current_max_x < ANCHO_NIVEL:
        gap = random.randint(MIN_GAP, MAX_GAP)
        ancho = random.choice(PLATFORM_WIDTH_OPTIONS)
        alto_y = random.randint(200, ALTO_PANTALLA - 140)
        new_x = min(current_max_x + gap, ANCHO_NIVEL - ancho)
        tipo = "movil" if random.random() < PROB_MOBILE_PLATFORM else "normal"
        nueva = Plataforma(new_x, alto_y, ancho, 30, tipo=tipo)
        plataformas.append(nueva)
        current_max_x = max(current_max_x, nueva.rect.right)
        if random.random() < PROB_ENEMY_SPAWN:
            ex = nueva.rect.left + (nueva.rect.width // 2) - 16
            ey = nueva.rect.top - 32
            etipo = random.choice(["normal", "saltador"])
            enemigos.append(Enemigo(ex, ey, etipo))
    return current_max_x

def limpiar_atras(plataformas, enemigos, monedas, cam_x):
    limite = cam_x - CLEANUP_BUFFER
    plataformas[:] = [p for p in plataformas if p.rect.right >= limite and p.rect.left <= ANCHO_NIVEL]
    enemigos[:] = [e for e in enemigos if e.rect.right >= limite and e.rect.left <= ANCHO_NIVEL]
    monedas[:] = [m for m in monedas if m.rect.right >= limite and m.rect.left <= ANCHO_NIVEL]

corriendo = True
jugador_muerto = False

# FUNCIÓN AYUDA: comprobar si puede abrir puerta (requiere ambas condiciones)
def verificar_abrir_puerta():
    global monedas_recogidas, monedas_totales, enemigos_derrotados, enemigos_totales, puerta_salida
    if monedas_recogidas >= monedas_totales and enemigos_derrotados >= enemigos_totales:
        if not puerta_salida.abierta:
            puerta_salida.abrir()
            print(f"[DEBUG] Nivel {nivel_actual}: Condiciones cumplidas -> puerta ABIERTA (monedas {monedas_recogidas}/{monedas_totales}, enemigos {enemigos_derrotados}/{enemigos_totales}).")

while corriendo:
    dt = clock.tick(FPS) / 1000.0

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            corriendo = False
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_w and not jugador_muerto and not transicion_activa:
                jugador.saltar()
            if evento.key == pygame.K_j and not jugador_muerto and not transicion_activa:
                alcanzados = jugador.atacar(enemigos)
                # eliminar enemigos atacados y contabilizar derrotas
                for e in alcanzados:
                    try:
                        enemigos.remove(e)
                        enemigos_derrotados += 1
                    except ValueError:
                        pass
            if evento.key == pygame.K_r:
                jugador, plataformas, enemigos, monedas, puerta_salida, max_platform_x = reiniciar_nivel(nivel_actual)
                monedas_totales = len(monedas)
                monedas_recogidas = 0
                enemigos_totales = len(enemigos)
                enemigos_derrotados = 0
                jugador_muerto = False
                transicion_activa = False
                detener_generacion = True

    # muerte por caída inmediata
    if jugador.rect.top > LIMITE_MUERTE_Y:
        print(f"[DEBUG] Nivel {nivel_actual}: jugador cayó por debajo del límite. Reiniciando nivel.")
        jugador, plataformas, enemigos, monedas, puerta_salida, max_platform_x = reiniciar_nivel(nivel_actual)
        monedas_totales = len(monedas)
        monedas_recogidas = 0
        enemigos_totales = len(enemigos)
        enemigos_derrotados = 0
        jugador_muerto = False
        transicion_activa = False
        detener_generacion = True
        continue

    # transición en curso: solo animación de puerta
    if transicion_activa:
        sigue = puerta_salida.actualizar_animacion()
        if not sigue:
            nivel_actual += 1
            if nivel_actual > TOTAL_NIVELES:
                pantalla.fill(NEGRO)
                fuente_v = pygame.font.SysFont(None, 80)
                texto_v = fuente_v.render("¡VICTORIA!", True, BLANCO)
                pantalla.blit(texto_v, (ANCHO_PANTALLA//2 - 150, ALTO_PANTALLA//2 - 50))
                pygame.display.flip()
                pygame.time.wait(1500)
                corriendo = False
                break
            jugador, plataformas, enemigos, monedas, puerta_salida, max_platform_x = reiniciar_nivel(nivel_actual)
            monedas_totales = len(monedas)
            monedas_recogidas = 0
            enemigos_totales = len(enemigos)
            enemigos_derrotados = 0
            transicion_activa = False
            detener_generacion = True
            continue

    # generar adelante si se permitiera (está detenido por defecto)
    max_platform_x = generar_plataformas_adelante(plataformas, enemigos, max_platform_x, jugador.rect.x)

    # actualizar plataformas (móviles)
    for p in plataformas:
        p.actualizar()

    # arrastrar entidades sobre plataformas móviles
    entidades = [jugador] + enemigos
    for p in plataformas:
        if getattr(p, "movil", False) and getattr(p, "last_dx", 0) != 0:
            dx = p.last_dx
            for ent in entidades:
                if p.entidad_encima(ent):
                    ent.rect.x += dx

    # tope superior
    if jugador.rect.top < 0:
        jugador.rect.top = 0
        jugador.velocidad_y = 0

    jugador.actualizar(plataformas)

    # limitar jugador dentro del mundo
    if jugador.rect.left < 0:
        jugador.rect.left = 0
    if jugador.rect.right > ANCHO_NIVEL:
        jugador.rect.right = ANCHO_NIVEL

    # actualizar enemigos y gestionar interacciones (stomp vs frontal)
    if not transicion_activa:
        enemigos_copy = enemigos[:]
        for enemigo in enemigos_copy:
            enemigo.actualizar(jugador, plataformas)

            if jugador.rect.colliderect(enemigo.rect):
                pies_diff = jugador.rect.bottom - enemigo.rect.top
                # STOMP: jugador cae sobre enemigo
                if jugador.velocidad_y > 0 and pies_diff > -4 and pies_diff < 24:
                    try:
                        enemigos.remove(enemigo)
                        enemigos_derrotados += 1
                    except ValueError:
                        pass
                    jugador.velocidad_y = FUERZA_SALTO * 0.6
                    jugador.experiencia += 7
                    verificar_abrir_puerta()
                    continue
                else:
                    resultado = enemigo.atacar(jugador)
                    if resultado == "muerto":
                        jugador_muerto = True

            # límites para enemigos dentro del nivel
            if enemigo.rect.left < 0:
                enemigo.rect.left = 0
                enemigo.direccion = 1
            if enemigo.rect.right > ANCHO_NIVEL:
                enemigo.rect.right = ANCHO_NIVEL
                enemigo.direccion = -1

    # recolectar monedas: incrementar contador y comprobar condiciones de puerta
    for m in monedas[:]:
        if jugador.rect.colliderect(m.rect):
            try:
                m.recoger(jugador)
            except Exception:
                jugador.monedas += 1
                jugador.experiencia += 5
            try:
                monedas.remove(m)
            except ValueError:
                pass
            monedas_recogidas += 1
            verificar_abrir_puerta()

    # colisión con puerta: iniciar transición solo si abierta
    if puerta_salida.abierta and puerta_salida.colisiona_con(jugador) and not transicion_activa and not jugador_muerto:
        print(f"[DEBUG] Nivel {nivel_actual}: jugador tocó puerta; iniciando transición.")
        puerta_salida.iniciar_transicion()
        transicion_activa = True
        detener_generacion = True
        continue

    # GAME OVER
    if jugador_muerto:
        pantalla.fill(NEGRO)
        cam_x = jugador.rect.centerx - ANCHO_PANTALLA // 2
        cam_x = max(0, min(cam_x, max(0, ANCHO_NIVEL - ANCHO_PANTALLA)))
        for p in plataformas:
            pantalla.blit(p.image, (p.rect.x - cam_x, p.rect.y))
        pantalla.blit(jugador.image, (jugador.rect.x - cam_x, jugador.rect.y))
        for e in enemigos:
            pantalla.blit(e.image, (e.rect.x - cam_x, e.rect.y))
        for m in monedas:
            pantalla.blit(m.image, (m.rect.x - cam_x, m.rect.y))
        pantalla.blit(puerta_salida.image, (puerta_salida.rect.x - cam_x, puerta_salida.rect.y))
        fuente = pygame.font.SysFont(None, 80)
        texto = fuente.render("GAME OVER", True, ROJO)
        pantalla.blit(texto, (ANCHO_PANTALLA//2 - 180, ALTO_PANTALLA//2 - 100))
        fuente2 = pygame.font.SysFont(None, 40)
        texto2 = fuente2.render("Presiona R para reiniciar", True, BLANCO)
        pantalla.blit(texto2, (ANCHO_PANTALLA//2 - 180, ANCHO_PANTALLA//2))
        pygame.display.flip()
        continue

    # limpieza de atrás
    cam_x = jugador.rect.centerx - ANCHO_PANTALLA // 2
    cam_x = max(0, min(cam_x, max(0, ANCHO_NIVEL - ANCHO_PANTALLA)))
    limpiar_atras(plataformas, enemigos, monedas, cam_x)

    # cámara horizontal limitada
    cam_x = jugador.rect.centerx - ANCHO_PANTALLA // 2
    cam_x = max(0, min(cam_x, max(0, ANCHO_NIVEL - ANCHO_PANTALLA)))

    # ------------------- DIBUJO / ESTILO SIMPLE (Geometry-like) -------------------
    pantalla.fill((30, 34, 46))  # fondo plano
    # subtle horizontal bands as background
    for i in range(0, ALTO_PANTALLA, 40):
        rect = (0, i, ANCHO_PANTALLA, 20)
        pygame.draw.rect(pantalla, (30 + (i//40)*2, 34 + (i//40)*2, 46 + (i//40)*2), rect)

    # plataformas (ya son rects geométricos)
    for p in plataformas:
        pantalla.blit(p.image, (p.rect.x - cam_x, p.rect.y))

    # monedas
    for m in monedas:
        pantalla.blit(m.image, (m.rect.x - cam_x, m.rect.y))

    # puerta (anim o normal)
    if getattr(puerta_salida, "_transicion_activa", False) or getattr(puerta_salida, "image_anim", None):
        puerta_salida.dibujar_anim(pantalla, cam_x)
    else:
        pantalla.blit(puerta_salida.image, (puerta_salida.rect.x - cam_x, puerta_salida.rect.y))

    # jugador
    pantalla.blit(jugador.image, (jugador.rect.x - cam_x, jugador.rect.y))

    # enemigos
    for enemigo in enemigos:
        pantalla.blit(enemigo.image, (enemigo.rect.x - cam_x, enemigo.rect.y))

    # ------------------- HUD MINIMALISTA TRANSPARENTE -------------------
    hud_padding_x = 18
    hud_padding_y = 12
    fuente = pygame.font.SysFont(None, 28)

    # Icon sizes
    icon_size = 18
    gap_x = 14
    line_height = 28

    # --- Vida (icon + texto) ---
    icon_x = hud_padding_x
    icon_y = hud_padding_y
    # simple geometric icon: small rounded rectangle (as life bar icon)
    vida_rect = pygame.Rect(icon_x, icon_y + 6, icon_size, icon_size - 4)
    pygame.draw.rect(pantalla, ROJO, vida_rect, border_radius=4)
    pygame.draw.rect(pantalla, BLANCO, vida_rect, 2, border_radius=4)
    texto_vida = fuente.render(f"Vida: {jugador.vida}", True, BLANCO)
    pantalla.blit(texto_vida, (icon_x + icon_size + 8, icon_y))

    # --- Monedas (icon + texto) ---
    icon_x2 = hud_padding_x
    icon_y2 = hud_padding_y + line_height
    center_coin = (icon_x2 + icon_size//2, icon_y2 + icon_size//2 + 4)
    pygame.draw.circle(pantalla, AMARILLO, center_coin, icon_size//2)
    pygame.draw.circle(pantalla, BLANCO, center_coin, icon_size//2, 2)
    texto_monedas = fuente.render(f"{monedas_recogidas}/{monedas_totales}", True, AMARILLO)
    pantalla.blit(texto_monedas, (icon_x2 + icon_size + 8, icon_y2))

    # Label for coins
    label_coin = pygame.font.SysFont(None, 20).render("Monedas", True, BLANCO)
    pantalla.blit(label_coin, (icon_x2 + icon_size + 8 + texto_monedas.get_width() + 8, icon_y2 + 4))

    # --- Enemigos (icon + texto) ---
    icon_x3 = hud_padding_x
    icon_y3 = hud_padding_y + line_height * 2
    # simple square icon for enemy
    enemy_rect = pygame.Rect(icon_x3, icon_y3 + 6, icon_size, icon_size - 4)
    pygame.draw.rect(pantalla, MAGENTA, enemy_rect)
    pygame.draw.rect(pantalla, BLANCO, enemy_rect, 2)
    texto_enems = fuente.render(f"{enemigos_derrotados}/{enemigos_totales}", True, MAGENTA)
    pantalla.blit(texto_enems, (icon_x3 + icon_size + 8, icon_y3))

    # --- Nivel (icon + texto) align right on HUD area ---
    nivel_text = fuente.render(f"Nivel: {nivel_actual}/{TOTAL_NIVELES}", True, CYAN)
    # draw a small diamond icon left of the level text
    nivel_icon_w = icon_size
    nivel_icon_h = icon_size
    nivel_icon_x = ANCHO_PANTALLA - hud_padding_x - nivel_icon_w - 8 - nivel_text.get_width()
    nivel_icon_y = hud_padding_y
    # diamond polygon
    cx = nivel_icon_x + nivel_icon_w // 2
    cy = nivel_icon_y + nivel_icon_h // 2 + 6
    diamond_pts = [(cx, cy - nivel_icon_h//2), (cx + nivel_icon_w//2, cy), (cx, cy + nivel_icon_h//2), (cx - nivel_icon_w//2, cy)]
    pygame.draw.polygon(pantalla, CYAN, diamond_pts)
    pygame.draw.polygon(pantalla, BLANCO, diamond_pts, 2)
    pantalla.blit(nivel_text, (nivel_icon_x + nivel_icon_w + 8, nivel_icon_y))

    # If the door is blocked show a subtle centered message (no background)
    if not puerta_salida.abierta:
        fuente_small = pygame.font.SysFont(None, 22)
        msg = "Puerta BLOQUEADA: recoge monedas y derrota enemigos"
        txt = fuente_small.render(msg, True, (220, 200, 80))
        pantalla.blit(txt, (ANCHO_PANTALLA//2 - txt.get_width()//2, 10))

    pygame.display.flip()

pygame.quit()
