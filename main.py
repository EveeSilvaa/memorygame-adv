import pygame
import random
import sys
import time
import pyttsx3  # For voice synthesis
import os
from pygame import mixer

# Initialize Pygame
pygame.init()

# Initialize text-to-speech engine
try:
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)  # Speed of speech
    engine.setProperty('volume', 0.9)  # Volume level
except Exception as e:
    print(f"Error initializing text-to-speech: {e}")
    engine = None

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

# Game settings
TIME_LIMIT = 300  # 5 minutes in seconds
VOICE_FEEDBACK = False  # Disabled by default
BRAILLE_DISPLAY = False  # Disabled by default

# Character descriptions for voice feedback
CHARACTER_DESCRIPTIONS = {
    "fin": "Finn the Human, the main protagonist of Adventure Time",
    "jake": "Jake the Dog, Finn's best friend and adoptive brother",
    "jujuba": "Princess Bubblegum, the ruler of the Candy Kingdom",
    "marcelinne": "Marceline the Vampire Queen, a vampire musician",
    "princesafogo": "Flame Princess, ruler of the Fire Kingdom",
    "caroço": "Lumpy Space Princess, a princess from Lumpy Space",
    "ricardio": "Ricardio the Heart Guy, a villainous heart",
    "menta": "Peppermint Butler, Princess Bubblegum's loyal servant",
    "rei gelado": "Ice King, a wizard who kidnaps princesses",
    "canelinha": "Cinnamon Bun, a resident of the Candy Kingdom",
    "gunther": "Gunter, Ice King's penguin servant",
    "angry lemongrab": "Lemongrab, a sour ruler of the Lemon Kingdom",
    "simon": "Simon Petrikov, the human form of Ice King",
    "rei da noitosfera": "The Nightosphere King, Marceline's father",
    "lady iris": "Lady Rainicorn, Jake's girlfriend"
}

# Load sound effects
try:
    SOUND_EFFECTS = {
        "match": pygame.mixer.Sound("sounds/match.wav"),
        "game_over": pygame.mixer.Sound("sounds/game_over.wav"),
        "victory": pygame.mixer.Sound("sounds/victory.wav")
    }
except Exception as e:
    print(f"Error loading sound effects: {e}")
    SOUND_EFFECTS = {}

# Load character-specific bell sounds
try:
    BELL_SOUNDS = {
        "fin": pygame.mixer.Sound("sounds/bells/bell1.wav"),
        "jake": pygame.mixer.Sound("sounds/bells/bell2.wav"),
        "jujuba": pygame.mixer.Sound("sounds/bells/bell3.wav"),
        "marcelinne": pygame.mixer.Sound("sounds/bells/bell4.wav"),
        "princesafogo": pygame.mixer.Sound("sounds/bells/bell5.wav"),
        "caroço": pygame.mixer.Sound("sounds/bells/bell6.wav"),
        "ricardio": pygame.mixer.Sound("sounds/bells/bell7.wav"),
        "menta": pygame.mixer.Sound("sounds/bells/bell8.wav")
    }
except Exception as e:
    print(f"Error loading bell sounds: {e}")
    BELL_SOUNDS = {}

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
    "src/menta.jpg"
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
        self.card_sounds = {}  # Initialize card_sounds dictionary
        
        # Calculate card dimensions to fit screen with padding
        control_bar_height = 60
        available_height = SCREEN_HEIGHT - control_bar_height - 40  # 40px for padding
        available_width = SCREEN_WIDTH - 40  # 40px for padding
        
        # Calculate maximum possible card size that fits both width and height
        self.card_width = min(available_width // self.cols - 10, 
                            available_height // self.rows - 10)
        self.card_height = self.card_width  # Keep cards square
        
        # Calculate grid offset to center it
        self.grid_width = self.cols * (self.card_width + 10) - 10
        self.grid_height = self.rows * (self.card_height + 10) - 10
        self.grid_x = (SCREEN_WIDTH - self.grid_width) // 2
        self.grid_y = control_bar_height + (available_height - self.grid_height) // 2
        
        self.remaining_time = TIME_LIMIT
        self.game_over = False
        self.reset_grid()  # Call reset_grid after initializing all attributes

    def speak_text(self, text):
        if engine and VOICE_FEEDBACK:
            try:
                engine.say(text)
                engine.runAndWait()
            except Exception as e:
                print(f"Error in text-to-speech: {e}")

    def get_card_name(self, card):
        """Helper function to get card name from a card surface"""
        for i, icon in enumerate(icons):
            if card == icon:
                path = icon_paths[i % len(icon_paths)]
                return path.split('/')[-1].split('.')[0].lower()
        return None

    def get_card_description(self, row, col):
        if 0 <= row < self.rows and 0 <= col < self.cols:
            card_name = self.get_card_name(self.grid[row][col])
            if card_name:
                # Try exact match first
                if card_name in CHARACTER_DESCRIPTIONS:
                    return CHARACTER_DESCRIPTIONS[card_name]
                # Try partial matching if exact match fails
                for name, description in CHARACTER_DESCRIPTIONS.items():
                    if name in card_name or card_name in name:
                        return description
        return "Card selected"

    def get_card_identifier(self, card):
        card_name = self.get_card_name(card)
        if card_name:
            # Try exact match first
            if card_name in CHARACTER_DESCRIPTIONS:
                return card_name
            # Try partial matching if exact match fails
            for name in CHARACTER_DESCRIPTIONS.keys():
                if name in card_name or card_name in name:
                    return name
        return None

    def reset_grid(self):
        shuffled_icons = shuffle_icons()
        index = 0
        self.card_sounds.clear()  # Clear existing sounds
        for i in range(self.rows):
            for j in range(self.cols):
                self.grid[i][j] = shuffled_icons[index]
                card_name = self.get_card_name(shuffled_icons[index])
                if card_name and card_name in BELL_SOUNDS:
                    self.card_sounds[(i, j)] = BELL_SOUNDS[card_name]
                index += 1

    def play_card_sound(self, row, col):
        if (row, col) in self.card_sounds:
            self.card_sounds[(row, col)].play()

    def draw_grid(self):
        # Draw game controls bar at the top
        control_bar_height = 60
        pygame.draw.rect(screen, BLACK, (0, 0, SCREEN_WIDTH, control_bar_height))
        
        # Draw control buttons with hover effects
        font = pygame.font.Font(None, 36)
        buttons = [
            ("Pause", 10),
            ("Restart", 150),
            ("Menu", 290),
            ("Help", 430)
        ]
        
        mouse_x, mouse_y = pygame.mouse.get_pos()
        for text, x_pos in buttons:
            button = font.render(text, True, WHITE)
            button_rect = button.get_rect(x=x_pos, y=15)
            
            # Draw button background with hover effect
            if button_rect.collidepoint(mouse_x, mouse_y):
                pygame.draw.rect(screen, (255, 255, 255, 128), 
                               (button_rect.x - 10, button_rect.y - 5, 
                                button_rect.width + 20, button_rect.height + 10))
                button = font.render(text, True, BLACK)
            
            screen.blit(button, button_rect)
        
        # Draw game stats
        time_text = font.render(f"Time: {self.remaining_time}s", True, WHITE)
        score_text = font.render(f"Score: {self.score}", True, WHITE)
        screen.blit(time_text, (SCREEN_WIDTH - 200, 15))
        screen.blit(score_text, (SCREEN_WIDTH - 400, 15))

        # Draw the game grid
        for i in range(self.rows):
            for j in range(self.cols):
                x = self.grid_x + j * (self.card_width + 10)
                y = self.grid_y + i * (self.card_height + 10)
                if (i, j) in self.matched or (i, j) in self.selected:
                    screen.blit(pygame.transform.scale(self.grid[i][j], 
                              (self.card_width, self.card_height)), (x, y))
                else:
                    pygame.draw.rect(screen, BLACK, (x, y, self.card_width, self.card_height))
                    pygame.draw.rect(screen, PINK, (x + 2, y + 2, 
                                  self.card_width - 4, self.card_height - 4))
                    # Add hover effect
                    if (x < mouse_x < x + self.card_width and 
                        y < mouse_y < y + self.card_height):
                        pygame.draw.rect(screen, WHITE, (x, y, self.card_width, self.card_height), 2)

        pygame.display.flip()

    def check_match(self):
        time.sleep(0.5)
        if len(self.selected) == 2:
            card1 = self.grid[self.selected[0][0]][self.selected[0][1]]
            card2 = self.grid[self.selected[1][0]][self.selected[1][1]]
            
            # Compare the actual card surfaces
            if card1 == card2:
                self.matched.extend(self.selected)
                self.score += 10
                if "match" in SOUND_EFFECTS:
                    SOUND_EFFECTS["match"].play()
                # Get the character name for the matched pair
                card_id = self.get_card_identifier(self.grid[self.selected[0][0]][self.selected[0][1]])
                if card_id:
                    self.speak_text(f"Match found! You found {card_id}!")
                else:
                    self.speak_text("Match found!")
            else:
                if "card_flip" in SOUND_EFFECTS:
                    SOUND_EFFECTS["card_flip"].play()
                self.speak_text("No match. Try again!")
            self.selected = []
            self.moves += 1

    def check_game_over(self):
        if len(self.matched) == self.rows * self.cols:
            if "victory" in SOUND_EFFECTS:
                SOUND_EFFECTS["victory"].play()
            self.speak_text("Congratulations! You won the game!")
            return True
        if self.remaining_time <= 0:
            if "game_over" in SOUND_EFFECTS:
                SOUND_EFFECTS["game_over"].play()
            self.speak_text("Time's up! Game Over!")
            return True
        return False

    def game_loop(self):
        clock = pygame.time.Clock()
        running = True
        paused = False
        control_bar_height = 60
        last_frame_time = pygame.time.get_ticks()

        while running:
            current_time = pygame.time.get_ticks()
            delta_time = (current_time - last_frame_time) / 1000.0  # Convert to seconds
            last_frame_time = current_time
            
            if not paused:
                self.remaining_time = max(0, TIME_LIMIT - (current_time - self.start_time) // 1000)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if not paused:
                        mouse_x, mouse_y = event.pos
                        # Check if click is in control bar
                        if mouse_y < control_bar_height:
                            if 10 <= mouse_x <= 100:  # Pause button
                                paused = not paused
                            elif 150 <= mouse_x <= 250:  # Restart button
                                self.reset_grid()
                                self.selected = []
                                self.matched = []
                                self.moves = 0
                                self.score = 0
                                self.start_time = current_time
                            elif 290 <= mouse_x <= 390:  # Menu button
                                return
                            elif 430 <= mouse_x <= 530:  # Help button
                                help_menu()
                        # Check if click is in game grid
                        elif len(self.selected) < 2:
                            # Convert mouse position to grid coordinates
                            if mouse_x >= self.grid_x and mouse_y >= self.grid_y:
                                col = (mouse_x - self.grid_x) // (self.card_width + 10)
                                row = (mouse_y - self.grid_y) // (self.card_height + 10)
                                if 0 <= row < self.rows and 0 <= col < self.cols:
                                    if (row, col) not in self.selected and (row, col) not in self.matched:
                                        self.selected.append((row, col))
                                        self.play_card_sound(row, col)
                                        if "card_flip" in SOUND_EFFECTS:
                                            SOUND_EFFECTS["card_flip"].play()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:  # Return to main menu
                        return
                    elif event.key == pygame.K_p:  # Pause
                        paused = not paused
                    elif event.key == pygame.K_r:  # Restart
                        self.reset_grid()
                        self.selected = []
                        self.matched = []
                        self.moves = 0
                        self.score = 0
                        self.start_time = current_time

            if not paused:
                self.draw_grid()
                self.check_match()

                if self.check_game_over():
                    self.show_game_over()
                    return

            # Cap the frame rate for smooth animation
            clock.tick(144)  # Increased to 144 FPS for smoother animations

    def show_game_over(self):
        elapsed_time = (pygame.time.get_ticks() - self.start_time) // 1000
        result_message = f"Game Over!\nMoves: {self.moves}\nScore: {self.score}\nTime: {elapsed_time} seconds"
        print(result_message)
        
        # Create a semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill(BLACK)
        overlay.set_alpha(128)
        screen.blit(overlay, (0, 0))

        # Display game over message
        font = pygame.font.Font(None, 74)
        game_over_text = font.render("Game Over!", True, WHITE)
        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 100))

        font = pygame.font.Font(None, 36)
        stats_text = font.render(f"Moves: {self.moves} | Score: {self.score} | Time: {elapsed_time}s", True, WHITE)
        screen.blit(stats_text, (SCREEN_WIDTH // 2 - stats_text.get_width() // 2, SCREEN_HEIGHT // 2 + 20))

        pygame.display.flip()
        time.sleep(3)  # Show the game over screen for 3 seconds

# Help text content for the manual
HELP_TEXT = [
    "How to Play:",
    "- Click on cards to reveal them",
    "- Match pairs of identical cards",
    "- Complete the grid before time runs out",
    "",
    "Game Controls:",
    "- Left Click: Select card",
    "- ESC: Return to main menu",
    "- P: Pause game",
    "- R: Restart game",
    "",
    "Scoring:",
    "- Each match: +10 points",
    "- Time bonus: Remaining time × 2",
    "",
    "Sound Settings:",
    "- Each card has a unique bell sound",
    "- Match sound plays when pairs are found",
    "- Victory sound plays when game is won",
    "",
    "Tips:",
    "- Remember card positions",
    "- Listen for unique bell sounds",
    "- Watch the timer",
    "- Try to make fewer moves for higher scores"
]

def draw_menu():
    if background_image:
        screen.blit(background_image, (0, 0))
    else:
        screen.fill(WHITE)

    # Draw a semi-transparent overlay for better text visibility
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.fill(BLACK)
    overlay.set_alpha(128)
    screen.blit(overlay, (0, 0))

    # Draw title with shadow effect
    font = pygame.font.Font(None, 74)
    title_shadow = font.render("Adventure Time", True, BLACK)
    title = font.render("Adventure Time", True, RED)
    screen.blit(title_shadow, (SCREEN_WIDTH // 2 - title.get_width() // 2 + 2, 102))
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))

    # Draw buttons with hover effects
    font = pygame.font.Font(None, 50)
    buttons = [
        ("Start Game", 200),
        ("Accessibility Settings", 300),
        ("Help", 400),
        ("Quit", 500)
    ]

    mouse_x, mouse_y = pygame.mouse.get_pos()
    for text, y_pos in buttons:
        button = font.render(text, True, PINK)
        button_rect = button.get_rect(center=(SCREEN_WIDTH // 2, y_pos))
        
        # Draw button background with hover effect
        if button_rect.collidepoint(mouse_x, mouse_y):
            pygame.draw.rect(screen, (255, 255, 255, 128), 
                           (button_rect.x - 20, button_rect.y - 10, 
                            button_rect.width + 40, button_rect.height + 20))
            button = font.render(text, True, WHITE)
        
        screen.blit(button, button_rect)

    # Draw accessibility status with better visibility
    font = pygame.font.Font(None, 36)
    status_text = f"Voice Feedback: {'On' if VOICE_FEEDBACK else 'Off'} | Braille Display: {'On' if BRAILLE_DISPLAY else 'Off'}"
    status = font.render(status_text, True, WHITE)
    status_rect = status.get_rect()
    status_rect.bottomleft = (10, SCREEN_HEIGHT - 10)
    screen.blit(status, status_rect)

    pygame.display.flip()

def draw_accessibility_menu():
    if background_image:
        screen.blit(background_image, (0, 0))
    else:
        screen.fill(WHITE)

    # Draw semi-transparent overlay
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.fill(BLACK)
    overlay.set_alpha(128)
    screen.blit(overlay, (0, 0))

    font = pygame.font.Font(None, 74)
    title = font.render("Sound Settings", True, RED)
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))

    # Draw buttons with hover effects
    font = pygame.font.Font(None, 50)
    buttons = [
        ("Toggle Sound Effects", 300),
        ("Adjust Volume", 400),
        ("Back to Main Menu", 500)
    ]

    mouse_x, mouse_y = pygame.mouse.get_pos()
    for text, y_pos in buttons:
        button = font.render(text, True, PINK)
        button_rect = button.get_rect(center=(SCREEN_WIDTH // 2, y_pos))
        
        # Draw button background with hover effect
        if button_rect.collidepoint(mouse_x, mouse_y):
            pygame.draw.rect(screen, (255, 255, 255, 128), 
                           (button_rect.x - 20, button_rect.y - 10, 
                            button_rect.width + 40, button_rect.height + 20))
            button = font.render(text, True, WHITE)
        
        screen.blit(button, button_rect)

    # Draw back button
    back_button = font.render("Back to Main Menu (ESC)", True, WHITE)
    back_rect = back_button.get_rect()
    back_rect.bottomleft = (10, SCREEN_HEIGHT - 10)
    screen.blit(back_button, back_rect)

    pygame.display.flip()

def accessibility_menu():
    while True:
        draw_accessibility_menu()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                if SCREEN_WIDTH // 2 - 200 <= mouse_x <= SCREEN_WIDTH // 2 + 200:
                    if 300 <= mouse_y <= 350:  # Toggle Sound Effects
                        pygame.mixer.set_num_channels(0 if pygame.mixer.get_num_channels() > 0 else 8)
                    elif 400 <= mouse_y <= 450:  # Adjust Volume
                        current_volume = pygame.mixer.music.get_volume()
                        pygame.mixer.music.set_volume(min(1.0, current_volume + 0.1))
                    elif 500 <= mouse_y <= 550:  # Back to Main Menu
                        return
                # Check if back button was clicked
                elif 10 <= mouse_x <= 200 and SCREEN_HEIGHT - 40 <= mouse_y <= SCREEN_HEIGHT - 10:
                    return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return

def draw_help_menu(scroll_y):
    if background_image:
        screen.blit(background_image, (0, 0))
    else:
        screen.fill(WHITE)

    # Draw semi-transparent overlay
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.fill(BLACK)
    overlay.set_alpha(128)
    screen.blit(overlay, (0, 0))

    # Create a surface for the help text
    help_surface = pygame.Surface((SCREEN_WIDTH - 100, SCREEN_HEIGHT * 2))
    help_surface.fill(BLACK)
    help_surface.set_alpha(200)

    # Title
    font_title = pygame.font.Font(None, 74)
    title = font_title.render("Game Manual", True, RED)
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))

    # Help text content
    font = pygame.font.Font(None, 36)
    y = 20
    for line in HELP_TEXT:
        text = font.render(line, True, WHITE)
        help_surface.blit(text, (40, y))
        y += 40

    # Draw the visible portion of the help surface
    screen.blit(help_surface, (50, 150), (0, -scroll_y, SCREEN_WIDTH - 100, SCREEN_HEIGHT - 200))

    # Draw scroll bar
    total_height = len(HELP_TEXT) * 40
    visible_height = SCREEN_HEIGHT - 200
    scroll_ratio = visible_height / total_height
    scroll_bar_height = max(50, visible_height * scroll_ratio)
    scroll_position = (scroll_y / total_height) * visible_height
    
    # Draw scroll bar background
    pygame.draw.rect(screen, (100, 100, 100), (SCREEN_WIDTH - 30, 150, 20, SCREEN_HEIGHT - 200))
    # Draw scroll bar handle
    pygame.draw.rect(screen, WHITE, (SCREEN_WIDTH - 30, 150 + scroll_position, 20, scroll_bar_height))

    # Draw back button
    back_button = font.render("Back to Main Menu (ESC)", True, WHITE)
    back_rect = back_button.get_rect()
    back_rect.bottomleft = (10, SCREEN_HEIGHT - 10)
    screen.blit(back_button, back_rect)

    pygame.display.flip()

def help_menu():
    scroll_y = 0
    scroll_speed = 30  # Increased scroll speed for smoother scrolling
    
    # Calculate total content height and maximum scroll position
    help_text_height = len(HELP_TEXT) * 40  # Height of all text lines
    visible_height = SCREEN_HEIGHT - 350  # Visible area height
    max_scroll = max(0, help_text_height - visible_height)  # Prevent negative scroll values
    
    while True:
        draw_help_menu(scroll_y)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                
                # Check if back button was clicked
                if 10 <= mouse_x <= 300 and SCREEN_HEIGHT - 40 <= mouse_y <= SCREEN_HEIGHT - 10:
                    return
                    
                # Handle mouse wheel scrolling
                if event.button == 4:  # Mouse wheel up
                    scroll_y = max(0, scroll_y - scroll_speed)
                elif event.button == 5:  # Mouse wheel down
                    scroll_y = min(max_scroll, scroll_y + scroll_speed)
                    
                # Handle scroll bar dragging
                elif event.button == 1:  # Left click
                    if SCREEN_WIDTH - 30 <= mouse_x <= SCREEN_WIDTH - 10 and 150 <= mouse_y <= SCREEN_HEIGHT - 50:
                        # Calculate new scroll position based on click position
                        click_ratio = (mouse_y - 150) / (SCREEN_HEIGHT - 350)
                        scroll_y = min(max_scroll, int(click_ratio * max_scroll))
                        
            elif event.type == pygame.MOUSEMOTION:
                # Handle scroll bar dragging
                if event.buttons[0]:  # Left button held
                    mouse_x, mouse_y = event.pos
                    if SCREEN_WIDTH - 30 <= mouse_x <= SCREEN_WIDTH - 10 and 150 <= mouse_y <= SCREEN_HEIGHT - 50:
                        click_ratio = (mouse_y - 150) / (SCREEN_HEIGHT - 350)
                        scroll_y = min(max_scroll, int(click_ratio * max_scroll))
                        
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
                elif event.key == pygame.K_UP:
                    scroll_y = max(0, scroll_y - scroll_speed)
                elif event.key == pygame.K_DOWN:
                    scroll_y = min(max_scroll, scroll_y + scroll_speed)
                elif event.key == pygame.K_PAGEUP:
                    scroll_y = max(0, scroll_y - visible_height)
                elif event.key == pygame.K_PAGEDOWN:
                    scroll_y = min(max_scroll, scroll_y + visible_height)

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
                if SCREEN_WIDTH // 2 - 150 <= mouse_x <= SCREEN_WIDTH // 2 + 150:
                    if 200 <= mouse_y <= 250:
                        # Start game directly with default size (4x4 grid)
                        start_game(4, 4, "normal")
                    elif 300 <= mouse_y <= 350:
                        accessibility_menu()
                    elif 400 <= mouse_y <= 450:
                        help_menu()
                    elif 500 <= mouse_y <= 550:
                        pygame.quit()
                        sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

def start_game(rows, cols, mode):
    game = MemoryGame(rows, cols, mode)
    game.game_loop()
    main_menu()  # Return to main menu after game ends

if __name__ == "__main__":
    main_menu()