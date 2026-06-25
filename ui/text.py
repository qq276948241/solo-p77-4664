import pygame

from config import WHITE

FONT_PATH = pygame.font.match_font('simhei') or pygame.font.match_font('microsoftyahei') or None


def draw_text(surface, text, size, x, y, color=WHITE, center=False):
    if FONT_PATH:
        font = pygame.font.Font(FONT_PATH, size)
    else:
        font = pygame.font.SysFont(None, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    if center:
        text_rect.center = (x, y)
    else:
        text_rect.topleft = (x, y)
    surface.blit(text_surface, text_rect)
    return text_rect
