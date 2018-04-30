import pygame
from support import request
from GUI import TextBox, Button, Label, L_GREY, GUI
import sys

# Const
map_api_server = "http://static-maps.yandex.ru/1.x/"
geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"
max_map_size = 17
min_map_size = 3
#   Keys used to move or resize map
control_keys = (pygame.K_PAGEUP, pygame.K_PAGEDOWN, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN,
                pygame.K_m)
#   Map modes
map_modes = ['sat', 'map', 'sat,skl']

# Offset for each map size
offsets = [[105.4, 40], [52.5, 37], [26.4, 19.65], [13.2, 9.65], [6.6, 4.865],
           [3.3, 2.464], [1.65, 1.232], [0.825, 0.6165], [0.4125, 0.30825], [0.20625, 0.1542], [0.103125, 0.07521],
           [0.0515625, 0.037605], [0.02578125, 0.0185], [0.012890625, 0.00940125], [0.0064453125, 0.004700625]]
max_latitude = 87
min_latitude = -87
min_longitude = -180
max_longitude = 180

# Start values
p_i_value = ''
p_i_show = False
running = True
map_size = 3
longitude = 0
latitude = 0
map_type_index = 0
map_points = []


# Function for generating new map file.
def create_new_map():
    # Params for static-maps request
    formated_pos = '{},{}'.format(str(longitude), str(latitude))
    map_params = {"ll": formated_pos, "l": map_modes[map_type_index], "z": str(map_size)}
    if map_points:
        map_params['pt'] = map_points
    # Static-maps request
    response = request(map_api_server, params=map_params)
    if response:
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
    text = ','.join(text.split())
    global map_image, longitude, latitude, search_line, p_i_value
    # Clear p_i_value
    p_i_value = ''
    # Geocoder request
    params = {"geocode": text, "format": "json"}
    response = request(geocoder_api_server, params=params)
    json_response = response.json()
    if json_response["response"]["GeoObjectCollection"]["featureMember"]:
        # Get toponym
        toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        # Toponym name
        name = toponym["metaDataProperty"]["GeocoderMetaData"]['text']
        # Postal index
        try:
            p_i_value = toponym["metaDataProperty"]["GeocoderMetaData"]['Address']['postal_code']
        except KeyError:
            pass
        # Show name in adress line
        if p_i_show and p_i_value:
            address_line.change_text(name + ' | ' + p_i_value)
        else:
            address_line.change_text(name)
        # Get toponym cords
        longitude, latitude = map(float, toponym["Point"]["pos"].split())
        # Add point on map, remove old one
        map_points.clear()
        map_points.append('{},{},pm2dgl'.format(longitude, latitude))
        # Create new map
        create_new_map()
        map_image = pygame.image.load('map.png')
    else:
        address_line.change_text('Не найдено.')


# Function for clear button
def clear():
    global map_image
    map_points.clear()
    address_line.change_text('')
    create_new_map()
    map_image = pygame.image.load('map.png')


def postal_index():
    global p_i_show
    if map_points:
        p_i_show = not p_i_show
        if p_i_show:
            if p_i_value:
                new_text = address_line.text + ' | ' + p_i_value
                address_line.change_text(new_text)
        elif p_i_value:
            new_text = ' '.join(address_line.text.split()[:-2])
            address_line.change_text(new_text)


# Pygame setup
pygame.init()
screen = pygame.display.set_mode((700, 597))
timer = pygame.time.Clock()
# Entry field
search_line = TextBox((0, 450, 700, 50), '', search, 40)
# Adress line
address_line = Label((0, 497, 700, 100), '', 40, True)
# Clear button
clear_button = Button((600, 0, 100, 50), 'Сброс', clear, 28)
# Postal index button
postal_index_button = Button((600, 55, 100, 50), 'Индекс', postal_index, 28)
# Filling gui
gui = GUI()
gui.add_page('Main', [search_line, address_line, clear_button, postal_index_button])
gui.open_page('Main')
# Create first map
create_new_map()
map_image = pygame.image.load('map.png')
# Draw map
screen.blit(map_image, (0, 0))

# Main loop
while running:
    # Clean screen
    screen.fill(L_GREY)
    for event in pygame.event.get():
        # Quit case
        if event.type == pygame.QUIT:
            running = False
        # Move or resize events catcher
        if event.type == pygame.KEYDOWN and event.key in control_keys:
            if event.key == pygame.K_PAGEDOWN and map_size - 1 >= min_map_size:
                map_size -= 1
            if event.key == pygame.K_PAGEUP and map_size + 1 <= max_map_size:
                map_size += 1
            if event.key in control_keys[2:-1]:
                lon_offset, lat_offset = offsets[map_size - 3]
                if event.key == pygame.K_LEFT:
                    longitude -= lon_offset
                if event.key == pygame.K_RIGHT:
                    longitude += lon_offset
                if event.key == pygame.K_UP:
                    latitude += lat_offset
                if event.key == pygame.K_DOWN:
                    latitude -= lat_offset

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
        gui.get_event(event)
    # Update gui
    gui.update()
    # Draw gui
    gui.render(screen)
    # Draw map
    screen.blit(map_image, (0, 0))
    pygame.display.flip()
    timer.tick(60)
pygame.quit()
