import pygame
import random
import neat
import math
import pickle
import os


SCREEN_WIDTH, SCREEN_HEIGHT = 720, 720
MAX_ENEMIES = 6


class Player:
    def __init__(self, border_thickness=10):
        self.gap = 5
        self.player_width = 30
        self.player_height = 30
        self.player_color = (0, 255, 0)
        self.border_thickness = border_thickness
        self.rect = pygame.Rect(
            random.randint(border_thickness + self.gap,
                           SCREEN_WIDTH - border_thickness - self.player_width - self.gap),
            SCREEN_HEIGHT - border_thickness - self.player_height - self.gap,
            self.player_width,
            self.player_height
        )
        self.speed = 15

    def move_ai(self, outputs):
        if outputs[0] > 0.5:
            self.rect.x -= self.speed
        if outputs[1] > 0.5:
            self.rect.x += self.speed

    def is_out_of_bounds(self):
        return (self.rect.x < self.border_thickness or
                self.rect.x + self.player_width > SCREEN_WIDTH - self.border_thickness or
                self.rect.y < self.border_thickness or
                self.rect.y + self.player_height > SCREEN_HEIGHT - self.border_thickness)

    def draw(self, screen):
        pygame.draw.rect(screen, self.player_color, self.rect)


class Border:
    def __init__(self, thickness=10):
        self.thickness = thickness
        self.border_color = (225, 225, 225)
        self.border1 = pygame.Rect(0, 0, self.thickness, SCREEN_HEIGHT)
        self.border2 = pygame.Rect(0, 0, SCREEN_WIDTH, self.thickness)
        self.border3 = pygame.Rect(SCREEN_WIDTH - self.thickness, 0, self.thickness, SCREEN_HEIGHT)
        self.border4 = pygame.Rect(0, SCREEN_HEIGHT - self.thickness, SCREEN_WIDTH, self.thickness)

    def draw(self, screen):
        pygame.draw.rect(screen, self.border_color, self.border1)
        pygame.draw.rect(screen, self.border_color, self.border2)
        pygame.draw.rect(screen, self.border_color, self.border3)
        pygame.draw.rect(screen, self.border_color, self.border4)


class Enemy:
    def __init__(self, border_thickness=10, speed=10):
        self.enemy_color = (255, 0, 0)
        self.enemy_width = 30
        self.enemy_height = 30
        self.border_thickness = border_thickness
        self.rect = pygame.Rect(
            random.randint(border_thickness, SCREEN_WIDTH - border_thickness - self.enemy_width),
            0,
            self.enemy_width,
            self.enemy_height
        )
        self.enemy_speed = speed

    def draw(self, screen):
        pygame.draw.rect(screen, self.enemy_color, self.rect)

    def move(self):
        self.rect.y += self.enemy_speed
        if self.rect.y > SCREEN_HEIGHT - self.border_thickness - self.enemy_height:
            self.rect.y = 0
            self.rect.x = random.randint(self.border_thickness, SCREEN_WIDTH - self.border_thickness - self.enemy_width)


# ---------------- Neural Network Visualizer ---------------- #
class NeuralNetworkVisualizer:
    def __init__(self, screen, genome, config, pos=(500, 80), size=(200, 500)):
        self.screen = screen
        self.genome = genome
        self.config = config
        self.pos = pos
        self.size = size

    def draw_network(self, activations):
        x, y = self.pos
        w, h = self.size
        node_positions = {}

        # Determine layers
        input_nodes = self.config.genome_config.input_keys
        output_nodes = self.config.genome_config.output_keys

        # Input positions
        spacing_y = h / (len(input_nodes) + 1)
        for i, nid in enumerate(input_nodes):
            node_positions[nid] = (x, y + spacing_y * (i + 1))

        # Output positions
        spacing_y = h / (len(output_nodes) + 1)
        for i, nid in enumerate(output_nodes):
            node_positions[nid] = (x + w, y + spacing_y * (i + 1))

        # Hidden nodes
        hidden_nodes = [n for n in self.genome.nodes.keys()
                        if n not in input_nodes and n not in output_nodes]
        if hidden_nodes:
            spacing_y = h / (len(hidden_nodes) + 1)
            for i, nid in enumerate(hidden_nodes):
                node_positions[nid] = (x + w / 2, y + spacing_y * (i + 1))

        # Draw connections
        for key, conn in self.genome.connections.items():
            if not conn.enabled:
                continue
            n1, n2 = key
            if n1 not in node_positions or n2 not in node_positions:
                continue
            x1, y1 = node_positions[n1]
            x2, y2 = node_positions[n2]
            weight = conn.weight
            color = (0, 255, 0) if weight > 0 else (255, 0, 0)
            thickness = max(1, int(abs(weight) * 2))
            pygame.draw.line(self.screen, color, (x1, y1), (x2, y2), thickness)

        # Draw nodes
        for nid, (nx, ny) in node_positions.items():
            activation = activations.get(nid, 0)
            brightness = int(255 * min(1, max(0, (activation + 1) / 2)))
            if nid in input_nodes:
                color = (0, brightness, 0)
            elif nid in output_nodes:
                color = (brightness, 0, 0)
            else:
                color = (0, 0, brightness)
            pygame.draw.circle(self.screen, color, (int(nx), int(ny)), 8)


# ---------------- NEAT Training ---------------- #
def train_genomes(genomes, config):
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Avoid Cubes (NEAT) - Improved")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 36)

    border_thickness = 20
    border = Border(border_thickness)

    # Prepare genome/network/player lists
    nets, ge, players = [], [], []

    for genome_id, genome in genomes:
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        players.append(Player(border_thickness=border_thickness))
        genome.fitness = 0
        ge.append(genome)

    # Visualizer for the best genome (first in list)
    visualizer = NeuralNetworkVisualizer(screen, ge[0], config)

    # Fixed enemies
    initial_speed = 10
    enemies = [Enemy(border_thickness=border_thickness, speed=initial_speed) for _ in range(MAX_ENEMIES)]

    survival_time = 0
    active_players = [True for _ in players]

    while any(active_players):
        screen.fill((0, 0, 0))
        border.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

        # Move and draw enemies
        for enemy in enemies:
            enemy.move()
            enemy.draw(screen)

        best_idx = 0  # we'll visualize this one's network
        best_activations = {}

        # Move players
        for idx, player in enumerate(players):
            if not active_players[idx]:
                continue

            # --- Improved input design ---
            inputs = [
                player.rect.x / SCREEN_WIDTH,
                player.rect.y / SCREEN_HEIGHT
            ]
            for enemy in enemies:
                rel_x = (enemy.rect.x - player.rect.x) / SCREEN_WIDTH
                rel_y = (enemy.rect.y - player.rect.y) / SCREEN_HEIGHT
                vel_y = enemy.enemy_speed / 25.0
                inputs += [rel_x, rel_y, vel_y]

            # Activate NN
            outputs = nets[idx].activate(inputs)
            player.move_ai(outputs)
            player.draw(screen)

            # Store activations for visualizer if this is the best one
            if idx == best_idx:
                # Build a simple activation dict for coloring (approximation)
                best_activations = {i: val for i, val in enumerate(inputs)}
                best_activations.update({100 + i: outputs[i] for i in range(len(outputs))})

            # --- Fitness function ---
            ge[idx].fitness += 0.1  # survival reward

            # Reward distance from nearest enemy
            nearest_enemy = min(enemies, key=lambda e: abs(player.rect.centerx - e.rect.centerx) +
                                                abs(player.rect.centery - e.rect.centery))
            dist = math.sqrt((player.rect.centerx - nearest_enemy.rect.centerx) ** 2 +
                             (player.rect.centery - nearest_enemy.rect.centery) ** 2)
            ge[idx].fitness += (dist / SCREEN_WIDTH) * 0.5

            # Penalize hugging walls
            if player.rect.x < 40 or player.rect.x > SCREEN_WIDTH - 70:
                ge[idx].fitness -= 0.05

            # Check out of bounds
            if player.is_out_of_bounds():
                ge[idx].fitness -= 1.0
                active_players[idx] = False
                continue

            # Check collision
            for enemy in enemies:
                if player.rect.colliderect(enemy.rect):
                    ge[idx].fitness -= 1.0
                    active_players[idx] = False
                    break

        # Gradually increase enemy speed
        survival_time += 1
        for enemy in enemies:
            enemy.enemy_speed = min(25, initial_speed + survival_time // 300)

        # Display survival time
        score_text = font.render(f"Survival Time: {survival_time // 60}s", True, (200, 150, 50))
        screen.blit(score_text, (border_thickness + 5, border_thickness + 5))

        # Draw best network visualization
        visualizer.draw_network(best_activations)

        pygame.display.flip()
        clock.tick(60)


def run_neat(n_iterations=10000):
    config_file_path = 'config-feedforward.txt'
    config = neat.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_file_path
    )

    population = neat.Population(config)
    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)

    winner = population.run(train_genomes, n_iterations)
    print("\nBest AI achieved.")
    return winner


if __name__ == "__main__":
    pygame.init()
    run_neat()
    pygame.quit()
