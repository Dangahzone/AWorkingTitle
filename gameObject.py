import pygame

class GameObject:

    def __init__(self, x, y, width, height, image_path):
        image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(image, (width, height))

        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def draw(self, game_window):
        game_window.blit(self.image, (self.x, self.y))

    def move(self, dx, dy):
        self.x += dx
        self.y += dy
