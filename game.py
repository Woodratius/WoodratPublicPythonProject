import pygame
import sys
import math
from enum import Enum

# Инициализация Pygame
pygame.init()

# Константы
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 64
GRID_WIDTH = 8
GRID_HEIGHT = 8

# Цвета
BACKGROUND = (40, 44, 52)
GRID_COLOR = (86, 98, 112)
CUBE_COLORS = {
    1: (255, 107, 107),  # Красный
    2: (255, 206, 107),  # Оранжевый
    3: (255, 255, 107),  # Желтый
    4: (107, 255, 107),  # Зеленый
    5: (107, 206, 255),  # Голубой
    6: (107, 107, 255),  # Синий
    7: (206, 107, 255),  # Фиолетовый
}


class Cube:
    def __init__(self, level=1):
        self.level = level
        self.color = CUBE_COLORS.get(level, (200, 200, 200))
        self.selected = False

    def can_merge_with(self, other):
        return self.level == other.level

    def merge(self):
        """Объединение кубиков - увеличивает уровень"""
        self.level += 1
        self.color = CUBE_COLORS.get(self.level, (200, 200, 200))


class IsometricGrid:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = [[None for _ in range(height)] for _ in range(width)]
        self.selected_cube = None

    def is_valid_position(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height

    def add_cube(self, x, y, cube):
        if self.is_valid_position(x, y) and self.grid[x][y] is None:
            self.grid[x][y] = cube
            return True
        return False

    def remove_cube(self, x, y):
        if self.is_valid_position(x, y):
            cube = self.grid[x][y]
            self.grid[x][y] = None
            return cube
        return None

    def move_cube(self, from_x, from_y, to_x, to_y):
        if not self.is_valid_position(from_x, from_y) or not self.is_valid_position(to_x, to_y):
            return False

        cube = self.grid[from_x][from_y]
        target = self.grid[to_x][to_y]

        if cube is None:
            return False

        # Если целевая ячейка пуста - просто перемещаем
        if target is None:
            self.grid[from_x][from_y] = None
            self.grid[to_x][to_y] = cube
            return True

        # Если кубики можно объединить
        if cube.can_merge_with(target):
            target.merge()
            self.grid[from_x][from_y] = None
            return True

        return False

    def get_cube_at_screen_pos(self, screen_x, screen_y):
        """Преобразование экранных координат в координаты сетки"""
        # Смещение для центрирования сетки
        offset_x = SCREEN_WIDTH // 2
        offset_y = 100

        # Обратное преобразование изометрических координат
        cart_x = (screen_x - offset_x) / TILE_SIZE + (screen_y - offset_y) / (TILE_SIZE / 2)
        cart_y = (screen_y - offset_y) / (TILE_SIZE / 2) - (screen_x - offset_x) / TILE_SIZE

        grid_x = int(cart_x)
        grid_y = int(cart_y)

        if self.is_valid_position(grid_x, grid_y):
            return grid_x, grid_y, self.grid[grid_x][grid_y]

        return None, None, None

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y, cube = self.grid.get_cube_at_screen_pos(*event.pos)

                if event.button == 1:  # Левая кнопка мыши
                    if cube is not None:
                        # Если кубик уже выбран, снимаем выделение
                        if cube.selected:
                            cube.selected = False
                            self.grid.selected_cube = None
                            self.selected_pos = None
                        else:
                            # Снимаем выделение с предыдущего кубика
                            if self.grid.selected_cube:
                                self.grid.selected_cube.selected = False

                            # Выбираем новый кубик
                            cube.selected = True
                            self.grid.selected_cube = cube
                            self.selected_pos = (x, y)

                    # Перемещаем выбранный кубик, если позиция свободна
                    elif self.grid.selected_cube and x is not None:
                        from_x, from_y = self.selected_pos
                        if self.grid.move_cube(from_x, from_y, x, y):
                            self.grid.selected_cube.selected = False
                            self.grid.selected_cube = None
                            self.selected_pos = None

                elif event.button == 3:  # Правая кнопка мыши
                    self.grid.spawn_random_cube()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:  # Рестарт
                    self.grid = IsometricGrid(GRID_WIDTH, GRID_HEIGHT)
                    for _ in range(5):
                        self.grid.spawn_random_cube()

        return True
    def spawn_random_cube(self):
        """Создает случайный кубик в случайной пустой ячейке"""
        import random
        empty_cells = []

        for x in range(self.width):
            for y in range(self.height):
                if self.grid[x][y] is None:
                    empty_cells.append((x, y))

        if empty_cells:
            x, y = random.choice(empty_cells)
            # 80% шанс создать кубик уровня 1, 20% - уровня 2
            level = 1 if random.random() < 0.8 else 2
            self.add_cube(x, y, Cube(level))
            return True
        return False


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Изометрическая игра с кубиками")
        self.clock = pygame.time.Clock()
        self.grid = IsometricGrid(GRID_WIDTH, GRID_HEIGHT)
        self.font = pygame.font.Font(None, 24)

        # Заполняем начальными кубиками
        for _ in range(5):
            self.grid.spawn_random_cube()

    def draw_isometric_grid(self):
        """Отрисовка изометрической сетки"""
        offset_x = SCREEN_WIDTH // 2
        offset_y = 100

        for x in range(self.grid.width):
            for y in range(self.grid.height):
                # Преобразование в изометрические координаты
                iso_x = offset_x + (x - y) * TILE_SIZE
                iso_y = offset_y + (x + y) * (TILE_SIZE // 2)

                # Рисуем плитку
                points = [
                    (iso_x, iso_y),
                    (iso_x + TILE_SIZE, iso_y + TILE_SIZE // 2),
                    (iso_x, iso_y + TILE_SIZE),
                    (iso_x - TILE_SIZE, iso_y + TILE_SIZE // 2)
                ]

                pygame.draw.polygon(self.screen, GRID_COLOR, points, 1)

    def draw_cube(self, x, y, cube):
        """Отрисовка кубика в изометрической проекции"""
        offset_x = SCREEN_WIDTH // 2
        offset_y = 100

        iso_x = offset_x + (x - y) * TILE_SIZE
        iso_y = offset_y + (x + y) * (TILE_SIZE // 2)

        # Размер кубика зависит от его уровня
        size_factor = 0.3 + (cube.level - 1) * 0.1
        cube_height = int(TILE_SIZE * size_factor)

        # Верхняя грань кубика
        top_points = [
            (iso_x, iso_y - cube_height),
            (iso_x + TILE_SIZE, iso_y + TILE_SIZE // 2 - cube_height),
            (iso_x, iso_y + TILE_SIZE - cube_height),
            (iso_x - TILE_SIZE, iso_y + TILE_SIZE // 2 - cube_height)
        ]

        # Боковые грани
        left_face = [
            (iso_x - TILE_SIZE, iso_y + TILE_SIZE // 2 - cube_height),
            (iso_x - TILE_SIZE, iso_y + TILE_SIZE // 2),
            (iso_x, iso_y + TILE_SIZE),
            (iso_x, iso_y + TILE_SIZE - cube_height)
        ]

        right_face = [
            (iso_x + TILE_SIZE, iso_y + TILE_SIZE // 2 - cube_height),
            (iso_x + TILE_SIZE, iso_y + TILE_SIZE // 2),
            (iso_x, iso_y + TILE_SIZE),
            (iso_x, iso_y + TILE_SIZE - cube_height)
        ]

        # Рисуем грани с разными оттенками для 3D эффекта
        dark_color = tuple(max(0, c - 40) for c in cube.color)
        darker_color = tuple(max(0, c - 80) for c in cube.color)

        pygame.draw.polygon(self.screen, darker_color, left_face)  # Левая грань
        pygame.draw.polygon(self.screen, dark_color, right_face)  # Правая грань
        pygame.draw.polygon(self.screen, cube.color, top_points)  # Верхняя грань

        # Контуры
        pygame.draw.polygon(self.screen, (0, 0, 0), top_points, 1)
        pygame.draw.polygon(self.screen, (0, 0, 0), left_face, 1)
        pygame.draw.polygon(self.screen, (0, 0, 0), right_face, 1)

        # Отображаем уровень кубика
        if cube.level > 1:
            level_text = self.font.render(str(cube.level), True, (255, 255, 255))
            text_rect = level_text.get_rect(center=(iso_x, iso_y - cube_height // 2))
            self.screen.blit(level_text, text_rect)

        # Выделение выбранного кубика
        if cube.selected:
            highlight_points = [
                (iso_x, iso_y - cube_height - 2),
                (iso_x + TILE_SIZE, iso_y + TILE_SIZE // 2 - cube_height - 2),
                (iso_x, iso_y + TILE_SIZE - cube_height - 2),
                (iso_x - TILE_SIZE, iso_y + TILE_SIZE // 2 - cube_height - 2)
            ]
            pygame.draw.polygon(self.screen, (255, 255, 255), highlight_points, 3)

    def draw_ui(self):
        """Отрисовка пользовательского интерфейса"""
        # Инструкции
        instructions = [
            "ЛКМ - выбрать/переместить кубик",
            "ПКМ - спавн нового кубика",
            "R - рестарт игры"
        ]

        for i, text in enumerate(instructions):
            text_surface = self.font.render(text, True, (255, 255, 255))
            self.screen.blit(text_surface, (10, 10 + i * 30))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Левая кнопка мыши
                    x, y, cube = self.grid.get_cube_at_screen_pos(*event.pos)
                    if cube is not None:
                        # Если кубик уже выбран, снимаем выделение
                        if cube.selected:
                            cube.selected = False
                            self.grid.selected_cube = None
                        else:
                            # Снимаем выделение с предыдущего кубика
                            if self.grid.selected_cube:
                                self.grid.selected_cube.selected = False

                            # Выбираем новый кубик
                            cube.selected = True
                            self.grid.selected_cube = cube
                            self.selected_pos = (x, y)
                    elif self.grid.selected_cube and x is not None:
                        # Пытаемся переместить выбранный кубик
                        from_x, from_y = self.selected_pos
                        if self.grid.move_cube(from_x, from_y, x, y):
                            self.grid.selected_cube.selected = False
                            self.grid.selected_cube = None

                elif event.button == 3:  # Правая кнопка мыши
                    self.grid.spawn_random_cube()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:  # Рестарт
                    self.grid = IsometricGrid(GRID_WIDTH, GRID_HEIGHT)
                    for _ in range(5):
                        self.grid.spawn_random_cube()

        return True

    def run(self):
        running = True
        while running:
            running = self.handle_events()

            # Отрисовка
            self.screen.fill(BACKGROUND)
            self.draw_isometric_grid()

            # Отрисовка всех кубиков
            for x in range(self.grid.width):
                for y in range(self.grid.height):
                    cube = self.grid.grid[x][y]
                    if cube:
                        self.draw_cube(x, y, cube)

            self.draw_ui()

            pygame.display.flip()
            self.clock.tick(60)


if __name__ == "__main__":
    game = Game()
    game.run()
    pygame.quit()
    sys.exit()