import pygame
from support import request
from GUI import TextBox
import sys

# Const
map_api_server = "http://static-maps.yandex.ru/1.x/"
geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"
max_map_size = 17
min_map_size = 0
#   Keys used to move or resize map
control_keys = (pygame.K_PAGEUP, pygame.K_PAGEDOWN, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN,
                pygame.K_m)
#   Map modes
map_modes = ['sat', 'map', 'sat,skl']

# Offset for each map size
offsets = [[0, 0], [0, 0], [211, 82.9], [105.4, 62], [52.5, 37], [26.4, 19.65], [13.2, 9.65], [6.6, 4.865],
           [3.3, 2.464], [1.65, 1.232], [0.825, 0.6165], [0.4125, 0.30825], [0.20625, 0.1542], [0.103125, 0.07521],
           [0.0515625, 0.037605], [0.02578125, 0.0185], [0.012890625, 0.00940125], [0.0064453125, 0.004700625]]
max_latitude = 180
min_latitude = -180
min_longitude = -85
max_longitude = 85

# Start values
running = True
map_size = 0
longitude = 0
latitude = 0
map_type_index = 0
map_points = []


# Function for generating new map file.  Z(bool) - automatic scale if z is False
def create_new_map():
    # Params for static-maps request
    formated_pos = '{},{}'.format(str(longitude), str(latitude))
    map_params = {"ll": formated_pos, "l": map_modes[map_type_index], "z": str(map_size)}
    if map_points:
        map_params['pt'] = map_points
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


# Function for searching objects using search line
def search(text):
    if text != 'Not found':
        text = ','.join(text.split())
        global map_image, longitude, latitude, search_line
        # Geocoder request
        params = {"geocode": text, "format": "json"}
        response = request(geocoder_api_server, params=params)
        json_response = response.json()
        if json_response["response"]["GeoObjectCollection"]["featureMember"]:
            # Get toponym
            toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
            # Get toponym cords
            longitude, latitude = map(float, toponym["Point"]["pos"].split())
            # Add point on map, remove old one
            map_points.clear()
            map_points.append('{},{},pm2dgl'.format(longitude, latitude))
            # Create new map
            create_new_map()
            map_image = pygame.image.load('map.png')
        else:
            search_line.change_text('Not found')


# Pygame setup
pygame.init()
screen = pygame.display.set_mode((600, 500))
timer = pygame.time.Clock()
# Entry field
search_line = TextBox((0, 450, 600, 50), '', search)
# Create first map
create_new_map()
map_image = pygame.image.load('map.png')
# Draw map
screen.blit(map_image, (0, 0))

# Main loop
while running:
    # Clean screen
    screen.fill((255, 255, 255))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # Move or resize events catcher
        if event.type == pygame.KEYDOWN and event.key in control_keys:
            if event.key == pygame.K_PAGEDOWN and map_size - 1 >= min_map_size:
                map_size -= 1
            if event.key == pygame.K_PAGEUP and map_size + 1 <= max_map_size:
                map_size += 1
            if event.key in control_keys[2:-1]:
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
            # Key "m" switches map type
            if event.key == pygame.K_m:
                map_type_index = (map_type_index + 1) % 3
            # Each move action requires new map
            # Create and load new map
            create_new_map()
            map_image = pygame.image.load('map.png')
        # Search lane actions catcher
        search_line.get_event(event)
    # Update blinking thing
    search_line.update()
    # Draw search line
    search_line.render(screen)
    # Draw map
    screen.blit(map_image, (0, 0))
    pygame.display.flip()
    timer.tick(60)
pygame.quit()
