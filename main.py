import pygame
import sys
from pygame.locals import *

# Инициализация Pygame
pygame.init()

# Настройки окна
WIDTH, HEIGHT = 600, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hamster Clicker")

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GOLD = (255, 215, 0)

# Загрузка изображений (ВСТАВЬТЕ СВОИ ПУТИ К ФАЙЛАМ)
# Пример:
# hamster_img = pygame.image.load("hamster.png")
# background_img = pygame.image.load("background.jpg")
# coin_img = pygame.image.load("coin.png")

# Размеры и позиции
hamster_rect = pygame.Rect(WIDTH//2 - 50, HEIGHT//2 - 50, 100, 100)
shop_x = WIDTH - 200

# Игровые переменные
coins = 0
click_power = 1
confirm_exit = False

# Улучшения
upgrades = [
    {"name": "Усиленные лапки", "cost": 10, "power": 1},
    {"name": "Золотая клетка", "cost": 50, "power": 2},
    {"name": "Стероидный корм", "cost": 100, "power": 5}
]

class UpgradeButton:
    def __init__(self, y, upgrade):
        self.rect = pygame.Rect(shop_x + 10, y, 180, 50)
        self.upgrade = upgrade
        self.level = 0

    def draw(self, surface):
        pygame.draw.rect(surface, GOLD, self.rect, 2)
        font = pygame.font.Font(None, 24)
        text = font.render(f"{self.upgrade['name']} (Ур. {self.level}) - {self.upgrade['cost']}", True, GOLD)
        surface.blit(text, (self.rect.x + 5, self.rect.y + 5))

    def buy(self):
        global coins, click_power
        if coins >= self.upgrade['cost']:
            coins -= self.upgrade['cost']
            click_power += self.upgrade['power']
            self.level += 1
            self.upgrade['cost'] *= 2  # Увеличиваем стоимость для следующего уровня

buttons = [UpgradeButton(100 + i*100, upgrade) for i, upgrade in enumerate(upgrades)]

def draw_text(text, size, color, x, y):
    font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    screen.blit(text_surface, text_rect)

def exit_confirmation():
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if WIDTH//2 - 100 < mx < WIDTH//2 - 20 and HEIGHT//2 + 20 < my < HEIGHT//2 + 60:
                    return True
                elif WIDTH//2 + 20 < mx < WIDTH//2 + 100 and HEIGHT//2 + 20 < my < HEIGHT//2 + 60:
                    return False

        # Затемнение фона
        s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 180))
        screen.blit(s, (0, 0))

        # Окно подтверждения
        pygame.draw.rect(screen, BLACK, (WIDTH//2 - 150, HEIGHT//2 - 50, 300, 150))
        draw_text("Вы уверены, что хотите выйти?", 36, WHITE, WIDTH//2, HEIGHT//2 - 20)
        
        # Кнопки Да/Нет
        pygame.draw.rect(screen, GOLD, (WIDTH//2 - 100, HEIGHT//2 + 20, 80, 40))
        pygame.draw.rect(screen, GOLD, (WIDTH//2 + 20, HEIGHT//2 + 20, 80, 40))
        draw_text("Да", 30, BLACK, WIDTH//2 - 60, HEIGHT//2 + 40)
        draw_text("Нет", 30, BLACK, WIDTH//2 + 60, HEIGHT//2 + 40)

        pygame.display.update()

# Основной цикл
running = True
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            if exit_confirmation():
                running = False
        if event.type == MOUSEBUTTONDOWN:
            mx, my = event.pos
            
            # Проверка клика по хомяку
            if hamster_rect.collidepoint(mx, my):
                coins += click_power
            
            # Проверка клика по кнопкам улучшений
            for button in buttons:
                if button.rect.collidepoint(mx, my):
                    button.buy()
            
            # Проверка клика вне активных зон (ИСПРАВЛЕННЫЙ УЧАСТОК)
            if not (hamster_rect.collidepoint(mx, my) or any(btn.rect.collidepoint(mx, my) for btn in buttons)):
                if exit_confirmation():
                    running = False

    # Отрисовка фона
    screen.fill(BLACK)
    # screen.blit(background_img, (0, 0))  # Раскомментируйте если есть фон
    
    # Отрисовка хомяка
    pygame.draw.rect(screen, GOLD, hamster_rect)
    # screen.blit(hamster_img, (WIDTH//2 - 50, HEIGHT//2 - 50))  # Раскомментируйте если есть изображение
    
    # Отрисовка магазина
    pygame.draw.rect(screen, GOLD, (shop_x, 0, 200, HEIGHT), 2)
    
    # Отрисовка улучшений
    for button in buttons:
        button.draw(screen)
    
    # Отрисовка счётчика монет
    draw_text(f"Монеты: {coins}", 36, GOLD, 100, 50)
    draw_text(f"Сила клика: {click_power}", 36, GOLD, 100, 100)
    
    pygame.display.update()

pygame.quit()
sys.exit()