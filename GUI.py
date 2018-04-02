import pygame

# Colors
GREY = (119, 113, 110)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


class TextBox:
    def __init__(self, rect, text):
        self.rect = pygame.Rect(rect)
        self.inner_rect = pygame.Rect((rect[0] + 3, rect[1] + 3, rect[2] - 6, rect[3] - 6))
        # Font size is calculated using bordering rectangle height
        self.font = pygame.font.Font(None, self.rect.height - 4)
        self.active = True
        self.blink = True
        self.blink_timer = 0
        self.rendered_text = None
        self.text = None
        self.text_length = None
        # Text position
        text_max_height = self.font.size('W')[1]
        y_pos = self.inner_rect.centery - text_max_height / 2
        self.text_pos = [None, y_pos]
        # Create rendered text
        self.change_text(text)

    def get_event(self, event):
        if event.type == pygame.KEYDOWN and self.active:
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self.execute()
            elif event.key == pygame.K_BACKSPACE:
                if len(self.text) > 0:
                    if len(self.text) == 1:
                        self.change_text('')
                    else:
                        self.change_text(self.text[:-1])

            elif self.rendered_text.get_width() < self.rect.width - 15:
                self.change_text(self.text + event.unicode)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.active = self.rect.collidepoint(event.pos)

    def update(self):
        if pygame.time.get_ticks() - self.blink_timer > 800:
            self.blink = not self.blink
            self.blink_timer = pygame.time.get_ticks()

    def render(self, surface):
        surface.fill(GREY, self.rect)
        surface.fill(WHITE, self.inner_rect)
        if self.text:
            surface.blit(self.rendered_text, self.text_pos)
        if self.blink and self.active:
            pygame.draw.line(surface, BLACK,
                             (self.inner_rect.centerx + self.text_length / 2 + 2, self.inner_rect.top + 3),
                             (self.inner_rect.centerx + self.text_length / 2 + 2, self.inner_rect.bottom - 3))

    def change_text(self, text):
        if text:
            self.rendered_text = []
            test_text = ''
            for char in text:
                test_text += char
                x_size, y_size = self.font.size(test_text)
                if x_size > self.inner_rect.width - 25:
                    # Long text that doesnt fit rect will be cut(ending is '...')
                    test_text = test_text[:-1] + '...'
                    x_size = self.font.size(test_text)[0]
                    break
            self.rendered_text = self.font.render(test_text, 1, BLACK)
            x_pos = self.inner_rect.centerx - x_size / 2
            self.text_pos[0] = x_pos
            self.text_length = x_size
        else:
            self.text_length = 0
        self.text = text
