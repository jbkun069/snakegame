import pygame
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
    """Get the initial game speed from the user."""
    while True:
        try:
            speed = int(input("Enter the initial game speed (1-20, default is 8): "))
            if 1 <= speed <= 20:
                return speed
            else:
                print("Invalid input. Please enter a number between 1 and 20.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")

def draw_grid():
    """Draw the grid on the window."""
    for x in range(0, WINDOW_WIDTH, CELL_SIZE):
        pygame.draw.line(window, WHITE, (x, 0), (x, WINDOW_HEIGHT))
    for y in range(0, WINDOW_HEIGHT, CELL_SIZE):
        pygame.draw.line(window, WHITE, (0, y), (WINDOW_WIDTH, y))

def draw_snake(snake_body):
    """Draw the snake on the window."""
    for segment in snake_body:
        pygame.draw.rect(window, GREEN, (segment[0] * CELL_SIZE, segment[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE))

def draw_food(food_position):
    """Draw the food on the window."""
    pygame.draw.rect(window, RED, (food_position[0] * CELL_SIZE, food_position[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE))

def main():
    """Main function to run the Snake game."""
    snake_body = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
    direction = (1, 0)
    food = generate_food(snake_body)
    game_speed = get_initial_speed()
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
        draw_grid()
        draw_snake(snake_body)
        draw_food(food)
        pygame.display.flip()

        # Control the game speed
        clock.tick(10 + game_speed)

    # Save high score when the game ends
    save_high_score(high_score)
    print(f"Game Over! Your score: {score}, High Score: {high_score}")

    pygame.quit()

if __name__ == "__main__":
    main()