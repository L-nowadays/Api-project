import pygame
from support import request
import sys

# Const
map_api_server = "http://static-maps.yandex.ru/1.x/"
geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"
max_map_size = 17
min_map_size = 0
# Offset for each map size
offsets = [30, 30, 20, 15, 10, 3, 2, 1, 1, 0.5, 0.2, 0.1, 0.08, 0.008, 0.006, 0.0005, 0.0003, 0.0002]
max_latitude = 180
min_latitude = -180
min_longitude = -89
max_longitude = 89

# Keys used to move or resize map
control_keys = (pygame.K_PAGEUP, pygame.K_PAGEDOWN, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN)

# Start values
running = True
map_size = 0
longitude = 0
latitude = 0


# Function for generating new map file.
def create_new_map():
    # Params for static-maps request
    formated_pos = '{},{}'.format(str(latitude), str(longitude))
    map_params = {"ll": formated_pos, "z": str(map_size), "l": "map"}
    # Static-maps request
    response = request(map_api_server, params=map_params)
    # Create temporary image file
    map_file = "map.png"
    try:
        with open(map_file, "wb") as file:
            file.write(response.content)
    except IOError as ex:
        print("Ошибка записи временного файла:", ex)
        sys.exit(2)


# Function for drawing map file on screen
def draw_map():
    screen.fill((255, 255, 255))
    screen.blit(map_image, (0, 0))
    pygame.display.flip()


# Pygame setup
pygame.init()
screen = pygame.display.set_mode((600, 450))
timer = pygame.time.Clock()
# Create first map
create_new_map()
map_image = pygame.image.load('map.png')
# Draw map
draw_map()

# Main loop
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # Move or resize events catcher
        if event.type == pygame.KEYDOWN and event.key in control_keys:
            if event.key == pygame.K_PAGEDOWN and map_size - 1 >= min_map_size:
                map_size -= 1
            if event.key == pygame.K_PAGEUP and map_size + 1 <= max_map_size:
                map_size += 1
            if event.key in control_keys[2:]:
                offset = offsets[map_size]
                if event.key == pygame.K_LEFT:
                    latitude -= offset
                if event.key == pygame.K_RIGHT:
                    latitude += offset
                if event.key == pygame.K_UP:
                    longitude += offset
                if event.key == pygame.K_DOWN:
                    longitude -= offset
                # Handle outside values for latitude and longitude
                if latitude < min_latitude:
                    latitude = max_latitude - offset
                elif latitude > max_latitude:
                    latitude = min_latitude + offset
                if longitude < min_longitude:
                    longitude = max_longitude - offset
                elif longitude > max_longitude:
                    longitude = min_longitude + offset
            print(longitude, latitude)
            # Each move action requires new map
            # Create and load new map
            create_new_map()
            map_image = pygame.image.load('map.png')
            # Draw new map
            draw_map()
    timer.tick(60)
pygame.quit()
