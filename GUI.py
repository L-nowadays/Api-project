import pygame

# Colors
GREY = (119, 113, 110)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
L_GREY = (190, 190, 190)


class Label:
    # Rect is pygame.rect object (x0, y0, dx, dy), text - str
    def __init__(self, rect, text='', font_size=None, multilines=False):
        self.rect = pygame.Rect(rect)
        self.inner_rect = pygame.Rect((rect[0] + 3, rect[1] + 3, rect[2] - 6, rect[3] - 6))
        # Font
        if font_size is None:
            # Font size is calculated using bordering rectangle height
            font_size = self.rect.height - 4
        self.font = pygame.font.Font(None, font_size)
        # Text
        self.rendered_text = []
        self.text = None
        self.text_height = 0
        # Multilines
        self.multilines = multilines
        # Create rendered text
        self.change_text(text)

    def change_text(self, text):
        test_text = ''
        if text:
            self.rendered_text = []
            if self.multilines:
                text_height = 0
                line_text = ''
                for char in text:
                    test_text += char
                    line_text += char
                    x_size, y_size = self.font.size(line_text)
                    if x_size > self.inner_rect.width - 25:
                        # Long text that doesnt fit rect will be cut(ending is '...')
                        if text_height + y_size > self.inner_rect.height - 4:
                            test_text = test_text[:-1] + '...'
                            line_text = line_text[:-1] + '...'
                            rendered_line = self.font.render(line_text, 1, BLACK)
                            self.rendered_text.append(rendered_line)
                            text_height += y_size
                            break
                        else:
                            rendered_line = self.font.render(line_text[:-1], 1, BLACK)
                            text_height += y_size + 1
                            self.rendered_text.append(rendered_line)
                            line_text = line_text[-1]

                if char == text[-1] and line_text:
                    text_height += y_size
                    rendered_line = self.font.render(line_text, 1, BLACK)
                    self.rendered_text.append(rendered_line)
            else:
                for char in text:
                    test_text += char
                    x_size, y_size = self.font.size(test_text)
                    if x_size > self.inner_rect.width - 25:
                        # Long text that doesnt fit rect will be cut(ending is '...')
                        test_text = test_text[:-1] + '...'
                        x_size = self.font.size(test_text)[0]
                        break
                self.rendered_text.append(self.font.render(test_text, 1, BLACK))
                text_height = y_size
            self.text_height = text_height
        self.text = test_text

    def render(self, surface):
        surface.fill(GREY, self.rect)
        surface.fill(WHITE, self.inner_rect)
        if self.text:
            y_pos = self.inner_rect.centery - self.text_height / 2
            if len(self.rendered_text) > 1:
                x_pos = self.inner_rect.left + 12.5
            else:
                x_pos = self.inner_rect.centerx - self.rendered_text[0].get_width() / 2
            for line in self.rendered_text:
                surface.blit(line, (x_pos, y_pos))
                y_pos += line.get_height() + 2


class TextBox(Label):
    def __init__(self, rect, text, exec_func=lambda: None, font_size=None):
        super().__init__(rect, text, font_size)
        # Execution function
        self.exec_func = exec_func
        # Blink
        self.active = True
        self.blink = True
        self.blink_timer = 0

    def get_event(self, event):
        if event.type == pygame.KEYDOWN and self.active:
            # Text length
            if self.rendered_text:
                text_length = self.rendered_text[-1].get_width()
            else:
                text_length = 0
            # Enter leads to execution
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self.exec_func(self.text)
            # Erase char
            elif event.key == pygame.K_BACKSPACE:
                if len(self.text) > 0:
                    if len(self.text) == 1:
                        self.change_text('')
                    else:
                        self.change_text(self.text[:-1])
            # Add char
            elif text_length < self.rect.width - 15:
                self.change_text(self.text + event.unicode)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.active = self.rect.collidepoint(event.pos)

    def update(self):
        if pygame.time.get_ticks() - self.blink_timer > 800:
            self.blink = not self.blink
            self.blink_timer = pygame.time.get_ticks()

    def render(self, surface):
        super().render(surface)
        if self.blink and self.active:
            if self.rendered_text:
                text_length = self.rendered_text[-1].get_width()
            else:
                text_length = 0
            pygame.draw.line(surface, BLACK,
                             (self.inner_rect.centerx + text_length / 2 + 2, self.inner_rect.top + 3),
                             (self.inner_rect.centerx + text_length / 2 + 2, self.inner_rect.bottom - 3))


class Button:
    def __init__(self, rect, text, action=lambda: None, font_size=None):
        self.rect = pygame.Rect(rect)
        self.text = None
        self.light = False
        self.action = action
        self.text_length = None
        # Prepared texts
        self.rendered_text = None
        self.rendered_light_text = None
        if font_size is None:
            # Font size is calculated using bordering rectangle height
            font_size = self.rect.height - 4
        self.font = pygame.font.Font(None, font_size)
        # Text position
        text_max_height = self.font.size('W')[1]
        y_pos = self.rect.centery - text_max_height / 2
        self.text_pos = [None, y_pos]
        # Set "text" as text for button
        self.change_text(text)

    def change_text(self, text):
        if text:
            self.rendered_text = None
            test_text = ''
            for char in text:
                test_text += char
                x_size, y_size = self.font.size(test_text)
                if x_size > self.rect.width - 25:
                    # Long text that doesnt fit rect will be cut(ending is '...')
                    test_text = test_text[:-1] + '...'
                    x_size = self.font.size(test_text)[0]
                    break
            self.rendered_text = self.font.render(test_text, 1, BLACK)
            self.rendered_light_text = self.font.render(test_text, 1, WHITE)
            x_pos = self.rect.centerx - x_size / 2
            self.text_pos[0] = x_pos
            self.text_length = x_size
        else:
            self.text_length = 0
        self.text = text

    def render(self, surface):
        if self.light:
            surface.fill(BLACK, self.rect)
            if self.text:
                surface.blit(self.rendered_light_text, self.text_pos)
        else:
            surface.fill(GREY, self.rect)
            if self.text:
                surface.blit(self.rendered_text, self.text_pos)

    def get_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.light = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.action()


class GUI:
    def __init__(self):
        self.pages = {}
        self.active_page = None

    def add_element(self, page, element):
        self.pages[page].append(element)

    def add_page(self, name, elements_list=[]):  # add_page('name', [button,...]) creates page with [button,...]
        self.pages[name] = elements_list.copy()

    def render(self, surface):
        if self.is_active():
            for element in self.pages[self.active_page]:
                render = getattr(element, "render", None)
                if callable(render):
                    element.render(surface)

    def update(self):
        if self.is_active():
            for element in self.pages[self.active_page]:
                update = getattr(element, "update", None)
                if callable(update):
                    element.update()

    def get_event(self, event):
        if self.is_active():
            for element in self.pages[self.active_page]:
                get_event = getattr(element, "get_event", None)
                if callable(get_event):
                    element.get_event(event)

    def open_page(self, page):
        self.active_page = page

    def close(self):
        self.active_page = None

    def is_active(self):
        return self.active_page is not None
