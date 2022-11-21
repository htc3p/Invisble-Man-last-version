import pygame
from pygame import mixer
import os
import random
import csv
import menu
from screenfade import ScreenFade
from button import Button
from objects import *


mixer.init()
pygame.init()

# create game window
SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Invisible Man')

# set framerate
clock = pygame.time.Clock()
FPS = 65

# define game variables
GRAVITY = 0.75
SCROLL_THRESH = 150
ROWS = 16
COLS = 150
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES = 35
MAX_LEVELS = 5
screen_scroll = 0
bg_scroll = 0
level = 1
level_show = 1
start_game = False
restart_game = False
start_intro = False

SCORE = 0
HEALTH = 0
AMMO = 0

# define player action variables
moving_left = False
moving_right = False
shoot = False


# load music and sounds -----------------------------------------------------------------
jump_fx = pygame.mixer.Sound('audio/jump.wav')
jump_fx.set_volume(0.1)
shot_fx = pygame.mixer.Sound('audio/shot.wav')
shot_fx.set_volume(0.1)
arrow_fx = pygame.mixer.Sound('audio/arrow.wav')
arrow_fx.set_volume(0.1)
bite_fx = pygame.mixer.Sound('audio/bite.wav')
bite_fx.set_volume(0.1)
fireball_fx = pygame.mixer.Sound('audio/fireball.wav')
fireball_fx.set_volume(0.05)
shock_fx = pygame.mixer.Sound('audio/shock.wav')
shock_fx.set_volume(0.1)
keydrop_fx = pygame.mixer.Sound('audio/keydrop.wav')
keydrop_fx.set_volume(0.1)


# load images ---------------------------------------------------------------------------
# background
intro_img = pygame.image.load('images/background/intro2.jpg')
building_img = pygame.image.load('images/background/bg2.jpg').convert_alpha()
# button images
play_img = pygame.image.load('images/buttons/play_img.png').convert_alpha()
scoreboard_img = pygame.image.load('images/buttons/scoreboard_img.png').convert_alpha()
exit_img = pygame.image.load('images/buttons/exit_img.png').convert_alpha()
restart_img = pygame.image.load('images/buttons/restart_img.png').convert_alpha()
# store tiles in a list
img_list = []
for x in range(TILE_TYPES):
	img = pygame.image.load(f'images/tile/{x}.png')
	img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
	img_list.append(img)
# bullet
bullet_img = pygame.image.load('images/icons/bullet.png').convert_alpha()
arrow_img = pygame.image.load('images/icons/arrow.png').convert_alpha()
fireball_img = pygame.image.load('images/icons/fire.png').convert_alpha()
# pick up boxes
health_box_img = pygame.image.load('images/icons/health_box.png').convert_alpha()
ammo_box_img = pygame.image.load('images/icons/ammo_box.png').convert_alpha()
key_box_img = pygame.image.load('images/icons/key.png').convert_alpha()
item_boxes = {
	'Health': health_box_img,
	'Ammo': ammo_box_img,
    'Key' : key_box_img
}


# define colors
RED = (255, 0, 0)
WHITE = (241, 250, 238)
BLUE = (0,30,255)
RED = 	(255,126,126)
PINK = (214,0,255)
GREEN = (0,255,159)
BLACK = (0, 0, 0)
GRAY = (47, 62, 70)

# define font
font1 = pygame.font.Font('fonts/ARCADE.TTF', 28)
font2 = pygame.font.Font('fonts/ARCADE.TTF', 22)
largefont = pygame.font.Font('fonts/ARCADE.TTF', 120)


def draw_text(text, font, text_col, x, y):
	img = font.render(text, True, text_col)
	screen.blit(img, (x, y))


def draw_bg():
    screen.fill(GREEN)
    width = building_img.get_width()
    for x in range(6):
        screen.blit(building_img, ((x * width) - bg_scroll, 0))


#function to reset level
def reset_level():
    enemy1_group.empty()
    enemy2_group.empty()
    enemy3_group.empty()
    enemy4_group.empty()
    enemy5_group.empty()

    bullet_group.empty()
    arrow_group.empty()
    fireball_group.empty()
    item_box_group.empty()
    acid_group.empty()
    spike_group.empty()
    decoration_group.empty()
    exit_group.empty()

    #create empty tile list
    data = []
    for row in range(ROWS):
        r = [-1] * COLS
        data.append(r)

    return data

class Player(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed, ammo):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.char_type = char_type
        self.speed = speed
        self.ammo = ammo
        self.start_ammo = False
        self.shoot_cooldown = 0
        self.key = 0
        self.health = 3000
        self.max_health = self.health
        self.direction = 1
        self.vel_y = 0
        self.jump = False
        self.in_air = True
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()
        self.score = 0

        # load all images for the players
        animation_types = ['idle', 'run', 'jump', 'death', 'shoot']
        for animation in animation_types:
            # reset temporary list of images
            temp_list = []
            # count number of files in the folder
            num_of_frames = len(os.listdir(
                f'images/{self.char_type}/{animation}'))
            for i in range(num_of_frames):
                img = pygame.image.load(
                    f'images/{self.char_type}/{animation}/{i}.png')
                img = pygame.transform.scale(
                    img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def update(self):
        self.update_animation()
        self.check_alive()
        # update cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def move(self, moving_left, moving_right):
        # reset movement variables
        screen_scroll = 0
        dx = 0
        dy = 0

        # assign movement variables if moving left or right
        if moving_left:
            self.flip = True
            self.direction = -1
            dx = -self.speed
        if moving_right:
            self.flip = False
            self.direction = 1
            dx = self.speed

        # jump
        if self.jump == True and self.in_air == False:
            self.vel_y = -12
            jump_fx.play()
            self.jump = False
            self.in_air = True

        # apply gravity
        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y
        dy += self.vel_y

        # check collision
        for tile in world.obstacle_list:
            #check collision in the x direction
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
            #check for collision in the y direction
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                #check if below the ground, i.e. jumping
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                #check if above the ground, i.e. falling
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    self.in_air = False
                    dy = tile[1].top - self.rect.bottom

        #check for collision with spike
        if pygame.sprite.spritecollide(self, spike_group, False):
            self.health = 0

        #check for collision with exit
        level_complete = False
        if pygame.sprite.spritecollide(self, exit_group, False) and self.key == 1:
            level_complete = True
        
        #check if fallen off the map
        if self.rect.bottom > SCREEN_HEIGHT:
            self.health = 0
        
        #check if going off the edges of the screen
        if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
            dx = 0

        # update rectangle position
        self.rect.x += dx
        self.rect.y += dy

        #update scroll based on player position
        if (self.rect.right > SCREEN_WIDTH - SCROLL_THRESH and bg_scroll < (world.level_length * TILE_SIZE) - SCREEN_WIDTH)\
            or (self.rect.left < SCROLL_THRESH and bg_scroll > abs(dx)):
            self.rect.x -= dx
            screen_scroll = -dx

        return screen_scroll, level_complete

    def shoot(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.start_ammo = True
            self.shoot_cooldown = 20
            bullet = Bullet(self.rect.centerx + (
                0.5 * self.rect.size[0] * self.direction), self.rect.centery, self.direction)
            bullet_group.add(bullet)
            # reduce ammo
            self.ammo -= 1
            shot_fx.play()

    def update_animation(self):
        # update animation
        ANIMATION_COOLDOWN = 100
        # update image depending on current frame
        self.image = self.animation_list[self.action][self.frame_index]
        # check if enough time has passed since the last update
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        # if the animation has run out the reset back to the start
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0

    def update_action(self, new_action):
        # check if the new action is different to the previous one
        if new_action != self.action:
            self.action = new_action
            # update the animation settings
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(3)

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed, health):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.char_type = char_type
        self.speed = speed
        self.arrow = 50
        self.fireball = 50
        self.skill_cooldown = 0
        self.shoot_cooldown = 0
        self.fire_cooldown = 0
        self.health = health
        self.max_health = self.health
        self.direction = 1
        self.vel_y = 0
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()
        self.key_drop = False

        # ai specific variables
        self.move_counter = 0
        self.vision_enm1 = pygame.Rect(0, 0, 180, 20)
        self.vision_enm2 = pygame.Rect(0, 0, 60, 20)
        self.vision_enm3 = pygame.Rect(0, 0, 200, 20)
        self.vision_enm4 = pygame.Rect(0, 0, 70, 20)
        self.vision_enm5 = pygame.Rect(0, 0, 70, 30)
        self.colliding = False

        # load all images for the players
        animation_types = ['idle', 'run', 'death', 'attack']
        for animation in animation_types:
            # reset temporary list of images
            temp_list = []
            # count number of files in the folder
            num_of_frames = len(os.listdir(
                f'images/{self.char_type}/{animation}'))
            for i in range(num_of_frames):
                img = pygame.image.load(
                    f'images/{self.char_type}/{animation}/{i}.png')
                img = pygame.transform.scale(
                    img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def update(self):
        self.update_animation()
        self.check_alive()

        # update cooldown
        if self.skill_cooldown > 0:
            self.skill_cooldown -= 1
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        if self.fire_cooldown > 0:
            self.fire_cooldown -= 1

    def move(self, moving_left, moving_right):

        # reset movement variables
        dx = 0

        # assign movement variables if moving left or right
        if moving_left:
            self.flip = True
            self.direction = -1
            dx = -self.speed
        if moving_right:
            self.flip = False
            self.direction = 1
            dx = self.speed

        # check collision
        for tile in world.obstacle_list:
            #check collision in the x direction
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
                #if the ai has hit a wall then make it turn around
                self.direction *= -1
                self.move_counter = 0

        # update rectangle position
        self.rect.x += dx

    def ai(self):
        if self.alive and player.alive:
            # check if the ai in near the player
            if self.vision_enm1.colliderect(player.rect):
                # attack
                if self.char_type == 'enemy1':
                    self.shoot()
            elif self.vision_enm2.colliderect(player.rect):
                # attack
                if self.char_type == 'enemy2':
                    self.attack(player, 100)
            elif self.vision_enm3.colliderect(player.rect):
                # attack
                if self.char_type == 'enemy3':
                    self.fire()
            elif self.vision_enm4.colliderect(player.rect):
                # attack
                if self.char_type == 'enemy4':
                    self.attack(player, 300)
            elif self.vision_enm5.colliderect(player.rect):
                # attack
                if self.char_type == 'enemy5':
                    self.attack(player, 500)

            else:
                if self.direction == 1: 
                    ai_moving_right = True
                else:
                    ai_moving_right = False
                ai_moving_left = not ai_moving_right
                self.move(ai_moving_left, ai_moving_right)
                self.update_action(1) #run

                if self.char_type == 'enemy2':
                    self.move_counter += 0.4
                if self.char_type == 'enemy1':
                    self.move_counter += 1
                if self.char_type == 'enemy3' or self.char_type == 'enemy4' or self.char_type == 'enemy5':
                    self.move_counter += 0.5

                # update ai vision as the enemy moves
                if self.char_type == 'enemy1':
                    self.vision_enm1.center = (self.rect.centerx + 80 * self.direction, self.rect.centery)
                if self.char_type == 'enemy2':
                    self.vision_enm2.center = (self.rect.centerx + 40 * self.direction, self.rect.centery)
                if self.char_type == 'enemy3':
                    self.vision_enm3.center = (self.rect.centerx + 100 * self.direction, self.rect.centery)
                if self.char_type == 'enemy4':
                    self.vision_enm4.center = (self.rect.centerx + 30 * self.direction, self.rect.centery)
                if self.char_type == 'enemy5':
                    self.vision_enm5.center = (self.rect.centerx + 30 * self.direction, self.rect.centery)

                # pygame.draw.rect(screen, RED, self.vision_enm1)
                # pygame.draw.rect(screen, RED, self.vision_enm2)
                # pygame.draw.rect(screen, RED, self.vision_enm3)
                # pygame.draw.rect(screen, RED, self.vision_enm4)
                # pygame.draw.rect(screen, RED, self.vision_enm5)

                if self.move_counter > TILE_SIZE:
                    self.direction *= -1
                    self.move_counter *= -1
        
        elif self.alive == False and player.alive:
            rand_num = random.uniform(0, 100)
            if rand_num >= 0 and rand_num <= 35: #35%
                self.key_drop = True
            if self.key_drop and player.key != 1:
                key = ItemBox(item_boxes, 'Key', self.rect.centerx, self.rect.centery - 10)
                item_box_group.add(key)
                keydrop_fx.play()

            # heal and score up player
            if self.char_type == 'enemy1':
                player.score += 500
                player.health += 50
            if self.char_type == 'enemy2':
                player.score += 1000
                player.health += 75
            if self.char_type == 'enemy3':
                player.score += 1500
                player.health += 100
            if self.char_type == 'enemy4':
                player.score += 2000
                player.health += 150
            if self.char_type == 'enemy5':
                player.score += 2500
                player.health += 300
            if player.health > player.max_health:
                player.health = player.max_health
            
            self.kill()
            
        #scroll
        self.rect.x += screen_scroll

    def idle(self):
        # set variables to attack animation
        self.action = 0
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()

    def attack(self, target, damage):
        # deal damage to enemy
        if self.skill_cooldown == 0:
            self.skill_cooldown = 20
            target.health -= damage
            self.update_action(3)  #attack
            if self.char_type == 'enemy4':
                shock_fx.play()
            else:
                bite_fx.play()

    def shoot(self):
        if self.shoot_cooldown == 0 and self.arrow > 0:
            self.shoot_cooldown = 20
            arrow = Arrow(self.rect.centerx + (0.75 * self.rect.size[0] * self.direction), self.rect.centery, self.direction)
            arrow_group.add(arrow)
            self.update_action(3) #attack
            # reduce arrow
            self.arrow -= 1
            arrow_fx.play()

    def fire(self):
        if self.fire_cooldown == 0 and self.fireball > 0:
            self.fire_cooldown = 20
            fireball = Fireball(self.rect.centerx + (0.75 * self.rect.size[0] * self.direction), self.rect.top + 20, self.direction)
            fireball_group.add(fireball)
            self.update_action(3) #attack
            # reduce fireball
            self.fireball -= 1
            fireball_fx.play()

    def update_animation(self):
        # update animation
        ANIMATION_COOLDOWN = 100

        # update image depending on current frame
        self.image = self.animation_list[self.action][self.frame_index]
        # check if enough time has passed since the last update
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        # if the animation has run out the reset back to the start
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 2:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.idle()

    def update_action(self, new_action):
        # check if the new action is different to the previous one
        if new_action != self.action:
            self.action = new_action
            # update the animation settings
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(2)  #death

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)


class World():
    def __init__(self):
        self.obstacle_list = []

    def process_data(self, data):
        self.level_length = len(data[0])
        # iterate through each value in level data file
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    img = img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * TILE_SIZE
                    img_rect.y = y * TILE_SIZE
                    tile_data = (img, img_rect)
                    if tile >= 0 and tile <= 7:
                        self.obstacle_list.append(tile_data)
                    elif tile >= 8 and tile <= 14:
                        self.obstacle_list.append(tile_data)
                    elif tile == 15: #spike
                        spike = Spike(img, x * TILE_SIZE, y * TILE_SIZE)
                        spike_group.add(spike)
                    elif tile >= 16 and tile <= 17: #acid
                        acid = Acid(img, x * TILE_SIZE, y * TILE_SIZE)
                        acid_group.add(acid)
                    elif tile >= 18 and tile <= 23:
                        decoration = Decoration(img, x * TILE_SIZE, y * TILE_SIZE)
                        decoration_group.add(decoration)
                    elif tile >= 24 and tile <= 25: #exit door
                        exit = Exit(img, x * TILE_SIZE, y * TILE_SIZE)
                        exit_group.add(exit)
                    elif tile == 26: #create ammo box
                        item_box = ItemBox(item_boxes, 'Ammo', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 27: #create health box
                        item_box = ItemBox(item_boxes, 'Health', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 29: #create player
                        player = Player('player', x * TILE_SIZE, y * TILE_SIZE, 1.5, 4, 30)
                        health_bar = HealthBar(screen, 10, 10, player.health, player.health)
                    elif tile == 30: #create enemy1
                        enemy1 = Enemy('enemy1', x * TILE_SIZE, y * TILE_SIZE, 1.75, 2, 200)
                        enemy1_group.add(enemy1)
                    elif tile == 31: #create enemy2
                        enemy2 = Enemy('enemy2', x * TILE_SIZE, y * (TILE_SIZE-0.75), 2, 2, 350)
                        enemy2_group.add(enemy2)
                    elif tile == 32: #create enemy3
                        enemy3 = Enemy('enemy3', x * TILE_SIZE, y * (TILE_SIZE-1.5), 3, 2, 500)
                        enemy3_group.add(enemy3)
                    elif tile == 33: #create enemy4
                        enemy4 = Enemy('enemy4', x * TILE_SIZE, y * (TILE_SIZE-0.75), 2.5, 2, 1000)
                        enemy4_group.add(enemy4)
                    elif tile == 34: #create enemy5
                        enemy5 = Enemy('enemy5', x * TILE_SIZE, y * (TILE_SIZE-0.75), 1.5, 2, 2000)
                        enemy5_group.add(enemy5)

        return player, health_bar
          
    def draw(self):
        for tile in self.obstacle_list:
            tile[1][0] += screen_scroll
            screen.blit(tile[0], tile[1])


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    def update(self):
        # move bullet
        self.rect.x += (self.direction * self.speed) + screen_scroll
        # check if bullet has gone off screen
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()
        #check for collision with level
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()

        # check collision with characters
        rand_num = random.uniform(0, 100)
        for enemy in enemy1_group:
            if pygame.sprite.spritecollide(enemy, bullet_group, False):
                if enemy.alive:
                    if rand_num >= 0 and rand_num <= 15: #15%
                        damage = 75
                    else:
                        damage = 25
                    enemy.health -= damage
                    self.kill()
        for enemy in enemy2_group:
            if pygame.sprite.spritecollide(enemy, bullet_group, False):
                if enemy.alive:
                    if rand_num >= 0 and rand_num <= 20: #20%
                        damage = 75
                    else:
                        damage = 25
                    enemy.health -= damage
                    self.kill()
        for enemy in enemy3_group:
            if pygame.sprite.spritecollide(enemy, bullet_group, False):
                if enemy.alive:
                    if rand_num >= 0 and rand_num <= 5: #5%
                        damage = 100
                    elif rand_num >= 5 and rand_num <= 20: #15%
                        damage = 75
                    else:
                        damage = 25
                    enemy.health -= damage
                    self.kill()
        for enemy in enemy4_group:
            if pygame.sprite.spritecollide(enemy, bullet_group, False):
                if enemy.alive:
                    if rand_num >= 0 and rand_num <= 10: #10%
                        damage = 200
                    elif rand_num >= 10 and rand_num <= 35: #25%
                        damage = 75
                    else:
                        damage = 25
                    enemy.health -= damage
                    self.kill()
        for enemy in enemy5_group:
            if pygame.sprite.spritecollide(enemy, bullet_group, False):
                if enemy.alive:
                    if rand_num >= 0 and rand_num <= 10: #10%
                        damage = 500
                    elif rand_num >= 10 and rand_num <= 40: #30%
                        damage = 75
                    else:
                        damage = 25
                    enemy.health -= damage
                    self.kill()
        

class Arrow(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 5
        self.image = arrow_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    def update(self):
        # move bullet
        self.rect.x += (self.direction * self.speed) + screen_scroll
        # check if bullet has gone off screen
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()
        #check for collision with level
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()
        
        #check collision with characters
        if pygame.sprite.spritecollide(player, arrow_group, False):
            if player.alive:
                player.health -=  35
                self.kill()


class Fireball(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 5
        self.vel_y = 1
        self.image = fireball_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    def update(self):
        # move bullet
        self.rect.x += (self.direction * self.speed) + screen_scroll
        self.rect.y += self.vel_y
        # check if bullet has gone off screen
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()
        #check for collision with level
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()
        
        #check collision with characters
        if pygame.sprite.spritecollide(player, fireball_group, False):
            if player.alive:
                player.health -= 200
                self.kill()


# create screen fades
intro_fade = ScreenFade(screen, 1, BLACK, 6)


# create sprite groups
enemy1_group = pygame.sprite.Group()
enemy2_group = pygame.sprite.Group()
enemy3_group = pygame.sprite.Group()
enemy4_group = pygame.sprite.Group()
enemy5_group = pygame.sprite.Group()

bullet_group = pygame.sprite.Group()
arrow_group = pygame.sprite.Group()
fireball_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
acid_group = pygame.sprite.Group()
spike_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()


#create empty tile list
world_data = []
for row in range(ROWS):
	r = [-1] * COLS
	world_data.append(r)
#load in level data and create world
with open(f'level{level}_data.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            world_data[x][y] = int(tile)
world = World()
player, health_bar = world.process_data(world_data)


run = True
while run:

    clock.tick(FPS)

    if start_game == False:
        #draw menu
        start_game = menu.main_menu(screen, start_game)
        if start_game:
            start_intro = True

    else:
        #update background
        draw_bg()
        #draw world map
        world.draw()
        # show player score
        SCORE = player.score
        draw_text('SCORE: ' + str(SCORE), font1, PINK, 620, 20)
        # show level map
        draw_text('STATE: ' + str(level_show), font1, PINK, 620, 50)
        # show player health
        HEALTH = player.health
        health_bar.draw(player.health)
        draw_text(str(HEALTH), font2, BLACK, 65, 10)
        # show ammo
        AMMO = player.ammo
        draw_text('AMMO: ' + str(AMMO), font1, WHITE, 10, 35)
        # show key
        draw_text('KEY: ', font1, WHITE, 10, 60)
        if player.key == 1:
            screen.blit(key_box_img, (70, 58))


        player.update()
        player.draw()


        for enemy in enemy1_group:
            enemy.ai()
            enemy.update()
            enemy.draw()
        for enemy in enemy2_group:
            enemy.ai()
            enemy.update()
            enemy.draw()
        for enemy in enemy3_group:
            enemy.ai()
            enemy.update()
            enemy.draw()
        for enemy in enemy4_group:
            enemy.ai()
            enemy.update()
            enemy.draw()
        for enemy in enemy5_group:
            enemy.ai()
            enemy.update()
            enemy.draw()


        # update and draw groups
        bullet_group.update()
        arrow_group.update()
        fireball_group.update()
        item_box_group.update(player, screen_scroll)
        decoration_group.update(screen_scroll)
        acid_group.update(screen_scroll)
        spike_group.update(screen_scroll)
        exit_group.update(screen_scroll)

        bullet_group.draw(screen)
        arrow_group.draw(screen)
        fireball_group.draw(screen)
        item_box_group.draw(screen)
        decoration_group.draw(screen)
        acid_group.draw(screen)
        spike_group.draw(screen)
        exit_group.draw(screen)

        
        # show intro
        if start_intro == True:
            if intro_fade.fade():
                start_intro = False
                intro_fade.fade_counter = 0

        # update player actions
        if player.alive:
            # shoot bullets
            if shoot:
                player.shoot()
            if player.in_air:
                player.update_action(2) #jump
            if moving_left or moving_right:
                player.update_action(1) #run
            else:
                player.update_action(0)  #idle
            screen_scroll, level_complete =  player.move(moving_left, moving_right)
            bg_scroll -= screen_scroll

            #check if player has completed the level
            if level_complete:
                level += 1
                level_show += 1
                SCORE += 2000
                bg_scroll = 0
                world_data = reset_level()
                if level <= MAX_LEVELS:
                    #load in level data and create world
                    with open(f'level{level}_data.csv', newline='') as csvfile:
                        reader = csv.reader(csvfile, delimiter=',')
                        for x, row in enumerate(reader):
                            for y, tile in enumerate(row):
                                world_data[x][y] = int(tile)
                    world = World()
                    player, health_bar = world.process_data(world_data)
                    player.score = SCORE
                    player.health = HEALTH
                    player.ammo = AMMO
                if level > MAX_LEVELS:
                    level = 1
                    world_data = reset_level()
                    #load in level data and create world
                    with open(f'level{level}_data.csv', newline='') as csvfile:
                        reader = csv.reader(csvfile, delimiter=',')
                        for x, row in enumerate(reader):
                            for y, tile in enumerate(row):
                                world_data[x][y] = int(tile)
                    world = World()
                    player, health_bar = world.process_data(world_data)
                    player.score = SCORE
                    player.health = HEALTH
                    player.ammo = AMMO
        else:
            screen_scroll = 0
            restart_game = menu.user_input(screen, SCORE, restart_game)
            if restart_game:
                moving_left = False
                moving_right = False
                bg_scroll = 0
                world_data = reset_level()
                #load in level data and create world
                level = 1
                level_show = 1
                with open(f'level{level}_data.csv', newline='') as csvfile:
                    reader = csv.reader(csvfile, delimiter=',')
                    for x, row in enumerate(reader):
                        for y, tile in enumerate(row):
                            world_data[x][y] = int(tile)
                world = World()
                player, health_bar = world.process_data(world_data)
                restart_game = False

    
    for event in pygame.event.get():
        # quit game
        if event.type == pygame.QUIT:
            run = False

        # keyboard presses
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_w and player.alive:
                player.jump = True
            if event.key == pygame.K_SPACE:
                shoot = True
            if event.key == pygame.K_ESCAPE:
                run = False

        # keyboard button released
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_SPACE:
                shoot = False

    pygame.display.update()

pygame.quit()
