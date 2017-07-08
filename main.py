"""
Main script for Space Bounce.
"""
import pygame
import sys
import os
import csv
from helpers import ui
from helpers import paths
from helpers import materialize as colors
from helpers import timer
import maps
import sprites

# Initialize the modules
pygame.init()
paths.init(os.path.dirname(os.path.abspath(os.path.realpath(__file__))))

# Constants
width, height = 1280, 720
fps = 30
# Spawn for platforms
blue_spawnpoint = (100, 600)
red_spawnpoint = (1130, 600)
# Spawn for astronauts
blue_spawn = (blue_spawnpoint[0] + (sprites.Platform.width / 2 - sprites.Astronaut.width / 2),
    blue_spawnpoint[1] - sprites.Astronaut.height)
red_spawn = (red_spawnpoint[0] + (sprites.Platform.width / 2 - sprites.Astronaut.width / 2),
    red_spawnpoint[1] - sprites.Astronaut.height)

# Initialize window and clock
display = pygame.display.set_mode((width, height))
pygame.display.set_icon(pygame.image.load(paths.path('maps', 'icon.png')))
pygame.display.set_caption('Space Bounce')
clock = pygame.time.Clock()

# Load settings
settings = {}
with open(paths.path('settings.csv'), 'r') as settings_file:
    reader = csv.reader(settings_file)
    for row in reader:
        settings[row[0]] = row[1]

def menu_main():
    quit = False
    # Stop pending music
    pygame.mixer.music.stop()
    # Button dimension constants
    button_width_factor = 2 # Button width will take up 1 / x of horizontal screen
    button_height_factor = 6 # Button height will take up 1 / x of vertical screen
    # Load image and font
    bg = pygame.image.load(paths.path('maps', 'main-menu.png'))
    display.blit(bg, (0, 0))
    font = pygame.font.Font(paths.path('fonts', 'PressStart2P.ttf'), 30)
    # Create buttons
    fight_button = ui.TextButton(display, colors.white, colors.blue_darken_4, font, 'FIGHT!',
        (width / button_width_factor / 2,
        400,
        width / button_width_factor,
        height / button_height_factor)
        )
    help_button = ui.TextButton(display, colors.white, colors.blue_darken_4, font, 'Help',
        (width / button_width_factor / 2,
        550,
        width / button_width_factor / 2 - 10,
        height / button_height_factor)
        )
    settings_button = ui.TextButton(display, colors.white, colors.blue_darken_4, font, 'Settings',
        (width / button_width_factor + 10,
        550,
        width / button_width_factor / 2 - 10,
        height / button_height_factor)
        )

    # Game loop
    while not quit:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit = True
            # Button interactivity
            if fight_button.hovered:
                fight_button.toggle_bg(colors.blue_darken_3)
                if event.type == pygame.MOUSEBUTTONUP:
                    return menu_maps()
            else:
                fight_button.toggle_bg(colors.blue_darken_4)
            if help_button.hovered:
                help_button.toggle_bg(colors.blue_darken_3)
                if event.type == pygame.MOUSEBUTTONUP:
                    return menu_help()
            else:
                help_button.toggle_bg(colors.blue_darken_4)
            if settings_button.hovered:
                settings_button.toggle_bg(colors.blue_darken_3)
                if event.type == pygame.MOUSEBUTTONUP:
                    return menu_settings()
            else:
                settings_button.toggle_bg(colors.blue_darken_4)

        # Render screen
        pygame.display.update()
        # FIXME: Screen turns blue when minimized and restored
        clock.tick(fps)

def menu_maps():
    quit = False
    # Keep track of maps
    if settings['suddendeath_available'] == 'ON':
        map_list = list(maps.load().keys()) # If hidden option on, include sudden death in map selection
    else:
        map_list = list(maps.load().keys())[:-1] # Do not include sudden death by default
    map_index = 0
    # UI data
    preview_factor = 4 / 5
    title_font = pygame.font.Font(paths.path('fonts', 'PressStart2P.ttf'), 50)
    # Game loop
    while not quit:
        # Preview map
        map_preview = pygame.image.load(paths.path('maps', 'previews', map_list[map_index % len(map_list)] + '.png'))
        display.blit(map_preview, (0, 0))
        # Map title
        title = ui.TextButton(display, colors.white, None, title_font, map_list[map_index % len(map_list)].title(),
            (width / 3,
            25,
            width / 3,
            50,
            ))
        # Selection buttons
        left_button = ui.TextButton(display, colors.white, None, title_font, '<', (50, 25, 50, 50))
        right_button = ui.TextButton(display, colors.white, None, title_font, '>', (1180, 25, 50, 50))
        # Confirm button
        confirm_button = ui.TextButton(display, colors.white, None, title_font, 'SELECT',
            (width / 3,
            height - 75,
            width / 3,
            50,
            ))

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit = True
            # User confirms or changes map by key
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    map_index -= 1
                elif event.key == pygame.K_RIGHT:
                    map_index += 1
                elif event.key == pygame.K_RETURN:
                    return menu_fight(maps.load(), map_list[map_index % len(map_list)])
            # User changes map by arrows
            if left_button.hovered:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    map_index -= 1
            elif right_button.hovered:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    map_index += 1
            # User selects map
            if confirm_button.hovered:
                if event.type == pygame.MOUSEBUTTONUP:
                    return menu_fight(maps.load(), map_list[map_index % len(map_list)])

        # Render results
        clock.tick(fps)
        pygame.display.update()

def menu_fight(map_list, map_chosen):
    quit = False
    # If astronaut is shooting
    blue_shoot = False
    red_shoot = False
    # Fonts
    middle_font = pygame.font.Font(paths.path('fonts', 'PressStart2P.ttf'), 100)
    top_font = pygame.font.Font(paths.path('fonts', 'PressStart2P.ttf'), 25)
    # Spawn astronauts
    blue = sprites.Astronaut(display, 'blue', blue_spawn)
    red = sprites.Astronaut(display, 'red', red_spawn)
    # Keep track of coordinates
    blue_coordinates = blue_spawn
    red_coordinates = red_spawn
    # Generate map
    objects = maps.draw_map(display, map_list, map_chosen)
    if map_chosen != 'suddendeath':
        time = timer.Timer((0, int(settings['fight_length']), 0))
        if settings['sfx'] == 'ON':
            sprites.effects['countdown'].play()
        # Count down from three
        for text in ('3', '2', '1', 'GO!'):
            if map_chosen != 'random':
                maps.draw_map(display, map_list, map_chosen)
            else:
                maps.update_map(display, map_list, map_chosen, objects, True)
            ui.TextButton(display, colors.white, None, middle_font, text, (width / 2, height / 2, 0, 0))
            # Wait one second
            pygame.display.update()
            pygame.event.clear()
            clock.tick(1)
    else:
        ui.TextButton(display, colors.white, None, middle_font, 'SUDDEN DEATH', (width / 2, height / 2, 0, 0))
        # Wait one second
        pygame.display.update()
        pygame.event.clear()
        clock.tick(0.5)
    if settings['music'] == 'ON':
        pygame.mixer.music.load(map_list[map_chosen][2])
        pygame.mixer.music.play()
    # Game loop
    while not quit:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit = True
            # User has held down a key
            if event.type == pygame.KEYDOWN:
                # Check blue input
                if event.key == pygame.K_s:
                    blue.direction = 'left'
                elif event.key == pygame.K_f:
                    blue.direction = 'right'
                elif event.key == pygame.K_q:
                    blue.shoot(display, objects, settings['sfx'])
                elif event.key == pygame.K_w:
                    blue.punch(red, settings['sfx'])
                # Check red input
                if event.key == pygame.K_LEFT:
                    red.direction = 'left'
                elif event.key == pygame.K_RIGHT:
                    red.direction = 'right'
                elif event.key == pygame.K_PERIOD:
                    red.shoot(display, objects, settings['sfx'])
                elif event.key == pygame.K_SLASH:
                    red.punch(blue, settings['sfx'])
                # Pause
                if event.key == pygame.K_SPACE:
                    paused = True
                    ui.TextButton(display, colors.white, None, middle_font, 'PAUSED', (width / 2, height / 2, 0, 0))
                    while paused:
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                quit = True
                                paused = False
                            if event.type == pygame.KEYDOWN:
                                if event.key == pygame.K_SPACE:
                                    paused = False

                        clock.tick(fps)
                        pygame.display.update()

            # User has released a key
            if event.type == pygame.KEYUP:
                # Check blue input
                if event.key == pygame.K_s:
                    if blue.direction == 'left':
                        blue.direction = None
                elif event.key == pygame.K_f:
                    if blue.direction == 'right':
                        blue.direction = None
                # Check red input
                if event.key == pygame.K_LEFT:
                    if red.direction == 'left':
                        red.direction = None
                elif event.key == pygame.K_RIGHT:
                    if red.direction == 'right':
                        red.direction = None

        # Check game over by falling
        if blue.fallen(display):
            return menu_over(red, map_list, map_chosen)
        elif red.fallen(display):
            return menu_over(blue, map_list, map_chosen)
        # Render maps
        maps.update_map(display, map_list, map_chosen, objects)
        blue.update_pos(display, objects, fps, settings['sfx'])
        red.update_pos(display, objects, fps, settings['sfx'])
        # Draw ammo information
        display.blit(sprites.object_sprites['ammo-count'], (25, 25))
        display.blit(sprites.object_sprites['ammo-count'], (1238, 25))
        ui.TextButton(display, colors.white, None, top_font, str(blue.bullets).zfill(2), (90, 50, 0, 0))
        ui.TextButton(display, colors.white, None, top_font, str(red.bullets).zfill(2), (1190, 50, 0, 0))
        # Update timer
        if map_chosen != 'suddendeath':
            time_text = time.str_time()[4:8]
            # Check for sudden death
            if time.tick(fps) is False:
                return menu_fight(map_list, 'suddendeath')
            # Make text red if under 10 seconds
            elif time.time['seconds'] < 10 and time.time['minutes'] == 0:
                # Fade out music
                if round(time.time['seconds'], 1) == 10.0:
                    if settings['sfx'] == 'ON':
                        sprites.effects['suddendeath'].play()
                    pygame.mixer.music.fadeout(9000)
                time_color = colors.red
            # Update timer
            else:
                time_color = colors.white
            ui.TextButton(display, time_color, None, top_font, time_text, (640, 30, 0, 0))
        # Update time and screen
        clock.tick(fps)
        pygame.display.update()

def menu_help():
    quit = False
    # Font
    font = pygame.font.Font(paths.path('fonts', 'PressStart2P.ttf'), 30)
    # Display help image
    display.fill(colors.blue_grey_lighten_5)
    help_image = pygame.image.load(paths.path('maps', 'help.png'))
    display.blit(help_image, (0, 0))
    # Create buttons
    back_button = ui.TextButton(display, colors.black, None, font, '< Back', (50, 25, 200, 50))
    next_button = ui.TextButton(display, colors.black, None, font, 'Fight >', (1030, 25, 200, 50))
    # Game loop
    while not quit:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit = True
            if back_button.hovered:
                if event.type == pygame.MOUSEBUTTONUP:
                    return menu_main()
            if next_button.hovered:
                if event.type == pygame.MOUSEBUTTONUP:
                    return menu_maps()

        clock.tick(fps)
        pygame.display.update()

def menu_settings():
    quit = False
    # Font
    font = pygame.font.Font(paths.path('fonts', 'PressStart2P.ttf'), 50)
    while not quit:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit = True
            if event.type == pygame.MOUSEBUTTONUP:
                if music_button.hovered:
                    if music_button.bg == colors.green:
                        music_button.toggle_bg(colors.red)
                        settings['music'] = 'OFF'
                    elif music_button.bg == colors.red:
                        music_button.toggle_bg(colors.green)
                        settings['music'] = 'ON'
                if sfx_button.hovered:
                    if sfx_button.bg == colors.green:
                        sfx_button.toggle_bg(colors.red)
                        settings['sfx'] = 'OFF'
                    elif sfx_button.bg == colors.red:
                        sfx_button.toggle_bg(colors.green)
                        settings['sfx'] = 'ON'
                if fightlength_button.hovered:
                    settings['fight_length'] = str(int(settings['fight_length']) % 3 + 1)
            if ok_button.hovered:
                if event.type == pygame.MOUSEBUTTONUP:
                    # Write settings
                    with open(paths.path('settings.csv'), 'w') as settings_file:
                        writer = csv.writer(settings_file)
                        for setting in settings:
                            row = setting, settings[setting]
                            writer.writerow(row)
                    return menu_main()

        # Clear screen
        display.fill(colors.blue_grey_lighten_5)
        # Store settings
        color = {}
        for setting in settings:
            color[setting] = colors.green if settings[setting] == 'ON' else colors.red
        # Buttons
        music_button = ui.TextButton(display, colors.white, color['music'], font, 'Music', (40, 50, 390, 500))
        sfx_button = ui.TextButton(display, colors.white, color['sfx'], font, 'SFX', (450, 50, 390, 500))
        fightlength_button = ui.TextButton(display, colors.white, colors.green, font, settings['fight_length'] + ' min', (860, 50, 390, 500))
        ui.TextButton(display, colors.white, None, font, 'Fight', (860, 150, 390, 50))
        ui.TextButton(display, colors.white, None, font, 'Length', (860, 200, 390, 50))
        ok_button = ui.TextButton(display, colors.white, colors.blue, font, 'OK', (width / 3, 600, width / 3, 100))
        # Update display
        clock.tick(fps)
        pygame.display.update()

def menu_over(winner, map_list, map_chosen):
    quit = False
    # Switch off pending sound effects
    sprites.effects['suddendeath'].stop()
    # UI data
    resize_factor = 5 # How much bigger the astronaut will be displayed
    astronaut_coordinates = (width / 2 - sprites.Astronaut.width * resize_factor / 2, 225)
    # Load fonts
    title_font = pygame.font.Font(paths.path('fonts', 'PressStart2P.ttf'), 100)
    button_font = pygame.font.Font(paths.path('fonts', 'PressStart2P.ttf'), 50)
    # Draw winning screen
    display.blit(map_list[map_chosen][0], (0, 0))
    ui.TextButton(display, colors.white, None, title_font, 'WINNER', (
        width / 3,
        100,
        width / 3,
        100,
        ))
    astronaut = pygame.transform.scale(winner.sprite, (sprites.Astronaut.width * resize_factor, sprites.Astronaut.height * resize_factor))
    display.blit(astronaut, astronaut_coordinates)
    # Draw buttons
    play_again = ui.TextButton(display, colors.white, colors.blue_darken_4, button_font, 'Play Again', (50, 525, 550, 100))
    quit_button = ui.TextButton(display, colors.white, colors.blue_darken_4, button_font, 'Quit', (680, 525, 550, 100))
    # Game loop
    while not quit:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit = True
            # Play again
            if play_again.hovered:
                play_again.toggle_bg(colors.blue_darken_3)
                if event.type == pygame.MOUSEBUTTONUP:
                    return menu_main()
            else:
                play_again.toggle_bg(colors.blue_darken_4)
            # Quit
            if quit_button.hovered:
                quit_button.toggle_bg(colors.blue_darken_3)
                if event.type == pygame.MOUSEBUTTONUP:
                    quit = True
            else:
                quit_button.toggle_bg(colors.blue_darken_4)

        clock.tick(fps)
        pygame.display.update()

if __name__ == '__main__':
    menu_main()

# Tear things down
pygame.quit()
sys.exit()
