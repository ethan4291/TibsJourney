import pygame
import sys
import json
import math

from data.game_text import (
    WINDOW_TITLE,
    INTERACT_PROMPT,
    CONTINUE_PROMPT,
    DIALOGUE,
    DINO_ORDER,
    INTRO_TEXT,
    CUTSCENE_SIMPLE,
    CUTSCENE_ADVANCED_CAPTIONS,
    CUTSCENE_ADVANCED_FINALE,
)

pygame.init()
pygame.mixer.init()
pygame.mixer.music.load("data/audio/maingamemusic_loop.wav")
pygame.mixer.music.play(loops=-1)

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

# Each dino "quest" pairs an egg tile (found first) with a parent dino tile
# (returned to second). Tile ids below must match data/levels/level1.json.
QUEST_CONFIG = {
    "yellow": {"egg_tile": 3, "dino_tile": 4, "egg_dialogue": "yellow_egg", "ask": "yellowdino_ask", "thanks": "yellowdino_thanks", "done": "yellowdino_done"},
    "blue": {"egg_tile": 9, "dino_tile": 10, "egg_dialogue": "blue_egg", "ask": "bluedino_ask", "thanks": "bluedino_thanks", "done": "bluedino_done"},
    "green": {"egg_tile": 11, "dino_tile": 12, "egg_dialogue": "green_egg", "ask": "greendino_ask", "thanks": "greendino_thanks", "done": "greendino_done"},
    "red": {"egg_tile": 13, "dino_tile": 14, "egg_dialogue": "red_egg", "ask": "reddino_ask", "thanks": "reddino_thanks", "done": "reddino_done"},
}

dino_images = {
    "yellow": pygame.image.load("data/img/yellowdino.png").convert_alpha(),
    "blue": pygame.image.load("data/img/bluedino.png").convert_alpha(),
    "green": pygame.image.load("data/img/greendino.png").convert_alpha(),
    "red": pygame.image.load("data/img/reddino.png").convert_alpha(),
}

tile_images = {
    1: pygame.image.load("data/img/tile1.png").convert_alpha(),
    2: pygame.image.load("data/img/tile2.png").convert_alpha(),
    3: pygame.image.load("data/img/tile3.png").convert_alpha(),
    4: pygame.image.load("data/img/yellowdinospawnpos.png").convert_alpha(),
    9: pygame.image.load("data/img/blueegg.png").convert_alpha(),
    10: pygame.image.load("data/img/bluedinospawnpos.png").convert_alpha(),
    11: pygame.image.load("data/img/greenegg.png").convert_alpha(),
    12: pygame.image.load("data/img/greendinospawnpos.png").convert_alpha(),
    13: pygame.image.load("data/img/redegg.png").convert_alpha(),
    14: pygame.image.load("data/img/reddinospawnpos.png").convert_alpha(),
}

with open("data/levels/level1.json", "r") as level_file:
    level_data = json.load(level_file)

level_tiles = level_data["layers"][0]["tiles"]

quests = [
    {
        "id": dino_id,
        "egg_tile": QUEST_CONFIG[dino_id]["egg_tile"],
        "dino_tile": QUEST_CONFIG[dino_id]["dino_tile"],
        "egg_dialogue": QUEST_CONFIG[dino_id]["egg_dialogue"],
        "ask": QUEST_CONFIG[dino_id]["ask"],
        "thanks": QUEST_CONFIG[dino_id]["thanks"],
        "done": QUEST_CONFIG[dino_id]["done"],
        "egg_rect": None,
        "egg_interact_rect": None,
        "dino_rect": None,
        "dino_interact_rect": None,
        "delivered": False,
    }
    for dino_id in DINO_ORDER
]
quest_lookup = {quest["id"]: quest for quest in quests}
quest_by_egg_tile = {quest["egg_tile"]: quest for quest in quests}
quest_by_dino_tile = {quest["dino_tile"]: quest for quest in quests}

solid_tiles = []
interact_margin = tile_size * camera_zoom
for tile in level_tiles:
    tile_id = tile["tile"]
    tile_x = tile["x"] * tile_size * camera_zoom
    tile_y = tile["y"] * tile_size * camera_zoom
    if tile_id in (1, 2):
        solid_tiles.append(pygame.Rect(tile_x, tile_y, tile_size * camera_zoom, tile_size * camera_zoom))
    elif tile_id in quest_by_egg_tile:
        quest = quest_by_egg_tile[tile_id]
        quest["egg_rect"] = pygame.Rect(tile_x, tile_y, tile_size * camera_zoom, tile_size * camera_zoom)
        quest["egg_interact_rect"] = quest["egg_rect"].inflate(interact_margin * 2, interact_margin * 2)
    elif tile_id in quest_by_dino_tile:
        quest = quest_by_dino_tile[tile_id]
        quest["dino_rect"] = pygame.Rect(tile_x, tile_y, tile_size * camera_zoom, tile_size * camera_zoom)
        quest["dino_interact_rect"] = quest["dino_rect"].inflate(interact_margin * 2, interact_margin * 2)

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
active_npc = None  # tuple of (kind, quest_id) where kind is "egg" or "dino"
carried_quest = None
dialogue_font = pygame.font.SysFont("couriernew", 26)
prompt_font = pygame.font.SysFont("couriernew", 20, bold=True)

#intro cutscene (plays once at the start of the game)
intro_line_index = 0

#cutscene state (plays once every egg has been returned to its parent)
cutscene_stage = "intro"  # "intro" | None | "simple" | "advanced" | "advanced_finale"
cutscene_triggered = False
cutscene_line_index = 0
cutscene_adv_index = 0
cutscene_adv_phase = "panning"
cutscene_adv_timer = 0
cutscene_camera_start = (0, 0)
CUTSCENE_PAN_DURATION = 900
CUTSCENE_HOLD_DURATION = 1600

egg_size = round(tile_size * camera_zoom * 0.75)
egg_overlap = round(egg_size * 0.35)
egg_images = {quest["id"]: pygame.transform.scale(tile_images[quest["egg_tile"]], (egg_size, egg_size)) for quest in quests}

scaled_dino_images = {
    dino_id: pygame.transform.scale(image, (image.get_width() * camera_zoom, image.get_height() * camera_zoom))
    for dino_id, image in dino_images.items()
}


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


def draw_dialogue_box(surface, text, hint=INTERACT_PROMPT):
    box_margin = 20
    text_padding = 20
    line_height = 34
    max_width = screen_width - box_margin * 2 - text_padding * 2
    lines = wrap_text(text, dialogue_font, max_width)
    box_height = max(140, text_padding * 2 + len(lines) * line_height + 30)
    box_rect = pygame.Rect(box_margin, screen_height - box_height - box_margin, screen_width - box_margin * 2, box_height)
    pygame.draw.rect(surface, black, box_rect)
    pygame.draw.rect(surface, white, box_rect, 4)

    for line_index, line in enumerate(lines):
        line_surface = dialogue_font.render(line, True, white)
        surface.blit(line_surface, (box_rect.x + text_padding, box_rect.y + text_padding + line_index * line_height))

    hint_surface = prompt_font.render(hint, True, white)
    surface.blit(hint_surface, (box_rect.right - hint_surface.get_width() - 16, box_rect.bottom - hint_surface.get_height() - 12))


def draw_cutscene_caption(surface, text):
    box_margin = 20
    text_padding = 16
    line_height = 34
    max_width = screen_width - box_margin * 2 - text_padding * 2
    lines = wrap_text(text, dialogue_font, max_width)
    box_height = text_padding * 2 + len(lines) * line_height
    box_rect = pygame.Rect(box_margin, box_margin, screen_width - box_margin * 2, box_height)
    overlay = pygame.Surface((box_rect.width, box_rect.height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 170))
    surface.blit(overlay, box_rect.topleft)
    pygame.draw.rect(surface, white, box_rect, 3)
    for line_index, line in enumerate(lines):
        line_surface = dialogue_font.render(line, True, white)
        line_x = box_rect.centerx - line_surface.get_width() / 2
        line_y = box_rect.y + text_padding + line_index * line_height
        surface.blit(line_surface, (line_x, line_y))


def draw_cutscene_heart(surface, dino_rect, camera_x, camera_y, ticks):
    if not dino_rect:
        return
    pulse = 6 + 3 * math.sin(ticks / 180)
    offset = pulse * 0.6
    center_x = dino_rect.centerx - camera_x
    center_y = dino_rect.top - camera_y - 30
    heart_color = (255, 90, 140)
    pygame.draw.circle(surface, heart_color, (round(center_x - offset), round(center_y)), round(pulse))
    pygame.draw.circle(surface, heart_color, (round(center_x + offset), round(center_y)), round(pulse))
    point_bottom = (center_x, center_y + pulse * 1.6)
    point_left = (center_x - offset * 2, center_y)
    point_right = (center_x + offset * 2, center_y)
    pygame.draw.polygon(surface, heart_color, [point_left, point_right, point_bottom])


def draw_cutscene_finale(surface, text, hint=INTERACT_PROMPT):
    overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 190))
    surface.blit(overlay, (0, 0))
    lines = wrap_text(text, dialogue_font, screen_width - 120)
    total_height = len(lines) * 34
    start_y = screen_height / 2 - total_height / 2
    for line_index, line in enumerate(lines):
        line_surface = dialogue_font.render(line, True, white)
        surface.blit(line_surface, (screen_width / 2 - line_surface.get_width() / 2, start_y + line_index * 34))
    hint_surface = prompt_font.render(hint, True, white)
    surface.blit(hint_surface, (screen_width / 2 - hint_surface.get_width() / 2, start_y + total_height + 30))


camera_x = round(player_x - screen_width / 2 + camera_x_offset)
camera_y = round(player_y - screen_height / 2 + camera_y_offset)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if event.key == pygame.K_e:
                if cutscene_stage == "intro":
                    intro_line_index += 1
                    if intro_line_index >= len(INTRO_TEXT):
                        cutscene_stage = None
                elif cutscene_stage == "simple":
                    cutscene_line_index += 1
                    if cutscene_line_index >= len(CUTSCENE_SIMPLE):
                        cutscene_stage = "advanced"
                        cutscene_adv_index = 0
                        cutscene_adv_phase = "panning"
                        cutscene_adv_timer = 0
                        cutscene_camera_start = (camera_x, camera_y)
                elif cutscene_stage == "advanced_finale":
                    cutscene_stage = None
                elif cutscene_stage == "advanced":
                    pass
                elif dialogue_active:
                    dialogue_active = False
                    kind, quest_id = active_npc
                    quest = quest_lookup[quest_id]
                    if kind == "egg":
                        if carried_quest is None and not quest["delivered"]:
                            carried_quest = quest_id
                    elif kind == "dino":
                        if carried_quest == quest_id and not quest["delivered"]:
                            carried_quest = None
                            quest["delivered"] = True
                            if not cutscene_triggered and all(q["delivered"] for q in quests):
                                cutscene_triggered = True
                                cutscene_stage = "simple"
                                cutscene_line_index = 0
                    active_npc = None
                else:
                    opened = False
                    for quest in quests:
                        if quest["delivered"] or carried_quest is not None:
                            continue
                        if quest["egg_interact_rect"] and player_rect.colliderect(quest["egg_interact_rect"]):
                            dialogue_active = True
                            active_npc = ("egg", quest["id"])
                            dialogue_text = DIALOGUE[quest["egg_dialogue"]]
                            opened = True
                            break
                    if not opened:
                        for quest in quests:
                            if quest["dino_interact_rect"] and player_rect.colliderect(quest["dino_interact_rect"]):
                                dialogue_active = True
                                active_npc = ("dino", quest["id"])
                                if quest["delivered"]:
                                    dialogue_text = DIALOGUE[quest["done"]]
                                elif carried_quest == quest["id"]:
                                    dialogue_text = DIALOGUE[quest["thanks"]]
                                else:
                                    dialogue_text = DIALOGUE[quest["ask"]]
                                break
    keys = pygame.key.get_pressed()
    frame_time = clock.get_time()
    left_pressed = keys[pygame.K_LEFT] or keys[pygame.K_a]
    right_pressed = keys[pygame.K_RIGHT] or keys[pygame.K_d]
    jump_input = keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_SPACE]
    if dialogue_active or cutscene_stage is not None:
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

    if cutscene_stage == "advanced":
        cutscene_adv_timer += frame_time
        current_quest = quests[cutscene_adv_index]
        target_dino_rect = current_quest["dino_rect"]
        target_camera_x = round(target_dino_rect.centerx - screen_width / 2)
        target_camera_y = round(target_dino_rect.centery - screen_height / 2 - 40)
        start_x, start_y = cutscene_camera_start
        if cutscene_adv_phase == "panning":
            t = min(1.0, cutscene_adv_timer / CUTSCENE_PAN_DURATION)
            camera_x = round(start_x + (target_camera_x - start_x) * t)
            camera_y = round(start_y + (target_camera_y - start_y) * t)
            if t >= 1.0:
                cutscene_adv_phase = "holding"
                cutscene_adv_timer = 0
        else:
            camera_x, camera_y = target_camera_x, target_camera_y
            if cutscene_adv_timer >= CUTSCENE_HOLD_DURATION:
                cutscene_adv_index += 1
                if cutscene_adv_index >= len(quests):
                    cutscene_stage = "advanced_finale"
                else:
                    cutscene_adv_phase = "panning"
                    cutscene_adv_timer = 0
                    cutscene_camera_start = (camera_x, camera_y)
    elif cutscene_stage is None:
        camera_x = round(player_x - screen_width / 2 + camera_x_offset)
        camera_y = round(player_y - screen_height / 2 + camera_y_offset)
    # while "simple" or "advanced_finale" is active the camera stays where it last was

    screen.fill(sky_blue)
    for tile in level_tiles:
        tile_id = tile["tile"]
        egg_quest = quest_by_egg_tile.get(tile_id)
        if egg_quest and (egg_quest["delivered"] or carried_quest == egg_quest["id"]):
            continue
        if tile_id in quest_by_dino_tile:
            continue
        tile_image = tile_images.get(tile_id)
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

    for quest in quests:
        dino_rect = quest["dino_rect"]
        if not dino_rect:
            continue
        scaled_dino_image = scaled_dino_images[quest["id"]]
        dino_draw_x = dino_rect.x + (dino_rect.width - scaled_dino_image.get_width()) / 2
        dino_draw_y = dino_rect.bottom - scaled_dino_image.get_height()
        screen.blit(scaled_dino_image, (dino_draw_x - camera_x, dino_draw_y - camera_y))

    show_player = cutscene_stage not in ("advanced", "advanced_finale")
    if show_player:
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

        if carried_quest:
            egg_x = round(player_rect.centerx - egg_size / 2)
            egg_y = round(player_rect.top - egg_size + egg_overlap)
            screen.blit(egg_images[carried_quest], (egg_x - camera_x, egg_y - camera_y))

    prompt_target_rect = None
    if not dialogue_active and cutscene_stage is None:
        for quest in quests:
            if quest["delivered"] or carried_quest is not None:
                continue
            if quest["egg_rect"] and quest["egg_interact_rect"] and player_rect.colliderect(quest["egg_interact_rect"]):
                prompt_target_rect = quest["egg_rect"]
                break
        if prompt_target_rect is None:
            for quest in quests:
                if quest["dino_rect"] and quest["dino_interact_rect"] and player_rect.colliderect(quest["dino_interact_rect"]):
                    prompt_target_rect = quest["dino_rect"]
                    break
    if prompt_target_rect:
        prompt_surface = prompt_font.render(INTERACT_PROMPT, True, white)
        prompt_x = prompt_target_rect.centerx - camera_x - prompt_surface.get_width() / 2
        prompt_y = prompt_target_rect.top - camera_y - prompt_surface.get_height() - 6
        screen.blit(prompt_surface, (prompt_x, prompt_y))

    if dialogue_active:
        draw_dialogue_box(screen, dialogue_text)
    elif cutscene_stage == "intro":
        draw_dialogue_box(screen, INTRO_TEXT[intro_line_index], hint=CONTINUE_PROMPT)
    elif cutscene_stage == "simple":
        draw_dialogue_box(screen, CUTSCENE_SIMPLE[cutscene_line_index], hint=CONTINUE_PROMPT)
    elif cutscene_stage == "advanced":
        current_quest = quests[cutscene_adv_index]
        draw_cutscene_caption(screen, CUTSCENE_ADVANCED_CAPTIONS[current_quest["id"]])
        draw_cutscene_heart(screen, current_quest["dino_rect"], camera_x, camera_y, pygame.time.get_ticks())
    elif cutscene_stage == "advanced_finale":
        draw_cutscene_finale(screen, CUTSCENE_ADVANCED_FINALE, hint=CONTINUE_PROMPT)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
