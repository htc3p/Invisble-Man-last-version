import pygame
import random

#define game variables
SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)
ROWS = 16
COLS = 150
TILE_SIZE = SCREEN_HEIGHT // ROWS

# define colours
RED = (255, 0, 0)
WHITE = (241, 250, 238)
BLUE = (0,30,255)
PINK = (214,0,255)
GREEN = (0,255,159)
BLACK = (0, 0, 0)

class ItemBox(pygame.sprite.Sprite):
	def __init__(self, item_boxes, item_type, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.item_type = item_type
		self.img = item_boxes[self.item_type]
		self.image = pygame.transform.scale(self.img, (int(self.img.get_width() * 1.2), int(self.img.get_height() * 1.2)))
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

	def update(self, player, screen_scroll):
		# scroll
		self.rect.x += screen_scroll
		# check if the player has picked up the box
		if pygame.sprite.collide_rect(self, player):
			# check what kind of box it was
			if self.item_type == 'Health':
				player.health += 150
				player.score -= 100
				if player.health > player.max_health:
					player.health = player.max_health
			elif self.item_type == 'Ammo':
				player.ammo += 12
				player.score -= 100
			elif self.item_type == 'Key':
				player.key += 1
				player.score += 1000
			# delete the item box
			self.kill()


class HealthBar():
	def __init__(self, screen, x, y, health, max_health):
		self.screen = screen
		self.x = x
		self.y = y
		self.health = health
		self.max_health = max_health

	def draw(self, health):
		#update with new health
		self.health = health
		#calculate health ratio
		ratio = self.health / self.max_health
		pygame.draw.rect(self.screen, BLACK, (self.x - 2, self.y - 2, 154, 24))
		pygame.draw.rect(self.screen, RED, (self.x, self.y, 150, 20))
		pygame.draw.rect(self.screen, GREEN, (self.x, self.y, 150 * ratio, 20))


class Decoration(pygame.sprite.Sprite):
	def __init__(self, img, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.transform.scale(img, (int(img.get_width() * 1.5), int(img.get_height() * 1.5)))
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

	def update(self, screen_scroll):
		self.rect.x += screen_scroll


class Acid(pygame.sprite.Sprite):
	def __init__(self, img, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = img
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

	def update(self, screen_scroll):
		self.rect.x += screen_scroll
 

class Spike(pygame.sprite.Sprite):
	def __init__(self, img, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = img
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

	def update(self, screen_scroll):
		self.rect.x += screen_scroll


class Exit(pygame.sprite.Sprite):
	def __init__(self, img, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.transform.scale(img, (int(img.get_width()), int(img.get_height() * 2)))
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

	def update(self, screen_scroll):
		self.rect.x += screen_scroll