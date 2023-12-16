import pygame
import os
import math
import random

pygame.font.init()

pygame.init()

WIDTH, HEIGHT = 550, 550

WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))

pygame.display.set_caption("Top Shooter")

BG = pygame.transform.scale(pygame.image.load(os.path.join("images", "bg.png")), (WIDTH, HEIGHT))
PLAYER_IMG = pygame.transform.scale(pygame.image.load(os.path.join("images", "player.png")), (50,50))
BULLET = pygame.transform.scale(pygame.image.load(os.path.join("images", "bullet1.png")), (10,10))
ZOMBIE1 = pygame.transform.scale(pygame.image.load(os.path.join("images", "zombie_small.png")), (50,50))
CREEPY_BG = pygame.transform.scale(pygame.image.load(os.path.join("images", "creepy_bg.jpg")), (WIDTH, HEIGHT))

KILL_COUNT = 0

HIGHEST_RECORD = 0

KILLS = 0

BULLET_SPEED = 10

CUSTOM_FONT = pygame.font.Font("Exquisite Corpse.dfont", 40)
    
TEXT_FONT = pygame.font.Font("Exquisite Corpse.dfont", 30)


def collide(obj1, obj2):
    rect1 = obj1.img.get_rect(topleft=(obj1.x, obj1.y))
    rect2 = obj2.img.get_rect(topleft=(obj2.x, obj2.y))
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y

    mask1 = pygame.mask.from_surface(obj1.img)
    mask2 = pygame.mask.from_surface(obj2.img)
    return rect1.colliderect(rect2) and mask1.overlap(mask2, (offset_x, offset_y)) is not None



class Bullet:
    def __init__(self, x, y, mouse_x, mouse_y, player_angle):
        self.x = x
        self.y = y
        self.player_angle = player_angle
        self.mouse_x = mouse_x
        self.mouse_y = mouse_y
        self.img = BULLET
        self.speed = BULLET_SPEED
        self.mask = pygame.mask.from_surface(self.img)
        self.angle = math.atan2(self.mouse_y - self.y, self.mouse_x - self.x)
        self.x_vel = math.cos(self.angle) * self.speed
        self.y_vel = math.sin(self.angle) * self.speed


    def draw(self, window):
        self.rotate = pygame.transform.rotate(self.img, math.degrees(self.angle) + self.player_angle)
        # position of the bullet
        window.blit(self.rotate, (self.x + 20, self.y + 20))
        self.mask = pygame.mask.from_surface(self.rotate)

    def move(self):
        self.x += int(self.x_vel) 
        self.y += int(self.y_vel) 


    def collision(self, obj):
        return collide(self, obj)
    

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, health = 100):
        self.x = x
        self.y = y
        self.img = PLAYER_IMG
        self.health = health
        self.max_health = health
        self.mask = pygame.mask.from_surface(self.img)
        self.bullet_hold = []
        self.angle = 0
        self.vel = 5
        self.max_bullet = 10
        self.bullet_amount = 45

    def draw(self, window):
        # to calculate the angle between the mouse and player
        mouse_x, mouse_y = pygame.mouse.get_pos()
        # the self.angle to to make the player start by facing upward
        angle = math.degrees(math.atan2(mouse_y - self.y, mouse_x  - self.x)) - self.angle

        # all for rotating the player according
        # the -angle is for ensuring the direction of rotation
        # if "-" not there, it will be inverted
        self.rotate = pygame.transform.rotate(self.img, -angle)
        # this to make the player rotate around the rect this created
        self.rect = self.rotate.get_rect(center = (self.x + self.get_width() / 2, self.y + self.get_height() / 2))
        
        window.blit(self.rotate, self.rect.topleft)
        # the 180 is to make the player rotate 180 to face the mouse
        # its too make sure the player rotating back doesn't screw it up
        self.mask = pygame.mask.from_surface(self.rotate, 180)

        for bullet in self.bullet_hold[:]:
            bullet.draw(window)

        self.healthbar(window)

    def healthbar(self,window):
        # losing the health
        pygame.draw.rect(window, (0,0,0), (self.x, self.y + self.img.get_height() + 10, self.img.get_width(), 10))

        # full health and remainding health
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.img.get_height() + 10, self.img.get_width() * (self.health / self.max_health), 10))

    # create the bullet
    def shoot(self):
        if len(self.bullet_hold) < self.max_bullet and self.bullet_amount >= 1:
            bullet = Bullet(self.x, self.y, *pygame.mouse.get_pos(), self.angle)
            self.bullet_hold.append(bullet)
            self.bullet_amount -= 1
    

    # movement of hte bullet 
    def move_bullet(self):
        for bullet in self.bullet_hold:
            bullet.move()
            if bullet.y > HEIGHT or bullet.y < 0 or bullet.x > WIDTH or bullet.x < 0:
                self.bullet_hold.remove(bullet)
            

    def move(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_a] and self.x - self.vel + 10 > 0:
            self.x -= self.vel
        if keys[pygame.K_d] and self.x + self.vel + self.get_width() - 15 < WIDTH:
            self.x += self.vel
        if keys[pygame.K_w] and self.y - self.vel + 10 > 0:
            self.y -= self.vel
        if keys[pygame.K_s] and self.y + self.vel + self.get_height() - 10 < HEIGHT:
            self.y += self.vel  
        if keys[pygame.MOUSEBUTTONDOWN] and len(self.bullet_hold) < self.max_bullet and self.bullet_amount >= 1:
            self.shoot()
        if keys[pygame.K_r] and self.bullet_amount < 24:
            self.bullet_amount = 45

    def get_width(self):
        return self.img.get_width()

    def get_height(self):
        return self.img.get_height() 
    


class Zombie:
    def __init__(self, x, y,  health = 50):
        self.x = x
        self.y = y
        self.img = ZOMBIE1
        self.mask = pygame.mask.from_surface(self.img)
        self.health = health
        self.flipped = False


    def move_at_player(self, player_x, player_y, vel):

        # the atan2 gives the angle between 2 points
        # it is to determine the direction
        # of the zombie to player
        # use atan2 because it takes 2 parameter(x,y)
        # and return the tangent, (atan2 is more prefered)
        # normal atan only take one parameter and return
        # the arctan of the ratio y/x
        angle = math.atan2(player_y - self.y, player_x - self.x)

        # cos gives the horizontal direction
        self.x += int(vel * math.cos(angle))

        # the sin gives vertical direction
        self.y += int(vel * math.sin(angle))

    def move(self, player_x, player_y, vel):
        self.move_at_player(player_x, player_y, vel)

    def draw(self, window):
        rotated_image = pygame.transform.rotate(self.img, 0)
        window.blit(self.img, (self.x, self.y))
        self.mask = pygame.mask.from_surface(rotated_image, 0)
        

    def collision(self, obj):
        return collide(self, obj)


def main():
    global HIGHEST_RECORD 
    global KILLS
    FPS = 60
    clock = pygame.time.Clock()

    run = True

    zombies = []

    zombie_speed = 2

    round_num = 1

    zombies_left = 0

    break_count = 100

    round_count = 0

    num_zombie = 5

    lost_count = 0

    lost = False

    player = Player(WIDTH / 2 - 25, HEIGHT / 2)


    def draw_window():
        WINDOW.blit(BG, (0,0))

        kills_label = TEXT_FONT.render(f"Kills: {KILLS}", 1, (255,255,255))
        WINDOW.blit(kills_label, (10,10))

        bullet_left = TEXT_FONT.render(f"Bullets: {player.bullet_amount}",1,(255,255,255))
        WINDOW.blit(bullet_left, (10, 40))

        zombie_label = TEXT_FONT.render(f"Zombie Left: {zombies_left}",1,(255,255,255))
        WINDOW.blit(zombie_label, (WIDTH - zombie_label.get_width() - 20, 10))

        if round_count <= 50 and len(zombies) == 0:
            round_label = CUSTOM_FONT.render(f"Round: {round_num}", 1, (255,0,0))
            WINDOW.blit(round_label, (WIDTH / 2 - round_label.get_width() / 2, 235))

        if lost:
            lost_label = CUSTOM_FONT.render("Your Dead", 1,(0,0,0))
            WINDOW.blit(lost_label, (WIDTH / 2 - lost_label.get_width() / 2, 235))



        for zombie in zombies:
            zombie.draw(WINDOW)
            

        player.draw(WINDOW)

        pygame.display.update()

    while run:
        clock.tick(FPS)
        draw_window()


        if len(zombies) == 0 and break_count > 0:
            break_count -= 1
            round_count += 1
            if break_count <= 0:
                round_count = 0
                break_count = 100
                round_num += 1
                num_zombie = 2 * round_num
                for i in range(num_zombie):
                    side = random.choice(["left", "right", "top", "bottom"])
                    
                    if side == "left":
                        x = random.randrange(-100, -50)
                        y = random.randrange(0, HEIGHT)

                    elif side == "right":
                        x = random.randrange(WIDTH + 50, WIDTH + 100)
                        y = random.randrange(0, HEIGHT)
                    elif side == "top":
                        x = random.randrange(0, WIDTH)
                        y = random.randrange(-100, -50)
                    elif side == "bottom":
                        x = random.randrange(0, WIDTH)
                        y = random.randrange(HEIGHT + 50, HEIGHT + 100)

                    zombie = Zombie(x, y)
                    zombies.append(zombie)
                    zombies_left += 1

        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Check for left mouse button click
                player.shoot()



        for zombie in zombies:
            zombie.move(player.x, player.y, zombie_speed)

            if collide(player, zombie):
                player.health -= 10
                zombies.remove(zombie)
                zombies_left -= 1
        
        if player.health <= 0:
            lost = True
            lost_count += 1
        

        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue

            
        for bullet in player.bullet_hold:
            for zombie in zombies:
                if bullet.collision(zombie):
                    player.bullet_hold.remove(bullet)
                    zombie.health -= 3
                    if zombie.health <= 0:
                        zombies.remove(zombie)
                        KILLS += 1
                        zombies_left -= 1
                    break

        player.move()

        # must have this to be able to move bullet
        # otherwise bullet will be stuck
        player.move_bullet()


def main_menu():
    global HIGHEST_RECORD
    run = True
    while run:
        WINDOW.blit(CREEPY_BG, (0, 0))
        title_label = CUSTOM_FONT.render("Press Any Key To Play Again", 1, (255, 255, 255))
        WINDOW.blit(title_label, (WIDTH / 2 - title_label.get_width() / 2, 235))
        highest_record_label = CUSTOM_FONT.render(f"Highest Record: {HIGHEST_RECORD} Kills!", 1, (255, 255, 255))
        WINDOW.blit(highest_record_label, (WIDTH / 2 - highest_record_label.get_width() / 2, 325))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.KEYDOWN:
                main()
                break

    pygame.quit()


main()
main_menu()
