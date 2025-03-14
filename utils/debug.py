import pygame
import sys
import os
import logging
import traceback
from datetime import datetime
import time
from collections import deque

# Use this class to disable debugging but keep the interface intact
class DummyDebugger:
    def __init__(self):
        pass
        
    def toggle(self):
        pass
        
    def log_error(self, error):
        pass
        
    def update_frame_time(self, dt):
        pass
        
    def get_fps(self):
        return 60  # Return a default value
        
    def add_debug_info(self, info):
        pass
        
    def clear_debug_info(self):
        pass
        
    def draw(self, surface):
        pass
        
    def check_game_state(self, game):
        pass
        
    def get_debug_info(self):
        return {}

    def set_fps(self, fps):
        """
        Set the current FPS value to display.
        
        Args:
            fps (int): The current frames per second value
        """
        pass
        
    def add_message(self, key, value):
        """
        Add or update a debug message.
        
        Args:
            key (str): The message identifier
            value (str): The message content
        """
        pass
        
    def remove_message(self, key):
        """
        Remove a debug message.
        
        Args:
            key (str): The message identifier to remove
        """
        pass

class GameDebugger:
    def __init__(self):
        self.enabled = False
        self.frame_time = 0
        self.last_error = None
        self.error_count = 0
        self.debug_info = []
        self.frame_times = deque(maxlen=60)  # Store last 60 frame times
        self.max_frame_times = 60  # Add this line to define max_frame_times
        self.error_log = deque(maxlen=10)    # Store last 10 errors
        self.is_active = False
        self.start_time = time.time()
        self.font = pygame.font.SysFont('monospace', 16)
        
        # Create logs directory if it doesn't exist
        self.logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
        os.makedirs(self.logs_dir, exist_ok=True)
        self.log_file = os.path.join(self.logs_dir, f"game_debug_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        logging.basicConfig(filename=self.log_file, level=logging.DEBUG)

    def toggle(self):
        self.enabled = not self.enabled
        self.is_active = not self.is_active
        logging.info(f"Debug mode: {'enabled' if self.enabled else 'disabled'}")
        logging.info(f"Debug overlay {'enabled' if self.is_active else 'disabled'}")

    def log_error(self, error):
        self.last_error = error
        self.error_count += 1
        error_trace = traceback.format_exc()
        logging.error(f"Error #{self.error_count}:\n{error_trace}")
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        self.error_log.append((timestamp, str(error)))
        logging.error(f"Game error: {error}")

    def update_frame_time(self, dt):
        self.frame_time = dt
        self.frame_times.append(dt)
        if len(self.frame_times) > self.max_frame_times:
            self.frame_times.pop(0)
        if dt > 0.1:  # Frame took longer than 100ms
            logging.warning(f"Performance warning: Frame took {dt*1000:.2f}ms")

    def get_fps(self):
        if not self.frame_times:
            return 0
        return 1.0 / (sum(self.frame_times) / len(self.frame_times))

    def add_debug_info(self, info):
        self.debug_info.append(info)

    def clear_debug_info(self):
        self.debug_info.clear()

    def draw(self, surface):
        if not self.enabled:
            return

        y = 10
        x = 10
        fps = self.get_fps()
        
        # Draw FPS counter
        fps_text = self.font.render(f'FPS: {fps:.1f}', True, (255, 255, 0))
        surface.blit(fps_text, (x, y))
        y += 20

        # Draw debug information
        for info in self.debug_info:
            text = self.font.render(str(info), True, (255, 255, 0))
            surface.blit(text, (x, y))
            y += 20

        # Draw last error if any
        if self.last_error:
            error_text = self.font.render(
                f"Last Error: {type(self.last_error).__name__}: {str(self.last_error)[:50]}...",
                True, (255, 0, 0))
            surface.blit(error_text, (x, y))

    def check_game_state(self, game):
        """Validate game state and objects"""
        if self.enabled:
            logging.debug(f"Current game state: {game.state}")
            logging.debug(f"FPS: {1.0 / self.frame_time if self.frame_time > 0 else 0}")
        try:
            # Check player state
            if game.player.health < 0:
                raise ValueError("Player health cannot be negative")
            
            # Check enemy positions
            for enemy in game.enemies:
                if not isinstance(enemy.pos[0], (int, float)) or \
                   not isinstance(enemy.pos[1], (int, float)):
                    raise ValueError(f"Invalid enemy position: {enemy.pos}")

            # Check projectile states
            if hasattr(game, 'projectiles'):
                for proj in game.projectiles:
                    # Your projectile debugging code here
                    pass

            return True
        except Exception as e:
            self.log_error(e)
            return False

        if not self.is_active:
            return

        # Check for common crash indicators
        if not pygame.display.get_init():
            self.log_error("Display system lost initialization")
        
        if len(self.frame_times) > 0:
            avg_fps = 1.0 / (sum(self.frame_times) / len(self.frame_times))
            if avg_fps < 30:  # FPS dropped below 30
                logging.warning(f"Performance warning: Average FPS: {avg_fps:.1f}")

    def get_debug_info(self):
        return {
            'enabled': self.enabled,
            'frame_time': self.frame_time,
            'error_count': self.error_count,
            'last_error': str(self.last_error) if self.last_error else None,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
