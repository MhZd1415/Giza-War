import sys
import os
import logging
import traceback
import time

"""
Tank Game - Main Entry Point
---------------------------
This is the main entry point for the Tank Game.
It initializes the game environment, sets up logging,
and runs the main game loop.
"""

# Configure game root paths before any imports
GAME_ROOT = os.path.dirname(os.path.abspath(__file__))

# Add the game directory to Python path BEFORE any imports
sys.path.append(GAME_ROOT)

# Adding module paths using proper package structure
sys.path.append(os.path.join(GAME_ROOT, "entities"))
sys.path.append(os.path.join(GAME_ROOT, "utils"))
sys.path.append(os.path.join(GAME_ROOT, "ui"))
sys.path.append(os.path.join(GAME_ROOT, "assets"))
sys.path.append(os.path.join(GAME_ROOT, "world"))

def setup_logging():
    """Configure and set up logging for the game"""
    log_file = os.path.join(GAME_ROOT, "game.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger("TankGame")

def init_pygame():
    """Initialize all pygame modules safely"""
    try:
        import pygame
        pygame.init()
        pygame.mixer.init()
        pygame.font.init()
        return True
    except Exception as e:
        logging.error(f"Failed to initialize pygame: {e}")
        return False

def main():
    """Main entry point for the game"""
    # Set up logging
    logger = setup_logging()
    logger.info("Starting game initialization")
    
    # Initialize pygame
    if not init_pygame():
        logger.critical("Failed to initialize pygame. Exiting.")
        return 1
    
    try:
        # Try to import game-specific modules
        logger.info("Importing game modules...")
        try:
            import pygame
            from utils.config import load_configuration
            
            # This is where syntax errors in game.py would be caught
            logger.info("Importing Game class...")
            from game import Game
            logger.info("Game class imported successfully")
        except SyntaxError as se:
            logger.critical(f"Syntax error in game code: {se}")
            logger.critical(f"Error location: {se.filename}, line {se.lineno}, offset {se.offset}")
            logger.critical(f"Error text: {se.text}")
            return 1
        except ImportError as ie:
            logger.critical(f"Import error: {ie}")
            logger.critical("Make sure all required modules are installed and in the Python path")
            return 1
        
        # Load configuration
        config = load_configuration()
        screen_width = config.get('screen_width', 1280)
        screen_height = config.get('screen_height', 720)
        
        logger.info(f"Game window size: {screen_width}x{screen_height}")
        
        # Create game instance with screen dimensions and run it
        game = Game(screen_width=screen_width, screen_height=screen_height)
        
        # Set up event handlers
        pygame.event.set_allowed([pygame.KEYDOWN, pygame.QUIT])
        
        # Run the game
        logger.info("Starting game loop")
        game.run()
        
        # Clean exit
        logger.info("Game loop ended normally")
        return 0
        
    except Exception as fatal_error:
        logger.critical(f"Fatal error caused crash: {str(fatal_error)}")
        traceback.print_exc()
        
        # Create crash report
        crash_report_path = os.path.join(GAME_ROOT, "crash_report.txt")
        with open(crash_report_path, 'w') as f:
            f.write(f"Game crashed at {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Error: {str(fatal_error)}\n")
            f.write(traceback.format_exc())
            
        logger.info(f"Crash report written to {crash_report_path}")
        return 1
    
    finally:
        logger.info("Initiating controlled shutdown")
        
        # Save game state if possible
        try:
            if 'game' in locals():
                if hasattr(game, 'save_state'):
                    game.save_state()
                    logger.info("Game state saved")
        except Exception as shutdown_error:
            logger.error(f"Error during state saving: {str(shutdown_error)}")
            
        # Shut down pygame
        logger.info("Shutting down pygame modules")
        if pygame.get_init():
            try:
                pygame.quit()
                logger.info("Pygame shutdown successful")
            except Exception as pygame_shutdown_error:
                logger.error(f"Pygame shutdown error: {str(pygame_shutdown_error)}")

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
