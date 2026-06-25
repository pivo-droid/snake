import pygame 
from sys import exit # выход из игры
import random # для генерации рандомных чисел, понадобится для генерации еды в разных местах
import json # для сохранения рекордов в файл
from pathlib import Path # для работы с путями к файлам, понадобится для сохранения рекордов в файл

# определяем папку где находится сам скрипт игры
game_folder = Path(__file__).parent # берём папку текущего файла
scores_file = game_folder / "scores.json" # файл рекордов в этой же папке

TILE_SIZE = 25 # размер клетки еды
ROWS = 25 # количество строк, по которым будет двигаться змейка, можно менять, но нужно следить за тем, чтобы количество строк и столбцов было одинаковым, иначе могут возникать баги
COLUMNS = ROWS # количество столбцов, по которым будет двигаться змейка, можно менять, но нужно следить за тем, чтобы количество строк и столбцов было одинаковым, иначе могут возникать баги
GAME_WIDTH = TILE_SIZE * COLUMNS # ширина игрового поля, зависит от количества столбцов и размера клетки еды
GAME_HEIGHT = TILE_SIZE * ROWS # высота игрового поля, зависит от количества строк и размера клетки еды

# скорость змейки: начальная, максимальная и сколько еды нужно съесть, чтобы увеличить скорость
INITIAL_GAME_SPEED = 5 # начальная скорость, игра будет медленнее в начале
MAX_GAME_SPEED = 16 # максимальная скорость, до которой разгоняется игра
FOOD_PER_SPEED_UP = 3 # скорость растёт не за каждую еду, а после каждых трёх

pygame.init() #инициализация игры
window = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT)) # создание окна передав значения высоты и ширины
pygame.display.set_caption("Snake") # название окна
clock = pygame.time.Clock() # создание часов для управления фпс, часы это объект, который позволяет отслеживать время и управлять частотой кадров в игре
font = pygame.font.Font(None, 56) # шрифт для текста Game Over
font_small = pygame.font.Font(None, 36) # маленький шрифт для счёта и рекордов
game_over = False # отмажка, что игра закончилась
paused = False # переменная для паузы
score = 0 # счёт игрока (сколько еды съела змейка)
best_score = 0 # лучший счёт всех времён
game_speed = INITIAL_GAME_SPEED # скорость игры (чем больше, тем быстрее)
score_saved = False # флаг чтобы сохранить рекорд только один раз

def load_scores():
    # загружаем рекорды из файла если он существует
    if scores_file.exists():
        try:
            with open(scores_file, "r") as f:
                return json.load(f)
        except:
            return []
    return []

def save_scores(scores):
    # сохраняем только топ 5 рекордов в файл
    scores = get_top_scores(scores)
    with open(scores_file, "w") as f:
        json.dump(scores, f)

def get_top_scores(scores):
    # берём топ 5 лучших рекордов
    sorted_scores = sorted(scores, reverse=True)
    return sorted_scores[:5]

def get_random(limit):
    return random.randint(0, limit-1) * TILE_SIZE # возвращаем случайное число в пределах от 0 до limit-1, умноженное на размер клетки еды, чтобы еда появлялась в пределах игрового поля

def set_direction(new_vel):
    # устанавливаем направление движения змейки, запрещая разворот на 180 градусов
    global snake_velocity
    # если змейка длиной 1 разворот возможен, иначе запрещаем противоположное направление
    if len(snake) <= 1 or snake_velocity != (-new_vel[0], -new_vel[1]):
        snake_velocity = new_vel

def update_game_speed():
    global game_speed
    # считаем скорость по счёту, скорость растёт медленнее и ограничивается 16
    game_speed = min(MAX_GAME_SPEED, INITIAL_GAME_SPEED + score // FOOD_PER_SPEED_UP)


def reset_game():
    global food, snake, snake_velocity, game_over, score, paused, score_saved, game_speed
    # сбрасываем параметры игры: еду, змейку, скорость и состояние Game Over
    food = pygame.Rect(get_random(COLUMNS), get_random(ROWS), TILE_SIZE, TILE_SIZE)
    snake = [pygame.Rect(get_random(COLUMNS), get_random(ROWS), TILE_SIZE, TILE_SIZE)]
    snake_velocity = (0, 0)
    game_over = False
    paused = False # после перезагрузки пауза отключена
    score = 0 # очищаем счёт для новой игры
    game_speed = INITIAL_GAME_SPEED # возвращаем начальную скорость
    score_saved = False # очищаем флаг сохранения

# загружаем рекорды при запуске
all_scores = load_scores()
best_score = max(all_scores) if all_scores else 0

print(f"Рекорды сохраняются в: {scores_file}") # показываем в консоли куда сохраняется файл

reset_game() # инициализация игры при запуске

#игровой цикл
while True: # цикл для игры до тех пор пока игра работает
    for event in pygame.event.get(): # для обработки всех действий в игре
        if event.type == pygame.QUIT: # если игрок нажимает на крестик
            pygame.quit() # выход из игры
            exit() # выход из программы полностью + выше есть импорт связанный с этим

        if event.type == pygame.KEYDOWN: # игрок нажал на клавишу
            if game_over:
                # если игра завершена, R - новый запуск, Q - выход
                if event.key == pygame.K_r:
                    reset_game()
                elif event.key == pygame.K_q:
                    pygame.quit()
                    exit()
            else:
                # если игра идёт, ESC ставит на паузу
                if event.key == pygame.K_ESCAPE:
                    paused = not paused # включаем или выключаем паузу
                elif not paused: # управление работает только если не на паузе
                    if event.key in (pygame.K_UP, pygame.K_w):
                        set_direction((0, -TILE_SIZE))
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        set_direction((0, TILE_SIZE))
                    elif event.key in (pygame.K_LEFT, pygame.K_a):
                        set_direction((-TILE_SIZE, 0))
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        set_direction((TILE_SIZE, 0))

    if not game_over and not paused: # игра идёт только если не game over и не пауза
        if snake[0].center == food.center:
            snake.append(snake[-1].copy())
            score += 1 # увеличиваем счёт на 1 когда съели еду
            update_game_speed() # обновляем скорость после нужного количества еды
            food = pygame.Rect(get_random(COLUMNS), get_random(ROWS), TILE_SIZE, TILE_SIZE)

        # движение змейки
        for i in range(len(snake)-1, 0, -1):
            snake[i] = snake[i-1].copy()
        snake[0].move_ip(snake_velocity) # двигаем змейку

        # проверка выхода за границы
        if (snake[0].left < 0 or snake[0].right > GAME_WIDTH
                or snake[0].top < 0 or snake[0].bottom > GAME_HEIGHT):
            game_over = True # если голова за границей, ставим Game Over

        # проверка столкновения с самой собой (если голова коснулась любой части хвоста)
        for segment in snake[1:]:
            if snake[0].center == segment.center:
                game_over = True # если врезались в себя, ставим Game Over

    # если игра закончилась, сохраняем рекорд только один раз
    if game_over and not score_saved:
        all_scores.append(score) # добавляем текущий счёт в список рекордов
        save_scores(all_scores) # сохраняем рекорды в файл
        best_score = max(all_scores) # обновляем лучший счёт
        print(f"Файл сохранён! Путь: {scores_file}") # показываем что файл сохранился
        score_saved = True # отмечаем что уже сохранили

    # отрисовка
    window.fill("black") # закрашиваем окно черным цветом
    pygame.draw.rect(window, "red", food) # рисуем еду на поле, передаем окно, цвет и координаты еды
    for snake_part in snake:
        pygame.draw.rect(window, "green", snake_part) # рисуем змейку на поле, передаем окно, цвет и координаты каждой части змейки

    # показываем текущий счёт в левом верхнем углу
    score_text = font_small.render(f"Score: {score}", True, "white")
    window.blit(score_text, (10, 10))

    # показываем лучший счёт рядом со счётом
    best_text = font_small.render(f"Best: {best_score}", True, "yellow")
    window.blit(best_text, (10, 50))

    # показываем скорость игры
    speed_text = font_small.render(f"Speed: {game_speed}", True, "cyan")
    window.blit(speed_text, (10, 90))

    # если пауза включена, показываем сообщение
    if paused and not game_over:
        pause_text = font_small.render("PAUSED (ESC to resume)", True, "orange")
        window.blit(pause_text, (GAME_WIDTH//2 - 150, GAME_HEIGHT//2))

    if game_over:
        # отрисовка экрана Game Over поверх игры
        text = font.render("Game Over", True, "white")
        restart = font.render("Press R to restart", True, "white")
        window.blit(text, text.get_rect(center=(GAME_WIDTH//2, GAME_HEIGHT//2 - 30)))
        window.blit(restart, restart.get_rect(center=(GAME_WIDTH//2, GAME_HEIGHT//2 + 30)))

        # показываем топ 5 рекордов когда игра закончилась
        top_scores = get_top_scores(all_scores)
        top_text = font_small.render("Top 5 Scores:", True, "lightgreen")
        window.blit(top_text, (GAME_WIDTH//2 - 80, GAME_HEIGHT//2 + 90))

        for i, sc in enumerate(top_scores):
            rank_text = font_small.render(f"{i+1}. {sc}", True, "lightgreen")
            window.blit(rank_text, (GAME_WIDTH//2 - 60, GAME_HEIGHT//2 + 130 + i * 30))

    pygame.display.update() # обновление окна
    clock.tick(game_speed) # ограничение фпс по скорости игры