import pgzrun
import random
from pgzhelper import *

class Settings:
    WIDTH = 800
    HEIGHT = 600
    GROUND_Y = 500
    BLACK_COLOR, GRAY_COLOR, WHITE_COLOR = (0, 0, 0), (150, 150, 150), (255, 255, 255)

class Character:
    def __init__(self, image, position, animation_frames=None, animation_fps=None):
        self.sprite = Actor(image, position)
        if animation_frames:
            self.sprite.images = animation_frames
        if animation_fps:
            self.sprite.fps = animation_fps
    
    def keep_within_screen(self, limit_x=True, limit_y=True):
        if limit_x:
            self.sprite.x = max(0, min(Settings.WIDTH, self.sprite.x))
        if limit_y:
            self.sprite.y = max(0, min(Settings.HEIGHT, self.sprite.y))
    
    def draw(self):
        self.sprite.draw()

class Hero(Character):
    GRAVITY = 1
    HERO_SPEED = 5
    JUMP_STRENGTH = -18
    START_IMAGE = 'hero1.png'
    JUMP_IMAGE = 'hero6.png'
    ANIMATION_FRAMES = ['hero2.png', 'hero3.png', 'hero4.png', 'hero5.png']
    SPAWN_AREA = (20, 600)
    
    def __init__(self):
        super().__init__(self.START_IMAGE, self.SPAWN_AREA, self.ANIMATION_FRAMES)
        self.velocity = 0
        self.is_jumping = False

    def update(self, world):
        self.process_input()
        self.apply_gravity()
        self.resolve_collisions(world)
        self.keep_within_screen()
        
    def process_input(self):
        self.handle_horizontal_movement()
        self.handle_jump()

    def handle_horizontal_movement(self):
        if keyboard.left:
            self.sprite.x -= self.HERO_SPEED
            self.sprite.flip_x = True
            self.sprite.animate()
        elif keyboard.right:
            self.sprite.x += self.HERO_SPEED
            self.sprite.flip_x = False
            self.sprite.animate()
        else:
            self.set_idle_image()

    def handle_jump(self):
        if keyboard.up and not self.is_jumping:
            self.jump()
    
    def jump(self):
        self.velocity = self.JUMP_STRENGTH
        self.is_jumping = True
        self.set_jump_image()

    def set_idle_image(self):
        self.sprite.image = self.START_IMAGE

    def set_jump_image(self):
        self.sprite.image = self.JUMP_IMAGE

    def apply_gravity(self):
        self.sprite.y += self.velocity
        self.velocity += self.GRAVITY

    def resolve_collisions(self, world):
        bottom_limit = world.get_ground_y(self.sprite)
        if self.sprite.y > bottom_limit:
            self.sprite.y = bottom_limit
            self.velocity = 0
            self.is_jumping = False

        platform = world.get_platform_below(self.sprite, self.velocity)
        if platform:
            self.sprite.y = platform.platform_parts[0].y - self.sprite.height
            self.velocity = 0
            self.is_jumping = False
    
class Enemy(Character):
    ENEMY_SPEED = 2
    ANIMATION_FRAMES = ['enemy1.png', 'enemy2.png']
    ANIMATION_FPS = 5
    START_IMAGE = ANIMATION_FRAMES[0]
    SPAWN_AREA = (50, 200)

    def __init__(self):
        super().__init__(self.START_IMAGE, self.random_spawn_position(),
                         self.ANIMATION_FRAMES, self.ANIMATION_FPS)
                    
    def random_spawn_position(self):
        x = random.randint(0, Settings.WIDTH)
        y = random.randint(*self.SPAWN_AREA) 
        return x, y

    def update(self, target):
        self.sprite.animate()
        self.move_towards_target(target)
        self.keep_within_screen()
 
    def get_direction(self, target_coord, current_coord):
        if target_coord > current_coord:
            return 1
        elif target_coord < current_coord:
            return -1
        return 0

    def move_towards_target(self, target):
        direction_x = self.get_direction(target.x, self.sprite.x)
        direction_y = self.get_direction(target.y, self.sprite.y)

        self.sprite.x += direction_x * self.ENEMY_SPEED
        self.sprite.y += direction_y * self.ENEMY_SPEED
    
class World:
    NUM_STARS = 50

    class Platform:
        PLATFORM_Y = 400
        PLATFORM_SIZE = 32
        PLATFORM_POSITIONS = [200, 400, 600]
        PLATFORM_IMAGES = ['platform_part1.png', 'platform_part2.png', 'platform_part3.png']

        def __init__(self, x, y, images):
            self.platform_parts = [Actor(img, (x + i * World.Platform.PLATFORM_SIZE, y)) for i, img in enumerate(images)]

        def colliderect(self, actor):
            return any(part.colliderect(actor) for part in self.platform_parts)

        def draw(self):
            for part in self.platform_parts:
                part.draw()

    def __init__(self):
        self.platforms = self.create_platforms()
        self.stars = self.generate_stars()

    def create_platforms(self):
        return [self.Platform(x, self.Platform.PLATFORM_Y, self.Platform.PLATFORM_IMAGES)
                for x in self.Platform.PLATFORM_POSITIONS]

    def generate_stars(self):
        return [[random.randint(0, Settings.WIDTH), 
                random.randint(0, 300), 
                random.randint(1, 3), 
                random.randint(150, 255)]
            for _ in range(self.NUM_STARS)]
    
    def update_stars(self):
        self.stars = self.generate_stars()

    def get_platform_below(self, actor, velocity):
        if velocity <= 0:
            return None
        for platform in self.platforms:
            if platform.colliderect(actor):
                return platform
        return None

    def get_ground_y(self, actor):
        return Settings.GROUND_Y - actor.height // 2

    def draw_ground(self):
        screen.draw.filled_rect(Rect(0, Settings.GROUND_Y, Settings.WIDTH, 100), Settings.GRAY_COLOR)

    def draw(self):
        self.draw_stars()
        self.draw_ground()
        for platform in self.platforms:
            platform.draw()
    
    def draw_stars(self):
        for x, y, size, brightness in self.stars:
            color = (brightness, brightness, brightness)
            screen.draw.filled_circle((x, y), size, color)

def init_game():
    hero = Hero()
    enemy = Enemy()
    world = World()
    return {
        "hero": hero,
        "enemy": enemy,
        "world": world
    }

game_objects = init_game()
hero = game_objects["hero"]
enemy = game_objects["enemy"]
world = game_objects["world"]

def draw():
    screen.clear()
    world.draw()
    enemy.draw()
    hero.draw()

def update():
    hero.update(world)
    enemy.update(hero.sprite)

def main():
    pgzrun.go()
