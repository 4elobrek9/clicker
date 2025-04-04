import pygame
import sys
import random
import math
import pickle  # Для работы с сохранениями
from pygame.locals import *
from pygame import gfxdraw

# Инициализация Pygame
pygame.init()
pygame.mixer.init()

# Настройки окна
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hamster Combat Clicker")

# Шрифты
try:
    title_font = pygame.font.Font(None, 48)
    main_font = pygame.font.Font(None, 24)
    tooltip_font = pygame.font.Font(None, 22)
except:
    title_font = pygame.font.SysFont('arial', 48)
    main_font = pygame.font.SysFont('arial', 24)
    tooltip_font = pygame.font.SysFont('arial', 22)

# Цветовая палитра
COLORS = {
    "background": (18, 18, 29),
    "primary": (255, 215, 0),
    "secondary": (230, 230, 250),
    "accent": (255, 105, 180),
    "text": (230, 230, 250),
    "panel": (30, 30, 45),
    "button": (40, 40, 60),
    "button_hover": (60, 60, 80),
    "tooltip": (50, 50, 70)
}

# Загрузка изображений
try:
    hamster_img = pygame.image.load("hamster.jpg").convert_alpha()
    background_img = pygame.image.load("back.webp").convert()
    coin_img = pygame.image.load("coin.jpg").convert_alpha()
    
    # Масштабирование изображений
    hamster_img = pygame.transform.scale(hamster_img, (150, 150))
    background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))
    coin_img = pygame.transform.scale(coin_img, (30, 30))
except:
    # Заглушки если изображений нет
    hamster_img = pygame.Surface((150, 150), pygame.SRCALPHA)
    pygame.draw.circle(hamster_img, (200, 150, 100), (75, 75), 75)
    background_img = pygame.Surface((WIDTH, HEIGHT))
    background_img.fill((50, 50, 70))
    coin_img = pygame.Surface((30, 30), pygame.SRCALPHA)
    pygame.draw.circle(coin_img, (255, 215, 0), (15, 15), 15)

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.size = random.randint(2, 5)
        self.color = color
        self.speed = random.uniform(1, 3)
        self.angle = random.uniform(0, 6.28)
        self.life = random.randint(20, 40)
        self.original_life = self.life
        
    def update(self):
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed
        self.life -= 1
        self.size = max(0, self.size * (self.life / self.original_life))
        
    def draw(self, surface):
        alpha = int(255 * (self.life / self.original_life))
        color = (*self.color[:3], alpha)
        pygame.gfxdraw.filled_circle(surface, int(self.x), int(self.y), int(self.size), color)

class AnimatedHamster:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 150
        self.animation_frame = 0
        self.scale_factor = 1.0
        self.target_scale = 1.0
        self.particles = []
        self.image = hamster_img
        
    def update(self):
        self.scale_factor += (self.target_scale - self.scale_factor) * 0.1
        
        if self.animation_frame > 0:
            self.animation_frame -= 1
            
        for particle in self.particles[:]:
            particle.update()
            if particle.life <= 0:
                self.particles.remove(particle)
                
    def draw(self, surface):
        scaled_size = int(self.size * self.scale_factor)
        scaled_img = pygame.transform.scale(self.image, (scaled_size, scaled_size))
        img_rect = scaled_img.get_rect(center=(self.x, self.y))
        
        shadow = pygame.Surface((scaled_size, scaled_size), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 50), (0, 0, scaled_size, scaled_size//3))
        shadow_rect = shadow.get_rect(center=(self.x, self.y + scaled_size//2 - 10))
        surface.blit(shadow, shadow_rect)
        
        surface.blit(scaled_img, img_rect)
        
        for particle in self.particles:
            particle.draw(surface)
            
    def click(self):
        self.animation_frame = 10
        self.target_scale = 0.95
        pygame.time.set_timer(pygame.USEREVENT, 100, True)
        
        for _ in range(15):
            self.particles.append(Particle(
                self.x + random.randint(-50, 50),
                self.y + random.randint(-50, 50),
                (*COLORS["primary"], 255)
            ))

class UpgradeButton:
    def __init__(self, x, y, width, height, upgrade):
        self.rect = pygame.Rect(x, y, width, height)
        self.upgrade = upgrade
        self.level = 0
        self.hover = False
        self.pulse = 0
        
    def update(self):
        self.pulse = max(0, self.pulse - 0.05)
        
    def draw(self, surface):
        base_color = COLORS["button_hover"] if self.hover else COLORS["button"]
        if self.pulse > 0:
            pulse_color = (
                min(255, base_color[0] + int(100 * self.pulse)),
                min(255, base_color[1] + int(100 * self.pulse)),
                min(255, base_color[2] + int(100 * self.pulse))
            )
            base_color = pulse_color
            
        pygame.draw.rect(surface, base_color, self.rect, border_radius=10)
        pygame.draw.rect(surface, COLORS["primary"], self.rect, 2, border_radius=10)
        
        name_text = main_font.render(self.upgrade["name"], True, COLORS["text"])
        level_text = main_font.render(f"Ур. {self.level}", True, COLORS["secondary"])
        cost_text = main_font.render(f"{self.upgrade['cost']}", True, COLORS["primary"])
        
        surface.blit(name_text, (self.rect.x + 15, self.rect.y + 10))
        surface.blit(level_text, (self.rect.x + 15, self.rect.y + 35))
        
        coin_rect = coin_img.get_rect(center=(self.rect.x + self.rect.width - 30, self.rect.y + self.rect.height//2))
        surface.blit(coin_img, coin_rect)
        surface.blit(cost_text, (self.rect.x + self.rect.width - 60 - cost_text.get_width(), 
                  self.rect.y + self.rect.height//2 - cost_text.get_height()//2))
    
    def draw_tooltip(self, surface):
        if self.hover:
            tooltips = {
                "Боевые перчатки": "Увеличивает силу удара на +1 (базовое улучшение)",
                "Тренировочный лагерь": "Увеличивает силу удара на +2 (интенсивные тренировки)",
                "Стероидные семечки": "Увеличивает силу удара на +5 (временный эффект)",
                "Титановые зубы": "Увеличивает силу удара на +10 (постоянное улучшение)",
                "Плазменные колеса": "Увеличивает силу удара на +20 (космические технологии)",
                "Космический удар": "Увеличивает силу удара на +50 (финальное улучшение)"
            }
            
            tooltip_text = tooltips.get(self.upgrade["name"], "Нет описания")
            lines = []
            
            # Разбиваем текст на строки, если он слишком длинный
            words = tooltip_text.split(' ')
            current_line = []
            max_width = 250
            
            for word in words:
                test_line = ' '.join(current_line + [word])
                if tooltip_font.size(test_line)[0] <= max_width:
                    current_line.append(word)
                else:
                    lines.append(' '.join(current_line))
                    current_line = [word]
            lines.append(' '.join(current_line))
            
            # Рассчитываем размер подсказки
            line_height = tooltip_font.get_height()
            padding = 10
            tooltip_width = max(max_width, max(tooltip_font.size(line)[0] for line in lines)) + 2*padding
            tooltip_height = len(lines) * line_height + 2*padding
            
            # Позиционируем подсказку
            tooltip_x = self.rect.x
            tooltip_y = self.rect.y - tooltip_height - 10
            
            # Если подсказка выходит за верхний край, показываем снизу
            if tooltip_y < 0:
                tooltip_y = self.rect.y + self.rect.height + 10
            
            tooltip_rect = pygame.Rect(tooltip_x, tooltip_y, tooltip_width, tooltip_height)
            
            # Рисуем подсказку
            pygame.draw.rect(surface, COLORS["tooltip"], tooltip_rect, border_radius=5)
            pygame.draw.rect(surface, COLORS["primary"], tooltip_rect, 1, border_radius=5)
            
            # Рисуем текст
            for i, line in enumerate(lines):
                text_surface = tooltip_font.render(line, True, COLORS["text"])
                surface.blit(text_surface, (tooltip_rect.x + padding, tooltip_rect.y + padding + i*line_height))
        
    def buy(self, game_state):
        if game_state["coins"] >= self.upgrade['cost']:
            game_state["coins"] -= self.upgrade['cost']
            game_state["click_power"] += self.upgrade['power']
            self.level += 1
            self.upgrade['cost'] = int(self.upgrade['cost'] * 1.8)
            self.pulse = 1.0
            return True
        return False

class CoinEffect:
    def __init__(self, x, y, value):
        self.x = x
        self.y = y
        self.value = value
        self.life = 60
        self.alpha = 255
        self.y_vel = -1
        
    def update(self):
        self.y += self.y_vel
        self.y_vel *= 0.95
        self.life -= 1
        self.alpha = int(255 * (self.life / 60))
        
    def draw(self, surface):
        text = main_font.render(f"+{self.value}", True, (*COLORS["primary"], self.alpha))
        text_rect = text.get_rect(center=(self.x, self.y))
        surface.blit(text, text_rect)

class HamsterClickerGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = {
            "coins": 0,
            "click_power": 1,
            "total_clicks": 0,
            "coin_effects": [],
            "show_confirmation": False
        }
        
        self.hamster = AnimatedHamster(WIDTH // 3, HEIGHT // 2)
        
        self.upgrades = [
            {"name": "Боевые перчатки", "cost": 10, "power": 1},
            {"name": "Тренировочный лагерь", "cost": 50, "power": 2},
            {"name": "Стероидные семечки", "cost": 100, "power": 5},
            {"name": "Титановые зубы", "cost": 250, "power": 10},
            {"name": "Плазменные колеса", "cost": 500, "power": 20},
        ]
        
        self.upgrade_buttons = []
        button_width = 250
        button_height = 70
        start_y = 120
        spacing = 20
        
        for i, upgrade in enumerate(self.upgrades):
            self.upgrade_buttons.append(UpgradeButton(
                WIDTH - button_width - 20,
                start_y + i * (button_height + spacing),
                button_width,
                button_height,
                upgrade
            ))
        
        # Загружаем сохранение после создания всех кнопок
        self.load_game()
    
    def save_game(self):
        """Сохраняет текущий прогресс в файл"""
        save_data = {
            'coins': self.state['coins'],
            'click_power': self.state['click_power'],
            'total_clicks': self.state['total_clicks'],
            'upgrades': []
        }
        
        # Сохраняем уровни улучшений
        for button in self.upgrade_buttons:
            save_data['upgrades'].append({
                'name': button.upgrade['name'],
                'level': button.level,
                'cost': button.upgrade['cost']
            })
        
        with open('save.dat', 'wb') as f:
            pickle.dump(save_data, f)
    
    def load_game(self):
        """Загружает сохранённый прогресс из файла"""
        try:
            with open('save.dat', 'rb') as f:
                save_data = pickle.load(f)
                
                self.state['coins'] = save_data['coins']
                self.state['click_power'] = save_data['click_power']
                self.state['total_clicks'] = save_data['total_clicks']
                
                # Восстанавливаем улучшения
                for saved_upgrade, button in zip(save_data['upgrades'], self.upgrade_buttons):
                    if saved_upgrade['name'] == button.upgrade['name']:
                        button.level = saved_upgrade['level']
                        button.upgrade['cost'] = saved_upgrade['cost']
                        
        except (FileNotFoundError, EOFError, KeyError):
            # Если файла нет или он повреждён - начинаем новую игру
            self.state = {
                "coins": 0,
                "click_power": 1,
                "total_clicks": 0,
                "coin_effects": [],
                "show_confirmation": False
            }
            for button in self.upgrade_buttons:
                button.level = 0
                # Восстанавливаем базовую стоимость из первоначальных данных
                for upgrade in self.upgrades:
                    if upgrade['name'] == button.upgrade['name']:
                        button.upgrade['cost'] = upgrade['cost']
    
    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == QUIT:
                self.state["show_confirmation"] = True
                
            if event.type == pygame.USEREVENT:
                self.hamster.target_scale = 1.0
                
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                if self.state["show_confirmation"]:
                    if hasattr(self, 'yes_button') and self.yes_button.collidepoint(mouse_pos):
                        self.save_game()  # Сохраняем перед выходом
                        self.running = False
                    elif hasattr(self, 'no_button') and self.no_button.collidepoint(mouse_pos):
                        self.state["show_confirmation"] = False
                else:
                    hamster_rect = pygame.Rect(
                        self.hamster.x - self.hamster.size//2,
                        self.hamster.y - self.hamster.size//2,
                        self.hamster.size,
                        self.hamster.size
                    )
                    
                    if hamster_rect.collidepoint(mouse_pos):
                        self.hamster.click()
                        self.state["coins"] += self.state["click_power"]
                        self.state["total_clicks"] += 1
                        self.state["coin_effects"].append(
                            CoinEffect(mouse_pos[0], mouse_pos[1], self.state["click_power"])
                        )
                    
                    for button in self.upgrade_buttons:
                        if button.rect.collidepoint(mouse_pos):
                            button.buy(self.state)
    
    def update(self):
        self.hamster.update()
        
        for button in self.upgrade_buttons:
            button.hover = button.rect.collidepoint(pygame.mouse.get_pos())
            button.update()
            
        for effect in self.state["coin_effects"][:]:
            effect.update()
            if effect.life <= 0:
                self.state["coin_effects"].remove(effect)
    
    def draw(self):
        self.screen.blit(background_img, (0, 0))
        
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 50))
        self.screen.blit(overlay, (0, 0))
        
        pygame.draw.rect(self.screen, COLORS["panel"], (20, 20, 300, 120), border_radius=15)
        
        coins_text = main_font.render(f"Монеты: {self.state['coins']}", True, COLORS["text"])
        power_text = main_font.render(f"Сила удара: {self.state['click_power']}", True, COLORS["text"])
        clicks_text = main_font.render(f"Всего ударов: {self.state['total_clicks']}", True, COLORS["text"])
        
        self.screen.blit(coins_text, (40, 40))
        self.screen.blit(power_text, (40, 70))
        self.screen.blit(clicks_text, (40, 100))
        
        coin_stat_rect = coin_img.get_rect(center=(160, 55))
        self.screen.blit(coin_img, coin_stat_rect)
        
        self.hamster.draw(self.screen)
        
        for effect in self.state["coin_effects"]:
            effect.draw(self.screen)
        
        pygame.draw.rect(self.screen, COLORS["panel"], (WIDTH - 300, 20, 280, HEIGHT - 40), border_radius=15)
        shop_title = title_font.render("Арсенал", True, COLORS["primary"])
        self.screen.blit(shop_title, (WIDTH - 300 + (280 - shop_title.get_width()) // 2, 40))
        
        for button in self.upgrade_buttons:
            button.draw(self.screen)
            button.draw_tooltip(self.screen)  # Отрисовываем подсказки
        
        if self.state["show_confirmation"]:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))
            
            dialog_rect = pygame.Rect(WIDTH//2 - 200, HEIGHT//2 - 100, 400, 200)
            pygame.draw.rect(self.screen, COLORS["panel"], dialog_rect, border_radius=15)
            pygame.draw.rect(self.screen, COLORS["primary"], dialog_rect, 2, border_radius=15)
            
            title = title_font.render("Выход", True, COLORS["primary"])
            question = main_font.render("Прервать тренировку?", True, COLORS["text"])
            
            self.screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 70))
            self.screen.blit(question, (WIDTH//2 - question.get_width()//2, HEIGHT//2 - 20))
            
            self.yes_button = pygame.Rect(WIDTH//2 - 120, HEIGHT//2 + 40, 100, 50)
            self.no_button = pygame.Rect(WIDTH//2 + 20, HEIGHT//2 + 40, 100, 50)
            
            pygame.draw.rect(self.screen, COLORS["button_hover"] if self.yes_button.collidepoint(pygame.mouse.get_pos()) else COLORS["button"], 
                            self.yes_button, border_radius=10)
            pygame.draw.rect(self.screen, COLORS["primary"], self.yes_button, 2, border_radius=10)
            
            pygame.draw.rect(self.screen, COLORS["button_hover"] if self.no_button.collidepoint(pygame.mouse.get_pos()) else COLORS["button"], 
                            self.no_button, border_radius=10)
            pygame.draw.rect(self.screen, COLORS["primary"], self.no_button, 2, border_radius=10)
            
            yes_text = main_font.render("Да", True, COLORS["text"])
            no_text = main_font.render("Нет", True, COLORS["text"])
            
            self.screen.blit(yes_text, (self.yes_button.x + self.yes_button.width//2 - yes_text.get_width()//2, 
                            self.yes_button.y + self.yes_button.height//2 - yes_text.get_height()//2))
            self.screen.blit(no_text, (self.no_button.x + self.no_button.width//2 - no_text.get_width()//2, 
                            self.no_button.y + self.no_button.height//2 - no_text.get_height()//2))
        
        pygame.display.flip()
    
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = HamsterClickerGame()
    game.run()