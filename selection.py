import pygame
import sys
import os


pygame.init()
WIDTH, HEIGHT = 1400, 788
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Shooting Game")

bg_image = pygame.image.load("background.jpg")
bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))

logo_image = pygame.image.load("screens/start_screen/logo.png")
logo_image = pygame.transform.scale(logo_image, (400, 300))
button_start = pygame.image.load("screens/start_screen/start.png")
button_start = pygame.transform.scale(button_start, (180, 180))
button_settings = pygame.image.load("screens/start_screen/image.png")
button_settings = pygame.transform.scale(button_settings, (130, 130))
button_info = pygame.image.load("screens/start_screen/infp.png")
button_info = pygame.transform.scale(button_info, (130, 130))
button_credits = pygame.image.load("screens/start_screen/credits.png")
button_credits = pygame.transform.scale(button_credits, (100, 100))

overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
overlay.fill((0, 0, 0, 100))

title_font = pygame.font.Font(None, 80)

skins_folder = "skins"
default_folder = os.path.join(skins_folder, "default")
weapons_folder = os.path.join(skins_folder, "weapons")

skin_heads = sorted([f for f in os.listdir(default_folder) if f.endswith(".png")])
player_skins = {}

for head_skin in skin_heads:
    base_name = os.path.splitext(head_skin)[0]
    skin_path = os.path.join(default_folder, head_skin)

    try:
        img = pygame.image.load(skin_path).convert_alpha()
        player_skins[base_name] = img
    except pygame.error as e:
        print(f"Error loading {head_skin}: {e}")

player_weapons = {}
for base_name in player_skins.keys():
    weapon_path = os.path.join(weapons_folder, f"{base_name}_gun.png")

    if os.path.exists(weapon_path):
        try:
            weapon_img = pygame.image.load(weapon_path).convert_alpha()
            player_weapons[base_name] = weapon_img
        except pygame.error as e:
            print(f"Error loading weapon for {base_name}: {e}")
maps_folder = "maps"
map_files = sorted(os.listdir(maps_folder))
map_thumbnails = [pygame.image.load(os.path.join(maps_folder, img)) for img in map_files]
map_thumbnails = [pygame.transform.scale(map_img, (130, 130)) for map_img in map_thumbnails]

WHITE = (255, 255, 255)
BUTTON_COLOR = (20, 100, 20)
HOVER_COLOR = (50, 150, 50)
RED = (200, 50, 50)
DARK_RED = (150, 0, 0)

title_font = pygame.font.Font(None, 80)
button_font = pygame.font.Font(None, 40)

player1_index = list(player_skins.keys())[0]
player2_index = list(player_skins.keys())[0]
selected_map = None

pygame.init()
pygame.mixer.init()

pygame.mixer.music.load("music/selection_song.mp3")
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(-1)

button_click_sound = pygame.mixer.Sound("music/click_sound_effect.mp3")
button_click_sound.set_volume(0.7)


def change_skin(player, direction):
    global player1_index, player2_index
    skin_list = list(player_skins.keys())

    if player == 1:
        current_index = skin_list.index(player1_index)
        player1_index = skin_list[(current_index + direction) % len(skin_list)]
    elif player == 2:
        current_index = skin_list.index(player2_index)
        player2_index = skin_list[(current_index + direction) % len(skin_list)]


def character_select_screen():
    global player1_index, player2_index, selected_map
    selected_map = 0
    running = True

    panel_width, panel_height = 550, 400
    panel_x, panel_y = WIDTH // 2 - panel_width // 2, HEIGHT // 2 - panel_height // 2

    button_size = 100
    player_box_width = 220

    skin_size = (110, 125)

    arrow_button = pygame.image.load("screens/strelka.png")
    arrow_button = pygame.transform.scale(arrow_button, (button_size, button_size))
    left_arrow_button = pygame.transform.rotate(arrow_button, 180)

    while running:
        screen.blit(bg_image, (0, 0))
        screen.blit(overlay, (0, 0))

        title_surface_orange = title_font.render("SELECT YOUR CHARACTERS", True, (255, 140, 0))
        title_surface_cyan = title_font.render("SELECT YOUR CHARACTERS", True, (0, 255, 255))

        title_x = WIDTH // 2 - title_surface_orange.get_width() // 2
        screen.blit(title_surface_cyan, (title_x + 2, 120))
        screen.blit(title_surface_orange, (title_x, 118))

        pygame.draw.rect(screen, (80, 0, 120), (panel_x, panel_y - 15, panel_width, panel_height), border_radius=25)
        pygame.draw.rect(screen, (255, 140, 0), (panel_x, panel_y - 15
                                                 , panel_width, panel_height), width=5,
                         border_radius=25)

        pygame.draw.rect(screen, (180, 0, 180), (panel_x + 30, panel_y + 10, player_box_width, 40), border_radius=10)
        pygame.draw.rect(screen, (0, 180, 0),
                         (panel_x + panel_width - player_box_width - 30, panel_y + 10, player_box_width, 40),
                         border_radius=10)

        player1_label = button_font.render("PLAYER 1", True, (255, 255, 255))
        player2_label = button_font.render("PLAYER 2", True, (255, 255, 255))

        screen.blit(player1_label, (panel_x + 75, panel_y + 16))
        screen.blit(player2_label, (panel_x + panel_width - player_box_width + 20, panel_y + 17))

        pygame.draw.rect(screen, (50, 0, 100), (panel_x + 30, panel_y + 60, player_box_width, 230), border_radius=15)
        pygame.draw.rect(screen, (255, 140, 0), (panel_x + 30, panel_y + 60, player_box_width, 230), width=3,
                         border_radius=15)

        pygame.draw.rect(screen, (50, 0, 100),
                         (panel_x + panel_width - player_box_width - 30, panel_y + 60, player_box_width, 230),
                         border_radius=15)
        pygame.draw.rect(screen, (255, 140, 0),
                         (panel_x + panel_width - player_box_width - 30, panel_y + 60, player_box_width, 230), width=3,
                         border_radius=15)

        skin1 = pygame.transform.scale(player_skins[player1_index], skin_size)
        skin2 = pygame.transform.scale(player_skins[player2_index], skin_size)

        screen.blit(skin1, (panel_x + 85, panel_y + 105))
        screen.blit(skin2, (panel_x + panel_width - player_box_width + 25, panel_y + 105))

        if player1_index in player_weapons:
            weapon1 = pygame.transform.scale(player_weapons[player1_index], (skin_size[0] // 2, skin_size[1] // 2))

        if player2_index in player_weapons:
            weapon2 = pygame.transform.scale(player_weapons[player2_index], (skin_size[0] // 2, skin_size[1] // 2))

        left_arrow_rect_p1 = screen.blit(left_arrow_button, (panel_x + 50, panel_y + 280))
        right_arrow_rect_p1 = screen.blit(arrow_button, (panel_x + 130, panel_y + 280))

        left_arrow_rect_p2 = screen.blit(left_arrow_button,
                                         (panel_x + panel_width - player_box_width - 10, panel_y + 280))
        right_arrow_rect_p2 = screen.blit(arrow_button, (panel_x + panel_width - player_box_width + 70, panel_y + 280))

        draw_fancy_button("Back", panel_x - 150, panel_y + panel_height + 20, 150, 50, (255, 140, 0), (200, 100, 0),
                          start_screen)
        draw_fancy_button("Next", panel_x + panel_width + 20, panel_y + panel_height + 20, 150, 50, (180, 0, 180),
                          (120, 0, 120), map_select_screen)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()

                if left_arrow_rect_p1.collidepoint(mouse_pos):
                    change_skin(1, -1)
                elif right_arrow_rect_p1.collidepoint(mouse_pos):
                    change_skin(1, 1)
                elif left_arrow_rect_p2.collidepoint(mouse_pos):
                    change_skin(2, -1)
                elif right_arrow_rect_p2.collidepoint(mouse_pos):
                    change_skin(2, 1)


def change_map(direction):
    global selected_map
    selected_map = (selected_map + direction) % len(map_files)


def map_select_screen():
    global selected_map
    running = True

    panel_width, panel_height = 700, 450
    panel_x, panel_y = WIDTH // 2 - panel_width // 2, HEIGHT // 2 - panel_height // 2

    button_size = 80
    map_preview_size = (550, 350)

    arrow_button = pygame.image.load("screens/strelka.png")
    arrow_button = pygame.transform.scale(arrow_button, (button_size, button_size))
    left_arrow_button = pygame.transform.rotate(arrow_button, 180)

    full_star = pygame.image.load("screens/map_screen/star.png")
    full_star = pygame.transform.scale(full_star, (30, 30))

    empty_star = pygame.image.load("screens/map_screen/prazna_star.png")
    empty_star = pygame.transform.scale(empty_star, (30, 30))

    while running:
        screen.blit(bg_image, (0, 0))
        screen.blit(overlay, (0, 0))

        title_surface_orange = title_font.render("CHOOSE YOUR MAP", True, (255, 140, 0))
        title_surface_cyan = title_font.render("CHOOSE YOUR MAP", True, (0, 255, 255))

        title_x = WIDTH // 2 - title_surface_orange.get_width() // 2
        screen.blit(title_surface_cyan, (title_x + 2, 120))
        screen.blit(title_surface_orange, (title_x, 118))

        pygame.draw.rect(screen, (80, 0, 120), (panel_x, panel_y, panel_width, panel_height), border_radius=25)
        pygame.draw.rect(screen, (255, 140, 0), (panel_x, panel_y, panel_width, panel_height), width=5,
                         border_radius=25)

        pygame.draw.rect(screen, (50, 0, 100), (panel_x + 75, panel_y + 60, map_preview_size[0], map_preview_size[1]),
                         border_radius=15)
        pygame.draw.rect(screen, (255, 140, 0), (panel_x + 75, panel_y + 60, map_preview_size[0], map_preview_size[1]),
                         width=3, border_radius=15)

        map_image = pygame.image.load(os.path.join(maps_folder, map_files[selected_map])).convert_alpha()
        map_image = pygame.transform.smoothscale(map_image, map_preview_size)
        screen.blit(map_image, (panel_x + 75, panel_y + 60))

        left_arrow_rect = screen.blit(left_arrow_button, (panel_x + 10, panel_y + panel_height // 2 - 40))
        right_arrow_rect = screen.blit(arrow_button,
                                       (panel_x + panel_width - button_size - 10, panel_y + panel_height // 2 - 40))

        star_count = get_map_rating(selected_map)

        for i in range(5):
            if i < star_count:
                screen.blit(full_star, (panel_x + panel_width - 180 + (i * 35), panel_y + 20))
            else:
                screen.blit(empty_star, (panel_x + panel_width - 180 + (i * 35), panel_y + 20))

        map_count_text = button_font.render(f"Map {selected_map + 1} of {len(map_files)}", True, WHITE)
        screen.blit(map_count_text, (panel_x + 20, panel_y + 20))

        draw_fancy_button("Back", panel_x - 150, panel_y + panel_height + 20, 150, 50, (255, 140, 0), (200, 100, 0),
                          character_select_screen)
        draw_fancy_button("Start", panel_x + panel_width + 20, panel_y + panel_height + 20, 150, 50, (180, 0, 180),
                          (120, 0, 120), None)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()

                if left_arrow_rect.collidepoint((x, y)):
                    change_map(-1)
                elif right_arrow_rect.collidepoint((x, y)):
                    change_map(1)

                start_button_rect = pygame.Rect(panel_x + panel_width + 20, panel_y + panel_height + 20, 150, 50)
                if start_button_rect.collidepoint(x, y):
                    pygame.mixer.music.stop()
                    from gameplay import game_loop
                    game_loop(selected_map, player1_index, player2_index, player_skins)


def get_map_rating(map_index):
    ratings = [3, 4, 5, 2, 3]
    return ratings[map_index % len(ratings)]


def draw_circular_button(image, x, y, action=None):
    circle_center = (x + image.get_width() // 2, y + image.get_height() // 2)
    pygame.draw.circle(screen, (255, 255, 255), circle_center, image.get_width() // 2 + 10)
    screen.blit(image, (x, y))
    button_rect = image.get_rect(topleft=(x, y))
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    if button_rect.collidepoint(mouse) and click[0] == 1 and action:
        pygame.time.delay(150)
        action()


def settings_screen():
    running = True
    buttons_layout = pygame.image.load("screens/start_screen/buttons_layout.png")

    image_width = buttons_layout.get_width() + 100
    image_height = buttons_layout.get_height() + 100
    buttons_layout = pygame.transform.scale(buttons_layout, (image_width, image_height))

    platform_width = image_width + 60
    platform_height = image_height + 60

    layout_x = WIDTH // 2 - image_width // 2
    layout_y = HEIGHT // 2 - image_height // 2

    platform_x = WIDTH // 2 - platform_width // 2
    platform_y = HEIGHT // 2 - platform_height // 2

    while running:
        screen.blit(bg_image, (0, 0))
        screen.blit(overlay, (0, 0))

        border_rect = pygame.Rect(platform_x - 3, platform_y - 3, platform_width + 6, platform_height + 6)
        pygame.draw.rect(screen, (255, 140, 0), border_rect, border_radius=25)

        platform_rect = pygame.Rect(platform_x, platform_y, platform_width, platform_height)
        pygame.draw.rect(screen, (50, 10, 70, 180), platform_rect, border_radius=20)

        title_text = "Game Controls"
        title_font = pygame.font.Font(None, 80)
        shadow_color = (0, 255, 255)
        main_color = (255, 140, 0)

        title_surface_shadow = title_font.render(title_text, True, shadow_color)
        title_surface_main = title_font.render(title_text, True, main_color)

        title_x = WIDTH // 2 - title_surface_main.get_width() // 2
        title_y = 50

        screen.blit(title_surface_shadow, (title_x + 3, title_y + 3))
        screen.blit(title_surface_main, (title_x, title_y))

        screen.blit(buttons_layout, (layout_x, layout_y))

        draw_fancy_button("Back", WIDTH // 2 - 75, layout_y + image_height + 50, 150, 60, (255, 140, 0), (200, 100, 0),
                          start_screen)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()


def info_screen():
    running = True
    while running:
        screen.blit(bg_image, (0, 0))
        screen.blit(overlay, (0, 0))

        title_surface_orange = title_font.render("CREDITS", True, (255, 140, 0))
        title_surface_cyan = title_font.render("CREDITS", True, (0, 255, 255))

        title_x = WIDTH // 2 - title_surface_orange.get_width() // 2
        screen.blit(title_surface_cyan, (title_x + 2, 132))
        screen.blit(title_surface_orange, (title_x, 130))

        company_logo = pygame.image.load("screens/info_screen/company_logo.png")
        company_logo = pygame.transform.scale(company_logo, (300, 300))
        screen.blit(company_logo, (WIDTH // 2 - company_logo.get_width() // 2, 130))

        icon_size = 50
        icon_y_start = HEIGHT // 2 - 50
        icon_x = WIDTH // 2 - 250

        facebook_icon = pygame.image.load("screens/info_screen/Facebook_logo_(square).png")
        facebook_icon = pygame.transform.scale(facebook_icon, (icon_size, icon_size))

        linkedin_icon = pygame.image.load("screens/info_screen/LinkedIn_logo_initials.png")
        linkedin_icon = pygame.transform.scale(linkedin_icon, (icon_size, icon_size))

        instagram_icon = pygame.image.load("screens/info_screen/1000_F_542990265_jDTgAc4HLdrhAt8TGxGySA4O3TcXtO0j.png")
        instagram_icon = pygame.transform.scale(instagram_icon, (icon_size + 20, icon_size + 20))

        screen.blit(facebook_icon, (icon_x + 80, icon_y_start + 30))
        screen.blit(linkedin_icon, (icon_x + 40, icon_y_start + icon_size + 50))
        screen.blit(instagram_icon, (icon_x + 120, icon_y_start + icon_size + 40))

        social_text = button_font.render("@AGCompany", True, WHITE)
        shadow_text = button_font.render("@AGCompany", True, (50, 50, 50))

        text_x = WIDTH // 2 - 20
        text_y = icon_y_start + 110

        screen.blit(shadow_text, (text_x + 2, text_y + 2))
        screen.blit(social_text, (text_x, text_y))

        draw_fancy_button("Back", WIDTH // 2 - 75, 550, 150, 60, (255, 140, 0), (200, 100, 0), start_screen)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()


def credits_screen():
    running = True
    while running:
        screen.blit(bg_image, (0, 0))
        screen.blit(overlay, (0, 0))

        title_surface = title_font.render("Credits", True, WHITE)
        screen.blit(title_surface, (WIDTH // 2 - title_surface.get_width() // 2, 50))

        credits_text = button_font.render("Game developed by Your Name", True, WHITE)
        screen.blit(credits_text, (WIDTH // 2 - credits_text.get_width() // 2, HEIGHT // 2 - 50))

        draw_fancy_button("Back", WIDTH // 2 - 75, 500, 150, 60, HOVER_COLOR, BUTTON_COLOR, start_screen)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()


def start_screen():
    button_radius = 50
    border_thickness = 5

    play_button_x = WIDTH // 2
    settings_button_x = play_button_x - 150
    info_button_x = play_button_x + 150
    credits_button_x = WIDTH - 100
    credits_button_y = HEIGHT - 100

    button_y = 500

    running = True
    while running:
        screen.blit(bg_image, (0, 0))
        screen.blit(overlay, (0, 0))

        screen.blit(logo_image, (WIDTH // 2 - logo_image.get_width() // 2, 100))

        mouse_x, mouse_y = pygame.mouse.get_pos()
        dist_play = ((mouse_x - play_button_x) ** 2 + (mouse_y - button_y) ** 2) ** 0.5
        play_button_color = (130, 0, 180) if dist_play < button_radius else (75, 0, 130)

        dist_settings = ((mouse_x - settings_button_x) ** 2 + (mouse_y - button_y) ** 2) ** 0.5
        settings_button_color = (180, 180, 180) if dist_settings < button_radius else (100, 100, 100)

        dist_info = ((mouse_x - info_button_x) ** 2 + (mouse_y - button_y) ** 2) ** 0.5
        info_button_color = (0, 180, 255) if dist_info < button_radius else (0, 100, 200)

        dist_credits = ((mouse_x - credits_button_x) ** 2 + (mouse_y - credits_button_y) ** 2) ** 0.5
        credits_button_color = (255, 140, 0) if dist_credits < button_radius else (255, 100, 0)

        pygame.draw.circle(screen, (255, 165, 0), (play_button_x, button_y), button_radius + border_thickness)
        pygame.draw.circle(screen, play_button_color, (play_button_x, button_y), button_radius)

        pygame.draw.circle(screen, (255, 165, 0), (settings_button_x, button_y), border_thickness)
        pygame.draw.circle(screen, settings_button_color, (settings_button_x + 30, button_y), button_radius - 20)

        pygame.draw.circle(screen, (255, 165, 0), (info_button_x, button_y), border_thickness)
        pygame.draw.circle(screen, info_button_color, (info_button_x - 30, button_y), button_radius - 20)

        screen.blit(button_start,
                    (play_button_x - button_start.get_width() // 2, button_y - button_start.get_height() // 2))
        screen.blit(button_settings, (
            settings_button_x - button_settings.get_width() // 2 + 30, button_y - button_settings.get_height() // 2))
        screen.blit(button_info,
                    (info_button_x - button_info.get_width() // 2 - 30, button_y - button_info.get_height() // 2))

        clicked = False
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if dist_play < button_radius and not clicked:
                    clicked = True
                    pygame.time.wait(100)
                    button_click_sound.play()
                    character_select_screen()
                    return

                elif dist_settings < button_radius:
                    settings_screen()

                elif dist_info < button_radius:
                    info_screen()


def draw_fancy_button(text, x, y, width, height, active_color, inactive_color, action=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    pygame.draw.rect(screen, inactive_color, (x, y, width, height), border_radius=25)

    if x + width > mouse[0] > x and y + height > mouse[1] > y:
        pygame.draw.rect(screen, active_color, (x, y, width, height), border_radius=25)

        if click[0] == 1 and action:
            pygame.time.delay(150)
            button_click_sound.play()
            action()

    text_surface = button_font.render(text, True, WHITE)
    text_rect = text_surface.get_rect(center=(x + width // 2, y + height // 2))
    screen.blit(text_surface, text_rect)


start_screen()
