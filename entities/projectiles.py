"""
DEPRECATED MODULE - Use entities.projectile instead

This module is maintained for backward compatibility only.
New code should import directly from entities.projectile.
"""

import logging

# Display deprecation warning
logging.warning("Using deprecated entities.projectiles module. Use entities.projectile instead.")

# Import the actual implementation
from entities.projectile import Projectile, PlayerProjectile, EnemyProjectile, SpecialProjectile

class PiercingProjectile(PlayerProjectile):
    """Legacy piercing projectile that can travel through enemies"""
    def __init__(self, x, y, direction_x, direction_y, speed=10, damage=10, lifetime=180, pierce_count=3):
        super().__init__(x, y, direction_x, direction_y, speed, damage, pierce=True)
        self.pierce_count = pierce_count
        self.hits = []  # Track which enemies this projectile has hit
        
    def hit_enemy(self, enemy_id):
        """Handle a hit with an enemy, decrementing pierce count"""
        # Add to hits list if not already hit
        if enemy_id not in self.hits:
            self.hits.append(enemy_id)
        
        # Check if we've reached maximum pierce count
        return len(self.hits) >= self.pierce_count

class AttackManager:
    """
    DEPRECATED - Legacy attack manager
    
    This class is maintained for backward compatibility.
    New code should create projectiles directly.
    """
    
    def __init__(self):
        logging.debug("Creating instance of deprecated AttackManager")
        self._projectiles = []
        
    def create_projectile(self, x, y, direction_x, direction_y, 
                        projectile_type="normal", speed=10, damage=10):
        """Create a projectile of the specified type"""
        if projectile_type == "normal":
            projectile = PlayerProjectile(x, y, direction_x, direction_y, speed, damage)
        elif projectile_type == "piercing":
            projectile = PiercingProjectile(x, y, direction_x, direction_y, speed, damage)
        elif projectile_type == "special":
            projectile = SpecialProjectile(x, y, direction_x, direction_y, speed, damage)
        else:
            projectile = PlayerProjectile(x, y, direction_x, direction_y, speed, damage)
            
        self._projectiles.append(projectile)
        return projectile
        
    def update_projectiles(self, world_bounds=None):
        """Update all projectiles and remove inactive ones"""
        for i in range(len(self._projectiles) - 1, -1, -1):
            if not self._projectiles[i].update(world_bounds):
                self._projectiles.pop(i)
                
    def get_projectiles(self):
        """Get the list of active projectiles"""
        return self._projectiles
        
    def clear_projectiles(self):
        """Clear all projectiles"""
        self._projectiles.clear()
