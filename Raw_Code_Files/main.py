import json
import os
import sys
import bin.audio_loader as sounds
import bin.font_loader as fonts
import bin.image_loader as bin
import bin.map_loader as maps
from math import cos, sin, radians, ceil, floor
from random import randint
from threading import Thread, Event
from time import sleep

try:
    import pygame
except ImportError:
    from tkinter import messagebox, Toplevel, Message
    import subprocess
    if not messagebox.askyesno('Install Pygame?', 'Pygame is required for this gameplay.\nWould you like to install Pygame?'):
        if not messagebox.askyesno('Are you sure?', 'If you do not install pygame, you will not be able to play this gameplay!\nDo you want to install pygame?', icon='warning', default=messagebox.NO):
            sys.exit()
    try:
        subprocess.check_call(
            [sys.executable, '-m', 'pip', 'install', 'pygame'])
        import pygame
        messagebox.showinfo('Success', 'Pygame was successfully installed.')
    except (subprocess.CalledProcessError, ModuleNotFoundError) as error:
        if not messagebox.askretrycancel('Could not Install', f'There was an error installing pygame:\n{error}\nIf the problem persists, you may have to install it manually.\n\nWould you like to retry?', icon='error'):
            sys.exit()

pygame.init()
pygame.joystick.init()
pygame.mixer.init()

RED = 255, 0, 0
GREEN = 0, 255, 0
WHITE = 255, 255, 255
V_LIGHT_GREY = 200, 200, 200
LIGHT_GREY = 170, 170, 170
GREY = 150, 150, 150
DARK_GREY = 100, 100, 100
BLACK = 0, 0, 0
ORANGE = 255, 165, 0
CAR_1 = 232, 106, 23
CAR_2 = 255, 204, 0
CAR_3 = 57, 194, 114
CAR_4 = 47, 149, 208
CAR_5 = 93, 91, 91
Debug = False
Race_debug = False
Force_resolution = []
Screen = 0
Animations = False
Mute_volume = False
Music_volume = 0
Sfx_volume = 0 
FPS = 60
Intro_screen = True
Countdown = True
Load_settings = True
Game_end = False

def save_settings(settings):
    """Save the settings to a JSON file."""
    
    if not os.path.exists('settings.json'):
        print('*** ERROR: Failed to save settings -> settings file not found! ***')
        return
    try:
        with open('settings.json', 'w') as file:
            
            json.dump(settings, file, indent=2)
            print('Successfully saved settings to file.')
    except IOError:
        print('*** ERROR: Failed to save settings -> I/O error! ***')
    except json.JSONDecodeError:
        print('*** ERROR: Failed to save settings -> invalid JSON data! ***')



def load_settings():
    global Debug, Force_resolution, Screen, Animations, Mute_volume, Music_volume, Sfx_volume
    try:
        with open('settings.json', 'r') as file:
            settings = json.load(file)
            Debug = settings['Debug']
            Force_resolution = settings['Resolution']
            Screen = settings['Screen']
            Animations = settings['Menu animations']
            Mute_volume = settings['Mute volume']
            Music_volume = settings['Music volume']
            Sfx_volume = settings['Sfx volume']
            print('Successfully loaded settings from file.')
    except FileNotFoundError:
        print("*** WARNING: 'settings.json' not found, creating new file with default settings. ***")
        try:
            with open('settings.json', 'w') as file:
                default_settings = {'Debug': False,
                                    'Resolution': 0,
                                    'Screen': 0,
                                    'Menu animations': True,
                                    'Mute volume': False,
                                    'Music volume': 0,
                                    'Sfx volume': 0}
                json.dump(default_settings, file, indent=2)
                Debug = default_settings['Debug']
                Force_resolution = default_settings['Resolution']
                Screen = default_settings['Screen']
                Animations = default_settings['Menu animations']
                Mute_volume = default_settings['Mute volume']
                Music_volume = default_settings['Music volume']
                Sfx_volume = default_settings['Sfx volume']
                print('Successfully created new settings file.')
        except PermissionError:
            print(
                "*** ERROR: Failed to create new 'settings.json' file -> permission denied! ***")
    except json.JSONDecodeError:
        print("*** WARNING: Invalid JSON data in 'settings.json', creating new file with default settings. ***")
        try:
            with open('settings.json', 'w') as file:
                default_settings = {'Debug': False,
                                    'Resolution': 0,
                                    'Screen': 0,
                                    'Menu animations': True,
                                    'Mute volume': False,
                                    'Music volume': 0,
                                    'Sfx volume': 0}
                json.dump(default_settings, file, indent=2)
                Debug = default_settings['Debug']
                Force_resolution = default_settings['Resolution']
                Screen = default_settings['Screen']
                Animations = default_settings['Menu animations']
                Mute_volume = default_settings['Mute volume']
                Music_volume = default_settings['Music volume']
                Sfx_volume = default_settings['Sfx volume']
                print('Successfully created new settings file.')
        except PermissionError:
            print(
                "*** ERROR: Failed to create new 'settings.json' file -> permission denied! ***")
if Load_settings:
    load_settings()
device_information = pygame.display.get_desktop_sizes()
if not Force_resolution:
    
    if len(device_information) < Screen + 1:
        Screen = 0
    device_screen_resolution = tuple(device_information[Screen])
else:
    
    if len(device_information) < Screen + 1:
        Screen = 0
        save_settings()
    device_screen_resolution = tuple(Force_resolution)
print('Running at ' +
      str(device_screen_resolution[0]) + ' x ' + str(device_screen_resolution[1]))
pygame.display.set_caption('road fighter')
try:
    icon = pygame.surface.Surface((32, 32))
    icon.set_colorkey(BLACK)
    icon.blit(pygame.transform.scale(pygame.image.load(
        bin.car(CAR_1, 'family car')), (20, 32)), (6, 0))
    pygame.display.set_icon(icon)
except FileNotFoundError:
    print('*** ERROR: Could not set window icon -> {0} not found! ***'.format(
        bin.car(CAR_1, 'family car')))
if device_information[Screen] != device_screen_resolution:
    Display = pygame.display.set_mode(device_screen_resolution, display=Screen)
    Fullscreen = False
else:
    Display = pygame.display.set_mode(
        device_screen_resolution, display=Screen, flags=pygame.FULLSCREEN)
    Fullscreen = True

WIDTH, HEIGHT = 1920, 1080
CENTRE = WIDTH // 2, HEIGHT // 2
Window = pygame.Surface((WIDTH, HEIGHT))
Window_resolution = Window.get_size()
Window_screenshot = Window.copy()
Window_sleep = False  
second_screen = pygame.Surface((WIDTH, HEIGHT))
present_window = ''
if device_screen_resolution != Window_resolution:
    Display_scaling = True
else:
    Display_scaling = False

Players = []
Selected_player = []
Player_amount = 0
Enemy_Amount = 3
Map = maps.objs[len(maps.index)//2]()
Track_mask = pygame.mask.Mask((WIDTH, HEIGHT))
Total_laps = 3
Current_lap = 0
Race_time = 0
Player_positions = []
Player_list = []
Machines_available = []
Enemy_names = [['Alice', False], ['Bob', False], ['Cathy', False], ['David', False], ['Emma', False],
               ['Frank', False], ['Grace', False], ['Henry', False], [
                   'Isabella', False], ['Jack', False],
               ['Kate', False], ['Leo', False], ['Mia', False], [
                   'Nathan', False], ['Olivia', False],
               ['Peter', False], ['Quinn', False], ['Riley', False], [
    'Sarah', False], ['Thomas', False],
    ['Uma', False], ['Victor', False], ['William', False], [
        'Xavier', False], ['Yuna', False],
    ['Zack', False]]
test_alphas = []
controls = []
test_alpha_prompts = []
Enemy_machines = 0
Enemy_machine_color = None
lightning_frames = [pygame.transform.scale(pygame.image.load(
    bin.animation('lightning', frame)), (128, 128)) for frame in range(0, 15)]
smoke_frames = [pygame.transform.scale(pygame.image.load(
    bin.animation('smoke', frame)), (64, 64)) for frame in range(0, 7)]
repair_frames = [pygame.transform.scale(pygame.image.load(
    bin.animation('repair', frame)), (128, 128)) for frame in range(0, 11)]
map_preview_size = 974, 600
map_preview_pos = CENTRE[0] - \
    map_preview_size[0] // 2, CENTRE[1] - map_preview_size[1] // 2

map_prev_demo = '', pygame.surface.Surface(map_preview_size)
tile_scale = ceil(WIDTH / 15), ceil(HEIGHT / 10)
menu_scroll_speed = 70 
menu_car_speed = 10  
button_trigger = False 
selected_text_entry = 0
current_song = ''
Clock = pygame.time.Clock()
music_thread = Thread()
loading_thread = Thread()
loading_thread_event = Event()
music_thread_event = Event()
powerups = True
Game_paused = False
global_car_rotation_speed = 1
global_car_move_speed = 4
screen_updates = []
loaded_bin = []
loaded_sounds = []
loaded_fonts = {}

class Object:
    def __init__(own, game_surface: pygame.surface.Surface, rect: pygame.rect.Rect, mask: pygame.mask.Mask):
        own.game_surface = game_surface
        own.rect = rect
        own.mask = mask
        own.ver = None
        own.timeout = None
        own.active = None

class Player:
    def __init__(own, position: int, is_player=True):
        own.id = position
        own.is_player = is_player
        if 0 > own.id or 5 < own.id:
            raise ValueError(
                'Player | own.id can only be between 0 and 5 not ' + str(own.id))
        own.name = None
        own.machine_name = None
        own.car_image = None
        own.car_color = None
        own.start_pos = own.id + 1
        own.controls = None
        own.default_controls = None
        if own.is_player:
            own.load_player()
        else:
            own.load_npc()
        own.update_image()
    def load_player(own):
        if own.id == 0:
            own.machine_name = 'Family Car'
            own.car_color = CAR_1
            if 'wasd' not in controls:
                own.controls = 'wasd'
            elif 'arrows' not in controls:
                own.controls = 'arrows'
        elif own.id == 1:
            own.name = ''
            own.machine_name = 'Sports Car'
            own.car_color = CAR_2
            if 'wasd' not in controls:
                own.controls = 'wasd'
            elif 'arrows' not in controls:
                own.controls = 'arrows'
        elif own.id == 2:
            own.machine_name = 'Luxury Car'
            own.car_color = CAR_3
            if 'wasd' not in controls:
                own.controls = 'wasd'
            elif 'arrows' not in controls:
                own.controls = 'arrows'
        elif own.id == 3:
            own.machine_name = 'Truck'
            own.car_color = CAR_4
            if 'wasd' not in controls:
                own.controls = 'wasd'
            elif 'arrows' not in controls:
                own.controls = 'arrows'
        elif own.id == 4:
            own.machine_name = 'Race Car'
            own.car_color = CAR_5
            if 'wasd' not in controls:
                own.controls = 'wasd'
            elif 'arrows' not in controls:
                own.controls = 'arrows'
        elif own.id == 5:
            own.machine_name = 'Family Car'
            own.car_color = CAR_1
            if 'wasd' not in controls:
                own.controls = 'wasd'
            elif 'arrows' not in controls:
                own.controls = 'arrows'
        if own.controls:
            controls.append(own.controls)
        else:
            own.controls = 'test_alpha'
        own.name = ''
        own.default_controls = own.controls
    def load_npc(own):
        
        own.name = Enemy_names[randint(0, len(Enemy_names) - 1)]
        while own.name[1] or own.name[0].lower() == Players[0].name.lower() or Player_amount >= 2 and \
                own.name[0].lower() == Players[1].name.lower() or Player_amount >= 3 and \
                own.name[0].lower() == Players[2].name.lower() or Player_amount >= 4 and \
                own.name[0].lower() == Players[3].name.lower() or Player_amount >= 5 and \
                own.name[0].lower() == Players[4].name.lower() or Player_amount == 6 and \
                own.name[0].lower() and Players[5].name.lower():
            own.name = Enemy_names[randint(0, len(Enemy_names) - 1)]
        own.name[1] = True
        if Enemy_machines == 1:
            own.machine_name = 'Family Car'
        elif Enemy_machines == 2:
            own.machine_name = 'Sports Car'
        elif Enemy_machines == 3:
            own.machine_name = 'Luxury Car'
        elif Enemy_machines == 4:
            own.machine_name = 'Truck'
        elif Enemy_machines == 5:
            own.machine_name = 'Race Car'
        else:
            own.machine_name = random_car()
        if Enemy_machine_color:
            own.car_color = Enemy_machine_color
        else:
            own.car_color = random_color()
    def update_image(own):
        own.car_image = pygame.transform.scale(pygame.image.load(bin.car(own.car_color, own.machine_name)),
                                               (175, 300))

class MenuCar:  
    def __init__(own):
        own.scale = 71, 131
        own.pos_x = CENTRE[0]
        own.pos_y = CENTRE[1]
        own.rotation = 0  
        own.image = pygame.transform.scale(pygame.image.load(
            bin.car('green', 'race car')).convert(), own.scale)
        own.image.set_colorkey(BLACK)  
        own.size = own.image.get_size()
        own.rect = own.image.get_rect()  
        own.scaled_rect = None
        own.prev_rect = own.rect
        own.rect.center = own.pos_x, own.pos_y  
        own.speed = menu_car_speed
    def rotate(own, degree):  
        if own.rotation != degree:  
            
            own.prev_rect = pygame.rect.Rect(own.rect)
            own.image = pygame.transform.rotate(pygame.transform.scale(pygame.image.load(
                bin.car('green', 'race car')).convert(), own.scale), degree)  
            own.image.set_colorkey(BLACK)  
            own.rotation = degree  
            own.rect = own.image.get_rect()  
            own.rect.center = own.pos_x, own.pos_y
            own.size = own.image.get_size()
    def move(own, x, y):
        
        own.prev_rect = pygame.rect.Rect(own.rect)
        
        screen_updates.append(own.prev_rect)
        own.pos_x = x
        own.pos_y = y
        own.rect.center = x, y
    def draw(own, update=False):
        
        Window.blit(own.image, (own.rect.left, own.rect.top))
        if update:
            if Display_scaling:
                own.scaled_rect = [own.rect[0],
                                   own.rect[1], own.rect[2], own.rect[3]]
                screen_refresh(scale_rect(own.scaled_rect))
                own.scaled_rect = [
                    own.prev_rect[0], own.prev_rect[1], own.prev_rect[2], own.prev_rect[3]]
                screen_refresh(scale_rect(own.scaled_rect))
            else:
                screen_refresh(rect=own.prev_rect)
                screen_refresh(rect=own.rect)
        else:
            if Display_scaling:
                
                own.scaled_rect = [own.rect[0],
                                   own.rect[1], own.rect[2], own.rect[3]]
                
                screen_updates.append(scale_rect(own.scaled_rect))
                own.scaled_rect = [
                    own.prev_rect[0], own.prev_rect[1], own.prev_rect[2], own.prev_rect[3]]
                screen_updates.append(scale_rect(own.scaled_rect))
            else:
                screen_updates.append(own.prev_rect)
                screen_updates.append(own.rect)
    def animate(own, direction: str, bg: any):
        if direction == 'up':
            if own.rotation != 0:
                if own.rotation < 180:
                    for rotation in reversed(range(0, own.rotation, own.speed)):
                        
                        Clock.tick(FPS)
                        
                        own.rotate(rotation)
                        own.draw(update=True)
                else:
                    for rotation in range(own.rotation, 360 + 1, own.speed):
                        
                        Clock.tick(FPS)
                        
                        own.rotate(rotation)
                        own.draw(update=True)
                    own.rotation = 0
        elif direction == 'down':
            if own.rotation != 180:
                if own.rotation < 180:
                    for rotation in range(own.rotation, 180 + 1, own.speed):
                        
                        Clock.tick(FPS)
                        
                        own.rotate(rotation)  
                        own.draw(update=True)  
                else:
                    for rotation in reversed(range(180, own.rotation, own.speed)):
                        
                        Clock.tick(FPS)
                       
                        own.rotate(rotation)  
                        own.draw(update=True)  
        elif direction == 'left':
            if own.rotation != 90:
                if own.rotation > 90:
                    for rotation in reversed(range(90, own.rotation, own.speed)):
                        
                        Clock.tick(FPS)
                        
                        own.rotate(rotation)
                        own.draw(update=True)
                else:
                    for rotation in range(own.rotation, 90 + 1, own.speed):
                        
                        Clock.tick(FPS)
                        
                        own.rotate(rotation)
                        own.draw(update=True)
        elif direction == 'right':
            if own.rotation != 270:
                if own.rotation > 270:
                    for rotation in reversed(range(270, own.rotation, menu_car_speed)):
                        
                        Clock.tick(FPS)
                        
                        own.rotate(rotation)
                        own.draw(update=True)
                elif own.rotation < 90:
                    for rotation in reversed(range(-90, own.rotation, menu_car_speed)):
                        Clock.tick(FPS)
                        
                        own.rotate(rotation)
                        own.draw(update=True)
                    own.rotation = 270
                else:
                    for rotation in range(own.rotation, 270 + 1, menu_car_speed):
                        
                        Clock.tick(FPS)
                        
                        own.rotate(rotation)
                        own.draw(update=True)

class Car(pygame.sprite.Sprite):
    def __init__(own, player: Player):
        super().__init__()
        own.player = player
        own.is_player = own.player.is_player
        own.id = own.player.id
        if own.id > 6 or own.id < 0:
            raise ValueError(
                'Car | own.id should only be between 0 and 5, not ' + str(own.player.id))
        
        own.start_pos = own.player.start_pos
        own.original_start_position = Map.start_pos(own.start_pos)
        
        own.original_start_rotation = own.original_start_position[2]
        own.original_start_position = own.original_start_position[:2]
        own.vehicle = own.player.machine_name
        own._move_speed = global_car_move_speed
        own._rotation_speed = global_car_rotation_speed
        if own.vehicle == 'Family Car':
            own.max_speed = 3
            own.max_rotation_speed = 2
            own.Strength = 4
        elif own.vehicle == 'Sports Car':
            own.max_speed = 4
            own.max_rotation_speed = 3
            own.Strength = 2
        elif own.vehicle == 'Luxury Car':
            own.max_speed = 3
            own.max_rotation_speed = 3
            own.Strength = 3
        elif own.vehicle == 'Truck':
            own.max_speed = 2
            own.max_rotation_speed = 2
            own.Strength = 5
        elif own.vehicle == 'Race Car':
            own.max_speed = 5
            own.max_rotation_speed = 3
            own.Strength = 1
        own.set_move_speed(own.max_speed)
        own.set_rotation_speed(own.max_rotation_speed)
        
        own.colour = own.player.car_color
        own.image_dir = bin.car(own.colour, own.vehicle)
        own.image = pygame.transform.scale(
            pygame.image.load(own.image_dir).convert(), (40, 70))
        own.image.set_colorkey(BLACK)
        own._origin_img = own.image
        own._dmg_img = None
        own.damage = 0
        own.size = own.image.get_size()
        
        own.rect = own.image.get_rect()
        own.rect.center = own.original_start_position
        own.pos_x = own.rect.x
        own.pos_y = own.rect.y
        own.rotation = own.original_start_rotation
        
        own.mask = pygame.mask.from_surface(own.image)  
        own.mask_overlap = None  
        own.mask_area = None  
        own.mask_size = None
        own.collision = False
        own.finished = False
        
        own._up = None
        own._down = None
        own._left = None
        own._right = None
        own.input_type = None
        own.test_alpha = None
        own.set_controls(own.player.controls)
        own._allow_forwards = True
        own._allow_reverse = True
        own._pressed_keys = None
        own._boost_timeout = 0
        own.debris_penalty = 0
        own.debris_damage = 0
        own._current_speed = 0
        
        own._boost_frames = []
        own._boost_ani_frame = -1
        for frames in range(0, 4):
            own._boost_frames.append(pygame.transform.scale(pygame.image.load(bin.animation(
                'flame', frames, car_num=own.vehicle)), (own.size[0], own.size[1] + 20)))
        own._smoke_ani_frame = -1
        own._repair_ani_frame = -1
        own._ani_frame = None
        own._ani_frame_rect = None
        own.lightning_animation = False
        own.lightning_target = False
        own.lightning_indicator = pygame.transform.scale(
            pygame.image.load(bin.power_up('lightning')), (16, 16))
        own._lightning_frame = None
        
        own.name = own.player.name
        own._name_rect = None
        
        own._lap_halfway = True
        own.laps = 0
        
        own.checkpoint_count = -1
        own.checkpoint_time = 99999999999
        
        own._collision_sound = False
        
        own.move(own.original_start_position[0],
                 own.original_start_position[1])
        if own.rotation != 0:  
            own.rotate(own.rotation)

    def set_move_speed(own, speed):
        if speed < 1:
            speed = 1
        if speed != 10:  
            own._current_speed = speed
        own._move_speed = global_car_move_speed + speed
    
    def set_rotation_speed(own, speed):
        own._rotation_speed = global_car_rotation_speed + speed
    
    def set_controls(own, control: str or pygame.joystick.Joystick):
        if control == 'wasd':
            own.input_type = 'wasd'
            own._up = pygame.K_w
            own._down = pygame.K_s
            own._left = pygame.K_a
            own._right = pygame.K_d
        elif control == 'arrows':
            own.input_type = 'arrows'
            own._up = pygame.K_UP
            own._down = pygame.K_DOWN
            own._left = pygame.K_LEFT
            own._right = pygame.K_RIGHT
        else:
            raise ValueError("Car | controls is not == 'wasd' or 'arrows'"
                             " or test_alpha : {0} as {1}".format(control, type(control)))
    
    def check_checkpoints(own, checkpoint_rectangles):
        if not own.finished:
            for checkpoint in checkpoint_rectangles:  
                if checkpoint.colliderect(own.rect) and \
                        own.checkpoint_count != checkpoint_rectangles.index(checkpoint):
                    own.checkpoint_count = checkpoint_rectangles.index(
                        checkpoint)  
                    own.checkpoint_time = pygame.time.get_ticks()  
                    if not own._lap_halfway and own.checkpoint_count == \
                            ceil(len(checkpoint_rectangles) / 2):  
                        own._lap_halfway = True  
                    if own._lap_halfway and checkpoint_rectangles.index(checkpoint) == 0 and \
                            own.checkpoint_count <= checkpoint_rectangles.index(checkpoint):  
                        own._lap_halfway = False  
                        own.laps += 1
    
    def check_track_collisions(own):
        if not own.collision or own.collision == 'track':
            own.mask_overlap = own.mask.overlap(
                Track_mask, (-own.rect.left, -own.rect.top))
            if own.mask_overlap:
                own.collision = 'track'
                if not own._collision_sound:
                    play_music('collision')
                    own._collision_sound = True
                    if own.damage < own.Strength:
                        own.damage += 1
                    if own.damage:
                        own._dmg_img = pygame.transform.rotate(pygame.transform.scale(pygame.image.load(
                            bin.car_damage(own.vehicle, own.damage)), own.size), own.rotation)
                        own._dmg_img.set_colorkey(WHITE)
                        
                        own.image.blit(own._dmg_img, (0, 0))
                
                own.mask_area = own.mask.overlap_area(
                    Track_mask, (-own.rect.left, -own.rect.top))
                own.mask_size = own.mask.count()
                if own.rotation <= 45 or own.rotation >= 315:  
                    
                    
                    if own.image.get_size()[1] // 2 > own.mask_overlap[1]:
                        own._allow_forwards = False  
                        own._allow_reverse = True
                        
                    
                    elif own.image.get_size()[1] // 2 < own.mask_overlap[1]:
                        own._allow_forwards = True  
                        own._allow_reverse = False
                        
                elif 45 < own.rotation < 135:  
                    
                    
                    if own.image.get_size()[0] // 2 > own.mask_overlap[0]:
                        own._allow_forwards = False  
                        own._allow_reverse = True
                        
                    
                    elif own.image.get_size()[0] // 2 < own.mask_overlap[0]:
                        own._allow_forwards = True  
                        own._allow_reverse = False
                        
                elif 135 <= own.rotation <= 225:  
                    
                    
                    if own.image.get_size()[1] // 2 < own.mask_overlap[1]:
                        own._allow_forwards = False  
                        own._allow_reverse = True
                        
                    
                    elif own.image.get_size()[1] // 2 > own.mask_overlap[1]:
                        own._allow_forwards = True  
                        own._allow_reverse = False
                        
                elif 225 < own.rotation < 315:  
                    
                    
                    if own.image.get_size()[0] // 2 < own.mask_overlap[0]:
                        own._allow_forwards = False  
                        own._allow_reverse = True
                        
                    
                    elif own.image.get_size()[0] // 2 > own.mask_overlap[0]:
                        own._allow_forwards = True  
                        own._allow_reverse = False
                        
                
                if own.mask_area > own.mask_size // 2:
                    
                    own.move(
                        own.original_start_position[0], own.original_start_position[1])
                    own.rotate(own.original_start_rotation)
                    
            else:  
                own.collision = False
                own._collision_sound = False
                if not own._allow_forwards:  
                    own._allow_forwards = True
                if not own._allow_reverse:
                    own._allow_reverse = True

    def check_car_collision(own, sprite):
        if not own.finished and not sprite.finished and (not own.collision or own.collision == sprite):
            own.mask_overlap = pygame.sprite.collide_mask(own, sprite)
            if own.mask_overlap:
                own.collision = sprite
                if not own._collision_sound:
                    play_music('collision')
                    own._collision_sound = True
                    if own.damage < own.Strength:
                        own.damage += 1
                    if own.damage:
                        own._dmg_img = pygame.transform.rotate(pygame.transform.scale(pygame.image.load(
                            bin.car_damage(own.vehicle, own.damage)), own.size), own.rotation)
                        own._dmg_img.set_colorkey(WHITE)
                        
                        own.image.blit(own._dmg_img, (0, 0))
                
                own.mask_area = own.mask.overlap_area(
                    sprite.mask, (-own.rect.left, -own.rect.top))
                own.mask_size = own.mask.count()
                if own.rotation <= 45 or own.rotation >= 315:  
                    
                    
                    if own.image.get_size()[1] // 2 > own.mask_overlap[1]:
                        own._allow_forwards = False  
                        own._allow_reverse = True
                        
                    
                    elif own.image.get_size()[1] // 2 < own.mask_overlap[1]:
                        own._allow_forwards = True  
                        own._allow_reverse = False
                        
                elif 45 < own.rotation < 135:  
                    
                    
                    if own.image.get_size()[0] // 2 > own.mask_overlap[0]:
                        own._allow_forwards = False  
                        own._allow_reverse = True
                        
                    
                    elif own.image.get_size()[0] // 2 < own.mask_overlap[0]:
                        own._allow_forwards = True  
                        own._allow_reverse = False
                        
                elif 135 <= own.rotation <= 225:  
                    
                    
                    if own.image.get_size()[1] // 2 < own.mask_overlap[1]:
                        own._allow_forwards = False  
                        own._allow_reverse = True
                        
                    
                    elif own.image.get_size()[1] // 2 > own.mask_overlap[1]:
                        own._allow_forwards = True  
                        own._allow_reverse = False
                        
                elif 225 < own.rotation < 315:  
                    
                    
                    if own.image.get_size()[0] // 2 < own.mask_overlap[0]:
                        own._allow_forwards = False  
                        own._allow_reverse = True
                        
                    
                    elif own.image.get_size()[0] // 2 > own.mask_overlap[0]:
                        own._allow_forwards = True  
                        own._allow_reverse = False
                        
                
                if own.mask_area > own.mask_size // 1.5:
                    
                    own.move(
                        own.original_start_position[0], own.original_start_position[1])
                    own.rotate(own.original_start_rotation)
                    
            else:  
                own.collision = False
                own._collision_sound = False
                if not own._allow_forwards:  
                    own._allow_forwards = True
                if not own._allow_reverse:
                    own._allow_reverse = True
    
    def move(own, x, y):  
        own.pos_x = x
        own.pos_y = y
        own.rect.center = x, y

    def rotate(own, degree):  
        own.rotation = degree  
        if global_car_rotation_speed + 1 >= own.rotation:  
            own.rotation = 360
        elif own.rotation >= 360 - (global_car_rotation_speed + 1):
            own.rotation = 0
        elif 90 - (global_car_rotation_speed + 1) <= own.rotation <= 90 + (global_car_rotation_speed + 1):
            own.rotation = 90
        elif 180 - (global_car_rotation_speed + 1) <= own.rotation <= 180 + (global_car_rotation_speed + 1):
            own.rotation = 180
        elif 270 - (global_car_rotation_speed + 1) <= own.rotation <= 270 + (global_car_rotation_speed + 1):
            own.rotation = 270
        own.image = pygame.transform.rotate(pygame.transform.scale(pygame.image.load(
            own.image_dir).convert(), own.size), own.rotation)  
        own.image.set_colorkey(BLACK)
        own.mask = pygame.mask.from_surface(
            own.image)  
        if 0 < own.damage <= own.Strength:
            own._dmg_img = pygame.transform.rotate(pygame.transform.scale(pygame.image.load(
                bin.car_damage(own.vehicle, own.damage)), own.size), own.rotation)  
            own._dmg_img.set_colorkey(WHITE)
            
            own.image.blit(own._dmg_img, (0, 0))
        own.rect = own.image.get_rect()  
        if own.finished:
            own.image.set_alpha(150)
        own.rect.center = own.pos_x, own.pos_y

    def power_up(own, ver):
        if ver == 'repair':
            play_music('repair')
            own.damage = 0
            own._repair_ani_frame = 0
        elif ver == 'boost':
            play_music('boost')
            if not own._boost_timeout:
                own._boost_timeout = pygame.time.get_ticks(
                ) + 2000 + (5000 - own._current_speed * 1000)
                own.set_move_speed(10)
                own.set_rotation_speed(5)
                own._boost_ani_frame = 0
            else:
                own._boost_timeout += 2000 + (5000 - own._current_speed * 1000)
        elif ver == 'bullet':
            if own._boost_timeout:
                own._boost_timeout = 0
                own._boost_ani_frame = -1
            play_music('bullet')
            own.debris_damage = own.damage
            own.debris_penalty = pygame.time.get_ticks(
            ) + 2000 + (5000 - own._current_speed * 1000)
            own._smoke_ani_frame = 0
            own.damage = own.Strength
            own.rotate(own.rotation + 1)  
            own.rotate(own.rotation - 1)
        elif ver == 'lightning':
            if ver == 'lightning' and not own.collision and not own.debris_penalty:
                own.lightning_animation = pygame.time.get_ticks() // 70

    def check_inputs(own):  
        if own.input_type == 'wasd' or own.input_type == 'arrows':
            own._pressed_keys = pygame.key.get_pressed()  
            
            if own._pressed_keys[own._up] and own._pressed_keys[own._down]:
                return  
            if own._pressed_keys[own._up] and own._allow_forwards:  
                own.move(own.pos_x - round(cos(radians(own.rotation - 90)) * own._move_speed),
                         own.pos_y + round(sin(radians(own.rotation - 90)) * own._move_speed))
                if own._pressed_keys[own._left]:  
                    
                    own.rotate(own.rotation + own._rotation_speed)
                elif own._pressed_keys[own._right]:  
                    own.rotate(own.rotation - own._rotation_speed)
            
            elif own._pressed_keys[own._down] and own._allow_reverse:
                own.move(own.pos_x + round(cos(radians(own.rotation - 90)) * own._move_speed),  
                         own.pos_y - round(sin(radians(own.rotation - 90)) * own._move_speed))  
                if own._pressed_keys[own._left]:  
                    
                    own.rotate(own.rotation - own._rotation_speed)
                elif own._pressed_keys[own._right]:  
                    own.rotate(own.rotation + own._rotation_speed)

    def draw(own, game_surface=Window):
        game_surface.blit(
            own.image, (own.rect.left, own.rect.top))  
        draw_side_arrow((own.rect.centerx, own.rect.top - 14), 'down',  
                        width=10, height=10, border=own.colour, border_width=3, surface=game_surface)
        own._name_rect = render_text_on_screen(own.rect.centerx, own.rect.top - 35,
                                               own.name, WHITE, 12, game_surface=game_surface, return_rect=True)
        if own.lightning_target:
            game_surface.blit(own.lightning_indicator, (own.rect.centerx - own._name_rect.width/2 -
                                                        own.lightning_indicator.get_width() - 8, own.rect.top - 38))
        if own._boost_ani_frame == 4 and own._boost_timeout:  
            own._boost_ani_frame = 0  
        elif not own._boost_timeout and own._boost_ani_frame != -1:  
            own._boost_ani_frame = -1  
        if own._boost_timeout and own._boost_ani_frame >= 0:  
            own._ani_frame = pygame.transform.rotate(
                own._boost_frames[own._boost_ani_frame], own.rotation)
            own._ani_frame_rect = own._ani_frame.get_rect()
            own._ani_frame_rect.center = own.rect.center
            game_surface.blit(
                own._ani_frame, (own._ani_frame_rect.left, own._ani_frame_rect.top))
            own._boost_ani_frame += 1  
        if own._smoke_ani_frame >= 14 and own.debris_penalty:  
            own._smoke_ani_frame = 0  
        elif not own.debris_penalty and own._smoke_ani_frame >= 14:  
            own._smoke_ani_frame = -1  
        if own._smoke_ani_frame >= 0:  
            own._ani_frame = smoke_frames[floor(own._smoke_ani_frame / 2)]
            own._ani_frame_rect = own._ani_frame.get_rect()
            own._ani_frame_rect.centerx = own.rect.centerx
            own._ani_frame_rect.bottom = own.rect.centery
            game_surface.blit(
                own._ani_frame, (own._ani_frame_rect.left, own._ani_frame_rect.top))
            own._smoke_ani_frame += 1  
        if own._repair_ani_frame >= 22:  
            own._repair_ani_frame = -1  
        if own._repair_ani_frame >= 0:
            own._ani_frame = repair_frames[floor(own._repair_ani_frame / 2)]
            own._ani_frame_rect = own._ani_frame.get_rect()
            own._ani_frame_rect.center = own.rect.center
            game_surface.blit(
                own._ani_frame, (own._ani_frame_rect.left, own._ani_frame_rect.top))
            own._repair_ani_frame += 1  
        if own.lightning_animation:  
            own._lightning_frame = pygame.time.get_ticks() // 70 - own.lightning_animation
            if own._lightning_frame < 15:
                game_surface.blit(
                    lightning_frames[own._lightning_frame], (own.rect.centerx - 64, own.rect.centery - 128))
                if own._lightning_frame == 2:
                    play_music('lightning')
                elif own._lightning_frame == 3:
                    if own._boost_timeout:
                        own._boost_timeout = 0
                        own._boost_ani_frame = -1
                    own.debris_damage = own.damage
                    own.debris_penalty = pygame.time.get_ticks() + 3000 + \
                        (own._move_speed - global_car_move_speed) * 1000
                    own._smoke_ani_frame = 0  
                    own.damage = own.Strength
                    own.rotate(own.rotation + 1)  
                    own.rotate(own.rotation - 1)

    def update(own):  
        if own.laps > Total_laps and not own.finished:
            own.finished = True
            if not own.image.get_alpha():
                own.image.set_alpha(150)
        if own._boost_timeout and own._boost_timeout < pygame.time.get_ticks():  
            own._boost_timeout = 0  
            own.set_move_speed(own._current_speed)
            own.set_rotation_speed(own.max_rotation_speed)
        elif own.debris_penalty and own.debris_penalty < pygame.time.get_ticks():  
            own.debris_penalty = 0  
            own.damage = own.debris_damage
            own.rotate(own.rotation + 1)
            own.rotate(own.rotation - 1)
        elif not own._boost_timeout:
            if own.damage:  
                own.set_move_speed(
                    round(own.max_speed - (own.max_speed / (own.Strength / own.damage))))
                own.set_rotation_speed(own.max_rotation_speed)
            elif own._move_speed != own.max_speed or own._rotation_speed != own.max_rotation_speed:
                own.set_move_speed(own.max_speed)
                own.set_rotation_speed(own.max_rotation_speed)
        if not own.debris_penalty:
            own.check_inputs()

class Enemy_machine(pygame.sprite.Sprite):
    def __init__(own, player: Player):
        super().__init__()
        own.player = player
        own.is_player = own.player.is_player
        own.id = own.player.id
        own.start_pos = own.player.start_pos
        own.original_start_position = Map.start_pos(own.start_pos)
        
        own.original_start_rotation = own.original_start_position[2]
        own.original_start_position = own.original_start_position[:2]
        own._move_speed = global_car_move_speed
        own._rotation_speed = global_car_rotation_speed
        own.vehicle = own.player.machine_name
        if own.vehicle == 'Family Car':
            own.max_speed = 3
            own.max_rotation_speed = 2
            own.Strength = 4
        elif own.vehicle == 'Sports Car':
            own.max_speed = 4
            own.max_rotation_speed = 3
            own.Strength = 2
        elif own.vehicle == 'Luxury Car':
            own.max_speed = 3
            own.max_rotation_speed = 3
            own.Strength = 3
        elif own.vehicle == 'Truck':
            own.max_speed = 2
            own.max_rotation_speed = 2
            own.Strength = 5
        elif own.vehicle == 'Race Car':
            own.max_speed = 5
            own.max_rotation_speed = 3
            own.Strength = 1
        own.set_move_speed(own.max_speed)
        own.set_rotation_speed(own.max_rotation_speed)
        
        own.colour = own.player.car_color
        own.image_dir = bin.car(own.colour, own.vehicle)
        own.image = pygame.transform.scale(
            pygame.image.load(own.image_dir).convert(), (40, 70))
        own.image.set_colorkey(BLACK)
        own._origin_img = own.image
        own._dmg_img = None
        own.damage = 0
        own.size = own.image.get_size()
        
        own.rect = own.image.get_rect()
        own.rect.center = own.original_start_position
        own.pos_x = own.rect.x
        own.pos_y = own.rect.y
        own.rotation = own.original_start_rotation
        
        own.mask = pygame.mask.from_surface(own.image)  
        own.mask_overlap = None  
        own.mask_area = None  
        own.mask_size = None
        own.collision = False
        own.finished = False
        own.collision_time = 0
        own._boost_timeout = 0
        own.debris_penalty = 0
        own.debris_damage = 0
        own._current_speed = 0
        
        own._boost_frames = []
        own._boost_ani_frame = -1
        for frames in range(0, 4):
            own._boost_frames.append(pygame.transform.scale(pygame.image.load(bin.animation(
                'flame', frames, car_num=own.vehicle)), (own.size[0], own.size[1] + 20)))
        own._smoke_ani_frame = -1
        own._repair_ani_frame = -1
        own._ani_frame = None
        own._ani_frame_rect = None
        own.lightning_animation = False
        own.lightning_target = False
        own.lightning_indicator = pygame.transform.scale(
            pygame.image.load(bin.power_up('lightning')), (16, 16))
        own._lightning_frame = None
        
        own.allow_forward = True
        own.allow_back = True
        own.allow_left = True
        own.allow_right = True
        own.move_forward = False
        own.move_back = False
        own.move_left = False
        own.move_right = False
        own.reverse = False
        own.reverse_time = 0
        own._move_rect_radius = 90  
        own._move_rect_offset = 28  
        own._move_layer_offset = 35
        own._avoid_rect_radius = 60
        own._avoid_rect_offset = 15
        own._avoid_layer_offset = 32
        own.movements_obj = []
        for layer_num in range(0, 4):
            layer = []
            for index in range(0, 4):
                game_surface = pygame.surface.Surface((10, 10))
                rect = game_surface.get_rect()
                mask = pygame.mask.from_surface(game_surface)
                rect.center = own.rect.centerx, own.rect.centery - own._move_rect_radius
                game_surface.fill(RED)
                layer.append(Object(game_surface, rect, mask))
            own.movements_obj.append(tuple(layer))
        own.movements_obj = tuple(own.movements_obj)
        own.avoidance_obj = []
        for layer_num in range(0, 5):
            layer = []
            for index in range(0, 4):
                game_surface = pygame.surface.Surface((8, 8))
                rect = game_surface.get_rect()
                mask = pygame.mask.from_surface(game_surface)
                rect.center = own.rect.centerx, own.rect.centery - own._avoid_rect_radius
                game_surface.fill(GREEN)
                layer.append(Object(game_surface, rect, mask))
            own.avoidance_obj.append(tuple(layer))
        own.avoidance_obj = tuple(own.avoidance_obj)
        
        own.name = own.player.name[0]
        own._name_rect = None
        
        own._lap_halfway = True
        own.laps = 0
        
        own.checkpoint_count = -1
        own.checkpoint_time = 0
        own.prev_checkpoint_position = own.original_start_position
        own.prev_checkpoint_rotation = own.original_start_rotation
        
        own.collision_sound = False
        own.move(own.original_start_position[0],
                 own.original_start_position[1])
        if own.original_start_rotation != 0:  
            own.rotate(own.rotation)

    def set_move_speed(own, speed):
        if speed < 1:
            speed = 1
        if speed != 10:  
            own._current_speed = speed
        own._move_speed = global_car_move_speed + speed

    def set_rotation_speed(own, speed):
        own._rotation_speed = global_car_rotation_speed + speed

    def check_checkpoints(own, checkpoint_rectangles):
        if not own.finished:
            for checkpoint in checkpoint_rectangles:
                if checkpoint.colliderect(own.rect) and \
                        own.checkpoint_count != checkpoint_rectangles.index(checkpoint):
                    own.checkpoint_count = checkpoint_rectangles.index(
                        checkpoint)
                    own.checkpoint_time = pygame.time.get_ticks()
                    if not own._lap_halfway and own.checkpoint_count == floor(len(checkpoint_rectangles) / 2):
                        own._lap_halfway = True
                    if own._lap_halfway and own.checkpoint_count == 0:
                        own._lap_halfway = False
                        own.laps += 1
    
    def check_track_collisions(own):
        if not own.collision or own.collision == 'track':  
            own.mask_overlap = own.mask.overlap(
                Track_mask, (-own.rect.left, -own.rect.top))
            if own.mask_overlap:
                own.collision = 'track'
                if not own.collision_time:
                    play_music('collision')
                    own.collision_time = pygame.time.get_ticks()
                    if own.damage < own.Strength:
                        own.damage += 1
                    if own.damage:
                        own._dmg_img = pygame.transform.rotate(pygame.transform.scale(pygame.image.load(
                            bin.car_damage(own.vehicle, own.damage)), own.size), own.rotation)
                        own._dmg_img.set_colorkey(WHITE)
                        
                        own.image.blit(own._dmg_img, (0, 0))
                
                own.mask_area = own.mask.overlap_area(
                    Track_mask, (-own.rect.left, -own.rect.top))
                own.mask_size = own.mask.count()
                if own.rotation <= 45 or own.rotation >= 315:  
                    
                    
                    if own.image.get_size()[1] // 2 > own.mask_overlap[1]:
                        own.allow_forward = False  
                        own.allow_back = True
                    
                    elif own.image.get_size()[1] // 2 < own.mask_overlap[1]:
                        own.allow_forward = True  
                        own.allow_back = False
                elif 45 < own.rotation < 135:  
                    
                    
                    if own.image.get_size()[0] // 2 > own.mask_overlap[0]:
                        own.allow_forward = False  
                        own.allow_back = True
                    
                    elif own.image.get_size()[0] // 2 < own.mask_overlap[0]:
                        own.allow_forward = True  
                        own.allow_back = False
                elif 135 <= own.rotation <= 225:  
                    
                    if own.image.get_size()[1] // 2 < own.mask_overlap[1]:
                        own.allow_forward = False  
                        own.allow_back = True
                    
                    elif own.image.get_size()[1] // 2 > own.mask_overlap[1]:
                        own.allow_forward = True  
                        own.allow_back = False
                elif 225 < own.rotation < 315:  
                    
                    if own.image.get_size()[0] // 2 < own.mask_overlap[0]:
                        own.allow_forward = False  
                        own.allow_back = True
                    
                    elif own.image.get_size()[0] // 2 > own.mask_overlap[0]:
                        own.allow_forward = True  
                        own.allow_back = False
                
                if own.mask_area > own.mask_size // 1.5:
                    
                    own.move(
                        own.original_start_position[0], own.original_start_position[1])
                    own.rotate(own.original_start_rotation)
            else:  
                own.collision = False
                own.collision_time = 0
                own.collision_sound = False

    def check_car_collision(own, sprite):
        if not own.finished and not sprite.finished and (not own.collision or own.collision == sprite):
            own.mask_overlap = pygame.sprite.collide_mask(own, sprite)
            if own.mask_overlap:
                own.collision = sprite
                if not own.collision_time:
                    play_music('collision')
                    own.collision_time = pygame.time.get_ticks()
                    if own.damage < own.Strength:
                        own.damage += 1
                    if own.damage:
                        own._dmg_img = pygame.transform.rotate(pygame.transform.scale(pygame.image.load(
                            bin.car_damage(own.vehicle, own.damage)), own.size), own.rotation)
                        own._dmg_img.set_colorkey(WHITE)
                        
                        own.image.blit(own._dmg_img, (0, 0))
                
                own.mask_area = own.mask.overlap_area(
                    sprite.mask, (-own.rect.left, -own.rect.top))
                own.mask_size = own.mask.count()
                if own.rotation <= 45 or own.rotation >= 315:  
                    
                    if own.image.get_size()[1] // 2 > own.mask_overlap[1]:
                        own.allow_forward = False  
                        own.allow_back = True
                    
                    elif own.image.get_size()[1] // 2 < own.mask_overlap[1]:
                        own.allow_forward = True  
                        own.allow_back = False
                elif 45 < own.rotation < 135:  
                    
                    if own.image.get_size()[0] // 2 > own.mask_overlap[0]:
                        own.allow_forward = False  
                        own.allow_back = True
                    
                    elif own.image.get_size()[0] // 2 < own.mask_overlap[0]:
                        own.allow_forward = True  
                        own.allow_back = False
                elif 135 <= own.rotation <= 225:  
                    
                    if own.image.get_size()[1] // 2 < own.mask_overlap[1]:
                        own.allow_forward = False  
                        own.allow_back = True
                    
                    elif own.image.get_size()[1] // 2 > own.mask_overlap[1]:
                        own.allow_forward = True  
                        own.allow_back = False
                elif 225 < own.rotation < 315:  
                    
                    if own.image.get_size()[0] // 2 < own.mask_overlap[0]:
                        own.allow_forward = False  
                        own.allow_back = True
                    
                    elif own.image.get_size()[0] // 2 > own.mask_overlap[0]:
                        own.allow_forward = True  
                        own.allow_back = False
                
                if own.mask_area > own.mask_size // 1.5:
                    
                    own.move(
                        own.original_start_position[0], own.original_start_position[1])
                    own.rotate(own.original_start_rotation)
            else:  
                own.collision = False
                own.collision_sound = False
                own.collision_time = 0

    def move(own, x, y):  
        for layer in own.movements_obj:
            for obj in [layer[0], layer[3]]:
                obj.rect.centerx -= own.pos_x - x
                obj.rect.centery -= own.pos_y - y
        for layer in own.avoidance_obj:
            for obj in [layer[0], layer[3]]:
                obj.rect.centerx -= own.pos_x - x
                obj.rect.centery -= own.pos_y - y
        own.pos_x = x
        own.pos_y = y
        own.rect.center = x, y

    def rotate(own, degree):  
        own.rotation = degree  
        if global_car_rotation_speed + 1 >= own.rotation:  
            own.rotation = 360
        elif own.rotation >= 360 - (global_car_rotation_speed + 1):
            own.rotation = 0
        elif 90 - (global_car_rotation_speed + 1) <= own.rotation <= 90 + (global_car_rotation_speed + 1):
            own.rotation = 90
        elif 180 - (global_car_rotation_speed + 1) <= own.rotation <= 180 + (global_car_rotation_speed + 1):
            own.rotation = 180
        elif 270 - (global_car_rotation_speed + 1) <= own.rotation <= 270 + (global_car_rotation_speed + 1):
            own.rotation = 270
        own.image = pygame.transform.rotate(
            own._origin_img.copy(), own.rotation)  
        own.image.set_colorkey(BLACK)
        own.mask = pygame.mask.from_surface(
            own.image)  
        if 0 < own.damage <= own.Strength:
            own._dmg_img = pygame.transform.rotate(pygame.transform.scale(pygame.image.load(
                bin.car_damage(own.vehicle, own.damage)), own.size), own.rotation)  
            own._dmg_img.set_colorkey(WHITE)
            
            own.image.blit(own._dmg_img, (0, 0))
        own.rect = own.image.get_rect()  
        if own.finished:
            own.image.set_alpha(150)
        own.rect.center = own.pos_x, own.pos_y
        for layer in own.movements_obj:
            layer_num = own.movements_obj.index(layer)
            own.rotate_rect(layer[0].rect, -own.rotation - own._move_rect_offset,
                            own._move_rect_radius + own._move_layer_offset * layer_num)
            own.rotate_rect(layer[3].rect, -own.rotation + own._move_rect_offset,
                            own._move_rect_radius + own._move_layer_offset * layer_num)
        for layer in own.avoidance_obj:
            layer_num = own.avoidance_obj.index(layer)
            own.rotate_rect(layer[0].rect, -own.rotation - own._avoid_rect_offset,
                            own._avoid_rect_radius + own._avoid_layer_offset * layer_num)
            own.rotate_rect(layer[3].rect, -own.rotation + own._avoid_rect_offset,
                            own._avoid_rect_radius + own._avoid_layer_offset * layer_num)
            
    def rotate_rect(own, rect, angle, radius):
        origin_x, origin_y = own.pos_x, own.pos_y
        rect.center = origin_x, origin_y - radius
        x, y = rect.centerx, rect.centery
        angle = radians(angle)
        rect.centerx = cos(angle) * (x - origin_x) - \
            sin(angle) * (y - origin_y) + origin_x
        rect.centery = sin(angle) * (x - origin_x) + \
            cos(angle) * (y - origin_y) + origin_y
        
    def reset_to_checkpoint(own):
        own.collision_time = 0
        own.allow_forward = True
        own.allow_back = True
        own.collision = False
        
        own.move(*own.prev_checkpoint_position)
        own.rotate(own.prev_checkpoint_rotation)

    def decide_movement(own):
        
        own.move_forward = False if own.reverse else True
        own.move_back = own.reverse
        own.move_left = False
        own.move_right = False
        if not own.collision and not own.reverse:
            own.allow_forward = True  
            own.allow_back = True
            own.allow_left = True
            own.allow_right = True
        trk_fl = 4
        trk_fr = 4
        
        for layer in reversed(own.movements_obj):
            obj = layer[0]
            if obj.mask.overlap(Track_mask, (-obj.rect.left, -obj.rect.top)):
                
                trk_fl = own.movements_obj.index(layer) + 1
            obj = layer[3]
            if obj.mask.overlap(Track_mask, (-obj.rect.left, -obj.rect.top)):
                trk_fr = own.movements_obj.index(layer) + 1
        veh_fl = 5
        veh_fr = 5
        
        if not own.finished:
            for layer in reversed(own.avoidance_obj):
                for index in range(len(Machines_available)):
                    
                    if index != own.id and not Machines_available[index].finished:
                        veh = Machines_available[index]
                        obj = layer[0]
                        if obj.mask.overlap(veh.mask, (veh.rect.x - obj.rect.x, veh.rect.y - obj.rect.y)):
                            
                            if own.avoidance_obj.index(layer) < veh_fl:
                                veh_fl = own.avoidance_obj.index(layer)
                        obj = layer[3]
                        if obj.mask.overlap(veh.mask, (veh.rect.x - obj.rect.x, veh.rect.y - obj.rect.y)):
                            if own.avoidance_obj.index(layer) < veh_fr:
                                veh_fr = own.avoidance_obj.index(layer)
        if (trk_fl < 4 or trk_fr < 4) and (veh_fl < 5 or veh_fr < 5):  
            if trk_fl == 2:
                own.move_right = True
            if trk_fr == 2:
                own.move_left = True
            if veh_fl == 1:
                own.move_right = True
            if veh_fr == 1:
                own.move_left = True
        else:  
            if trk_fl <= 1:
                own.allow_left = False
            if trk_fr <= 1:
                own.allow_right = False
            if not own.allow_left and not own.allow_right:
                if trk_fl > trk_fr:
                    own.allow_left = True
                elif trk_fl < trk_fr:
                    own.allow_right = True
            if trk_fl == 1:
                own.allow_left = False
            if trk_fl <= 3:
                own.move_right = True
            if trk_fr == 1:
                own.allow_right = False
            if trk_fr <= 3:
                own.move_left = True
            if own.move_left and own.move_right:
                if trk_fl > trk_fr:
                    own.move_left = False
                    own.move_right = True
                elif trk_fl < trk_fr:
                    own.move_left = True
                    own.move_right = False
                else:
                    own.move_left = False
                    own.move_right = False
            if veh_fl <= 3:
                own.move_right = True
            if veh_fr <= 3:
                own.move_left = True
            if own.move_left and own.move_right:
                if veh_fl > veh_fr:
                    own.move_left = False
                elif veh_fl < veh_fr:
                    own.move_right = False
                else:
                    own.move_left = False
                    own.move_right = False

    def take_movement(own):  
        own.decide_movement()  
        if own.move_forward and own.allow_forward:  
            own.move(own.pos_x - round(cos(radians(own.rotation - 90)) * own._move_speed),
                     own.pos_y + round(sin(radians(own.rotation - 90)) * own._move_speed))
            if own.move_left and own.allow_left:  
                own.rotate(own.rotation + own._rotation_speed + 1)
            elif own.move_right and own.allow_right:  
                own.rotate(own.rotation - own._rotation_speed - 1)
        elif own.move_back and own.allow_back:  
            own.move(own.pos_x + round(cos(radians(own.rotation - 90)) * own._move_speed),
                     own.pos_y - round(sin(radians(own.rotation - 90)) * own._move_speed))
            if own.move_left and own.allow_left:  
                own.rotate(own.rotation + own._rotation_speed - 1)
            elif own.move_right and own.allow_right:  
                own.rotate(own.rotation - own._rotation_speed + 1)

    def power_up(own, ver):
        if ver == 'repair':
            play_music('repair')
            own.damage = 0
            own._repair_ani_frame = 0
        elif ver == 'boost':
            play_music('boost')
            if not own._boost_timeout:
                own._boost_timeout = pygame.time.get_ticks(
                ) + 2000 + (5000 - own._current_speed * 1000)
                own.set_move_speed(10)
                own.set_rotation_speed(5)
                own._boost_ani_frame = 0
            else:
                own._boost_timeout += 2000 + (5000 - own._current_speed * 1000)
        elif ver == 'bullet':
            if own._boost_timeout:
                own._boost_timeout = 0
                own._boost_ani_frame = -1
            play_music('bullet')
            own.debris_damage = own.damage
            own.debris_penalty = pygame.time.get_ticks(
            ) + 2000 + (5000 - own._current_speed * 1000)
            own._smoke_ani_frame = 0
            own.damage = own.Strength
            own.rotate(own.rotation + 1)  
            own.rotate(own.rotation - 1)
        elif ver == 'lightning':
            if ver == 'lightning' and not own.collision and not own.debris_penalty:
                own.lightning_animation = pygame.time.get_ticks() // 70

    def draw(own, game_surface=Window):
        game_surface.blit(
            own.image, (own.rect.left, own.rect.top))  
        draw_side_arrow((own.rect.centerx, own.rect.top - 14), 'down', width=10, height=10,
                        border=own.colour, border_width=3, surface=game_surface)
        own._name_rect = render_text_on_screen(
            own.rect.centerx, own.rect.top - 35, own.name, WHITE, 12, game_surface=game_surface, return_rect=True)
        if own.lightning_target:
            game_surface.blit(own.lightning_indicator, (own.rect.centerx - own._name_rect.width/2 -
                                                        own.lightning_indicator.get_width() - 8, own.rect.top - 38))
        if own._boost_ani_frame == 4 and own._boost_timeout:  
            own._boost_ani_frame = 0  
        elif not own._boost_timeout and own._boost_ani_frame != -1:  
            own._boost_ani_frame = -1  
        if own._boost_timeout and own._boost_ani_frame >= 0:  
            own._ani_frame = pygame.transform.rotate(
                own._boost_frames[own._boost_ani_frame], own.rotation)
            own._ani_frame_rect = own._ani_frame.get_rect()
            own._ani_frame_rect.center = own.rect.center
            game_surface.blit(
                own._ani_frame, (own._ani_frame_rect.left, own._ani_frame_rect.top))
            own._boost_ani_frame += 1  
        if own._smoke_ani_frame >= 14 and own.debris_penalty:  
            own._smoke_ani_frame = 0  
        elif not own.debris_penalty and own._smoke_ani_frame >= 14:  
            own._smoke_ani_frame = -1  
        if own._smoke_ani_frame >= 0:  
            own._ani_frame = smoke_frames[floor(own._smoke_ani_frame / 2)]
            own._ani_frame_rect = own._ani_frame.get_rect()
            own._ani_frame_rect.centerx = own.rect.centerx
            own._ani_frame_rect.bottom = own.rect.centery
            game_surface.blit(
                own._ani_frame, (own._ani_frame_rect.left, own._ani_frame_rect.top))
            own._smoke_ani_frame += 1  
        if own._repair_ani_frame >= 22:  
            own._repair_ani_frame = -1  
        if own._repair_ani_frame >= 0:
            own._ani_frame = repair_frames[floor(own._repair_ani_frame / 2)]
            own._ani_frame_rect = own._ani_frame.get_rect()
            own._ani_frame_rect.center = own.rect.center
            game_surface.blit(
                own._ani_frame, (own._ani_frame_rect.left, own._ani_frame_rect.top))
            own._repair_ani_frame += 1  
        if own.lightning_animation:  
            own._lightning_frame = pygame.time.get_ticks() // 70 - own.lightning_animation
            if own._lightning_frame < 15:
                game_surface.blit(
                    lightning_frames[own._lightning_frame], (own.rect.centerx - 64, own.rect.centery - 128))
                if own._lightning_frame == 2:
                    play_music('lightning')
                elif own._lightning_frame == 3:
                    if own._boost_timeout:
                        own._boost_timeout = 0
                        own._boost_ani_frame = -1
                    own.debris_damage = own.damage
                    own.debris_penalty = pygame.time.get_ticks() + 3000 + \
                        (own._move_speed - global_car_move_speed) * 1000
                    own._smoke_ani_frame = 0  
                    own.damage = own.Strength
                    own.rotate(own.rotation + 1)  
                    own.rotate(own.rotation - 1)

    def update(own):  
        if own.laps > Total_laps and not own.finished:
            own.finished = True
            if not own.image.get_alpha():
                own.image.set_alpha(150)
        if own._boost_timeout and own._boost_timeout < pygame.time.get_ticks():  
            own._boost_timeout = 0  
            own.set_move_speed(own._current_speed)
            own.set_rotation_speed(own.max_rotation_speed)
        elif own.debris_penalty and own.debris_penalty < pygame.time.get_ticks():  
            own.debris_penalty = 0  
            own.damage = own.debris_damage
            own.rotate(own.rotation + 1)
            own.rotate(own.rotation - 1)
        elif not own._boost_timeout:
            if own.damage:  
                own.set_move_speed(
                    round(own.max_speed - (own.max_speed / (own.Strength / own.damage))))
                own.set_rotation_speed(own.max_rotation_speed)
            elif own._move_speed != own.max_speed or own._rotation_speed != own.max_rotation_speed:
                own.set_move_speed(own.max_speed)
                own.set_rotation_speed(own.max_rotation_speed)
        if not own.debris_penalty:
            if own.collision_time != 0 and not own.reverse and \
                    pygame.time.get_ticks() >= own.collision_time + randint(600, 2000):  
                own.reverse = True
                own.reverse_time = pygame.time.get_ticks()
            elif own.reverse_time != 0 and own.reverse and \
                    pygame.time.get_ticks() >= own.reverse_time + randint(1000, 1500):  
                own.reverse_time = 0
                own.reverse = False
            elif own.collision_time != 0 and pygame.time.get_ticks() >= own.collision_time + 5000:  
                own.reset_to_checkpoint()
            else:  
                if not own.collision and own.collision_time:
                    own.collision_time = 0
                own.take_movement()

def vehicle_location():
    positions = []
    for vehicle in Machines_available:
        vehicle = vehicle.laps, vehicle.checkpoint_count, vehicle.checkpoint_time, vehicle
        positions.append(vehicle)  
    
    positions = sorted(positions, key=lambda tup: tup[2])
    
    positions = sorted(positions, key=lambda tup: tup[1], reverse=True)
    
    positions = sorted(positions, key=lambda tup: tup[0], reverse=True)
    vehicles = []
    for vehicle in positions:
        vehicles.append(vehicle[3])
    return vehicles

def quit():
    pygame.quit()
    sys.exit()

def map_demo():
    global map_prev_demo
    if Map.name != map_prev_demo[0]:
        game_surface = pygame.surface.Surface(map_preview_size)
        for layer in range(0, 3):
            game_surface.blit(pygame.transform.scale(
                pygame.image.load(Map.layer(layer)), map_preview_size), (0, 0))
        map_prev_demo = Map.name, game_surface

def main_menu_page(new_bg, pad_x1=0, pad_y1=0):
    new_bg = pygame.image.load('new_bg.jpg')
    Window.blit(new_bg, (pad_x1, pad_y1))  
    x = pad_x1 + CENTRE[0]
    y = pad_y1 + 100
    render_text_on_screen(x, y, 'Road Fighter', ORANGE,
                          100, bold=True, type1=True)  
    x = pad_x1 + 800
    y = pad_y1 + 940
    tile(x, y, 'dirt road', 76, grid=False)  
    tile(x + 65, y, 'dirt road', 1, grid=False)
    tile(x + 190, y, 'dirt road', 60, grid=False)
    render_text_on_screen(x + 160, y + 20, 'Quit', WHITE, 70)
    x = pad_x1 + 340
    y = pad_y1 + 324
    tile(x, y, 'dirt road', 76, grid=False)  
    tile(x + 65, y, 'dirt road', 1, grid=False)
    tile(x + 190, y, 'dirt road', 60, grid=False)
    render_text_on_screen(x + 160, y + 20, 'Race', WHITE, 70)
    x = pad_x1 + 1220
    y = pad_y1 + 324
    tile(x, y, 'dirt road', 76, grid=False)  
    tile(x + 128, y, 'dirt road', 1, grid=False)
    tile(x + 256, y, 'dirt road', 60, grid=False)
    render_text_on_screen(x + 190, y + 20, 'Settings', WHITE, 70)
    x = pad_x1 + 1220
    y = pad_y1 + 648
    tile(x, y, 'dirt road', 76, grid=False)  
    tile(x + 128, y, 'dirt road', 1, grid=False)
    tile(x + 256, y, 'dirt road', 60, grid=False)
    render_text_on_screen(x + 190, y + 20, 'Hints', WHITE, 70)
    x = pad_x1 + 340
    y = pad_y1 + 648
    tile(x, y, 'dirt road', 76, grid=False)  
    tile(x + 128, y, 'dirt road', 1, grid=False)
    tile(x + 205, y, 'dirt road', 60, grid=False)
    render_text_on_screen(x + 163, y + 20, 'Credits', WHITE, 70)

def choose_map_window(new_bg, pad_x1=0, pad_y1=0):
    new_bg = pygame.image.load('new_bg.jpg')
    Window.blit(new_bg, (pad_x1, pad_y1))
    x = pad_x1 + CENTRE[0]
    y = pad_y1 + 70
    render_text_on_screen(x, y, 'Choose your Location', ORANGE, 100)  
    x = pad_x1 + 528
    y = pad_y1 + 890
    tile(x, y, 'dirt road', 76, grid=False)  
    tile(x + 128, y, 'dirt road', 60, grid=False)
    render_text_on_screen(x + 130, y + 20, 'Back', WHITE, 70)
    x = pad_x1 + 1100
    y = pad_y1 + 890
    tile(x, y, 'dirt road', 76, grid=False)  
    tile(x + 65, y, 'dirt road', 1, grid=False)
    tile(x + 190, y, 'dirt road', 60, grid=False)
    render_text_on_screen(x + 160, y + 20, 'Select', WHITE, 70)
    
    Window.blit(map_prev_demo[1], (pad_x1 +
                map_preview_pos[0], pad_y1 + map_preview_pos[1]))
    pygame.draw.rect(Window, WHITE, (pad_x1 +
                     map_preview_pos[0], pad_y1 + map_preview_pos[1], *map_preview_size), 4)
    x = pad_x1 + CENTRE[0]
    y = pad_y1 + (map_preview_pos[1] - 70)
    text = str(maps.index.index(Map.name) + 1) + '. ' + Map.name
    render_text_on_screen(x, y, text, WHITE, 60)  
    draw_side_arrow((pad_x1 + (map_preview_pos[0] - 50),  
                     pad_y1 + (map_preview_pos[1] + map_preview_size[1] // 2)), 'left', width=40, height=80)
    draw_side_arrow((pad_x1 + (map_preview_pos[0] + map_preview_size[0] + 50),
                     pad_y1 + (map_preview_pos[1] + map_preview_size[1] // 2)), 'right', width=40, height=80)
    
def player_screen(new_bg, pad_x1=0, pad_y1=0):
    new_bg = pygame.image.load('new_bg.jpg')
    Window.blit(new_bg, (pad_x1, pad_y1))
    x = pad_x1 + CENTRE[0]
    y = pad_y1 + 115
    render_text_on_screen(x, y, 'Decide Your Players', ORANGE, 100)  
    x = pad_x1 + 210
    y = pad_y1 + 112
    tile(x, y, 'dirt road', 76, grid=False, scale=(100, 100))  
    tile(x + 100, y, 'dirt road', 60, grid=False, scale=(100, 100))
    render_text_on_screen(x + 100, y + 23, 'Back', WHITE, 55)
    if Player_amount == 1:
        player = Players[0]
        
        x = pad_x1 + CENTRE[0]
        y = pad_y1 + 240
        render_text_on_screen(x, y, 'Player 1 controls', WHITE, 50, type1=True)
        rect = render_controls(x, y + 140, player.controls, return_rect=True)
        if type(player.controls) == str:
            draw_side_arrow((pad_x1 + 840, pad_y1 + 380),
                            'left', width=25, height=50)
            draw_side_arrow((pad_x1 + 1080, pad_y1 + 380),
                            'right', width=25, height=50)
        x = pad_x1 + CENTRE[0]
        y = pad_y1 + CENTRE[1] + 100
        
        render_text_on_screen(x, y, 'Player 1 Name', WHITE, 50, type1=True)
        
        pygame.draw.line(Window, WHITE, (x - 200, y + 160),
                         (x + 200, y + 160), 4)
        
        rect = render_text_on_screen(
            x, y + 115, player.name, WHITE, 50, return_rect=True)
        
        if (pygame.time.get_ticks() // 530) % 2 and selected_text_entry == 1:
            pygame.draw.line(Window, WHITE, (x + 5 + rect.width //
                             2, y + 124), (x + 5 + rect.width // 2, y + 152), 3)
        
        if selected_text_entry != 1 and not player.name:
            if (pygame.time.get_ticks() // 1060) % 2:
                render_text_on_screen(
                    x, y + 115, 'Enter name', V_LIGHT_GREY, 50)
            else:
                render_text_on_screen(x, y + 115, 'Enter name', LIGHT_GREY, 50)
    elif Player_amount >= 2:
        
        player = Players[0]
        
        x = pad_x1 + 560
        y = pad_y1 + 240
        render_text_on_screen(x, y, 'Player 1 controls', WHITE, 50, type1=True)
        rect = render_controls(x, y + 140, player.controls, return_rect=True)
        if type(player.controls) == str:
            draw_side_arrow((pad_x1 + 440, pad_y1 + 380),
                            'left', width=25, height=50)
            draw_side_arrow((pad_x1 + 680, pad_y1 + 380),
                            'right', width=25, height=50)
        y = pad_y1 + CENTRE[1] + 100
        
        render_text_on_screen(x, y, 'Player 1 Name', WHITE, 50, type1=True)
        
        pygame.draw.line(Window, WHITE, (x - 200, y + 160),
                         (x + 200, y + 160), 4)
        
        rect = render_text_on_screen(
            x, y + 115, player.name, WHITE, 50, return_rect=True)
        
        if (pygame.time.get_ticks() // 530) % 2 and selected_text_entry == 1:
            pygame.draw.line(Window, WHITE, (x + 5 + rect.width //
                             2, y + 124), (x + 5 + rect.width // 2, y + 152), 3)
        
        if selected_text_entry != 1 and not player.name:
            if (pygame.time.get_ticks() // 1060) % 2:
                render_text_on_screen(
                    x, y + 115, 'Enter name', V_LIGHT_GREY, 50)
            else:
                render_text_on_screen(x, y + 115, 'Enter name', LIGHT_GREY, 50)
        
        player = Players[1]
        x = pad_x1 + 1360
        y = pad_y1 + 240
        
        render_text_on_screen(x, y, 'Player 2 controls', WHITE, 50, type1=True)
        rect = render_controls(x, y + 140, player.controls, return_rect=True)
        if type(player.controls) == str:
            draw_side_arrow((pad_x1 + 1240, pad_y1 + 380),
                            'left', width=25, height=50)
            draw_side_arrow((pad_x1 + 1480, pad_y1 + 380),
                            'right', width=25, height=50)
        y = pad_y1 + CENTRE[1] + 100
        
        render_text_on_screen(x, y, 'Player 2 Name', WHITE, 50, type1=True)
        
        pygame.draw.line(Window, WHITE, (x - 200, y + 160),
                         (x + 200, y + 160), 4)
        
        rect = render_text_on_screen(
            x, y + 115, player.name, WHITE, 50, return_rect=True)
        
        if (pygame.time.get_ticks() // 530) % 2 and selected_text_entry == 2:
            pygame.draw.line(Window, WHITE, (x + 5 + rect.width //
                             2, y + 124), (x + 5 + rect.width // 2, y + 152), 3)
        
        if selected_text_entry != 2 and not player.name:
            if (pygame.time.get_ticks() // 1060) % 2:
                render_text_on_screen(
                    x, y + 115, 'Enter name', V_LIGHT_GREY, 50)
            else:
                render_text_on_screen(x, y + 115, 'Enter name', LIGHT_GREY, 50)
    
    if Player_amount == 1 and Players[0].name.strip() and Players[0].controls != 'test_alpha' or \
            Player_amount >= 2 and Players[0].name.strip() and Players[0].controls != 'test_alpha' and \
            Players[1].name.strip() and Players[1].controls != 'test_alpha':
        x = pad_x1 + 800
        y = pad_y1 + 940
        tile(x, y, 'dirt road', 76, grid=False)  
        tile(x + 65, y, 'dirt road', 1, grid=False)
        tile(x + 190, y, 'dirt road', 60, grid=False)
        render_text_on_screen(x + 160, y + 20, 'Next', WHITE, 70)
    if Player_amount != 1:
        x = pad_x1 + 400
        y = pad_y1 + 476
        tile(x, y, 'dirt road', 76, grid=False)  
        tile(x + 65, y, 'dirt road', 1, grid=False)
        tile(x + 190, y, 'dirt road', 60, grid=False)
        render_text_on_screen(x + 160, y + 20, 'Single', WHITE, 70)
    if Player_amount != 2:
        x = pad_x1 + 1200
        y = pad_y1 + 476
        tile(x, y, 'dirt road', 76, grid=False)  
        tile(x + 65, y, 'dirt road', 1, grid=False)
        tile(x + 190, y, 'dirt road', 60, grid=False)
        render_text_on_screen(x + 160, y + 20, 'Dual', WHITE, 70)
    
    if Player_amount == 1:
        x = pad_x1 + 400
        y = pad_y1 + 476
        tile(x, y, 'road', 77, grid=False)  
        tile(x + 65, y, 'road', 2, grid=False)
        tile(x + 190, y, 'road', 61, grid=False)
        render_text_on_screen(x + 160, y + 20, 'Single', BLACK, 70)
    elif Player_amount == 2:
        x = pad_x1 + 1200
        y = pad_y1 + 476
        tile(x, y, 'road', 77, grid=False)  
        tile(x + 65, y, 'road', 2, grid=False)
        tile(x + 190, y, 'road', 61, grid=False)
        render_text_on_screen(x + 160, y + 20, 'Dual', BLACK, 70)

def test1a(new_bg, pad_x1=0, pad_y1=0):
    new_bg = pygame.image.load('new_bg.jpg')
    Window.blit(new_bg, (pad_x1, pad_y1))

def test2a(new_bg, pad_x1=0, pad_y1=0):
    new_bg = pygame.image.load('new_bg.jpg')
    Window.blit(new_bg, (pad_x1, pad_y1))

def choose_machine_screen(new_bg, pad_x1=0, pad_y1=0):
    new_bg = pygame.image.load('new_bg.jpg')
    Window.blit(new_bg, (pad_x1, pad_y1))
    x = pad_x1 + CENTRE[0]
    y = pad_y1 + 115
    render_text_on_screen(x, y, 'Choose your Machine', ORANGE, 100)  
    x = pad_x1 + 528
    y = pad_y1 + 890
    tile(x, y, 'dirt road', 76, grid=False)  
    tile(x + 128, y, 'dirt road', 60, grid=False)
    render_text_on_screen(x + 130, y + 20, 'Back', WHITE, 70)
    x = pad_x1 + 1100
    y = pad_y1 + 890
    tile(x, y, 'dirt road', 76, grid=False)  
    tile(x + 65, y, 'dirt road', 1, grid=False)
    tile(x + 190, y, 'dirt road', 60, grid=False)
    render_text_on_screen(x + 160, y + 20, 'Next', WHITE, 70)
    if Player_amount == 1:
        player = Players[0]
        render_text_on_screen(
            pad_x1 + CENTRE[0], pad_y1 + 220, player.name, WHITE, 60, type1=True)
        render_text_on_screen(
            pad_x1 + CENTRE[0], pad_y1 + 325, player.machine_name, WHITE, 50)
        p1_veh_rect = player.car_image.get_rect()
        draw_side_arrow((pad_x1 + CENTRE[0] - 170 - p1_veh_rect.width,
                        pad_y1 + CENTRE[1]), 'left', width=40, height=80)
        Window.blit(player.car_image, (pad_x1 + CENTRE[0] - 215 - p1_veh_rect.width // 2,
                                       pad_y1 + CENTRE[1] - p1_veh_rect.height // 2))
        draw_side_arrow((pad_x1 + CENTRE[0] + 170 + p1_veh_rect.width,
                        pad_y1 + CENTRE[1]), 'right', width=40, height=80)
        if player.car_color == CAR_1:
            text = 'Red'
        elif player.car_color == CAR_2:
            text = 'Yellow'
        elif player.car_color == CAR_3:
            text = 'Green'
        elif player.car_color == CAR_4:
            text = 'Blue'
        else:
            text = 'Black'
        render_text_on_screen(
            pad_x1 + CENTRE[0], pad_y1 + CENTRE[1] + 160, text, WHITE, 50)
        draw_side_arrow(
            (pad_x1 + CENTRE[0] - 120, pad_y1 + CENTRE[1] + 183), 'left', width=25, height=25)
        draw_side_arrow(
            (pad_x1 + CENTRE[0] + 120, pad_y1 + CENTRE[1] + 183), 'right', width=25, height=25)
        render_text_on_screen(
            pad_x1 + CENTRE[0], pad_y1 + 400, 'Speed', WHITE, 40)
        render_text_on_screen(
            pad_x1 + CENTRE[0], pad_y1 + 520, 'Control', WHITE, 40)
        render_text_on_screen(
            pad_x1 + CENTRE[0], pad_y1 + 640, 'Durability', WHITE, 40)
        if player.machine_name == 'Family Car':
            slider_design((pad_x1 + CENTRE[0] + 115, pad_y1 + 408),
                          (200, 22), 3, 0, 5, center_x=False, fill_color=player.car_color)
            slider_design((pad_x1 + CENTRE[0] + 115, pad_y1 + 528),
                          (200, 22), 2, 0, 5, center_x=False, fill_color=player.car_color)
            slider_design((pad_x1 + CENTRE[0] + 115, pad_y1 + 648),
                          (200, 22), 4, 0, 5, center_x=False, fill_color=player.car_color)
        elif player.machine_name == 'Sports Car':
            slider_design((pad_x1 + CENTRE[0] + 115, pad_y1 + 408),
                          (200, 22), 4, 0, 5, center_x=False, fill_color=player.car_color)
            slider_design((pad_x1 + CENTRE[0] + 115, pad_y1 + 528),
                          (200, 22), 3, 0, 5, center_x=False, fill_color=player.car_color)
            slider_design((pad_x1 + CENTRE[0] + 115, pad_y1 + 648),
                          (200, 22), 2, 0, 5, center_x=False, fill_color=player.car_color)
        elif player.machine_name == 'Luxury Car':
            slider_design((pad_x1 + CENTRE[0] + 115, pad_y1 + 408),
                          (200, 22), 3, 0, 5, center_x=False, fill_color=player.car_color)
            slider_design((pad_x1 + CENTRE[0] + 115, pad_y1 + 528),
                          (200, 22), 3, 0, 5, center_x=False, fill_color=player.car_color)
            slider_design((pad_x1 + CENTRE[0] + 115, pad_y1 + 648),
                          (200, 22), 3, 0, 5, center_x=False, fill_color=player.car_color)
        elif player.machine_name == 'Truck':
            slider_design((pad_x1 + CENTRE[0] + 115, pad_y1 + 408),
                          (200, 22), 2, 0, 5, center_x=False, fill_color=player.car_color)
            slider_design((pad_x1 + CENTRE[0] + 115, pad_y1 + 528),
                          (200, 22), 2, 0, 5, center_x=False, fill_color=player.car_color)
            slider_design((pad_x1 + CENTRE[0] + 115, pad_y1 + 648),
                          (200, 22), 5, 0, 5, center_x=False, fill_color=player.car_color)
        elif player.machine_name == 'Race Car':
            slider_design((pad_x1 + CENTRE[0] + 115, pad_y1 + 408),
                          (200, 22), 5, 0, 5, center_x=False, fill_color=player.car_color)
            slider_design((pad_x1 + CENTRE[0] + 115, pad_y1 + 528),
                          (200, 22), 3, 0, 5, center_x=False, fill_color=player.car_color)
            slider_design((pad_x1 + CENTRE[0] + 115, pad_y1 + 648),
                          (200, 22), 1, 0, 5, center_x=False, fill_color=player.car_color)
    elif Player_amount >= 2:
        
        player = Players[0]
        pos_x = CENTRE[0] // 2 + 10
        render_text_on_screen(pad_x1 + pos_x, pad_y1 + 220,
                              player.name, WHITE, 60, type1=True)
        render_text_on_screen(pad_x1 + pos_x, pad_y1 + 325,
                              player.machine_name, WHITE, 50)
        draw_side_arrow((pad_x1 + pos_x - 345, pad_y1 +
                        CENTRE[1]), 'left', width=40, height=80)
        Window.blit(player.car_image, (pad_x1 + pos_x -
                    300, pad_y1 + CENTRE[1] - 150))
        draw_side_arrow((pad_x1 + pos_x + 345, pad_y1 +
                        CENTRE[1]), 'right', width=40, height=80)
        if player.car_color == CAR_1:
            text = 'Red'
        elif player.car_color == CAR_2:
            text = 'Yellow'
        elif player.car_color == CAR_3:
            text = 'Green'
        elif player.car_color == CAR_4:
            text = 'Blue'
        else:
            text = 'Black'
        render_text_on_screen(pad_x1 + pos_x, pad_y1 +
                              CENTRE[1] + 160, text, WHITE, 50)
        draw_side_arrow((pad_x1 + pos_x - 120, pad_y1 +
                        CENTRE[1] + 183), 'left', width=25, height=25)
        draw_side_arrow((pad_x1 + pos_x + 120, pad_y1 +
                        CENTRE[1] + 183), 'right', width=25, height=25)
        render_text_on_screen(pad_x1 + pos_x, pad_y1 + 400, 'Speed', WHITE, 40)
        render_text_on_screen(pad_x1 + pos_x, pad_y1 +
                              520, 'Control', WHITE, 40)
        render_text_on_screen(pad_x1 + pos_x, pad_y1 +
                              640, 'Durability', WHITE, 40)
        if player.machine_name == 'Family Car':
            slider_design((pad_x1 + pos_x + 115, pad_y1 + 408),
                          (200, 22), 3, 0, 5, center_x=False, fill_color=player.car_color)
            slider_design((pad_x1 + pos_x + 115, pad_y1 + 528),
                          (200, 22), 2, 0, 5, center_x=False, fill_color=player.car_color)
            slider_design((pad_x1 + pos_x + 115, pad_y1 + 648),
                          (200, 22), 4, 0, 5, center_x=False, fill_color=player.car_color)
        elif player.machine_name == 'Sports Car':
            slider_design((pad_x1 + pos_x + 115, pad_y1 + 408),
                          (200, 22), 4, 0, 5, center_x=False, fill_color=player.car_color)
            slider_design((pad_x1 + pos_x + 115, pad_y1 + 528),
                          (200, 22), 3, 0, 5, center_x=False, fill_color=player.car_color)
            slider_design((pad_x1 + pos_x + 115, pad_y1 + 648),
                          (200, 22), 2, 0, 5, center_x=False, fill_color=player.car_color)
        elif player.machine_name == 'Luxury Car':
            slider_design((pad_x1 + pos_x + 115, pad_y1 + 408),
                          (200, 22), 3, 0, 5, center_x=False, fill_color=player.car_color)
            slider_design((pad_x1 + pos_x + 115, pad_y1 + 528),
                          (200, 22), 3, 0, 5, center_x=False, fill_color=player.car_color)
            slider_design((pad_x1 + pos_x + 115, pad_y1 + 648),
                          (200, 22), 3, 0, 5, center_x=False, fill_color=player.car_color)
        elif player.machine_name == 'Truck':
            slider_design((pad_x1 + pos_x + 115, pad_y1 + 408),
                          (200, 22), 2, 0, 5, center_x=False, fill_color=player.car_color)
            slider_design((pad_x1 + pos_x + 115, pad_y1 + 528),
                          (200, 22), 1, 0, 5, center_x=False, fill_color=player.car_color)
            slider_design((pad_x1 + pos_x + 115, pad_y1 + 648),
                          (200, 22), 5, 0, 5, center_x=False, fill_color=player.car_color)
        elif player.machine_name == 'Race Car':
            slider_design((pad_x1 + pos_x + 115, pad_y1 + 408),
                          (200, 22), 5, 0, 5, center_x=False, fill_color=player.car_color)
            slider_design((pad_x1 + pos_x + 115, pad_y1 + 528),
                          (200, 22), 2, 0, 5, center_x=False, fill_color=player.car_color)
            slider_design((pad_x1 + pos_x + 115, pad_y1 + 648),
                          (200, 22), 1, 0, 5, center_x=False, fill_color=player.car_color)
        
        player = Players[1]
        pos_x = CENTRE[0] + CENTRE[0] // 2 - 10
        render_text_on_screen(pad_x1 + pos_x, pad_y1 + 220,
                              player.name, WHITE, 60, type1=True)
        render_text_on_screen(pad_x1 + pos_x, pad_y1 + 325,
                              player.machine_name, WHITE, 50)
        draw_side_arrow((pad_x1 + pos_x - 345, pad_y1 +
                        CENTRE[1]), 'left', width=40, height=80)
        Window.blit(player.car_image, (pad_x1 + pos_x -
                    300, pad_y1 + CENTRE[1] - 150))
        draw_side_arrow((pad_x1 + pos_x + 345, pad_y1 +
                        CENTRE[1]), 'right', width=40, height=80)
        if player.car_color == CAR_1:
            text = 'Red'
        elif player.car_color == CAR_2:
            text = 'Yellow'
        elif player.car_color == CAR_3:
            text = 'Green'
        elif player.car_color == CAR_4:
            text = 'Blue'
        else:
            text = 'Black'
        render_text_on_screen(pad_x1 + pos_x, pad_y1 +
                              CENTRE[1] + 160, text, WHITE, 50)
        draw_side_arrow((pad_x1 + pos_x - 120, pad_y1 +
                        CENTRE[1] + 183), 'left', width=25, height=25)
        draw_side_arrow((pad_x1 + pos_x + 120, pad_y1 +
                        CENTRE[1] + 183), 'right', width=25, height=25)
        render_text_on_screen(pad_x1 + pos_x, pad_y1 + 400, 'Speed', WHITE, 40)
        render_text_on_screen(pad_x1 + pos_x, pad_y1 +
                              520, 'Cornering', WHITE, 40)
        render_text_on_screen(pad_x1 + pos_x, pad_y1 +
                              640, 'Strength', WHITE, 40)
        if player.machine_name == 'Family Car':
            slider_design((pad_x1 + pos_x + 115, pad_y1 + 408),
                          (200, 22), 3, 0, 5, center_x=False, fill_color=player.car_color)
            slider_design((pad_x1 + pos_x + 115, pad_y1 + 528),
                          (200, 22), 2, 0, 5, center_x=False, fill_color=player.car_color)
            slider_design((pad_x1 + pos_x + 115, pad_y1 + 648),
                          (200, 22), 4, 0, 5, center_x=False, fill_color=player.car_color)
        elif player.machine_name == 'Sports Car':
            slider_design((pad_x1 + pos_x + 115, pad_y1 + 408),
                          (200, 22), 4, 0, 5, center_x=False, fill_color=player.car_color)
            slider_design((pad_x1 + pos_x + 115, pad_y1 + 528),
                          (200, 22), 3, 0, 5, center_x=False, fill_color=player.car_color)
            slider_design((pad_x1 + pos_x + 115, pad_y1 + 648),
                          (200, 22), 2, 0, 5, center_x=False, fill_color=player.car_color)
        elif player.machine_name == 'Luxury Car':
            slider_design((pad_x1 + pos_x + 115, pad_y1 + 408),
                          (200, 22), 3, 0, 5, center_x=False, fill_color=player.car_color)
            slider_design((pad_x1 + pos_x + 115, pad_y1 + 528),
                          (200, 22), 3, 0, 5, center_x=False, fill_color=player.car_color)
            slider_design((pad_x1 + pos_x + 115, pad_y1 + 648),
                          (200, 22), 3, 0, 5, center_x=False, fill_color=player.car_color)
        elif player.machine_name == 'Truck':
            slider_design((pad_x1 + pos_x + 115, pad_y1 + 408),
                          (200, 22), 2, 0, 5, center_x=False, fill_color=player.car_color)
            slider_design((pad_x1 + pos_x + 115, pad_y1 + 528),
                          (200, 22), 1, 0, 5, center_x=False, fill_color=player.car_color)
            slider_design((pad_x1 + pos_x + 115, pad_y1 + 648),
                          (200, 22), 5, 0, 5, center_x=False, fill_color=player.car_color)
        elif player.machine_name == 'Race Car':
            slider_design((pad_x1 + pos_x + 115, pad_y1 + 408),
                          (200, 22), 5, 0, 5, center_x=False, fill_color=player.car_color)
            slider_design((pad_x1 + pos_x + 115, pad_y1 + 528),
                          (200, 22), 2, 0, 5, center_x=False, fill_color=player.car_color)
            slider_design((pad_x1 + pos_x + 115, pad_y1 + 648),
                          (200, 22), 1, 0, 5, center_x=False, fill_color=player.car_color)
            
def test1(new_bg, pad_x1=0, pad_y1=0):
    new_bg = pygame.image.load('new_bg.jpg')
    Window.blit(new_bg, (pad_x1, pad_y1))

def test2(new_bg, pad_x1=0, pad_y1=0):
    new_bg = pygame.image.load('new_bg.jpg')
    Window.blit(new_bg, (pad_x1, pad_y1))

def settings_confirmation(new_bg, pad_x1=0, pad_y1=0):
    new_bg = pygame.image.load('new_bg.jpg')
    Window.blit(new_bg, (pad_x1, pad_y1))
    x = pad_x1 + CENTRE[0]
    y = pad_y1 + 115
    render_text_on_screen(x, y, 'Finalise Settings', ORANGE, 100)  
    x = pad_x1 + 210
    y = pad_y1 + 112
    tile(x, y, 'dirt road', 76, grid=False, scale=(100, 100))  
    tile(x + 100, y, 'dirt road', 60, grid=False, scale=(100, 100))
    render_text_on_screen(x + 100, y + 23, 'Back', WHITE, 55)
    x = pad_x1 + 800
    y = pad_y1 + 850
    tile(x, y, 'dirt road', 76, grid=False)  
    tile(x + 65, y, 'dirt road', 1, grid=False)
    tile(x + 190, y, 'dirt road', 60, grid=False)
    render_text_on_screen(x + 160, y + 20, 'Start', WHITE, 70)
    if Player_amount != 6:
        x = pad_x1 + 511
        y = pad_y1 + 345
        render_text_on_screen(x, y, str(Enemy_Amount),
                              WHITE, 70)  
        render_text_on_screen(x, y - 48, 'Enemy Amount', WHITE, 30)
        draw_side_arrow((x - 120, y - 34), 'left', width=25, height=25)
        draw_side_arrow((x + 120, y - 34), 'right', width=25, height=25)
        x = pad_x1 + 960
        y = pad_y1 + 345
        if powerups:
            text = 'On'
        else:
            text = 'Off'
        render_text_on_screen(x, y, text, WHITE, 70)  
        render_text_on_screen(x, y - 48, 'Powerups', WHITE, 30)
        draw_side_arrow((x - 100, y - 34), 'left', width=25, height=25)
        draw_side_arrow((x + 100, y - 34), 'right', width=25, height=25)
        x = pad_x1 + 1408
        y = pad_y1 + 345
        render_text_on_screen(x, y, str(Total_laps), WHITE, 70)  
        render_text_on_screen(x, y - 48, 'Laps', WHITE, 30)
        draw_side_arrow((x - 60, y - 34), 'left', width=25, height=25)
        draw_side_arrow((x + 60, y - 34), 'right', width=25, height=25)
        if Enemy_Amount:
            x = pad_x1 + 511
            y = pad_y1 + 540
            if Enemy_machines == 1:
                text = 'family car'
            elif Enemy_machines == 2:
                text = 'sports car'
            elif Enemy_machines == 3:
                text = 'luxury car'
            elif Enemy_machines == 4:
                text = 'truck'
            elif Enemy_machines == 5:
                text = 'race car'
            else:
                text = 'random'
            render_text_on_screen(x, y, str(text), WHITE,
                                  70)  
            render_text_on_screen(x, y - 48, 'Enemy Machines', WHITE, 30)
            draw_side_arrow((x - 110, y - 34), 'left', width=25, height=25)
            draw_side_arrow((x + 110, y - 34), 'right', width=25, height=25)
            x = pad_x1 + 511
            y = pad_y1 + 735
            if Enemy_machine_color == CAR_1:
                text = 'red'
            elif Enemy_machine_color == CAR_2:
                text = 'yellow'
            elif Enemy_machine_color == CAR_3:
                text = 'green'
            elif Enemy_machine_color == CAR_4:
                text = 'blue'
            elif Enemy_machine_color == CAR_5:
                text = 'black'
            else:
                text = 'random'
            render_text_on_screen(x, y, str(text), WHITE,
                                  70)  
            render_text_on_screen(x, y - 48, 'Enemy Color', WHITE, 30)
            draw_side_arrow((x - 110, y - 34), 'left', width=25, height=25)
            draw_side_arrow((x + 110, y - 34), 'right', width=25, height=25)
        x = pad_x1 + 1408
        y = pad_y1 + 540
        render_text_on_screen(
            x, y, str(Players[0].start_pos), WHITE, 70)  
        render_text_on_screen(x, y - 48, 'P1 Start', WHITE, 30)
        draw_side_arrow((x - 90, y - 34), 'left', width=25, height=25)
        draw_side_arrow((x + 90, y - 34), 'right', width=25, height=25)
        if Player_amount >= 2:
            x = pad_x1 + 1408
            y = pad_y1 + 735
            render_text_on_screen(
                x, y, str(Players[1].start_pos), WHITE, 70)  
            render_text_on_screen(x, y - 48, 'P2 Start', WHITE, 30)
            draw_side_arrow((x - 90, y - 34), 'left', width=25, height=25)
            draw_side_arrow((x + 90, y - 34), 'right', width=25, height=25)
        if Player_amount >= 3:
            x = pad_x1 + 1408
            y = pad_y1 + 930
            render_text_on_screen(
                x, y, str(Players[2].start_pos), WHITE, 70)  
            render_text_on_screen(x, y - 48, 'P3 Start', WHITE, 30)
            draw_side_arrow((x - 90, y - 34), 'left', width=25, height=25)
            draw_side_arrow((x + 90, y - 34), 'right', width=25, height=25)
        if Player_amount >= 4:
            x = pad_x1 + 1688
            y = pad_y1 + 540
            render_text_on_screen(
                x, y, str(Players[3].start_pos), WHITE, 70)  
            render_text_on_screen(x, y - 48, 'P4 Start', WHITE, 30)
            draw_side_arrow((x - 90, y - 34), 'left', width=25, height=25)
            draw_side_arrow((x + 90, y - 34), 'right', width=25, height=25)
        if Player_amount == 5:
            x = pad_x1 + 1688
            y = pad_y1 + 735
            render_text_on_screen(
                x, y, str(Players[4].start_pos), WHITE, 70)  
            render_text_on_screen(x, y - 48, 'P5 Start', WHITE, 30)
            draw_side_arrow((x - 90, y - 34), 'left', width=25, height=25)
            draw_side_arrow((x + 90, y - 34), 'right', width=25, height=25)
    else:
        x = pad_x1 + 960
        y = pad_y1 + 345
        render_text_on_screen(x, y, str(Total_laps), WHITE, 70)  
        render_text_on_screen(x, y - 48, 'Laps', WHITE, 30)
        draw_side_arrow((x - 60, y - 34), 'left', width=25, height=25)
        draw_side_arrow((x + 60, y - 34), 'right', width=25, height=25)
        x = pad_x1 + 960
        y = pad_y1 + 735
        if powerups:
            text = 'On'
        else:
            text = 'Off'
        render_text_on_screen(x, y, text, WHITE, 70)  
        render_text_on_screen(x, y - 48, 'Powerups', WHITE, 30)
        draw_side_arrow((x - 100, y - 34), 'left', width=25, height=25)
        draw_side_arrow((x + 100, y - 34), 'right', width=25, height=25)
        x = pad_x1 + 511
        y = pad_y1 + 345
        render_text_on_screen(
            x, y, str(Players[0].start_pos), WHITE, 70)  
        render_text_on_screen(x, y - 48, 'P1 Start', WHITE, 30)
        x = pad_x1 + 511
        y = pad_y1 + 540
        render_text_on_screen(
            x, y, str(Players[1].start_pos), WHITE, 70)  
        render_text_on_screen(x, y - 48, 'P2 Start', WHITE, 30)
        x = pad_x1 + 511
        y = pad_y1 + 735
        render_text_on_screen(
            x, y, str(Players[2].start_pos), WHITE, 70)  
        render_text_on_screen(x, y - 48, 'P3 Start', WHITE, 30)
        x = pad_x1 + 1408
        y = pad_y1 + 345
        render_text_on_screen(
            x, y, str(Players[3].start_pos), WHITE, 70)  
        render_text_on_screen(x, y - 48, 'P4 Start', WHITE, 30)
        x = pad_x1 + 1408
        y = pad_y1 + 540
        render_text_on_screen(
            x, y, str(Players[4].start_pos), WHITE, 70)  
        render_text_on_screen(x, y - 48, 'P5 Start', WHITE, 30)
        x = pad_x1 + 1408
        y = pad_y1 + 735
        render_text_on_screen(
            x, y, str(Players[5].start_pos), WHITE, 70)  
        render_text_on_screen(x, y - 48, 'P6 Start', WHITE, 30)

def quit_confirmation(new_bg, pad_x1=0, pad_y1=0, game_surface=Window):
    new_bg = pygame.image.load('new_bg.jpg')
    game_surface.blit(new_bg, (pad_x1, pad_y1))
    x = pad_x1 + CENTRE[0]
    y = pad_y1 + 128
    render_text_on_screen(x, y, 'Are you sure?', ORANGE, 100,
                          game_surface=game_surface)  
    x = pad_x1 + 347
    y = pad_y1 + CENTRE[1] - (tile_scale[1] // 2)
    tile(x, y, 'dirt road', 76, grid=False,
         game_surface=game_surface)  
    tile(x + 85, y, 'dirt road', 1, grid=False, game_surface=game_surface)
    tile(x + 168, y, 'dirt road', 60, grid=False, game_surface=game_surface)
    render_text_on_screen(x + 153, y + 20, 'Yes', WHITE,
                          70, game_surface=game_surface)
    x = pad_x1 + CENTRE[0] + 347
    y = pad_y1 + CENTRE[1] - (tile_scale[1] // 2)
    tile(x, y, 'dirt road', 76, grid=False,
         game_surface=game_surface)  
    tile(x + 85, y, 'dirt road', 1, grid=False, game_surface=game_surface)
    tile(x + 168, y, 'dirt road', 60, grid=False, game_surface=game_surface)
    render_text_on_screen(x + 153, y + 20, 'No', WHITE,
                          70, game_surface=game_surface)
    
def dev_credits(new_bg, pad_x1=0, pad_y1=0):
    new_bg = pygame.image.load('new_bg.jpg')
    Window.blit(new_bg, (pad_x1, pad_y1))
    x = pad_x1 + CENTRE[0]
    y = pad_y1 + 115
    render_text_on_screen(x, y, 'Credits', ORANGE, 100)  
    y = pad_y1 + 215
    text = 'Aaryan Krishna'
    render_text_on_screen(x, y, text, WHITE, 50)  
    y += 70
    text = 'Jehil Thakkar'
    render_text_on_screen(x, y, text, WHITE, 50)  
    y += 70
    text = 'Yash Nayankumar Chavda'
    render_text_on_screen(x, y, text, WHITE, 50)  
    y += 70
    text = 'Kimia Ketabfoorosh'
    render_text_on_screen(x, y, text, WHITE, 50)  
    x = pad_x1 + 800
    y = pad_y1 + 940
    tile(x, y, 'dirt road', 76, grid=False)  
    tile(x + 65, y, 'dirt road', 1, grid=False)
    tile(x + 190, y, 'dirt road', 60, grid=False)
    render_text_on_screen(x + 160, y + 20, 'Back', WHITE, 70)

def hints_screen(new_bg, pad_x1=0, pad_y1=0):
    new_bg = pygame.image.load('new_bg.jpg')
    Window.blit(new_bg, (pad_x1, pad_y1))
    x = pad_x1 + CENTRE[0]
    y = pad_y1 + 115
    render_text_on_screen(
        x, y, 'Read the following Hints ', ORANGE, 100)  
    x = pad_x1 + 800
    y = pad_y1 + 940
    tile(x, y, 'dirt road', 76, grid=False)  
    tile(x + 65, y, 'dirt road', 1, grid=False)
    tile(x + 190, y, 'dirt road', 60, grid=False)
    render_text_on_screen(x + 160, y + 20, 'Back', WHITE, 70)
    x = pad_x1 + 535
    y = pad_y1 + 325
    game_surface = pygame.transform.scale(
        pygame.image.load(bin.power_up('boost')), (80, 80))
    game_surface.set_colorkey(BLACK)
    Window.blit(game_surface, (x, y))
    render_text_on_screen(x + 40, y + 80, 'Nitro', WHITE, 60)
    render_text_on_screen(
        x + 40, y + 140, "Temporarily boosts the", WHITE, 40)
    render_text_on_screen(
        x + 40, y + 180, "player's speed", WHITE, 40)
    x = pad_x1 + 535
    y = pad_y1 + 649
    game_surface = pygame.transform.scale(
        pygame.image.load(bin.power_up('repair')), (80, 80))
    game_surface.set_colorkey(BLACK)
    Window.blit(game_surface, (x, y))
    render_text_on_screen(x + 40, y + 80, 'Repair', WHITE, 60)
    render_text_on_screen(
        x + 40, y + 140, "Repairs player's damage", WHITE, 40)
    render_text_on_screen(
        x + 40, y + 180, "caused by crashes or thunder", WHITE, 40)
    x = pad_x1 + 1435
    y = pad_y1 + 325
    game_surface = pygame.transform.scale(
        pygame.image.load(bin.power_up('lightning')), (80, 80))
    game_surface.set_colorkey(BLACK)
    Window.blit(game_surface, (x, y))
    render_text_on_screen(x + 40, y + 80, 'Thunder', WHITE, 60)
    render_text_on_screen(
        x + 40, y + 140, "Damages the car with the", WHITE, 40)
    render_text_on_screen(
        x + 40, y + 180, "symbol next to their name", WHITE, 40)
    x = pad_x1 + 1435
    y = pad_y1 + 649
    game_surface = pygame.transform.scale(
        pygame.image.load(bin.power_up('bullet')), (80, 80))
    game_surface.set_colorkey(BLACK)
    Window.blit(game_surface, (x, y))
    render_text_on_screen(x + 40, y + 80, 'Debris', WHITE, 60)
    render_text_on_screen(x + 40, y + 140, "Stops the car", WHITE, 40)
    render_text_on_screen(x + 40, y + 180, "for a few seconds", WHITE, 40)

def basic_settings(new_bg, pad_x1=0, pad_y1=0, game_surface=Window):
    new_bg = pygame.image.load('new_bg.jpg')
    game_surface.blit(new_bg, (pad_x1, pad_y1))
    x = pad_x1 + CENTRE[0]
    y = pad_y1 + 115
    render_text_on_screen(x, y, 'Settings', ORANGE, 100,
                          game_surface=game_surface)  
    x = pad_x1 + 800
    y = pad_y1 + 940
    tile(x, y, 'dirt road', 76, grid=False,
         game_surface=game_surface)  
    tile(x + 65, y, 'dirt road', 1, grid=False, game_surface=game_surface)
    tile(x + 190, y, 'dirt road', 60, grid=False, game_surface=game_surface)
    render_text_on_screen(x + 160, y + 20, 'Back', WHITE,
                          70, game_surface=game_surface)
    x = pad_x1 + 514
    y = pad_y1 + 345
    if device_screen_resolution == device_information[Screen]:
        text = 'Auto'
    else:
        
        text = str(device_screen_resolution[0]) + \
            ' x ' + str(device_screen_resolution[1])
    render_text_on_screen(x, y, text, WHITE, 70, game_surface=game_surface)
    render_text_on_screen(x, y - 48, 'Resolution', WHITE,
                          30, game_surface=game_surface)
    draw_side_arrow((x - 105, y - 34), 'left', width=25,
                    height=25, surface=game_surface)
    draw_side_arrow((x + 105, y - 34), 'right', width=25,
                    height=25, surface=game_surface)
    x = pad_x1 + 1408
    y = pad_y1 + 345
    if Animations:
        text = 'On'
    else:
        text = 'Off'
    render_text_on_screen(x, y, text, WHITE, 70,
                          game_surface=game_surface)  
    render_text_on_screen(x, y - 48, 'Animations', WHITE,
                          30, game_surface=game_surface)
    draw_side_arrow((x - 105, y - 34), 'left', width=25,
                    height=25, surface=game_surface)
    draw_side_arrow((x + 105, y - 34), 'right', width=25,
                    height=25, surface=game_surface)
    x = pad_x1 + 1408
    y = pad_y1 + 696
    if Mute_volume:
        text = 'On'
    else:
        text = 'Off'
    render_text_on_screen(x, y, text, WHITE, 70,
                          game_surface=game_surface)  
    render_text_on_screen(x, y - 48, 'Mute volume', WHITE,
                          30, game_surface=game_surface)
    draw_side_arrow((x - 125, y - 34), 'left', width=25,
                    height=25, surface=game_surface)
    draw_side_arrow((x + 125, y - 34), 'right', width=25,
                    height=25, surface=game_surface)
    x = pad_x1 + 960
    y = pad_y1 + 696
    slider_design((x, y + 30), (300, 20), Music_volume, 0, 1,
                  surface=game_surface)  
    render_text_on_screen(x, y - 48, 'Music Volume',
                          WHITE, 30, game_surface=game_surface)
    draw_side_arrow((x - 125, y - 34), 'left', width=25,
                    height=25, surface=game_surface)
    draw_side_arrow((x + 125, y - 34), 'right', width=25,
                    height=25, surface=game_surface)
    x = pad_x1 + 514
    y = pad_y1 + 696
    slider_design((x, y + 30), (300, 20), Sfx_volume, 0, 1,
                  surface=game_surface)  
    render_text_on_screen(x, y - 48, 'Sfx Volume', WHITE,
                          30, game_surface=game_surface)
    draw_side_arrow((x - 110, y - 34), 'left', width=25,
                    height=25, surface=game_surface)
    draw_side_arrow((x + 110, y - 34), 'right', width=25,
                    height=25, surface=game_surface)
    
def ranking_screen(new_bg, pad_x1=0, pad_y1=0):
    new_bg = pygame.image.load('new_bg.jpg')
    Window.blit(new_bg, (pad_x1, pad_y1))
    x = pad_x1 + CENTRE[0]
    y = pad_y1 + 115
    render_text_on_screen(x, y, 'Ranking', ORANGE, 100)  
    x = pad_x1 + 800
    y = pad_y1 + 764
    tile(x, y, 'dirt road', 76, grid=False)  
    tile(x + 65, y, 'dirt road', 1, grid=False)
    tile(x + 190, y, 'dirt road', 60, grid=False)
    render_text_on_screen(x + 160, y + 20, 'Finish', WHITE, 70)
    for car_no in range(0, len(Player_positions)):
        rect = render_text_on_screen(CENTRE[0], 85 * car_no + 250, str(car_no + 1) + '. ' + Player_positions[car_no].name,
                                     WHITE, 75, return_rect=True)  
        Window.blit(pygame.transform.scale(pygame.image.load(Player_positions[car_no].image_dir),
                                           (45, 68)), (CENTRE[0] + rect.width // 2 + 15, 85 * car_no + 250))
    
    text = 'Map: ' + str(Map.name) + '  |  Laps: ' + str(Total_laps) + '  |  AI: ' + str(Enemy_Amount) + \
           '  |  Players: ' + str(Player_amount) + \
        '  |  Time Taken: ' + str(Race_time)
    render_text_on_screen(CENTRE[0], 926, text, WHITE, 50)

def game_interface(player_list, game_countdown_timer, lap_timer):
    if Player_amount >= 1:
        render_text_on_screen(CENTRE[0] - 250, 10, 'Player 1 Lap', WHITE, 40)
        render_text_on_screen(
            CENTRE[0] - 250, 50, str(player_list[0].laps) + '/' + str(Total_laps), WHITE, 30)
        render_text_on_screen(CENTRE[0] - 450, 10,
                              'Player 1 Damage', WHITE, 40)
        slider_design((CENTRE[0] - 450, 63), (130, 20), player_list[0].damage, 0,
                      player_list[0].Strength, fill_color=player_list[0].colour)
    if Player_amount == 2:
        render_text_on_screen(CENTRE[0] + 250, 10, 'Player 2 Lap', WHITE, 40)
        render_text_on_screen(
            CENTRE[0] + 250, 50, str(player_list[1].laps) + '/' + str(Total_laps), WHITE, 30)
        render_text_on_screen(CENTRE[0] + 450, 10,
                              'Player 2 Damage', WHITE, 40)
        slider_design((CENTRE[0] + 450, 63), (130, 20), player_list[1].damage, 0,
                      player_list[1].Strength, fill_color=player_list[1].colour)
    render_text_on_screen(10, 10, 'Ranking', WHITE, 50,
                          center_x=False)  
    for car_no in range(0, len(Player_positions)):
        render_text_on_screen(10, 40 * car_no + 60, str(car_no + 1) +
                              '.', WHITE, 40, center_x=False)  
        Window.blit(pygame.transform.scale(pygame.image.load(Player_positions[car_no].image_dir),
                                           (30, 40)), (50, 40 * car_no + 60))  
        render_text_on_screen(85, 40 * car_no + 60, ' ' + str(Player_positions[car_no].laps) + '/' + str(Total_laps) + ' ' +
                              Player_positions[car_no].name, WHITE, 40, center_x=False)  
    render_text_on_screen(1800, 10, 'Laps Done', WHITE, 40)
    if Player_positions:
        render_text_on_screen(1850, 50, Player_positions[0].laps, WHITE, 40)
        if lap_timer > pygame.time.get_ticks():
            render_text_on_screen(
                CENTRE[0], CENTRE[1], 'Lap ' + str(Player_positions[0].laps), WHITE, 70, type1=True)
    else:
        render_text_on_screen(1850, 50, 0, WHITE, 40)
    if game_countdown_timer:
        render_text_on_screen(
            CENTRE[0], CENTRE[1] - 50, Player_positions[0].name + ' has finished!', WHITE, 50)
        render_text_on_screen(
            CENTRE[0], CENTRE[1], 'Game ends in ' + str(game_countdown_timer // 1000), WHITE, 50)
        
def window_is_paused():
    second_screen.fill(BLACK)
    second_screen.blit(Window_screenshot, (0, 0))
    render_text_on_screen(CENTRE[0], 115, 'Game Paused', ORANGE,
                          100, type1=True, game_surface=second_screen)  
    x = CENTRE[0] - 192
    y = CENTRE[1] - 180
    tile(x, y, 'dirt road', 76, grid=False,
         game_surface=second_screen)  
    tile(x + 128, y, 'dirt road', 1, grid=False, game_surface=second_screen)
    tile(x + 256, y, 'dirt road', 60, grid=False, game_surface=second_screen)
    render_text_on_screen(x + 193, y + 20, 'Resume', WHITE,
                          70, game_surface=second_screen)
    x = CENTRE[0] - 192
    y = CENTRE[1] - 30
    tile(x, y, 'dirt road', 76, grid=False,
         game_surface=second_screen)  
    tile(x + 128, y, 'dirt road', 1, grid=False, game_surface=second_screen)
    tile(x + 256, y, 'dirt road', 60, grid=False, game_surface=second_screen)
    render_text_on_screen(x + 190, y + 20, 'Settings',
                          WHITE, 70, game_surface=second_screen)
    x = CENTRE[0] - 192
    y = CENTRE[1] + 120
    tile(x, y, 'dirt road', 76, grid=False,
         game_surface=second_screen)  
    tile(x + 128, y, 'dirt road', 1, grid=False, game_surface=second_screen)
    tile(x + 256, y, 'dirt road', 60, grid=False, game_surface=second_screen)
    render_text_on_screen(x + 193, y + 20, 'Controls',
                          WHITE, 70, game_surface=second_screen)
    x = CENTRE[0] - 128
    y = CENTRE[1] + 270
    tile(x, y, 'dirt road', 76, grid=False,
         game_surface=second_screen)  
    tile(x + 128, y, 'dirt road', 60, grid=False, game_surface=second_screen)
    render_text_on_screen(x + 130, y + 20, 'Quit', WHITE,
                          70, game_surface=second_screen)
    
def player_control_screen():
    game_surface = second_screen
    game_surface.fill(BLACK)
    game_surface.blit(Window_screenshot, (0, 0))
    render_text_on_screen(CENTRE[0], 115, 'Controls', WHITE,
                          100, type1=True, game_surface=game_surface)  
    x = 332
    y = HEIGHT - 170
    tile(x, y, 'dirt road', 76, grid=False,
         game_surface=second_screen)  
    tile(x + 128, y, 'dirt road', 60, grid=False, game_surface=second_screen)
    render_text_on_screen(x + 130, y + 20, 'Quit', WHITE,
                          70, game_surface=second_screen)
    bound_players = 0
    for player in Player_list:
        if player.input_type == 'wasd' or player.input_type == 'arrows':
            bound_players += 1
    if bound_players == len(Player_list):
        x = 1268
        y = HEIGHT - 170
        tile(x, y, 'dirt road', 76, grid=False,
             game_surface=second_screen)  
        tile(x + 128, y, 'dirt road', 1, grid=False, game_surface=second_screen)
        tile(x + 256, y, 'dirt road', 60, grid=False, game_surface=second_screen)
        render_text_on_screen(x + 193, y + 20, 'Confirm',
                              WHITE, 70, game_surface=second_screen)
    
    for index in range(0, len(Player_list)):
        player = Player_list[index]
        if index == 0:
            x = CENTRE[0] - 500
            y = 310
        elif index == 1:
            x = CENTRE[0]
            y = 310
        elif index == 2:
            x = CENTRE[0] + 500
            y = 310
        elif index == 3:
            x = CENTRE[0] - 500
            y = 600
        elif index == 4:
            x = CENTRE[0]
            y = 600
        elif index == 5:
            x = CENTRE[0] + 500
            y = 600
        else:
            x, y = CENTRE
        good = True
        rect = render_controls(x, y + 140, player.input_type,
                             return_rect=True, surface=game_surface)
        render_text_on_screen(x, y, 'P{0} controls'.format(
            index + 1), CAR_3 if good else CAR_1, 50, type1=True, game_surface=game_surface)
        draw_side_arrow((x - 120, y + 140), 'left', width=25,
                        height=50, surface=game_surface)
        draw_side_arrow((x + 120, y + 140), 'right', width=25,
                        height=50, surface=game_surface)
        
def menu_background(top=False, right=False, bottom=False, left=False):
    
    game_surface = pygame.surface.Surface((WIDTH, HEIGHT))
    bg_image = pygame.image.load("new_bg.jpg").convert()
    game_surface.blit(bg_image, (0, 0))
    return game_surface  

def screen_animation(window, new_window, bg, new_bg, car, direction: str):
    if direction == 'up':
        
        if new_window == choose_map_window or new_window == choose_machine_screen:
            
            for offset_y in range(0, HEIGHT + 1, menu_scroll_speed):
                Clock.tick(FPS)  
                window(bg, pad_y1=offset_y)
                new_window(new_bg, pad_y1=offset_y - HEIGHT)
                if offset_y // 2 + HEIGHT // 2 < 940:
                    car.move(960, offset_y // 2 + HEIGHT // 2)
                else:
                    car.move(960, 940)
                car.draw()
                screen_refresh(full_screen=True)
        
        elif window == choose_map_window or window == choose_machine_screen and \
                new_window != test1 or new_window == settings_confirmation:
            for offset_y in reversed(range(540, 940, menu_scroll_speed)):
                Clock.tick(FPS)
                window(bg)
                car.move(960, offset_y)
                car.draw()
                screen_refresh(full_screen=True)
            
            for offset_y in range(0, HEIGHT + 1, menu_scroll_speed):
                Clock.tick(FPS)  
                window(bg, pad_y1=offset_y)
                new_window(new_bg, pad_y1=offset_y - HEIGHT)
                car.draw()
                screen_refresh(full_screen=True)
        
        else:
            
            for offset_y in range(0, HEIGHT + 1, menu_scroll_speed):
                Clock.tick(FPS)  
                window(bg, pad_y1=offset_y)
                new_window(new_bg, pad_y1=offset_y - HEIGHT)
                car.draw()
                screen_refresh(full_screen=True)
    elif direction == 'down':
        
        if new_window == choose_map_window or window == settings_confirmation and \
                (new_window == choose_machine_screen or new_window == test1 or
                 new_window == test2):
            for offset_y in range(540, 940, menu_scroll_speed):
                Clock.tick(FPS)
                window(bg)
                car.move(960, offset_y)
                car.draw()
                screen_refresh(full_screen=True)
            
            for offset_y in reversed(range(0, HEIGHT + 1, menu_scroll_speed)):
                
                Clock.tick(FPS)
                window(bg, pad_y1=offset_y - HEIGHT)  
                new_window(new_bg, pad_y1=offset_y)  
                car.draw()
                
                screen_refresh(full_screen=True)
        
        elif window == choose_map_window or window == choose_machine_screen:
            for offset_y in range(940, 1080, menu_scroll_speed):
                Clock.tick(FPS)
                window(bg)
                car.move(960, offset_y)
                car.draw()
                screen_refresh(full_screen=True)
            
            for offset_y in reversed(range(0, HEIGHT + 1, menu_scroll_speed)):
                
                Clock.tick(FPS)
                window(bg, pad_y1=offset_y - HEIGHT)  
                new_window(new_bg, pad_y1=offset_y)  
                if offset_y // 2 <= CENTRE[1]:
                    car.move(960, offset_y // 2 + HEIGHT // 2)
                else:
                    car.move(*CENTRE)
                car.draw()
                
                screen_refresh(full_screen=True)
        
        else:
            
            for offset_y in reversed(range(0, HEIGHT + 1, menu_scroll_speed)):
                
                Clock.tick(FPS)
                window(bg, pad_y1=offset_y - HEIGHT)  
                new_window(new_bg, pad_y1=offset_y)  
                car.draw()
                
                screen_refresh(full_screen=True)
    elif direction == 'left':
        for offset_x in range(0, WIDTH + 1, menu_scroll_speed):
            Clock.tick(FPS)  
            window(bg, pad_x1=offset_x)
            
            new_window(new_bg, pad_x1=offset_x - WIDTH)
            car.draw()
            screen_refresh(full_screen=True)  
    elif direction == 'right':
        for offset_x in reversed(range(0, WIDTH + 1, menu_scroll_speed)):
            Clock.tick(FPS)  
            window(bg, pad_x1=offset_x - WIDTH)
            
            new_window(new_bg, pad_x1=offset_x)
            car.draw()
            screen_refresh(full_screen=True)  

def demo_test(game_surface=Window):
    global test_alpha_prompts

def tile(x, y, material, ver, grid=True, scale=tile_scale, game_surface=Window, update=True):
    if grid:
        x *= tile_scale[0]
        y *= tile_scale[1]
    
    img = bin.tile(material, ver)
    for loaded in loaded_bin:
        if img == loaded[0]:  
            raw_surf = loaded[1]  
            image = pygame.transform.scale(raw_surf, scale)
            game_surface.blit(image, (x, y))
            if update:
                
                add_screen_update(image.get_rect(), x, y)
            return
    
    raw_surf = pygame.image.load(img).convert()
    raw_surf.set_colorkey(BLACK)
    loaded_bin.append([img, raw_surf])  
    image = pygame.transform.scale(raw_surf, scale)  
    game_surface.blit(image, (x, y))  
    if update:
        
        add_screen_update(image.get_rect(), x, y)

def draw_side_arrow(pos: tuple[int, int], direction: str,
                    width=18, height=18, colour=WHITE, border=DARK_GREY, border_width=4, surface=Window):
    points = []
    if direction == 'up':
        points.append((pos[0], pos[1] - height / 2))
        points.append((pos[0] + width / 2, pos[1] + height / 2))
        points.append((pos[0] - width / 2, pos[1] + height / 2))
    elif direction == 'down':
        points.append((pos[0] - width / 2, pos[1] - height / 2))
        points.append((pos[0] + width / 2, pos[1] - height / 2))
        points.append((pos[0], pos[1] + height / 2))
    elif direction == 'left':
        points.append((pos[0] + width / 2, pos[1] - height / 2))
        points.append((pos[0] + width / 2, pos[1] + height / 2))
        points.append((pos[0] - width / 2, pos[1]))
    elif direction == 'right':
        points.append((pos[0] + width / 2, pos[1]))
        points.append((pos[0] - width / 2, pos[1] + height / 2))
        points.append((pos[0] - width / 2, pos[1] - height / 2))
    pygame.draw.polygon(surface, colour, points)
    if border:
        pygame.draw.polygon(surface, border, points, border_width)
    if surface == Window:
        screen_updates.append((pos[0] - border_width * 2 - width // 2, pos[1] - border_width * 2 - height // 2,
                               width + width // 2, height + height // 2))
        
def slider_design(pos: tuple[int, int], size: tuple[int, int],
                  value: float or int, min_value: float or int, max_value: float or int, center_x=True,
                  fill_color=CAR_1, surface=Window, border_width=2, border_radius=7):
    game_surface = pygame.surface.Surface((size[0], size[1]))
    game_surface.set_colorkey(BLACK)
    ratio = round((size[0] - border_width - 1) / max_value * value)
    if value > min_value and ratio > border_width:
        pygame.draw.line(game_surface, fill_color, (border_width, (size[1] / 2) - 1),
                         (ratio, (size[1] / 2) - 1), size[1] - border_width * 2)
    pygame.draw.rect(game_surface, WHITE, (0, 0,
                     size[0], size[1]), width=border_width, border_radius=border_radius)
    if center_x:
        surface.blit(
            game_surface, (pos[0] - size[0] / 2, pos[1] - size[1] / 2))
    else:
        surface.blit(game_surface, pos)

def render_text_on_screen(x, y, text, colour, size, bold=False, type1=False, type3=False,
                          center_x=True, return_rect=False, game_surface=Window):
    global loaded_fonts
    font_name = str(size)
    if bold:
        font_name += 'bold'
    if type1:
        font_name += 'type1'
    if type3:
        font_name += 'type3'
    try:
        font = loaded_fonts[font_name]
    except KeyError:
        font = pygame.font.Font(fonts.load(bold, type1, type3), size)
        loaded_fonts[font_name] = font
    render = font.render(str(text), True, colour)
    if center_x:
        x -= render.get_width() // 2  
    game_surface.blit(render, (x, y))
    
    add_screen_update(render.get_rect(), x, y)
    if return_rect:
        return render.get_rect()
    
def render_key_values(value: str, size=50):
    game_surface = pygame.surface.Surface((size, size))
    game_surface.set_colorkey(BLACK)
    pygame.draw.rect(game_surface, WHITE, (0, 0, size, size), 4, 12)
    if len(value) == 1:
        font = pygame.font.Font(fonts.load(), 40)
        render = font.render(value, False, WHITE)
        game_surface.blit(render, (((size - render.get_width()) // 2) + 1,
                                   ((size - render.get_height()) // 2)))
    else:
        draw_side_arrow((size // 2, size // 2), value, width=size // 2,
                        height=size // 2, border=None, surface=game_surface)
    return game_surface

def render_controls(x, y, ver: str or pygame.joystick.Joystick, surface=Window, return_rect=False):
    if type(ver) == str and ver != 'test_alpha':
        game_surface = pygame.surface.Surface((170, 110))
        game_surface.set_colorkey(BLACK)
        centre = game_surface.get_width() // 2
        key_size = 50
        if ver == 'wasd':
            game_surface.blit(render_key_values(
                'W', key_size), (centre - key_size // 2, 0))
            game_surface.blit(render_key_values(
                'A', key_size), (centre - key_size // 2 - key_size - 10, key_size + 10))
            game_surface.blit(render_key_values('S', key_size),
                              (centre - key_size // 2, key_size + 10))
            game_surface.blit(render_key_values(
                'D', key_size), (centre - key_size // 2 + key_size + 10, key_size + 10))
        elif ver == 'arrows':
            game_surface.blit(render_key_values(
                'up', key_size), (centre - key_size // 2, 0))
            game_surface.blit(render_key_values(
                'left', key_size), (centre - key_size // 2 - key_size - 10, key_size + 10))
            game_surface.blit(render_key_values('down', key_size),
                              (centre - key_size // 2, key_size + 10))
            game_surface.blit(render_key_values(
                'right', key_size), (centre - key_size // 2 + key_size + 10, key_size + 10))
        else:
            raise ValueError(
                'render_controls | ver can only be wasd or arrows, not' + str(ver))
    else:
        game_surface = pygame.transform.scale(
            pygame.image.load(bin.test_alpha()), (128, 88))
        game_surface.set_colorkey(BLACK)
    surface.blit(game_surface, (x - game_surface.get_width() //
                 2, y - game_surface.get_height() // 2))
    add_screen_update(game_surface.get_rect())
    if return_rect:
        return game_surface.get_rect()
    
def bin_files_render(bin_files, pos, rotation, scale, return_rect=False):
    global screen_updates
    for loaded in loaded_bin:
        if bin_files == loaded[0]:  
            raw_surf = loaded[1]  
            game_surface = pygame.transform.rotate(
                pygame.transform.scale(raw_surf, scale), rotation)
            Window.blit(game_surface, pos)
            
            add_screen_update(game_surface.get_rect(), pos[0], pos[1])
            if return_rect:
                return game_surface.get_rect()
            else:
                return
    
    
    raw_surf = pygame.image.load(bin_files).convert()
    raw_surf.set_colorkey(BLACK)
    loaded_bin.append([bin_files, raw_surf])
    game_surface = pygame.transform.rotate(
        pygame.transform.scale(raw_surf, scale), rotation)
    Window.blit(game_surface, pos)
    
    add_screen_update(game_surface.get_rect(), pos[0], pos[1])
    if return_rect:
        return game_surface.get_rect()
    
def black_conclusion(speed=12, show_loading=False, paused=False, car=None):
    alpha = Window.get_alpha()
    if not alpha:
        alpha = 255
    second_screen.fill(BLACK)
    if show_loading:
        render_text_on_screen(CENTRE[0], CENTRE[1] - 50, 'Road Fighter', WHITE, 100,
                              type1=True, type3=True, game_surface=second_screen)
        render_text_on_screen(
            CENTRE[0], CENTRE[1] + 150, 'Loading...', WHITE, 50, game_surface=second_screen)
    elif paused:
        window_is_paused()
    for alpha in reversed(range(0, alpha, speed)):
        Clock.tick(FPS)
        Window.set_alpha(alpha)
        Display.blit(pygame.transform.scale(
            second_screen, device_screen_resolution), (0, 0))
        Display.blit(pygame.transform.scale(
            Window, device_screen_resolution), (0, 0))
        if car:
            car.draw()
        pygame.display.update()
    Window.set_alpha(0)  

def black_initialisation(speed=12, show_loading=False, paused=False, window=''):
    alpha = Window.get_alpha()
    if not alpha:
        alpha = 0
        Window.set_alpha(alpha)
    second_screen.fill(BLACK)
    if show_loading:
        render_text_on_screen(CENTRE[0], CENTRE[1] - 50, 'Road Fighter', WHITE, 100,
                              type1=True, type3=True, game_surface=second_screen)
        render_text_on_screen(
            CENTRE[0], CENTRE[1] + 150, 'Loading...', WHITE, 50, game_surface=second_screen)
    elif paused:
        if window == 'settings':
            basic_settings(Window_screenshot, game_surface=second_screen)
        elif window == 'confirm quit':
            quit_confirmation(Window_screenshot, game_surface=second_screen)
        else:
            window_is_paused()
    for alpha in range(alpha, 256, speed):
        Clock.tick(FPS)
        Window.set_alpha(alpha)  
        Display.blit(pygame.transform.scale(
            second_screen, device_screen_resolution), (0, 0))
        Display.blit(pygame.transform.scale(
            Window, device_screen_resolution), (0, 0))
        pygame.display.update()
    Window.set_alpha(None) 

def render_animation(x: int, y: int):
    size = 80, 80  
    dot_size = 18  
    speed = 8  
    debug_surf = None
    prev_frame_timestamp = pygame.time.get_ticks()
    dots = []  
    for dot in range(0, 8):
        dots.append(pygame.surface.Surface((dot_size, dot_size)))
        dots[dot].fill((1, 1, 1))
        dots[dot].set_colorkey((1, 1, 1))
        pygame.draw.circle(
            dots[dot], WHITE, (dot_size / 2, dot_size / 2), dot_size / 2)
        dots[dot].set_alpha(255 // 8 * dot)
        dots[dot] = dots[dot], dots[dot].get_rect()
    dots[0][1].center = x, y - size[1] / 2  
    dots[1][1].center = x + size[0] / 3, y - size[1] / 3
    dots[2][1].center = x + size[0] / 2, y
    dots[3][1].center = x + size[0] / 3, y + size[1] / 3
    dots[4][1].center = x, y + size[1] / 2
    dots[5][1].center = x - size[0] / 3, y + size[1] / 3
    dots[6][1].center = x - size[0] / 2, y
    dots[7][1].center = x - size[0] / 3, y - size[1] / 3
    try:
        while not loading_thread_event.is_set():  
            Clock.tick(FPS)
            for event in pygame.event.get():  
                if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    raise KeyboardInterrupt
            if prev_frame_timestamp != pygame.time.get_ticks():  
                for dot in dots:
                    alpha = dot[0].get_alpha()
                    if alpha - speed < 0 and alpha != 0:
                        alpha = 0
                    elif alpha - speed <= 0:
                        alpha = 255
                    else:
                        alpha -= speed
                    dot[0].set_alpha(alpha)
                prev_frame_timestamp = pygame.time.get_ticks()
            second_screen.fill(BLACK)  
            render_text_on_screen(CENTRE[0], CENTRE[1] - 50, 'Road Fighter', WHITE, 100,
                                  type1=True, type3=True, game_surface=second_screen)
            render_text_on_screen(
                CENTRE[0], CENTRE[1] + 150, 'Loading...', WHITE, 50, game_surface=second_screen)
            second_screen.blit(dots[0][0], dots[0][1].topleft)
            second_screen.blit(dots[1][0], dots[1][1].topleft)
            second_screen.blit(dots[2][0], dots[2][1].topleft)
            second_screen.blit(dots[3][0], dots[3][1].topleft)
            second_screen.blit(dots[4][0], dots[4][1].topleft)
            second_screen.blit(dots[5][0], dots[5][1].topleft)
            second_screen.blit(dots[6][0], dots[6][1].topleft)
            second_screen.blit(dots[7][0], dots[7][1].topleft)
            Display.blit(pygame.transform.scale(
                second_screen, device_screen_resolution), (0, 0))
            pygame.display.update()
    except pygame.error:
        print('render_animation() | pygame.error, stopping ani to avoid crash.')
        return
    second_screen.fill(BLACK)  
    render_text_on_screen(CENTRE[0], CENTRE[1] - 50, 'Road Fighter', WHITE, 100,
                          type1=True, type3=True, game_surface=second_screen)
    render_text_on_screen(
        CENTRE[0], CENTRE[1] + 150, 'Loading...', WHITE, 50, game_surface=second_screen)
    Display.blit(pygame.transform.scale(
        second_screen, device_screen_resolution), (0, 0))
    pygame.display.update()
    return

def change_car_right(player: Player):
    if player.machine_name == 'Race Car':
        player.machine_name = 'Family Car'
    elif player.machine_name == 'Family Car':
        player.machine_name = 'Sports Car'
    elif player.machine_name == 'Sports Car':
        player.machine_name = 'Luxury Car'
    elif player.machine_name == 'Luxury Car':
        player.machine_name = 'Truck'
    elif player.machine_name == 'Truck':
        player.machine_name = 'Race Car'
    player.update_image()
    return player

def change_car_left(player: Player):
    if player.machine_name == 'Family Car':
        player.machine_name = 'Race Car'
    elif player.machine_name == 'Race Car':
        player.machine_name = 'Truck'
    elif player.machine_name == 'Truck':
        player.machine_name = 'Luxury Car'
    elif player.machine_name == 'Luxury Car':
        player.machine_name = 'Sports Car'
    elif player.machine_name == 'Sports Car':
        player.machine_name = 'Family Car'
    player.update_image()
    return player

def change_car_color_right(player: Player):
    if player.car_color == CAR_2:
        player.car_color = CAR_5
    elif player.car_color == CAR_5:
        player.car_color = CAR_4
    elif player.car_color == CAR_4:
        player.car_color = CAR_3
    elif player.car_color == CAR_3:
        player.car_color = CAR_1
    elif player.car_color == CAR_1:
        player.car_color = CAR_2
    player.update_image()
    return player

def change_car_color_left(player: Player):
    if player.car_color == CAR_5:
        player.car_color = CAR_2
    elif player.car_color == CAR_2:
        player.car_color = CAR_1
    elif player.car_color == CAR_1:
        player.car_color = CAR_3
    elif player.car_color == CAR_3:
        player.car_color = CAR_4
    elif player.car_color == CAR_4:
        player.car_color = CAR_5
    player.update_image()
    return player

def change_controls_left(control):
    if control == 'wasd':
        if test_alphas:
            control = 'test_alpha'
        elif 'arrows' not in controls:
            control = 'arrows'
        else:
            return False
    elif control == 'test_alpha':
        if 'arrows' not in controls:
            control = 'arrows'
        elif 'wasd' not in controls:
            control = 'wasd'
        else:
            return False
    elif control == 'arrows':
        if 'wasd' not in controls:
            control = 'wasd'
        elif test_alphas:
            control = 'test_alpha'
        else:
            return False
    return control

def change_controls_right(control):
    if control == 'wasd':
        if 'arrows' not in controls:
            control = 'arrows'
        elif test_alphas:
            control = 'test_alpha'
        else:
            return False
    elif control == 'arrows':
        if test_alphas:
            control = 'test_alpha'
        elif 'wasd' not in controls:
            control = 'wasd'
        else:
            return False
    elif control == 'test_alpha':
        if 'wasd' not in controls:
            control = 'wasd'
        elif 'arrows' not in controls:
            control = 'arrows'
        else:
            return False
    return control

def position_up(player, amount=1, reset=False):
    if not reset:
        return player[0], player[1], player[2], player[3], player[4], player[5] + amount
    else:
        return player[0], player[1], player[2], player[3], player[4], 0
    
def position_down(player, amount=1, reset=False):
    if not reset:
        return player[0], player[1], player[2], player[3], player[4], player[5] - amount
    else:
        return player[0], player[1], player[2], player[3], player[4], 0
    
def random_car():
    rand = randint(1, 5)
    if rand == 1:
        return 'Family Car'
    elif rand == 2:
        return 'Sports Car'
    elif rand == 3:
        return 'Luxury Car'
    elif rand == 4:
        return 'Truck'
    else:
        return 'Race Car'
    
def random_color():
    rand = randint(1, 5)
    if rand == 1:
        return CAR_1
    elif rand == 2:
        return CAR_2
    elif rand == 3:
        return CAR_3
    elif rand == 4:
        return CAR_4
    else:
        return CAR_5
    
def menu_music():
    if not Mute_volume and Music_volume != 0:
        playing = pygame.mixer.music.get_busy()
        if not playing:
            global current_song
            current_song = sounds.menu_track(randint(0, 11))
            pygame.mixer.music.load(current_song)
            pygame.mixer.music.set_volume(Music_volume)
            pygame.mixer.music.play()

def in_game_music(stage, leaderboard=False):
    if not Mute_volume:
        global current_song
        playing = pygame.mixer.music.get_busy()
        while stage > 3:
            stage -= 2
        while stage < 0:
            stage += 1
        if not playing or sounds.game_track(stage) != current_song:
            if leaderboard:
                if not pygame.mixer.music.get_busy():
                    current_song = sounds.game_track(4)
                    pygame.mixer.music.load(sounds.game_track(4))
                    pygame.mixer.music.set_volume(Music_volume)
                    pygame.mixer.music.play()
            else:
                if not pygame.mixer.music.get_busy():
                    current_song = sounds.game_track(stage)
                    pygame.mixer.music.load(sounds.game_track(stage))
                    pygame.mixer.music.set_volume(Music_volume)
                    pygame.mixer.music.play()
                elif current_song != sounds.game_track(stage):
                    pygame.mixer.music.stop()
                    current_song = sounds.game_track(stage)
                    pygame.mixer.music.load(sounds.game_track(stage))
                    pygame.mixer.music.set_volume(Music_volume)
                    pygame.mixer.music.play(fade_ms=200)

def play_music(event: str):
    if Mute_volume and event != 'error':
        return
    if event == 'error':
        sound = pygame.mixer.Sound(sounds.negative('error', 3))
        pygame.mixer.Sound.set_volume(sound, Sfx_volume)
        pygame.mixer.Sound.play(sound)
        return
    elif event == 'boot':
        boot_1 = pygame.mixer.Sound(sounds.pause_sound(6))
        boot_2 = pygame.mixer.Sound(sounds.pause_sound(7, out=True))
        pygame.mixer.Sound.set_volume(boot_1, Sfx_volume)
        pygame.mixer.Sound.set_volume(boot_2, Sfx_volume)
        pygame.mixer.Sound.play(boot_1)
        sleep(0.5)
        pygame.mixer.Sound.play(boot_2)
        return
    if event == 'collision':
        rand = randint(3, 7)
        while rand == 5:  
            rand = randint(3, 7)
        sound_dir = sounds.impact(rand)
    elif event == 'power up':
        sound_dir = sounds.positive(3)
    elif event == 'lightning':
        sound_dir = sounds.explosion('medium', 10)
    elif event == 'bullet':
        sound_dir = sounds.machine_gun(6)
    elif event == 'boost':
        sound_dir = sounds.alarm(8)
    elif event == 'repair':
        sound_dir = sounds.interaction(6)
    elif event == 'lap advance':
        sound_dir = sounds.positive(18)
    elif event == 'lap finish':
        sound_dir = sounds.positive(7)
    elif event == 'menu button':
        sound_dir = sounds.menu(4)
    elif event == 'option up':
        sound_dir = sounds.menu(2)
    elif event == 'option down':
        sound_dir = sounds.menu(3)
    elif event == 'text entry':
        sound_dir = sounds.menu(1)
    elif event == 'start button':
        sound_dir = sounds.menu(4, select=True)
    elif event == 'save button':
        sound_dir = sounds.menu(2, select=True)
    elif event == 'traffic light advance':
        sound_dir = sounds.bleep(2)
    elif event == 'traffic light finish':
        sound_dir = sounds.bleep(11)
    elif event == 'pause in':
        sound_dir = sounds.pause_sound(3)
    elif event == 'pause out':
        sound_dir = sounds.pause_sound(3, out=True)
    else:
        raise ValueError('play_music() - Unknown event: "' + str(event) + '"')
    for audio in loaded_sounds:
        if audio[0] == sound_dir:
            pygame.mixer.Sound.play(audio[1])
            return
    sound = pygame.mixer.Sound(sound_dir)
    pygame.mixer.Sound.set_volume(sound, Sfx_volume)
    pygame.mixer.Sound.play(sound)
    loaded_sounds.append((sound_dir, sound))

def game_menu_loop():
    print('Game music started')
    if not Mute_volume and Music_volume != 0:
        while not music_thread_event.is_set() and not Mute_volume and Music_volume != 0:
            if not Window_sleep:
                if Current_lap > Total_laps:  
                    in_game_music(Current_lap - 2)
                else:
                    in_game_music(Current_lap - 1)
            else:
                if pygame.mixer.music.get_busy():
                    pygame.mixer.music.pause()
                sleep(0.5)
        return  
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.pause()
    print('Game music stopped')
    return

def menu_loop_music():
    print('Menu loop started')
    if not Mute_volume and Music_volume != 0:
        while not music_thread_event.is_set() and Music_volume != 0 and not Mute_volume:
            if not Window_sleep:
                if present_window != 'leaderboard':
                    menu_music()
                else:
                    in_game_music(4, leaderboard=True)
            else:
                if pygame.mixer.music.get_busy():
                    pygame.mixer.music.pause()
                sleep(0.5)
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.pause()
    print('Menu loop stopped')
    return  

def resolution_increase():
    global Display, device_screen_resolution, Display_scaling, Fullscreen
    
    if device_screen_resolution[0] <= 640 and device_screen_resolution[1] <= 360:
        device_screen_resolution = 854, 480
    elif device_screen_resolution[0] <= 854 and device_screen_resolution[1] <= 480:
        device_screen_resolution = 1280, 720
    elif device_screen_resolution[0] <= 1280 and device_screen_resolution[1] <= 720:
        device_screen_resolution = 1920, 1080
    elif device_screen_resolution[0] <= 1920 and device_screen_resolution[1] <= 1080:
        device_screen_resolution = 2560, 1440
    if device_information[Screen][0] <= device_screen_resolution[0] and device_information[Screen][1] <= device_screen_resolution[1]:
        if Fullscreen:
            device_screen_resolution = 640, 360
            Fullscreen = False
        else:
            device_screen_resolution = device_information[Screen]
            Fullscreen = True
    if device_information[Screen] != device_screen_resolution:
        if Window_resolution != device_screen_resolution:
            Display_scaling = True
        Fullscreen = False
        pygame.display.set_caption('Road Fighter')  
        pygame.display.set_icon(icon)  
        Display = pygame.display.set_mode(
            device_screen_resolution, display=Screen)
    else:
        if Window_resolution == device_screen_resolution:
            Display_scaling = False
        Fullscreen = True
        pygame.display.set_caption('Road Fighter')  
        pygame.display.set_icon(icon)  
        Display = pygame.display.set_mode(
            device_screen_resolution, display=Screen, flags=pygame.FULLSCREEN)
    pygame.mouse.set_pos(*display_scaling((619, 311)))

def resolution_decrease():
    global Display, device_screen_resolution, Display_scaling, Fullscreen
    if device_screen_resolution[0] >= 3480 and device_screen_resolution[1] >= 2160:
        device_screen_resolution = 2560, 1440
    elif device_screen_resolution[0] >= 2560 and device_screen_resolution[1] >= 1440:
        device_screen_resolution = 1920, 1080
    elif device_screen_resolution[0] >= 1920 and device_screen_resolution[1] >= 1080:
        device_screen_resolution = 1280, 720
    elif device_screen_resolution[0] >= 1280 and device_screen_resolution[1] >= 720:
        device_screen_resolution = 854, 480
    elif device_screen_resolution[0] >= 854 and device_screen_resolution[1] >= 480:
        device_screen_resolution = 640, 360
    if device_information[Screen][0] < device_screen_resolution[0] or device_information[Screen][1] < device_screen_resolution[1]:
        device_screen_resolution = device_information[Screen]
    if device_information[Screen] != device_screen_resolution:
        if Window_resolution != device_screen_resolution:
            Display_scaling = True
        Fullscreen = False
        pygame.display.set_caption('Road Fighter')  
        pygame.display.set_icon(icon)  
        Display = pygame.display.set_mode(
            device_screen_resolution, display=Screen)
    else:
        if Window_resolution == device_screen_resolution:
            Display_scaling = False
        Fullscreen = True
        pygame.display.set_caption('Road Fighter')  
        pygame.display.set_icon(icon)  
        Display = pygame.display.set_mode(
            device_screen_resolution, display=Screen, flags=pygame.FULLSCREEN)
    pygame.mouse.set_pos(*display_scaling((409, 311)))

def display_scaling(pos: tuple[int, int]):
    return ceil(pos[0] / WIDTH * device_screen_resolution[0]), ceil(pos[1] / HEIGHT * device_screen_resolution[1])

def screen_scaling(pos: tuple[int, int]):
    return ceil(pos[0] / device_screen_resolution[0] * WIDTH), ceil(pos[1] / device_screen_resolution[1] * HEIGHT)

def scale_rect(scaled_rect, x=None, y=None):
    if x and y:
        scaled_rect[0] += x
        scaled_rect[1] += y
    scaled_rect[0], scaled_rect[1] = display_scaling(
        (scaled_rect[0], scaled_rect[1]))
    scaled_rect[2], scaled_rect[3] = display_scaling(
        (scaled_rect[2], scaled_rect[3]))
    return scaled_rect

def add_screen_update(rect, x=None, y=None):
    if Display_scaling:
        rect = scale_rect(rect, x, y)
    else:
        if x and y:
            rect[0] += x
            rect[1] += y
    screen_updates.append(rect)

def screen_refresh(full_screen=False, rect=None, game_surface=Window):
    global screen_updates
    if rect:
        Display.blit(pygame.transform.scale(
            game_surface, Display.get_size()), (0, 0))
        pygame.display.update(rect)
    else:
        
        if full_screen or len(screen_updates) > 15 or Debug:
            
            Display.blit(pygame.transform.scale(
                game_surface, Display.get_size()), (0, 0))
            pygame.display.update()  
        else:
            
            Display.blit(pygame.transform.scale(
                game_surface, Display.get_size()), (0, 0))
            
            pygame.display.update(screen_updates)
        
        screen_updates = []

def mouse_position():
    pos = pygame.mouse.get_pos()
    if Display_scaling:
        return screen_scaling(pos)
    else:
        return pos
    
def gameplay():  
    global Track_mask, Player_positions, Race_time, Countdown, Window_screenshot, button_trigger, \
        Debug, Screen, Animations, Mute_volume, Music_volume, Sfx_volume, loaded_bin, loaded_sounds, \
        Current_lap, Window_sleep, Game_end, music_thread, present_window, Game_paused, loading_thread, Machines_available, \
        Player_list
    Game_paused = False
    present_window = ''
    game_countdown = 0
    game_countdown_timer = 0
    Player_positions = []
    Player_list = []
    power_ups = []
    triggered_power_ups = []
    Race_time = pygame.time.get_ticks()
    Game_end = False
    game_quit = False
    saved_timer = 0
    lap_timer = 0
    music_thread = Thread(name='music_thread', target=game_menu_loop)
    full_map = pygame.Surface((WIDTH, HEIGHT))
    for layer in range(0, 3):
        full_map.blit(pygame.transform.scale(pygame.image.load(
            Map.layer(layer)), (WIDTH, HEIGHT)), (0, 0))
    
    checkpoint_positions = Map.layer(3)
    checkpoint_rectangles = []
    for point in checkpoint_positions:
        checkpoint_rectangles.append(pygame.rect.Rect(*point))
    for pos in range(1, 7):  
        full_map.blit(pygame.transform.rotate(pygame.transform.scale(pygame.image.load(bin.tile(
            'road', 84)), (50, 80)), Map.start_pos(pos)[2]),
            (Map.start_pos(pos)[0] - 40, Map.start_pos(pos)[1] - 25))
    Track_mask = pygame.mask.from_surface(pygame.transform.scale(
        pygame.image.load(Map.layer(2)), (WIDTH, HEIGHT)))
    checkpoint_surfaces = []
    Track_mask.invert()
    if not Debug:  
        pygame.mouse.set_visible(False)
    for player in range(0, Player_amount):
        Player_list.append(Car(Players[player]))
    npc_list = []
    if Enemy_Amount != 0:
        npc_pos = 1
        while len(npc_list) <= Enemy_Amount - 1:
            if Player_amount == 1 and npc_pos != Players[0].start_pos or Player_amount == 2 and \
                    npc_pos != Players[0].start_pos and npc_pos != Players[1].start_pos or Player_amount == 3 and \
                    npc_pos != Players[0].start_pos and npc_pos != Players[1].start_pos and \
                    npc_pos != Players[2].start_pos or Player_amount == 4 and npc_pos != Players[0].start_pos and \
                    npc_pos != Players[1].start_pos and npc_pos != Players[2].start_pos and npc_pos != Players[3] or \
                    Player_amount == 5 and npc_pos != Players[0].start_pos and npc_pos != Players[1].start_pos and \
                    npc_pos != Players[2].start_pos and npc_pos != Players[3] and npc_pos != Players[4].start_pos or \
                    Player_amount == 5 and npc_pos != Players[0].start_pos and npc_pos != Players[1].start_pos and \
                    npc_pos != Players[2].start_pos and npc_pos != Players[3] and npc_pos != Players[4].start_pos and \
                    npc_pos != Players[5].start_pos:
                npc_list.append(Enemy_machine(Player(npc_pos - 1, is_player=False)))
            elif Player_amount <= 0:
                raise ValueError("There are no players!")
            npc_pos += 1
    Machines_available = []
    for player in Player_list:
        Machines_available.append(player)
    for npc in npc_list:
        Machines_available.append(npc)
    if not Player_list and not npc_list:
        raise ValueError("There are no players or AIs!")
    pygame.time.wait(1000)
    if Animations:
        loading_thread_event.set()  
        if loading_thread.is_alive():
            loading_thread.join()
    Window.blit(full_map, (0, 0))  
    for player in Player_list:
        player.draw()
    for npc in npc_list:
        npc.draw()
    game_interface(Player_list, 0, 0)
    black_initialisation(show_loading=True)  
    if Countdown and not Debug:
        for pos_y in range(-108, 1, 2):  
            Clock.tick(FPS)
            Window.blit(pygame.image.load(
                bin.traffic_light(0)), (822, pos_y))
            screen_updates.append((822, pos_y, 276, 108))
            for player in Player_list:
                player.draw()
            for npc in npc_list:
                npc.draw()
            screen_refresh(full_screen=True)
        
        pygame.time.wait(1000)
        tl_stage = 0  
        start_time = pygame.time.get_ticks()
        while Countdown:
            Clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DELETE:
                        
                        pygame.quit()
                        quit()
                elif event.type == pygame.FULLSCREEN:
                    pygame.display.toggle_fullscreen()
                    screen_refresh(full_screen=True)
            if pygame.time.get_ticks() >= start_time + 5000:
                Window.blit(pygame.image.load(
                    bin.traffic_light(4)), (822, 0))
                screen_updates.append((822, 0, 276, 108))
                screen_refresh()
                play_music('traffic light finish')
                pygame.time.wait(150)
                Countdown = False
            elif pygame.time.get_ticks() >= start_time + 4000:
                Window.blit(pygame.image.load(
                    bin.traffic_light(3)), (822, 0))
                screen_updates.append((822, 0, 276, 108))
                if tl_stage != 3:
                    play_music('traffic light advance')
                    tl_stage = 3
            elif pygame.time.get_ticks() >= start_time + 3000:
                Window.blit(pygame.image.load(
                    bin.traffic_light(2)), (822, 0))
                screen_updates.append((822, 0, 276, 108))
                if tl_stage != 2:
                    play_music('traffic light advance')
                    tl_stage = 2
            elif pygame.time.get_ticks() >= start_time + 2000:
                Window.blit(pygame.image.load(
                    bin.traffic_light(1)), (822, 0))
                screen_updates.append((822, 0, 276, 108))
                if tl_stage != 1:
                    play_music('traffic light advance')
                    tl_stage = 1
            for player in Player_list:
                player.draw()
            for npc in npc_list:
                npc.draw()
            screen_refresh(full_screen=True)
    pygame.mixer.music.unpause()
    while not Game_end and not game_quit:  
        if Player_positions:
            if Current_lap != Player_positions[0].laps:
                Current_lap = Player_positions[0].laps
                if Current_lap > Total_laps:
                    play_music('lap finish')
                else:
                    play_music('lap advance')
                    lap_timer = pygame.time.get_ticks() + 3000
        else:
            Current_lap = 0
        if not Window_sleep:
            
            Clock.tick(30)
        else:
            Clock.tick(5)
        if not music_thread.is_alive() and not Mute_volume and Music_volume:
            music_thread_event.clear()
            music_thread = Thread(name='music_thread', target=game_menu_loop)
            music_thread.start()
        elif music_thread.is_alive() and (Mute_volume or not Music_volume):
            music_thread_event.set()
            music_thread.join()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if music_thread.is_alive():
                    music_thread_event.set()
                    music_thread.join(timeout=0.25)
                pygame.quit()
                quit()
            elif event.type == pygame.FULLSCREEN:
                pygame.display.toggle_fullscreen()
                screen_refresh(full_screen=True)
            elif event.type == pygame.WINDOWFOCUSLOST and not game_countdown and not Debug:
                if not game_countdown:
                    if not Game_paused:
                        Game_paused = True
                        play_music('pause out')
                        Music_volume -= 0.05 if Music_volume >= 0.06 else 0
                        pygame.mixer.music.set_volume(Music_volume)
                        pygame.mouse.set_visible(True)
                        Window_screenshot = Window.copy()
                        Window_screenshot.set_alpha(80)
                        black_conclusion(paused=True, speed=15)
                    Window_sleep = True
            elif event.type == pygame.WINDOWFOCUSGAINED:
                Window_sleep = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    pygame.display.toggle_fullscreen()
                    screen_refresh(full_screen=True)
                elif event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN and present_window != 'controls':
                    if not game_countdown:
                        if not Game_paused:
                            Game_paused = True
                            play_music('pause out')
                            Music_volume -= 0.05 if Music_volume >= 0.06 else 0
                            pygame.mixer.music.set_volume(Music_volume)
                            pygame.mouse.set_visible(True)
                            Window_screenshot = Window.copy()
                            Window_screenshot.set_alpha(80)
                            black_conclusion(paused=True, speed=15)
                        else:
                            Game_paused = False
                            play_music('pause in')
                            Music_volume += 0.05 if Music_volume >= 0.06 else 0
                            pygame.mixer.music.set_volume(Music_volume)
                            black_initialisation(paused=True, speed=15,
                                            window=present_window)
                            present_window = ''
                elif event.key == pygame.K_DELETE:  
                    print(mouse_position())
                    if music_thread.is_alive():
                        music_thread_event.set()
                        music_thread.join(timeout=0.25)
                    pygame.quit()
                    quit()
        if Game_paused:
            
            mouse_pointer_position = mouse_position()
            if not present_window:
                window_is_paused()  
                
                
                if 768 <= mouse_pointer_position[0] <= 1151 and 359 <= mouse_pointer_position[1] <= 467:
                    x = CENTRE[0] - 192
                    y = CENTRE[1] - 180
                    tile(x, y, 'sand road', 73, grid=False,
                         game_surface=second_screen)  
                    tile(x + 128, y, 'sand road', 88,
                         grid=False, game_surface=second_screen)
                    tile(x + 256, y, 'sand road', 57,
                         grid=False, game_surface=second_screen)
                    render_text_on_screen(
                        x + 193, y + 20, 'Resume', BLACK, 70, game_surface=second_screen)
                    buttons = pygame.mouse.get_pressed()
                    if buttons[0] and not button_trigger:
                        button_trigger = True
                        Game_paused = False
                        play_music('pause in')
                        Music_volume += 0.05 if Music_volume >= 0.06 else 0
                        pygame.mixer.music.set_volume(Music_volume)
                        black_initialisation(window=present_window, speed=9)
                    elif not buttons[0] and button_trigger:
                        button_trigger = False
                
                elif 768 <= mouse_pointer_position[0] <= 1151 and 509 <= mouse_pointer_position[1] <= 617:
                    x = CENTRE[0] - 192
                    y = CENTRE[1] - 30
                    tile(x, y, 'sand road', 73, grid=False,
                         game_surface=second_screen)  
                    tile(x + 128, y, 'sand road', 88,
                         grid=False, game_surface=second_screen)
                    tile(x + 256, y, 'sand road', 57,
                         grid=False, game_surface=second_screen)
                    render_text_on_screen(
                        x + 190, y + 20, 'Settings', BLACK, 70, game_surface=second_screen)
                    buttons = pygame.mouse.get_pressed()
                    if buttons[0] and not button_trigger:
                        button_trigger = True
                        play_music('menu button')
                        present_window = 'settings'
                        Music_volume += 0.05 if Music_volume >= 0.06 else 0
                        pygame.mixer.music.set_volume(Music_volume)
                        second_screen.fill(BLACK)
                        basic_settings(Window_screenshot,
                                        game_surface=second_screen)
                    elif not buttons[0] and button_trigger:
                        button_trigger = False
                
                elif 768 <= mouse_pointer_position[0] <= 1151 and 660 <= mouse_pointer_position[1] <= 767:
                    x = CENTRE[0] - 192
                    y = CENTRE[1] + 120
                    tile(x, y, 'sand road', 73, grid=False,
                         game_surface=second_screen)  
                    tile(x + 128, y, 'sand road', 88,
                         grid=False, game_surface=second_screen)
                    tile(x + 256, y, 'sand road', 57,
                         grid=False, game_surface=second_screen)
                    render_text_on_screen(
                        x + 193, y + 20, 'Controls', BLACK, 70, game_surface=second_screen)
                    buttons = pygame.mouse.get_pressed()
                    if buttons[0] and not button_trigger:
                        button_trigger = True
                        play_music('menu button')
                        present_window = 'controls'
                        second_screen.fill(BLACK)
                        player_control_screen()
                    elif not buttons[0] and button_trigger:
                        button_trigger = False
                
                elif 832 <= mouse_pointer_position[0] <= 1087 and 810 <= mouse_pointer_position[1] <= 917:
                    x = CENTRE[0] - 128
                    y = CENTRE[1] + 270
                    tile(x, y, 'sand road', 73, grid=False,
                         game_surface=second_screen)  
                    tile(x + 128, y, 'sand road', 57,
                         grid=False, game_surface=second_screen)
                    render_text_on_screen(
                        x + 130, y + 20, 'Quit', BLACK, 70, game_surface=second_screen)
                    buttons = pygame.mouse.get_pressed()
                    if buttons[0] and not button_trigger:
                        button_trigger = True
                        play_music('menu button')
                        present_window = 'confirm quit'
                        second_screen.fill(BLACK)
                        quit_confirmation(
                            Window_screenshot, game_surface=second_screen)
                    elif not buttons[0] and button_trigger:
                        button_trigger = False
            elif present_window == 'settings':
                second_screen.fill(BLACK)
                
                basic_settings(Window_screenshot, game_surface=second_screen)
                mouse_pointer_position = mouse_position()  
                
                if 396 <= mouse_pointer_position[0] <= 421 and 298 <= mouse_pointer_position[1] <= 324:
                    draw_side_arrow((409, 311), 'left', width=25,
                                    height=25, border=GREY, surface=second_screen)
                    buttons = pygame.mouse.get_pressed()
                    if buttons[0] and not button_trigger and device_screen_resolution <= device_information[Screen]:
                        button_trigger = True
                        play_music('option down')
                        resolution_decrease()
                    elif not buttons[0] and button_trigger:
                        button_trigger = False
                
                elif 606 <= mouse_pointer_position[0] <= 631 and 298 <= mouse_pointer_position[1] <= 324:
                    draw_side_arrow((619, 311), 'right', width=25,
                                    height=25, border=GREY, surface=second_screen)
                    buttons = pygame.mouse.get_pressed()
                    if buttons[0] and not button_trigger and device_screen_resolution <= device_information[Screen]:
                        button_trigger = True
                        play_music('option up')
                        resolution_increase()
                    elif not buttons[0] and button_trigger:
                        button_trigger = False
                
                elif 1290 <= mouse_pointer_position[0] <= 1315 and 298 <= mouse_pointer_position[1] <= 324:
                    draw_side_arrow((1303, 311), 'left', width=25,
                                    height=25, border=GREY, surface=second_screen)
                    buttons = pygame.mouse.get_pressed()
                    if buttons[0] and not button_trigger:
                        button_trigger = True
                        play_music('option down')
                        if Animations:
                            Animations = False
                        else:
                            Animations = True
                    elif not buttons[0] and button_trigger:
                        button_trigger = False
                
                elif 1500 <= mouse_pointer_position[0] <= 1526 and 298 <= mouse_pointer_position[1] <= 324:
                    draw_side_arrow((1513, 311), 'right', width=25,
                                    height=25, border=GREY, surface=second_screen)
                    buttons = pygame.mouse.get_pressed()
                    if buttons[0] and not button_trigger:
                        button_trigger = True
                        play_music('option up')
                        if Animations:
                            Animations = False
                        else:
                            Animations = True
                    elif not buttons[0] and button_trigger:
                        button_trigger = False
                
                elif 1270 <= mouse_pointer_position[0] <= 1296 and 649 <= mouse_pointer_position[1] <= 675:
                    draw_side_arrow((1283, 662), 'left', width=25,
                                    height=25, border=GREY, surface=second_screen)
                    buttons = pygame.mouse.get_pressed()
                    if buttons[0] and not button_trigger:
                        button_trigger = True
                        if Mute_volume:
                            Mute_volume = False
                            music_thread_event.clear()
                            music_thread = Thread(
                                name='music_thread', target=game_menu_loop)
                            pygame.mixer.music.unpause()
                            music_thread.start()
                        else:
                            Mute_volume = True
                            if music_thread.is_alive():
                                music_thread_event.set()
                                music_thread.join()
                                pygame.mixer.music.pause()
                        loaded_sounds = []
                        play_music('option down')
                    elif not buttons[0] and button_trigger:
                        button_trigger = False
                
                elif 1520 <= mouse_pointer_position[0] <= 1546 and 649 <= mouse_pointer_position[1] <= 675:
                    draw_side_arrow((1533, 662), 'right', width=25,
                                    height=25, border=GREY, surface=second_screen)
                    buttons = pygame.mouse.get_pressed()
                    if buttons[0] and not button_trigger:
                        button_trigger = True
                        if Mute_volume:
                            Mute_volume = False
                            music_thread_event.clear()
                            music_thread = Thread(
                                name='music_thread', target=game_menu_loop)
                            pygame.mixer.music.unpause()
                            music_thread.start()
                        else:
                            Mute_volume = True
                            if music_thread.is_alive():
                                music_thread_event.set()
                                music_thread.join()
                                pygame.mixer.music.pause()
                        loaded_sounds = []
                        play_music('option up')
                    elif not buttons[0] and button_trigger:
                        button_trigger = False
                
                elif 822 <= mouse_pointer_position[0] <= 847 and 649 <= mouse_pointer_position[1] <= 675:
                    if Music_volume <= 0:
                        draw_side_arrow((835, 662), 'left', width=25,
                                        height=25, border=RED, surface=second_screen)
                    else:
                        draw_side_arrow(
                            (835, 662), 'left', width=25, height=25, border=GREY, surface=second_screen)
                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger:
                            button_trigger = True
                            if Music_volume - 0.01 <= 0:
                                Music_volume = 0
                                pygame.mixer.music.pause()
                            elif Music_volume - 0.01 > 0:
                                Music_volume = round(Music_volume - 0.01, 3)
                            play_music('option down')
                            pygame.mixer.music.set_volume(Music_volume)
                        elif not buttons[0] and button_trigger:
                            button_trigger = False
                
                elif 1072 <= mouse_pointer_position[0] <= 1097 and 649 <= mouse_pointer_position[1] <= 675:
                    if Music_volume >= 1:
                        draw_side_arrow(
                            (1085, 662), 'right', width=25, height=25, border=RED, surface=second_screen)
                    else:
                        draw_side_arrow(
                            (1085, 662), 'right', width=25, height=25, border=GREY, surface=second_screen)
                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger:
                            button_trigger = True
                            if Music_volume + 0.01 >= 1:
                                Music_volume = 1
                            elif Music_volume + 0.01 < 1:
                                Music_volume = round(Music_volume + 0.01, 3)
                            if not pygame.mixer.music.get_busy() and not Mute_volume:
                                pygame.mixer.music.unpause()
                            play_music('option up')
                            pygame.mixer.music.set_volume(Music_volume)
                        elif not buttons[0] and button_trigger:
                            button_trigger = False
                
                elif 391 <= mouse_pointer_position[0] <= 416 and 649 <= mouse_pointer_position[1] <= 675:
                    if Sfx_volume <= 0:
                        draw_side_arrow((404, 662), 'left', width=25,
                                        height=25, border=RED, surface=second_screen)
                    else:
                        draw_side_arrow(
                            (404, 662), 'left', width=25, height=25, border=GREY, surface=second_screen)
                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger:
                            button_trigger = True
                            if Sfx_volume - 0.01 <= 0:
                                Sfx_volume = 0
                            elif Sfx_volume - 0.01 > 0:
                                Sfx_volume = round(Sfx_volume - 0.01, 4)
                            loaded_sounds = []  
                            play_music('option down')
                        elif not buttons[0] and button_trigger:
                            button_trigger = False
                
                elif 611 <= mouse_pointer_position[0] <= 636 and 649 <= mouse_pointer_position[1] <= 675:
                    if Sfx_volume >= 1:
                        draw_side_arrow((624, 662), 'right', width=25,
                                        height=25, border=RED, surface=second_screen)
                    else:
                        draw_side_arrow((624, 662), 'right', width=25,
                                        height=25, border=GREY, surface=second_screen)
                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger:
                            button_trigger = True
                            if Sfx_volume + 0.01 >= 1:
                                Sfx_volume = 1
                            elif Sfx_volume + 0.01 < 1:
                                Sfx_volume = round(Sfx_volume + 0.01, 4)
                            loaded_sounds = []  
                            play_music('option up')
                        elif not buttons[0] and button_trigger:
                            button_trigger = False
                
                
                
                
                
                
                
                
                
                
                
                elif 800 <= mouse_pointer_position[0] <= 1117 and 940 <= mouse_pointer_position[1] <= 1047:
                    pos_x = 800
                    pos_y = 940
                    tile(pos_x, pos_y, 'sand road', 73, grid=False,game_surface=second_screen)
                    tile(pos_x + 65, pos_y, 'sand road', 88, grid=False,game_surface=second_screen)
                    tile(pos_x + 190, pos_y, 'sand road', 57, grid=False,game_surface=second_screen)
                    render_text_on_screen(
                        pos_x + 160, pos_y + 20, 'Back', BLACK, 70,game_surface=second_screen)
                
                    buttons = pygame.mouse.get_pressed()
                    if buttons[0] and not button_trigger:
                        button_trigger = True
                        saved_timer = None
                        present_window = None
                        Music_volume -= 0.05 if Music_volume >= 0.06 else 0
                        pygame.mixer.music.set_volume(Music_volume)
                        play_music('menu button')  
                        window_is_paused()
                    elif not buttons[0] and button_trigger:
                        button_trigger = False
            elif present_window == 'confirm quit':
                second_screen.fill(BLACK)
                quit_confirmation(Window_screenshot,
                                    game_surface=second_screen)
                render_text_on_screen(
                    CENTRE[0], 300, 'You will lose all progress!', WHITE, 50, game_surface=second_screen)
                mouse_pointer_position = mouse_position()  
                
                if 347 <= mouse_pointer_position[0] <= 642 and 486 <= mouse_pointer_position[1] <= 593:
                    pos_x = 347
                    pos_y = CENTRE[1] - (tile_scale[1] // 2)
                    tile(pos_x, pos_y, 'sand road', 73, grid=False,
                         game_surface=second_screen)  
                    tile(pos_x + 85, pos_y, 'sand road', 88,
                         grid=False, game_surface=second_screen)
                    tile(pos_x + 168, pos_y, 'sand road', 57,
                         grid=False, game_surface=second_screen)
                    render_text_on_screen(
                        pos_x + 153, pos_y + 20, 'Yes', BLACK, 70, game_surface=second_screen)
                    buttons = pygame.mouse.get_pressed()
                    if buttons[0] and not button_trigger:
                        button_trigger = True
                        Music_volume += 0.05 if Music_volume >= 0.06 else 0
                        play_music('menu button')  
                        game_quit = True
                    elif not buttons[0] and button_trigger:
                        button_trigger = False
                
                elif 1307 <= mouse_pointer_position[0] <= 1602 and 486 <= mouse_pointer_position[1] <= 593:
                    pos_x = CENTRE[0] + 347
                    pos_y = CENTRE[1] - (tile_scale[1] // 2)
                    tile(pos_x, pos_y, 'sand road', 73, grid=False,
                         game_surface=second_screen)  
                    tile(pos_x + 85, pos_y, 'sand road', 88,
                         grid=False, game_surface=second_screen)
                    tile(pos_x + 168, pos_y, 'sand road', 57,
                         grid=False, game_surface=second_screen)
                    render_text_on_screen(
                        pos_x + 153, pos_y + 20, 'No', BLACK, 70, game_surface=second_screen)
                    buttons = pygame.mouse.get_pressed()
                    if buttons[0] and not button_trigger:
                        button_trigger = True
                        play_music('menu button')  
                        present_window = None
                        window_is_paused()
                    elif not buttons[0] and button_trigger:
                        button_trigger = False
            elif present_window == 'controls':
                second_screen.fill(BLACK)
                player_control_screen()
                mouse_pointer_position = mouse_position()  
                player = None
                direction = None
                
                if 332 <= mouse_pointer_position[0] <= 587 and 910 <= mouse_pointer_position[1] <= 1017:
                    x = 332
                    y = HEIGHT - 170
                    tile(x, y, 'sand road', 73, grid=False,
                         game_surface=second_screen)  
                    tile(x + 128, y, 'sand road', 57,
                         grid=False, game_surface=second_screen)
                    render_text_on_screen(
                        x + 130, y + 20, 'Quit', BLACK, 70, game_surface=second_screen)
                    buttons = pygame.mouse.get_pressed()
                    if buttons[0] and not button_trigger:
                        button_trigger = True
                        play_music('menu button')
                        present_window = 'controls quit'
                        second_screen.fill(BLACK)
                        quit_confirmation(
                            Window_screenshot, game_surface=second_screen)
                    elif not buttons[0] and button_trigger:
                        button_trigger = False
                
                elif 328 <= mouse_pointer_position[0] <= 352 and 425 <= mouse_pointer_position[1] <= 475 and not Player_list[0].test_alpha:
                    if not change_controls_left(Player_list[0].input_type):
                        draw_side_arrow(
                            (340, 450), 'left', border=RED, width=25, height=50, surface=second_screen)
                    else:
                        draw_side_arrow(
                            (340, 450), 'left', border=GREY, width=25, height=50, surface=second_screen)
                        player = Player_list[0]
                        direction = 'left'
                
                elif 568 <= mouse_pointer_position[0] <= 592 and 425 <= mouse_pointer_position[1] <= 475 and not Player_list[0].test_alpha:
                    if not change_controls_right(Player_list[0].input_type):
                        draw_side_arrow(
                            (580, 450), 'right', border=RED, width=25, height=50, surface=second_screen)
                    else:
                        draw_side_arrow(
                            (580, 450), 'right', border=GREY, width=25, height=50, surface=second_screen)
                        player = Player_list[0]
                        direction = 'right'
                
                elif Player_amount >= 2 and not Player_list[1].test_alpha and \
                        828 <= mouse_pointer_position[0] <= 852 and 425 <= mouse_pointer_position[1] <= 475:
                    if not change_controls_left(Player_list[1].input_type):
                        draw_side_arrow(
                            (840, 450), 'left', border=RED, width=25, height=50, surface=second_screen)
                    else:
                        draw_side_arrow(
                            (840, 450), 'left', border=GREY, width=25, height=50, surface=second_screen)
                        player = Player_list[1]
                        direction = 'left'
                
                elif Player_amount >= 2 and not Player_list[1].test_alpha and \
                        1068 <= mouse_pointer_position[0] <= 1092 and 425 <= mouse_pointer_position[1] <= 475:
                    if not change_controls_right(Player_list[1].input_type):
                        draw_side_arrow(
                            (1080, 450), 'right', border=RED, width=25, height=50, surface=second_screen)
                    else:
                        draw_side_arrow(
                            (1080, 450), 'right', border=GREY, width=25, height=50, surface=second_screen)
                        player = Player_list[1]
                        direction = 'right'
                if player and direction == 'left':  
                    buttons = pygame.mouse.get_pressed()
                    if buttons[0] and not button_trigger:
                        button_trigger = True
                        if player.input_type != 'test_alpha':
                            controls.remove(player.input_type)
                        player.input_type = change_controls_left(
                            player.input_type)
                        if player.input_type != 'test_alpha':
                            controls.append(player.input_type)
                    elif button_trigger and not buttons[0]:
                        button_trigger = False
                elif player and direction == 'right':  
                    buttons = pygame.mouse.get_pressed()
                    if buttons[0] and not button_trigger:
                        button_trigger = True
                        if player.input_type != 'test_alpha':
                            controls.remove(player.input_type)
                        player.input_type = change_controls_right(
                            player.input_type)
                        if player.input_type != 'test_alpha':
                            controls.append(player.input_type)
                    elif button_trigger and not buttons[0]:
                        button_trigger = False
                bound_players = 0
                for player in Player_list:
                    if player.input_type == 'wasd' or player.input_type == 'arrows' or (
                            player.input_type == 'test_alpha' and player.test_alpha):
                        bound_players += 1
                if bound_players == len(Player_list):
                    
                    
                    if 1268 <= mouse_pointer_position[0] <= 1651 and 910 <= mouse_pointer_position[1] <= 1017:
                        x = 1268
                        y = HEIGHT - 170
                        tile(x, y, 'sand road', 73, grid=False,
                             game_surface=second_screen)  
                        tile(x + 128, y, 'sand road', 88,
                             grid=False, game_surface=second_screen)
                        tile(x + 256, y, 'sand road', 57,
                             grid=False, game_surface=second_screen)
                        render_text_on_screen(
                            x + 193, y + 20, 'Confirm', BLACK, 70, game_surface=second_screen)
                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger:
                            for player in Player_list:
                                if player.input_type == 'test_alpha' and player.test_alpha:
                                    player.set_controls(player.test_alpha)
                                else:
                                    player.set_controls(player.input_type)
                            button_trigger = True
                            play_music('menu button')
                            present_window = ''
                            second_screen.fill(BLACK)
                            window_is_paused()
                        elif not buttons[0] and button_trigger:
                            button_trigger = False
            elif present_window == 'controls quit':
                second_screen.fill(BLACK)
                quit_confirmation(Window_screenshot,
                                    game_surface=second_screen)
                render_text_on_screen(
                    CENTRE[0], 300, 'All progress will be lost!', WHITE, 50, game_surface=second_screen)
                mouse_pointer_position = mouse_position()  
                
                if 347 <= mouse_pointer_position[0] <= 642 and 486 <= mouse_pointer_position[1] <= 593:
                    pos_x = 347
                    pos_y = CENTRE[1] - (tile_scale[1] // 2)
                    tile(pos_x, pos_y, 'sand road', 73, grid=False,
                         game_surface=second_screen)  
                    tile(pos_x + 85, pos_y, 'sand road', 88,
                         grid=False, game_surface=second_screen)
                    tile(pos_x + 168, pos_y, 'sand road', 57,
                         grid=False, game_surface=second_screen)
                    render_text_on_screen(
                        pos_x + 153, pos_y + 20, 'Yes', BLACK, 70, game_surface=second_screen)
                    buttons = pygame.mouse.get_pressed()
                    if buttons[0] and not button_trigger:
                        button_trigger = True
                        Music_volume += 0.05 if Music_volume >= 0.06 else 0
                        play_music('menu button')  
                        game_quit = True
                    elif not buttons[0] and button_trigger:
                        button_trigger = False
                
                elif 1307 <= mouse_pointer_position[0] <= 1602 and 486 <= mouse_pointer_position[1] <= 593:
                    pos_x = CENTRE[0] + 347
                    pos_y = CENTRE[1] - (tile_scale[1] // 2)
                    tile(pos_x, pos_y, 'sand road', 73, grid=False,
                         game_surface=second_screen)  
                    tile(pos_x + 85, pos_y, 'sand road', 88,
                         grid=False, game_surface=second_screen)
                    tile(pos_x + 168, pos_y, 'sand road', 57,
                         grid=False, game_surface=second_screen)
                    render_text_on_screen(
                        pos_x + 153, pos_y + 20, 'No', BLACK, 70, game_surface=second_screen)
                    buttons = pygame.mouse.get_pressed()
                    if buttons[0] and not button_trigger:
                        button_trigger = True
                        play_music('menu button')  
                        present_window = 'controls'
                        player_control_screen()
                    elif not buttons[0] and button_trigger:
                        button_trigger = False
            if Game_paused:  
                screen_refresh(full_screen=True, game_surface=second_screen)
        else:  
            Window.blit(full_map, (0, 0))
            if Countdown > -108:  
                Window.blit(pygame.image.load(
                    bin.traffic_light(4)), (822, Countdown * 2))
                Countdown -= 2
            if powerups and len(power_ups) < 15 * Player_amount:  
                rand = randint(0, 900 // (10 + Player_amount + Enemy_Amount))
                if not rand:
                    rand = randint(0, 5)
                    if not rand or rand == 1:
                        ver = 'repair'
                    elif rand == 2:
                        ver = 'boost'
                    elif rand == 3 or rand == 4:
                        ver = 'bullet'
                    elif rand == 5:
                        ver = 'lightning'
                    else:
                        raise ValueError(
                            'gameplay() [ver] Incorrect value: ' + str(rand))
                    game_surface = pygame.transform.scale(
                        pygame.image.load(bin.power_up(ver)), (30, 30))
                    game_surface.set_colorkey(BLACK)
                    mask = pygame.mask.from_surface(game_surface)
                    timestamp = pygame.time.get_ticks() + 1000  
                    while timestamp > pygame.time.get_ticks():
                        pos_x = randint(0, WIDTH)
                        pos_y = randint(0, HEIGHT)
                        if not Track_mask.overlap(mask, (pos_x, pos_y)):
                            power_up = Object(game_surface, pygame.rect.Rect(
                                pos_x, pos_y, 30, 30), mask)
                            power_up.active = True
                            power_up.ver = ver
                            power_up.timeout = pygame.time.get_ticks() + 15000
                            power_ups.append(power_up)
                            break
                    else:
                        print('ERR: Powerup generation timed out!')
            for power_up in power_ups:
                if power_up.timeout <= pygame.time.get_ticks():
                    power_ups.remove(power_up)
                    triggered_power_ups.append(power_up)
                else:
                    Window.blit(power_up.game_surface, power_up.rect.topleft)
            lightning_target = None
            if powerups:
                for vehicle in Player_positions:
                    if not vehicle.debris_penalty:
                        vehicle.lightning_target = True
                        lightning_target = vehicle
                        break
                for vehicle in Player_positions:
                    if vehicle.lightning_target and vehicle != lightning_target:
                        vehicle.lightning_target = False
            for veh in Machines_available:  
                veh.update()  
                veh.check_track_collisions()  
                
                veh.check_checkpoints(checkpoint_rectangles)
                if veh.laps > Total_laps and not game_countdown:  
                    
                    game_countdown = pygame.time.get_ticks() + 6000
                for other_veh in Machines_available:  
                    if other_veh != veh:  
                        veh.check_car_collision(other_veh)  
                for power_up in power_ups:  
                    if veh.mask.overlap(power_up.mask, (power_up.rect.left - veh.rect.left,
                                                        power_up.rect.top - veh.rect.top)) and not veh.finished:
                        if power_up.ver == 'lightning':  
                            
                            for vehicle in Player_positions:
                                if not vehicle.debris_penalty:  
                                    
                                    vehicle.power_up('lightning')
                                    break
                        else:
                            veh.power_up(power_up.ver)  
                        play_music('power up')  
                        triggered_power_ups.append(
                            power_up)  
                        
                        power_ups.remove(power_up)
                veh.draw()
            for power_up in triggered_power_ups:
                if power_up.active:  
                    game_surface = pygame.surface.Surface((30, 30))
                    game_surface.fill(WHITE)
                    img = pygame.transform.scale(pygame.image.load(bin.power_up(
                        power_up.ver, active=False)), (30, 30))
                    game_surface.blit(img, (0, 0))
                    game_surface.set_colorkey(WHITE)
                    game_surface.set_alpha(255)
                    power_up.game_surface = game_surface
                    power_up.active = False
                alpha = power_up.game_surface.get_alpha()
                if not power_up.game_surface.get_alpha() - 20:
                    triggered_power_ups.remove(power_up)
                else:
                    power_up.game_surface.set_alpha(alpha - 20)
                    Window.blit(power_up.game_surface, power_up.rect.topleft)
            if game_countdown:  
                game_countdown_timer = game_countdown - pygame.time.get_ticks()
                if game_countdown_timer // 1000 <= 0:
                    Game_end = True
            Player_positions = vehicle_location()  
            game_interface(Player_list, game_countdown_timer,
                         lap_timer)  
            screen_refresh(full_screen=True)  
        if Window_sleep:
            sleep(0.5)
    if not game_quit:
        Race_time = pygame.time.get_ticks() - Race_time  
        seconds = Race_time // 1000
        minutes = 0
        hours = 0
        if seconds >= 60:
            minutes = seconds // 60
            seconds -= minutes * 60
        if minutes >= 60:
            hours = minutes // 60
            minutes -= hours * 60
        if seconds and not minutes and not hours:
            Race_time = str(seconds) + 's'
        elif seconds and minutes and not hours:
            Race_time = str(minutes) + 'm ' + str(seconds) + 's'
        elif seconds and minutes and hours:
            Race_time = str(hours) + 'h ' + str(minutes) + \
                'm ' + str(seconds) + 's'
    pygame.mixer.music.fadeout(250)
    if music_thread.is_alive():
        music_thread_event.set()
        music_thread.join()
    for player in Player_list:
        if player.test_alpha:
            player.test_alpha.stop_rumble()
    black_conclusion(show_loading=True)
    if Animations:
        loading_thread_event.clear()
        loading_thread = Thread(name='loading_thread', target=render_animation, args=(
            CENTRE[0], CENTRE[1] + 300))
        loading_thread.start()  
    return game_quit

def main():
    global Player_amount, Enemy_Amount, Total_laps, Debug, loaded_bin, Music_volume, Screen, Sfx_volume, \
        loaded_sounds, Mute_volume, Animations, Map, selected_text_entry, button_trigger, Window_sleep, music_thread, \
        loading_thread, powerups, Enemy_machines, Enemy_machine_color, present_window, Players, test_alphas, controls, \
        selected_text_entry
    music_thread_event.clear()
    menu_loop = True  
    saved_timer = None  
    leaderboard = False
    present_window = 'main menu'  
    prev_window = ''  
    car = MenuCar()
    
    bg = menu_background(top=True, right=True, bottom=True, left=True)
    new_bg = bg
    music_thread = Thread(name='music_thread', target=menu_loop_music)
    loading_thread = Thread(name='loading_thread', target=render_animation, args=(
        CENTRE[0], CENTRE[1] + 300))
    Players.append(Player(0))
    Player_amount = 1
    if Intro_screen and not Debug:
        intro_bg = menu_background()
        Window.blit(intro_bg, (0, 0))
        render_text_on_screen(
            CENTRE[0], CENTRE[1] - 150, 'Road Fighter', ORANGE, 150, type1=True, type3=True)
        screen_refresh(full_screen=True)
        play_music('boot')
        pygame.time.wait(2000)
    while True:  
        while menu_loop:  
            if not Window_sleep:
                Clock.tick(FPS)  
            else:
                Clock.tick(2)
            if not music_thread.is_alive() and not Mute_volume and Music_volume:
                music_thread_event.clear()
                music_thread = Thread(
                    name='music_thread', target=menu_loop_music)
                music_thread.start()
            elif music_thread.is_alive() and (Mute_volume or not Music_volume):
                music_thread_event.set()
                music_thread.join()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    if music_thread.is_alive():
                        music_thread_event.set()
                        music_thread.join(timeout=0.25)
                    pygame.quit()
                    quit()
                elif event.type == pygame.FULLSCREEN:
                    pygame.display.toggle_fullscreen()
                    Window.blit(bg, (0, 0))
                    screen_refresh(full_screen=True)
                elif event.type == pygame.WINDOWFOCUSLOST:
                    Window_sleep = True
                    if not Mute_volume:
                        pygame.mixer.music.pause()
                elif event.type == pygame.WINDOWFOCUSGAINED:
                    Window_sleep = False
                    if not Mute_volume:
                        pygame.mixer.music.unpause()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F11:
                        pygame.display.toggle_fullscreen()
                        Window.blit(bg, (0, 0))
                        screen_refresh(full_screen=True)
                    elif event.key == pygame.K_ESCAPE:  
                        print(mouse_position())
                        if music_thread.is_alive():
                            music_thread_event.set()
                            music_thread.join(timeout=0.25)
                        pygame.quit()
                        quit()
                    elif event.key == pygame.K_RETURN and selected_text_entry:  
                        selected_text_entry = 0
                    elif event.key == pygame.K_BACKSPACE:
                        Players[selected_text_entry -
                                1].name = Players[selected_text_entry - 1].name[:-1]
                    if selected_text_entry and len(Players[selected_text_entry - 1].name) <= 12 and \
                            event.key != pygame.K_BACKSPACE and event.key != pygame.K_DELETE and \
                            event.key != pygame.K_TAB:
                        Players[selected_text_entry - 1].name += event.unicode
                        Players[selected_text_entry -
                                1].name = Players[selected_text_entry - 1].name.title()
            
            if present_window == 'main menu':
                if prev_window != present_window:  
                    bg = new_bg  
                    main_menu_page(bg)  
                    car.draw()
                    if prev_window == 'leaderboard' or prev_window == 'tutorial':
                        black_initialisation()
                    screen_refresh(full_screen=True)  
                    prev_window = present_window  
                main_menu_page(bg)  
                
                mouse_pointer_position = mouse_position()
                
                
                if 800 <= mouse_pointer_position[0] <= 1117 and 940 <= mouse_pointer_position[1] <= 1047:
                    pos_x = 800
                    pos_y = 940
                    
                    tile(pos_x, pos_y, 'sand road', 73, grid=False)
                    tile(pos_x + 65, pos_y, 'sand road', 88, grid=False)
                    tile(pos_x + 190, pos_y, 'sand road', 57, grid=False)
                    render_text_on_screen(
                        pos_x + 160, pos_y + 20, 'Quit', BLACK, 70)
                    
                    buttons = pygame.mouse.get_pressed()
                    if buttons[0] and not button_trigger:
                        button_trigger = True
                        present_window = 'confirm quit'  
                        play_music('menu button')  
                        new_bg = menu_background(top=True)
                        if Animations:
                            car.animate('down', bg)
                            screen_animation(
                                main_menu_page, quit_confirmation, bg, new_bg, car, 'down')
                        else:
                            quit_confirmation(bg)
                            car.rotate(180)
                            screen_refresh(full_screen=True)
                    elif not buttons[0] and button_trigger:
                        button_trigger = False
                
                
                elif 340 <= mouse_pointer_position[0] <= 657 and 324 <= mouse_pointer_position[1] <= 431:
                    pos_x = 340
                    pos_y = 324
                    
                    tile(pos_x, pos_y, 'sand road', 73, grid=False)
                    tile(pos_x + 65, pos_y, 'sand road', 88, grid=False)
                    tile(pos_x + 190, pos_y, 'sand road', 57, grid=False)
                    render_text_on_screen(
                        pos_x + 160, pos_y + 20, 'Race', BLACK, 70)
                    buttons = pygame.mouse.get_pressed()  
                    if buttons[0] and not button_trigger:
                        button_trigger = True
                        present_window = 'choose map'  
                        play_music('menu button')  
                        new_bg = menu_background(bottom=True, top=True)
                        map_demo()  
                        if Animations:
                            car.animate('up', bg)
                            screen_animation(
                                main_menu_page, choose_map_window, bg, new_bg, car, 'up')
                        else:
                            choose_map_window(new_bg)
                            car.rotate(0)
                            car.move(960, 940)
                            
                            screen_refresh(full_screen=True)
                    elif not buttons[0] and button_trigger:
                        button_trigger = False
                
                
                elif 338 <= mouse_pointer_position[0] <= 671 and 648 <= mouse_pointer_position[1] <= 755:
                    pos_x = 340
                    pos_y = 648
                    tile(pos_x, pos_y, 'sand road', 73, grid=False)
                    tile(pos_x + 128, pos_y, 'sand road', 88, grid=False)
                    tile(pos_x + 205, pos_y, 'sand road', 57, grid=False)
                    render_text_on_screen(
                        pos_x + 163, pos_y + 20, 'Credits', BLACK, 70)
                    buttons = pygame.mouse.get_pressed()
                    if buttons[0] and not button_trigger:
                        button_trigger = True
                        present_window = 'credits'  
                        play_music('menu button')  
                        new_bg = menu_background(right=True)
                        if Animations:
                            car.animate('left', bg)
                            screen_animation(
                                main_menu_page, dev_credits, bg, new_bg, car, 'left')
                        else:
                            dev_credits(new_bg)
                            car.rotate(90)
                            
                            screen_refresh(full_screen=True)
                    elif not buttons[0] and button_trigger:
                        button_trigger = False
                
                elif 1220 <= mouse_pointer_position[0] <= 1604 and 324 <= mouse_pointer_position[1] <= 432:
                    x = 1220
                    y = 324
                    tile(x, y, 'sand road', 73, grid=False)  
                    tile(x + 128, y, 'sand road', 88, grid=False)
                    tile(x + 256, y, 'sand road', 57, grid=False)
                    render_text_on_screen(
                        x + 190, y + 20, 'Settings', BLACK, 70)
                    buttons = pygame.mouse.get_pressed()
                    if buttons[0] and not button_trigger:
                        button_trigger = True
                        present_window = 'settings'  
                        play_music('menu button')  
                        new_bg = menu_background(left=True)
                        if Animations:
                            car.animate('right', bg)
                            screen_animation(
                                main_menu_page, basic_settings, bg, new_bg, car, 'right')
                        else:
                            basic_settings(new_bg)
                            car.rotate(270)
                            
                            screen_refresh(full_screen=True)
                    elif not buttons[0] and button_trigger:
                        button_trigger = False
                
                elif 1220 <= mouse_pointer_position[0] <= 1604 and 648 <= mouse_pointer_position[1] <= 755:
                    x = 1220
                    y = 648
                    tile(x, y, 'sand road', 73, grid=False)  
                    tile(x + 128, y, 'sand road', 88, grid=False)
                    tile(x + 256, y, 'sand road', 57, grid=False)
                    render_text_on_screen(x + 190, y + 20, 'Hints', BLACK, 70)
                    buttons = pygame.mouse.get_pressed()
                    if buttons[0] and not button_trigger:
                        button_trigger = True
                        present_window = 'tutorial'  
                        play_music('menu button')  
                        new_bg = menu_background()
                        black_conclusion(car=car)
                    elif not buttons[0] and button_trigger:
                        button_trigger = False
            
            elif present_window == 'choose map':
                if prev_window != present_window:  
                    bg = new_bg  
                    choose_map_window(bg)
                    car.move(960, 940)
                    car.draw()
                    screen_refresh(full_screen=True)  
                    prev_window = present_window  
                choose_map_window(bg)
                mouse_pointer_position = mouse_position()
                
                if 403 <= mouse_pointer_position[0] <= 443 and 500 <= mouse_pointer_position[1] <= 580:
                    if maps.index.index(Map.name) <= 0:
                        draw_side_arrow((map_preview_pos[0] - 50,  
                                         map_preview_pos[1] + map_preview_size[1] // 2),
                                        'left', width=40, height=80, border=RED)
                    else:
                        draw_side_arrow((map_preview_pos[0] - 50,  
                                         map_preview_pos[1] + map_preview_size[1] // 2),
                                        'left', width=40, height=80, border=GREY)
                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger:
                            button_trigger = True
                            play_music('option down')
                            Map = maps.objs[maps.index.index(Map.name) - 1]()
                            map_demo()
                            screen_refresh(full_screen=True)
                        elif not buttons[0] and button_trigger:
                            button_trigger = False
                
                if 1477 <= mouse_pointer_position[0] <= 1517 and 500 <= mouse_pointer_position[1] <= 580:
                    if maps.index.index(Map.name) >= len(maps.index) - 1:
                        draw_side_arrow((map_preview_pos[0] + map_preview_size[0] + 50,
                                         map_preview_pos[1] + map_preview_size[1] // 2), 'right', width=40, height=80,
                                        border=RED)
                    else:
                        draw_side_arrow((map_preview_pos[0] + map_preview_size[0] + 50,
                                         map_preview_pos[1] + map_preview_size[1] // 2), 'right', width=40, height=80,
                                        border=GREY)
                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger:
                            button_trigger = True
                            play_music('option up')
                            Map = maps.objs[maps.index.index(Map.name) + 1]()
                            map_demo()
                            screen_refresh(full_screen=True)
                        elif not buttons[0] and button_trigger:
                            button_trigger = False
                
                if 528 <= mouse_pointer_position[0] <= 783 and 890 <= mouse_pointer_position[1] <= 997:
                    x = 528
                    y = 890
                    tile(x, y, 'sand road', 73, grid=False)  
                    tile(x + 128, y, 'sand road', 57, grid=False)
                    render_text_on_screen(x + 130, y + 20, 'Back', BLACK, 70)
                    buttons = pygame.mouse.get_pressed()
                    if buttons[0] and not button_trigger:
                        button_trigger = True
                        present_window = 'main menu'
                        play_music('menu button')  
                        new_bg = menu_background(
                            top=True, right=True, bottom=True, left=True)
                        if Animations:
                            car.animate('down', bg)
                            screen_animation(
                                choose_map_window, main_menu_page, bg, new_bg, car, 'down')
                        else:
                            main_menu_page(new_bg)
                            car.rotate(180)
                            car.move(*CENTRE)
                            screen_refresh(full_screen=True)
                    elif not buttons[0] and button_trigger:
                        button_trigger = False
                
                elif 1100 <= mouse_pointer_position[0] <= 1417 and 890 <= mouse_pointer_position[1] <= 997:
                    x = 1100
                    y = 890
                    tile(x, y, 'sand road', 73, grid=False)  
                    tile(x + 65, y, 'sand road', 88, grid=False)
                    tile(x + 190, y, 'sand road', 57, grid=False)
                    render_text_on_screen(x + 160, y + 20, 'Select', BLACK, 70)
                    buttons = pygame.mouse.get_pressed()  
                    
                    if buttons[0] and not button_trigger:
                        button_trigger = True
                        present_window = 'choose players'
                        play_music('menu button')  
                        new_bg = menu_background(top=True, bottom=True)
                        if Animations:
                            car.animate('up', bg)
                            screen_animation(
                                choose_map_window, player_screen, bg, new_bg, car, 'up')
                        else:
                            player_screen(new_bg)
                            car.rotate(0)
                            car.move(*CENTRE)
                            screen_refresh(full_screen=True)
                    elif not buttons[0] and button_trigger:
                        button_trigger = False
            
            elif present_window == 'choose players':
                if prev_window != present_window:  
                    bg = new_bg  
                    player_screen(bg)
                    car.draw()
                    screen_refresh(full_screen=True)  
                    prev_window = present_window  
                    selected_text_entry = 0
                player_screen(bg)
                mouse_pointer_position = mouse_position()
                
                if Player_amount != 1 and 400 <= mouse_pointer_position[0] <= 717 and 476 <= mouse_pointer_position[1] <= 583:
                    x = 400
                    y = 476
                    
                    tile(x, y, 'sand road', 73, grid=False)
                    tile(x + 65, y, 'sand road', 88, grid=False)
                    tile(x + 190, y, 'sand road', 57, grid=False)
                    render_text_on_screen(x + 160, y + 20, 'Single', BLACK, 70)
                    buttons = pygame.mouse.get_pressed()
                    if buttons[0] and not button_trigger:
                        button_trigger = True
                        selected_text_entry = 0
                        Player_amount = 1
                        Enemy_Amount = 3
                        while len(Players) != Player_amount:
                            if len(Players) < Player_amount:
                                Players.append(Player(len(Players)))
                            elif len(Players) > Player_amount:
                                if Players[len(Players) - 1].controls != 'test_alpha':
                                    controls.remove(
                                        Players[len(Players) - 1].controls)
                                Players.pop(len(Players) - 1)
                        play_music('menu button')
                    elif button_trigger and not buttons[0]:
                        button_trigger = False
                
                elif Player_amount != 2 and 1200 <= mouse_pointer_position[0] <= 1517 and 476 <= mouse_pointer_position[1] <= 583:
                    x = 1200
                    y = 476
                    
                    tile(x, y, 'sand road', 73, grid=False)
                    tile(x + 65, y, 'sand road', 88, grid=False)
                    tile(x + 190, y, 'sand road', 57, grid=False)
                    render_text_on_screen(x + 160, y + 20, 'Dual', BLACK, 70)
                    buttons = pygame.mouse.get_pressed()
                    if buttons[0] and not button_trigger:
                        button_trigger = True
                        selected_text_entry = 0
                        Player_amount = 2
                        Enemy_Amount = 2
                        while len(Players) != Player_amount:
                            if len(Players) < Player_amount:
                                Players.append(Player(len(Players)))
                            elif len(Players) > Player_amount:
                                if Players[len(Players) - 1].controls != 'test_alpha':
                                    controls.remove(
                                        Players[len(Players) - 1].controls)
                                Players.pop(len(Players) - 1)
                        play_music('menu button')
                    elif button_trigger and not buttons[0]:
                        button_trigger = False
                
                elif 210 <= mouse_pointer_position[0] <= 409 and 112 <= mouse_pointer_position[1] <= 211:
                    pos_x = 210
                    pos_y = 112
                    tile(pos_x, pos_y, 'sand road', 73, grid=False,
                         scale=(100, 100))  
                    tile(pos_x + 100, pos_y, 'sand road',
                         57, grid=False, scale=(100, 100))
                    render_text_on_screen(
                        pos_x + 100, pos_y + 23, 'Back', BLACK, 55)
                    buttons = pygame.mouse.get_pressed()
                    if buttons[0] and not button_trigger:
                        selected_text_entry = 0
                        button_trigger = True
                        present_window = 'choose map'  
                        play_music('menu button')  
                        new_bg = menu_background(top=True, bottom=True)
                        if Animations:
                            car.animate('down', bg)
                            screen_animation(
                                player_screen, choose_map_window, bg, new_bg, car, 'down')
                        else:
                            choose_map_window(new_bg)
                            car.rotate(180)
                            screen_refresh(full_screen=True)
                        selected_text_entry = 0
                    elif button_trigger and not buttons[0]:
                        button_trigger = False
                if Player_amount == 1:
                    
                    if 827 <= mouse_pointer_position[0] <= 852 and 355 <= mouse_pointer_position[1] <= 406 and type(Players[0].controls) == str:
                        if not change_controls_left(Players[0].controls):
                            draw_side_arrow((840, 380), 'left',
                                            border=RED, width=25, height=50)
                        else:
                            draw_side_arrow((840, 380), 'left',
                                            border=GREY, width=25, height=50)
                            buttons = pygame.mouse.get_pressed()
                            if buttons[0] and not button_trigger:
                                button_trigger = True
                                if Players[0].controls != 'test_alpha':
                                    controls.remove(Players[0].controls)
                                Players[0].controls = change_controls_left(
                                    Players[0].controls)
                                if Players[0].controls != 'test_alpha':
                                    controls.append(Players[0].controls)
                            elif button_trigger and not buttons[0]:
                                button_trigger = False
                    
                    elif 1067 <= mouse_pointer_position[0] <= 1107 and 355 <= mouse_pointer_position[1] <= 406 and \
                            type(Players[0].controls) == str:
                        if not change_controls_right(Players[0].controls):
                            draw_side_arrow((1080, 380), 'right',
                                            border=RED, width=25, height=50)
                        else:
                            draw_side_arrow((1080, 380), 'right',
                                            border=GREY, width=25, height=50)
                            buttons = pygame.mouse.get_pressed()
                            if buttons[0] and not button_trigger:
                                button_trigger = True
                                if Players[0].controls != 'test_alpha':
                                    controls.remove(Players[0].controls)
                                Players[0].controls = change_controls_right(
                                    Players[0].controls)
                                if Players[0].controls != 'test_alpha':
                                    controls.append(Players[0].controls)
                            elif button_trigger and not buttons[0]:
                                button_trigger = False
                    
                    elif 754 <= mouse_pointer_position[0] <= 1166 and 764 <= mouse_pointer_position[1] <= 802:
                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger and selected_text_entry != 1:
                            button_trigger = True
                            play_music('text entry')
                            selected_text_entry = 1
                        elif button_trigger and not buttons[0]:
                            button_trigger = False
                    
                    elif 210 <= mouse_pointer_position[0] <= 409 and 112 <= mouse_pointer_position[1] <= 211:
                        pos_x = 210
                        pos_y = 112
                        tile(pos_x, pos_y, 'sand road', 73, grid=False,
                             scale=(100, 100))  
                        tile(pos_x + 100, pos_y, 'sand road',
                             57, grid=False, scale=(100, 100))
                        render_text_on_screen(
                            pos_x + 100, pos_y + 23, 'Back', BLACK, 55)
                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger:
                            selected_text_entry = 0
                            button_trigger = True
                            present_window = 'choose map'  
                            
                            play_music('menu button')
                            new_bg = menu_background(top=True, bottom=True)
                            if Animations:
                                car.animate('down', bg)
                                screen_animation(
                                    player_screen, choose_map_window, bg, new_bg, car, 'down')
                            else:
                                choose_map_window(new_bg)
                                car.rotate(180)
                                screen_refresh(full_screen=True)
                            selected_text_entry = 0
                        elif button_trigger and not buttons[0]:
                            button_trigger = False
                    
                    elif 800 <= mouse_pointer_position[0] <= 1117 and 940 <= mouse_pointer_position[1] <= 1047 and Players[0].name.strip() and \
                            Players[0].controls != 'test_alpha':
                        
                        pos_x = 800
                        pos_y = 940
                        
                        tile(pos_x, pos_y, 'sand road', 73, grid=False)
                        tile(pos_x + 65, pos_y, 'sand road', 88, grid=False)
                        tile(pos_x + 190, pos_y, 'sand road', 57, grid=False)
                        render_text_on_screen(
                            pos_x + 160, pos_y + 20, 'Next', BLACK, 70)
                        buttons = pygame.mouse.get_pressed()  
                        if buttons[0] and not button_trigger:
                            selected_text_entry = 0
                            button_trigger = True
                            present_window = 'choose your vehicle'
                            for player in Players:
                                player.name = player.name.strip()
                            
                            play_music('menu button')
                            new_bg = menu_background(bottom=True, top=True)
                            if Animations:
                                car.animate('up', bg)
                                screen_animation(
                                    player_screen, choose_machine_screen, bg, new_bg, car, 'up')
                            else:
                                choose_machine_screen(new_bg)
                                car.rotate(0)
                                screen_refresh(full_screen=True)
                        elif button_trigger and not buttons[0]:
                            button_trigger = False
                    elif pygame.mouse.get_pressed()[0] and selected_text_entry:
                        selected_text_entry = 0
                elif Player_amount >= 2:
                    
                    if 427 <= mouse_pointer_position[0] <= 452 and 355 <= mouse_pointer_position[1] <= 406 and type(Players[0].controls) == str:
                        if not change_controls_left(Players[0].controls):
                            draw_side_arrow((440, 380), 'left',
                                            border=RED, width=25, height=50)
                        else:
                            draw_side_arrow((440, 380), 'left',
                                            border=GREY, width=25, height=50)
                            buttons = pygame.mouse.get_pressed()
                            if buttons[0] and not button_trigger:
                                button_trigger = True
                                if Players[0].controls != 'test_alpha':
                                    controls.remove(Players[0].controls)
                                Players[0].controls = change_controls_left(
                                    Players[0].controls)
                                if Players[0].controls != 'test_alpha':
                                    controls.append(Players[0].controls)
                            elif button_trigger and not buttons[0]:
                                button_trigger = False
                    
                    elif 667 <= mouse_pointer_position[0] <= 692 and 355 <= mouse_pointer_position[1] <= 406 and \
                            type(Players[0].controls) == str:
                        if not change_controls_right(Players[0].controls):
                            draw_side_arrow((680, 380), 'right',
                                            border=RED, width=25, height=50)
                        else:
                            draw_side_arrow((680, 380), 'right',
                                            border=GREY, width=25, height=50)
                            buttons = pygame.mouse.get_pressed()
                            if buttons[0] and not button_trigger:
                                button_trigger = True
                                if Players[0].controls != 'test_alpha':
                                    controls.remove(Players[0].controls)
                                Players[0].controls = change_controls_right(
                                    Players[0].controls)
                                if Players[0].controls != 'test_alpha':
                                    controls.append(Players[0].controls)
                            elif button_trigger and not buttons[0]:
                                button_trigger = False
                    
                    elif 354 <= mouse_pointer_position[0] <= 766 and 764 <= mouse_pointer_position[1] <= 802:
                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger and selected_text_entry != 1:
                            button_trigger = True
                            play_music('text entry')
                            selected_text_entry = 1
                        elif button_trigger and not buttons[0]:
                            button_trigger = False
                    
                    elif 1227 <= mouse_pointer_position[0] <= 1252 and 355 <= mouse_pointer_position[1] <= 406 and \
                            type(Players[1].controls) == str:
                        if not change_controls_left(Players[1].controls):
                            draw_side_arrow((1240, 380), 'left',
                                            border=RED, width=25, height=50)
                        else:
                            draw_side_arrow((1240, 380), 'left',
                                            border=GREY, width=25, height=50)
                            buttons = pygame.mouse.get_pressed()
                            if buttons[0] and not button_trigger:
                                button_trigger = True
                                if Players[1].controls != 'test_alpha':
                                    controls.remove(Players[1].controls)
                                Players[1].controls = change_controls_left(
                                    Players[1].controls)
                                if Players[1].controls != 'test_alpha':
                                    controls.append(Players[1].controls)
                            elif button_trigger and not buttons[0]:
                                button_trigger = False
                    
                    elif 1467 <= mouse_pointer_position[0] <= 1493 and 355 <= mouse_pointer_position[1] <= 406 and \
                            type(Players[1].controls) == str:
                        if not change_controls_right(Players[1].controls):
                            draw_side_arrow((1480, 380), 'right',
                                            border=RED, width=25, height=50)
                        else:
                            draw_side_arrow((1480, 380), 'right',
                                            border=GREY, width=25, height=50)
                            buttons = pygame.mouse.get_pressed()
                            if buttons[0] and not button_trigger:
                                button_trigger = True
                                if Players[1].controls != 'test_alpha':
                                    controls.remove(Players[1].controls)
                                Players[1].controls = change_controls_right(
                                    Players[1].controls)
                                if Players[1].controls != 'test_alpha':
                                    controls.append(Players[1].controls)
                            elif button_trigger and not buttons[0]:
                                button_trigger = False
                    
                    elif 1154 <= mouse_pointer_position[0] <= 1566 and 764 <= mouse_pointer_position[1] <= 802:
                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger and selected_text_entry != 2:
                            button_trigger = True
                            play_music('text entry')
                            selected_text_entry = 2
                        elif button_trigger and not buttons[0]:
                            button_trigger = False
                    
                    elif 210 <= mouse_pointer_position[0] <= 409 and 112 <= mouse_pointer_position[1] <= 211:
                        pos_x = 210
                        pos_y = 112
                        tile(pos_x, pos_y, 'sand road', 73, grid=False,
                             scale=(100, 100))  
                        tile(pos_x + 100, pos_y, 'sand road',
                             57, grid=False, scale=(100, 100))
                        render_text_on_screen(
                            pos_x + 100, pos_y + 23, 'Back', BLACK, 55)
                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger:
                            selected_text_entry = 0
                            button_trigger = True
                            present_window = 'choose map'  
                            
                            play_music('menu button')
                            new_bg = menu_background(top=True, bottom=True)
                            if Animations:
                                car.animate('down', bg)
                                screen_animation(
                                    player_screen, choose_map_window, bg, new_bg, car, 'down')
                            else:
                                choose_map_window(new_bg)
                                car.rotate(180)
                                screen_refresh(full_screen=True)
                            selected_text_entry = 0
                        elif button_trigger and not buttons[0]:
                            button_trigger = False
                    
                    elif 800 <= mouse_pointer_position[0] <= 1117 and 940 <= mouse_pointer_position[1] <= 1047 and \
                            Players[0].name.strip() and Players[0].controls != 'test_alpha' and \
                            Players[1].name.strip() and Players[1].controls != 'test_alpha':
                        
                        pos_x = 800
                        pos_y = 940
                        
                        tile(pos_x, pos_y, 'sand road', 73, grid=False)
                        tile(pos_x + 65, pos_y, 'sand road', 88, grid=False)
                        tile(pos_x + 190, pos_y, 'sand road', 57, grid=False)
                        render_text_on_screen(
                            pos_x + 160, pos_y + 20, 'Next', BLACK, 70)
                        buttons = pygame.mouse.get_pressed()  
                        if buttons[0] and not button_trigger:
                            selected_text_entry = 0
                            button_trigger = True
                            if Player_amount == 2:
                                present_window = 'choose your vehicle'
                            else:
                                present_window = 'choose players 2'
                            for player in Players:
                                player.name = player.name.strip()
                            
                            play_music('menu button')
                            new_bg = menu_background(bottom=True, top=True)
                            if Animations:
                                car.animate('up', bg)
                                if Player_amount == 2:
                                    screen_animation(player_screen, choose_machine_screen,
                                                     bg, new_bg, car, 'up')
                                else:
                                    screen_animation(player_screen, test1a,
                                                     bg, new_bg, car, 'up')
                            else:
                                if Player_amount == 2:
                                    choose_machine_screen(new_bg)
                                else:
                                    test1a(new_bg)
                                car.rotate(0)
                                screen_refresh(full_screen=True)
                        elif button_trigger and not buttons[0]:
                            button_trigger = False
                    elif pygame.mouse.get_pressed()[0] and selected_text_entry:
                        selected_text_entry = 0
            
            elif present_window == 'choose players 2':
                if prev_window != present_window:  
                    bg = new_bg  
                    test1a(bg)
                    car.draw()
                    screen_refresh(full_screen=True)  
                    prev_window = present_window  
                    selected_text_entry = 0
                test1a(bg)
                mouse_pointer_position = mouse_position()
            
            elif present_window == 'choose your vehicle':
                if prev_window != present_window:  
                    bg = new_bg  
                    choose_machine_screen(bg)  
                    car.move(960, 940)
                    car.draw()
                    screen_refresh(full_screen=True)  
                    prev_window = present_window  
                    selected_text_entry = 0
                choose_machine_screen(bg)
                mouse_pointer_position = mouse_position()
                
                if 528 <= mouse_pointer_position[0] <= 783 and 890 <= mouse_pointer_position[1] <= 997:
                    x = 528
                    y = 890
                    tile(x, y, 'sand road', 73, grid=False)  
                    tile(x + 128, y, 'sand road', 57, grid=False)
                    render_text_on_screen(x + 130, y + 20, 'Back', BLACK, 70)
                    buttons = pygame.mouse.get_pressed()
                    if buttons[0] and not button_trigger:
                        button_trigger = True
                        if Player_amount == 1 or Player_amount == 2:
                            present_window = 'choose players'
                        else:
                            present_window = 'choose players 3'
                        play_music('menu button')  
                        new_bg = menu_background(top=True, bottom=True)
                        if Animations:
                            car.animate('down', bg)
                            if Player_amount == 1 or Player_amount == 2:
                                screen_animation(
                                    choose_machine_screen, player_screen, bg, new_bg, car, 'down')
                            else:
                                screen_animation(
                                    choose_machine_screen, test2a, bg, new_bg, car, 'down')
                        else:
                            if Player_amount == 1 or Player_amount == 2:
                                player_screen(new_bg)
                            else:
                                test2a(new_bg)
                            car.rotate(180)
                            car.move(*CENTRE)
                            screen_refresh(full_screen=True)
                    elif button_trigger and not buttons[0]:
                        button_trigger = False
                
                elif 1100 <= mouse_pointer_position[0] <= 1417 and 890 <= mouse_pointer_position[1] <= 997:
                    x = 1100
                    y = 890
                    tile(x, y, 'sand road', 73, grid=False)  
                    tile(x + 65, y, 'sand road', 88, grid=False)
                    tile(x + 190, y, 'sand road', 57, grid=False)
                    render_text_on_screen(x + 160, y + 20, 'Next', BLACK, 70)
                    buttons = pygame.mouse.get_pressed()  
                    if buttons[0] and not button_trigger:
                        selected_text_entry = 0
                        button_trigger = True
                        if Player_amount <= 2:
                            present_window = 'Finalise Settings'
                            new_bg = menu_background(bottom=True)
                        else:
                            present_window = 'Choose your Machine'
                            new_bg = menu_background(top=True, bottom=True)
                        play_music('menu button')  
                        if Animations:
                            car.animate('up', bg)
                            if Player_amount <= 2:
                                screen_animation(
                                    choose_machine_screen, settings_confirmation, bg, new_bg, car, 'up')
                            else:
                                screen_animation(
                                    choose_machine_screen, settings_confirmation, bg, new_bg, car, 'up')
                        else:
                            if Player_amount <= 2:
                                settings_confirmation(new_bg)
                            else:
                                test1(new_bg)
                            car.rotate(0)
                            car.move(*CENTRE)
                            screen_refresh(full_screen=True)
                    elif button_trigger and not buttons[0]:
                        button_trigger = False
                if Player_amount == 1:
                    
                    if 595 <= mouse_pointer_position[0] <= 635 and 500 <= mouse_pointer_position[1] <= 580:
                        draw_side_arrow(
                            (615, CENTRE[1]), 'left', width=40, height=80, border=GREY)
                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger:
                            button_trigger = True
                            play_music('option down')
                            change_car_left(Players[0])
                        elif not buttons[0] and button_trigger:
                            button_trigger = False
                    
                    elif 1285 <= mouse_pointer_position[0] <= 1325 and 500 <= mouse_pointer_position[1] <= 580:
                        draw_side_arrow(
                            (1305, CENTRE[1]), 'right', width=40, height=80, border=GREY)
                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger:
                            button_trigger = True
                            play_music('option up')
                            change_car_right(Players[0])
                        elif not buttons[0] and button_trigger:
                            button_trigger = False
                    
                    elif 827 <= mouse_pointer_position[0] <= 852 and 710 <= mouse_pointer_position[1] <= 735:
                        draw_side_arrow(
                            (CENTRE[0] - 120, CENTRE[1] + 183), 'left', width=25, height=25, border=GREY)
                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger:
                            button_trigger = True
                            play_music('option down')
                            change_car_color_left(Players[0])
                        elif not buttons[0] and button_trigger:
                            button_trigger = False
                    
                    elif 1067 <= mouse_pointer_position[0] <= 1093 and 710 <= mouse_pointer_position[1] <= 735:
                        draw_side_arrow(
                            (CENTRE[0] + 120, CENTRE[1] + 183), 'right', width=25, height=25, border=GREY)
                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger:
                            button_trigger = True
                            play_music('option up')
                            change_car_color_right(Players[0])
                        elif not buttons[0] and button_trigger:
                            button_trigger = False
                elif Player_amount >= 2:
                    pos_x = CENTRE[0] // 2 + 10
                    
                    if 125 <= mouse_pointer_position[0] <= 165 and 500 <= mouse_pointer_position[1] <= 580:
                        draw_side_arrow(
                            (pos_x - 345, CENTRE[1]), 'left', width=40, height=80, border=GREY)
                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger:
                            button_trigger = True
                            play_music('option down')
                            change_car_left(Players[0])
                        elif not buttons[0] and button_trigger:
                            button_trigger = False
                    
                    elif 815 <= mouse_pointer_position[0] <= 855 and 500 <= mouse_pointer_position[1] <= 580:
                        draw_side_arrow(
                            (pos_x + 345, CENTRE[1]), 'right', width=40, height=80, border=GREY)
                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger:
                            button_trigger = True
                            play_music('option up')
                            change_car_right(Players[0])
                        elif not buttons[0] and button_trigger:
                            button_trigger = False
                    
                    elif 357 <= mouse_pointer_position[0] <= 382 and 710 <= mouse_pointer_position[1] <= 735:
                        draw_side_arrow(
                            (pos_x - 120, CENTRE[1] + 183), 'left', width=25, height=25, border=GREY)
                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger:
                            button_trigger = True
                            play_music('option down')
                            change_car_color_left(Players[0])
                        elif not buttons[0] and button_trigger:
                            button_trigger = False
                    
                    elif 597 <= mouse_pointer_position[0] <= 623 and 710 <= mouse_pointer_position[1] <= 735:
                        draw_side_arrow(
                            (pos_x + 120, CENTRE[1] + 183), 'right', width=25, height=25, border=GREY)
                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger:
                            button_trigger = True
                            play_music('option up')
                            change_car_color_right(Players[0])
                        elif not buttons[0] and button_trigger:
                            button_trigger = False
                    pos_x = CENTRE[0] + CENTRE[0] // 2 - 10
                    
                    if 1065 <= mouse_pointer_position[0] <= 1105 and 500 <= mouse_pointer_position[1] <= 580:
                        draw_side_arrow(
                            (pos_x - 345, CENTRE[1]), 'left', width=40, height=80, border=GREY)
                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger:
                            button_trigger = True
                            play_music('option down')
                            change_car_left(Players[1])
                        elif not buttons[0] and button_trigger:
                            button_trigger = False
                    
                    elif 1755 <= mouse_pointer_position[0] <= 1795 and 500 <= mouse_pointer_position[1] <= 580:
                        draw_side_arrow(
                            (pos_x + 345, CENTRE[1]), 'right', width=40, height=80, border=GREY)
                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger:
                            button_trigger = True
                            play_music('option up')
                            change_car_right(Players[1])
                        elif not buttons[0] and button_trigger:
                            button_trigger = False
                    
                    elif 1297 <= mouse_pointer_position[0] <= 1322 and 710 <= mouse_pointer_position[1] <= 735:
                        draw_side_arrow(
                            (pos_x - 120, CENTRE[1] + 183), 'left', width=25, height=25, border=GREY)
                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger:
                            button_trigger = True
                            play_music('option down')
                            change_car_color_left(Players[1])
                        elif not buttons[0] and button_trigger:
                            button_trigger = False
                    
                    elif 1537 <= mouse_pointer_position[0] <= 1562 and 710 <= mouse_pointer_position[1] <= 735:
                        draw_side_arrow(
                            (pos_x + 120, CENTRE[1] + 183), 'right', width=25, height=25, border=GREY)
                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger:
                            button_trigger = True
                            play_music('option up')
                            change_car_color_right(Players[1])
                        elif not buttons[0] and button_trigger:
                            button_trigger = False
            
            elif present_window == 'Choose your Machine 2':
                if prev_window != present_window:  
                    bg = new_bg  
                    test1(bg)  
                    car.move(960, 940)
                    car.draw()
                    screen_refresh(full_screen=True)  
                    prev_window = present_window  
                test1(bg)
                mouse_pointer_position = mouse_position()
                
                if 528 <= mouse_pointer_position[0] <= 783 and 890 <= mouse_pointer_position[1] <= 997:
                    x = 528
                    y = 890
                    tile(x, y, 'sand road', 73, grid=False)  
                    tile(x + 128, y, 'sand road', 57, grid=False)
                    render_text_on_screen(x + 130, y + 20, 'Back', BLACK, 70)
                    buttons = pygame.mouse.get_pressed()
                    if buttons[0] and not button_trigger:
                        button_trigger = True
                        present_window = 'choose your vehicle'
                        play_music('menu button')  
                        new_bg = menu_background(top=True, bottom=True)
                        if Animations:
                            car.animate('down', bg)
                            screen_animation(
                                test1, choose_machine_screen, bg, new_bg, car, 'down')
                        else:
                            choose_machine_screen(new_bg)
                            car.rotate(180)
                            car.move(*CENTRE)
                            screen_refresh(full_screen=True)
                    elif button_trigger and not buttons[0]:
                        button_trigger = False
                
                elif 1100 <= mouse_pointer_position[0] <= 1417 and 890 <= mouse_pointer_position[1] <= 997:
                    x = 1100
                    y = 890
                    tile(x, y, 'sand road', 73, grid=False)  
                    tile(x + 65, y, 'sand road', 88, grid=False)
                    tile(x + 190, y, 'sand road', 57, grid=False)
                    render_text_on_screen(x + 160, y + 20, 'Next', BLACK, 70)
                    buttons = pygame.mouse.get_pressed()  
                    if buttons[0] and not button_trigger:
                        selected_text_entry = 0
                        button_trigger = True
                        if Player_amount <= 4:
                            present_window = 'Finalise Settings'
                            new_bg = menu_background(bottom=True)
                        else:
                            present_window = 'Choose your Machine'
                            new_bg = menu_background(top=True, bottom=True)
                        play_music('menu button')  
                        if Animations:
                            car.animate('up', bg)
                            if Player_amount <= 4:
                                screen_animation(
                                    test1, settings_confirmation, bg, new_bg, car, 'up')
                            else:
                                screen_animation(
                                    test1, test2, bg, new_bg, car, 'up')
                        else:
                            if Player_amount <= 4:
                                settings_confirmation(new_bg)
                            else:
                                test2(new_bg)
                            car.rotate(0)
                            car.move(*CENTRE)
                            screen_refresh(full_screen=True)
                    elif button_trigger and not buttons[0]:
                        button_trigger = False
                    
                    elif 1285 <= mouse_pointer_position[0] <= 1325 and 500 <= mouse_pointer_position[1] <= 580:
                        draw_side_arrow(
                            (1305, CENTRE[1]), 'right', width=40, height=80, border=GREY)
                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger:
                            button_trigger = True
                            play_music('option up')
                            change_car_right(Players[2])
                        elif not buttons[0] and button_trigger:
                            button_trigger = False
                    
                    elif 827 <= mouse_pointer_position[0] <= 852 and 710 <= mouse_pointer_position[1] <= 735:
                        draw_side_arrow(
                            (CENTRE[0] - 120, CENTRE[1] + 183), 'left', width=25, height=25, border=GREY)
                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger:
                            button_trigger = True
                            play_music('option down')
                            change_car_color_left(Players[2])
                        elif not buttons[0] and button_trigger:
                            button_trigger = False
                    
                    elif 1067 <= mouse_pointer_position[0] <= 1093 and 710 <= mouse_pointer_position[1] <= 735:
                        draw_side_arrow(
                            (CENTRE[0] + 120, CENTRE[1] + 183), 'right', width=25, height=25, border=GREY)
                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger:
                            button_trigger = True
                            play_music('option up')
                            change_car_color_right(Players[2])
                        elif not buttons[0] and button_trigger:
                            button_trigger = False
            
            elif present_window == 'Finalise Settings':
                if prev_window != present_window:  
                    bg = new_bg  
                    settings_confirmation(bg)  
                    car.draw()
                    screen_refresh(full_screen=True)  
                    prev_window = present_window  
                settings_confirmation(bg)
                mouse_pointer_position = mouse_position()
                if Player_amount != 6:
                    
                    if 381 <= mouse_pointer_position[0] <= 407 and 297 <= mouse_pointer_position[1] <= 324:
                        if Enemy_Amount <= 0:
                            draw_side_arrow((390, 311), 'left',
                                            width=25, height=25, border=RED)
                        else:
                            draw_side_arrow((390, 311), 'left',
                                            width=25, height=25, border=GREY)
                            buttons = pygame.mouse.get_pressed()
                            if buttons[0] and not button_trigger:
                                button_trigger = True
                                play_music('option down')
                                Enemy_Amount -= 1
                            elif not buttons[0] and button_trigger:
                                button_trigger = False
                    
                    elif 621 <= mouse_pointer_position[0] <= 647 and 297 <= mouse_pointer_position[1] <= 324:
                        if Enemy_Amount >= 6 - Player_amount:
                            draw_side_arrow((632, 311), 'right',
                                            width=25, height=25, border=RED)
                        else:
                            draw_side_arrow((632, 311), 'right',
                                            width=25, height=25, border=GREY)
                            buttons = pygame.mouse.get_pressed()
                            if buttons[0] and not button_trigger:
                                button_trigger = True
                                play_music('option up')
                                Enemy_Amount += 1
                            elif not buttons[0] and button_trigger:
                                button_trigger = False
                    
                    elif 388 <= mouse_pointer_position[0] <= 413 and 493 <= mouse_pointer_position[1] <= 518:
                        if Enemy_machines - 1 < 0:
                            draw_side_arrow((401, 506), 'left',
                                            width=25, height=25, border=RED)
                        else:
                            draw_side_arrow((401, 506), 'left',
                                            width=25, height=25, border=GREY)
                            buttons = pygame.mouse.get_pressed()
                            if buttons[0] and not button_trigger:
                                button_trigger = True
                                play_music('option down')
                                Enemy_machines -= 1
                            elif not buttons[0] and button_trigger:
                                button_trigger = False
                    
                    elif 608 <= mouse_pointer_position[0] <= 633 and 493 <= mouse_pointer_position[1] <= 518:
                        if Enemy_machines + 1 > 5:
                            draw_side_arrow((621, 506), 'right',
                                            width=25, height=25, border=RED)
                        else:
                            draw_side_arrow((621, 506), 'right',
                                            width=25, height=25, border=GREY)
                            buttons = pygame.mouse.get_pressed()
                            if buttons[0] and not button_trigger:
                                button_trigger = True
                                play_music('option up')
                                Enemy_machines += 1
                            elif not buttons[0] and button_trigger:
                                button_trigger = False
                    
                    elif 388 <= mouse_pointer_position[0] <= 413 and 688 <= mouse_pointer_position[1] <= 713:
                        if not Enemy_machine_color:
                            draw_side_arrow((401, 701), 'left',
                                            width=25, height=25, border=RED)
                        else:
                            draw_side_arrow((401, 701), 'left',
                                            width=25, height=25, border=GREY)
                            buttons = pygame.mouse.get_pressed()
                            if buttons[0] and not button_trigger:
                                button_trigger = True
                                play_music('option down')
                                if Enemy_machine_color == CAR_5:
                                    Enemy_machine_color = CAR_4
                                elif Enemy_machine_color == CAR_4:
                                    Enemy_machine_color = CAR_3
                                elif Enemy_machine_color == CAR_3:
                                    Enemy_machine_color = CAR_2
                                elif Enemy_machine_color == CAR_2:
                                    Enemy_machine_color = CAR_1
                                elif Enemy_machine_color == CAR_1:
                                    Enemy_machine_color = None
                            elif not buttons[0] and button_trigger:
                                button_trigger = False
                    
                    elif 608 <= mouse_pointer_position[0] <= 633 and 688 <= mouse_pointer_position[1] <= 713:
                        if Enemy_machine_color == CAR_5:
                            draw_side_arrow((621, 701), 'right',
                                            width=25, height=25, border=RED)
                        else:
                            draw_side_arrow((621, 701), 'right',
                                            width=25, height=25, border=GREY)
                            buttons = pygame.mouse.get_pressed()
                            if buttons[0] and not button_trigger:
                                button_trigger = True
                                play_music('option up')
                                if not Enemy_machine_color:
                                    Enemy_machine_color = CAR_1
                                elif Enemy_machine_color == CAR_1:
                                    Enemy_machine_color = CAR_2
                                elif Enemy_machine_color == CAR_2:
                                    Enemy_machine_color = CAR_3
                                elif Enemy_machine_color == CAR_3:
                                    Enemy_machine_color = CAR_4
                                elif Enemy_machine_color == CAR_4:
                                    Enemy_machine_color = CAR_5
                            elif not buttons[0] and button_trigger:
                                button_trigger = False
                    
                    elif 1335 <= mouse_pointer_position[0] <= 1360 and 297 <= mouse_pointer_position[1] <= 324:
                        if Total_laps <= 1:
                            draw_side_arrow((1348, 311), 'left',
                                            width=25, height=25, border=RED)
                        else:
                            draw_side_arrow((1348, 311), 'left',
                                            width=25, height=25, border=GREY)
                            buttons = pygame.mouse.get_pressed()
                            if buttons[0] and not button_trigger:
                                button_trigger = True
                                play_music('option down')
                                Total_laps -= 1
                            elif not buttons[0] and button_trigger:
                                button_trigger = False
                    
                    elif 1455 <= mouse_pointer_position[0] <= 1481 and 297 <= mouse_pointer_position[1] <= 324:
                        if Total_laps >= 10:
                            draw_side_arrow((1468, 311), 'right',
                                            width=25, height=25, border=RED)
                        else:
                            draw_side_arrow((1468, 311), 'right',
                                            width=25, height=25, border=GREY)
                            buttons = pygame.mouse.get_pressed()
                            if buttons[0] and not button_trigger:
                                button_trigger = True
                                play_music('option up')
                                Total_laps += 1
                            elif not buttons[0] and button_trigger:
                                button_trigger = False
                    
                    elif 847 <= mouse_pointer_position[0] <= 872 and 298 <= mouse_pointer_position[1] <= 324:
                        draw_side_arrow((860, 311), 'left',
                                        width=25, height=25, border=GREY)
                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger:
                            button_trigger = True
                            play_music('option down')
                            if powerups:
                                powerups = False
                            else:
                                powerups = True
                        elif not buttons[0] and button_trigger:
                            button_trigger = False
                    
                    elif 1047 <= mouse_pointer_position[0] <= 1072 and 298 <= mouse_pointer_position[1] <= 323:
                        draw_side_arrow((1060, 311), 'right',
                                        width=25, height=25, border=GREY)
                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger:
                            button_trigger = True
                            play_music('option up')
                            if powerups:
                                powerups = False
                            else:
                                powerups = True
                        elif not buttons[0] and button_trigger:
                            button_trigger = False
                    
                    elif 1305 <= mouse_pointer_position[0] <= 1330 and 493 <= mouse_pointer_position[1] <= 518:
                        if Player_amount == 2:
                            if Players[0].start_pos - 1 < 1 or Players[0].start_pos - 2 < 1 and \
                                    Players[0].start_pos - 1 == Players[1].start_pos and Player_amount == 2:
                                draw_side_arrow(
                                    (1318, 506), 'left', width=25, height=25, border=RED)
                            else:
                                draw_side_arrow(
                                    (1318, 506), 'left', width=25, height=25, border=GREY)
                                buttons = pygame.mouse.get_pressed()
                                if buttons[0] and not button_trigger:
                                    button_trigger = True
                                    play_music('option down')
                                    if Players[0].start_pos - 1 == Players[1].start_pos and Player_amount == 2:
                                        Players[0].start_pos -= 2
                                    else:
                                        Players[0].start_pos -= 1
                                elif not buttons[0] and button_trigger:
                                    button_trigger = False
                        else:
                            if Players[0].start_pos - 1 < 1:
                                draw_side_arrow(
                                    (1318, 506), 'left', width=25, height=25, border=RED)
                            else:
                                draw_side_arrow(
                                    (1318, 506), 'left', width=25, height=25, border=GREY)
                                buttons = pygame.mouse.get_pressed()
                                if buttons[0] and not button_trigger:
                                    button_trigger = True
                                    play_music('option down')
                                    Players[0].start_pos -= 1
                                elif not buttons[0] and button_trigger:
                                    button_trigger = False
                    
                    elif 1485 <= mouse_pointer_position[0] <= 1510 and 493 <= mouse_pointer_position[1] <= 518:
                        if Player_amount == 2:
                            if Players[0].start_pos + 1 > 6 or Players[0].start_pos + 1 == Players[1].start_pos and \
                                    Players[0].start_pos + 2 > 6 and Player_amount == 2:
                                draw_side_arrow(
                                    (1498, 506), 'right', width=25, height=25, border=RED)
                            else:
                                draw_side_arrow(
                                    (1498, 506), 'right', width=25, height=25, border=GREY)
                                buttons = pygame.mouse.get_pressed()
                                if buttons[0] and not button_trigger:
                                    button_trigger = True
                                    play_music('option down')
                                    if Players[0].start_pos + 1 == Players[1].start_pos:
                                        Players[0].start_pos += 2
                                    else:
                                        Players[0].start_pos += 1
                                elif not buttons[0] and button_trigger:
                                    button_trigger = False
                        else:
                            if Players[0].start_pos + 1 > 6:
                                draw_side_arrow(
                                    (1498, 506), 'right', width=25, height=25, border=RED)
                            else:
                                draw_side_arrow(
                                    (1498, 506), 'right', width=25, height=25, border=GREY)
                                buttons = pygame.mouse.get_pressed()
                                if buttons[0] and not button_trigger:
                                    button_trigger = True
                                    play_music('option down')
                                    Players[0].start_pos += 1
                                elif not buttons[0] and button_trigger:
                                    button_trigger = False
                    
                    elif 1305 <= mouse_pointer_position[0] <= 1330 and 688 <= mouse_pointer_position[1] <= 713 and Player_amount >= 2:
                        if Players[1].start_pos - 1 < 1 or Players[1].start_pos - 2 < 1 and \
                                Players[1].start_pos - 1 == Players[0].start_pos:
                            draw_side_arrow((1318, 701), 'left',
                                            width=25, height=25, border=RED)
                        else:
                            draw_side_arrow((1318, 701), 'left',
                                            width=25, height=25, border=GREY)
                            buttons = pygame.mouse.get_pressed()
                            if buttons[0] and not button_trigger:
                                button_trigger = True
                                play_music('option down')
                                if Players[1].start_pos - 1 == Players[0].start_pos:
                                    Players[1].start_pos -= 2
                                else:
                                    Players[1].start_pos -= 1
                            elif not buttons[0] and button_trigger:
                                button_trigger = False
                    
                    elif 1485 <= mouse_pointer_position[0] <= 1510 and 688 <= mouse_pointer_position[1] <= 713 and Player_amount >= 2:
                        if Players[1].start_pos + 1 > 6 or Players[1].start_pos + 1 == Players[0].start_pos and \
                                Players[1].start_pos + 2 > 6:
                            draw_side_arrow((1498, 701), 'right',
                                            width=25, height=25, border=RED)
                        else:
                            draw_side_arrow((1498, 701), 'right',
                                            width=25, height=25, border=GREY)
                            buttons = pygame.mouse.get_pressed()
                            if buttons[0] and not button_trigger:
                                button_trigger = True
                                play_music('option down')
                                if Players[1].start_pos + 1 == Players[0].start_pos:
                                    Players[1].start_pos += 2
                                else:
                                    Players[1].start_pos += 1
                            elif not buttons[0] and button_trigger:
                                button_trigger = False
                else:
                    
                    if 887 <= mouse_pointer_position[0] <= 912 and 298 <= mouse_pointer_position[1] <= 323:
                        if Total_laps <= 1:
                            draw_side_arrow((900, 311), 'left',
                                            width=25, height=25, border=RED)
                        else:
                            draw_side_arrow((900, 311), 'left',
                                            width=25, height=25, border=GREY)
                            buttons = pygame.mouse.get_pressed()
                            if buttons[0] and not button_trigger:
                                button_trigger = True
                                play_music('option down')
                                Total_laps -= 1
                            elif not buttons[0] and button_trigger:
                                button_trigger = False
                    
                    elif 1007 <= mouse_pointer_position[0] <= 1032 and 298 <= mouse_pointer_position[1] <= 323:
                        if Total_laps >= 10:
                            draw_side_arrow((1020, 311), 'right',
                                            width=25, height=25, border=RED)
                        else:
                            draw_side_arrow((1020, 311), 'right',
                                            width=25, height=25, border=GREY)
                            buttons = pygame.mouse.get_pressed()
                            if buttons[0] and not button_trigger:
                                button_trigger = True
                                play_music('option up')
                                Total_laps += 1
                            elif not buttons[0] and button_trigger:
                                button_trigger = False
                    
                    elif 847 <= mouse_pointer_position[0] <= 872 and 688 <= mouse_pointer_position[1] <= 713:
                        draw_side_arrow((860, 701), 'left',
                                        width=25, height=25, border=GREY)
                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger:
                            button_trigger = True
                            play_music('option down')
                            if powerups:
                                powerups = False
                            else:
                                powerups = True
                        elif not buttons[0] and button_trigger:
                            button_trigger = False
                    
                    elif 1047 <= mouse_pointer_position[0] <= 1072 and 688 <= mouse_pointer_position[1] <= 713:
                        draw_side_arrow((1060, 701), 'right',
                                        width=25, height=25, border=GREY)
                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger:
                            button_trigger = True
                            play_music('option up')
                            if powerups:
                                powerups = False
                            else:
                                powerups = True
                        elif not buttons[0] and button_trigger:
                            button_trigger = False
                
                if 210 <= mouse_pointer_position[0] <= 409 and 112 <= mouse_pointer_position[1] <= 211:
                    pos_x = 210
                    pos_y = 112
                    tile(pos_x, pos_y, 'sand road', 73, grid=False,
                         scale=(100, 100))  
                    tile(pos_x + 100, pos_y, 'sand road',
                         57, grid=False, scale=(100, 100))
                    render_text_on_screen(
                        pos_x + 100, pos_y + 23, 'Back', BLACK, 55)
                    buttons = pygame.mouse.get_pressed()
                    if buttons[0] and not button_trigger:
                        button_trigger = True
                        if Player_amount == 1 or Player_amount == 2:
                            present_window = 'Choose your Machine'
                        elif Player_amount == 3 or Player_amount == 4:
                            present_window = 'Choose your Machine'
                        else:
                            present_window = 'Choose your Machine'
                        play_music('menu button')  
                        new_bg = menu_background(top=True, bottom=True)
                        if Animations:
                            car.animate('down', bg)
                            if Player_amount == 1 or Player_amount == 2:
                                screen_animation(
                                    settings_confirmation, choose_machine_screen, bg, new_bg, car, 'down')
                            elif Player_amount == 3 or Player_amount == 4:
                                screen_animation(
                                    settings_confirmation, choose_machine_screen, bg, new_bg, car, 'down')
                            else:
                                screen_animation(
                                    settings_confirmation, choose_machine_screen, bg, new_bg, car, 'down')
                        else:
                            if Player_amount == 1 or Player_amount == 2:
                                choose_machine_screen(new_bg)
                            elif Player_amount == 3 or Player_amount == 4:
                                test1(new_bg)
                            else:
                                test2(new_bg)
                            car.rotate(180)
                            screen_refresh(full_screen=True)
                    elif button_trigger and not buttons[0]:
                        button_trigger = False
                
                
                elif 800 <= mouse_pointer_position[0] <= 1118 and 850 <= mouse_pointer_position[1] <= 958:
                    pos_x = 800
                    pos_y = 850
                    
                    tile(pos_x, pos_y, 'sand road', 73, grid=False)
                    tile(pos_x + 65, pos_y, 'sand road', 88, grid=False)
                    tile(pos_x + 190, pos_y, 'sand road', 57, grid=False)
                    render_text_on_screen(
                        pos_x + 160, pos_y + 20, 'Start', BLACK, 70)
                    buttons = pygame.mouse.get_pressed()  
                    
                    if buttons[0] and not button_trigger:
                        button_trigger = True
                        play_music('start button')  
                        pygame.mixer.music.fadeout(250)
                        menu_loop = False
                    elif button_trigger and not buttons[0]:
                        button_trigger = False
            
            elif present_window == 'confirm quit':
                if prev_window != present_window:  
                    bg = new_bg  
                    quit_confirmation(bg)  
                    car.draw()
                    if prev_window == 'leaderboard':
                        black_initialisation()
                        leaderboard = True
                    else:
                        leaderboard = False
                    screen_refresh(full_screen=True)  
                    prev_window = present_window  
                quit_confirmation(bg)  
                mouse_pointer_position = mouse_position()  
                
                if 347 <= mouse_pointer_position[0] <= 642 and 486 <= mouse_pointer_position[1] <= 593:
                    pos_x = 347
                    pos_y = CENTRE[1] - (tile_scale[1] // 2)
                    tile(pos_x, pos_y, 'sand road',
                         73, grid=False)  
                    tile(pos_x + 85, pos_y, 'sand road', 88, grid=False)
                    tile(pos_x + 168, pos_y, 'sand road', 57, grid=False)
                    render_text_on_screen(
                        pos_x + 153, pos_y + 20, 'Yes', BLACK, 70)
                    buttons = pygame.mouse.get_pressed()
                    if buttons[0] and not button_trigger:
                        button_trigger = True
                        play_music('menu button')  
                        pygame.mixer.fadeout(50)
                        pygame.mixer.music.fadeout(500)
                        if music_thread.is_alive():
                            music_thread_event.set()
                            music_thread.join(timeout=0.25)
                        sleep(0.5)
                        pygame.quit()
                        quit()
                    elif not buttons[0] and button_trigger:
                        button_trigger = False
                
                elif 1307 <= mouse_pointer_position[0] <= 1602 and 486 <= mouse_pointer_position[1] <= 593:
                    pos_x = CENTRE[0] + 347
                    pos_y = CENTRE[1] - (tile_scale[1] // 2)
                    tile(pos_x, pos_y, 'sand road',
                         73, grid=False)  
                    tile(pos_x + 85, pos_y, 'sand road', 88, grid=False)
                    tile(pos_x + 168, pos_y, 'sand road', 57, grid=False)
                    render_text_on_screen(
                        pos_x + 153, pos_y + 20, 'No', BLACK, 70)
                    buttons = pygame.mouse.get_pressed()
                    if buttons[0] and not button_trigger:
                        button_trigger = True
                        play_music('menu button')  
                        if leaderboard:
                            present_window = 'leaderboard'
                            black_conclusion()
                        else:
                            present_window = 'main menu'
                            new_bg = menu_background(
                                top=True, right=True, bottom=True, left=True)
                            if Animations:
                                car.animate('up', bg)
                                screen_animation(
                                    quit_confirmation, main_menu_page, bg, new_bg, car, 'up')
                            else:
                                main_menu_page(new_bg)
                                car.rotate(0)
                                screen_refresh(full_screen=True)
                    elif not buttons[0] and button_trigger:
                        button_trigger = False
            
            elif present_window == 'credits':
                if prev_window != present_window:  
                    bg = new_bg  
                    dev_credits(bg)  
                    car.draw()
                    screen_refresh(full_screen=True)  
                    prev_window = present_window  
                dev_credits(bg)  
                mouse_pointer_position = mouse_position()  
                
                if 800 <= mouse_pointer_position[0] <= 1117 and 940 <= mouse_pointer_position[1] <= 1047:
                    pos_x = 800
                    pos_y = 940
                    tile(pos_x, pos_y, 'sand road', 73, grid=False)
                    tile(pos_x + 65, pos_y, 'sand road', 88, grid=False)
                    tile(pos_x + 190, pos_y, 'sand road', 57, grid=False)
                    render_text_on_screen(
                        pos_x + 160, pos_y + 20, 'Back', BLACK, 70)
                    buttons = pygame.mouse.get_pressed()
                    if buttons[0] and not button_trigger:
                        button_trigger = True
                        present_window = 'main menu'
                        play_music('menu button')  
                        new_bg = menu_background(
                            top=True, right=True, bottom=True, left=True)
                        if Animations:
                            car.animate('right', bg)
                            screen_animation(
                                dev_credits, main_menu_page, bg, new_bg, car, 'right')
                        else:
                            main_menu_page(new_bg)
                            car.rotate(270)
                            screen_refresh(full_screen=True)
                    elif not buttons[0] and button_trigger:
                        button_trigger = False
            
            elif present_window == 'tutorial':
                if prev_window != present_window:  
                    bg = new_bg  
                    hints_screen(bg)  
                    black_initialisation()
                    screen_refresh(full_screen=True)
                    prev_window = present_window  
                hints_screen(bg)  
                mouse_pointer_position = mouse_position()  
                
                if 800 <= mouse_pointer_position[0] <= 1117 and 940 <= mouse_pointer_position[1] <= 1047:
                    pos_x = 800
                    pos_y = 940
                    tile(pos_x, pos_y, 'sand road', 73, grid=False)
                    tile(pos_x + 65, pos_y, 'sand road', 88, grid=False)
                    tile(pos_x + 190, pos_y, 'sand road', 57, grid=False)
                    render_text_on_screen(
                        pos_x + 160, pos_y + 20, 'Back', BLACK, 70)
                    buttons = pygame.mouse.get_pressed()
                    if buttons[0] and not button_trigger:
                        button_trigger = True
                        present_window = 'main menu'
                        play_music('menu button')  
                        new_bg = menu_background(
                            top=True, right=True, bottom=True, left=True)
                        black_conclusion()
                    elif not buttons[0] and button_trigger:
                        button_trigger = False
            
            elif present_window == 'settings':
                if prev_window != present_window:  
                    bg = new_bg  
                    basic_settings(bg)  
                    car.draw()
                    screen_refresh(full_screen=True)  
                    prev_window = present_window  
                basic_settings(bg)  
                mouse_pointer_position = mouse_position()  
                
                if 396 <= mouse_pointer_position[0] <= 421 and 298 <= mouse_pointer_position[1] <= 324:
                    draw_side_arrow((409, 311), 'left',
                                    width=25, height=25, border=GREY)
                    buttons = pygame.mouse.get_pressed()
                    if buttons[0] and not button_trigger and device_screen_resolution <= device_information[Screen]:
                        button_trigger = True
                        play_music('option down')
                        resolution_decrease()
                    elif not buttons[0] and button_trigger:
                        button_trigger = False
                
                elif 606 <= mouse_pointer_position[0] <= 631 and 298 <= mouse_pointer_position[1] <= 324:
                    draw_side_arrow((619, 311), 'right',
                                    width=25, height=25, border=GREY)
                    buttons = pygame.mouse.get_pressed()
                    if buttons[0] and not button_trigger and device_screen_resolution <= device_information[Screen]:
                        button_trigger = True
                        play_music('option up')
                        resolution_increase()
                    elif not buttons[0] and button_trigger:
                        button_trigger = False
                
                elif 1290 <= mouse_pointer_position[0] <= 1315 and 298 <= mouse_pointer_position[1] <= 324:
                    draw_side_arrow((1303, 311), 'left',
                                    width=25, height=25, border=GREY)
                    buttons = pygame.mouse.get_pressed()
                    if buttons[0] and not button_trigger:
                        button_trigger = True
                        play_music('option down')
                        if Animations:
                            Animations = False
                        else:
                            Animations = True
                    elif not buttons[0] and button_trigger:
                        button_trigger = False
                
                elif 1500 <= mouse_pointer_position[0] <= 1526 and 298 <= mouse_pointer_position[1] <= 324:
                    draw_side_arrow((1513, 311), 'right',
                                    width=25, height=25, border=GREY)
                    buttons = pygame.mouse.get_pressed()
                    if buttons[0] and not button_trigger:
                        button_trigger = True
                        play_music('option up')
                        if Animations:
                            Animations = False
                        else:
                            Animations = True
                    elif not buttons[0] and button_trigger:
                        button_trigger = False
                
                elif 1270 <= mouse_pointer_position[0] <= 1296 and 649 <= mouse_pointer_position[1] <= 675:
                    draw_side_arrow((1283, 662), 'left',
                                    width=25, height=25, border=GREY)
                    buttons = pygame.mouse.get_pressed()
                    if buttons[0] and not button_trigger:
                        button_trigger = True
                        if Mute_volume:
                            Mute_volume = False
                            music_thread_event.clear()
                            music_thread = Thread(
                                name='music_thread', target=menu_loop_music)
                            pygame.mixer.music.unpause()
                            music_thread.start()
                        else:
                            Mute_volume = True
                            if music_thread.is_alive():
                                music_thread_event.set()
                                music_thread.join()
                                pygame.mixer.music.pause()
                        loaded_sounds = []
                        play_music('option down')
                    elif not buttons[0] and button_trigger:
                        button_trigger = False
                
                elif 1520 <= mouse_pointer_position[0] <= 1546 and 649 <= mouse_pointer_position[1] <= 675:
                    draw_side_arrow((1533, 662), 'right',
                                    width=25, height=25, border=GREY)
                    buttons = pygame.mouse.get_pressed()
                    if buttons[0] and not button_trigger:
                        button_trigger = True
                        if Mute_volume:
                            Mute_volume = False
                            music_thread_event.clear()
                            music_thread = Thread(
                                name='music_thread', target=menu_loop_music)
                            pygame.mixer.music.unpause()
                            music_thread.start()
                        else:
                            Mute_volume = True
                            if music_thread.is_alive():
                                music_thread_event.set()
                                music_thread.join()
                                pygame.mixer.music.pause()
                        loaded_sounds = []
                        play_music('option up')
                    elif not buttons[0] and button_trigger:
                        button_trigger = False
                
                elif 822 <= mouse_pointer_position[0] <= 847 and 649 <= mouse_pointer_position[1] <= 675:
                    if Music_volume <= 0:
                        draw_side_arrow((835, 662), 'left',
                                        width=25, height=25, border=RED)
                    else:
                        draw_side_arrow((835, 662), 'left',
                                        width=25, height=25, border=GREY)
                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger:
                            button_trigger = True
                            if Music_volume - 0.01 <= 0:
                                Music_volume = 0
                                pygame.mixer.music.pause()
                            elif Music_volume - 0.01 > 0:
                                Music_volume = round(Music_volume - 0.01, 4)
                            play_music('option down')
                            pygame.mixer.music.set_volume(Music_volume)
                        elif not buttons[0] and button_trigger:
                            button_trigger = False
                
                elif 1072 <= mouse_pointer_position[0] <= 1097 and 649 <= mouse_pointer_position[1] <= 675:
                    if Music_volume >= 1:
                        draw_side_arrow((1085, 662), 'right',
                                        width=25, height=25, border=RED)
                    else:
                        draw_side_arrow((1085, 662), 'right',
                                        width=25, height=25, border=GREY)
                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger:
                            button_trigger = True
                            if Music_volume + 0.01 >= 1:
                                Music_volume = 1
                            elif Music_volume + 0.01 < 1:
                                Music_volume = round(Music_volume + 0.01, 4)
                            if not pygame.mixer.music.get_busy() and not Mute_volume:
                                pygame.mixer.music.unpause()
                            play_music('option up')
                            pygame.mixer.music.set_volume(Music_volume)
                        elif not buttons[0] and button_trigger:
                            button_trigger = False
                
                elif 391 <= mouse_pointer_position[0] <= 416 and 649 <= mouse_pointer_position[1] <= 675:
                    if Sfx_volume <= 0:
                        draw_side_arrow((404, 662), 'left',
                                        width=25, height=25, border=RED)
                    else:
                        draw_side_arrow((404, 662), 'left',
                                        width=25, height=25, border=GREY)
                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger:
                            button_trigger = True
                            if Sfx_volume - 0.01 <= 0:
                                Sfx_volume = 0
                            elif Sfx_volume - 0.01 > 0:
                                Sfx_volume = round(Sfx_volume - 0.01, 4)
                            loaded_sounds = []  
                            play_music('option down')
                        elif not buttons[0] and button_trigger:
                            button_trigger = False
                
                elif 611 <= mouse_pointer_position[0] <= 636 and 649 <= mouse_pointer_position[1] <= 675:
                    if Sfx_volume >= 1:
                        draw_side_arrow((624, 662), 'right',
                                        width=25, height=25, border=RED)
                    else:
                        draw_side_arrow((624, 662), 'right',
                                        width=25, height=25, border=GREY)
                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger:
                            button_trigger = True
                            if Sfx_volume + 0.01 >= 1:
                                Sfx_volume = 1
                            elif Sfx_volume + 0.01 < 1:
                                Sfx_volume = round(Sfx_volume + 0.01, 4)
                            loaded_sounds = []  
                            play_music('option up')
                        elif not buttons[0] and button_trigger:
                            button_trigger = False
                
                elif 800 <= mouse_pointer_position[0] <= 1117 and 940 <= mouse_pointer_position[1] <= 1047:
                    pos_x = 800
                    pos_y = 940
                    tile(pos_x, pos_y, 'sand road', 73, grid=False)
                    tile(pos_x + 65, pos_y, 'sand road', 88, grid=False)
                    tile(pos_x + 190, pos_y, 'sand road', 57, grid=False)
                    render_text_on_screen(
                        pos_x + 160, pos_y + 20, 'Back', BLACK, 70)
                    buttons = pygame.mouse.get_pressed()
                    if buttons[0] and not button_trigger:
                        button_trigger = True
                        saved_timer = None
                        present_window = 'main menu'
                        play_music('menu button')  
                        new_bg = menu_background(
                            top=True, right=True, bottom=True, left=True)
                        if Animations:
                            car.animate('left', bg)
                            screen_animation(
                                basic_settings, main_menu_page, bg, new_bg, car, 'left')
                        else:
                            main_menu_page(new_bg)
                            car.rotate(90)
                            screen_refresh(full_screen=True)
                    elif not buttons[0] and button_trigger:
                        button_trigger = False
            
            elif present_window == 'leaderboard':
                if prev_window != present_window:  
                    bg = new_bg  
                    ranking_screen(bg)  
                    if Window.get_alpha() or Window.get_alpha() == 0:
                        black_initialisation()
                    else:
                        screen_refresh(full_screen=True)  
                    prev_window = present_window  
                ranking_screen(bg)  
                mouse_pointer_position = mouse_position()  
                
                if 800 <= mouse_pointer_position[0] <= 1117 and 764 <= mouse_pointer_position[1] <= 871:
                    x = 800
                    y = 764
                    tile(x, y, 'sand road', 73, grid=False)  
                    tile(x + 65, y, 'sand road', 88, grid=False)
                    tile(x + 190, y, 'sand road', 57, grid=False)
                    render_text_on_screen(x + 160, y + 20, 'Finish', BLACK, 70)
                    buttons = pygame.mouse.get_pressed()
                    if buttons[0] and not button_trigger:
                        button_trigger = True
                        present_window = 'main menu'
                        play_music('menu button')  
                        new_bg = menu_background(
                            top=True, right=True, bottom=True, left=True)
                        pygame.mixer.music.fadeout(250)
                        black_conclusion()
                        main_menu_page(new_bg)
                    elif not buttons[0] and button_trigger:
                        button_trigger = False
            else:
                raise ValueError('present_window == ' + str(present_window))
            if present_window != 'leaderboard' and present_window != 'tutorial':
                car.draw()
            if present_window == 'choose map':
                screen_refresh(full_screen=True)
            else:
                screen_refresh()
        if music_thread.is_alive():
            music_thread_event.set()
            music_thread.join()
        black_conclusion(show_loading=True)  
        if Animations:
            loading_thread_event.clear()
            loading_thread = Thread(name='loading_thread', target=render_animation, args=(
                CENTRE[0], CENTRE[1] + 300))
            loading_thread.start()  
        game_quit = gameplay()  
        pygame.time.wait(1000)
        if Animations:
            loading_thread_event.set()  
            if loading_thread.is_alive():
                
                loading_thread.join()
        if game_quit:
            new_bg = menu_background(
                top=True, right=True, bottom=True, left=True)
            main_menu_page(new_bg)
            present_window = 'main menu'
        else:
            new_bg = menu_background()
            ranking_screen(new_bg)
            present_window = 'leaderboard'
        car.rotate(0)
        car.move(*CENTRE)
        black_initialisation(show_loading=True)
        if not pygame.mouse.get_visible():
            pygame.mouse.set_visible(True)
        menu_loop = True
        music_thread_event.clear()

if __name__ == '__main__':
    if Debug or Race_debug:  
        try:
            main()
        except KeyboardInterrupt:
            print('KeyboardInterrupt raised, Goodbye!')
            pygame.quit()
        quit()
    else:
        try:
            main()
        except KeyboardInterrupt:
            Music_loop = False
            if music_thread.is_alive():
                music_thread.join()
            if loading_thread.is_alive():
                loading_thread_event.set()
                loading_thread.join()
            print('KeyboardInterrupt raised, Goodbye!')
            pygame.quit()
            quit()    
        except Exception as error:  
            print(error)
            Music_loop = False
            if music_thread.is_alive():
                music_thread.join()
            if loading_thread.is_alive():
                loading_thread_event.set()
                loading_thread.join()
            pygame.mixer.music.stop()
            pygame.mixer.stop()
            pygame.time.wait(100)
            Display.fill(BLACK)
            play_music('error')
            error_type = str(type(error)).replace(
                "<class '", '').replace("'>", '')
            try:
                Display.blit(pygame.font.Font(fonts.load(), 50).render(
                    error_type, True, WHITE, 50), (0, 0))
                Display.blit(pygame.font.Font(fonts.load(), 50).render(
                    str(error), True, WHITE, 50), (0, 50))
            except FileNotFoundError:
                Display.blit(pygame.font.Font(None, 50).render(
                    error_type, True, WHITE, 50), (0, 0))
                Display.blit(pygame.font.Font(None, 50).render(
                    str(error), True, WHITE, 50), (0, 50))
            pygame.display.update()
            pygame.time.wait(3000)
        finally:
            Music_loop = False
            if music_thread.is_alive():
                music_thread.join()
            if loading_thread.is_alive():
                loading_thread_event.set()
                loading_thread.join()
            pygame.quit()
            quit()    
    pygame.quit()
    quit()
elif __name__ == 'main':
    device_screen_resolution = 1280, 720
    Display = pygame.display.set_mode(device_screen_resolution)
    Music_volume = 0.02
    Sfx_volume = 0.02
    try:
        Window.blit(pygame.font.Font(fonts.load(type1=True), 100).render(
            'Road Fighter', True, WHITE), (CENTRE[0] - 412, CENTRE[1] - 60))
        Window.blit(pygame.font.Font(fonts.load(), 100).render(
            'Testing mode', True, WHITE), (CENTRE[0] - 346, CENTRE[1] + 60))
    except FileNotFoundError:
        Window.blit(pygame.font.Font(None, 100).render('Road Fighter', True, ORANGE),
                    (CENTRE[0] - 256, CENTRE[1] - 60))
        Window.blit(pygame.font.Font(None, 100).render('Testing mode', True, WHITE),
                    (CENTRE[0] - 224, CENTRE[1] + 60))
    Display.blit(pygame.transform.scale(
        Window, device_screen_resolution), (0, 0))
    pygame.display.update()
    
