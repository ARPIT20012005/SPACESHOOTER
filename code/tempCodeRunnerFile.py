from typing import Any
import pygame
from os.path import join, isfile
from random import randint, uniform

from pygame.sprite import _Group


# Player Class
class Player(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.image = pygame.image.load(join('images', 'player.png')).convert_alpha()  # Define self.image here
        self.rect = self.image.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
        self.direction = pygame.Vector2()
        self.speed = 500

        # Cooldown variables
        self.can_shoot = True
        self.laser_shoot_time = 0
        self.cooldown_duration = 400
        # Mask for collision detection
        self.mask = pygame.mask.from_surface(self.image)

      
    def laser_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.laser_shoot_time >= self.cooldown_duration:
                self.can_shoot = True    

    def update(self, dt):
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
        self.direction.y = int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])
        self.direction = self.direction.normalize() if self.direction else self.direction
        self.rect.center += self.direction * self.speed * dt

        # Fire laser if cooldown allows
        if keys[pygame.K_SPACE] and self.can_shoot:
            Laser(laser_surf, self.rect.midtop, (all_sprites, laser_sprites))
            self.can_shoot = False
            self.laser_shoot_time = pygame.time.get_ticks()
        
        self.laser_timer()

# Star Class
class Star(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.image = star_surf
        self.rect = self.image.get_rect(center=(randint(0, WINDOW_WIDTH), randint(0, WINDOW_HEIGHT)))

# Laser Class
class Laser(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(midbottom=pos)

    def update(self, dt):
        self.rect.centery -= 700 * dt
        if self.rect.bottom < 0:
            self.kill()

# Meteor Class
class Meteor(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.original_surf = surf
        self.image = surf
        self.rect = self.image.get_rect(center=pos)
        self.start_time = pygame.time.get_ticks()
        self.lifetime = 7000
        self.direction = pygame.Vector2(uniform(-0.5, 0.5), 1)
        self.speed = randint(600, 700)
        self.rotation_speed = randint(40,80)
        self.rotation = 0

        
    def update(self, dt):
        self.rect.center += self.direction * self.speed * dt
        if pygame.time.get_ticks() - self.start_time >= self.lifetime:
            self.kill()
        self.rotation += self.rotation_speed * dt
        self.image = pygame.transform.rotozoom(self.original_surf, self.rotation, 1)
        self.rect = self.image.get_rect(center =self.rect.center)


class AnimationExplosion(pygame.sprite.Sprite):
    def __init__(self, frames, pos, groups):
        self.image = frames[0]
        self.rect  =self.image.get_rect(center = pos)



# Collision Detection
def collisions():
    
    if pygame.sprite.spritecollide(player, meteor_sprites, True, pygame.sprite.collide_mask):
        running = False

    for laser in laser_sprites:
        if pygame.sprite.spritecollide(laser, meteor_sprites, True):
            laser.kill()


# score
def display_score():
    current_time = pygame.time.get_ticks() // 100
    text_surf = font.render(str(current_time), True, (240,240,240))
    text_rect = text_surf.get_rect(midbottom = (WINDOW_WIDTH / 2, WINDOW_HEIGHT -50))
    display_surface.blit(text_surf, text_rect)
    pygame.draw.rect(display_surface, (240,240,240), text_rect.inflate(20,10 ).move(0, -8), 5 ,10)
# General setup
pygame.init()
WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Space Shooter')
running = True
clock = pygame.time.Clock()

# Load images
star_surf = pygame.image.load(join('images', 'star.png')).convert_alpha()
meteor_surf = pygame.image.load(join('images', 'meteor.png')).convert_alpha()
laser_surf = pygame.image.load(join('images', 'laser.png')).convert_alpha()

# Load font
font_path = join('images', 'Oxanium-Bold.ttf')
font = pygame.font.Font(font_path, 40) if isfile(font_path) else pygame.font.Font(None, 20)
explosion_frames = [pygame.image.load(join('image', 'explotion', f'{i}.png')).convert_alpha() for i in range(21)]
print(explosion_frames)


# Initialize sprite groups
all_sprites = pygame.sprite.Group()
meteor_sprites = pygame.sprite.Group()
laser_sprites = pygame.sprite.Group()

# Create stars and player
for _ in range(20):
    Star(all_sprites)
player = Player(all_sprites)
all_sprites.add(player)

# Custom meteor event
meteor_event = pygame.event.custom_type()
pygame.time.set_timer(meteor_event, 500)

# Game loop
while running:
    dt = clock.tick(60) / 1000  # Cap the frame rate

    # Event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == meteor_event:
            x, y = randint(0, WINDOW_WIDTH), randint(-200, -100)
            Meteor(meteor_surf, (x, y), (all_sprites, meteor_sprites))

    # Update and collision detection
    all_sprites.update(dt)
    collisions()

    # Background and drawing
    display_surface.fill('#3a2e3f')
    display_score()
    all_sprites.draw(display_surface)

    pygame.display.update()

pygame.quit()
