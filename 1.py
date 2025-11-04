import pygame
import sys
import random
import os
import math
import ctypes
from ctypes import wintypes
from Boss2_AI import Boss2AI
from music_menu import MusicMenu

# Initialize
pygame.init()
pygame.mixer.init()
base_path = os.path.dirname(__file__)
music_menu = MusicMenu(base_path)

# Screen
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Triangle Blaster")

# Clock
clock = pygame.time.Clock()
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)

# Fonts
font = pygame.font.SysFont("Arial", 30)
title_font = pygame.font.SysFont("Arial", 50)
settings_title = font.render("Settings", True, WHITE)
back_text = font.render("Press ESC to go Back", True, YELLOW)

def draw_text_center(text, font, color, x, y):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    screen.blit(text_surface, text_rect)

# Load Sounds
beam_sound = pygame.mixer.Sound("Beam.mp3")
explosion_sound = pygame.mixer.Sound("small.mp3")
loss_sound = pygame.mixer.Sound("loss.mp3")
boss_death_sound = pygame.mixer.Sound("boss.mp3")

# Load Images
base_path = os.path.dirname(__file__)
enemy_imgs = [
    pygame.transform.scale(pygame.image.load(os.path.join(base_path, "enemy.webp")), (40, 30)),
    pygame.transform.scale(pygame.image.load(os.path.join(base_path, "enemy1.png")), (40, 30)),
    pygame.transform.scale(pygame.image.load(os.path.join(base_path, "enemy2.png")), (40, 30))
]
boss_imgs = [
    pygame.transform.scale(pygame.image.load(os.path.join(base_path, "boss.png")), (100, 80)),
    pygame.transform.scale(pygame.image.load(os.path.join(base_path, "boss1.png")), (100, 80)),
    pygame.transform.scale(pygame.image.load(os.path.join(base_path, "boss2.png")), (100, 80))
]
powerup_img = pygame.transform.scale(pygame.image.load(os.path.join(base_path, "2x.png")), (30, 30))

# Game States
START, PLAYING, PAUSED, GAME_OVER, NEXT_WAVE, BOSS_WAVE, FINISHED = "start", "playing", "paused", "game_over", "next_wave", "boss_wave", "finished"
game_state = START
# Volume control
music_volume = 0.3
game_volume = 0.1
game_state = "start"
previous_state = None
pause_pressed = False
# --- Discrete Volume Bars ---
max_bars = 10
music_volume_bars = int(music_volume * max_bars)  # convert 0.5 -> 5
game_volume_bars = int(game_volume * max_bars)

# Players
player1 = pygame.Rect(WIDTH // 2 - 50, HEIGHT - 60, 40, 40)
player2 = pygame.Rect(WIDTH // 2 + 50, HEIGHT - 60, 40, 40)
players_enabled = 1  # 1 for single, 2 for multiplayer
player_speed = 7
shared_health = 15

# Bullets and powerups
player1_bullets, player2_bullets = [], []
enemy_bullets, boss_bullets, enemies = [], [], []
powerups = []
player1_last_hit_time = 0
player2_last_hit_time = 0
DAMAGE_COOLDOWN_TIME = 20
player1_damage_cooldown = 0
player2_damage_cooldown = 0
player_damage_cooldown = 1000  # in milliseconds (1 seconds)
player1_inside_laser = False
player2_inside_laser = False

# Boss
boss2_window_offset_x = 0
boss2_window_offset_y = 0
boss2_window_active = False
boss_ai = None

# Enemies
enemy_direction = 1  # 1 = right, -1 = left
enemy_speed_x = 2    # speed in pixels per frame

# Background Music
pygame.mixer.music.load("music.mp3")
pygame.mixer.music.set_volume(music_volume)
pygame.mixer.music.play(-1)  # loop forever

# Flags
double_fire_timer1, double_fire_timer2 = 0, 0
enemy_rows, enemy_cols, enemy_speed, enemy_cooldown = 2, 12, 2, 70
boss = None
boss_health, boss_index, boss_move_dir = 100, 0, 1
boss_fire_timer = 0
boss_fire_cooldown = 120  # about 2 seconds per shot
cooldown_counter1, cooldown_counter2 = 0, 0
enemy_fire_counter, wave, wave_timer = 0, 1, 60
laser_active = False
laser_angle = 0
laser_timer = 0
laser_cooldown = 180  # 3 seconds between toggles
laser_dir = 1
lasers = []
MAX_LASERS = 4           # how many lasers can exist at once
LASER_WARNING_TIME = 180 # 3 sec warning
LASER_ACTIVE_TIME = 120   # 2 sec active
LASER_COOLDOWN = 90      # time between spawns (~1.5 sec)
LASER_THICKNESS = 10    # 5x thicker than before
laser_spawn_timer = 0

# --- MUSIC SETUP ---
def get_music_files():
    music_folder = os.path.join(os.path.dirname(__file__), "Music")
    if not os.path.exists(music_folder):
        os.makedirs(music_folder)
    return [f for f in os.listdir(music_folder) if f.endswith(".mp3")]

def play_music(filename):
    music_folder = os.path.join(os.path.dirname(__file__), "Music")
    path = os.path.join(music_folder, filename)
    pygame.mixer.music.stop()
    pygame.mixer.music.load(path)
    pygame.mixer.music.play(-1)  # loop forever

def music_menu(screen, font, clock):
    music_files = get_music_files()
    selected = 0
    running = True

    while running:
        screen.fill((0, 0, 0))

        # Title
        title = font.render("Music Menu", True, (255, 255, 255))
        screen.blit(title, (400 - title.get_width() // 2, 80))

        # Display list of songs
        if not music_files:
            text = font.render("No music files found in /Music", True, (255, 0, 0))
            screen.blit(text, (400 - text.get_width() // 2, 250))
        else:
            for i, file in enumerate(music_files):
                display_name = f"{i+1}. {file[:-4]}"  # remove .mp3
                color = (0, 255, 0) if i == selected else (255, 255, 255)
                text = font.render(display_name, True, color)

                # center horizontally
                x = 50  # fixed left padding
                y = 200 + i * 40
                screen.blit(text, (x, y))

                # underline for selected
                if i == selected:
                    pygame.draw.line(screen, (0, 150, 255),
                                    (x, y + text.get_height() + 2),
                                    (x + text.get_width(), y + text.get_height() + 2), 2)

        # Footer
        esc_text = font.render("Press ESC or M to go Back", True, (255, 255, 0))
        screen.blit(esc_text, (400 - esc_text.get_width() // 2, 550))

        pygame.display.flip()
        clock.tick(30)

        # Input handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_m:
                    running = False
                elif event.key == pygame.K_UP:
                    selected = (selected - 1) % len(music_files)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(music_files)
                elif event.key == pygame.K_RETURN and music_files:
                    play_music(music_files[selected])

def spawn_wave():
    global enemies
    enemies = []
    if wave <= 4:
        level = 0
    elif wave <= 9:
        level = 1
    else:
        level = 2

    for row in range(enemy_rows):
        for col in range(enemy_cols):
            x = 80 + col * 60
            y = 50 + row * 50
            base_health = 3
            health = base_health * (1.5 if level >= 1 else 1)
            if level == 2:
                health *= 1.5
            enemies.append({
                'rect': pygame.Rect(x, y, 40, 30),
                'health': int(health),
                'img': enemy_imgs[level],
                'type': f'enemy{"" if level == 0 else level}',
            })

def spawn_boss():
    global boss, boss_health, boss_index
    boss_fire_timer = 0
    if wave == 5:
        boss_index = 0
        boss_health = 50
    elif wave == 10:
        boss_index = 1
        boss_health = 75
    elif wave == 15:
        boss_index = 2
        boss_health = 100
    else:
        boss_index = 0
        boss_health = 50  # fallback

    boss = {
        'rect': pygame.Rect(WIDTH // 2 - 50, 50, 100, 80),
        'health': boss_health,
        'img': boss_imgs[boss_index],
        'ricochet': 3
    }
    boss_bullets.clear()

def draw_player(p, color):
    pygame.draw.polygon(screen, color, [(p.centerx, p.top), (p.left, p.bottom), (p.right, p.bottom)])

def draw_enemies():
    for e in enemies:
        if e['health'] > 0:
            screen.blit(e['img'], e['rect'].topleft)

def draw_boss():
    if boss:
        screen.blit(boss['img'], boss['rect'].topleft)
        pygame.draw.rect(screen, RED, (boss['rect'].x, boss['rect'].y - 10, boss['rect'].width, 5))
        pygame.draw.rect(screen, GREEN, (boss['rect'].x, boss['rect'].y - 10, boss['rect'].width * (boss['health'] / 50), 5))

def draw_health():
    text1 = font.render(f"Health: {shared_health}", True, WHITE)
    screen.blit(text1, (10, 10))
    if players_enabled == 2:
        text2 = font.render(f"Health: {shared_health}", True, WHITE)
        screen.blit(text2, (WIDTH - 150, 10))

def draw_wave():
    text = font.render(f"Wave {wave}", True, WHITE)
    screen.blit(text, (WIDTH // 2 - 60, HEIGHT // 2))

# When spawning enemies, add 'orig_x' and 'move_dir'
def spawn_wave():
    global enemies
    enemies = []
    if wave <= 4:
        level = 0
    elif wave <= 9:
        level = 1
    else:
        level = 2

    for row in range(enemy_rows):
        for col in range(enemy_cols):
            x = 80 + col * 60
            y = 50 + row * 50
            base_health = 3
            health = base_health * (1.5 if level >= 1 else 1)
            if level == 2:
                health *= 1.5
            enemies.append({
                'rect': pygame.Rect(x, y, 40, 30),
                'health': int(health),
                'img': enemy_imgs[level],
                'type': f'enemy{"" if level == 0 else level}',
                'orig_x': x,              # mean position
                'move_dir': 1              # 1 = right, -1 = left
            })

def reset_game():
    global player1, player2, shared_health, player1_bullets, player2_bullets
    global enemy_bullets, boss_bullets, wave, game_state, boss, powerups
    player1.x = WIDTH // 2 - 50
    player2.x = WIDTH // 2 + 50
    shared_health = 15
    player1_bullets.clear()
    player2_bullets.clear()
    enemy_bullets.clear()
    boss_bullets.clear()
    lasers.clear()
    powerups.clear()
    wave = 1
    boss = None
    game_state = START

class BossBullet:
    def __init__(self, rect, dx, dy):
        self.rect = rect
        self.dx = dx
        self.dy = dy
        self.ricochet = 2

def draw_volume_bar(x, y, volume, label):
    max_blocks = 10
    filled_blocks = int(volume * max_blocks)
    block_width = 25
    block_height = 20
    spacing = 8

    text = font.render(label, True, WHITE)
    screen.blit(text, (x, y - 30))

    for i in range(max_blocks):
        color = GREEN if i < filled_blocks else (60, 60, 60)
        rect = pygame.Rect(x + i * (block_width + spacing), y, block_width, block_height)
        pygame.draw.rect(screen, color, rect, border_radius=4)

def boss2_fire_octagon(center_x, center_y):
    speed = 6
    for i in range(8):
        angle = math.radians(i * 45)  # 360 / 8 = 45 degrees
        dx = math.cos(angle) * speed
        dy = math.sin(angle) * speed
        boss_bullets.append(BossBullet(pygame.Rect(center_x - 5, center_y - 5, 10, 10), dx, dy))
        
running = True
while running:
    clock.tick(FPS)
    screen.fill(BLACK)
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if game_state in [PLAYING, PAUSED, "settings"]:
                    reset_game()
                    lasers.clear()
                    game_state = START
                elif game_state == START:
                    running = False
            elif event.key == pygame.K_p:
                if game_state != "settings":
                    # Pause the game + music
                    previous_state = game_state
                    game_state = "settings"
                else:
                    # Resume game + music
                    game_state = previous_state if previous_state else START
                    pygame.mixer.music.unpause()
            elif event.key == pygame.K_m:
                paused = True
                music_menu(screen, font, clock)
                paused = False

    if game_state == START:
        title_text = font.render("Space Triangle Blaster", True, WHITE)
        option1 = font.render("1. Single Player", True, GREEN)
        option2 = font.render("2. Multiplayer", True, YELLOW)
        option3 = font.render("3. Settings", True, WHITE)
        option4 = font.render("4. Music", True, WHITE)

        
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 2 - 100))
        screen.blit(option1, (WIDTH // 2 - option1.get_width() // 2, HEIGHT // 2 - 20))
        screen.blit(option2, (WIDTH // 2 - option2.get_width() // 2, HEIGHT // 2 + 30))
        screen.blit(option3, (WIDTH // 2 - option3.get_width() // 2, HEIGHT // 2 + 80))
        screen.blit(option4, (WIDTH // 2 - option4.get_width() // 2, HEIGHT // 2 + 130))

        if keys[pygame.K_1]:
            players_enabled = 1
            game_state = NEXT_WAVE
            wave_timer = 60
        elif keys[pygame.K_2]:
            players_enabled = 2
            game_state = NEXT_WAVE
            wave_timer = 60
        elif keys[pygame.K_3]:
            previous_state = START
            game_state = "settings"
        elif keys[pygame.K_4]:  
            music_menu(screen, font, clock)
    
    elif game_state == "settings":
        screen.fill((10, 10, 10))
        draw_text_center("Settings", title_font, WHITE, WIDTH // 2, 100)

        # 🎵 Draw the volume bars
        draw_volume_bar(WIDTH // 2 - 150, 250, music_volume, "Music Volume")
        draw_volume_bar(WIDTH // 2 - 150, 350, game_volume, "Game Volume")

        info_text = font.render("↑/↓ Music | ←/→ Game | ESC to Back | P to Resume", True, (200, 200, 200))
        screen.blit(info_text, (WIDTH // 2 - info_text.get_width() // 2, HEIGHT - 100))

        # Continuous key press for smooth bar adjustment
        if keys[pygame.K_UP]:
            music_volume_bars = min(max_bars, music_volume_bars + 0.1)
        if keys[pygame.K_DOWN]:
            music_volume_bars = max(0, music_volume_bars - 0.1)
        if keys[pygame.K_RIGHT]:
            game_volume_bars = min(max_bars, game_volume_bars + 0.1)
        if keys[pygame.K_LEFT]:
            game_volume_bars = max(0, game_volume_bars - 0.1)

        # Update actual volume values
        music_volume = music_volume_bars / max_bars
        game_volume = game_volume_bars / max_bars
        pygame.mixer.music.set_volume(music_volume)
        beam_sound.set_volume(game_volume)
        explosion_sound.set_volume(game_volume)
        boss_death_sound.set_volume(game_volume)
        loss_sound.set_volume(game_volume)

        # ⏪ Back / Resume
        if keys[pygame.K_ESCAPE]:
            game_state = START

            # Input handling
            if keys[pygame.K_LEFT]:
                music_volume = max(0, music_volume - 0.01)
            if keys[pygame.K_RIGHT]:
                music_volume = min(1, music_volume + 0.01)
            if keys[pygame.K_a]:
                game_volume = max(0, game_volume - 0.01)
            if keys[pygame.K_d]:
                game_volume = min(1, game_volume + 0.01)

            
            game_volume = game_volume_bars / max_bars
            pygame.mixer.music.set_volume(music_volume)
            beam_sound.set_volume(game_volume)
            explosion_sound.set_volume(game_volume)
            boss_death_sound.set_volume(game_volume)
            loss_sound.set_volume(game_volume)

    elif game_state == PAUSED:
        pause_text = font.render("Paused", True, WHITE)
        resume_text = font.render("Press P to Resume", True, YELLOW)

        screen.blit(pause_text, (WIDTH // 2 - pause_text.get_width() // 2, HEIGHT // 2 - 30))
        screen.blit(resume_text, (WIDTH // 2 - resume_text.get_width() // 2, HEIGHT // 2 + 20))
    
    elif game_state == GAME_OVER:
        over_text = font.render("GAME OVER", True, RED)
        restart_text = font.render("Press ENTER to Restart", True, WHITE)

        screen.blit(over_text, (WIDTH // 2 - over_text.get_width() // 2, HEIGHT // 2 - 30))
        screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 20))

        if keys[pygame.K_RETURN]:
            reset_game()

    elif game_state == FINISHED:
        win_text = font.render("YOU WIN!", True, GREEN)
        thanks_text = font.render("Thanks for playing!", True, WHITE)
        restart_text = font.render("Press ENTER to Restart", True, YELLOW)

        screen.blit(win_text, (WIDTH // 2 - win_text.get_width() // 2, HEIGHT // 2 - 60))
        screen.blit(thanks_text, (WIDTH // 2 - thanks_text.get_width() // 2, HEIGHT // 2 - 10))
        screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 40))

        if keys[pygame.K_RETURN]:
            reset_game()
    elif game_state == "settings":
        settings_title = font.render("Settings", True, WHITE)
        back_text = font.render("Press ESC to go Back", True, YELLOW)
  
    elif game_state == "music_menu":
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                music_menu.handle_input(event)
        music_menu.draw()

        screen.blit(settings_title, (WIDTH // 2 - settings_title.get_width() // 2, HEIGHT // 2 - 50))
        screen.blit(back_text, (WIDTH // 2 - back_text.get_width() // 2, HEIGHT // 2 + 20))

        if keys[pygame.K_ESCAPE]:
            game_state = START

    elif game_state == NEXT_WAVE:
        # Show wave message for a moment, then spawn enemies or boss
        draw_wave()
        wave_timer -= 1
        if wave_timer <= 0:
            if wave % 5 == 0:
                spawn_boss()
                game_state = PLAYING
            else:
                spawn_wave()
                game_state = PLAYING
    
    elif game_state == BOSS_WAVE:
        draw_wave()
        wave_timer -= 1
        if wave_timer <= 0:
            game_state = PLAYING

    elif game_state == PLAYING:
        # Movement
        # 🧭 Player 1 Movement (arrow keys)
        if keys[pygame.K_LEFT] and player1.left > 0:
            player1.x -= player_speed
        if keys[pygame.K_RIGHT] and player1.right < WIDTH:
            player1.x += player_speed
        if keys[pygame.K_UP] and player1.top > 0:
            player1.y -= player_speed
        if keys[pygame.K_DOWN] and player1.bottom < HEIGHT:
            player1.y += player_speed

        # 🧭 Player 2 Movement (WASD)
        if players_enabled == 2:
            if keys[pygame.K_a] and player2.left > 0:
                player2.x -= player_speed
            if keys[pygame.K_d] and player2.right < WIDTH:
                player2.x += player_speed
            if keys[pygame.K_w] and player2.top > 0:
                player2.y -= player_speed
            if keys[pygame.K_s] and player2.bottom < HEIGHT:
                player2.y += player_speed

        # Shooting
        if keys[pygame.K_SPACE] and cooldown_counter1 == 0:
            for dx in [-7, 7] if double_fire_timer1 > 0 else [0]:
                player1_bullets.append(pygame.Rect(player1.centerx + dx - 3, player1.top, 6, 15))
            pygame.mixer.Sound.play(beam_sound)
            cooldown_counter1 = 15

        if players_enabled == 2 and cooldown_counter2 == 0:
            for dx in [-7, 7] if double_fire_timer2 > 0 else [0]:
                player2_bullets.append(pygame.Rect(player2.centerx + dx - 3, player2.top, 6, 15))
            pygame.mixer.Sound.play(beam_sound)
            cooldown_counter2 = 15

        cooldown_counter1 = max(cooldown_counter1 - 1, 0)
        cooldown_counter2 = max(cooldown_counter2 - 1, 0)
        double_fire_timer1 = max(double_fire_timer1 - 1, 0)
        double_fire_timer2 = max(double_fire_timer2 - 1, 0)
       
        # --- Laser Spawning ---
        laser_spawn_timer += 1
        if laser_spawn_timer >= LASER_COOLDOWN and len(lasers) < MAX_LASERS:
            orientation = random.choice(["vertical", "horizontal"])
            if orientation == "vertical":
                pos = random.randint(100, WIDTH - 100)
            else:
                pos = random.randint(100, HEIGHT - 100)

            lasers.append({
                'orientation': orientation,
                'pos': pos,
                'timer': LASER_WARNING_TIME,
                'active': False
            })
            laser_spawn_timer = 0

        # Bullet Logic
        for bullet_list in [player1_bullets, player2_bullets]:
            for b in bullet_list[:]:
                b.y -= 12
                if b.bottom < 0:
                    bullet_list.remove(b)
                else:
                    if boss and b.colliderect(boss['rect']):
                        boss['health'] -= 1
                        bullet_list.remove(b)
                        if boss['health'] <= 0:
                            pygame.mixer.Sound.play(boss_death_sound)
                            boss = None
                            # Don't increment wave here; let NEXT_WAVE handle it
                            game_state = FINISHED if wave >= 15 else NEXT_WAVE
                            wave_timer = 60
                    for e in enemies:
                        if b.colliderect(e['rect']) and e['health'] > 0:
                            e['health'] -= 1
                            bullet_list.remove(b)
                            pygame.mixer.Sound.play(explosion_sound)
                            if e['health'] <= 0:
                                # 10% chance of a powerup
                                if random.random() < 0.10:
                                    powerups.append(pygame.Rect(e['rect'].x + 10, e['rect'].y, 30, 30))

                                # 2% chance of health bonus
                                if random.random() < 0.20:
                                    shared_health = min(shared_health + 1, 100)  # Cap at 50 max health

        # Enemy Fire
        enemy_fire_counter += 1
        if enemy_fire_counter >= enemy_cooldown:
            shooters = [e for e in enemies if e['health'] > 0]
            if shooters:
                for shooter in random.sample(shooters, min(3, len(shooters))):
                    ex = shooter['rect'].centerx
                    ey = shooter['rect'].bottom
                    etype = shooter['type']

                    if etype == "enemy":
                        enemy_bullets.append({'rect': pygame.Rect(ex, ey, 5, 15), 'dx': 0})

                    elif etype == "enemy1":
                        enemy_bullets.append({'rect': pygame.Rect(ex - 8, ey, 5, 15), 'dx': 0})
                        enemy_bullets.append({'rect': pygame.Rect(ex + 8, ey, 5, 15), 'dx': 0})

                    elif etype == "enemy2":
                        enemy_bullets.append({'rect': pygame.Rect(ex - 5, ey, 5, 15), 'dx': -2})
                        enemy_bullets.append({'rect': pygame.Rect(ex + 5, ey, 5, 15), 'dx': 2})

                    pygame.mixer.Sound.play(beam_sound)

            enemy_fire_counter = 0

        # Boss Fire
        if boss:
            if wave == 10:
                pass  # no bullets, laser only
            else:
                boss_fire_timer += 1
                if boss_fire_timer >= boss_fire_cooldown:
                    bx = boss['rect'].centerx
                    by = boss['rect'].bottom
                    # Fire 4 bullets in a wider spread
                    boss_bullets.append(BossBullet(pygame.Rect(bx - 5, by, 10, 20), 0, 6))
                    boss_bullets.append(BossBullet(pygame.Rect(bx - 20, by, 10, 20), -2, 6))
                    boss_bullets.append(BossBullet(pygame.Rect(bx + 20, by, 10, 20), 2, 6))
                    boss_bullets.append(BossBullet(pygame.Rect(bx - 40, by, 10, 20), -3, 6))
                    pygame.mixer.Sound.play(beam_sound)
                    boss_fire_timer = 0

        # Boss1 (wave 10) special laser
        if boss and wave == 10:
            laser_timer += 1

            # Activate laser
            if not laser_active and laser_timer >= laser_cooldown:
                laser_active = True
                laser_timer = 0
                laser_duration = random.randint(300, 600)  # 5–10 seconds
                laser_speed = random.choice([0.3, 0.5, 0.7])  # slower spin
                if random.random() < 0.4:  # 40% chance to reverse direction
                    laser_dir *= -1

                # Randomly choose 1–4 lasers only once
                num_lasers = random.randint(1, 4)

            # Deactivate laser after duration
            elif laser_active and laser_timer >= laser_duration:
                laser_active = False
                laser_timer = 0

            if laser_active:
                # Update the base rotation angle
                laser_angle = (laser_angle + laser_speed * laser_dir) % 360
                center = boss['rect'].center
                length = max(WIDTH, HEIGHT)

                # Function to calculate distance from point to line
                def point_line_distance(px, py, x1, y1, x2, y2):
                    num = abs((y2 - y1) * px - (x2 - x1) * py + x2 * y1 - y2 * x1)
                    den = math.hypot(x2 - x1, y2 - y1)
                    return num / den if den != 0 else 9999

                # Draw lasers in a circular pattern around boss
                for i in range(num_lasers):
                    angle = (laser_angle + i * (360 / num_lasers)) % 360
                    rad = math.radians(angle)
                    end_x = center[0] + math.cos(rad) * length
                    end_y = center[1] + math.sin(rad) * length
                    opp_x = center[0] - math.cos(rad) * length
                    opp_y = center[1] - math.sin(rad) * length

                    # Draw laser
                    pygame.draw.line(screen, RED, center, (end_x, end_y), 8)
                    pygame.draw.line(screen, RED, center, (opp_x, opp_y), 8)

                    # Damage players
                    for player in [player1] + ([player2] if players_enabled == 2 else []):
                        px, py = player.center
                        dist = point_line_distance(px, py, end_x, end_y, opp_x, opp_y)
                        if dist < 10:  # 10px threshold
                            # Player 1 damage
                            if player1_damage_cooldown == 0 and player == player1:
                                shared_health -= 0.20
                                player1_damage_cooldown = DAMAGE_COOLDOWN_TIME

                            # Player 2 damage if enabled
                            if players_enabled == 2 and player2_damage_cooldown == 0 and player == player2:
                                shared_health -= 0.20
                                player2_damage_cooldown = DAMAGE_COOLDOWN_TIME
        if boss and wave == 15:
            if boss_ai is None:
                boss_ai = Boss2AI(boss['rect'], WIDTH, HEIGHT)

            p_positions = [player1.center, player2.center if players_enabled == 2 else None]
            prev1 = globals().get('prev_player1_center', player1.center)
            prev2 = globals().get('prev_player2_center', player2.center)
            p_vels = [(player1.centerx - prev1[0], player1.centery - prev1[1]),
                    (player2.centerx - prev2[0], player2.centery - prev2[1]) if players_enabled == 2 else (0, 0)]

            player_bullets_lists = [player1_bullets]
            if players_enabled == 2:
                player_bullets_lists.append(player2_bullets)

            shots = boss_ai.update(p_positions, p_vels, [player1, player2], players_enabled, player_bullets_lists)
            boss['rect'] = boss_ai.rect.copy()

            for sx, sy, svx, svy in shots:
                bb_rect = pygame.Rect(int(sx - 5), int(sy - 5), 10, 10)
                boss_bullets.append(BossBullet(bb_rect, svx, svy))
    
        # Enemy bullets
        for eb in enemy_bullets[:]:
            rect = eb['rect']
            rect.y += 8
            rect.x += eb['dx']

            if rect.top > HEIGHT:
                enemy_bullets.remove(eb)
            elif rect.colliderect(player1) or (players_enabled == 2 and rect.colliderect(player2)):
                shared_health -= 1
                enemy_bullets.remove(eb)

        for bb in boss_bullets[:]:
            bb.rect.x += bb.dx
            bb.rect.y += bb.dy
            if bb.rect.left <= 0 or bb.rect.right >= WIDTH:
                if bb.ricochet > 0:
                    bb.dx *= -1
                    bb.ricochet -= 1
            if bb.rect.top <= 0 or bb.rect.bottom >= HEIGHT:
                if bb.ricochet > 0:
                    bb.dy *= -1
                    bb.ricochet -= 1
            if bb.rect.colliderect(player1) or (players_enabled == 2 and bb.rect.colliderect(player2)):
                shared_health -= 1
                boss_bullets.remove(bb)
            elif bb.rect.top > HEIGHT:
                boss_bullets.remove(bb)

        for pu in powerups[:]:
            pu.y += 5
            screen.blit(powerup_img, pu.topleft)
            if pu.colliderect(player1):
                double_fire_timer1 = FPS * 5
                powerups.remove(pu)
            elif players_enabled == 2 and pu.colliderect(player2):
                double_fire_timer2 = FPS * 5
                powerups.remove(pu)

        if all(e['health'] <= 0 for e in enemies) and not boss:
            wave += 1
            # Clear all bullets and powerups to prevent leftover projectiles
            player1_bullets.clear()
            player2_bullets.clear()
            enemy_bullets.clear()
            boss_bullets.clear()
            powerups.clear()

            game_state = FINISHED if wave > 15 else NEXT_WAVE
            wave_timer = 60

        if shared_health <= 0:
            pygame.mixer.Sound.play(loss_sound)
            player1.x, player1.y = WIDTH // 2 - 50, HEIGHT - 60
            player2.x, player2.y = WIDTH // 2 + 50, HEIGHT - 60
            player1_bullets.clear()
            player2_bullets.clear()
            enemy_bullets.clear()
            boss_bullets.clear()
            powerups.clear()
            game_state = GAME_OVER

        if boss:
            if wave == 10:  # Boss1
                if 'move_dir' not in boss:
                    boss['move_dir'] = [random.choice([-1, 1]), random.choice([-1, 1])]
                boss['rect'].x += boss['move_dir'][0] * 4
                boss['rect'].y += boss['move_dir'][1] * 3

                # Bounce off all walls (full window)
                if boss['rect'].left <= 0 or boss['rect'].right >= WIDTH:
                    boss['move_dir'][0] *= -1
                if boss['rect'].top <= 0 or boss['rect'].bottom >= HEIGHT:
                    boss['move_dir'][1] *= -1

                # Damage players if boss touches them
                if boss['rect'].colliderect(player1):
                    shared_health -= 1
                if players_enabled == 2 and boss['rect'].colliderect(player2):
                    shared_health -= 1

            else:
                # Normal boss movement
                boss['rect'].x += boss_move_dir * 4
                if boss['rect'].left <= 0 or boss['rect'].right >= WIDTH:
                    boss_move_dir *= -1

        draw_player(player1, GREEN)
        if players_enabled == 2:
            draw_player(player2, YELLOW)

        # Move each enemy individually around its orig_x
        for e in enemies:
            if e['health'] <= 0:
                continue
            max_offset = 30  # pixels from original position
            e['rect'].x += enemy_speed_x * e['move_dir']
            
            # Bounce back at limits
            if e['rect'].x > e['orig_x'] + max_offset:
                e['move_dir'] = -1
            elif e['rect'].x < e['orig_x'] - max_offset:
                e['move_dir'] = 1

        draw_enemies()
        draw_boss()
        draw_health()

        # Player bullets
        for b in player1_bullets:
            pygame.draw.rect(screen, GREEN, b)
        for b in player2_bullets:
            pygame.draw.rect(screen, YELLOW, b)

        # Enemy bullets
        for eb in enemy_bullets:
            pygame.draw.rect(screen, RED, eb['rect'])

        # Boss bullets (round)
        for bb in boss_bullets:
            pygame.draw.circle(screen, YELLOW, bb.rect.center, 6)
        
        # --- Laser Update & Draw ---
        for laser in lasers[:]:
            if not laser['active']:
                # Countdown warning phase
                laser['timer'] -= 1
                color = (255, 255, 0)
                countdown = math.ceil(laser['timer'] / 60)

                if laser['orientation'] == "vertical":
                    pygame.draw.line(screen, color, (laser['pos'], 0), (laser['pos'], HEIGHT + LASER_THICKNESS), LASER_THICKNESS)
                    text = font.render(str(countdown), True, color)
                    screen.blit(text, (laser['pos'] - 10, 50))
                else:
                    pygame.draw.line(screen, color, (0, laser['pos']), (WIDTH + LASER_THICKNESS, laser['pos']), LASER_THICKNESS)
                    text = font.render(str(countdown), True, color)
                    screen.blit(text, (WIDTH // 2 - 10, laser['pos'] - 10))

                if laser['timer'] <= 0:
                    laser['active'] = True
                    laser['timer'] = LASER_ACTIVE_TIME

            else:
                # Active (damage) phase
                color = (255, 0, 0)
                if laser['orientation'] == "vertical":
                    pygame.draw.line(screen, color, (laser['pos'], 0), (laser['pos'], HEIGHT), LASER_THICKNESS)
                    if player1.left < laser['pos'] < player1.right:
                        if player1_damage_cooldown == 0:
                            shared_health -= 1
                            player1_damage_cooldown = DAMAGE_COOLDOWN_TIME
                    if players_enabled == 2 and player2.left < laser['pos'] < player2.right:
                        if player2_damage_cooldown == 0:
                            shared_health -= 1
                            player2_damage_cooldown = DAMAGE_COOLDOWN_TIME
                else:
                    pygame.draw.line(screen, color, (0, laser['pos']), (WIDTH, laser['pos']), LASER_THICKNESS)
                    if player1.top < laser['pos'] < player1.bottom:
                        if player1_damage_cooldown == 0:
                            shared_health -= 1
                            player1_damage_cooldown = DAMAGE_COOLDOWN_TIME
                    if players_enabled == 2 and player2.top < laser['pos'] < player2.bottom:
                        if player2_damage_cooldown == 0:
                            shared_health -= 1
                            player2_damage_cooldown = DAMAGE_COOLDOWN_TIME

                laser['timer'] -= 1
                if laser['timer'] <= 0:
                    lasers.remove(laser)

    # Decrement damage cooldowns
    if player1_damage_cooldown > 0:
        player1_damage_cooldown -= 1
    if players_enabled == 2 and player2_damage_cooldown > 0:
        player2_damage_cooldown -= 1
    prev_player1_center = player1.center
    if players_enabled == 2:
        prev_player2_center = player2.center    

    pygame.display.flip()
    
    pygame.display.flip()

pygame.quit()
sys.exit()
