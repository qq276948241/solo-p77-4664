from config import SCREEN_WIDTH, YELLOW
from .text import draw_text


class ComboDisplay:
    def __init__(self):
        self.combo = 0
        self.timer = 0
        self.max_timer = 90

    def add_combo(self):
        self.combo += 1
        self.timer = self.max_timer

    def reset(self):
        self.combo = 0
        self.timer = 0

    def get_multiplier(self):
        if self.combo >= 10:
            return 3.0
        elif self.combo >= 5:
            return 2.0
        elif self.combo >= 3:
            return 1.5
        return 1.0

    def update(self):
        if self.timer > 0:
            self.timer -= 1
            if self.timer <= 0:
                self.combo = 0

    def draw(self, surface):
        if self.combo >= 3 and self.timer > 0:
            alpha = min(255, self.timer * 3)
            color = (255, min(255, 50 + (10 - self.combo) * 20), 50)
            size = 36 + min(20, self.combo * 2)
            draw_text(surface, f"COMBO x{self.combo}!", size,
                      SCREEN_WIDTH // 2, 150, color, center=True)
            draw_text(surface, f"x{self.get_multiplier():.1f} 倍分", 24,
                      SCREEN_WIDTH // 2, 190, YELLOW, center=True)
