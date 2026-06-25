import pygame
import random

from config import SCREEN_WIDTH, SCREEN_HEIGHT, RED, YELLOW, PURPLE, DARK_GRAY, ORANGE


class FallingItem(pygame.sprite.Sprite):
    TYPES = {
        'apple': {'color': RED, 'points': 10, 'radius': 20, 'is_bomb': False},
        'banana': {'color': YELLOW, 'points': 15, 'radius': 22, 'is_bomb': False},
        'grape': {'color': PURPLE, 'points': 20, 'radius': 20, 'is_bomb': False},
        'bomb': {'color': DARK_GRAY, 'points': 0, 'radius': 22, 'is_bomb': True}
    }

    def __init__(self, level=1):
        super().__init__()
        self.item_type = random.choices(
            ['apple', 'banana', 'grape', 'bomb'],
            weights=[30, 25, 20, 20 + level * 1],
            k=1
        )[0]
        props = self.TYPES[self.item_type]
        self.radius = props['radius']
        self.points = props['points']
        self.is_bomb = props['is_bomb']
        self.is_golden = False
        self.is_star = False
        self.image = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        self._draw_item()
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(20, SCREEN_WIDTH - 20 - self.radius * 2)
        self.rect.y = -self.radius * 2
        self.speed = random.randint(2, 4) + level * 0.5
        self.rotation = 0
        self.rot_speed = random.choice([-2, -1, 1, 2])

    def _draw_item(self):
        if self.item_type == 'apple':
            pygame.draw.circle(self.image, RED, (self.radius, self.radius + 2), self.radius - 3)
            pygame.draw.circle(self.image, (255, 100, 100), (self.radius - 6, self.radius - 4), 5)
            pygame.draw.rect(self.image, (101, 67, 33), (self.radius - 2, self.radius - self.radius, 4, 8))
            pygame.draw.ellipse(self.image, (50, 150, 50), (self.radius + 2, self.radius - self.radius - 2, 10, 6))
        elif self.item_type == 'banana':
            points = []
            for i in range(20):
                angle = i * 3.14 / 19 + 0.5
                x = self.radius + int((self.radius - 5) * 0.9 * (angle / 3.14 - 0.5) * 2)
                y = self.radius + int((self.radius - 5) * 0.6 * ((3.14 - angle) / 3.14 - 0.5))
                points.append((x, y))
            pygame.draw.polygon(self.image, YELLOW, points)
            pygame.draw.polygon(self.image, (200, 200, 0), points, 2)
            pygame.draw.circle(self.image, (139, 69, 19), (self.radius - 12, self.radius - 10), 3)
        elif self.item_type == 'grape':
            positions = [
                (self.radius, self.radius - 8),
                (self.radius - 10, self.radius - 2),
                (self.radius + 10, self.radius - 2),
                (self.radius - 5, self.radius + 6),
                (self.radius + 5, self.radius + 6),
                (self.radius, self.radius + 12)
            ]
            for pos in positions:
                pygame.draw.circle(self.image, PURPLE, pos, 7)
                pygame.draw.circle(self.image, (200, 100, 220), (pos[0] - 2, pos[1] - 2), 2)
            pygame.draw.rect(self.image, (101, 67, 33), (self.radius - 1, self.radius - self.radius, 3, 6))
        elif self.item_type == 'bomb':
            pygame.draw.circle(self.image, DARK_GRAY, (self.radius, self.radius + 2), self.radius - 3)
            pygame.draw.circle(self.image, (120, 120, 120), (self.radius - 6, self.radius - 4), 4)
            pygame.draw.rect(self.image, (101, 67, 33), (self.radius - 2, self.radius - self.radius - 2, 4, 8))
            for i in range(5):
                fx = self.radius + random.randint(-8, 8)
                fy = self.radius - self.radius - 8 - random.randint(0, 8)
                pygame.draw.circle(self.image, random.choice([ORANGE, YELLOW, RED]), (fx, fy), random.randint(2, 4))

    def update(self):
        self.rect.y += self.speed
        self.rotation += self.rot_speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()
