import pygame  # type: ignore
import pygame_gui  # Added for UI enhancements
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
GRID_COLOR = (200, 200, 200)
GOLD = (255, 215, 0)
FLASH_COLOR = (255, 255, 255, 100)

# Initialize Pygame
pygame.init()
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Snake Game")
clock = pygame.time.Clock()

# Initialize Pygame GUI Manager
ui_manager = pygame_gui.UIManager((WINDOW_WIDTH, WINDOW_HEIGHT))

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

# Load food images
FOOD_IMAGE = load_and_scale_image(os.path.join('assets', 'apple.png'), CELL_SIZE)
GOLDEN_FOOD_IMAGE = load_and_scale_image(os.path.join('assets', 'golden_apple.png'), CELL_SIZE)

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
            is_golden = random.random() < 0.1
            return (food, is_golden)
        attempts += 1
    return None

def draw_background():
    """Draw the grass pattern background with grid overlay."""
    window.blit(GRASS_PATTERN, (0, 0))
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
    return 'right'

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

def draw_food(food):
    """Draw the food on the window."""
    if food:
        position, is_golden = food
        image = GOLDEN_FOOD_IMAGE if is_golden else FOOD_IMAGE
        window.blit(image, (position[0] * CELL_SIZE, position[1] * CELL_SIZE))

def draw_score(score, high_score, game_speed):
    """Draw the current score, high score, and speed on the screen."""
    font = pygame.font.Font(None, 36)
    score_text = font.render(f"Score: {score}", True, WHITE)
    high_score_text = font.render(f"High Score: {high_score}", True, WHITE)
    speed_text = font.render(f"Speed: {game_speed}", True, WHITE)
    window.blit(score_text, (10, 10))
    window.blit(high_score_text, (10, 50))
    window.blit(speed_text, (10, 90))

def flash_screen():
    """Flash the screen briefly when food is eaten."""
    flash_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
    flash_surface.fill(FLASH_COLOR)
    window.blit(flash_surface, (0, 0))
    pygame.display.flip()
    pygame.time.wait(50)

def start_screen():
    """Display the start screen with Pygame GUI."""
    ui_manager.clear_and_reset()  # Reset UI for fresh start
    
    pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((WINDOW_WIDTH // 2 - 150, 50), (300, 50)),
        text="Snake Game",
        manager=ui_manager
    )
    
    instructions = [
        "Use arrow keys to move",
        "Press + or = to increase speed",
        "Press - to decrease speed",
        "Press P to pause/resume",
        "Eat apples (1 pt) or golden apples (5 pts)"
    ]
    for i, text in enumerate(instructions):
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((WINDOW_WIDTH // 2 - 200, 150 + i * 40), (400, 30)),
            text=text,
            manager=ui_manager
        )
    
    start_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2 + 100), (200, 60)),
        text="Start",
        manager=ui_manager
    )
    
    window.fill(BLACK)
    time_delta = clock.tick(60) / 1000.0
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == start_button:
                    waiting = False
            ui_manager.process_events(event)
        
        ui_manager.update(time_delta)
        window.fill(BLACK)  # Redraw background each frame
        ui_manager.draw_ui(window)
        pygame.display.flip()

def game_over_screen(score, high_score):
    """Display game over screen with Pygame GUI buttons."""
    ui_manager.clear_and_reset()  # Reset UI for game over screen
    
    pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT // 2 - 150), (300, 50)),
        text="Game Over",
        manager=ui_manager,
        object_id="#game_over_label"  # Custom ID for styling if needed
    )
    
    pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2 - 50), (200, 40)),
        text=f"Score: {score}",
        manager=ui_manager
    )
    
    pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT // 2 + 10), (300, 40)),
        text=f"High Score: {high_score}",
        manager=ui_manager
    )
    
    restart_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((WINDOW_WIDTH // 2 - 210, WINDOW_HEIGHT // 2 + 100), (200, 60)),
        text="Restart",
        manager=ui_manager
    )
    
    quit_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((WINDOW_WIDTH // 2 + 10, WINDOW_HEIGHT // 2 + 100), (200, 60)),
        text="Quit",
        manager=ui_manager
    )
    
    window.fill(BLACK)
    time_delta = clock.tick(60) / 1000.0
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == restart_button:
                    return True
                if event.ui_element == quit_button:
                    return False
            ui_manager.process_events(event)
        
        ui_manager.update(time_delta)
        window.fill(BLACK)  # Redraw background each frame
        ui_manager.draw_ui(window)
        pygame.display.flip()
    return False

def main():
    """Main function to run the Snake game."""
    start_screen()
    while True:
        game_speed = 1
        snake_body = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        direction = (1, 0)
        next_direction = direction
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
                            next_direction = (0, -1)
                        elif event.key == pygame.K_DOWN and direction != (0, -1):
                            next_direction = (0, 1)
                        elif event.key == pygame.K_LEFT and direction != (1, 0):
                            next_direction = (-1, 0)
                        elif event.key == pygame.K_RIGHT and direction != (-1, 0):
                            next_direction = (1, 0)
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
            
            direction = next_direction
            new_head = (snake_body[0][0] + direction[0], snake_body[0][1] + direction[1])
            if (new_head in snake_body or
                new_head[0] < 0 or new_head[0] >= GRID_WIDTH or
                new_head[1] < 0 or new_head[1] >= GRID_HEIGHT):
                if GAME_OVER_SOUND:
                    GAME_OVER_SOUND.play()
                running = False
            snake_body.insert(0, new_head)
            if food and new_head == food[0]:
                score += 5 if food[1] else 1
                if EAT_SOUND:
                    EAT_SOUND.play()
                flash_screen()
                food = generate_food(snake_body)
                if score > high_score:
                    high_score = score
            else:
                snake_body.pop()
            draw_background()
            draw_snake(snake_body, direction)
            draw_food(food)
            draw_score(score, high_score, game_speed)
            pygame.display.flip()
            clock.tick(5 + game_speed * 2)
        save_high_score(high_score)
        if not game_over_screen(score, high_score):
            break
    pygame.quit()

if __name__ == "__main__":
    main()