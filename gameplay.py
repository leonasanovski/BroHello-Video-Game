import pygame
import sys
import os
import random

blood_particles = []


class Box:
    def __init__(self, x, y, image):
        self.rect = pygame.Rect(x, y, 45, 45)
        self.image = pygame.transform.scale(image, (45, 45))
        self.velocity_y = 2
        self.landed = False

    def update(self, platforms):
        if not self.landed:
            self.rect.y += self.velocity_y

            for px, py, pw, ph in platforms:
                platform_rect = pygame.Rect(px, py, pw, ph)
                if self.rect.colliderect(platform_rect) and self.velocity_y >= 0:
                    if self.rect.bottom - self.velocity_y <= platform_rect.top:
                        self.rect.bottom = platform_rect.top
                        self.velocity_y = 0
                        self.landed = True

    def draw(self):
        screen.blit(self.image, (self.rect.x, self.rect.y))

    def apply_effect(self, player):
        if random.random() < 0.15 and player.grenade_count < player.max_grenades:
            player.grenade_count += 1
        else:
            player.change_random_skin()


class Player:
    weapon_fire_rates = {
        "gun": 400,
        "sniper": 1200,
        "smg": 100,
        "ak": 200,
        "m4": 200,
        "shotgun": 600
    }
    weapon_damage = {"gun": 2, "sniper": 23, "smg": 3, "ak": 6, "m4": 5, "shotgun": 15}
    weapon_ammo = {"gun": 15, "sniper": 2, "smg": 28, "ak": 30, "m4": 30, "shotgun": 6}
    ultimate_magics = ["Shield", "Jump Boost", "Damage Boost"]

    def __init__(self, x, y, controls, skin_name, player_skins, bullet_image, hud_image):
        self.initial_x = x
        self.initial_y = y
        self.rect = pygame.Rect(x, y, 50, 50)
        self.velocity_y = 0
        self.speed = 5
        self.on_ground = False
        self.controls = controls
        self.direction = "left"
        self.bullets = []
        self.bullet_image = bullet_image
        self.last_shot_time = 0
        self.shooting = False
        self.health = 100
        self.ammo = self.weapon_ammo.copy()
        self.hud_image = pygame.image.load(hud_image)
        self.hud_image = pygame.transform.scale(self.hud_image, (170, 130))
        self.original_jump_strength = -12
        self.shield_active = False

        self.dust_image = pygame.image.load("gameplay_effects_images/landing_dust.png")
        self.dust_image = pygame.transform.scale(self.dust_image, (35, 22))
        self.show_dust = False
        self.dust_timer = 0

        self.hit_timer = 0
        self.grenades = []
        self.max_grenades = 2
        self.grenade_count = 0

        self.ultimate_charge = 0
        self.ultimate_ready = False
        self.ultimate_active = False
        self.ultimate_type = None
        self.ultimate_timer = 0

        self.skins = {}
        weapon_types = ["gun", "sniper", "ak", "m4", "shotgun", "smg"]

        self.weapon_sounds = {
            "gun": pygame.mixer.Sound("weapon_sounds/gun.mp3"),
            "sniper": pygame.mixer.Sound("weapon_sounds/sniper.mp3"),
            "smg": pygame.mixer.Sound("weapon_sounds/smg.mp3"),
            "ak": pygame.mixer.Sound("weapon_sounds/ak.mp3"),
            "m4": pygame.mixer.Sound("weapon_sounds/m4.mp3"),
            "shotgun": pygame.mixer.Sound("weapon_sounds/shotgun.mp3"),
            "weapon_change": pygame.mixer.Sound("weapon_sounds/weapon_change.mp3")
        }

        for sound in self.weapon_sounds.values():
            sound.set_volume(0.5)

        for weapon in weapon_types:
            weapon_skin = f"{skin_name}_{weapon}"
            weapon_skin_path = os.path.join(skins_folder, "weapons", f"{weapon_skin}.png")
            if os.path.exists(weapon_skin_path):
                self.skins[weapon] = pygame.transform.scale(pygame.image.load(weapon_skin_path), (100, 70))

        if not self.skins:
            self.skins["gun"] = pygame.transform.scale(player_skins.get(skin_name, list(player_skins.values())[0]),
                                                       (100, 70))
        self.current_skin = "gun"
        self.skin = self.skins[self.current_skin]

    def activate_ultimate(self):
        if self.ultimate_ready and not self.ultimate_active:
            self.ultimate_active = True
            self.ultimate_timer = 360
            self.ultimate_ready = False
            self.ultimate_charge = 0
            if self.ultimate_type == "Jump Boost":
                self.original_jump_strength *= 1.5
            elif self.ultimate_type == "Damage Boost":
                for weapon in self.weapon_damage:
                    self.weapon_damage[weapon] *= 2
            elif self.ultimate_type == "Shield":
                self.shield_active = True

    def update_ultimate(self):
        if not self.ultimate_ready and not self.ultimate_active:
            self.ultimate_charge += 1
            if self.ultimate_charge >= 900:
                self.ultimate_ready = True
                self.ultimate_type = random.choice(self.ultimate_magics)

        if self.ultimate_active:
            self.ultimate_timer -= 1
            if self.ultimate_timer <= 0:
                self.ultimate_active = False
                self.ultimate_charge = 0
                if self.ultimate_type == "Jump Boost":
                    self.original_jump_strength = int(self.original_jump_strength / 1.5)
                elif self.ultimate_type == "Damage Boost":
                    for weapon in self.weapon_damage:
                        self.weapon_damage[weapon] = int(self.weapon_damage[weapon] / 2)
                elif self.ultimate_type == "Shield":
                    self.shield_active = False

    def take_damage(self, damage):
        if not self.shield_active:
            self.health -= damage
            if self.health < 0:
                self.health = 0
            self.emit_blood()
            self.hit_timer = pygame.time.get_ticks()

    def draw_hud(self, position):
        global ultimate_icon
        x, y = position
        screen.blit(self.hud_image, (x, y))
        screen.blit(self.skin, (x, y + 16))

        font = pygame.font.Font(None, 20)

        health_text = font.render(str(self.health), True, (255, 255, 255))
        screen.blit(health_text, (x + 124, y + 35))

        font = pygame.font.Font(None, 23)
        ammo_text = font.render(str(self.ammo[self.current_skin]), True, (255, 255, 255))
        screen.blit(ammo_text, (x + 130, y + 68))

        grenade_icon = pygame.image.load("hud_images/grenade.png")
        grenade_icon = pygame.transform.scale(grenade_icon, (20, 20))
        for i in range(self.grenade_count):
            screen.blit(grenade_icon, (x + 110 + (i * 25), y + 100))

        pygame.draw.rect(screen, (255, 255, 0), (x, y + 140, 100 * (self.ultimate_charge / 900), 10))

        if self.ultimate_ready:
            if self.ultimate_type == "Shield":
                ultimate_icon = pygame.image.load("hud_images/ultimate_images/shield.png")
            elif self.ultimate_type == "Jump Boost":
                ultimate_icon = pygame.image.load("hud_images/ultimate_images/jump_boost.png")
            elif self.ultimate_type == "Damage Boost":
                ultimate_icon = pygame.image.load("hud_images/ultimate_images/damage.png")

            ultimate_icon = pygame.transform.scale(ultimate_icon, (30, 30))
            screen.blit(ultimate_icon, (x + 115, y + 130))

    def change_random_skin(self):
        available_weapons = list(self.skins.keys())
        available_weapons.remove(self.current_skin)
        if available_weapons:
            self.current_skin = random.choice(available_weapons)
            self.skin = self.skins[self.current_skin]
            self.ammo[self.current_skin] = self.weapon_ammo[self.current_skin]

    def respawn(self):
        self.rect.x = self.initial_x
        self.rect.y = self.initial_y
        self.velocity_y = 0
        self.health -= 10
        if self.health < 0:
            self.health = 0

    def shoot(self):
        current_time = pygame.time.get_ticks()
        fire_rate = self.weapon_fire_rates.get(self.current_skin, 400)

        if self.shooting and current_time - self.last_shot_time >= fire_rate:
            if self.ammo[self.current_skin] > 0:
                self.last_shot_time = current_time
                bullet_x = self.rect.right if self.direction == "right" else self.rect.left - 20
                bullet_y = self.rect.y + 20
                bullet_speed = 10
                bullet = Bullet(bullet_x, bullet_y, self.direction, self.bullet_image, bullet_speed, self.current_skin)
                self.bullets.append(bullet)
                self.ammo[self.current_skin] -= 1

                self.weapon_sounds[self.current_skin].play()
            else:
                self.weapon_sounds['weapon_change'].play()
                self.current_skin = "gun"
                self.skin = self.skins[self.current_skin]
                self.ammo[self.current_skin] = self.weapon_ammo[self.current_skin]

    def move(self, platforms):
        keys = pygame.key.get_pressed()
        was_on_ground = self.on_ground

        if keys[self.controls['left']]:
            self.rect.x -= 5
            self.direction = "left"
        if keys[self.controls['right']]:
            self.rect.x += 5
            self.direction = "right"
        if keys[self.controls['jump']] and self.on_ground:
            self.velocity_y = self.original_jump_strength
            self.on_ground = False
        self.velocity_y += 0.5
        self.rect.y += self.velocity_y

        self.on_ground = False
        for px, py, pw, ph in platforms:
            plat_rect = pygame.Rect(px, py, pw, ph)
            if self.rect.colliderect(plat_rect) and self.velocity_y >= 0:
                if self.rect.left >= plat_rect.left - 50 and self.rect.right <= plat_rect.right + 10:
                    if self.rect.bottom - self.velocity_y >= plat_rect.top:
                        self.rect.bottom = plat_rect.top
                        self.velocity_y = 0
                        self.on_ground = True
        if not was_on_ground and self.on_ground:
            self.show_dust = True
            self.dust_timer = 15

    def draw_health_bar(self):
        color = (255, 0, 0)
        pygame.draw.rect(screen, color,
                         (self.rect.x + 20, self.rect.y - 20, self.health // 2, 10))

    def update(self):
        self.update_ultimate()
        if self.rect.top > HEIGHT:
            self.respawn()

    def draw(self):
        current_time = pygame.time.get_ticks()
        img = self.skin.copy()

        if self.hit_timer and current_time - self.hit_timer < 300:
            img.fill((255, 0, 0, 50), special_flags=pygame.BLEND_RGBA_MULT)
            self.emit_blood()
        elif self.shield_active:
            img.fill((144, 213, 255, 80), special_flags=pygame.BLEND_RGBA_MULT)

        if self.direction == "right":
            img = pygame.transform.flip(img, True, False)

        screen.blit(img, (self.rect.x - 10, self.rect.y - 10))
        if self.show_dust and self.on_ground:
            dust_x = self.rect.x + 18
            dust_y = self.rect.bottom - 5
            dust_image_scaled = pygame.transform.scale(self.dust_image, (self.rect.width, 25))

            screen.blit(dust_image_scaled, (dust_x, dust_y))
            self.dust_timer -= 1
            if self.dust_timer <= 0:
                self.show_dust = False
        self.draw_health_bar()

        for bullet in self.bullets:
            bullet.draw()
        for grenade in self.grenades:
            grenade.draw(screen)

    def emit_blood(self):
        num_particles = random.randint(2, 3)
        for _ in range(num_particles):
            blood_x = self.rect.centerx + 15
            blood_y = self.rect.centery + 10

            blood_particle = {
                "x": blood_x,
                "y": blood_y,
                "size": random.randint(2, 5),
                "lifespan": random.randint(12, 16),
                "velocity_x": random.uniform(-0.3, 0.3),
                "velocity_y": random.uniform(0.8, 1.5)
            }
            blood_particles.append(blood_particle)

    def throw_grenade(self):
        if self.grenade_count > 0:
            grenade = Grenade(self.rect.centerx, self.rect.top, "right" if self.direction == "right" else "left")

            self.grenades.append(grenade)
            self.grenade_count -= 1

    def update_grenades(self, platforms, player1, player2):
        for grenade in self.grenades[:]:
            if not grenade.update(platforms):
                grenade.explode(player1, player2)
                self.grenades.remove(grenade)


def update_blood_particles():
    for particle in blood_particles[:]:
        particle["x"] += particle["velocity_x"]
        particle["y"] += particle["velocity_y"]
        particle["velocity_y"] += 0.05
        if particle["size"] > 1:
            particle["size"] -= 0.1
        pygame.draw.circle(screen, (180, 0, 0), (int(particle["x"]), int(particle["y"])), max(1, int(particle["size"])))

        particle["lifespan"] -= 1
        if particle["lifespan"] <= 0:
            blood_particles.remove(particle)


class Bullet:
    def __init__(self, x, y, direction, bullet_image, speed, weapon_type):
        if weapon_type == "shotgun":
            self.image = pygame.image.load("gameplay_effects_images/shotgun_bullet.png")
            if direction == "left":
                self.image = pygame.transform.flip(self.image, True, False)
            self.rect = pygame.Rect(x, y - 10, 20, 10)
        else:
            self.image = pygame.transform.scale(bullet_image, (20, 10))
            self.rect = pygame.Rect(x, y + 20, 20, 10)
        self.speed = speed if direction == "right" else -speed
        self.weapon_type = weapon_type
        self.start_x = x

    def update(self):
        self.rect.x += self.speed
        if self.weapon_type == "shotgun" and abs(self.rect.x - self.start_x) >= 120:
            return False

        return True

    def draw(self):
        screen.blit(self.image, (self.rect.x, self.rect.y))


class Grenade:
    def __init__(self, x, y, direction):
        self.image = pygame.image.load("hud_images/grenade.png")
        self.image = pygame.transform.scale(self.image, (25, 25))
        self.explosion_image = pygame.image.load("gameplay_effects_images/bomb_explosion_effect.png")
        self.explosion_image = pygame.transform.scale(self.explosion_image, (50, 50))
        self.rect = pygame.Rect(x, y, 25, 25)
        self.direction = direction
        self.vel_x = 8 if direction == "right" else -8
        self.vel_y = -12
        self.gravity = 0.5
        self.timer = 60
        self.exploded = False
        self.explosion_timer = 7
        self.explosion_position = (0, 0)

    def update(self, platforms):
        if not self.exploded:
            self.vel_y += self.gravity
            self.rect.x += self.vel_x
            self.rect.y += self.vel_y
            self.timer -= 1

            for px, py, pw, ph in platforms:
                platform_rect = pygame.Rect(px, py, pw, ph)
                if self.rect.colliderect(platform_rect):
                    self.exploded = True
                    self.explosion_position = (self.rect.x - 12, self.rect.y - 12)
                    return True
        else:
            self.explosion_timer -= 1
            if self.explosion_timer <= 0:
                return False

        return self.timer > 0

    def explode(self, player1, player2):
        self.exploded = True
        self.explosion_position = (self.rect.x - 12, self.rect.y - 12)
        weapon_change_sound = pygame.mixer.Sound("weapon_sounds/grenade.mp3")
        weapon_change_sound.set_volume(0.2)
        weapon_change_sound.play()
        if self.rect.colliderect(player1.rect):
            player1.take_damage(25)
        elif self.rect.colliderect(player2.rect):
            player2.take_damage(20)

    def draw(self, screen):
        if self.exploded and self.explosion_timer > 0:
            screen.blit(self.explosion_image, self.explosion_position)
        else:
            screen.blit(self.image, (self.rect.x, self.rect.y))


pygame.init()
WIDTH, HEIGHT = 1400, 788
screen = pygame.display.set_mode((WIDTH, HEIGHT))

map_files = ["maps/map1.png", "maps/map2.png", "maps/map3.png"]
map_images = [pygame.image.load(m).convert_alpha() for m in map_files]
map_images = [pygame.transform.scale(m, (WIDTH, HEIGHT)) for m in map_images]

platforms = [
    [(147, 440, 230, 25), (479, 346, 463, 25), (1040, 440, 230, 25), (224, 552, 360, 236), (830, 553, 357, 235)],
    [(112, 524, 250, 38), (570, 380, 243, 43), (1140, 427, 221, 123), (312, 674, 743, 109), (1223, 557, 130, 130),
     (868, 524, 166, 36)],
    [(340, 309, 280, 55), (833, 305, 280, 55), (1083, 459, 275, 50), (114, 463, 275, 50), (183, 685, 1075, 118)]
]

skins_folder = "skins"
weapons_folder = os.path.join(skins_folder, "weapons")
skin_heads = sorted([f for f in os.listdir(skins_folder) if f.endswith(".png")])
player_skins = {}
for head_skin in skin_heads:
    base_name = os.path.splitext(head_skin)[0]
    img = pygame.image.load(os.path.join(skins_folder, head_skin))
    player_skins[base_name] = pygame.transform.scale(img, (50, 50))

    for weapon in ["gun", "sniper", "ak", "m4", "shotgun", "smg"]:
        weapon_skin_path = os.path.join(weapons_folder, f"{base_name}_{weapon}.png")
        if os.path.exists(weapon_skin_path):
            player_skins[f"{base_name}_{weapon}"] = pygame.transform.scale(pygame.image.load(weapon_skin_path),
                                                                           (50, 50))

box_image = pygame.image.load("gameplay_effects_images/boxo.png")
box_image = pygame.transform.scale(box_image, (50, 50))

boxes = []
next_box_time = random.randint(5 * 60, 15 * 60)


def show_game_over_screen(winner, selected_map, player1_skin_name, player2_skin_name, player_skins):
    pygame.mixer.music.stop()
    game_snapshot = screen.copy()
    pygame.mixer.music.load("music/ending_screen_song.mp3")
    pygame.mixer.music.set_volume(0.2)
    pygame.mixer.music.play(-1)
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))

    title_font = pygame.font.Font(None, 100)
    result_font = pygame.font.Font(None, 55)
    label_font = pygame.font.Font(None, 50)

    if winner == 1:
        winning_skin = player_skins[player1_skin_name]
        losing_skin = player_skins[player2_skin_name]
        winner_text = "Winner"
        loser_text = "Loser"
        player1_label = "Player 1"
        player2_label = "Player 2"
    else:
        winning_skin = player_skins[player2_skin_name]
        losing_skin = player_skins[player1_skin_name]
        winner_text = "Winner"
        loser_text = "Loser"
        player1_label = "Player 2"
        player2_label = "Player 1"

    skin_size = (170, 200)
    winning_skin = pygame.transform.scale(winning_skin, skin_size)
    losing_skin = pygame.transform.scale(losing_skin, skin_size)

    losing_skin = losing_skin.copy()
    arr = pygame.surfarray.pixels3d(losing_skin)
    grayscale = (arr[:, :, 0] * 0.3 + arr[:, :, 1] * 0.59 + arr[:, :, 2] * 0.11).astype("uint8")
    arr[:, :, 0] = grayscale
    arr[:, :, 1] = grayscale
    arr[:, :, 2] = grayscale
    del arr

    panel_width, panel_height = 650, 400
    panel_x, panel_y = WIDTH // 2 - panel_width // 2, HEIGHT // 2 - panel_height // 2 - 20

    player_gap = 70
    winner_x = panel_x + (panel_width // 2) - skin_size[0] - (player_gap // 2)
    loser_x = panel_x + (panel_width // 2) + (player_gap // 2)
    skin_y = panel_y + 120

    result_y = skin_y - 60
    label_y = skin_y + skin_size[1] - 10

    button_width, button_height = 260, 90
    button_spacing = 40
    button_total_width = (2 * button_width) + button_spacing
    button_x_start = WIDTH // 2 - button_total_width // 2
    button_y = panel_y + panel_height - 10

    buttons = {
        "restart": pygame.Rect(button_x_start, button_y, button_width, button_height),
        "main_menu": pygame.Rect(button_x_start + button_width + button_spacing, button_y, button_width, button_height),
    }

    running = True
    while running:
        screen.blit(game_snapshot, (0, 0))
        screen.blit(overlay, (0, 0))
        title_text = "Game Over"
        shadow_color = (0, 255, 255)
        main_color = (255, 140, 0)

        title_surface_shadow = title_font.render(title_text, True, shadow_color)
        title_surface_main = title_font.render(title_text, True, main_color)

        title_x = WIDTH // 2 - title_surface_main.get_width() // 2
        title_y = 60

        screen.blit(title_surface_shadow, (title_x + 4, title_y + 4))
        screen.blit(title_surface_main, (title_x, title_y))

        pygame.draw.rect(screen, (80, 0, 120), (panel_x, panel_y, panel_width, panel_height), border_radius=30)
        pygame.draw.rect(screen, (255, 140, 0), (panel_x, panel_y, panel_width, panel_height), width=6,
                         border_radius=30)

        screen.blit(winning_skin, (winner_x, skin_y))
        screen.blit(losing_skin, (loser_x, skin_y))

        winner_text_surface = result_font.render(winner_text, True, (0, 200, 0))
        loser_text_surface = result_font.render(loser_text, True, (227, 34, 39))

        screen.blit(winner_text_surface,
                    (winner_x + (skin_size[0] // 2) - (winner_text_surface.get_width() // 2), result_y))
        screen.blit(loser_text_surface,
                    (loser_x + (skin_size[0] // 2) - (loser_text_surface.get_width() // 2), result_y))

        player1_label_surface = label_font.render(player1_label, True, (255, 255, 255))
        player2_label_surface = label_font.render(player2_label, True, (255, 255, 255))

        screen.blit(player1_label_surface,
                    (winner_x + (skin_size[0] // 2) - (player1_label_surface.get_width() // 2), label_y + 30))
        screen.blit(player2_label_surface,
                    (loser_x + (skin_size[0] // 2) - (player2_label_surface.get_width() // 2), label_y + 30))

        mouse = pygame.mouse.get_pos()
        button_font = pygame.font.Font(None, 60)

        for key, rect in buttons.items():
            button_color = (255, 180, 50) if rect.collidepoint(mouse) else (255, 140, 0)
            pygame.draw.rect(screen, button_color, rect, border_radius=35)
            pygame.draw.rect(screen, (200, 100, 0), rect, width=5, border_radius=35)

            button_text = key.replace("_", " ").title()
            text_surface = button_font.render(button_text, True, (255, 255, 255))
            text_x = rect.x + (rect.width - text_surface.get_width()) // 2
            text_y = rect.y + (rect.height - text_surface.get_height()) // 2
            screen.blit(text_surface, (text_x, text_y))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if buttons["restart"].collidepoint(event.pos):
                    game_loop(selected_map, player1_skin_name, player2_skin_name, player_skins)
                if buttons["main_menu"].collidepoint(event.pos):
                    from selection import start_screen
                    start_screen()


def game_loop(selected_map, player1_skin_name, player2_skin_name, player_skins):
    pygame.mixer.music.load("music/main_song.mp3")
    pygame.mixer.music.set_volume(0.2)
    pygame.mixer.music.play(-1)

    global next_box_time, boxes

    clock = pygame.time.Clock()
    bullet_image = pygame.image.load("gameplay_effects_images/bullet.png")
    controls_p1 = {
        'left': pygame.K_a,
        'right': pygame.K_d,
        'jump': pygame.K_w,
        'shoot': pygame.K_g,
        'throw_grenade': pygame.K_s,
        'ultimate': pygame.K_h
    }
    controls_p2 = {
        'left': pygame.K_LEFT,
        'right': pygame.K_RIGHT,
        'jump': pygame.K_UP,
        'shoot': pygame.K_BACKSPACE,
        'throw_grenade': pygame.K_DOWN,
        'ultimate': pygame.K_RETURN
    }

    player1 = Player(250, 100, controls_p1, player1_skin_name, player_skins, bullet_image, "hud_images/p1_s.png")
    player2 = Player(900, 100, controls_p2, player2_skin_name, player_skins, bullet_image, "hud_images/p2_s.png")

    boxes = []
    next_box_time = random.randint(1 * 60, 5 * 60)

    running = True
    frame_count = 0
    while running:
        screen.blit(map_images[selected_map], (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    pause_screen(selected_map, player1_skin_name, player2_skin_name, player_skins)
                if event.key == player1.controls['shoot']:
                    player1.shooting = True
                if event.key == player2.controls['shoot']:
                    player2.shooting = True
                if event.key == player1.controls['throw_grenade']:
                    player1.throw_grenade()
                if event.key == player2.controls['throw_grenade']:
                    player2.throw_grenade()
                if event.key == player1.controls['ultimate']:
                    player1.activate_ultimate()
                if event.key == player2.controls['ultimate']:
                    player2.activate_ultimate()

            if event.type == pygame.KEYUP:
                if event.key == player1.controls['shoot']:
                    player1.shooting = False
                if event.key == player2.controls['shoot']:
                    player2.shooting = False
        player1.update()
        player2.update()

        player1.shoot()
        player2.shoot()
        player1.move(platforms[selected_map])
        player2.move(platforms[selected_map])
        player1.draw()
        player2.draw()

        player1.draw_hud((20, 20))
        player2.draw_hud((WIDTH - 170, 20))

        player1.bullets = [bullet for bullet in player1.bullets if bullet.update()]
        player2.bullets = [bullet for bullet in player2.bullets if bullet.update()]

        player1.update()
        player2.update()

        player1.update_grenades(platforms[selected_map], player1, player2)
        player2.update_grenades(platforms[selected_map], player1, player2)
        if frame_count >= next_box_time and len(boxes) < 3:
            x_pos = random.randint(0, WIDTH - 50)
            boxes.append(Box(x_pos, 0, box_image))
            next_box_time = frame_count + random.randint(5 * 60, 15 * 60)

        for box in boxes[:]:
            box.update(platforms[selected_map])
            box.draw()
            if player1.rect.colliderect(box.rect):
                box.apply_effect(player1)
                boxes.remove(box)
            elif player2.rect.colliderect(box.rect):
                box.apply_effect(player2)
                boxes.remove(box)

        for bullet in player1.bullets[:]:
            bullet.update()
            if bullet.rect.colliderect(player2.rect):
                damage = player1.weapon_damage.get(player1.current_skin, 2)
                player2.take_damage(damage)
                player1.bullets.remove(bullet)

        for bullet in player2.bullets[:]:
            bullet.update()
            if bullet.rect.colliderect(player1.rect):
                damage = player2.weapon_damage.get(player2.current_skin, 2)
                player1.take_damage(damage)
                player2.bullets.remove(bullet)

        if player1.health <= 0:
            show_game_over_screen(2, selected_map, player1_skin_name, player2_skin_name, player_skins)
            return

        if player2.health <= 0:
            show_game_over_screen(1, selected_map, player1_skin_name, player2_skin_name, player_skins)
            return
        update_blood_particles()
        pygame.display.flip()
        clock.tick(60)
        frame_count += 1


def pause_screen(selected_map, player1_skin_name, player2_skin_name, player_skins):
    pygame.mixer.music.pause()

    game_snapshot = screen.copy()

    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((255, 255, 255, 80))

    button_width, button_height = 250, 90
    button_x = WIDTH // 2 - button_width // 2
    button_y_start = HEIGHT // 2 - 160
    button_spacing = 100

    buttons = {
        "continue": pygame.Rect(button_x, button_y_start, button_width, button_height),
        "restart": pygame.Rect(button_x, button_y_start + button_spacing, button_width, button_height),
        "main_menu": pygame.Rect(button_x, button_y_start + 2 * button_spacing, button_width, button_height),
        "quit": pygame.Rect(button_x, button_y_start + 3 * button_spacing, button_width, button_height)
    }

    running = True
    while running:
        screen.blit(game_snapshot, (0, 0))
        screen.blit(overlay, (0, 0))
        title_font = pygame.font.Font(None, 90)
        title_text = "Paused"

        shadow_color = (0, 255, 255)
        main_color = (255, 140, 0)

        title_surface_shadow = title_font.render(title_text, True, shadow_color)
        title_surface_main = title_font.render(title_text, True, main_color)

        title_x = WIDTH // 2 - title_surface_main.get_width() // 2
        title_y = 100

        screen.blit(title_surface_shadow, (title_x + 3, title_y + 3))
        screen.blit(title_surface_main, (title_x, title_y))

        mouse = pygame.mouse.get_pos()
        button_font = pygame.font.Font(None, 55)

        for key, rect in buttons.items():
            button_color = (255, 180, 50) if rect.collidepoint(mouse) else (255, 140, 0)

            pygame.draw.rect(screen, button_color, rect, border_radius=30)
            pygame.draw.rect(screen, (200, 100, 0), rect, width=4, border_radius=30)
            button_text = key.replace("_", " ").title()
            text_surface = button_font.render(button_text, True, (255, 255, 255))
            text_x = rect.x + (rect.width - text_surface.get_width()) // 2
            text_y = rect.y + (rect.height - text_surface.get_height()) // 2
            screen.blit(text_surface, (text_x, text_y))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if buttons["continue"].collidepoint(event.pos):
                    pygame.mixer.music.unpause()
                    return
                if buttons["restart"].collidepoint(event.pos):
                    pygame.mixer.music.unpause()
                    game_loop(selected_map, player1_skin_name, player2_skin_name, player_skins)
                if buttons["main_menu"].collidepoint(event.pos):
                    pygame.mixer.music.unpause()
                    from selection import start_screen
                    start_screen()
                if buttons["quit"].collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()
