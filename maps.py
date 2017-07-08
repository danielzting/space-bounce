"""
Maps for Space Bounce.
"""
import pygame
import os
import csv
import random
import sprites
import sounds
from helpers import paths

paths.init(os.path.dirname(os.path.abspath(os.path.realpath(__file__))))

def load():
    """Load the map images, objects, and songs, and return a list of all resources."""
    # Map dictionary with names and data
    map_list = {'earth': [],
                'asteroids': [],
                'sun': [],
                'random': [],
                'suddendeath': [],
                }
    # Loop through maps, adding background image and sprite file
    for item in map_list:
        map_list[item].append(pygame.image.load(paths.path('maps', item + '.png')))
        map_list[item].append(paths.path('data', item + '.csv'))
        map_list[item].append(paths.path('sounds', 'songs', item + '.ogg'))
    # Return resources
    return map_list

def draw_map(surface, map_list, map_chosen):
    """Draw the chosen map and return a list of all objects."""
    objects = []
    # Draw map
    surface.blit(map_list[map_chosen][0], (0, 0))
    # Load map data
    if map_chosen != 'random':
        with open(map_list[map_chosen][1]) as data:
            data.seek(0)
            reader = csv.reader(data)
            for row in reader:
                coordinates = int(row[1]), int(row[2])
                # For ammo packs
                if row[0] == 'ammo':
                    objects.append(sprites.AmmoPack(surface, coordinates))
                # For moving platforms, which require extra arguments
                elif row[0] == 'green':
                    objects.append(sprites.Platform(surface,
                        row[0],
                        coordinates,
                        (int(row[3]), int(row[4])),
                        row[5]))
                # For still platforms
                else:
                    objects.append(sprites.Platform(surface, row[0], coordinates))
    # Generate random map
    else:
        # Spawn platforms at normal spawnpoint
        objects.append(sprites.Platform(surface, 'brown', (100, 600)))
        objects.append(sprites.Platform(surface, 'brown', (1130, 600)))
        # Types of objects
        object_types = ('brown', 'green', 'yellow', 'red', 'ammo')
        # Spawn between 10 and 50 objects
        for _ in range(random.randint(10, 50)):
            # Determine type of object
            object_type = object_types[random.randint(0, 4)]
            # Generate random valid coordinates
            coordinates = random.randint(0, surface.get_width()), random.randint(0, surface.get_height())
            # Still platform
            if object_type in ('brown', 'yellow', 'red'):
                objects.append(sprites.Platform(surface, object_type, coordinates))
            # Moving platform
            elif object_type == 'green':
                boundaries = sorted((random.randint(0, surface.get_width()), coordinates[0]))
                direction = ('left', 'right')[random.randint(0, 1)]
                objects.append(sprites.Platform(surface, object_type, coordinates, boundaries, direction))
            elif object_type == 'ammo':
                objects.append(sprites.AmmoPack(surface, coordinates))
    return objects

def update_map(surface, map_list, map_chosen, objects, frozen=False):
    """Update the map's objects and return a list of all objects."""
    # Draw map
    surface.blit(map_list[map_chosen][0], (0, 0))
    # Update objects
    for index, item in enumerate(objects):
        # List containing objects to remove
        to_remove = []
        # Spawn ammo packs randomly
        if isinstance(item, sprites.AmmoPack):
            if not frozen:
                if item.visible:
                    surface.blit(item.sprite, item.coordinates)
                elif random.randint(0, item.rarity) == item.rarity:
                    item.spawn(surface)
        # Render bullets
        elif isinstance(item, sprites.Bullet):
            if item.visible:
                coordinates = item.coordinates[0] + item.change, item.coordinates[1]
                objects[index] = sprites.Bullet(surface, item.color, item.direction, coordinates)
            else:
                to_remove.append(item)
        # Draw platforms
        else:
            # Move green platform
            if item.color == 'green':
                if not frozen:
                    change, direction = item.change
                    coordinates = item.left_border + change, item.top_border
                    objects[index] = sprites.Platform(surface, item.color, coordinates, item.movement_borders, direction)
                else:
                    change, direction = item.change
                    coordinates = item.left_border, item.top_border
                    objects[index] = sprites.Platform(surface, item.color, coordinates, item.movement_borders, direction)
            else:
                coordinates = item.left_border, item.top_border
                objects[index] = sprites.Platform(surface, item.color, coordinates)
        # Remove objects
        for item in to_remove:
            objects.remove(item)
