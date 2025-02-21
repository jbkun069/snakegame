import pygame  # type: ignore
import random
import os

# Constants
GRID_WIDTH = 20
GRID_HEIGHT = 15
CELL_SIZE = 40
WINDOW_WIDTH = GRID_WIDTH * CELL_SIZE
WINDOW_HEIGHT = GRID_HEIGHT * CELL_SIZE
HIGH_SCORE_FILE = "high_score.txt"

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
GRASS_GREEN = (34, 139, 34)
GRASS_GREEN_DARK = (0, 100, 0)
GRID_COLOR = (200, 200, 200)  # Light gray for grid lines

# Initialize Pygame
pygame.init()
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Snake Game")
clock = pygame.time.Clock()

# Load assets
def load_and_scale_image(path, size):
    """Helper function to load and scale images with error handling."""
    try:
        return pygame.transform.scale(pygame.image.load(path), (size, size))
    except pygame.error as e:
        print(f"Error loading image {path}: {e}")
        surface = pygame.Surface((size, size))
        surface.fill(GREEN if 'head' in path or 'body' in path or 'tail' in path else RED)
        return surface

# Load food image
FOOD_IMAGE = load_and_scale_image(os.path.join('assets', 'apple.png'), CELL_SIZE)

# Load head images
HEAD_DIRECTIONS = ['up', 'down', 'left', 'right']
HEAD_IMAGES = {
    direction: load_and_scale_image(os.path.join('assets', f'head_{direction}.png'), CELL_SIZE)
    for direction in HEAD_DIRECTIONS
}

# Load body images
BODY_TYPES = ['horizontal', 'vertical', 'bottomleft', 'bottomright', 'topleft', 'topright']
BODY_IMAGES = {
    body_type: load_and_scale_image(os.path.join('assets', f'body_{body_type}.png'), CELL_SIZE)
    for body_type in BODY_TYPES
}

# Load tail images
TAIL_IMAGES = {
    direction: load_and_scale_image(os.path.join('assets', f'tail_{direction}.png'), CELL_SIZE)
    for direction in HEAD_DIRECTIONS
}

# Load sound effects
try:
    EAT_SOUND = pygame.mixer.Sound(os.path.join('assets', 'eat.wav'))
    GAME_OVER_SOUND = pygame.mixer.Sound(os.path.join('assets', 'game_over.wav'))
except pygame.error as e:
    print(f"Error loading sound: {e}")
    EAT_SOUND = None
    GAME_OVER_SOUND = None

# Create grass pattern
def create_grass_tile():
    """Create a grass pattern tile."""
    tile = pygame.Surface((CELL_SIZE, CELL_SIZE))
    tile.fill(GRASS_GREEN)
    for _ in range(4):
        spot_size = random.randint(4, 8)
        x = random.randint(0, CELL_SIZE - spot_size)
        y = random.randint(0, CELL_SIZE - spot_size)
        pygame.draw.circle(tile, GRASS_GREEN_DARK, (x, y), spot_size)
    return tile

GRASS_TILE = create_grass_tile()
GRASS_PATTERN = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
for x in range(0, WINDOW_WIDTH, CELL_SIZE):
    for y in range(0, WINDOW_HEIGHT, CELL_SIZE):
        GRASS_PATTERN.blit(GRASS_TILE, (x, y))

# Functions
def load_high_score():
    """Load the high score from a file."""
    try:
        if os.path.exists(HIGH_SCORE_FILE):
            with open(HIGH_SCORE_FILE, 'r') as file:
                return int(file.read())
    except (IOError, ValueError):
        pass
    return 0

def save_high_score(score):
    """Save the high score to a file."""
    try:
        with open(HIGH_SCORE_FILE, 'w') as file:
            file.write(str(score))
    except IOError:
        pass

def generate_food(snake_body):
    """Generate food at a random position not occupied by the snake."""
    max_attempts = 1000
    attempts = 0
    while attempts < max_attempts:
        food = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
        if food not in snake_body:
            return food
        attempts += 1
    return None

def draw_background():
    """Draw the grass pattern background with grid overlay."""
    window.blit(GRASS_PATTERN, (0, 0))
    # Draw grid lines
    for x in range(0, WINDOW_WIDTH, CELL_SIZE):
        pygame.draw.line(window, GRID_COLOR, (x, 0), (x, WINDOW_HEIGHT))
    for y in range(0, WINDOW_HEIGHT, CELL_SIZE):
        pygame.draw.line(window, GRID_COLOR, (0, y), (WINDOW_WIDTH, y))

def get_direction_name(direction):
    """Convert direction tuple to string name."""
    if direction == (0, -1): return 'up'
    if direction == (0, 1): return 'down'
    if direction == (-1, 0): return 'left'
    if direction == (1, 0): return 'right'
    return 'right'  # default

def get_segment_direction(prev_pos, curr_pos, next_pos):
    """Determine the appropriate body segment type based on neighboring positions."""
    if not prev_pos or not next_pos:
        return 'horizontal'
    dx1 = curr_pos[0] - prev_pos[0]
    dy1 = curr_pos[1] - prev_pos[1]
    dx2 = next_pos[0] - curr_pos[0]
    dy2 = next_pos[1] - curr_pos[1]
    if dx1 == dx2 and dx1 != 0: return 'horizontal'
    if dy1 == dy2 and dy1 != 0: return 'vertical'
    if (dx1 == 1 and dy2 == 1) or (dy1 == 1 and dx2 == 1): return 'topleft'
    if (dx1 == -1 and dy2 == 1) or (dy1 == 1 and dx2 == -1): return 'topright'
    if (dx1 == 1 and dy2 == -1) or (dy1 == -1 and dx2 == 1): return 'bottomleft'
    if (dx1 == -1 and dy2 == -1) or (dy1 == -1 and dx2 == -1): return 'bottomright'
    return 'horizontal'

def draw_snake(snake_body, direction):
    """Draw the snake using appropriate segment images."""
    if not snake_body:
        return
    dir_name = get_direction_name(direction)
    window.blit(HEAD_IMAGES[dir_name], (snake_body[0][0] * CELL_SIZE, snake_body[0][1] * CELL_SIZE))
    for i in range(1, len(snake_body) - 1):
        prev_pos = snake_body[i-1]
        curr_pos = snake_body[i]
        next_pos = snake_body[i+1]
        segment_type = get_segment_direction(prev_pos, curr_pos, next_pos)
        window.blit(BODY_IMAGES[segment_type], (curr_pos[0] * CELL_SIZE, curr_pos[1] * CELL_SIZE))
    if len(snake_body) > 1:
        tail_pos = snake_body[-1]
        prev_tail_pos = snake_body[-2]
        dx = tail_pos[0] - prev_tail_pos[0]
        dy = tail_pos[1] - prev_tail_pos[1]
        tail_dir = get_direction_name((dx, dy))
        window.blit(TAIL_IMAGES[tail_dir], (tail_pos[0] * CELL_SIZE, tail_pos[1] * CELL_SIZE))

def draw_food(food_position):
    """Draw the food on the window."""
    if food_position:
        window.blit(FOOD_IMAGE, (food_position[0] * CELL_SIZE, food_position[1] * CELL_SIZE))

def draw_score(score, high_score):
    """Draw the current score and high score on the screen."""
    font = pygame.font.Font(None, 36)
    score_text = font.render(f"Score: {score}", True, WHITE)
    high_score_text = font.render(f"High Score: {high_score}", True, WHITE)
    window.blit(score_text, (10, 10))
    window.blit(high_score_text, (10, 50))

def start_screen():
    """Display the start screen with instructions and start button."""
    font = pygame.font.Font(None, 72)
    button_font = pygame.font.Font(None, 48)
    title_text = font.render("Snake Game", True, WHITE)
    instructions = [
        "Use arrow keys to move",
        "Press + or = to increase speed",
        "Press - to decrease speed",
        "Press P to pause/resume",
        "Eat apples to grow and score points"
    ]
    instruction_texts = [button_font.render(text, True, WHITE) for text in instructions]
    
    # Start button
    button_width, button_height = 200, 60
    button_x = WINDOW_WIDTH // 2 - button_width // 2
    button_y = WINDOW_HEIGHT // 2 + 100
    button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
    start_text = button_font.render("Start", True, WHITE)
    start_text_rect = start_text.get_rect(center=button_rect.center)
    
    # Draw start screen
    window.fill(BLACK)
    window.blit(title_text, (WINDOW_WIDTH // 2 - 150, 50))
    for i, text in enumerate(instruction_texts):
        window.blit(text, (WINDOW_WIDTH // 2 - 200, 150 + i * 40))
    pygame.draw.rect(window, GREEN, button_rect)
    window.blit(start_text, start_text_rect)
    pygame.display.flip()
    
    # Wait for user to start
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN or (event.type == pygame.MOUSEBUTTONDOWN and button_rect.collidepoint(event.pos)):
                waiting = False

def game_over_screen(score, high_score):
    """Display game over screen with restart and quit options."""
    font = pygame.font.Font(None, 72)
    button_font = pygame.font.Font(None, 48)
    
    # Text
    game_over_text = font.render("Game Over", True, RED)
    score_text = font.render(f"Score: {score}", True, WHITE)
    high_score_text = font.render(f"High Score: {high_score}", True, WHITE)
    restart_text = font.render("Press R to Restart", True, WHITE)
    
    # Quit button
    button_width, button_height = 200, 60
    button_x = WINDOW_WIDTH // 2 - button_width // 2
    button_y = WINDOW_HEIGHT // 2 + 250
    button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
    quit_text = button_font.render("Quit", True, WHITE)
    quit_text_rect = quit_text.get_rect(center=button_rect.center)
    
    # Draw everything
    window.blit(game_over_text, (WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT // 2 - 150))
    window.blit(score_text, (WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2 - 50))
    window.blit(high_score_text, (WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT // 2 + 50))
    window.blit(restart_text, (WINDOW_WIDTH // 2 - 200, WINDOW_HEIGHT // 2 + 150))
    pygame.draw.rect(window, RED, button_rect)
    window.blit(quit_text, quit_text_rect)
    pygame.display.flip()
    
    # Event loop
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return True
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos):
                    return False
    return False

def main():
    """Main function to run the Snake game."""
    start_screen()  # Show start screen before starting the game
    while True:
        game_speed = 1  # Fixed initial speed (adjustable in-game)
        snake_body = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        direction = (1, 0)
        food = generate_food(snake_body)
        if food is None:
            print("Error: Could not generate food position")
            return
        score = 0
        high_score = load_high_score()
        running = True
        paused = False
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        paused = not paused
                    if not paused:
                        if event.key == pygame.K_UP and direction != (0, 1):
                            direction = (0, -1)
                        elif event.key == pygame.K_DOWN and direction != (0, -1):
                            direction = (0, 1)
                        elif event.key == pygame.K_LEFT and direction != (1, 0):
                            direction = (-1, 0)
                        elif event.key == pygame.K_RIGHT and direction != (-1, 0):
                            direction = (1, 0)
                        elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                            game_speed = min(game_speed + 1, 20)
                        elif event.key == pygame.K_MINUS:
                            game_speed = max(game_speed - 1, 1)
            
            if paused:
                font = pygame.font.Font(None, 72)
                pause_text = font.render("Paused", True, WHITE)
                window.blit(pause_text, (WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2 - 50))
                pygame.display.flip()
                continue
            
            new_head = (snake_body[0][0] + direction[0], snake_body[0][1] + direction[1])
            if (new_head in snake_body or
                new_head[0] < 0 or new_head[0] >= GRID_WIDTH or
                new_head[1] < 0 or new_head[1] >= GRID_HEIGHT):
                if GAME_OVER_SOUND:
                    GAME_OVER_SOUND.play()
                running = False
            snake_body.insert(0, new_head)
            if new_head == food:
                score += 1
                if EAT_SOUND:
                    EAT_SOUND.play()
                food = generate_food(snake_body)
                if score > high_score:
                    high_score = score
            else:
                snake_body.pop()
            draw_background()
            draw_snake(snake_body, direction)
            draw_food(food)
            draw_score(score, high_score)
            pygame.display.flip()
            clock.tick(5 + game_speed * 2)
        save_high_score(high_score)
        if not game_over_screen(score, high_score):
            break
    pygame.quit()

if __name__ == "__main__":
    main()