import pygame
import random
import math

GOLD = (255, 215, 0)
BRIGHT_GOLD = (255, 235, 100)
PALE_GOLD = (255, 245, 180)


class Particle(pygame.sprite.Sprite):
    def __init__(self, x, y, color, vx=None, vy=None, size=None, life=None):
        super().__init__()
        self.size = size or random.randint(3, 8)
        self.image = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (self.size, self.size), self.size)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.vx = vx if vx is not None else random.randint(-5, 5)
        self.vy = vy if vy is not None else random.randint(-8, -2)
        self.life = life or 30
        self.max_life = self.life
        self.color = color

    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy
        self.vy += 0.3
        self.life -= 1
        if self.life <= 0:
            self.kill()


class GoldenGlow(pygame.sprite.Sprite):
    def __init__(self, target):
        super().__init__()
        self.target = target
        self.halo_radius = 32
        self.image = pygame.Surface((self.halo_radius * 2, self.halo_radius * 2), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.tick = 0
        self.sparkles = []
        self._sync_position()

    def _sync_position(self):
        if self.target and self.target.alive():
            self.rect.center = self.target.rect.center
        else:
            self.kill()

    def _draw_halo(self):
        self.image.fill((0, 0, 0, 0))
        cx, cy = self.halo_radius, self.halo_radius
        pulse = math.sin(self.tick * 0.1) * 4
        for layer in range(3, 0, -1):
            r = int(self.halo_radius - 8 + pulse + layer * 3)
            alpha = max(0, 60 - layer * 18)
            surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*GOLD, alpha), (r, r), r)
            self.image.blit(surf, (cx - r, cy - r))
        inner_r = int(18 + pulse * 0.5)
        pygame.draw.circle(self.image, (*BRIGHT_GOLD, 40), (cx, cy), inner_r)
        self._draw_sparkles(cx, cy, pulse)

    def _draw_sparkles(self, cx, cy, pulse):
        if self.tick % 4 == 0:
            angle = random.uniform(0, 2 * math.pi)
            dist = random.uniform(10, 22 + pulse)
            self.sparkles.append({
                'angle': angle,
                'dist': dist,
                'life': random.randint(8, 16),
                'size': random.randint(1, 3)
            })
        new_sparkles = []
        for s in self.sparkles:
            s['life'] -= 1
            s['dist'] += 0.5
            s['angle'] += 0.05
            if s['life'] > 0:
                new_sparkles.append(s)
                alpha = min(255, s['life'] * 25)
                sx = cx + int(s['dist'] * math.cos(s['angle']))
                sy = cy + int(s['dist'] * math.sin(s['angle']))
                if 0 <= sx < self.halo_radius * 2 and 0 <= sy < self.halo_radius * 2:
                    size = s['size']
                    spark_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                    pygame.draw.circle(spark_surf, (*PALE_GOLD, alpha), (size, size), size)
                    self.image.blit(spark_surf, (sx - size, sy - size))
        self.sparkles = new_sparkles[-20:]

    def update(self):
        self.tick += 1
        self._sync_position()
        if self.alive():
            self._draw_halo()

    def draw(self, surface):
        if self.alive():
            surface.blit(self.image, self.rect)


class StarBurst(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.base_x = x
        self.base_y = y
        self.tick = 0
        self.max_life = 25
        self.rays = []
        for i in range(8):
            self.rays.append({
                'angle': i * math.pi / 4 + random.uniform(-0.2, 0.2),
                'speed': random.uniform(3, 7),
                'length': random.uniform(12, 25)
            })
        size = 80
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self):
        self.tick += 1
        if self.tick >= self.max_life:
            self.kill()
            return
        progress = self.tick / self.max_life
        alpha = int(255 * (1 - progress))
        self.image.fill((0, 0, 0, 0))
        cx, cy = self.image.get_width() // 2, self.image.get_height() // 2
        for ray in self.rays:
            dist = ray['speed'] * self.tick
            length = ray['length'] * (1 - progress * 0.5)
            end_x = cx + int((dist + length) * math.cos(ray['angle']))
            end_y = cy + int((dist + length) * math.sin(ray['angle']))
            start_x = cx + int(dist * math.cos(ray['angle']))
            start_y = cy + int(dist * math.sin(ray['angle']))
            color = (*GOLD, alpha)
            pygame.draw.line(self.image, color, (start_x, start_y), (end_x, end_y), 2)
        inner_r = int(8 * (1 - progress))
        if inner_r > 0:
            pygame.draw.circle(self.image, (*BRIGHT_GOLD, alpha), (cx, cy), inner_r)

    def draw(self, surface):
        if self.alive():
            surface.blit(self.image, self.rect)
