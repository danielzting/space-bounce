"""
Sprites for Space Bounce.
"""
import pygame
import os
import maps
from helpers import paths

paths.init(os.path.dirname(os.path.abspath(os.path.realpath(__file__))))
pygame.mixer.init()

# Load objects
object_sprites = {'brown': None,
                  'green': None,
                  'yellow': None,
                  'red': None,
                  'ammo-pack': None,
                  'ammo-count': None,
                  'blue-bullet': None,
                  'blue-bullet-flipped': None,
                  'red-bullet': None,
                  'red-bullet-flipped': None,
                  'astronaut-blue': None,
                  'astronaut-blue-flipped': None,
                  'astronaut-red': None,
                  'astronaut-red-flipped': None,
                 }
for item in object_sprites:
    object_sprites[item] = pygame.image.load(paths.path('sprites', item + '.png'))

# Load sound effects
effects = {'reload': None,
           'shoot': None,
           'punch': None,
           'birds': None,
           'countdown': None,
           'suddendeath': None,
          }
for effect in effects:
    effects[effect] = pygame.mixer.Sound(paths.path('sounds', 'effects', effect + '.ogg'))

class Astronaut():
    """Astronaut class."""
    # Size of astronaut
    width = 28
    height = 45

    def __init__(self, surface, color, coordinates):
        """Initialize an astronaut."""
        # Astronaut sprite
        self.surface = surface
        self.color = color
        # Bullets
        self.bullets = 5
        # Borders of astronaut
        self.top_border = coordinates[1]
        self.right_border = coordinates[0] + self.width
        self.bottom_border = coordinates[1] + self.height
        self.left_border = coordinates[0]
        # Variables for calculating movement
        self.dead = False # If astronaut has hit red platform
        self.speed = 10 # Speed of astronaut's horizontal movement every frame
        self.starting_height = coordinates[1] # Height of platform jumped from
        self.acceleration = -100 # Force of gravity
        self.jump = 200 # Power of jump
        self.y_time = 0 # Time elapsed since last bounce
        self.direction = None # Direction of x movement
        self.momentum = 0 # Momentum from being punched or shot
        self.force = 20 # Knockback of punch
        # Draw astronaut
        if color == 'blue':
            self.sprite = object_sprites['astronaut-blue']
            self.surface.blit(self.sprite, coordinates)
        elif color == 'red':
            self.sprite = object_sprites['astronaut-red']
            self.surface.blit(self.sprite, coordinates)
    
    def fallen(self, surface):
        """Return boolean representing if astronaut has fallen off the sceren."""
        if self.top_border > surface.get_height():
            return True
        if self.left_border < 0:
            return True
        if self.right_border > surface.get_width():
            return True
        # No check for top necessary because astronauts will never get that high

    def on_object(self, objects, sfx):
        """Return boolean representing if astronaut has touched an object and return the object touched."""
        error_range = 5 # Maximum amount of pixels that astronaut has o be away from platform to trigger; do not change below 5
        vertex = -self.jump / (2 * self.acceleration) # Vertex of parabola
        # Iterate through all objects
        for item in objects:
            # Check ammo pack
            if isinstance(item, AmmoPack):
                # Check if ammo pack is spawned
                if item.visible:
                    # Check y-level
                    if self.top_border <= item.top_border <= self.bottom_border or self.top_border <= item.bottom_border <= self.bottom_border:
                        if item.left_border <= self.left_border <= item.right_border:
                            return item
                        elif item.left_border <= self.right_border <= item.right_border:
                            return item
            # Check if been hit by bullet
            elif isinstance(item, Bullet):
                # Check x-level
                if self.left_border <= item.coordinates[0] <= self.right_border:
                    if self.top_border <= item.coordinates[1] <= self.bottom_border:
                        return item
            # Check if on platform
            else:
                # Check red platform
                if item.color == 'red':
                    # Check if astronaut has touched anywhere on y-level
                    if self.top_border <= item.top_border <= self.bottom_border or self.top_border <= item.bottom_border <= self.bottom_border:
                        # Check x-level
                        if item.left_border <= self.left_border <= item.right_border:
                            if sfx == 'ON':
                                effects['birds'].play()
                            self.dead = True
                        elif item.left_border <= self.right_border <= item.right_border:
                            if sfx == 'ON':
                                effects['birds'].play()
                            self.dead = True 
                else:
                    # Check if astronaut is falling
                    if self.y_time >= vertex or self.y_time == 0:
                        if abs(item.top_border - self.bottom_border) <= error_range:
                            # Check if left foot is touching
                            if item.left_border <= self.left_border <= item.right_border:
                                return item
                            # Check if right foot is touching
                            elif item.left_border <= self.right_border <= item.right_border:
                                return item

    def update_pos(self, surface, objects, fps, sfx):
        """Update the astronaut's position based on the given coordinates. Return False if astronaut has hit deadly object."""
        # If touched red platform, lose
        if self.dead:
            x = self.left_border
            y = self.top_border + 10
        else:
            # Update momentum by reducing it every frame
            if self.momentum < 0:
                self.momentum += 1
            elif self.momentum > 0:
                self.momentum -= 1
            self.y_time += 1 / fps
            # Update sprite and x change
            if self.direction == 'left':
                x_change = -self.speed + self.momentum
                # Flip astronaut as necessary
                if self.color == 'blue':
                    self.sprite = object_sprites['astronaut-blue-flipped']
                else:
                    self.sprite = object_sprites['astronaut-red']
            elif self.direction == 'right':
                x_change = self.speed + self.momentum
                # Flip astronaut as necessary
                if self.color == 'blue':
                    self.sprite = object_sprites['astronaut-blue']
                else:
                    self.sprite = object_sprites['astronaut-red-flipped']
            else:
                x_change = self.momentum
            # Update x
            x = self.left_border + x_change
            # Check if touching anything
            item = self.on_object(objects, sfx)
            # If on platform, don't fall
            if isinstance(item, Platform):
                self.y_time = 0
                self.starting_height = self.top_border
                y = self.top_border
                # If touched yellow platform, remove it
                if item.color == 'yellow':
                    objects.remove(item)
            # Otherwise, calculate fall
            else:
                # Grab ammo pack
                if isinstance(item, AmmoPack):
                    item.grab(self, sfx)
                # Get shot
                elif isinstance(item, Bullet):
                    if item.direction == 'left':
                        self.momentum -= item.force
                    elif item.direction == 'right':
                        self.momentum += item.force
                    objects.remove(item)
                # Quadratic equation of projectile under influence of gravity
                y = int(round(self.starting_height
                    - (
                        (self.acceleration * self.y_time ** 2
                        + self.jump * self.y_time
                        + self.starting_height)
                    - self.starting_height
                    )))
        # Draw astronaut and update borders
        self.top_border = y
        self.right_border = x + self.width
        self.bottom_border = y + self.height
        self.left_border = x
        surface.blit(self.sprite, (x, y))

    def punch(self, target, sfx):
        """Make an astronaut punch the target."""
        # Check if astronauts near same x-level
        if not target.top_border <= self.top_border <= target.bottom_border and not target.top_border <= self.bottom_border <= target.bottom_border:
            return
        # Check direction
        if self.sprite == object_sprites['astronaut-blue-flipped'] or self.sprite == object_sprites['astronaut-red']:
            # Check if facing target
            if target.left_border <= self.left_border <= target.right_border:
                if sfx == 'ON':
                    effects['punch'].play()
                target.momentum = -self.force
        elif self.sprite == object_sprites['astronaut-blue'] or self.sprite == object_sprites['astronaut-red-flipped']:
            # Check if facing target
            if target.left_border <= self.right_border <= target.right_border:
                if sfx == 'ON':
                    effects['punch'].play()
                target.momentum = self.force

    def shoot(self, surface, objects, sfx):
        """Make an astronaut shoot."""
        if self.bullets > 0:
            if sfx == 'ON':
                effects['shoot'].play()
            self.bullets -= 1
            coordinates = self.left_border, self.top_border + self.height / 2
            direction = self.direction
            if not direction:
                if self.sprite == object_sprites['astronaut-blue-flipped'] or self.sprite == object_sprites['astronaut-red']:
                    direction = 'left'
                elif self.sprite == object_sprites['astronaut-blue'] or self.sprite == object_sprites['astronaut-red-flipped']:
                    direction = 'right'
            objects.append(Bullet(surface, self.color, direction, coordinates))

class Platform():
    """Platform class."""
    # Size of platform
    width = 50
    height = 10

    def __init__(self, surface, color, coordinates, movement_borders=None, direction=None):
        """Initialize a platform."""
        # Platform sprite
        self.surface = surface
        self.color = color
        # Speed of moving platform
        self.speed = 5
        # Borders of platform
        self.top_border = coordinates[1]
        self.right_border = coordinates[0] + self.width
        self.bottom_border = coordinates[1] + self.height
        self.left_border = coordinates[0]
        # Draw platform
        if color == 'brown':
            self.surface.blit(object_sprites['brown'], coordinates)
        elif color == 'green':
            # Movement borders of moving platform
            if not movement_borders:
                raise TypeError('green platform missing borders')
            self.movement_borders = movement_borders
            # Which direction will the platform move at first
            if not direction:
                raise TypeError('green platform missing direction')
            self.direction = direction
            self.surface.blit(object_sprites['green'], coordinates)
        elif color == 'yellow':
            self.surface.blit(object_sprites['yellow'], coordinates)
        elif color == 'red':
            self.surface.blit(object_sprites['red'], coordinates)

    @property
    def change(self):
        """Calculate movement of moving platform and return its change and direction."""
        if self.direction == 'left':
            # Check if movement boundary has been hit
            if self.left_border - self.speed <= self.movement_borders[0]:
                self.direction = 'right'
                return self.speed, self.direction
            return -self.speed, self.direction
        elif self.direction == 'right':
            # Check if movement boundary has been hit
            if self.right_border + self.speed >= self.movement_borders[1]:
                self.direction = 'left'
                return -self.speed, self.direction
            return self.speed, self.direction

class AmmoPack():
    """Ammo pack sprite."""
    width = 50
    height = 50

    def __init__(self, surface, coordinates):
        """Initialize an ammo pack."""
        # Ammo pack sprite
        self.surface = surface
        self.sprite = object_sprites['ammo-pack']
        self.coordinates = coordinates
        # Border attributes
        self.top_border = coordinates[1]
        self.right_border = coordinates[0] + self.width
        self.bottom_border = coordinates[1] + self.height
        self.left_border = coordinates[0]
        # Number of bullets it contains
        self.bullets = 5
        # Rarity of spawn, RNG must return this between 0 and this
        self.rarity = 500
        # Visibility
        self.visible = False

    def spawn(self, surface):
        """Spawn an ammo pack at its location."""
        self.visible = True
        self.surface.blit(self.sprite, self.coordinates)

    def grab(self, astronaut, sfx):
        """An astronaut grabs an ammo pack."""
        if sfx == 'ON':
            effects['reload'].play()
        new = astronaut.bullets + self.bullets
        # Limit on bullets
        if new >= 100:
            pass
        else:
            astronaut.bullets = new
        self.visible = False 

class Bullet():
    """Bullet sprite."""
    width = 18
    height = 6

    def __init__(self, surface, color, direction, coordinates):
        # Bullet sprite
        self.surface = surface
        # Location
        self.coordinates = coordinates
        # Visibility
        self.visible = True
        # Movement variables
        self.direction = direction
        self.speed = 30 # Speed of bullet
        self.force = 5 # Knockback of bullet
        # Who shot it
        self.color = color
        # Draw bullet
        bullet = self.color + '-bullet'
        if direction == 'left':
            self.sprite = object_sprites[bullet]
        elif direction == 'right':
            self.sprite = object_sprites[bullet + '-flipped']
        self.surface.blit(self.sprite, coordinates)

    @property
    def change(self):
        """Calculate the x-change of a bullet if it is on the screen."""
        if self.direction == 'left':
            change = -self.speed
        elif self.direction == 'right':
            change = self.speed
        # If bullet has flown off the screen, mark for removal
        if not 0 < self.coordinates[0] + change < self.surface.get_width():
            self.visible = False
        return change
