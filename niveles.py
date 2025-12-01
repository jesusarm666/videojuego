# niveles.py
# Generación y distribución uniforme de plataformas, monedas y enemigos
import random
from plataformas import Plataforma
from enemigos import Enemigo
from moneda import Moneda
from puerta import Puerta
from config import *

def _clamp_y(y):
    min_y = 120
    max_y = ALTO_PANTALLA - 160
    return max(min_y, min(y, max_y))

def _obtener_derecha_mas_a_la_derecha(plataformas):
    if not plataformas:
        return None
    return max(plataformas, key=lambda p: p.rect.right)

def _extender_ultima_plataforma(plataformas, minimo_ancho=220):
    derecha = _obtener_derecha_mas_a_la_derecha(plataformas)
    if derecha is None or derecha.rect.right < ANCHO_NIVEL - 200:
        x = max(ANCHO_NIVEL - minimo_ancho - 120, (derecha.rect.right + 50) if derecha else 600)
        ancho = max(minimo_ancho, ANCHO_NIVEL - x - 80)
        y = ALTO_PANTALLA - 150
        nueva = Plataforma(x, y, ancho, 40)
        plataformas.append(nueva)
        return nueva
    return derecha

def _colocar_puerta_en_plataforma(puerta, plataforma):
    puerta_x = plataforma.rect.right - puerta.rect.width - 10
    if puerta_x < plataforma.rect.left + 10:
        puerta_x = plataforma.rect.left + 10
    puerta.rect.x = puerta_x
    puerta.rect.y = plataforma.rect.top - puerta.rect.height
    return puerta

def _limpiar_derecha_de_puerta(plataformas, enemigos, puerta):
    margen = 8
    limite_x = puerta.rect.right + margen
    plataformas[:] = [p for p in plataformas if p.rect.left <= limite_x]
    enemigos[:] = [e for e in enemigos if e.rect.left <= limite_x]

# ------------------------------
# DISTRIBUCIÓN UNIFORME
# ------------------------------
def distribuir_plataformas_uniformemente(plataformas, extra_count, mobile_ratio=0.25, min_y=200, max_y=None):
    """
    Añade 'extra_count' plataformas distribuidas uniformemente a lo largo del nivel.
    Evita aglomeraciones respetando plataformas ya existentes.
    """
    if max_y is None:
        max_y = ALTO_PANTALLA - 180
    if extra_count <= 0:
        return

    left_margin = 150
    right_margin = 150
    usable_width = max(ANCHO_NIVEL - left_margin - right_margin, 400)
    section_width = usable_width / max(1, extra_count)

    placed = 0
    for i in range(extra_count):
        # calculamos la sección y posicion X aleatoria dentro de la sección
        x_min = left_margin + int(i * section_width)
        x_max = left_margin + int((i + 1) * section_width) - 80
        if x_max <= x_min:
            x_pos = x_min + 40
        else:
            x_pos = random.randint(x_min, x_max)
        ancho = random.choice(PLATFORM_WIDTH_OPTIONS)
        y_pos = random.randint(min_y, max_y)
        tipo = "movil" if random.random() < mobile_ratio else "normal"

        # evitar solapamiento cercano: buscamos un desplazamiento a la derecha hasta 4 intentos
        candidate = Plataforma(x_pos, y_pos, ancho, 36, tipo=tipo)
        conflict = False
        for p in plataformas:
            if not (candidate.rect.right + 80 < p.rect.left or candidate.rect.left > p.rect.right + 80):
                conflict = True
                break
        if conflict:
            shifted = False
            for shift in (80, 160, 240, 320):
                candidate.rect.x = x_pos + shift
                if candidate.rect.right >= ANCHO_NIVEL - 60:
                    continue
                coll = any(not (candidate.rect.right + 60 < p.rect.left or candidate.rect.left > p.rect.right + 60) for p in plataformas)
                if not coll:
                    shifted = True
                    break
            if not shifted:
                continue
        plataformas.append(candidate)
        placed += 1

    return

def generar_monedas_sobre_plataformas(plataformas, nivel):
    """
    Genera monedas sobre o cerca de las plataformas.
    Cantidad por plataforma aumenta con el nivel.
    """
    monedas = []
    monedas_por_plat = {1:1, 2:1, 3:2, 4:2, 5:3, 6:3}
    mpp = monedas_por_plat.get(nivel, 1)
    for p in plataformas:
        # evitar suelo completo
        if p.rect.width >= ANCHO_NIVEL - 50 and p.rect.left == 0:
            continue
        for i in range(mpp):
            offset = 15 + int((p.rect.width - 30) * (i + 0.5) / max(1, mpp))
            coin_x = p.rect.left + offset
            coin_y = p.rect.top - 18 - (0 if i % 2 == 0 else 28)
            # asegurar dentro de mundo
            if coin_x < 10:
                coin_x = 10
            if coin_x > ANCHO_NIVEL - 20:
                coin_x = ANCHO_NIVEL - 40
            monedas.append(Moneda(coin_x, coin_y))
    return monedas

def colocar_enemigos_uniformes(plataformas, nivel, agresividad):
    """
    Coloca enemigos de forma uniforme entre las plataformas útiles.
    Número de enemigos escala por nivel.
    """
    enemigos = []
    base_por_nivel = {1:2, 2:3, 3:4, 4:6, 5:8, 6:10}
    objetivo = base_por_nivel.get(nivel, 2)

    plataformas_utiles = [p for p in plataformas if not (p.rect.left == 0 and p.rect.width >= ANCHO_NIVEL - 10)]
    if not plataformas_utiles:
        return enemigos

    # ordenar por posición X para distribuir uniformemente
    plataformas_sorted = sorted(plataformas_utiles, key=lambda p: p.rect.left)
    n_plats = len(plataformas_sorted)
    step = max(1, int(n_plats / max(1, objetivo)))

    placed = 0
    idx = 0
    attempts = 0
    while placed < objetivo and attempts < objetivo * 6:
        attempts += 1
        plat = plataformas_sorted[idx % n_plats]
        # evitar la plataforma final (la más a la derecha)
        if plat.rect.right >= max(p.rect.right for p in plataformas) - 60:
            idx += step
            continue
        # escoger tipo según nivel y probabilidad
        r = random.random()
        if nivel <= 2:
            tipo = "normal" if r < 0.7 else "volador"
        elif nivel <= 4:
            tipo = "normal" if r < 0.5 else ("saltador" if r < 0.8 else "volador")
        else:
            tipo = "normal" if r < 0.4 else ("saltador" if r < 0.75 else ("volador" if r < 0.9 else "tanque"))

        ex = plat.rect.left + max(16, (plat.rect.width // 2) - 16 + random.randint(-24, 24))
        ey = plat.rect.top - 32
        enemigos.append(Enemigo(ex, ey, tipo, agresividad=agresividad))

        placed += 1
        idx += step

    return enemigos

# ------------------------------
# CARGA DE NIVELES (1..6) - progresión
# ------------------------------
def cargar_nivel(numero):
    plataformas = []
    enemigos = []
    monedas = []
    puerta = None

    if numero < 1:
        numero = 1
    if numero > TOTAL_NIVELES:
        numero = TOTAL_NIVELES

    agresividad_por_nivel = {1:1.0, 2:1.08, 3:1.15, 4:1.25, 5:1.4, 6:1.6}
    agres = agresividad_por_nivel.get(numero, 1.0)

    # definimos plataformas base compactas y luego añadimos extras mediante la distribución uniforme
    if numero == 1:
        plataformas = [
            Plataforma(0, ALTO_PANTALLA - 50, 900, 50),
            Plataforma(260, _clamp_y(520), 260, 36),
            Plataforma(620, _clamp_y(480), 280, 36),
        ]
        distribuir_plataformas_uniformemente(plataformas, extra_count=1, mobile_ratio=0.0)
    elif numero == 2:
        plataformas = [
            Plataforma(0, ALTO_PANTALLA - 50, 900, 50),
            Plataforma(300, _clamp_y(520), 240, 36, tipo="movil"),
            Plataforma(680, _clamp_y(460), 260, 36),
            Plataforma(1040, _clamp_y(520), 240, 36),
        ]
        distribuir_plataformas_uniformemente(plataformas, extra_count=2, mobile_ratio=0.25)
    elif numero == 3:
        plataformas = [
            Plataforma(0, ALTO_PANTALLA - 50, 1000, 50),
            Plataforma(320, _clamp_y(540), 260, 36, tipo="movil"),
            Plataforma(700, _clamp_y(460), 240, 36, tipo="movil"),
            Plataforma(1060, _clamp_y(520), 260, 36),
        ]
        distribuir_plataformas_uniformemente(plataformas, extra_count=3, mobile_ratio=0.35)
    elif numero == 4:
        plataformas = [
            Plataforma(0, ALTO_PANTALLA - 50, 1100, 50),
            Plataforma(300, _clamp_y(560), 240, 36, tipo="movil"),
            Plataforma(640, _clamp_y(480), 220, 36, tipo="movil"),
            Plataforma(980, _clamp_y(420), 240, 36, tipo="movil"),
            Plataforma(1320, _clamp_y(520), 300, 36),
        ]
        distribuir_plataformas_uniformemente(plataformas, extra_count=4, mobile_ratio=0.45)
    elif numero == 5:
        plataformas = [
            Plataforma(0, ALTO_PANTALLA - 50, 1100, 50),
            Plataforma(320, _clamp_y(540), 260, 36, tipo="movil"),
            Plataforma(660, _clamp_y(480), 260, 36, tipo="movil"),
            Plataforma(1000, _clamp_y(420), 260, 36, tipo="movil"),
            Plataforma(1340, _clamp_y(520), 300, 36),
        ]
        distribuir_plataformas_uniformemente(plataformas, extra_count=5, mobile_ratio=0.55)
    elif numero == 6:
        plataformas = [
            Plataforma(0, ALTO_PANTALLA - 50, 1200, 50),
            Plataforma(320, _clamp_y(560), 300, 36, tipo="movil"),
            Plataforma(720, _clamp_y(500), 280, 36, tipo="movil"),
            Plataforma(1120, _clamp_y(440), 280, 36, tipo="movil"),
            Plataforma(1520, _clamp_y(520), 360, 36),
        ]
        distribuir_plataformas_uniformemente(plataformas, extra_count=6, mobile_ratio=0.62)

    # asegurar suelo base
    existe_suelo_completo = any(p.rect.left <= 0 and p.rect.right >= ANCHO_NIVEL for p in plataformas)
    if not existe_suelo_completo:
        plataformas.insert(0, Plataforma(0, ALTO_PANTALLA - 50, ANCHO_NIVEL, 50))

    # generar monedas y enemigos de forma uniforme
    monedas = generar_monedas_sobre_plataformas(plataformas, numero)
    enemigos = colocar_enemigos_uniformes(plataformas, numero, agresividad=agres)

    # colocar puerta sobre la ultima plataforma
    puerta = Puerta(0,0)
    ultima_plat = _obtener_derecha_mas_a_la_derecha(plataformas)
    if ultima_plat is None or ultima_plat.rect.right < ANCHO_NIVEL - 160:
        ultima_plat = _extender_ultima_plataforma(plataformas)
    puerta = _colocar_puerta_en_plataforma(puerta, ultima_plat)

    if puerta.rect.bottom > LIMITE_MUERTE_Y:
        candidatas = [p for p in plataformas if p.rect.top < LIMITE_MUERTE_Y - 40]
        if candidatas:
            mejor = max(candidatas, key=lambda p: p.rect.right)
            puerta = _colocar_puerta_en_plataforma(puerta, mejor)
        else:
            final = _extender_ultima_plataforma(plataformas)
            puerta = _colocar_puerta_en_plataforma(puerta, final)

    _limpiar_derecha_de_puerta(plataformas, enemigos, puerta)

    # evitar intersecciones con plataformas cercanas
    for p in plataformas:
        if p is ultima_plat:
            continue
        if puerta.rect.colliderect(p.rect):
            puerta = _colocar_puerta_en_plataforma(puerta, ultima_plat)
            break

    inicio = (50, ALTO_PANTALLA - 200)

    # LOG: resumen por nivel (ayuda testing)
    print(f"[NIVEL {numero}] Plataformas={len(plataformas)} Enemigos={len(enemigos)} Monedas={len(monedas)} Puerta x={puerta.rect.x}")

    return plataformas, enemigos, monedas, puerta, inicio
