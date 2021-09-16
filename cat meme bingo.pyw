import pygame
from pygame.locals import *
import os
import random
import math



pygame.init()
pygame.mixer.init()

cat_memes = [
  pygame.image.load('cat memes/'+file)
  for file in os.listdir('cat memes')
]

ding = pygame.mixer.Sound('sounds/Ding.mp3')
yay = pygame.mixer.Sound('sounds/Yay.mp3')
grumpy = pygame.transform.scale(pygame.image.load('sprites/grumpy.jpg'),(800,700))
card = pygame.transform.scale(pygame.image.load('sprites/bingocard.jpg'), (750,750))
paw = pygame.transform.scale(pygame.image.load('sprites/paw.png'), (120,120))





def rainbow():
  for r in range(0,256,1):
    yield (r,0,255)
  for b in range(255,150,-1):
    yield (255,0,b)
  while 1:
    for b in range(150,-1,-30):
      yield (255,0,b)
    for g in range(0,256,30):
      yield (255,g,0)
    for r in range(255,-1,-30):
      yield (r,255,0)
    for b in range(0,256,30):
      yield (0,255,b)
    for g in range(255,-1,-30):
      yield (0,g,255)
    for r in range(0,256,30):
      yield (r,0,255)
    for b in range(255,150,-30):
      yield (255,0,b)


def shrink():
  for i in range(9,31):
    yield 30/i
  while 1:
    yield 1

def decr():
  for i in range(9):
    yield 0.8
  while 1:
    yield 0.1

def incr():
  for i in range(9):
    yield random.randint(100,200)
  while 1:
    yield random.randint(400,600)




class BingoCard:
  offsets = [(65,140),(190,140),(315,140),(440,140),(565,140),
             (65,245),(190,245),(315,245),(440,245),(565,245),
             (65,350),(190,350),          (440,350),(565,350),
             (65,455),(190,455),(315,455),(440,455),(565,455),
             (65,560),(190,560),(315,560),(440,560),(565,560),]

  contents: dict['id','surface','got']
  
  def __init__(self, contents:list):
    self.contents = contents
    self.xpos = 0
    self.ypos = 0

    self.time = 0
    self.where_i_was = (0,0)
    self.where_im_going = (0,0)
    self.when_i_left = -1
    self.when_ill_arrive = 0
    self.delay = decr()

  def __repr__(self):
    contents = ', '.join([f'{{{item["id"]}:{item["got"]}}}' for item in self.contents])
    return f'BingoCard({contents})'

  def blit(self, displaysurface):
    displaysurface.blit(card, (self.xpos, self.ypos))
    for idx, item in enumerate(self.contents):
      offset = self.offsets[idx]
      displaysurface.blit(item['surface'], (self.xpos+offset[0], self.ypos+offset[1]))
      if item['got']:
        displaysurface.blit(paw, (self.xpos+offset[0], self.ypos+offset[1]))
        
  def update(self, time):
    self.time += time
    duration = self.when_ill_arrive-self.when_i_left
    elapsed = self.time-self.when_i_left
    x_m = (self.where_im_going[0]-self.where_i_was[0])/duration
    y_m = (self.where_im_going[1]-self.where_i_was[1])/duration
    self.xpos = self.where_i_was[0] + x_m * elapsed
    self.ypos = self.where_i_was[1] + y_m * elapsed

    if self.time < self.when_ill_arrive:
      return

    self.when_i_left = self.when_ill_arrive
    self.when_ill_arrive = self.time + next(self.delay)
    self.where_i_was = self.where_im_going
    self.where_im_going = (random.randint(-150,200), random.randint(-200,150))

  def win(self):
    return '####' in ''.join(map(lambda item: ('.','#')[item['got']], self.contents))

  @classmethod
  def new_random(cls):
    ids = list(range(1,len(cat_memes)))
    random.shuffle(ids)
    ids.insert(random.randint(0,20), 0)
    contents = [{
      'id':id,
      'surface':pygame.transform.scale(cat_memes[id], (120,110)),
      'got':False
    } for id in ids[:24]]
    return cls(contents)


class PopUp:
  def __init__(self, id, speed):
    self.id = id
    self.base_sprite = cat_memes[id]
    self.base_size = self.base_sprite.get_rect()[2:]
    scaleconstant = 200/self.base_size[1]
    self.base_size = tuple(map(lambda i: i*scaleconstant, self.base_size))

    self.scaling = shrink()
    self.scale = next(self.scaling)
    self.sprite = pygame.transform.scale(self.base_sprite, list(map(lambda i: int(i*self.scale), self.base_size)))

    self.angle = math.radians(random.randint(0,359))
    self.x = -random.randint(50,100)*math.cos(self.angle)+random.randint(0,500)
    self.y = -random.randint(50,100)*math.sin(self.angle)+random.randint(0,400)
    self.speed = speed

    self.vitality = 5
    

  def update(self, time):
    self.scale = next(self.scaling)
    self.sprite = pygame.transform.scale(self.base_sprite, list(map(lambda i: int(i*self.scale), self.base_size)))
    self.x += self.speed * time * math.cos(self.angle)
    self.y += self.speed * time * math.sin(self.angle)
    self.vitality -= time

  def blit(self, displaysurface):
    displaysurface.blit(self.sprite, (self.x, self.y))
    
    



class Game:
  def __init__(self):
    self.card = BingoCard.new_random()
    self.ids = list(range(1,len(cat_memes)))
    random.shuffle(self.ids)
    self.ids.insert(0,0)
    self.timegap = decr()
    self.timeuntilroll = next(self.timegap)
    self.popups = []
    self.speeds = incr()
    self.playing = True

  def blit(self, displaysurface):
    self.card.blit(displaysurface)
    for popup in self.popups:
      popup.blit(displaysurface)

  def update(self, time):
    self.timeuntilroll -= time
    if self.timeuntilroll < 0:
      self.timeuntilroll = next(self.timegap)
      newid = self.ids.pop(0)
      self.popups.append(PopUp(newid, next(self.speeds)))

      for item in self.card.contents:
        if item['id'] == newid:
          item['got'] = True
          ding.play()

      if self.card.win():
        self.playing = False
        return

    self.card.update(time)
    for popup in self.popups:
      popup.update(time)

    counter = 0
    for i in range(len(self.popups)):
      if self.popups[counter].vitality < 0:
        del self.popups[counter]
      else:
        counter += 1

  
    


FramePerSec = pygame.time.Clock()
displaysurface = pygame.display.set_mode((800, 680))
pygame.display.set_caption("CAT MEME BINGO YAY")
bgcol = rainbow()

pygame.mixer.music.load('sounds/Cocomall.mp3')
pygame.mixer.music.play(-1, 0.0)

game = Game()
fps = 60

while game.playing:
  for event in pygame.event.get():
    if event.type == QUIT:
      pygame.quit()

  displaysurface.fill(next(bgcol))
  
  game.update(1/fps)
  game.blit(displaysurface)

  pygame.display.update()
  FramePerSec.tick(fps)

pygame.mixer.music.stop()
displaysurface.blit(grumpy, (0,0))
pygame.display.update()
yay.play()

while True:
  for event in pygame.event.get():
    if event.type == QUIT:
      pygame.quit()



  

