import math
import pygame


class Car:

  def __init__(self, x, y, tracks):
    self.x = x
    self.y = y
    self.vel = 0
    self.angle = 90
    self.prev_angle = 90
    self.img = pygame.image.load("car.png")
    self.img.set_colorkey((0, 0, 0))
    self.front_x = self.x + 10 + 10 * math.sin(math.radians(self.angle))
    self.front_y = self.y + 15 + 15 * math.cos(math.radians(self.angle))
    self.tracks = tracks
    self.color = "BLACK"
    self.checkpoint_reward = 20
    self.stay = 0
    self.speed_penalty = 0

  def normalize(self, value):
      if value < 0.5:
          return 2
      else:
          return 3
        
  def move(self):
    self.x = self.x + math.sin(math.radians(self.angle)) * self.vel
    self.y = self.y + math.cos(math.radians(self.angle)) * self.vel

  def accelerate(self, value):
    sgn = [i for i in [-1, 1] if value*math.fabs(value)*i >= 0][0]
    self.vel += sgn*self.normalize(math.fabs(value))/100
    if self.vel < 0.5:
        self.vel = 0.5
        self.speed_penalty += 1
    if self.vel > 2:
        self.vel = 2

  def turn(self, value):
    sgn = [i for i in [-1, 1] if value*math.fabs(value)*i >= 0][0]
    self.prev_angle = self.angle
    self.angle += sgn*(self.normalize(math.fabs(value)) - self.vel)
    if self.angle < 0:
        self.angle += 360
    if self.angle > 360:
        self.angle -= 360


  def draw(self, win):
    rotated_img = pygame.transform.rotate(self.img, self.angle)
    #new_rect = rotated_img.get_rect(center=self.img.get_rect(center=(self.x, self.y)).center)
    win.blit(rotated_img, (self.x - int(rotated_img.get_width()/2), self.y - int(rotated_img.get_height()/2)))
    #pygame.draw.rect(win, (254, 254, 254), pygame.Rect(self.front_x, self.front_y, 1, 1))

  def get_ends(self):
    self.front_x = max(min(self.x + 10 * math.sin(math.radians(self.angle)), 599),0)
    self.back_x = max(min(self.x - 10 * math.sin(math.radians(self.angle)), 599),0)
    self.front_y = max(min(self.y + 15 * math.cos(math.radians(self.angle)), 299),0)
    self.back_y = max(min(self.y - 15 * math.cos(math.radians(self.angle)), 299),0)
    return self.front_x, self.back_x, self.front_y, self.back_y

  def calc_distance(self, angle, id):
    r, g, b, d = 0, 0, 0, 0
    while (r, g, b) != (109, 129, 98):  #pas rouge :')
      d += 1
      if self.front_x + d * math.sin(math.radians(
          self.angle + angle)) >= 599 or self.front_y + d * math.cos(
              math.radians(self.angle + angle)) >= 299:
        break

      if self.front_x + d * math.sin(math.radians(
          self.angle + angle)) < 0 or self.front_y + d * math.cos(
              math.radians(self.angle + angle)) < 0:
        break

      r, g, b, _ = self.tracks[id].getpixel(
          (self.front_x + d * math.sin(math.radians(self.angle + angle)),
           self.front_y + d * math.cos(math.radians(self.angle + angle))))

    return d

  def generate_inputs(self, id):
    inputs = []
    angles = [-90, -45, -10, 10, 45, 90]
    for i in angles:
      d = self.calc_distance(i, id)
      inputs.append(d)
    return inputs

  def gain_points(self, id):
    r, g, b, a = self.tracks[id].getpixel((self.front_x, self.front_y))
    reward = (self.vel/2)**0.5 - (self.speed_penalty / 1000)
    if (r, g, b) == (69, 69, 69) and self.color == "BLACK":
      self.stay = 0
      self.color = "WHITE"
      reward += self.checkpoint_reward

    elif (r, g, b) == (29, 17, 8) and self.color == "WHITE":
      self.stay = 0
      self.color = "BLACK"
      reward += self.checkpoint_reward

    elif (r, g, b) == (217, 203, 162):
      self.stay = 0

    self.stay += 1
    return reward

