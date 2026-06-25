import pygame

from config import WHITE
from .text import draw_text


def draw_button(surface, text, x, y, w, h, color, hover_color, action=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    if x + w > mouse[0] > x and y + h > mouse[1] > y:
        pygame.draw.rect(surface, hover_color, (x, y, w, h), border_radius=10)
        if click[0] == 1 and action is not None:
            pygame.time.delay(150)
            action()
    else:
        pygame.draw.rect(surface, color, (x, y, w, h), border_radius=10)
    pygame.draw.rect(surface, WHITE, (x, y, w, h), 3, border_radius=10)
    draw_text(surface, text, 24, x + w // 2, y + h // 2, WHITE, center=True)
