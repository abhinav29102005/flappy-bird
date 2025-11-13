import pygame
import random
import sys
import json
import os

# --- Pygame and Screen Setup ---
pygame.init()
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.NOFRAME)
FPS = 60
clock = pygame.time.Clock()

# --- Colors ---
SKY_BLUE = (135, 206, 235)
YELLOW = (255, 255, 0)
GREEN = (0, 200, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# --- Profile System ---
def load_profiles(filename="profiles.json"):
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return json.load(f)
    else:
        return {}

def save_profiles(profiles, filename="profiles.json"):
    with open(filename, "w") as f:
        json.dump(profiles, f, indent=2)

def get_profile(email, profiles):
    if email not in profiles:
        profiles[email] = {"scores": [], "best": 0}
    return profiles[email]

# --- Email Input on Pygame Window ---
def enter_email():
    font_big = pygame.font.Font(None, HEIGHT // 13)
    font_small = pygame.font.Font(None, HEIGHT // 22)
    input_text = ""
    active = True
    err = ""
    while active:
        screen.fill(BLACK)
        title = font_big.render("Enter your email:", True, WHITE)
        rect = title.get_rect(center=(WIDTH//2, HEIGHT//3))
        screen.blit(title, rect)
        hint = font_small.render("Press ENTER to submit. ESC to quit.", True, WHITE)
        rect2 = hint.get_rect(center=(WIDTH//2, HEIGHT//3+60))
        screen.blit(hint, rect2)
        input_box = font_big.render(input_text + "_", True, YELLOW)
        input_rect = input_box.get_rect(center=(WIDTH//2, HEIGHT//2))
        screen.blit(input_box, input_rect)
        if err:
            err_msg = font_small.render(err, True, (255, 100, 100))
            err_rect = err_msg.get_rect(center=(WIDTH//2, HEIGHT//2+50))
            screen.blit(err_msg, err_rect)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if '@' in input_text and '.' in input_text:
                        return input_text.lower().strip()
                    err = "Invalid email address!"
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                else:
                    if len(event.unicode) and event.unicode.isprintable():
                        input_text += event.unicode
                        err = ""

# --- Bird, Pipe, and Game Classes ---
class Bird:
    def __init__(self):
        self.x = WIDTH // 6
        self.y = HEIGHT // 2
        self.width = WIDTH // 18
        self.height = HEIGHT // 24
        self.velocity = 0

    def flap(self):
        self.velocity = -HEIGHT // 55

    def update(self):
        self.velocity += 0.5
        self.y += self.velocity

    def draw(self):
        pygame.draw.rect(screen, YELLOW, (self.x, self.y, self.width, self.height))
        pygame.draw.circle(screen, BLACK,
                           (self.x + int(self.width * 0.75), int(self.y + self.height/2)),
                           self.width // 8)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class Pipe:
    def __init__(self, x):
        self.x = x
        self.width = WIDTH // 14
        self.gap = HEIGHT // 3
        self.top_height = random.randint(HEIGHT // 10, HEIGHT - self.gap - HEIGHT // 10)
        self.scored = False

    def update(self):
        self.x -= max(2, int(WIDTH / 200))

    def draw(self):
        pygame.draw.rect(screen, GREEN, (self.x, 0, self.width, self.top_height))
        pygame.draw.rect(screen, GREEN, (self.x, self.top_height + self.gap, self.width,
                                         HEIGHT - self.top_height - self.gap))
        pygame.draw.rect(screen, (0, 150, 0),
                         (self.x - 5, self.top_height - 20, self.width + 10, 20))
        pygame.draw.rect(screen, (0, 150, 0),
                         (self.x - 5, self.top_height + self.gap, self.width + 10, 20))

    def collide(self, bird):
        bird_rect = bird.get_rect()
        top_pipe = pygame.Rect(self.x, 0, self.width, self.top_height)
        bottom_pipe = pygame.Rect(self.x, self.top_height + self.gap, self.width,
                                 HEIGHT - self.top_height - self.gap)
        return bird_rect.colliderect(top_pipe) or bird_rect.colliderect(bottom_pipe)

    def off_screen(self):
        return self.x + self.width < 0

class Game:
    def __init__(self):
        self.bird = Bird()
        self.pipes = []
        self.score = 0
        self.game_over = False
        self.last_pipe = pygame.time.get_ticks()

    def spawn_pipe(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_pipe > 1500:
            self.pipes.append(Pipe(WIDTH))
            self.last_pipe = current_time

    def update(self):
        if not self.game_over:
            self.bird.update()
            # Game over for floor/ceiling
            if self.bird.y <= 0 or self.bird.y + self.bird.height >= HEIGHT:
                self.game_over = True
            for pipe in self.pipes[:]:
                pipe.update()
                if pipe.collide(self.bird):
                    self.game_over = True
                # Score
                if pipe.x + pipe.width < self.bird.x and not pipe.scored:
                    pipe.scored = True
                    self.score += 1
                if pipe.off_screen():
                    self.pipes.remove(pipe)
            self.spawn_pipe()

    def draw(self):
        screen.fill(SKY_BLUE)
        pygame.draw.rect(screen, (222, 216, 149),
                         (0, HEIGHT-HEIGHT//14, WIDTH, HEIGHT//14))
        self.bird.draw()
        for pipe in self.pipes:
            pipe.draw()
        font = pygame.font.Font(None, HEIGHT // 7)
        score_text = font.render(str(self.score), True, WHITE)
        score_outline = font.render(str(self.score), True, BLACK)
        screen.blit(score_outline, (WIDTH // 2 - HEIGHT // 20, HEIGHT // 13 + 2))
        screen.blit(score_text, (WIDTH // 2 - HEIGHT // 22, HEIGHT // 13))
        if self.game_over:
            game_over_font = pygame.font.Font(None, HEIGHT // 6)
            game_over_text = game_over_font.render("GAME OVER", True, WHITE)
            game_over_outline = game_over_font.render("GAME OVER", True, BLACK)
            screen.blit(game_over_outline,
                        (WIDTH // 2 - HEIGHT // 4, HEIGHT // 2 - HEIGHT // 13))
            screen.blit(game_over_text,
                        (WIDTH // 2 - HEIGHT // 4 + 4, HEIGHT // 2 - HEIGHT // 13 + 3))
            restart_font = pygame.font.Font(None, HEIGHT // 22)
            restart_text = restart_font.render("Press SPACE for next attempt or ESC to Quit",
                                               True, WHITE)
            screen.blit(restart_text,
                        (WIDTH // 2 - HEIGHT // 4, HEIGHT // 2 + HEIGHT // 30))

# --- Profile Screen in Pygame Window ---
def show_profile(email, profile, attempt_number):
    font_title = pygame.font.Font(None, HEIGHT//14)
    font_body = pygame.font.Font(None, HEIGHT//22)
    screen.fill(BLACK)
    y = HEIGHT // 8
    msgs = [
        f"Welcome, {email}",
        f"Attempt {attempt_number}/2" if attempt_number <= 2 else "Attempts finished.",
        f"Your best score: {profile['best']}",
        f"Previous attempts: {profile['scores']}" if profile['scores'] else "No previous attempts.",
        "Press SPACE to start!" if attempt_number <= 2 else "Thanks for playing!"
    ]
    for msg in msgs:
        rendered = font_title.render(msg, True, WHITE) if y == HEIGHT // 8 else font_body.render(msg, True, WHITE)
        rect = rendered.get_rect(center=(WIDTH//2, y))
        screen.blit(rendered, rect)
        y += HEIGHT // 12
    pygame.display.flip()
    if attempt_number > 2:
        pygame.time.wait(2000)
        pygame.quit(); sys.exit()
    wait_for_space()

def wait_for_space():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                return
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit()

# --- Main Loop ---
def main():
    profiles = load_profiles()
    email = enter_email()
    profile = get_profile(email, profiles)
    attempt = 1 if not profile["scores"] else len(profile["scores"]) + 1
    show_profile(email, profile, attempt)
    while attempt <= 2:
        game = Game()
        running = True
        while running:
            clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    save_profiles(profiles)
                    pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        save_profiles(profiles)
                        pygame.quit(); sys.exit()
                    if event.key == pygame.K_SPACE:
                        if not game.game_over:
                            game.bird.flap()
                        else:
                            profile["scores"].append(game.score)
                            profile["scores"] = profile["scores"][-2:]
                            profile["best"] = max(profile["scores"])
                            save_profiles(profiles)
                            attempt += 1
                            show_profile(email, profile, attempt)
                            running = False
                            break
            game.update()
            game.draw()
            pygame.display.flip()

if __name__ == "__main__":
    main()
