import pygame
from support import *

pos = [20, 50]
strpos = ','.join(map(str, pos))
z = 17
geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"
geocoder_params = {"geocode": strpos, "format": "json"}

# Geocoder request
response = request(geocoder_api_server, params=geocoder_params)
json_response = response.json()

map_api_server = "http://static-maps.yandex.ru/1.x/"


def create_new_map():
    # Params for static-maps request
    map_params = {"ll": strpos, "z": str(z), "l": "map"}
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


def draw_map():
    screen.fill((255, 255, 255))
    screen.blit(map_image, (0, 0))
    pygame.display.flip()
    timer.tick(60)


# Show map
pygame.init()
screen = pygame.display.set_mode((600, 450))
timer = pygame.time.Clock()
create_new_map()
map_image = pygame.image.load('map.png')
running = True
draw_map()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_PAGEDOWN:
                if z - 1 >= 0:
                    z -= 1
            elif event.key == pygame.K_PAGEUP:
                if z + 1 <= 17:
                    z += 1
            if event.key in (pygame.K_PAGEUP, pygame.K_PAGEDOWN):
                create_new_map()
                map_image = pygame.image.load('map.png')
                draw_map()
pygame.quit()
