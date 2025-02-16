import os.path
import random
import pickle
import neat
import pygame
from PIL import Image
from car import Car
import math

pygame.font.init()
# importing all pictures
filename1 = "circuit0.png"
filename2 = "circuit1.png"
filename3 = "circuit2.png"
filename4 = "circuit3.png"
filename5 = "circuit4.png"
trackpx1 = Image.open(filename1)
trackpx2 = Image.open(filename2)
trackpx3 = Image.open(filename3)
trackpx4 = Image.open(filename4)
trackpx5 = Image.open(filename5)
window = pygame.display.set_mode((trackpx1.size[0], trackpx1.size[1]))
# initialising the font
font = pygame.font.SysFont("comicsans", 15)
gen = 0

class Track:

  def __init__(self):
    self.size = trackpx1.size[0], trackpx1.size[1]
    self.track = [
        Image.open("PIERRE_CUP_ZONED2.png"),
        Image.open("PIERRE_CUP_ZONED3.png"),
        Image.open("PIERRE_CUP_ZONED4.png"),
        Image.open("PIERRE_CUP_ZONED5.png"),
        Image.open("PIERRE_CUP_ZONED6.png")
    ]
    self.gen = 0

  def collide(self, car, id):
    front_x, back_x, front_y, back_y = car.get_ends()
    rf, gf, bf, *a = self.track[id].getpixel((front_x, front_y))
    rb, gb, bb, *a = self.track[id].getpixel((back_x, back_y))
    if (rf, gf, bf) == (109, 129, 98) or (rb, gb, bb) == (109, 129, 98):
      return True
    return False

  def draw(self, win):
    win.blit(self.track, (0, 0))


def draw_screen(screen, cars, BG_IMG, generation, seconds, cars_len, id):
  screen.blit(BG_IMG, (0, 0))
  for car in cars:
    car.draw(screen)

  gen = font.render("Gen: " + str(generation), True, (255, 255, 255))
  screen.blit(gen, (10, 10))
  timer = font.render("Time: " + str(seconds), True, (255, 255, 255))
  screen.blit(timer, (trackpx1.size[0] - timer.get_width(), 10))
  cars_alive = font.render("Cars alive: " + str(cars_len), True,
                           (255, 255, 255))
  screen.blit(cars_alive,
              (10, trackpx1.size[1] - 10 - cars_alive.get_height()))
  screen.blit(cars_alive, (10, 500))
  pygame.display.update()


def eval_genomes(genomes, config):
  global gen
  gen += 1
  nets = []
  cars = []
  ge = []

  #CHOIX DU CIRCUIT
  if gen < 30:
      track_id = 0
  else:
      track_id = random.randint(gen%2, 1)
  pos_id = random.randint(0, 4)
  
  if gen > 100:
      track_id = random.randint(0, 4)
  
  if track_id == 0:
    if pos_id == 0:
      default_x, default_y = 300, 220
    elif pos_id == 1:
      default_x, default_y = 390, 90
    elif pos_id == 2:
      default_x, default_y = 500, 35
    elif pos_id == 3:
      default_x, default_y = 475, 270
    elif pos_id == 4:
      default_x, default_y = 135, 45
  elif track_id == 1:
    if pos_id == 0:
      default_x, default_y = 425, 75
    elif pos_id == 1:
      default_x, default_y = 360, 25
    elif pos_id == 2:
      default_x, default_y = 80, 170
    elif pos_id == 3:
      default_x, default_y = 365, 255
    elif pos_id == 4:
      default_x, default_y = 255, 75
  elif track_id == 2:
    default_x, default_y = 320, 30
  elif track_id == 3:
    default_x, default_y = 385, 35
  elif track_id == 4:
    default_x, default_y = 280, 165
    
  BG_IMG = pygame.image.load(f"PIERRE_CUP_ZONED{track_id+2}.png")
    
  for genome_id, genome in genomes:
    # adding three lists of all nets and genomes
    net = neat.nn.FeedForwardNetwork.create(genome, config)
    nets.append(net)
    cars.append(Car(default_x, default_y, [trackpx1, trackpx2, trackpx3, trackpx4, trackpx5]))
    genome.fitness = 0
    ge.append(genome)

  clock = pygame.time.Clock()
  track = Track()
  clock.get_time()
  running = True
  begin_time = pygame.time.get_ticks()
  frames = 0

  while running:

    #PARAMETRE PYGAME
    clock.tick(60)
    millis = pygame.time.get_ticks()
    seconds = (millis - begin_time) // 1000
    frames += 1

    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        running = False
        pygame.quit()
        quit()
        break

    #GAIN
    for x, car in enumerate(cars):
      gain = car.gain_points(track_id)
      ge[x].fitness += gain

      if track.collide(car, track_id) or car.stay >= 50:
        ge[x].fitness -= 1
        cars.pop(x)
        nets.pop(x)
        ge.pop(x)
        continue
    
      if seconds > 20:
        ge[x].fitness += 1000
        cars.pop(x)
        nets.pop(x)
        ge.pop(x)
        continue

    #ARRET
    if len(cars) == 0:
      running = False

    #MOUVEMENT
    for x, car in enumerate(cars):
      inputs = car.generate_inputs(track_id)
      outputs = nets[x].activate(inputs)
      car.accelerate(outputs[1])
      car.turn(outputs[0])
      car.move()
    

def eval_fitness(config):
    track_id = 0
    pos_id = 0
    fitness = 0
  
    while (track_id, pos_id) != (2, 0):
        clock = pygame.time.Clock()
        track = Track()
        clock.get_time()
        running = True
        begin_time = pygame.time.get_ticks()
        frames = 0

        #CHOIX DU CIRCUIT
        if track_id == 0:
            if pos_id == 0:
              default_x, default_y = 300, 220
            elif pos_id == 1:
              default_x, default_y = 390, 90
            elif pos_id == 2:
              default_x, default_y = 500, 35
            elif pos_id == 3:
              default_x, default_y = 475, 270
            elif pos_id == 4:
              default_x, default_y = 135, 45
            elif track_id == 1:
                if pos_id == 0:
                  default_x, default_y = 425, 75
                elif pos_id == 1:
                  default_x, default_y = 360, 25
                elif pos_id == 2:
                  default_x, default_y = 80, 170
                elif pos_id == 3:
                  default_x, default_y = 365, 255
                elif pos_id == 4:
                  default_x, default_y = 255, 75

        BG_IMG = pygame.image.load(f"PIERRE_CUP_ZONED{track_id+2}.png")

        car = Car(default_x, default_y, [trackpx1, trackpx2, trackpx3, trackpx4, trackpx5])
        with open("winner.pkl", "rb") as f:
            genome = pickle.load(f)
        net = neat.nn.FeedForwardNetwork.create(genome, config)

        while running:

            #PARAMETRE PYGAME
            clock.tick(60)
            millis = pygame.time.get_ticks()
            seconds = (millis - begin_time) // 1000
            frames += 1

            fitness += car.gain_points(track_id)

            for event in pygame.event.get():
              if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                quit()
                break

            if track.collide(car, track_id) or seconds > 30:
              running = False

            #MOUVEMENT
            inputs = car.generate_inputs(track_id)
            outputs = net.activate(inputs)
            car.accelerate(outputs[1])
            car.move()
            if car.vel >= 1:
                car.turn(outputs[0])
    
        pos_id += 1
        if pos_id == 4:
            pos_id = 0
            track_id += 1
    
    return fitness/10
    

def run(config_path):
  config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                              neat.DefaultSpeciesSet, neat.DefaultStagnation,
                              config_path)

  p = neat.Population(config)
  p.add_reporter(neat.StdOutReporter(True))
  stats = neat.StatisticsReporter()
  p.add_reporter(stats)
  #p.add_reporter(neat.Checkpointer(50, 3600))
  #p = neat.Checkpointer.restore_checkpoint('neat-checkpoint-%i' % 99)

  winner = p.run(eval_genomes, 130)

  with open("winner.pkl", "wb") as f:
    pickle.dump(winner, f)
    f.close()

  fitness = eval_fitness(config)
  
  if fitness > 300:
      with open(f"{fitness}.pkl", "wb") as f:
        pickle.dump(winner, f)
        f.close()

  stats.save()



if __name__ == '__main__':
  local_dir = os.path.dirname(__file__)
  config_path = os.path.join(local_dir, "config.txt")
  run(config_path)

