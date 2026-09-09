import pygame
import sys
import json

from data.game_text import WINDOW_TITLE, INTERACT_PROMPT, DIALOGUE

pygame.init()

screen_width = 800
screen_height = 600

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption(WINDOW_TITLE)
clock = pygame.time.Clock()
FPS = 60
camera_zoom = 4
tile_size = 16
camera_x_offset = 0
camera_y_offset = 0

#load images

player_idle_image = pygame.image.load("data/img/playeridle1.png").convert_alpha()
playerwalk1 = pygame.image.load("data/img/playerwalk1.png").convert_alpha()
playerwalk2 = pygame.image.load("data/img/playerwalk2.png").convert_alpha()
playerwalk3 = pygame.image.load("data/img/playerwalk3.png").convert_alpha()
playerwalk4 = pygame.image.load("data/img/playerwalk4.png").convert_alpha()
playerwalk5 = pygame.image.load("data/img/playerwalk5.png").convert_alpha()
playerwalk6 = pygame.image.load("data/img/playerwalk6.png").convert_alpha()
playerjump = pygame.image.load("data/img/playerjump.png").convert_alpha()
playerfall = pygame.image.load("data/img/playerfall.png").convert_alpha()
tile_images = {
    1: pygame.image.load("data/img/tile1.png").convert_alpha(),
    2: pygame.image.load("data/img/tile2.png").convert_alpha(),
    3: pygame.image.load("data/img/tile3.png").convert_alpha(),
    4: pygame.image.load("data/img/yellowdinospawnpos.png").convert_alpha()
}
yellowdino_image = pygame.image.load("data/img/yellowdino.png").convert_alpha()

with open("data/levels/level1.json", "r") as level_file:
    level_data = json.load(level_file)

level_tiles = level_data["layers"][0]["tiles"]
solid_tiles = []
npc_rect = None
npc_interact_rect = None
dino_rect = None
dino_interact_rect = None
interact_margin = tile_size * camera_zoom
for tile in level_tiles:
    if tile["tile"] in (1, 2):
        tile_x = tile["x"] * tile_size * camera_zoom
        tile_y = tile["y"] * tile_size * camera_zoom
        solid_tiles.append(pygame.Rect(tile_x, tile_y, tile_size * camera_zoom, tile_size * camera_zoom))
    elif tile["tile"] == 3:
        tile_x = tile["x"] * tile_size * camera_zoom
        tile_y = tile["y"] * tile_size * camera_zoom
        npc_rect = pygame.Rect(tile_x, tile_y, tile_size * camera_zoom, tile_size * camera_zoom)
        npc_interact_rect = npc_rect.inflate(interact_margin * 2, interact_margin * 2)
    elif tile["tile"] == 4:
        tile_x = tile["x"] * tile_size * camera_zoom
        tile_y = tile["y"] * tile_size * camera_zoom
        dino_rect = pygame.Rect(tile_x, tile_y, tile_size * camera_zoom, tile_size * camera_zoom)
        dino_interact_rect = dino_rect.inflate(interact_margin * 2, interact_margin * 2)

#player animation frames
player_walk_frames = [playerwalk1, playerwalk2, playerwalk3, playerwalk4, playerwalk5, playerwalk6]
player_jump_frame = playerjump
player_fall_frame = playerfall

#game variables
player_x = 2750
player_y = 700
player_speed = 5
player_frame_index = 0
player_frame_timer = 0
player_frame_delay = 100  # milliseconds per frame
player_jump_power = 15
player_is_jumping = False
player_on_ground = False
player_is_flipped = False
player_horizontal_velocity = 0
player_vertical_velocity = 0
acceleration = 0.45
deceleration = 0.65
jump_gravity = 0.4
jump_hold_multiplier = 6.0
max_fall_speed = 12
coyote_time = 100
jump_buffer_time = 100
coyote_timer = coyote_time
jump_buffer_timer = 0
jump_input_previous = False
player_rect = pygame.Rect(player_x, player_y, player_idle_image.get_width() * camera_zoom, player_idle_image.get_height() * camera_zoom)

#colors
black = (0, 0, 0)
white = (255, 255, 255)
sky_blue = (135, 206, 235)

#dialogue box (undertale-style)
dialogue_active = False
dialogue_text = ""
active_npc = None
has_egg = False
quest_complete = False
dialogue_font = pygame.font.SysFont("couriernew", 26)
prompt_font = pygame.font.SysFont("couriernew", 20, bold=True)

egg_size = round(tile_size * camera_zoom * 0.75)
egg_image = pygame.transform.scale(tile_images[3], (egg_size, egg_size))
egg_overlap = round(egg_size * 0.35)

scaled_dino_image = pygame.transform.scale(yellowdino_image, (yellowdino_image.get_width() * camera_zoom, yellowdino_image.get_height() * camera_zoom))


def wrap_text(text, font, max_width):
    words = text.split(" ")
    lines = []
    current_line = ""
    for word in words:
        test_line = (current_line + " " + word).strip()
        if font.size(test_line)[0] > max_width and current_line:
            lines.append(current_line)
            current_line = word
        else:
            current_line = test_line
    if current_line:
        lines.append(current_line)
    return lines


def draw_dialogue_box(surface, text):
    box_margin = 20
    box_height = 140
    box_rect = pygame.Rect(box_margin, screen_height - box_height - box_margin, screen_width - box_margin * 2, box_height)
    pygame.draw.rect(surface, black, box_rect)
    pygame.draw.rect(surface, white, box_rect, 4)

    text_padding = 20
    lines = wrap_text(text, dialogue_font, box_rect.width - text_padding * 2)
    for line_index, line in enumerate(lines):
        line_surface = dialogue_font.render(line, True, white)
        surface.blit(line_surface, (box_rect.x + text_padding, box_rect.y + text_padding + line_index * 34))

    hint_surface = prompt_font.render(INTERACT_PROMPT, True, white)
    surface.blit(hint_surface, (box_rect.right - hint_surface.get_width() - 16, box_rect.bottom - hint_surface.get_height() - 12))


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if event.key == pygame.K_e:
                if dialogue_active:
                    dialogue_active = False
                    if active_npc == "tib_egg":
                        has_egg = True
                    elif active_npc == "yellow_dino" and has_egg and not quest_complete:
                        has_egg = False
                        quest_complete = True
                    active_npc = None
                elif not has_egg and npc_interact_rect and player_rect.colliderect(npc_interact_rect):
                    dialogue_active = True
                    active_npc = "tib_egg"
                    dialogue_text = DIALOGUE["tile3_npc"]
                elif dino_interact_rect and player_rect.colliderect(dino_interact_rect):
                    dialogue_active = True
                    active_npc = "yellow_dino"
                    if quest_complete:
                        dialogue_text = DIALOGUE["yellowdino_done"]
                    elif has_egg:
                        dialogue_text = DIALOGUE["yellowdino_thanks"]
                    else:
                        dialogue_text = DIALOGUE["yellowdino_ask"]
    keys = pygame.key.get_pressed()
    frame_time = clock.get_time()
    left_pressed = keys[pygame.K_LEFT] or keys[pygame.K_a]
    right_pressed = keys[pygame.K_RIGHT] or keys[pygame.K_d]
    jump_input = keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_SPACE]
    if dialogue_active:
        left_pressed = right_pressed = jump_input = False
    jump_pressed = jump_input and not jump_input_previous
    horizontal_input = int(right_pressed) - int(left_pressed)

    if horizontal_input != 0:
        player_horizontal_velocity += horizontal_input * acceleration
        player_horizontal_velocity = max(-player_speed, min(player_speed, player_horizontal_velocity))
        player_is_flipped = horizontal_input < 0
    elif player_horizontal_velocity > 0:
        player_horizontal_velocity = max(0, player_horizontal_velocity - deceleration)
    elif player_horizontal_velocity < 0:
        player_horizontal_velocity = min(0, player_horizontal_velocity + deceleration)
    player_x += player_horizontal_velocity
    player_rect.x = round(player_x)
    for tile_rect in solid_tiles:
        if player_rect.colliderect(tile_rect):
            if player_horizontal_velocity > 0:
                player_rect.right = tile_rect.left
            elif player_horizontal_velocity < 0:
                player_rect.left = tile_rect.right
            player_x = player_rect.x

    if jump_pressed:
        jump_buffer_timer = jump_buffer_time
    else:
        jump_buffer_timer = max(0, jump_buffer_timer - frame_time)

    if player_on_ground:
        coyote_timer = coyote_time
    else:
        coyote_timer = max(0, coyote_timer - frame_time)

    if jump_buffer_timer > 0 and coyote_timer > 0:
        player_is_jumping = True
        player_on_ground = False
        player_vertical_velocity = -player_jump_power
        jump_buffer_timer = 0
        coyote_timer = 0
        player_frame_index = 0
        player_frame_timer = 0

    if abs(player_horizontal_velocity) > 0.1 and player_on_ground:
        player_frame_timer += frame_time
        if player_frame_timer >= player_frame_delay:
            player_frame_timer = 0
            player_frame_index = (player_frame_index + 1) % len(player_walk_frames)
    else:
        player_frame_index = 0
    gravity = jump_gravity
    if not jump_input and player_vertical_velocity < 0:
        gravity *= jump_hold_multiplier
    player_vertical_velocity = min(max_fall_speed, player_vertical_velocity + gravity)
    player_y += player_vertical_velocity
    player_rect.y = round(player_y)
    player_on_ground = False
    for tile_rect in solid_tiles:
        if player_rect.colliderect(tile_rect):
            if player_vertical_velocity > 0:
                player_rect.bottom = tile_rect.top
                player_is_jumping = False
            elif player_vertical_velocity < 0:
                player_rect.top = tile_rect.bottom
            player_vertical_velocity = 0
            player_y = player_rect.y

    ground_check_rect = player_rect.move(0, 1)
    for tile_rect in solid_tiles:
        if ground_check_rect.colliderect(tile_rect):
            player_on_ground = True
            break
    if not player_on_ground:
        player_is_jumping = True

    jump_input_previous = jump_input

    camera_x = round(player_x - screen_width / 2 + camera_x_offset)
    camera_y = round(player_y - screen_height / 2 + camera_y_offset)
    screen.fill(sky_blue)
    for tile in level_tiles:
        if tile["tile"] == 3 and (has_egg or quest_complete):
            continue
        if tile["tile"] == 4:
            continue
        tile_image = tile_images.get(tile["tile"])
        if tile_image is None:
            continue
        tile_image = pygame.transform.scale(tile_image, (tile_size * camera_zoom, tile_size * camera_zoom))
        if tile["flipX"]:
            tile_image = pygame.transform.flip(tile_image, True, False)
        if tile["rot"] != 0:
            tile_image = pygame.transform.rotate(tile_image, tile["rot"])
        tile_x = tile["x"] * tile_size * camera_zoom - camera_x
        tile_y = tile["y"] * tile_size * camera_zoom - camera_y
        screen.blit(tile_image, (tile_x, tile_y))

    if dino_rect:
        dino_draw_x = dino_rect.x + (dino_rect.width - scaled_dino_image.get_width()) / 2
        dino_draw_y = dino_rect.bottom - scaled_dino_image.get_height()
        screen.blit(scaled_dino_image, (dino_draw_x - camera_x, dino_draw_y - camera_y))

    #scale using camera zoom
    if not player_on_ground and player_vertical_velocity < 0:
        player_image = player_jump_frame
    elif not player_on_ground:
        player_image = player_fall_frame
    elif abs(player_horizontal_velocity) > 0.1:
        player_image = player_walk_frames[player_frame_index]
    else:
        player_image = player_idle_image
    scaled_player_image = pygame.transform.scale(player_image, (player_image.get_width() * camera_zoom, player_image.get_height() * camera_zoom))

    if player_is_flipped:
        scaled_player_image = pygame.transform.flip(scaled_player_image, True, False)
    player_draw_x = round(player_x + (player_rect.width - scaled_player_image.get_width()) / 2)
    player_draw_y = round(player_y + player_rect.height - scaled_player_image.get_height())
    screen.blit(scaled_player_image, (player_draw_x - camera_x, player_draw_y - camera_y))

    if has_egg:
        egg_x = round(player_rect.centerx - egg_size / 2)
        egg_y = round(player_rect.top - egg_size + egg_overlap)
        screen.blit(egg_image, (egg_x - camera_x, egg_y - camera_y))

    prompt_target_rect = None
    if not dialogue_active:
        if not has_egg and npc_rect and npc_interact_rect and player_rect.colliderect(npc_interact_rect):
            prompt_target_rect = npc_rect
        elif dino_rect and dino_interact_rect and player_rect.colliderect(dino_interact_rect):
            prompt_target_rect = dino_rect
    if prompt_target_rect:
        prompt_surface = prompt_font.render(INTERACT_PROMPT, True, white)
        prompt_x = prompt_target_rect.centerx - camera_x - prompt_surface.get_width() / 2
        prompt_y = prompt_target_rect.top - camera_y - prompt_surface.get_height() - 6
        screen.blit(prompt_surface, (prompt_x, prompt_y))

    if dialogue_active:
        draw_dialogue_box(screen, dialogue_text)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()