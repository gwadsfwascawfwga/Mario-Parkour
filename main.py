import pygame
import random

# Инициализация PyGame
pygame.init()

# Настройки окна
WIDTH, HEIGHT = 800, 600
FPS = 60

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Создание окна
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mario Parkour")
clock = pygame.time.Clock()

# Загрузка текстур
def load_texture(path, size):
    texture = pygame.image.load(path)
    return pygame.transform.scale(texture, size)

# Текстуры
block_texture = load_texture("sprites/platform.png", (40, 40))
player_texture = load_texture("sprites/player.png", (40, 40))
enemy_texture = load_texture("sprites/enemy.png", (40, 40))

# Шрифт для счета и меню
font = pygame.font.Font(None, 36)

# Класс игрока
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_texture
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 2, HEIGHT - 100)
        self.vel_y = 0
        self.vel_x = 0
        self.on_ground = False
        self.jump_power = -15
        self.speed = 5
        self.score = 0

    def update(self):
        # Гравитация
        self.vel_y += 0.5
        self.rect.y += self.vel_y

        # Движение по горизонтали
        self.rect.x += self.vel_x

        # Ограничение на выход за границы экрана
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH

    def jump(self):
        if self.on_ground:
            self.vel_y = self.jump_power
            self.on_ground = False

    def move_left(self):
        self.vel_x = -self.speed

    def move_right(self):
        self.vel_x = self.speed

    def stop(self):
        self.vel_x = 0

# Класс платформы
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width=3, height=1):
        super().__init__()
        self.width = width
        self.height = height
        self.image = pygame.Surface((40 * width, 40 * height))
        for i in range(width):
            for j in range(height):
                self.image.blit(block_texture, (i * 40, j * 40))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

# Класс врага
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = enemy_texture  # Используем текстуру для врага
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.vel_x = random.choice([-3, 3])
        self.flipped = True  # Флаг для отражения текстуры

    def update(self):
        self.rect.x += self.vel_x

        # Отражение текстуры при изменении направления
        if self.vel_x > 0 and not self.flipped:
            self.image = pygame.transform.flip(self.image, True, False)
            self.flipped = True
        elif self.vel_x < 0 and self.flipped:
            self.image = pygame.transform.flip(self.image, True, False)
            self.flipped = False

        # Ограничение на выход за границы экрана
        if self.rect.left < 0 or self.rect.right > WIDTH:
            self.vel_x *= -1

# Функция для генерации платформ
def generate_platforms(y_start):
    platforms = []
    y = y_start
    for _ in range(5):  # Генерация 5 платформ на каждом уровне
        x = random.randint(20, WIDTH - 250)  # Ограничение, чтобы платформы не выходили за экран
        y -= random.randint(80, 120)  # Расстояние между платформами от 80 до 120 пикселей
        width = random.randint(3, 5)  # Ширина платформы (3-5 блоков)
        platforms.append(Platform(x, y, width))
    return platforms

# Функция для отображения меню
def show_menu():
    screen.fill(WHITE)
    title_text = font.render("Mario Parkour", True, BLACK)
    restart_text = font.render("Press R to Restart", True, BLACK)
    quit_text = font.render("Press Q to Quit", True, BLACK)

    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 3))
    screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2))
    screen.blit(quit_text, (WIDTH // 2 - quit_text.get_width() // 2, HEIGHT // 2 + 50))

    pygame.display.flip()

# Основной игровой цикл
def main():
    # Создание групп спрайтов
    all_sprites = pygame.sprite.Group()
    platforms = pygame.sprite.Group()
    enemies = pygame.sprite.Group()

    # Создание игрока
    player = Player()
    all_sprites.add(player)

    # Генерация начальных платформ
    platform_list = [
        Platform(20, HEIGHT - 50, 19),  # Платформа под игроком
        *generate_platforms(HEIGHT - 150)  # Генерация остальных платформ
    ]
    all_sprites.add(platform_list)
    platforms.add(platform_list)

    running = True
    game_over = False
    camera_y = 0

    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if not game_over:
            # Управление игроком
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                player.move_left()
            elif keys[pygame.K_RIGHT]:
                player.move_right()
            else:
                player.stop()

            if keys[pygame.K_SPACE]:
                player.jump()

            # Обновление спрайтов
            all_sprites.update()

            # Проверка столкновений игрока с платформами
            hits = pygame.sprite.spritecollide(player, platforms, False)
            if hits:
                if player.vel_y > 0:  # Если игрок падает
                    player.rect.bottom = hits[0].rect.top
                    player.on_ground = True
                    player.vel_y = 0

            # Проверка столкновений с врагами
            if pygame.sprite.spritecollide(player, enemies, False):
                game_over = True

            # Проверка на проигрыш (падение за экран)
            if player.rect.top > HEIGHT:
                game_over = True

            # Движение камеры вверх
            if player.rect.top < HEIGHT // 3:
                camera_y = HEIGHT // 3 - player.rect.top
                player.score += 1
                for sprite in all_sprites:
                    sprite.rect.y += camera_y

            # Удаление объектов, ушедших за пределы экрана
            for sprite in all_sprites:
                if sprite.rect.top > HEIGHT:
                    sprite.kill()

            # Генерация новых платформ и врагов
            if len(platforms) < 10:  # Поддерживаем количество платформ
                new_platforms = generate_platforms(min([plat.rect.y for plat in platforms]) - 120)
                all_sprites.add(new_platforms)
                platforms.add(new_platforms)

                # Генерация врагов
                for plat in new_platforms:
                    if random.random() < 0.3:  # 30% шанс появления врага на платформе
                        enemy = Enemy(plat.rect.x + 30, plat.rect.y - 50)
                        all_sprites.add(enemy)
                        enemies.add(enemy)

            # Отрисовка
            screen.fill(WHITE)
            for sprite in all_sprites:
                screen.blit(sprite.image, sprite.rect)

            # Отображение счета
            score_text = font.render(f"Score: {player.score}", True, BLACK)
            screen.blit(score_text, (10, 10))

            pygame.display.flip()

        else:
            # Меню после проигрыша
            show_menu()
            keys = pygame.key.get_pressed()
            if keys[pygame.K_r]:  # Перезапуск игры
                main()
            if keys[pygame.K_q]:  # Выход из игры
                running = False

    pygame.quit()

# Запуск игры
if __name__ == "__main__":
    main()
