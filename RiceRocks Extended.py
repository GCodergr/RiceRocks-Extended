# RiceRocks Extended

# Based on 'Introduction to Interactive Programming in Python' Course
# RICE University - coursera.org
# by Joe Warren, John Greiner, Stephen Wong, Scott Rixner

# To run the game copy following code and paste it at www.codeskulptor.org 

import simplegui
import math
import random

# globals for user interface
WIDTH = 800
HEIGHT = 600
score = 0
high_score = 0
lives = 3
time = 0
started = False
bonus_rock_counter = 0

# global game objects
rock_group = set([])
missile_group = set([])
explosion_group = set([])

ROCK_SPAWNING_DISTANCE = 100

class ImageInfo:
    def __init__(self, center, size, radius = 0, lifespan = None, animated = False):
        self.center = center
        self.size = size
        self.radius = radius
        if lifespan:
            self.lifespan = lifespan
        else:
            self.lifespan = float('inf')
        self.animated = animated

    def get_center(self):
        return self.center

    def get_size(self):
        return self.size

    def get_radius(self):
        return self.radius

    def get_lifespan(self):
        return self.lifespan

    def get_animated(self):
        return self.animated

    
# art assets created by Kim Lathrop, may be freely re-used in non-commercial projects, please credit Kim
    
# debris images - debris1_brown.png, debris2_brown.png, debris3_brown.png, debris4_brown.png
#                 debris1_blue.png, debris2_blue.png, debris3_blue.png, debris4_blue.png, debris_blend.png
debris_info = ImageInfo([320, 240], [640, 480])
debris_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/debris2_blue.png")

# nebula images - nebula_brown.png, nebula_blue.png
nebula_info = ImageInfo([400, 300], [800, 600])
nebula_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/nebula_blue.f2014.png")

# splash image
splash_info = ImageInfo([200, 150], [400, 300])
splash_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/splash.png")

# ship image
ship_info = ImageInfo([45, 45], [90, 90], 35) 
ship_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/double_ship.png")

# missile image - shot1.png, shot2.png, shot3.png
missile_info = ImageInfo([5,5], [10, 10], 3, 50) 
missile_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/shot2.png")

# asteroid images - asteroid_blue.png, asteroid_brown.png, asteroid_blend.png
asteroid_info = ImageInfo([45, 45], [90, 90], 40) 
asteroid_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/asteroid_blue.png")

# animated explosion - explosion_orange.png, explosion_blue.png, explosion_blue2.png, explosion_alpha.png
explosion_info = ImageInfo([64, 64], [128, 128], 17, 24, True)
explosion_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/explosion_alpha.png")

# sound assets purchased from sounddogs.com, please do not redistribute
# .ogg versions of sounds are also available, just replace .mp3 by .ogg
soundtrack = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/soundtrack.mp3")
missile_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/missile.mp3")
missile_sound.set_volume(.5)
# original ship thrust sound:
# ship_thrust_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/thrust.mp3")
ship_thrust_sound = simplegui.load_sound("https://dl.dropboxusercontent.com/s/1ganaqhyr6tzg4j/thrust2.mp3")
explosion_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/explosion.mp3")

# helper functions to handle transformations
def angle_to_vector(ang):
    return [math.cos(ang), math.sin(ang)]

def dist(p, q):
    return math.sqrt((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2)


# Ship class
class Ship:
    def __init__(self, pos, vel, angle, image, info):
        self.pos = [pos[0], pos[1]]
        self.vel = [vel[0], vel[1]]
        self.thrust = False
        self.angle = angle
        self.angle_vel = 0
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        self.weapon_enabled = False
        self.fire_rate = 15 # counted in frames. 60 frames = 1 sec  
        self.fire_timer = self.fire_rate # intialize value (so we can fire instantly)
                
    def draw(self,canvas):
        #draw_size = [self.radius * 2, self.radius * 2]
        #if self.thrust:
            #canvas.draw_image(self.image, [self.image_center[0] + self.image_size[0], self.image_center[1]] , self.image_size,
        #                       self.pos, draw_size, self.angle)
        #else:
            #canvas.draw_image(self.image, self.image_center, self.image_size,
        #                      self.pos, draw_size, self.angle)
        
        
        
        if self.thrust:
            canvas.draw_image(self.image, [self.image_center[0] + self.image_size[0], self.image_center[1]] , self.image_size,
                              self.pos, self.image_size, self.angle)
        else:
            canvas.draw_image(self.image, self.image_center, self.image_size,
                              self.pos, self.image_size, self.angle)
        #canvas.draw_circle(self.pos, self.radius, 1, "White") # collision detection debugging

    def update(self):
        # update angle
        self.angle += self.angle_vel
        
        # update position
        self.pos[0] = (self.pos[0] + self.vel[0]) % WIDTH
        self.pos[1] = (self.pos[1] + self.vel[1]) % HEIGHT

        # update velocity
        if self.thrust:
            acc = angle_to_vector(self.angle)
            self.vel[0] += acc[0] * .1
            self.vel[1] += acc[1] * .1
            
        self.vel[0] *= .99
        self.vel[1] *= .99
        
        # update fire timer
        self.fire_timer += 1
        
        # update ship weapon
        if self.weapon_enabled:
            if self.fire_timer >= self.fire_rate:
                # Shoot a missile
                Ship.shoot(self)
                # reset timer
                self.fire_timer = 0
                
    def enable_weapon(self):
        self.weapon_enabled = True
        
    def disable_weapon(self):
        self.weapon_enabled = False
        # make the weapon available again by initializing the fire timer
        self.fire_timer = self.fire_rate
        
    def set_thrust(self, on):
        self.thrust = on
        if on:
            ship_thrust_sound.rewind()
            ship_thrust_sound.play()
        else:
            ship_thrust_sound.pause()
       
    def increment_angle_vel(self):
        self.angle_vel += .05
        
    def decrement_angle_vel(self):
        self.angle_vel -= .05
        
    def shoot(self):
        global missile_group
        forward = angle_to_vector(self.angle)
        missile_pos = [self.pos[0] + self.radius * forward[0], self.pos[1] + self.radius * forward[1]]
        missile_vel = [self.vel[0] + 6 * forward[0], self.vel[1] + 6 * forward[1]]
        missile = Sprite(missile_pos, missile_vel, self.angle, 0, missile_image, missile_info, missile_sound)
        missile_group.add(missile)
                
    def get_position(self):
        return self.pos
    
    def get_radius(self):
        return self.radius
    
        
# Sprite class
class Sprite:
    def __init__(self, pos, vel, ang, ang_vel, image, info, sound = None):
        self.pos = [pos[0],pos[1]]
        self.vel = [vel[0],vel[1]]
        self.angle = ang
        self.angle_vel = ang_vel
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        self.lifespan = info.get_lifespan()
        self.animated = info.get_animated()
        self.age = 0
        if sound:
            sound.rewind()
            sound.play()
   
    def draw(self, canvas):
        if self.animated:
            image_center = [self.image_center[0] + (self.age * self.image_size[0]), self.image_center[1]]
            canvas.draw_image(self.image, image_center, self.image_size, self.pos, self.image_size, self.angle)
        else:
            canvas.draw_image(self.image, self.image_center, self.image_size, self.pos, self.image_size, self.angle)
            # canvas.draw_circle(self.pos, self.radius, 1, "Red") # collision detection debugging

    def update(self):
        # update angle
        self.angle += self.angle_vel
        
        # update position
        self.pos[0] = (self.pos[0] + self.vel[0]) % WIDTH
        self.pos[1] = (self.pos[1] + self.vel[1]) % HEIGHT
        
        # increment the age of the sprite
        self.age += 1
        
        # check the sprite age
        if self.age >= self.lifespan:
            # we want to remove the sprite
            return True
        else:
            # we want to keep the sprite
            return False
        
    def collide(self, other_object):
        other_pos = other_object.get_position()
        other_radius = other_object.get_radius()
        if dist(self.pos, other_pos) <= (self.radius + other_radius):
            return True
        else:
            return False
    
    def get_position(self):
        return self.pos
    
    def get_radius(self):
        return self.radius
  

# checks collisions between the elements of the group and other_object 
# returns True if there is a collision, else it returns False
def group_collide(group, other_object):
    # initialize result to False (no collision)
    result = False 
    remove_group_set = set([])
    
    for element in group:
        # check for collision
        if element.collide(other_object):            
            remove_group_set.add(element)
            result = True
            # Check if we have rock and ship collision in order to
            # instantiate an explosion for the rock
            if isinstance(other_object, Ship) == True:
                instantiate_explosion(element.pos)
    # update the original group, removing all the collided elements        
    group.difference_update(remove_group_set)    
    return result


# checks collsions between two groups of objects (rocks and missiles)
def group_group_collide(rock_group, missile_group):
    collisions = 0
      
    for rock in list(rock_group):
        if group_collide(missile_group, rock):
            instantiate_explosion(rock.pos)
            rock_group.discard(rock)
            collisions += 1
   
    return collisions


# call the update and draw methods for each sprite in the group
# it also removes dead sprites
def process_sprite_group(sprite_group, canvas):
    remove_sprite_group = set([])
    
    for sprite in sprite_group:
        # update sprite 
        sprite_dead = sprite.update()
        # ckeck if the sprite is dead
        if sprite_dead:
            remove_sprite_group.add(sprite)
        # draw sprite
        sprite.draw(canvas)
        
    # update the original sprite_group, removing all the dead sprites  
    sprite_group.difference_update(remove_sprite_group)
    
# key handlers to control ship   
def keydown(key):
    if key == simplegui.KEY_MAP['left']:
        my_ship.decrement_angle_vel()
    elif key == simplegui.KEY_MAP['right']:
        my_ship.increment_angle_vel()
    elif key == simplegui.KEY_MAP['up']:
        my_ship.set_thrust(True)
    elif key == simplegui.KEY_MAP['space']:
        my_ship.enable_weapon()
        
def keyup(key):
    if key == simplegui.KEY_MAP['left']:
        my_ship.increment_angle_vel()
    elif key == simplegui.KEY_MAP['right']:
        my_ship.decrement_angle_vel()
    elif key == simplegui.KEY_MAP['up']:
        my_ship.set_thrust(False)
    elif key == simplegui.KEY_MAP['space']:
        my_ship.disable_weapon()
        
# mouseclick handlers that reset UI and conditions whether splash image is drawn
def click(pos):
    global started, lives, score 
    center = [WIDTH / 2, HEIGHT / 2]
    size = splash_info.get_size()
    inwidth = (center[0] - size[0] / 2) < pos[0] < (center[0] + size[0] / 2)
    inheight = (center[1] - size[1] / 2) < pos[1] < (center[1] + size[1] / 2)
    if (not started) and inwidth and inheight:
        started = True
        # initialize globals
        lives = 3
        score = 0
        soundtrack.rewind()
        soundtrack.play()


def draw(canvas):
    global time, started, rock_group, my_ship, lives, score, missile_group, explosion_group, high_score, bonus_rock_counter
    
    # animate background
    time += 1
    wtime = (time / 4) % WIDTH
    center = debris_info.get_center()
    size = debris_info.get_size()
    canvas.draw_image(nebula_image, nebula_info.get_center(), nebula_info.get_size(), [WIDTH / 2, HEIGHT / 2], [WIDTH, HEIGHT])
    canvas.draw_image(debris_image, center, size, (wtime - WIDTH / 2, HEIGHT / 2), (WIDTH, HEIGHT))
    canvas.draw_image(debris_image, center, size, (wtime + WIDTH / 2, HEIGHT / 2), (WIDTH, HEIGHT))

    # draw ship 
    my_ship.draw(canvas)
  
    # update ship 
    my_ship.update()

    # process all the sprites (rocks, missiles and exposions)
    process_sprite_group(rock_group, canvas)
    process_sprite_group(missile_group, canvas)
    process_sprite_group(explosion_group, canvas)
       
    # check for collision between rocks and player ship
    if group_collide(rock_group, my_ship):
        lives -= 1
        instantiate_explosion(my_ship.pos)
        
    # check for collision between rocks and missiles
    destroyed_rocks = group_group_collide(rock_group, missile_group)
    score += (destroyed_rocks * 10) 
    
    # update bonus rock counter
    bonus_rock_counter += destroyed_rocks
    # for every 50 destroyed rocks give an extra life
    if bonus_rock_counter >= 50:
        lives += 1
        # reset the bonus counter (we calculate the difference if we are above 50 rocks)
        bonus_rock_counter = bonus_rock_counter - 50
        
    # draw UI 
    canvas.draw_text("Lives", [50, 50], 22, "White", "monospace")
    lives_width_div2 = frame.get_canvas_textwidth(str(lives), 22, "monospace") // 2
    canvas.draw_text(str(lives), [50 + lives_title_width_div2 - lives_width_div2, 80], 22, "White", "monospace")
    
    canvas.draw_text("Score", [680, 50], 22, "White", "monospace")  
    score_width_div2 = frame.get_canvas_textwidth(str(score), 22, "monospace") // 2  
    canvas.draw_text(str(score), [680 + score_title_width_div2 - score_width_div2, 80], 22, "White", "monospace")
    
    canvas.draw_text("High Score", [350, 50], 22, "White", "monospace")
    high_score_width_div2 = frame.get_canvas_textwidth(str(high_score), 22, "monospace") // 2
    canvas.draw_text(str(high_score), [350 + high_score_title_width_div2 - high_score_width_div2, 80], 22, "White", "monospace")
    
    # check if we run out of lives
    if lives <= 0:
        started = False
        rock_group = set([])
        soundtrack.pause()
        # check if we exceeded the current high score
        if score > high_score:
            # set a new high score
            high_score = score 

    # draw splash screen if not started
    if not started:
        canvas.draw_image(splash_image, splash_info.get_center(), 
                          splash_info.get_size(), [WIDTH / 2, HEIGHT / 2], 
                          splash_info.get_size())

        
# timer handler that spawns a rock    
def rock_spawner():
    global rock_group, started
    if started:
        # add a rock only if we have less than 12 rocks on the screen
        if len(rock_group) < 12:
            # check if can spawn far from the ship
            rock_pos = [random.randrange(0, WIDTH), random.randrange(0, HEIGHT)]
            if dist(rock_pos, my_ship.pos) > ROCK_SPAWNING_DISTANCE:
                rock_vel = [random.random() * .6 - .3, random.random() * .6 - .3]
                rock_avel = random.random() * .2 - .1
                rock = Sprite(rock_pos, rock_vel, 0, rock_avel, asteroid_image, asteroid_info)
                rock_group.add(rock)


# instantiate an explosion
def instantiate_explosion(pos):
    global explosion_group
    explosion = Sprite(pos, [0, 0], 0, 0, explosion_image, explosion_info, explosion_sound)
    explosion_group.add(explosion)
    
    
# initialize stuff
frame = simplegui.create_frame("RiceRocks Extended Edition", WIDTH, HEIGHT)

# initialize ship 
my_ship = Ship([WIDTH / 2, HEIGHT / 2], [0, 0], 0, ship_image, ship_info)

# register handlers
frame.set_keyup_handler(keyup)
frame.set_keydown_handler(keydown)
frame.set_mouseclick_handler(click)
frame.set_draw_handler(draw)

timer = simplegui.create_timer(1000.0, rock_spawner)

# Game information 
frame.add_label('Controls:', 100)
frame.add_label('')
frame.add_label('Left Arrow: Turns left', 200)
frame.add_label('Right Arrow: Turns right', 200)
frame.add_label('Up Arrow: Accelerates forward', 250)
frame.add_label('Space: Fires missile', 250)
frame.add_label('"Holding" Space: Autofire', 250)
frame.add_label('')
frame.add_label('You get an extra life', 250)
frame.add_label('every 500 score points', 250)

# get things rolling
timer.start()
frame.start()

# globals for user interface
lives_title_width_div2 = frame.get_canvas_textwidth("Lives", 22, "monospace") // 2
score_title_width_div2 = frame.get_canvas_textwidth("Score", 22, "monospace") // 2
high_score_title_width_div2 = frame.get_canvas_textwidth("High Score", 22, "monospace") // 2
