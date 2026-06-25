import pygame
import random
import json
import os
import sys
import math

from particles import Particle, GoldenGlow, StarBurst, GOLD, BRIGHT_GOLD

pygame.init()
pygame.mixer.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 50, 50)
GREEN = (50, 200, 50)
YELLOW = (255, 255, 50)
PURPLE = (150, 50, 200)
BLUE = (50, 100, 255)
ORANGE = (255, 150, 50)
GRAY = (150, 150, 150)
DARK_GRAY = (80, 80, 80)
BROWN = (139, 69, 19)
PINK = (255, 105, 180)

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
        pygame.draw.circle(self.image, GOLD, (cx, cy + 2), self.radius - 3)
        pygame.draw.circle(self.image, BRIGHT_GOLD, (cx - 5, cy - 3), 6)
        pygame.draw.circle(self.image, (255, 255, 220), (cx - 7, cy - 6), 3)
        pygame.draw.rect(self.image, (180, 120, 20), (cx - 2, cy - self.radius, 4, 9))
        pygame.draw.ellipse(self.image, (100, 180, 50), (cx + 3, cy - self.radius - 1, 11, 7))
        for i in range(3):
            sx = cx + int(6 * math.cos(i * 2.094))
            sy = cy + 2 + int(6 * math.sin(i * 2.094))
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


class Game:
    STATE_MENU = 'menu'
    STATE_PLAYING = 'playing'
    STATE_PAUSED = 'paused'
    STATE_GAMEOVER = 'gameover'
    STATE_LEVEL_COMPLETE = 'level_complete'

    GOLDEN_SPAWN_INTERVAL = 480

    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("接水果大作战")
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = self.STATE_MENU
        self.high_score_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'high_score.json')
        self.high_score = self._load_high_score()
        self.music_on = True
        self._init_audio()
        self._reset_game()

    def _init_audio(self):
        try:
            self.sounds = {
                'catch': self._create_sound(freq=800, duration=80),
                'bomb': self._create_sound(freq=150, duration=200),
                'combo': self._create_sound(freq=1000, duration=120),
                'level_complete': self._create_sound(freq=600, duration=300),
                'game_over': self._create_sound(freq=200, duration=400),
                'golden': self._create_sound(freq=1200, duration=150),
                'bounce': self._create_sound(freq=500, duration=100),
                'star': self._create_sound(freq=900, duration=120),
            }
            self._play_background_music()
        except Exception:
            self.sounds = {}

    def _create_sound(self, freq=440, duration=100):
        try:
            import array
            sample_rate = 44100
            n_samples = int(sample_rate * duration / 1000)
            buf = array.array('h', [0] * n_samples)
            for i in range(n_samples):
                t = i / sample_rate
                buf[i] = int(32767 * 0.3 * (
                    0.6 * pygame.math.sin(2 * 3.14159 * freq * t) +
                    0.3 * pygame.math.sin(2 * 3.14159 * freq * 2 * t) +
                    0.1 * pygame.math.sin(2 * 3.14159 * freq * 3 * t)
                ) * max(0, 1 - t * 3))
            return pygame.mixer.Sound(buffer=buf)
        except Exception:
            return None

    def _play_sound(self, name):
        if name in self.sounds and self.sounds[name]:
            self.sounds[name].play()

    def _play_background_music(self):
        if not self.music_on:
            return
        try:
            pygame.mixer.music.stop()
            sample_rate = 44100
            import array
            notes = [523, 587, 659, 698, 784, 880, 784, 698, 659, 587]
            total_duration = len(notes) * 0.3
            n_samples = int(sample_rate * total_duration)
            buf = array.array('h', [0] * n_samples)
            for i in range(n_samples):
                t = i / sample_rate
                note_idx = min(int(t / 0.3), len(notes) - 1)
                freq = notes[note_idx]
                local_t = t - note_idx * 0.3
                envelope = max(0, 1 - local_t * 3)
                buf[i] = int(32767 * 0.15 * envelope * pygame.math.sin(2 * 3.14159 * freq * t))
            music_sound = pygame.mixer.Sound(buffer=buf)
            channel = pygame.mixer.Channel(0)
            channel.play(music_sound, loops=-1)
            self.music_channel = channel
        except Exception:
            pass

    def _toggle_music(self):
        self.music_on = not self.music_on
        if not self.music_on:
            if hasattr(self, 'music_channel'):
                self.music_channel.stop()
        else:
            self._play_background_music()

    def _load_high_score(self):
        try:
            if os.path.exists(self.high_score_file):
                with open(self.high_score_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('high_score', 0)
        except Exception:
            pass
        return 0

    def _save_high_score(self):
        try:
            with open(self.high_score_file, 'w', encoding='utf-8') as f:
                json.dump({'high_score': self.high_score}, f, ensure_ascii=False)
        except Exception:
            pass

    def _reset_game(self):
        self.score = 0
        self.health = 3
        self.level = 1
        self.level_time = 30
        self.spawn_timer = 0
        self.spawn_interval = 45
        self.golden_spawn_timer = 0
        self.all_sprites = pygame.sprite.Group()
        self.items = pygame.sprite.Group()
        self.particles = pygame.sprite.Group()
        self.golden_glows = []
        self.star_bursts = []
        self.basket = Basket()
        self.all_sprites.add(self.basket)
        self.combo = ComboDisplay()
        self.floating_texts = []
        self.level_start_ticks = None

    def _spawn_item(self):
        item = FallingItem(self.level)
        self.items.add(item)
        self.all_sprites.add(item)

    def _spawn_golden_apple(self):
        ga = GoldenApple(self.level)
        self.items.add(ga)
        self.all_sprites.add(ga)
        glow = ga.create_glow()
        self.golden_glows.append(glow)

    def _spawn_star_from_bomb(self, bomb_x, bomb_y):
        star = Star(bomb_x, bomb_y)
        self.items.add(star)
        self.all_sprites.add(star)
        burst = StarBurst(bomb_x, bomb_y)
        self.star_bursts.append(burst)
        self._play_sound('bounce')

    def _add_particles(self, x, y, color, count=10):
        for _ in range(count):
            p = Particle(x, y, color)
            self.particles.add(p)
            self.all_sprites.add(p)

    def _add_floating_text(self, text, x, y, color=YELLOW):
        self.floating_texts.append({'text': text, 'x': x, 'y': y, 'color': color, 'life': 60})

    def _handle_collisions(self):
        hits = pygame.sprite.spritecollide(self.basket, self.items, False, pygame.sprite.collide_rect)
        for item in hits:
            if item.is_star:
                multiplier = self.combo.get_multiplier()
                points = int(item.points * multiplier)
                self.score += points
                self.combo.add_combo()
                self._play_sound('star')
                self._add_particles(item.rect.centerx, item.rect.centery, BRIGHT_GOLD, 12)
                mult_text = f" x{multiplier:.1f}" if multiplier > 1 else ""
                self._add_floating_text(f"+{points}{mult_text}",
                                        item.rect.centerx, item.rect.centery, BRIGHT_GOLD)
                item.kill()

            elif item.is_bomb:
                self._spawn_star_from_bomb(item.rect.centerx, item.rect.top)
                self._add_particles(item.rect.centerx, item.rect.centery, ORANGE, 10)
                self._add_floating_text("弹飞!", item.rect.centerx, item.rect.centery, ORANGE)
                item.kill()

            elif item.is_golden:
                multiplier = self.combo.get_multiplier()
                points = int(item.points * multiplier)
                self.score += points
                self.combo.add_combo()
                self._play_sound('golden')
                self._add_particles(item.rect.centerx, item.rect.centery, GOLD, 20)
                mult_text = f" x{multiplier:.1f}" if multiplier > 1 else ""
                self._add_floating_text(f"+{points}{mult_text}",
                                        item.rect.centerx, item.rect.centery, GOLD)
                if item.glow:
                    item.glow.kill()
                    if item.glow in self.golden_glows:
                        self.golden_glows.remove(item.glow)
                item.kill()

            else:
                multiplier = self.combo.get_multiplier()
                points = int(item.points * multiplier)
                self.score += points
                if self.combo.combo >= 2:
                    self._play_sound('combo')
                else:
                    self._play_sound('catch')
                self.combo.add_combo()
                self._add_particles(item.rect.centerx, item.rect.centery,
                                    FallingItem.TYPES[item.item_type]['color'], 8)
                mult_text = f" x{multiplier:.1f}" if multiplier > 1 else ""
                self._add_floating_text(f"+{points}{mult_text}",
                                        item.rect.centerx, item.rect.centery, GREEN)
                item.kill()

    def _game_over(self):
        self.state = self.STATE_GAMEOVER
        self._play_sound('game_over')
        if self.score > self.high_score:
            self.high_score = self.score
            self._save_high_score()

    def _next_level(self):
        if self.level >= 10:
            self.state = self.STATE_GAMEOVER
            if self.score > self.high_score:
                self.high_score = self.score
                self._save_high_score()
            return
        self.level += 1
        self.level_time = 30
        self.spawn_interval = max(15, 45 - self.level * 3)
        self.items.empty()
        self.golden_glows.clear()
        self.star_bursts.clear()
        self.state = self.STATE_LEVEL_COMPLETE
        self._play_sound('level_complete')

    def _start_game(self):
        self._reset_game()
        self.state = self.STATE_PLAYING
        self.level_start_ticks = pygame.time.get_ticks()

    def _toggle_pause(self):
        if self.state == self.STATE_PLAYING:
            self.state = self.STATE_PAUSED
        elif self.state == self.STATE_PAUSED:
            self.state = self.STATE_PLAYING
            self.level_start_ticks = pygame.time.get_ticks() - ((30 - self.level_time) * 1000)

    def _update_level_time(self):
        if self.level_start_ticks is None:
            return
        elapsed = (pygame.time.get_ticks() - self.level_start_ticks) / 1000
        self.level_time = max(0, 30 - elapsed)
        if self.level_time <= 0:
            self._next_level()

    def _draw_background(self):
        for y in range(SCREEN_HEIGHT):
            color = (
                max(0, 135 - y // 5),
                max(0, 206 - y // 4),
                min(255, 235 + y // 20)
            )
            pygame.draw.line(self.screen, color, (0, y), (SCREEN_WIDTH, y))
        pygame.draw.rect(self.screen, (50, 150, 50), (0, SCREEN_HEIGHT - 60, SCREEN_WIDTH, 60))
        pygame.draw.rect(self.screen, (30, 100, 30), (0, SCREEN_HEIGHT - 60, SCREEN_WIDTH, 5))
        for x in range(0, SCREEN_WIDTH, 50):
            pygame.draw.circle(self.screen, (60, 180, 60), (x + 25, SCREEN_HEIGHT - 60), 8)

    def _draw_hud(self):
        hud_bg = pygame.Surface((SCREEN_WIDTH, 55), pygame.SRCALPHA)
        hud_bg.fill((0, 0, 0, 120))
        self.screen.blit(hud_bg, (0, 0))
        draw_text(self.screen, f"分数: {self.score}", 26, 20, 12, WHITE)
        draw_text(self.screen, f"最高: {self.high_score}", 20, 20, 42, YELLOW)
        draw_text(self.screen, f"第 {self.level} 关", 26, SCREEN_WIDTH // 2 - 40, 12, WHITE)
        time_color = RED if self.level_time < 10 else WHITE
        draw_text(self.screen, f"时间: {int(self.level_time)}s", 26,
                  SCREEN_WIDTH // 2 - 50, 42, time_color)
        for i in range(3):
            hx = SCREEN_WIDTH - 100 + i * 30
            hy = 20
            if i < self.health:
                pygame.draw.circle(self.screen, RED, (hx, hy), 10)
                pygame.draw.circle(self.screen, (255, 100, 100), (hx - 3, hy - 3), 3)
            else:
                pygame.draw.circle(self.screen, GRAY, (hx, hy), 10)
        music_text = "♪ ON" if self.music_on else "♪ OFF"
        music_color = GREEN if self.music_on else GRAY
        draw_text(self.screen, music_text, 20, SCREEN_WIDTH - 200, 15, music_color)
        draw_text(self.screen, "[P]暂停", 18, SCREEN_WIDTH - 200, 42, WHITE)

    def _draw_floating_texts(self):
        texts_to_remove = []
        for i, ft in enumerate(self.floating_texts):
            draw_text(self.screen, ft['text'], 24, ft['x'], ft['y'], ft['color'], center=True)
            ft['y'] -= 2
            ft['life'] -= 1
            if ft['life'] <= 0:
                texts_to_remove.append(i)
        for i in reversed(texts_to_remove):
            self.floating_texts.pop(i)

    def _draw_effects(self):
        for glow in self.golden_glows[:]:
            if glow.alive():
                glow.update()
                glow.draw(self.screen)
            else:
                self.golden_glows.remove(glow)
        for burst in self.star_bursts[:]:
            if burst.alive():
                burst.update()
                burst.draw(self.screen)
            else:
                self.star_bursts.remove(burst)

    def _draw_menu(self):
        self._draw_background()
        title_y = 130
        draw_text(self.screen, "🍎 接水果大作战 🍇", 56,
                  SCREEN_WIDTH // 2, title_y, ORANGE, center=True)
        draw_text(self.screen, "Fruit Catcher", 28,
                  SCREEN_WIDTH // 2, title_y + 60, YELLOW, center=True)
        draw_text(self.screen, f"最高分: {self.high_score}", 28,
                  SCREEN_WIDTH // 2, title_y + 100, GREEN, center=True)
        instructions = [
            "← → 方向键移动篮子",
            "接水果得分，碰炸弹弹飞变星星⭐",
            "金色苹果🌟直接+50分!",
            "连续接住获得 Combo 加分",
            "共 10 关，每关 30 秒，3 条命",
        ]
        for i, line in enumerate(instructions):
            draw_text(self.screen, line, 20,
                      SCREEN_WIDTH // 2, title_y + 150 + i * 30, WHITE, center=True)
        button_w, button_h = 200, 60
        button_x = SCREEN_WIDTH // 2 - button_w // 2
        draw_button(self.screen, "开始游戏", button_x, 460, button_w, button_h,
                    GREEN, (80, 230, 80), self._start_game)
        draw_button(self.screen, f"音乐: {'开' if self.music_on else '关'}",
                    button_x, 530, button_w, button_h, BLUE, (100, 150, 255), self._toggle_music)

    def _draw_pause(self):
        self._draw_background()
        self.all_sprites.draw(self.screen)
        self._draw_effects()
        self._draw_hud()
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))
        draw_text(self.screen, "游戏暂停", 56, SCREEN_WIDTH // 2, 200, WHITE, center=True)
        button_w, button_h = 200, 60
        button_x = SCREEN_WIDTH // 2 - button_w // 2
        draw_button(self.screen, "继续游戏", button_x, 280, button_w, button_h,
                    GREEN, (80, 230, 80), self._toggle_pause)
        draw_button(self.screen, f"音乐: {'开' if self.music_on else '关'}",
                    button_x, 360, button_w, button_h, BLUE, (100, 150, 255), self._toggle_music)
        draw_button(self.screen, "返回主菜单", button_x, 440, button_w, button_h,
                    GRAY, (180, 180, 180), lambda: self._set_state(self.STATE_MENU))

    def _draw_game_over(self):
        self._draw_background()
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        if self.level >= 10 and self.health > 0:
            title = "🎉 恭喜通关！🎉"
            title_color = YELLOW
        else:
            title = "游戏结束"
            title_color = RED
        draw_text(self.screen, title, 56, SCREEN_WIDTH // 2, 180, title_color, center=True)
        draw_text(self.screen, f"最终得分: {self.score}", 36,
                  SCREEN_WIDTH // 2, 260, WHITE, center=True)
        is_new_record = self.score >= self.high_score and self.score > 0
        if is_new_record:
            draw_text(self.screen, "🏆 新纪录！", 32,
                      SCREEN_WIDTH // 2, 310, YELLOW, center=True)
        draw_text(self.screen, f"到达关卡: 第 {self.level} 关", 26,
                  SCREEN_WIDTH // 2, 360, WHITE, center=True)
        draw_text(self.screen, f"历史最高: {self.high_score}", 26,
                  SCREEN_WIDTH // 2, 400, GREEN, center=True)
        button_w, button_h = 200, 60
        button_x = SCREEN_WIDTH // 2 - button_w // 2
        draw_button(self.screen, "重新开始", button_x, 460, button_w, button_h,
                    GREEN, (80, 230, 80), self._start_game)
        draw_button(self.screen, "返回主菜单", button_x, 540, button_w, button_h,
                    GRAY, (180, 180, 180), lambda: self._set_state(self.STATE_MENU))

    def _draw_level_complete(self):
        self._draw_background()
        self.all_sprites.draw(self.screen)
        self._draw_hud()
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        self.screen.blit(overlay, (0, 0))
        draw_text(self.screen, f"第 {self.level - 1} 关完成!", 48,
                  SCREEN_WIDTH // 2, 200, GREEN, center=True)
        draw_text(self.screen, f"准备进入第 {self.level} 关...", 32,
                  SCREEN_WIDTH // 2, 270, WHITE, center=True)
        draw_text(self.screen, f"当前得分: {self.score}", 28,
                  SCREEN_WIDTH // 2, 330, YELLOW, center=True)
        draw_text(self.screen, f"剩余生命: {'♥' * self.health}", 28,
                  SCREEN_WIDTH // 2, 370, RED, center=True)
        draw_text(self.screen, "按任意键继续", 24,
                  SCREEN_WIDTH // 2, 450, GRAY, center=True)

    def _set_state(self, state):
        self.state = state
        if state == self.STATE_MENU:
            self.items.empty()
            self.golden_glows.clear()
            self.star_bursts.clear()
            if hasattr(self, 'music_channel'):
                self.music_channel.stop()
            self._play_background_music()

    def run(self):
        while self.running:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if self.state == self.STATE_MENU:
                        if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                            self._start_game()
                    elif self.state == self.STATE_PLAYING:
                        if event.key == pygame.K_p or event.key == pygame.K_ESCAPE:
                            self._toggle_pause()
                        elif event.key == pygame.K_m:
                            self._toggle_music()
                    elif self.state == self.STATE_PAUSED:
                        if event.key == pygame.K_p or event.key == pygame.K_ESCAPE:
                            self._toggle_pause()
                    elif self.state == self.STATE_LEVEL_COMPLETE:
                        self.state = self.STATE_PLAYING
                        self.level_start_ticks = pygame.time.get_ticks()
                    elif self.state == self.STATE_GAMEOVER:
                        if event.key == pygame.K_RETURN:
                            self._start_game()
                        elif event.key == pygame.K_ESCAPE:
                            self._set_state(self.STATE_MENU)

            if self.state == self.STATE_PLAYING:
                keys = pygame.key.get_pressed()
                self.basket.update(keys)
                self.items.update()
                self.particles.update()
                self.combo.update()
                self.spawn_timer += 1
                if self.spawn_timer >= self.spawn_interval:
                    self.spawn_timer = 0
                    self._spawn_item()
                    if random.random() < 0.3 and self.level > 3:
                        self._spawn_item()
                self.golden_spawn_timer += 1
                if self.golden_spawn_timer >= self.GOLDEN_SPAWN_INTERVAL:
                    self.golden_spawn_timer = 0
                    self._spawn_golden_apple()
                self._handle_collisions()
                self._update_level_time()

            if self.state == self.STATE_MENU:
                self._draw_menu()
            elif self.state == self.STATE_PLAYING or self.state == self.STATE_PAUSED:
                self._draw_background()
                self.all_sprites.draw(self.screen)
                self._draw_effects()
                self._draw_hud()
                self.combo.draw(self.screen)
                self._draw_floating_texts()
                if self.state == self.STATE_PAUSED:
                    self._draw_pause()
            elif self.state == self.STATE_GAMEOVER:
                self._draw_game_over()
            elif self.state == self.STATE_LEVEL_COMPLETE:
                self._draw_level_complete()

            pygame.display.flip()

        pygame.quit()
        sys.exit()


if __name__ == '__main__':
    game = Game()
    game.run()
