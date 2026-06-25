import pygame

from config import SCREEN_WIDTH, SCREEN_HEIGHT, BROWN


class Basket(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((100, 60), pygame.SRCALPHA)
        pygame.draw.rect(self.image, BROWN, (0, 20, 100, 40), border_radius=5)
        pygame.draw.rect(self.image, (101, 67, 33), (0, 20, 100, 40), 3, border_radius=5)
        pygame.draw.arc(self.image, BROWN, (10, 0, 80, 50), 3.14, 0, 5)
        for i in range(3):
            pygame.draw.line(self.image, (101, 67, 33), (15 + i * 30, 25), (15 + i * 30, 55), 2)
        pygame.draw.line(self.image, (101, 67, 33), (5, 40), (95, 40), 2)
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 20
        self.speed = 7

    def update(self, keys):
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += self.speed
