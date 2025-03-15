import pygame
import random
import sys
import time

# Initialize Pygame
pygame.init()

# Colors
RED = (255, 0, 0)  # RGB for Red
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PINK = (255, 192, 203)  # Light pink for card backs
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Adventure Time Memory Game")

# Load background music
try:
    pygame.mixer.music.load("Musica Hora.mpeg")  # Replace with your music file
    pygame.mixer.music.set_volume(0.5)
except pygame.error as e:
    print(f"Error loading music: {e}")

# Load images
icon_paths = [
    "src/fin.jpg", "src/jake.jpg", "src/jujuba.jpg", "src/marcelinne.jpg",
    "src/princesafogo.jpg", "src/caroço.jpg", "src/Ricardio.jpg",
    "src/menta.jpg", "src/rei gelado.jpg", "src/canelinha.jpg",
    "src/gunther.jpg", "src/Angry lemongrab.jpg", "src/simon.webp",
    "src/rei da noitosfera.jpg", "src/lady iris.jpg"
]
icons = []
for path in icon_paths:
    try:
        icon = pygame.image.load(path)
        icons.append(icon)
    except pygame.error as e:
        print(f"Error loading image {path}: {e}")

# Ensure all icons have pairs
icons = icons * 2  # Duplicate the list to create pairs

# Load background image for main menu
try:
    background_image = pygame.image.load("src/tela de inicio hora de aventura.jpg")
    background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
except pygame.error as e:
    print(f"Error loading background image: {e}")
    background_image = None

# Function to shuffle icons
def shuffle_icons():
    random.shuffle(icons)
    return icons

class MemoryGame:
    def __init__(self, rows, cols, mode):
        self.rows = rows
        self.cols = cols
        self.grid = [[None for _ in range(cols)] for _ in range(rows)]
        self.selected = []
        self.matched = []
        self.mode = mode
        self.moves = 0
        self.score = 0
        self.start_time = pygame.time.get_ticks()
        self.card_width = SCREEN_WIDTH // self.cols - 10
        self.card_height = SCREEN_HEIGHT // self.rows - 10
        self.reset_grid()

    def reset_grid(self):
        shuffled_icons = shuffle_icons()
        index = 0
        for i in range(self.rows):
            for j in range(self.cols):
                self.grid[i][j] = shuffled_icons[index]
                index += 1

    def draw_grid(self):
        screen.fill(WHITE)
        for i in range(self.rows):
            for j in range(self.cols):
                x = j * (self.card_width + 10) + 5
                y = i * (self.card_height + 10) + 5
                if (i, j) in self.matched or (i, j) in self.selected:
                    screen.blit(pygame.transform.scale(self.grid[i][j], (self.card_width, self.card_height)), (x, y))
                else:
                    pygame.draw.rect(screen, BLACK, (x, y, self.card_width, self.card_height))
                    pygame.draw.rect(screen, PINK, (x + 2, y + 2, self.card_width - 4, self.card_height - 4))  # Inner card color
        pygame.display.flip()

    def check_match(self):
        time.sleep(0.5)
        if len(self.selected) == 2:
            if self.grid[self.selected[0][0]][self.selected[0][1]] == self.grid[self.selected[1][0]][self.selected[1][1]]:
                self.matched.extend(self.selected)
                self.score += 10  # Increase score for a match
            self.selected = []
            self.moves += 1

    def check_game_over(self):
        return len(self.matched) == self.rows * self.cols

    def game_loop(self):
        clock = pygame.time.Clock()
        running = True
        paused = False

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if not paused:
                        if len(self.selected) < 2:
                            mouse_x, mouse_y = event.pos
                            row = (mouse_y - 5) // (self.card_height + 10)
                            col = (mouse_x - 5) // (self.card_width + 10)
                            if 0 <= row < self.rows and 0 <= col < self.cols:
                                if (row, col) not in self.selected and (row, col) not in self.matched:
                                    self.selected.append((row, col))
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:  # Pause the game
                        paused = not paused
                    elif event.key == pygame.K_r:  # Restart the game
                        self.reset_grid()
                        self.selected = []
                        self.matched = []
                        self.moves = 0
                        self.score = 0
                        self.start_time = pygame.time.get_ticks()
                    elif event.key == pygame.K_m:  # Return to main menu
                        return

            if not paused:
                self.draw_grid()
                self.check_match()

                if self.check_game_over():
                    self.show_game_over()
                    return

                if self.mode == "time":
                    elapsed_time = (pygame.time.get_ticks() - self.start_time) // 1000
                    if elapsed_time >= 60:  # Time limit of 60 seconds
                        self.show_game_over()
                        return

            clock.tick(30)

    def show_game_over(self):
        elapsed_time = (pygame.time.get_ticks() - self.start_time) // 1000
        result_message = f"Game Over!\nMoves: {self.moves}\nScore: {self.score}\nTime: {elapsed_time} seconds" if self.mode == "time" else f"Game Over!\nMoves: {self.moves}\nScore: {self.score}"
        print(result_message)  # Display in console or use a Pygame message box
        # You can also render this message on the screen using Pygame fonts

def draw_menu():
    if background_image:
        screen.blit(background_image, (0, 0))
    else:
        screen.fill(WHITE)

    font = pygame.font.Font(None, 74)
    title = font.render("Adventure Time", True, RED)
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))

    font = pygame.font.Font(None, 50)
    start_button = font.render("Start Game", True, PINK)
    screen.blit(start_button, (SCREEN_WIDTH // 2 - start_button.get_width() // 2, 300))

    quit_button = font.render("Quit", True, PINK)
    screen.blit(quit_button, (SCREEN_WIDTH // 2 - quit_button.get_width() // 2, 400))

    pygame.display.flip()

def draw_difficulty_menu():
    if background_image:
        screen.blit(background_image, (0, 0))
    else:
        screen.fill(WHITE)

    font = pygame.font.Font(None, 74)
    title = font.render("Select Difficulty", True, RED)
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))

    font = pygame.font.Font(None, 50)
    easy_button = font.render("Easy (3x4)", True, PINK)
    screen.blit(easy_button, (SCREEN_WIDTH // 2 - easy_button.get_width() // 2, 250))

    medium_button = font.render("Medium (4x5)", True, PINK)
    screen.blit(medium_button, (SCREEN_WIDTH // 2 - medium_button.get_width() // 2, 350))

    hard_button = font.render("Hard (5x6)", True, PINK)
    screen.blit(hard_button, (SCREEN_WIDTH // 2 - hard_button.get_width() // 2, 450))

    pygame.display.flip()

def main_menu():
    pygame.mixer.music.play(-1)  # Play background music on loop
    while True:
        draw_menu()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                if SCREEN_WIDTH // 2 - 100 <= mouse_x <= SCREEN_WIDTH // 2 + 100:
                    if 300 <= mouse_y <= 350:
                        select_difficulty()
                    elif 400 <= mouse_y <= 450:
                        pygame.quit()
                        sys.exit()

def select_difficulty():
    while True:
        draw_difficulty_menu()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                if SCREEN_WIDTH // 2 - 100 <= mouse_x <= SCREEN_WIDTH // 2 + 100:
                    if 250 <= mouse_y <= 300:
                        start_game(3, 4, "practice")  # Easy
                    elif 350 <= mouse_y <= 400:
                        start_game(4, 5, "practice")  # Medium
                    elif 450 <= mouse_y <= 500:
                        start_game(5, 6, "practice")  # Hard

def start_game(rows, cols, mode):
    game = MemoryGame(rows, cols, mode)
    game.game_loop()
    main_menu()  # Return to main menu after game ends

if __name__ == "__main__":
    main_menu()