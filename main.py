import pgzrun
import random
from pgzhelper import *

# Game config
WIDTH, HEIGHT, NUM_STARS = 800, 600, 100
BLACK, GRAY, WHITE = (0, 0, 0), (150, 150, 150), (255, 255, 255)

stars, platforms = [], []
damage_sound = sounds.load('damage.wav')
ambient_music = sounds.load('loopmusic.mp3')
is_sound_on, is_music_playing = True, False 
menu_active, game_over = True, False

damage_timer, invulnerability_timer = 0, 0
hero_speed, enemy_speed, hero_life = 5, 3, 3

timer = 10  # Initial timer value (in seconds)
win = False
last_time = 0  # To store the time of the last decrement

# Menu buttons
start_button = Rect(WIDTH // 2 - 150, HEIGHT // 2 - 80, 300, 60)
sound_button = Rect(WIDTH // 2 - 150, HEIGHT // 2, 300, 60)  
exit_button  = Rect(WIDTH // 2 - 150, HEIGHT // 2 + 80, 300, 60)  

class Hero:
    def __init__(self):
        self.actor = Actor('hero1.png', (20, 600))
        self.actor.images = ['hero2.png', 'hero3.png', 'hero4.png', 'hero5.png']
        self.is_jumping, self.velocity = False, 0

    def move(self):
        if keyboard.left:
            self.actor.x -= hero_speed
            self.actor.flip_x = True
            self.actor.animate()  
        elif keyboard.right:
            self.actor.x += hero_speed
            self.actor.flip_x = False
            self.actor.animate()  
        else:
            self.actor.image = 'hero1.png'

        if keyboard.up and not self.is_jumping:
            self.velocity = -18  # jump 
            self.is_jumping = True
            self.actor.image = 'hero6.png'

        self.actor.y += self.velocity
        self.velocity += 1  # gravity 

        self.check_platform_collision()
        self.check_ground_collision()

        self.actor.x = max(0, min(WIDTH, self.actor.x))

    def check_platform_collision(self):
        for platform in platforms:
            if platform.colliderect(self.actor) and self.velocity > 0:
                self.actor.y = platform.parts[0].y - self.actor.height  
                self.is_jumping = False
                self.velocity = 0 

    def check_ground_collision(self):
        if self.actor.y >= 485:
            self.actor.y = 485
            self.is_jumping, self.velocity = False, 0

    def draw(self):
        self.actor.draw()

    def take_damage(self):
        global damage_timer, invulnerability_timer
        if invulnerability_timer == 0:
            self.play_damage_sound()
            damage_timer, invulnerability_timer = 30, 60

    def play_damage_sound(self):
        if is_sound_on: damage_sound.play()

class Enemy:
    def __init__(self):
        self.actor = Actor('enemy1', (random.randint(0, WIDTH), random.randint(50, 200)))
        self.actor.images = ['enemy1', 'enemy2']; self.actor.fps = 5
        
    def move_towards_hero(self, hero):
        dx, dy = hero.actor.x - self.actor.x, hero.actor.y - self.actor.y
        self.actor.x += enemy_speed if dx > 0 else -enemy_speed
        self.actor.y += enemy_speed if dy > 0 else -enemy_speed

        self.actor.x = max(0, min(WIDTH, self.actor.x))
        self.actor.y = max(0, min(HEIGHT, self.actor.y))

    def draw(self):
        self.actor.animate(); self.actor.draw()
        
class Platform:
    def __init__(self, x, y, images):
        self.parts = [Actor(img, (x + i * 32, y)) for i, img in enumerate(images)]

    def draw(self):
        for part in self.parts:
            part.draw()

    def colliderect(self, actor):
        return any(part.colliderect(actor) for part in self.parts)

# Game functions
def generate_stars():
    global stars
    stars = [[random.randint(0, WIDTH), random.randint(0, 300), random.randint(1, 3), random.randint(150, 255)] 
            for _ in range(NUM_STARS)]

def create_platforms():
    global platforms
    platforms = [
        Platform(200, 400, ['platform_part1.png', 'platform_part2.png', 'platform_part3.png']),
        Platform(400, 400, ['platform_part1.png', 'platform_part2.png', 'platform_part3.png']),
        Platform(600, 400, ['platform_part1.png', 'platform_part2.png', 'platform_part3.png'])
    ]

def check_collision_with_enemy(hero, enemy):
    global hero_life
    if hero.actor.colliderect(enemy.actor) and invulnerability_timer == 0:
        hero.take_damage()
        hero_life -= 1
        print(f'Hero life: {hero_life}')  ## Log

def check_game_over():
    global hero_life, game_over
    if hero_life <= 0 and not game_over:
        game_over = True

def reset_game():
    global game_over, hero_life, timer, last_time
    timer = 10
    last_time = 0
    hero_life = 3
    game_over = False
    start_game()
    
def start_game():
    global hero, enemy, platforms, menu_active, is_music_playing, remaining_time, show_text, message_time
    hero, enemy = Hero(), Enemy()
    generate_stars(); create_platforms()

    menu_active = False 

    if is_sound_on and not is_music_playing:
        ambient_music.play(-1) 
        is_music_playing = True 
    
    is_music_playing = True 

    remaining_time = 20
    message_time = 50000
    show_text = True

def toggle_sound():
    global is_sound_on, is_music_playing
    if is_sound_on:
        damage_sound.stop(); ambient_music.stop()
        is_music_playing = False
    elif not is_music_playing:
            ambient_music.play(-1); is_music_playing = True
    is_sound_on = not is_sound_on  # Switch sound

def draw_menu():
    screen.fill((0, 0, 0))
    screen.draw.text("Main Menu", center=(WIDTH // 2, HEIGHT // 2 - 150), fontsize=60, color="WHITE")
    
    screen.draw.filled_rect(start_button, (150, 150, 150))  
    screen.draw.text("Start Game", center=start_button.center, fontsize=30, color="BLACK")
    
    screen.draw.filled_rect(sound_button, (100, 100, 100))  
    screen.draw.text("Toggle Sound", center=sound_button.center, fontsize=30, color="BLACK")
    
    screen.draw.filled_rect(exit_button, (50, 50, 50))  
    screen.draw.text("Exit", center=exit_button.center, fontsize=30, color="BLACK")

def draw_life_bar():
    screen.draw.filled_rect(Rect(10, 10, hero_life * 30, 20), (255, 0, 0))

def dec_timer():
    global win, timer
    if timer > 0:
        timer -= 1
    elif timer == 0 and not win:
        win = True

def draw():
    if menu_active: 
        draw_menu()
    else:
        screen.clear()
        text = f'Survive for: {timer}'
        screen.draw.text(text, center=(400, 50), fontsize=50, color="white")
        screen.fill(BLACK)
        screen.draw.filled_rect(Rect(0, 500, WIDTH, 100), GRAY)

        if win:
            screen.draw.text("You Won!", center=(400, 300), fontsize=50, color="white")
            screen.draw.text("Press Q to exit",      center=(WIDTH // 2, HEIGHT // 2 + 70), fontsize=30, color="GRAY")
            if keyboard.q: exit()
        else:
            screen.draw.text(f"Survive for: {timer}s", center=(400, 50), fontsize=60, color="WHITE")

        for star in stars:
            x, y, size, brightness = star
            screen.draw.filled_circle((x, y), size, (brightness, brightness, brightness))

        hero.draw(); enemy.draw(); draw_life_bar()

        for platform in platforms: platform.draw()

        if game_over: display_game_over_screen()

def display_game_over_screen():
    screen.fill(BLACK)
    screen.draw.text("Game Over",                  center=(WIDTH // 2, HEIGHT // 2 - 30), fontsize=60, color="WHITE")
    screen.draw.text("Press R to restart", center=(WIDTH // 2, HEIGHT // 2 + 30), fontsize=30, color="GRAY")
    screen.draw.text("Press Q to exit",      center=(WIDTH // 2, HEIGHT // 2 + 70), fontsize=30, color="GRAY")

    if keyboard.r:   reset_game()
    elif keyboard.q: exit()

def on_mouse_down(pos):
    global menu_active
    if   start_button.collidepoint(pos): start_game() 
    elif sound_button.collidepoint(pos): toggle_sound()
    elif exit_button.collidepoint(pos):  exit()  

def update():
    if win:
        screen.draw.filled_rect(Rect(0, 0, WIDTH, HEIGHT), (0, 0, 0))
        return

    global remaining_time, message_time, show_text, invulnerability_timer, timer, last_time

    if menu_active: return  
    if game_over: return
    
    hero.move() 
    enemy.move_towards_hero(hero)
    check_collision_with_enemy(hero, enemy)
    check_game_over()

    if remaining_time > 0:
        remaining_time -= 1
    else:
        show_text = False

    if message_time > 0:
        message_time -= 1
    else:
        show_text = False

    if invulnerability_timer > 0:
        invulnerability_timer -= 1
        if invulnerability_timer == 0:
            hero.actor.tint = (255, 255, 255)

clock.schedule_interval(dec_timer, 1.0)
pgzrun.go()
