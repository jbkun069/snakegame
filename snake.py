import pygame # type: ignore
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
    except:
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
    return None  # Return None if no valid position is found

def get_initial_speed():
    """Get the initial game speed."""
    return 1  # Default speed

def draw_background():
    """Draw a solid black background."""
    window.fill(BLACK)

def get_direction_name(direction):
    """Convert direction tuple to string name."""
    if direction == (0, -1): return 'up'
    if direction == (0, 1): return 'down'
    if direction == (-1, 0): return 'left'
    if direction == (1, 0): return 'right'
    return 'right'  # default

def get_segment_direction(prev_pos, curr_pos, next_pos):
    """Determine the appropriate body segment type based on neighboring positions."""
    if not prev_pos or not next_pos:  # For head or tail
        return 'horizontal'
        
    dx1 = curr_pos[0] - prev_pos[0]
    dy1 = curr_pos[1] - prev_pos[1]
    dx2 = next_pos[0] - curr_pos[0]
    dy2 = next_pos[1] - curr_pos[1]
    
    # Straight segments
    if dx1 == dx2 and dx1 != 0: return 'horizontal'
    if dy1 == dy2 and dy1 != 0: return 'vertical'
    
    # Corner segments
    if (dx1 == 1 and dy2 == 1) or (dy1 == 1 and dx2 == 1): return 'topleft'
    if (dx1 == -1 and dy2 == 1) or (dy1 == 1 and dx2 == -1): return 'topright'
    if (dx1 == 1 and dy2 == -1) or (dy1 == -1 and dx2 == 1): return 'bottomleft'
    if (dx1 == -1 and dy2 == -1) or (dy1 == -1 and dx2 == -1): return 'bottomright'
    
    return 'horizontal'  # default

def draw_snake(snake_body, direction):
    """Draw the snake using appropriate segment images."""
    if not snake_body:
        return

    # Draw head
    dir_name = get_direction_name(direction)
    window.blit(HEAD_IMAGES[dir_name], (snake_body[0][0] * CELL_SIZE, snake_body[0][1] * CELL_SIZE))
    
    # Draw body segments
    for i in range(1, len(snake_body) - 1):
        prev_pos = snake_body[i-1]
        curr_pos = snake_body[i]
        next_pos = snake_body[i+1]
        segment_type = get_segment_direction(prev_pos, curr_pos, next_pos)
        window.blit(BODY_IMAGES[segment_type], (curr_pos[0] * CELL_SIZE, curr_pos[1] * CELL_SIZE))
    
    # Draw tail
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

def select_speed():
    """Let user select initial game speed."""
    speed = 1
    selecting = True
    font = pygame.font.Font(None, 36)
    
    while selecting:
        window.fill(BLACK)
        text = font.render(f"Select Speed: {speed} (Use UP/DOWN, ENTER to confirm)", True, WHITE)
        text_rect = text.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2))
        window.blit(text, text_rect)
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    speed = min(speed + 1, 20)
                elif event.key == pygame.K_DOWN:
                    speed = max(speed - 1, 1)
                elif event.key == pygame.K_RETURN:
                    selecting = False
    
    return speed

def main():
    """Main function to run the Snake game."""
    # Get initial speed from user
    game_speed = select_speed()
    if game_speed is None:  # User closed window during speed selection
        return
        
    snake_body = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
    direction = (1, 0)
    food = generate_food(snake_body)
    if food is None:
        print("Error: Could not generate food position")
        return
    
    score = 0
    high_score = load_high_score()
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
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

        # Move the snake
        new_head = (snake_body[0][0] + direction[0], snake_body[0][1] + direction[1])

        # Check for collisions
        if (new_head in snake_body or
            new_head[0] < 0 or new_head[0] >= GRID_WIDTH or
            new_head[1] < 0 or new_head[1] >= GRID_HEIGHT):
            running = False  # Game over

        # Add new head to the snake
        snake_body.insert(0, new_head)

        # Check if the snake has eaten the food
        if new_head == food:
            score += 1
            food = generate_food(snake_body)
            if score > high_score:
                high_score = score
        else:
            snake_body.pop()  # Remove the tail segment

        # Draw everything
        window.fill(BLACK)
        draw_snake(snake_body, direction)  # Pass direction to draw_snake
        draw_food(food)
        pygame.display.flip()

        # Control the game speed (modified to use base speed of 5)
        clock.tick(5 + game_speed * 2)

    # Save high score when the game ends
    save_high_score(high_score)
    print(f"Game Over! Your score: {score}, High Score: {high_score}")

    pygame.quit()

if __name__ == "__main__":
    main()