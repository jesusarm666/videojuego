# config.py
# ===========================
# CONFIGURACIÓN GENERAL
# ===========================

# Configuración de la pantalla
ANCHO_PANTALLA = 1280
ALTO_PANTALLA = 720
FPS = 60

# Configuración del jugador
VELOCIDAD_JUGADOR = 5
FUERZA_SALTO = -15
GRAVEDAD = 0.5
VELOCIDAD_CAIDA_MAX = 15

# Configuración del nivel
# Reducimos la longitud máxima del nivel para niveles "moderados"
ANCHO_NIVEL = 2400   # <--- reducido desde 3840 a 2400
ALTO_NIVEL = 1080
MARGEN_VIEWPORT = 256

# Estados del juego
ESTADO_MENU = 0
ESTADO_JUGANDO = 1
ESTADO_PAUSA = 2
ESTADO_NIVEL_COMPLETADO = 3
ESTADO_MUERTE = 4
ESTADO_VICTORIA = 5

# Colores
NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
ROJO = (255, 0, 0)
VERDE = (0, 255, 0)
AZUL = (0, 0, 255)
AMARILLO = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)

# Enemigos
VELOCIDAD_ENEMIGO_BASICO = 3
DISTANCIA_DETECCION = 300

# Powerups
DURACION_POWERUP = 10  # segundos

# --- GENERACIÓN / LIMPIEZA ---
GENERAR_ADELANTE_DIST = ANCHO_PANTALLA * 2
PROB_MOBILE_PLATFORM = 0.25
PROB_ENEMY_SPAWN = 0.35
MIN_GAP = 140
MAX_GAP = 300
PLATFORM_WIDTH_OPTIONS = [120, 140, 160, 180, 200]
CLEANUP_BUFFER = 600

# ===========================
# CAMPAÑA DE 6 NIVELES
# ===========================
TOTAL_NIVELES = 6

# ===========================
# LÍMITE DE MUERTE (caída)
# ===========================
LIMITE_MUERTE_Y = ALTO_NIVEL + 300
