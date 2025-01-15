import pygame
import random

# Initialize pygame
pygame.init()

# Define constants
SCREEN_WIDTH = 300
SCREEN_HEIGHT = 600
BLOCK_SIZE = 30
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Tetris')

# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
PURPLE = (128, 0, 128)
RED = (255, 0, 0)

# Shape formats
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[0, 1, 0], [1, 1, 1]],  # T
    [[1, 1, 0], [0, 1, 1]],  # S
    [[0, 1, 1], [1, 1, 0]],  # Z
    [[1, 0, 0], [1, 1, 1]],  # J
    [[0, 0, 1], [1, 1, 1]],  # L
]

SHAPES_COLORS = [CYAN, YELLOW, PURPLE, GREEN, RED, BLUE, ORANGE]

class Tetris:
    def __init__(self):
        self.board = [[BLACK for _ in range(10)] for _ in range(20)]
        self.game_over = False
        self.current_piece = None
        self.current_color = None
        self.current_position = (0, 0)
        self.clock = pygame.time.Clock()

    def check_collision(self, shape, offset):
        off_x, off_y = offset
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    try:
                        if self.board[y + off_y][x + off_x] != BLACK:
                            return True
                    except IndexError:
                        return True
        return False

    def rotate(self, shape):
        return [list(row) for row in zip(*shape[::-1])]

    def freeze(self):
        shape = self.current_piece
        off_x, off_y = self.current_position
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    self.board[y + off_y][x + off_x] = self.current_color

    def clear_lines(self):
        new_board = [row for row in self.board if any(cell == BLACK for cell in row)]
        lines_cleared = 20 - len(new_board)
        new_board = [[BLACK] * 10] * lines_cleared + new_board
        self.board = new_board

    def new_piece(self):
        shape_idx = random.randint(0, len(SHAPES) - 1)
        self.current_piece = SHAPES[shape_idx]
        self.current_color = SHAPES_COLORS[shape_idx]
        self.current_position = (3, 0)

        if self.check_collision(self.current_piece, self.current_position):
            self.game_over = True

    def draw_board(self):
        for y in range(20):
            for x in range(10):
                pygame.draw.rect(SCREEN, self.board[y][x], (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
                pygame.draw.rect(SCREEN, WHITE, (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 1)

    def draw_piece(self):
        shape = self.current_piece
        off_x, off_y = self.current_position
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(SCREEN, self.current_color, ((off_x + x) * BLOCK_SIZE, (off_y + y) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))

    def move_piece(self, dx, dy):
        new_pos = (self.current_position[0] + dx, self.current_position[1] + dy)
        if not self.check_collision(self.current_piece, new_pos):
            self.current_position = new_pos
            return True
        return False

    def run(self):
        while not self.game_over:
            SCREEN.fill(BLACK)

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_over = True
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.move_piece(-1, 0)
                    elif event.key == pygame.K_RIGHT:
                        self.move_piece(1, 0)
                    elif event.key == pygame.K_DOWN:
                        self.move_piece(0, 1)
                    elif event.key == pygame.K_UP:
                        rotated = self.rotate(self.current_piece)
                        if not self.check_collision(rotated, self.current_position):
                            self.current_piece = rotated

            if not self.move_piece(0, 1):
                self.freeze()
                self.clear_lines()
                self.new_piece()

            # Draw everything
            self.draw_board()
            self.draw_piece()

            pygame.display.update()
            self.clock.tick(10)

        pygame.quit()


if __name__ == '__main__':
    game = Tetris()
    game.new_piece()
    game.run()