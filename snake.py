import pygame
import random
import os

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
GRID_SIZE = 20
GRID_WIDTH = WINDOW_WIDTH // GRID_SIZE
GRID_HEIGHT = WINDOW_HEIGHT // GRID_SIZE
FONT_SIZE = 32
HIGH_SCORE_FILE = "high_score.txt"

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GRAY = (128, 128, 128)

# Set up the display
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Snake Game')
font = pygame.font.Font(None, FONT_SIZE)

class Snake:
    def __init__(self):
        self.body = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = (1, 0)
        self.grow = False

    def move(self):
        head = self.body[0]
        new_head = (head[0] + self.direction[0], head[1] + self.direction[1])

        # Check for collisions with walls or itself
        if (new_head[0] < 0 or new_head[0] >= GRID_WIDTH or 
            new_head[1] < 0 or new_head[1] >= GRID_HEIGHT or 
            new_head in self.body[1:]):
            return False

        self.body.insert(0, new_head)
        if not self.grow:
            self.body.pop()
        self.grow = False
        return True

    def change_direction(self, new_direction):
        # Prevent 180-degree turns
        if (new_direction[0] * -1, new_direction[1] * -1) != self.direction:
            self.direction = new_direction

    def reset(self):
        self.body = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = (1, 0)
        self.grow = False

    def get_head(self):
        return self.body[0]

def load_high_score():
    if os.path.exists(HIGH_SCORE_FILE):
        with open(HIGH_SCORE_FILE, 'r') as file:
            return int(file.read())
    return 0

def save_high_score(score):
    with open(HIGH_SCORE_FILE, 'w') as file:
        file.write(str(score))

def generate_food(snake_body):
    while True:
        food = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
        if food not in snake_body:
            return food

def get_initial_speed():
    try:
        speed = int(input("Enter the initial game speed (1-20, default is 8): "))
        if 1 <= speed <= 20:
            return speed
        else:
            print("Invalid input. Using default speed.")
    except ValueError:
        print("Invalid input. Using default speed.")
    return 8

def main():
    clock = pygame.time.Clock()
    snake = Snake()
    food = generate_food(snake.body)
    running = True
    game_active = False
    paused = False
    score = 0
    high_score = load_high_score()
    game_speed = get_initial_speed()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not game_active:
                    # Reset and start new game
                    snake.reset()
                    food = generate_food(snake.body)
                    score = 0
                    game_active = True
                elif event.key == pygame.K_p and game_active:
                    paused = not paused
                elif event.key == pygame.K_q:
                    running = False
                elif game_active and not paused:
                    if event.key == pygame.K_UP:
                        snake.change_direction((0, -1))
                    elif event.key == pygame.K_DOWN:
                        snake.change_direction((0, 1))
                    elif event.key == pygame.K_LEFT:
                        snake.change_direction((-1, 0))
                    elif event.key == pygame.K_RIGHT:
                        snake.change_direction((1, 0))
                    elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                        game_speed += 1
                    elif event.key == pygame.K_MINUS and game_speed > 1:
                        game_speed -= 1

        screen.fill(BLACK)

        if game_active and not paused:
            # Move snake
            if not snake.move():
                game_active = False
                if score > high_score:
                    high_score = score
                    save_high_score(high_score)
                continue

            # Check for food collision
            if snake.body[0] == food:
                snake.grow = True
                score += 10
                food = generate_food(snake.body)

            # Draw food and snake
            pygame.draw.rect(screen, RED, (food[0] * GRID_SIZE, food[1] * GRID_SIZE, 
                                           GRID_SIZE - 2, GRID_SIZE - 2))
            
            for segment in snake.body:
                pygame.draw.rect(screen, GREEN, (segment[0] * GRID_SIZE, segment[1] * GRID_SIZE, 
                                                 GRID_SIZE - 2, GRID_SIZE - 2))

        # Draw scores and messages
        score_text = font.render(f'Score: {score}', True, WHITE)
        high_score_text = font.render(f'High Score: {high_score}', True, WHITE)
        speed_text = font.render(f'Speed: {game_speed}', True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(high_score_text, (WINDOW_WIDTH - high_score_text.get_width() - 10, 10))
        screen.blit(speed_text, (10, FONT_SIZE + 10))

        if not game_active:
            if score > 0:
                game_over_text = font.render('Game Over! Press SPACE to Restart', True, WHITE)
                text_rect = game_over_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
                screen.blit(game_over_text, text_rect)
                final_score_text = font.render(f'Final Score: {score}', True, WHITE)
                final_rect = final_score_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 40))
                screen.blit(final_score_text, final_rect)

        if paused:
            pause_text = font.render('PAUSED', True, WHITE)
            pause_rect = pause_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            screen.blit(pause_text, pause_rect)

        pygame.display.flip()
        clock.tick(game_speed)

    # Cleanup
    pygame.quit()

if __name__ == '__main__':
    main()
