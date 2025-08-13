import pygame
import math
import time
from enum import Enum

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 800
ARENA_RADIUS = 350
STAR_RADIUS = ARENA_RADIUS * 0.065  # 13% of arena diameter (30% bigger than 10%)
RING_WIDTH = STAR_RADIUS * 1.2  # Even thicker rings
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 150, 255)
PURPLE = (128, 0, 128)

class GameState(Enum):
    SETUP = 1
    PLAYING = 2
    PAUSED = 3

class Ring:
    def __init__(self, star):
        self.star = star
        self.base_radius = STAR_RADIUS * 1.5  # Initial ring radius, slightly outside star
        self.expansion_level = 0  # How many times the ring has expanded
        self.warning_duration = 2.0  # 2 seconds warning phase
        self.damage_duration = 0.5  # 0.5 seconds damage phase
        self.cycle_duration = self.warning_duration + self.damage_duration  # Total 2.5 seconds per cycle
        self.expansion_interval = 3.0  # Move to next position every 3 seconds
        
    def update(self, current_time, simulation_start_time):
        # Calculate time since simulation started
        elapsed = current_time - simulation_start_time
        
        # Check if it's time to expand to next position
        expected_expansions = int(elapsed / self.expansion_interval)
        if expected_expansions > self.expansion_level:
            self.expansion_level = expected_expansions
            
    def get_radius(self):
        # Each expansion adds more distance
        return self.base_radius + (self.expansion_level * STAR_RADIUS * 2)
    
    def get_phase_and_alpha(self, current_time, simulation_start_time):
        # Calculate time since this ring reached current position
        time_at_position = (current_time - simulation_start_time) - (self.expansion_level * self.expansion_interval)
        
        # Determine which phase of the cycle we're in
        cycle_time = time_at_position % self.cycle_duration
        
        if cycle_time < self.warning_duration:
            # Warning phase - purple ring on ground
            return "warning", 120
        else:
            # Damage phase - bright red/orange flash
            return "damage", 200
            
    def draw(self, screen, current_time, simulation_start_time):
        # Draw the ring at its current expansion level
        ring_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        
        radius = self.get_radius()
        phase, alpha = self.get_phase_and_alpha(current_time, simulation_start_time)
        
        if phase == "warning":
            # Purple warning ring
            color_with_alpha = (*PURPLE, alpha)
        else:
            # Red damage flash
            color_with_alpha = (255, 0, 0, alpha)  # Pure red for damage
            
        pygame.draw.circle(ring_surface, color_with_alpha, 
                         (int(self.star.x), int(self.star.y)), 
                         int(radius), int(RING_WIDTH))
        
        screen.blit(ring_surface, (0, 0))

class Star:
    def __init__(self, x, y, clockwise=True):
        self.start_x = x
        self.start_y = y
        self.x = x
        self.y = y
        self.clockwise = clockwise
        self.angle = math.atan2(y - WINDOW_HEIGHT//2, x - WINDOW_WIDTH//2)
        self.ring = Ring(self)  # Each star has one ring
        
    def update(self, current_time, is_playing, simulation_start_time):
        if not is_playing:
            return
            
        # No delay - start immediately
            
        # Rotate the star
        rotation_speed = 0.05  # radians per second (much slower rotation)
        if self.clockwise:
            self.angle += rotation_speed / FPS
        else:
            self.angle -= rotation_speed / FPS
            
        # Update position based on angle
        center_x = WINDOW_WIDTH // 2
        center_y = WINDOW_HEIGHT // 2
        distance = math.sqrt((self.start_x - center_x)**2 + (self.start_y - center_y)**2)
        
        self.x = center_x + distance * math.cos(self.angle)
        self.y = center_y + distance * math.sin(self.angle)
        
        # Update the ring
        self.ring.update(current_time, simulation_start_time)
    
    def draw(self, screen):
        # Draw the background circle first
        circle_color = BLUE if self.clockwise else PURPLE
        circle_radius = STAR_RADIUS * 1.3  # Slightly larger than the star
        pygame.draw.circle(screen, circle_color, (int(self.x), int(self.y)), int(circle_radius))
        
        # Draw the star on top
        points = []
        for i in range(5):
            angle = -math.pi/2 + (i * 2 * math.pi / 5)
            outer_x = self.x + STAR_RADIUS * math.cos(angle)
            outer_y = self.y + STAR_RADIUS * math.sin(angle)
            points.append((outer_x, outer_y))
            
            angle = -math.pi/2 + ((i + 0.5) * 2 * math.pi / 5)
            inner_x = self.x + (STAR_RADIUS * 0.4) * math.cos(angle)
            inner_y = self.y + (STAR_RADIUS * 0.4) * math.sin(angle)
            points.append((inner_x, inner_y))
        
        pygame.draw.polygon(screen, YELLOW, points)
        
    def draw_ring(self, screen, current_time, simulation_start_time):
        self.ring.draw(screen, current_time, simulation_start_time)

class Arena:
    def __init__(self):
        self.center_x = WINDOW_WIDTH // 2
        self.center_y = WINDOW_HEIGHT // 2
        self.radius = ARENA_RADIUS
        
    def draw(self, screen):
        # Draw arena border
        pygame.draw.circle(screen, WHITE, (self.center_x, self.center_y), 
                         self.radius, 3)
        
        # Draw arena floor with slight transparency
        floor_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        pygame.draw.circle(floor_surface, (*GRAY, 30), 
                         (self.center_x, self.center_y), self.radius)
        screen.blit(floor_surface, (0, 0))

class WoWBossSimulation:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("WoW Boss Fight Simulation")
        self.clock = pygame.time.Clock()
        self.running = True
        
        self.arena = Arena()
        self.stars = []
        self.state = GameState.SETUP
        self.simulation_start_time = 0
        
        # Fonts
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    if self.state == GameState.SETUP and len(self.stars) == 6:
                        self.state = GameState.PLAYING
                        self.simulation_start_time = time.time()
                    elif self.state == GameState.PLAYING:
                        self.state = GameState.PAUSED
                    elif self.state == GameState.PAUSED:
                        self.state = GameState.PLAYING
                elif event.key == pygame.K_r:
                    self.reset()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and self.state == GameState.SETUP:
                    if len(self.stars) < 6:
                        x, y = event.pos
                        # Check if click is within arena
                        dist = math.sqrt((x - self.arena.center_x)**2 + 
                                       (y - self.arena.center_y)**2)
                        if dist < self.arena.radius - STAR_RADIUS:
                            # First 3 are clockwise (blue), next 3 are counter-clockwise (purple)
                            clockwise = len(self.stars) < 3
                            self.stars.append(Star(x, y, clockwise))
    
    def reset(self):
        self.stars = []
        self.state = GameState.SETUP
        self.simulation_start_time = 0
    
    def update(self):
        current_time = time.time()
        is_playing = self.state == GameState.PLAYING
        
        for star in self.stars:
            star.update(current_time, is_playing, self.simulation_start_time)
    
    def draw(self):
        self.screen.fill(BLACK)
        
        # Draw arena
        self.arena.draw(self.screen)
        
        # Draw rings first (so they appear under stars)
        current_time = time.time()
        for star in self.stars:
            star.draw_ring(self.screen, current_time, self.simulation_start_time)
        
        # Draw stars
        for star in self.stars:
            star.draw(self.screen)
        
        # Draw UI text
        if self.state == GameState.SETUP:
            text = self.font.render(f"Place {6 - len(self.stars)} more stars", 
                                  True, WHITE)
            self.screen.blit(text, (10, 10))
            
            instructions = [
                "Click to place stars",
                "Space to start when all 6 are placed",
                "R to reset"
            ]
            for i, instruction in enumerate(instructions):
                text = self.small_font.render(instruction, True, WHITE)
                self.screen.blit(text, (10, WINDOW_HEIGHT - 80 + i * 25))
                
        elif self.state == GameState.PLAYING:
            text = self.font.render("Simulation Running", True, WHITE)
            self.screen.blit(text, (10, 10))
                
            instructions = [
                "Space to pause",
                "R to reset"
            ]
            for i, instruction in enumerate(instructions):
                text = self.small_font.render(instruction, True, WHITE)
                self.screen.blit(text, (10, WINDOW_HEIGHT - 55 + i * 25))
                
        elif self.state == GameState.PAUSED:
            text = self.font.render("PAUSED", True, WHITE)
            self.screen.blit(text, (10, 10))
            
            instructions = [
                "Space to resume",
                "R to reset"
            ]
            for i, instruction in enumerate(instructions):
                text = self.small_font.render(instruction, True, WHITE)
                self.screen.blit(text, (10, WINDOW_HEIGHT - 55 + i * 25))
        
        pygame.display.flip()
    
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()

if __name__ == "__main__":
    game = WoWBossSimulation()
    game.run()