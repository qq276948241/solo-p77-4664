import pygame
import random
import math

from config import SCREEN_WIDTH, SCREEN_HEIGHT
from effects import GoldenGlow, GOLD, BRIGHT_GOLD


class GoldenApple(pygame.sprite.Sprite):
    def __init__(self, level=1):
        super().__init__()
        self.radius = 22
        self.item_type = 'golden_apple'
        self.points = 50
        self.is_bomb = False
        self.is_golden = True
        self.is_star = False
        self.image = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        self._draw()
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(30, SCREEN_WIDTH - 30 - self.radius * 2)
        self.rect.y = -self.radius * 2
        self.speed = 2.5 + level * 0.3
        self.glow = None

    def _draw(self):
        cx, cy = self.radius, self.radius
        pygame.draw.circle(self.image, GOLD, (cx, cy), self.radius - 3)
        pygame.draw.circle(self.image, BRIGHT_GOLD, (cx - 5, cy - 5), 6)
        pygame.draw.circle(self.image, (255, 255, 220), (cx - 7, cy - 8), 3)
        pygame.draw.rect(self.image, (180, 120, 20), (cx - 2, cy - self.radius - 2, 4, 9))
        pygame.draw.ellipse(self.image, (100, 180, 50), (cx + 3, cy - self.radius - 3, 11, 7))
        for i in range(3):
            sx = cx + int(6 * math.cos(i * 2.094))
            sy = cy + int(6 * math.sin(i * 2.094))
            pygame.draw.circle(self.image, (255, 255, 255), (sx, sy), 1)

    def create_glow(self):
        self.glow = GoldenGlow(self)
        return self.glow

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            if self.glow:
                self.glow.kill()
            self.kill()
