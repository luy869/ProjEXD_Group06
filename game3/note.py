# note.py
import pygame

class Note:
    def __init__(self, direction, appear_time, x, y):
        self.direction = direction
        self.appear_time = appear_time  # 出現予定時刻
        self.x = x
        self.y = y  # Initial Y is at the bottom
        self.hit = False

    def update(self, speed):
        # Make the note move downwards (increase y coordinate)
        self.y += speed

    def draw(self, surface):
        pygame.draw.circle(surface, (255, 0, 0), (self.x, int(self.y)), 20)