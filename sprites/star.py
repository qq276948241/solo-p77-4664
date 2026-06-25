import pygame
import random
import math

from config import SCREEN_WIDTH, SCREEN_HEIGHT
from effects import GOLD, BRIGHT_GOLD


class Star(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.item_type = 'star'
        self.points = 30
        self.is_bomb = False
        self.is_golden = False
        self.is_star = True
        self.radius = 18
        self.size = self.radius * 2
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self._draw_star()
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.vy = -10
        self.gravity = 0.2
        self.wobble = 0
        self.wobble_speed = random.choice([-0.08, 0.08])

    def _draw_star(self):
        cx, cy = self.radius, self.radius
        points = []
        for i in range(10):
            angle = i * math.pi / 5 - math.pi / 2
            r = self.radius - 4 if i % 2 == 0 else (self.radius - 4) * 0.45
            px = cx + int(r * math.cos(angle))
            py = cy + int(r * math.sin(angle))
            points.append((px, py))
        pygame.draw.polygon(self.image, BRIGHT_GOLD, points)
        pygame.draw.polygon(self.image, GOLD, points, 2)
        inner_points = []
        for i in range(10):
            angle = i * math.pi / 5 - math.pi / 2
            r = (self.radius - 4) * 0.55 if i % 2 == 0 else (self.radius - 4) * 0.25
            px = cx + int(r * math.cos(angle))
            py = cy + int(r * math.sin(angle))
            inner_points.append((px, py))
        pygame.draw.polygon(self.image, (255, 255, 200), inner_points)
        pygame.draw.circle(self.image, (255, 255, 255), (cx - 3, cy - 3), 2)

    def update(self):
        self.vy += self.gravity
        self.rect.y += self.vy
        self.wobble += self.wobble_speed
        self.rect.x += int(math.sin(self.wobble) * 1.5)
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()
