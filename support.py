import requests
import sys


def request(server, params=None):
    try:
        if params:
            response = requests.get(server, params=params)
        else:
            response = requests.get(server)
        if not response:
            print("Ошибка выполнения запроса:")
            print(response.url)
            print("Http статус:", response.status_code, "(", response.reason, ")")
            sys.exit(1)
    except:
        print("Запрос не удалось выполнить. Проверьте наличие сети Интернет.")
        sys.exit(1)
    return response


def get_dimensions(toponym):
    lower_corner = toponym["boundedBy"]["Envelope"]["lowerCorner"].split()
    upper_corner = toponym["boundedBy"]["Envelope"]["upperCorner"].split()
    x_size = abs(float(upper_corner[0]) - float(lower_corner[0]))
    y_size = abs(float(upper_corner[1]) - float(lower_corner[1]))
    return [x_size, y_size]
