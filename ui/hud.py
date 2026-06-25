import pygame

from config import SCREEN_WIDTH, WHITE, RED, YELLOW, GREEN, GRAY
from .text import draw_text


def draw_hud(surface, score, high_score, level, level_time, health, music_on):
    hud_bg = pygame.Surface((SCREEN_WIDTH, 55), pygame.SRCALPHA)
    hud_bg.fill((0, 0, 0, 120))
    surface.blit(hud_bg, (0, 0))
    draw_text(surface, f"分数: {score}", 26, 20, 12, WHITE)
    draw_text(surface, f"最高: {high_score}", 20, 20, 42, YELLOW)
    draw_text(surface, f"第 {level} 关", 26, SCREEN_WIDTH // 2 - 40, 12, WHITE)
    time_color = RED if level_time < 10 else WHITE
    draw_text(surface, f"时间: {int(level_time)}s", 26,
              SCREEN_WIDTH // 2 - 50, 42, time_color)
    for i in range(3):
        hx = SCREEN_WIDTH - 100 + i * 30
        hy = 20
        if i < health:
            pygame.draw.circle(surface, RED, (hx, hy), 10)
            pygame.draw.circle(surface, (255, 100, 100), (hx - 3, hy - 3), 3)
        else:
            pygame.draw.circle(surface, GRAY, (hx, hy), 10)
    music_text = "♪ ON" if music_on else "♪ OFF"
    music_color = GREEN if music_on else GRAY
    draw_text(surface, music_text, 20, SCREEN_WIDTH - 200, 15, music_color)
    draw_text(surface, "[P]暂停", 18, SCREEN_WIDTH - 200, 42, WHITE)
