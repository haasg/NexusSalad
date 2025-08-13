import pygame
import math
import time
from enum import Enum

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 1194  # Match plan.png width
WINDOW_HEIGHT = 671  # Match plan.png height
ARENA_RADIUS = 300  # Adjusted for new window size
FPS = 60

# Default adjustable parameters
DEFAULT_STAR_SIZE = 0.065  # Multiplier of arena radius
DEFAULT_RING_WIDTH = 1.2  # Multiplier of star radius
DEFAULT_ROTATION_SPEED = 0.05  # Radians per second
DEFAULT_RING_START_OFFSET = 1.5  # Multiplier of star radius
DEFAULT_RING_SPACING = 2.0  # Multiplier of star radius

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

class SimulationParams:
    def __init__(self):
        self.star_size = DEFAULT_STAR_SIZE
        self.ring_width = DEFAULT_RING_WIDTH
        self.rotation_speed = DEFAULT_ROTATION_SPEED
        self.ring_start_offset = DEFAULT_RING_START_OFFSET
        self.ring_spacing = DEFAULT_RING_SPACING
        
    def get_star_radius(self):
        return ARENA_RADIUS * self.star_size
        
    def get_ring_width(self):
        return self.get_star_radius() * self.ring_width

class Ring:
    def __init__(self, star, params):
        self.star = star
        self.params = params
        self.base_radius = params.get_star_radius() * params.ring_start_offset
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
        return self.base_radius + (self.expansion_level * self.params.get_star_radius() * self.params.ring_spacing)
    
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
                         int(radius), int(self.params.get_ring_width()))
        
        screen.blit(ring_surface, (0, 0))

class Star:
    def __init__(self, x, y, clockwise, params):
        self.start_x = x
        self.start_y = y
        self.x = x
        self.y = y
        self.clockwise = clockwise
        self.params = params
        self.angle = math.atan2(y - WINDOW_HEIGHT//2, x - WINDOW_WIDTH//2)
        self.ring = Ring(self, params)  # Each star has one ring
        
    def update(self, current_time, is_playing, simulation_start_time):
        if not is_playing:
            return
            
        # No delay - start immediately
            
        # Rotate the star
        if self.clockwise:
            self.angle += self.params.rotation_speed / FPS
        else:
            self.angle -= self.params.rotation_speed / FPS
            
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
        star_radius = self.params.get_star_radius()
        circle_radius = star_radius * 1.3  # Slightly larger than the star
        pygame.draw.circle(screen, circle_color, (int(self.x), int(self.y)), int(circle_radius))
        
        # Draw the star on top
        points = []
        for i in range(5):
            angle = -math.pi/2 + (i * 2 * math.pi / 5)
            outer_x = self.x + star_radius * math.cos(angle)
            outer_y = self.y + star_radius * math.sin(angle)
            points.append((outer_x, outer_y))
            
            angle = -math.pi/2 + ((i + 0.5) * 2 * math.pi / 5)
            inner_x = self.x + (star_radius * 0.4) * math.cos(angle)
            inner_y = self.y + (star_radius * 0.4) * math.sin(angle)
            points.append((inner_x, inner_y))
        
        pygame.draw.polygon(screen, YELLOW, points)
        
    def draw_ring(self, screen, current_time, simulation_start_time):
        self.ring.draw(screen, current_time, simulation_start_time)

class Arena:
    def __init__(self):
        # Position arena slightly to the left to make room for controls
        self.center_x = 400
        self.center_y = WINDOW_HEIGHT // 2
        self.radius = ARENA_RADIUS
        
        # Load the background image
        try:
            self.background = pygame.image.load("plan.png")
            # Use image at original resolution
        except:
            self.background = None
            print("Could not load plan.png, using default arena")
        
    def draw(self, screen):
        if self.background:
            # Draw the background image at (0, 0)
            screen.blit(self.background, (0, 0))
        else:
            # Fallback to original arena if image not loaded
            pygame.draw.circle(screen, WHITE, (self.center_x, self.center_y), 
                             self.radius, 3)
            
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
        
        # Simulation parameters
        self.params = SimulationParams()
        
        # UI state
        self.selected_param = 0
        self.param_names = [
            ("Star Size", "star_size", 0.01, 0.2, 0.005),
            ("Ring Width", "ring_width", 0.5, 3.0, 0.1),
            ("Rotation Speed", "rotation_speed", 0.01, 0.2, 0.01),
            ("Ring Start Offset", "ring_start_offset", 0.5, 3.0, 0.1),
            ("Ring Spacing", "ring_spacing", 1.0, 5.0, 0.2)
        ]
        
        # Fonts
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.tiny_font = pygame.font.Font(None, 20)
        
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
                elif event.key == pygame.K_UP:
                    self.selected_param = (self.selected_param - 1) % len(self.param_names)
                elif event.key == pygame.K_DOWN:
                    self.selected_param = (self.selected_param + 1) % len(self.param_names)
                elif event.key == pygame.K_LEFT:
                    self.adjust_param(-1)
                elif event.key == pygame.K_RIGHT:
                    self.adjust_param(1)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and self.state == GameState.SETUP:
                    if len(self.stars) < 6:
                        x, y = event.pos
                        # Check if click is within arena
                        dist = math.sqrt((x - self.arena.center_x)**2 + 
                                       (y - self.arena.center_y)**2)
                        if dist < self.arena.radius - self.params.get_star_radius():
                            # First 3 are clockwise (blue), next 3 are counter-clockwise (purple)
                            clockwise = len(self.stars) < 3
                            self.stars.append(Star(x, y, clockwise, self.params))
    
    def adjust_param(self, direction):
        name, attr, min_val, max_val, step = self.param_names[self.selected_param]
        current = getattr(self.params, attr)
        new_val = current + (step * direction)
        new_val = max(min_val, min(max_val, new_val))
        setattr(self.params, attr, new_val)
        
        # Update existing stars and rings if needed
        for star in self.stars:
            star.params = self.params
            star.ring.params = self.params
    
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
                "R to reset",
                "Arrow keys to adjust parameters"
            ]
            for i, instruction in enumerate(instructions):
                text = self.small_font.render(instruction, True, WHITE)
                self.screen.blit(text, (10, WINDOW_HEIGHT - 100 + i * 25))
                
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
        
        # Draw parameter controls
        self.draw_parameters()
        
        pygame.display.flip()
    
    def draw_parameters(self):
        # Draw parameter panel background
        panel_x = 850
        panel_y = 50
        panel_width = WINDOW_WIDTH - panel_x - 20
        panel_height = 300
        
        pygame.draw.rect(self.screen, GRAY, (panel_x, panel_y, panel_width, panel_height), 2)
        
        # Title
        title = self.small_font.render("PARAMETERS", True, WHITE)
        self.screen.blit(title, (panel_x + 10, panel_y + 10))
        
        # Draw each parameter
        for i, (name, attr, min_val, max_val, step) in enumerate(self.param_names):
            y_offset = panel_y + 50 + i * 45
            
            # Highlight selected parameter
            if i == self.selected_param:
                pygame.draw.rect(self.screen, (100, 100, 100), 
                               (panel_x + 5, y_offset - 5, panel_width - 10, 40))
            
            # Parameter name
            text = self.tiny_font.render(name + ":", True, WHITE)
            self.screen.blit(text, (panel_x + 10, y_offset))
            
            # Current value
            value = getattr(self.params, attr)
            value_text = self.tiny_font.render(f"{value:.3f}", True, YELLOW)
            self.screen.blit(value_text, (panel_x + 10, y_offset + 20))
            
            # Value bar
            bar_x = panel_x + 80
            bar_y = y_offset + 10
            bar_width = 100
            bar_height = 20
            
            # Background bar
            pygame.draw.rect(self.screen, (50, 50, 50), 
                           (bar_x, bar_y, bar_width, bar_height))
            
            # Filled portion
            fill_percent = (value - min_val) / (max_val - min_val)
            fill_width = int(bar_width * fill_percent)
            pygame.draw.rect(self.screen, BLUE if i == self.selected_param else (100, 100, 200), 
                           (bar_x, bar_y, fill_width, bar_height))
            
            # Border
            pygame.draw.rect(self.screen, WHITE, 
                           (bar_x, bar_y, bar_width, bar_height), 1)
    
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