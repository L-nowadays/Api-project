import pygame
from support import request
import sys

# Const
map_api_server = "http://static-maps.yandex.ru/1.x/"
geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"
max_map_size = 17
min_map_size = 0
# Offset for each map size
offsets = [[0, 0], [0, 0], [211, 82.9], [105.4, 62], [52.5, 37], [26.4, 19.65], [13.2, 9.65], [6.6, 4.865],
           [3.3, 2.464], [1.65, 1.232], [0.825, 0.6165], [0.4125, 0.30825], [0.20625, 0.1542], [0.103125, 0.07521],
           [0.0515625, 0.037605], [0.02578125, 0.0185], [0.012890625, 0.00940125], [0.0064453125, 0.004700625]]
max_latitude = 180
min_latitude = -180
min_longitude = -85
max_longitude = 85

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
                lat_offset, lon_offset = offsets[map_size]
                if event.key == pygame.K_LEFT:
                    latitude -= lat_offset
                if event.key == pygame.K_RIGHT:
                    latitude += lat_offset
                if event.key == pygame.K_UP:
                    longitude += lon_offset
                if event.key == pygame.K_DOWN:
                    longitude -= lon_offset
                # Handle border values
                if longitude < min_longitude:
                    longitude = min_longitude
                elif longitude > max_longitude:
                    longitude = max_longitude
                if latitude < min_latitude:
                    latitude = min_latitude
                elif latitude > max_latitude:
                    latitude = max_latitude
            print(longitude, latitude)
            # Each move action requires new map
            # Create and load new map
            create_new_map()
            map_image = pygame.image.load('map.png')
            # Draw new map
            draw_map()
    timer.tick(60)
pygame.quit()
