import pygame
import random
import neat
import os

# ---------------------- CONSTANTS ----------------------
SCREEN_WIDTH = 720
SCREEN_HEIGHT = 720

# ---------------------- PLAYER ----------------------
class Player:
    def __init__(self):
        self.player_height = 50
        self.player_width = 50
        self.rect = pygame.Rect(
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2,
            self.player_width,
            self.player_height
        )
        self.speed = 10
        self.prev_distance = None

    def move_ai(self, output):
        dx = (output[1] - output[0]) * self.speed
        dy = (output[3] - output[2]) * self.speed
        self.rect.x += dx
        self.rect.y += dy
        return dx, dy

    def draw(self, screen, alpha=60):
        player_surface = pygame.Surface((self.player_width, self.player_height), pygame.SRCALPHA)
        player_surface.fill((0, 255, 0, alpha))
        screen.blit(player_surface, (self.rect.x, self.rect.y))

# ---------------------- ENEMIES ----------------------
class Enemy1:
    def __init__(self):
        self.rect = pygame.Rect(
            random.randint(0, SCREEN_WIDTH - 30),
            0,
            30,
            30
        )
        self.speed = 5

    def move(self):
        self.rect.y += self.speed
        if self.rect.y > SCREEN_HEIGHT:
            self.rect.y = 0
            self.rect.x = random.randint(0, SCREEN_WIDTH - 30)

    def draw(self, screen):
        pygame.draw.rect(screen, (255, 0, 0), self.rect)

class Enemy2:
    def __init__(self):
        self.rect = pygame.Rect(
            0,
            random.randint(0, SCREEN_HEIGHT - 30),
            30,
            30
        )
        self.speed = 5

    def move(self):
        self.rect.x += self.speed
        if self.rect.x > SCREEN_WIDTH:
            self.rect.x = 0
            self.rect.y = random.randint(0, SCREEN_HEIGHT - 30)

    def draw(self, screen):
        pygame.draw.rect(screen, (255, 0, 0), self.rect)

# ---------------------- BORDER ----------------------
class Border:
    def __init__(self, thickness=50):
        self.thickness = thickness
        self.rects = [
            pygame.Rect(0, 0, SCREEN_WIDTH, thickness),  # Top
            pygame.Rect(0, SCREEN_HEIGHT - thickness, SCREEN_WIDTH, thickness),  # Bottom
            pygame.Rect(0, 0, thickness, SCREEN_HEIGHT),  # Left
            pygame.Rect(SCREEN_WIDTH - thickness, 0, thickness, SCREEN_HEIGHT)  # Right
        ]

    def draw(self, screen):
        for rect in self.rects:
            pygame.draw.rect(screen, (255, 255, 0), rect)

# ---------------------- REWARD ----------------------
class Reward:
    def __init__(self, border_thickness=50):
        self.rect = pygame.Rect(
            random.randint(border_thickness, SCREEN_WIDTH - 10 - border_thickness),
            random.randint(border_thickness, SCREEN_HEIGHT - 10 - border_thickness),
            10, 10
        )

    def draw(self, screen):
        pygame.draw.rect(screen, (0, 0, 255), self.rect)

# ---------------------- NEAT EVALUATION ----------------------
def eval_genomes(genomes, config):
    nets = []
    ge = []
    players = []

    for genome_id, genome in genomes:
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        players.append(Player())
        genome.fitness = 0
        ge.append(genome)

    enemy1 = [Enemy1() for _ in range(3)]
    enemy2 = [Enemy2() for _ in range(3)]
    border = Border(thickness=50)
    reward = Reward(border_thickness=border.thickness)

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    pygame.display.set_caption("NEAT AI Training")

    generation_font = pygame.font.Font(None, 30)
    generation = getattr(eval_genomes, "generation", 0)

    run = True
    while run and len(players) > 0:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        screen.fill((0, 0, 0))
        reward.draw(screen)
        border.draw(screen)

        for enemy in enemy1 + enemy2:
            enemy.move()
            enemy.draw(screen)

        for x in range(len(players) - 1, -1, -1):
            player = players[x]

            # --- INPUTS: player, reward, all enemies ---
            inputs = [
                player.rect.x / SCREEN_WIDTH,
                player.rect.y / SCREEN_HEIGHT,
                reward.rect.x / SCREEN_WIDTH,
                reward.rect.y / SCREEN_HEIGHT
            ]
            for enemy in enemy1 + enemy2:
                inputs.append(enemy.rect.x / SCREEN_WIDTH)
                inputs.append(enemy.rect.y / SCREEN_HEIGHT)

            output = nets[x].activate(inputs)
            dx, dy = player.move_ai(output)

            # Highlight best AI
            best_fitness = max(g.fitness for g in ge)
            if ge[x].fitness == best_fitness:
                player.draw(screen, alpha=200)
            else:
                player.draw(screen, alpha=60)

            # --- FITNESS SHAPING ---
            ge[x].fitness += 0.2
            current_distance = ((player.rect.x - reward.rect.x)**2 + (player.rect.y - reward.rect.y)**2)**0.5
            if player.prev_distance is None:
                player.prev_distance = current_distance
            distance_change = player.prev_distance - current_distance
            ge[x].fitness += 0.3 if distance_change > 0 else -0.5
            player.prev_distance = current_distance

            if abs(dx) + abs(dy) > 0.1:
                ge[x].fitness += 0.05

            # --- BORDER COLLISION ---
            if any(player.rect.colliderect(r) for r in border.rects):
                ge[x].fitness -= 10
                players.pop(x)
                nets.pop(x)
                ge.pop(x)
                continue

            # --- REWARD COLLISION ---
            if player.rect.colliderect(reward.rect):
                ge[x].fitness += 5
                reward = Reward(border_thickness=border.thickness)

            # --- ENEMY COLLISION ---
            collided_enemy = False
            for enemy in enemy1 + enemy2:
                if player.rect.colliderect(enemy.rect):
                    ge[x].fitness -= 5
                    players.pop(x)
                    nets.pop(x)
                    ge.pop(x)
                    collided_enemy = True
                    break
            if collided_enemy:
                continue

        # --- HUD ---
        text_gen = generation_font.render(f"Generation: {generation}", True, (255, 255, 255))
        text_alive = generation_font.render(f"Alive: {len(players)}", True, (0, 255, 0))
        screen.blit(text_gen, (10, 10))
        screen.blit(text_alive, (10, 40))

        pygame.display.flip()
        clock.tick(60)

# ---------------------- NEAT RUNNER ----------------------
def run_neat(config_path, n_iterations=1000):
    eval_genomes.generation = 0

    def wrapped_eval(genomes, config):
        eval_genomes.generation += 1
        eval_genomes(genomes, config)

    config = neat.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )

    population = neat.Population(config)
    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)

    winner = population.run(wrapped_eval, n_iterations)
    print("\nBest AI achieved!")
    return winner

# ---------------------- MAIN ----------------------
if __name__ == "__main__":
    pygame.init()
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    run_neat(config_path, n_iterations=1000)
