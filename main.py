import pygame
import random
import os

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

# Загрузка звуков
pygame.mixer.music.load('sounds/soundtrack.mp3')  # Фоновая музыка
pygame.mixer.music.set_volume(0.05)
pygame.mixer.music.play(-1)

sound_coin = pygame.mixer.Sound("sounds/coins.mp3")  # Звук сбора монетки
sound_coin.set_volume(0.1)

sound_game_over = pygame.mixer.Sound("sounds/end_game.mp3")  # Звук проигрыша
sound_game_over.set_volume(0.1)

sound_checkpoint = pygame.mixer.Sound("sounds/points.mp3")  # Звук достижения контрольной точки
sound_checkpoint.set_volume(0.3)


# Сохранение рекорда
def save_highscore(score):
    with open("highscore.txt", "w") as f:
        f.write(str(score))


def load_highscore():
    try:
        with open("highscore.txt", "r") as f:
            return int(f.read())
    except:
        return 0


# Загрузка текстур
def load_textures(path, size, flip=False):
    textures = []
    for filename in sorted(os.listdir(path)):
        texture = pygame.image.load(os.path.join(path, filename))
        texture = pygame.transform.scale(texture, size)
        if flip:
            texture = pygame.transform.flip(texture, True, False)
        textures.append(texture)
    return textures


# Текстуры для анимаций
block_texture = pygame.transform.scale(pygame.image.load("sprites/platform.png"), (40, 40))
player_idle = [pygame.transform.scale(pygame.image.load("sprites/player.png"), (40, 40))]  # Основной спрайт
player_run_right = load_textures("sprites/animation", (40, 40))
player_run_left = load_textures("sprites/animation", (40, 40), flip=True)
enemy_texture = pygame.transform.scale(pygame.image.load("sprites/enemy.png"), (40, 40))
coin_texture = pygame.transform.scale(pygame.image.load("sprites/coin.png"), (20, 20))  # Текстура монетки
cloud_texture = pygame.image.load("sprites/background.png")  # Текстура облачков

# Загрузка текстур для прыжка
player_jump_idle = [pygame.transform.scale(pygame.image.load("sprites/jump_idle.png"), (40, 40))]  # Прыжок на месте
player_jump_move = [pygame.transform.scale(pygame.image.load("sprites/jump_move.png"), (40, 40))]  # Прыжок в движении

# Шрифт для счета и меню
font = pygame.font.Font("font/supermario_font.otf", 32)


# Класс игрока
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.animations = {
            "idle": player_idle,
            "right": player_run_right,
            "left": player_run_left,
            "jump_idle": player_jump_idle,  # Прыжок на месте
            "jump_move": player_jump_move,  # Прыжок в движении,
        }
        self.current_anim = "idle"
        self.anim_index = 0
        self.image = self.animations[self.current_anim][self.anim_index]
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 2, HEIGHT - 100)
        self.vel_y = 0
        self.vel_x = 0
        self.on_ground = False
        self.jump_power = -15
        self.speed = 5
        self.score = 0
        self.last_update = pygame.time.get_ticks()
        self.anim_delay = 100
        self.is_jumping = False  # Флаг для отслеживания прыжка
        self.facing_left = False  # Направление взгляда игрока (влево/вправо)

    def update(self):
        now = pygame.time.get_ticks()
        # Обновление анимации
        if now - self.last_update > self.anim_delay:
            self.last_update = now
            if not self.is_jumping:  # Обновляем анимацию только если не в прыжке
                self.anim_index = (self.anim_index + 1) % len(self.animations[self.current_anim])
                self.image = self.animations[self.current_anim][self.anim_index]

        # Гравитация
        self.vel_y += 0.5
        self.rect.y += self.vel_y

        # Движение по горизонтали
        self.rect.x += self.vel_x

        # Определение направления анимации
        if self.is_jumping:
            if self.vel_x == 0:  # Прыжок на месте
                self.current_anim = "jump_idle"
                self.image = self.animations["jump_idle"][0]
            else:  # Прыжок в движении
                self.current_anim = "jump_move"
                self.image = self.animations["jump_move"][0]
                if self.vel_x < 0:  # Если движется влево, отзеркаливаем текстуру
                    self.image = pygame.transform.flip(self.image, True, False)
        else:
            if self.vel_x > 0:
                self.current_anim = "right"
                self.facing_left = False
            elif self.vel_x < 0:
                self.current_anim = "left"
                self.facing_left = True
            else:
                self.current_anim = "idle"

        # Ограничение на выход за границы экрана
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH

    def jump(self):
        if self.on_ground:
            self.vel_y = self.jump_power
            self.on_ground = False
            self.is_jumping = True  # Устанавливаем флаг прыжка

    def move_left(self):
        self.vel_x = -self.speed

    def move_right(self):
        self.vel_x = self.speed

    def stop(self):
        self.vel_x = 0

    def check_ground(self):
        # Проверка, находится ли игрок на земле
        if self.vel_y == 0 and self.on_ground:
            self.is_jumping = False  # Сбрасываем флаг прыжка


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


# Класс монетки
class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = coin_texture
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self):
        pass


class CloudBackground:
    def __init__(self):
        self.cloud_image = cloud_texture
        self.cloud_width = self.cloud_image.get_width()
        self.cloud_height = self.cloud_image.get_height()

        # Создаем большое изображение фона (2x2 облака)
        self.bg_width = WIDTH * 2
        self.bg_height = HEIGHT * 2

        # Создаем поверхность с поддержкой альфа-канала
        self.background = pygame.Surface((self.bg_width, self.bg_height), pygame.SRCALPHA)

        # Заполняем фон облаками
        for x in range(0, self.bg_width, self.cloud_width):
            for y in range(0, self.bg_height, self.cloud_height):
                self.background.blit(self.cloud_image, (x, y))

        self.bg_x = 0
        self.bg_y = 0
        self.cloud_speed_x = 1
        self.cloud_speed_y = 0.1

    def update(self, player_y_velocity):
        # Движение фона
        self.bg_x -= self.cloud_speed_x
        self.bg_y += player_y_velocity * self.cloud_speed_y

        # Возврат фона, если он уходит за границы
        if self.bg_x + self.bg_width < 0:
            self.bg_x = 0
        if self.bg_y + self.bg_height < 0:
            self.bg_y = 0
        if self.bg_x > WIDTH:
            self.bg_x = -self.bg_width + WIDTH
        if self.bg_y > HEIGHT:
            self.bg_y = -self.bg_height + HEIGHT

    def draw(self, screen):
        # Отрисовка фона
        screen.blit(self.background, (self.bg_x, self.bg_y))
        # Если фон уходит за границы, отрисовываем его с другой стороны
        if self.bg_x < 0:
            screen.blit(self.background, (self.bg_x + self.bg_width, self.bg_y))
        if self.bg_y < 0:
            screen.blit(self.background, (self.bg_x, self.bg_y + self.bg_height))
        if self.bg_x < 0 and self.bg_y < 0:
            screen.blit(self.background, (self.bg_x + self.bg_width, self.bg_y + self.bg_height))


# Функция для генерации платформ и монеток
def generate_platforms(y_start, player_x):
    platforms = []
    coins = []
    y = y_start
    for _ in range(5):
        x = random.randint(max(0, player_x - 200), min(WIDTH - 120, player_x + 200))
        y -= random.randint(80, 120)
        width = random.randint(3, 5)
        platform = Platform(x, y, width)
        platforms.append(platform)

        # Добавляем монетку на платформу
        if random.random() < 0.5:  # 50% шанс появления монетки
            coin = Coin(x + random.randint(0, width * 40 - 20), y - 20)
            coins.append(coin)

    return platforms, coins


# Функция для отображения стартового меню
def start_menu(highscore):
    while True:
        screen.fill(WHITE)
        bg_loader = pygame.image.load("sprites/bg_loader.png")
        screen.blit(bg_loader, (0, 0))

        title_text = font.render("Mario Parkour", True, WHITE)
        hs_text = font.render(f"High Score: {highscore}", True, WHITE)
        start_text = font.render("Press S to Start", True, WHITE)
        quit_text = font.render("Press Q to Quit", True, WHITE)

        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 3))
        screen.blit(hs_text, (WIDTH // 2 - hs_text.get_width() // 2, HEIGHT // 2 - 50))
        screen.blit(start_text, (WIDTH // 2 - start_text.get_width() // 2, HEIGHT // 2))
        screen.blit(quit_text, (WIDTH // 2 - quit_text.get_width() // 2, HEIGHT // 2 + 50))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            keys = pygame.key.get_pressed()
            if keys[pygame.K_s]:
                return
            if keys[pygame.K_q]:
                pygame.quit()
                return


# Функция для отображения меню после проигрыша
def game_over_menu(score):
    while True:
        pygame.mixer.music.pause()
        bg_lose = pygame.image.load("sprites/bg_lose.png")
        screen.fill(WHITE)
        screen.blit(bg_lose, (0, 0))
        title_text = font.render("Game Over", True, WHITE)
        score_text = font.render(f"Score: {score}", True, WHITE)
        restart_text = font.render("Press R to Restart", True, WHITE)
        quit_text = font.render("Press Q to Quit", True, WHITE)

        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 3))
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2 - 50))
        screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2))
        screen.blit(quit_text, (WIDTH // 2 - quit_text.get_width() // 2, HEIGHT // 2 + 50))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            keys = pygame.key.get_pressed()
            if keys[pygame.K_r]:  # Перезапуск игры
                return True
            if keys[pygame.K_q]:  # Выйти из игры
                return False


# Основной игровой цикл
def main():
    pygame.mixer.music.unpause()
    # Создание групп спрайтов
    all_sprites = pygame.sprite.Group()
    platforms = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    coins = pygame.sprite.Group()  # Группа для монеток

    # Создание игрока
    player = Player()
    all_sprites.add(player)

    # Платформа под игроком
    start_platform = Platform(20, HEIGHT - 50, 19)  # Широкая платформа под игроком
    all_sprites.add(start_platform)
    platforms.add(start_platform)

    # Генерация начальных платформ и монеток
    platform_list, coin_list = generate_platforms(HEIGHT - 150, player.rect.x)
    all_sprites.add(platform_list)
    platforms.add(platform_list)
    all_sprites.add(coin_list)
    coins.add(coin_list)

    # Создание фона с облаками
    cloud_background = CloudBackground()

    running = True
    game_over = False
    camera_y = 0

    # Базовый шанс появления врага
    enemy_spawn_chance = 0.3  # 30% шанс появления врага

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

            # Обновление фона с облаками
            cloud_background.update(player.vel_y)

            # Проверка столкновений игрока с платформами
            hits = pygame.sprite.spritecollide(player, platforms, False)
            if hits:
                if player.vel_y > 0:  # Если игрок падает
                    player.rect.bottom = hits[0].rect.top
                    player.on_ground = True
                    player.vel_y = 0
                    player.check_ground()  # Проверка, находится ли игрок на земле

            # Проверка столкновений с монетками
            coins_collected = pygame.sprite.spritecollide(player, coins, True)
            if coins_collected:
                player.score += random.randint(10, 100)  # Добавляем очки за монетки
                sound_coin.play()  # Воспроизводим звук монетки

            # Проверка столкновений с врагами
            if pygame.sprite.spritecollide(player, enemies, False):
                game_over = True
                sound_game_over.play()  # Воспроизводим звук проигрыша

            # Проверка на проигрыш (падение за экран)
            if player.rect.top > HEIGHT:
                game_over = True
                sound_game_over.play()  # Воспроизводим звук проигрыша

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

            # Проверка на каждую тысячу
            if player.score % 1000 == 0 and player.score != 0:
                sound_checkpoint.play()  # Воспроизводим звук достижения контрольной точки

            # Генерация новых платформ и монеток
            if len(platforms) < 10:
                new_platforms, new_coins = generate_platforms(min([plat.rect.y for plat in platforms]), player.rect.x)
                all_sprites.add(new_platforms)
                platforms.add(new_platforms)
                all_sprites.add(new_coins)
                coins.add(new_coins)

                # Генерация врагов с учетом текущего счета
                current_enemy_spawn_chance = enemy_spawn_chance + (player.score // 100) * 0.01
                for plat in new_platforms:
                    if random.random() < current_enemy_spawn_chance:  # Шанс появления врага зависит от счета
                        enemy = Enemy(plat.rect.x + 30, plat.rect.y - 50)
                        all_sprites.add(enemy)
                        enemies.add(enemy)

            # Отрисовка
            screen.fill((135, 206, 235))  # Голубой фон неба
            cloud_background.draw(screen)  # Отрисовка облаков
            all_sprites.draw(screen)  # Отрисовка всех спрайтов

            # Отображение счета
            score_text = font.render(f"Score: {player.score}", True, BLACK)
            screen.blit(score_text, (10, 10))

            pygame.display.flip()

        else:
            if player.score > highscore:
                save_highscore(player.score)

            # Меню после проигрыша
            if game_over_menu(player.score):
                main()  # Перезапуск игры
            else:
                running = False  # Выход из игры

    pygame.quit()


# Запуск игры
if __name__ == "__main__":
    highscore = load_highscore()
    start_menu(highscore)
    main()  # Запускаем игру
