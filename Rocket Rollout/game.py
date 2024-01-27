# SETUP + INITIALIZATION
import pygame
import sys
import random
import time
pygame.init()

screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Rocket Rollout")
pygame.display.set_icon(pygame.image.load("media/sprites/rocket/rocket_default.png"))
clock = pygame.time.Clock()
fps = 60
dt = clock.tick(fps)/1000.0
time_baseline = 0



# VARIABLES
white = (255, 255, 255)
gray = (50, 50, 50)
black = (0, 0, 0)
red = (255, 0, 0)
yellow = (255, 255, 0)



# FONTS
roboto_big = pygame.font.SysFont("Roboto", 150)
roboto_small = pygame.font.SysFont("Roboto", 30)

# SOUNDS
explosion_sound = pygame.mixer.Sound("media/sounds/explosion.mp3")


# SPRITES

# Images
bullet_image = pygame.image.load("media/sprites/bullet.png")
enemy_image = pygame.image.load("media/sprites/enemy.png")
enemy_bullet_image = pygame.image.load("media/sprites/enemy_bullet.png")

# Actual Sprites
background = pygame.image.load("media/sprites/background.png")

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.is_moving = False
        self.default_frame = pygame.image.load("media/sprites/rocket/rocket_default.png")
        self.frames = []
        for i in range(1, 5): # Listing all sprite names
            image = pygame.image.load(f"media/sprites/rocket/rocket_{i}.png")
            self.frames.extend([image]*5) # 5 identical frames
        self.frame_no = 0
        self.image = self.frames[self.frame_no]

        self.rect = self.image.get_rect(center=((screen_width/2), (screen_height-100)))
        self.speed = 600 * dt
        self.frame = 1

        self.energy = 200
        self.health = 200

    def movement(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and keys[pygame.K_RIGHT]:
            move_x = 0
            self.is_moving = False
        elif keys[pygame.K_LEFT] and self.rect.left >= 0:
            move_x = -self.speed
            self.is_moving = True
        elif keys[pygame.K_RIGHT] and self.rect.right <= screen_width:
            move_x = self.speed
            self.is_moving = True
        else:
            move_x = 0
            self.is_moving = False
        self.rect.x += move_x

        if keys[pygame.K_SPACE] and self.energy >= 200:
            self.shoot()
        elif self.energy < 200:
            self.energy += 4

    def shoot(self):
        bullet.add(Bullet())
        self.energy = 0

    def animate(self):
        if self.is_moving and self.frame_no < len(self.frames)-1:
            self.image = self.frames[self.frame_no]
            self.frame_no += 1
        elif self.is_moving and self.frame_no == len(self.frames)-1:
            self.image = self.frames[self.frame_no]
            self.frame_no = 0
        else:
            self.frame_no = 0
            self.image = self.default_frame

    def collision_bullet_to_player(self):
        bullet_hit_list = pygame.sprite.spritecollide(player.sprite, enemy_bullet, False)
        if bullet_hit_list:
            for bullet_hit in bullet_hit_list:
                bullet_hit.kill()
                self.health -= 20
                enemy_explosion.add(Enemy_Explosion(self.rect.centerx, self.rect.centery-50))

    def update(self):
        self.movement()
        self.animate()
        self.collision_bullet_to_player()

        # Energy and Health Display
        self.draw_energy()
        self.draw_health()

    def draw_energy(self):  # Draw Energy
        pygame.draw.rect(screen, yellow, (10, 10, self.energy, 30))
        pygame.draw.rect(screen, gray, (10, 10, 200, 30), 2)
        energy_text = roboto_small.render("Energy", False, gray)
        screen.blit(energy_text, (70, 15))

    def draw_health(self):  # Draw Health
        pygame.draw.rect(screen, red, (10, 50, self.health, 30))
        pygame.draw.rect(screen, gray, (10, 50, 200, 30), 2)
        roboto_small.render("Health", False, white)
        health_text = roboto_small.render("Health", False, gray)
        screen.blit(health_text, (70, 55))

player = pygame.sprite.GroupSingle()
player.add(Player())

class Bullet(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = bullet_image
        self.rect = self.image.get_rect(center=(player.sprite.rect.centerx, player.sprite.rect.centery))
        self.speed = 1000 * dt

    def shoot(self):
        self.rect.y -= self.speed
        if self.rect.bottom < 0:
            self.kill()

    def update(self):
        self.shoot()

bullet = pygame.sprite.Group()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos_x):
        super().__init__()
        self.image = enemy_image
        self.rect = self.image.get_rect(bottom=0, x=pos_x)
        self.speed = 200 * dt
        self.energy = random.randint(0, 200)


    def move(self):
        self.rect.y += self.speed

    def shoot(self):
        if self.energy >= 200:
            enemy_bullet.add(Enemy_Bullet(self.rect.centerx, self.rect.centery))
            self.energy = 0
        else:
            self.energy += 2

    def collision_bullet_to_enemy(self):
        for bullet_sprite in bullet.sprites():
            enemy_hit_list = pygame.sprite.spritecollide(bullet_sprite, enemy, False)
            for enemy_hit in enemy_hit_list:
                bullet_sprite.kill()
                enemy_hit.explode()

    def collision_enemy_to_player(self):
        enemy_hit_list = pygame.sprite.spritecollide(player.sprite, enemy, False)
        if enemy_hit_list:
            for enemy_hit in enemy_hit_list:
                enemy_hit.explode()
                player.sprite.health -= 40

    def collision_enemy_to_home(self):
        if self.rect.top > screen_height:
            player.sprite.health -= 80
            self.explode(home_hit=True)

    def explode(self, home_hit =False):
        self.kill()
        if home_hit:
            enemy_explosion.add(Enemy_Explosion(self.rect.centerx, screen_height)) # W Spawn the explosion halfway
        else:
            enemy_explosion.add(Enemy_Explosion(self.rect.centerx, self.rect.centery))

    def update(self):
        self.shoot()
        self.move()
        self.collision_bullet_to_enemy()
        self.collision_enemy_to_player()
        self.collision_enemy_to_home()

enemy = pygame.sprite.Group()

class Enemy_Bullet(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__()
        self.image = enemy_bullet_image
        self.rect = self.image.get_rect(center=(pos_x, pos_y))
        self.speed = 750 * dt

    def shoot(self):
        self.rect.y += self.speed
        if self.rect.top > screen_height:
            self.kill()

    def update(self):
        self.shoot()


enemy_bullet = pygame.sprite.Group()

class Enemy_Explosion(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__()
        self.frames = []
        for i in range(1, 7):  # Listing all sprite names
            image = pygame.image.load(f"media/sprites/explosion/explosion_{i}.png")
            self.frames.extend([image] * 5)  # 5 identical frames
        self.frame_no = 0
        self.image = self.frames[self.frame_no]
        self.rect = self.image.get_rect(centerx=pos_x, centery=pos_y)
        # explosion_sound.play()

    def update(self):
        self.frame_no += 1
        self.image = self.frames[self.frame_no]
        if self.frame_no >= 29:
            self.kill()

enemy_explosion = pygame.sprite.Group()



# EXTRA FUNCTIONS
current_spawn_index = 0
spawn_order = [1, 2, 3, 4]
random.shuffle(spawn_order)
spawn_section_dict = {
    1: (0, screen_width // 4),
    2: (screen_width // 4, screen_width // 2),
    3: (screen_width // 4, (screen_width // 2 + screen_width // 4)),
    4: ((screen_width // 2 + screen_width // 4), screen_width - 100)
}
spawn_delay = 2
double_chance = 10
triple_chance = 10 # 10% of double chance so 1%
last_spawn_time = pygame.time.get_ticks() // 1000 - time_baseline
def enemy_spawning():
    global current_spawn_index, spawn_order,spawn_section_dict, spawn_delay, last_spawn_time, time, double_chance, triple_chance, time_baseline
    time_diff = time - last_spawn_time

    time = pygame.time.get_ticks() // 1000 - time_baseline
    time_diff = time - last_spawn_time  # Time since last spawn

    if time_diff > spawn_delay:
        spawn_section_index = spawn_order[current_spawn_index]
        spawn_section = spawn_section_dict[spawn_section_index]
        spawn_pos = [random.randint(*spawn_section)]

        if time > 25 and random.randint(0, 100) < double_chance:
            if time > 50 and random.randint(0, 100) < triple_chance:
                spawn_pos = []
                for spawn_section_index in spawn_order:
                    spawn_pos_single = random.randint(spawn_section_dict[5 - spawn_section_index][0],
                                                      spawn_section_dict[5 - spawn_section_index][1])
                    spawn_pos.append(spawn_pos_single)
                current_spawn_index += 3
            else:
                spawn_pos_single = random.randint(spawn_section_dict[5 - spawn_section_index][0],
                                                  spawn_section_dict[5 - spawn_section_index][1])
                spawn_pos.append(spawn_pos_single)
                current_spawn_index += 1

        if time > 50:  # Level 3
            spawn_delay = 1
            double_chance = 20
            for spawn_pos_single in spawn_pos:
                enemy.add(Enemy(spawn_pos_single))
            current_spawn_index += 1
            last_spawn_time = pygame.time.get_ticks() // 1000 - time_baseline

        elif time > 25:  # Level 2:
            spawn_delay = 1
            for spawn_pos_single in spawn_pos:
                enemy.add(Enemy(spawn_pos_single))
            current_spawn_index += 1
            last_spawn_time = pygame.time.get_ticks() // 1000 - time_baseline


        else:  # Level 1:
            for spawn_pos_single in spawn_pos:
                enemy.add(Enemy(spawn_pos_single))
            current_spawn_index += 1
            last_spawn_time = pygame.time.get_ticks() // 1000 - time_baseline

        if current_spawn_index > 3:
            current_spawn_index = 0
            last_spawn_time = pygame.time.get_ticks() // 1000 - time_baseline



# GAME LOOP
game_over = False
game_retry = False
while 1:
    if game_over:
        screen.blit(background, (0, 0))
        game_over_text = roboto_big.render("GAME OVER", False, white)
        game_over_text_rect = game_over_text.get_rect(center=(screen_width // 2, screen_height // 2))

        # Wiping the window clean
        player.sprite.kill()
        for sprite in bullet.sprites():
            sprite.kill()
        for sprite in enemy.sprites():
            sprite.kill()
        for sprite in enemy_bullet.sprites():
            sprite.kill()
        for sprite in enemy_explosion.sprites():
            sprite.kill()

        while game_over:
            screen.blit(game_over_text, game_over_text_rect)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:  # If quitting, then quit lol
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        game_over = False
                        game_retry = True

            pygame.display.update()



    elif game_retry:
        # Kinda a new game state
        player.add(Player())
        current_spawn_index = 0
        spawn_order = [1, 2, 3, 4]
        random.shuffle(spawn_order)
        spawn_delay = 2
        double_chance = 10
        triple_chance = 10  # 10% of double chance so 1%
        time_baseline = pygame.time.get_ticks() // 1000
        last_spawn_time = pygame.time.get_ticks() // 1000 - time_baseline
        game_retry = False



    else:
        while 1:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: # If quitting, then quit lol
                    pygame.quit()
                    sys.exit()

            screen.blit(background, (0,0))

            time = pygame.time.get_ticks() // 1000 - time_baseline


            # Update all sprites
            player.update()
            bullet.update()
            enemy_spawning()
            enemy.update()
            enemy_explosion.update()
            enemy_bullet.update()
            # Draw all sprites
            enemy_bullet.draw(screen)
            enemy_explosion.draw(screen)
            bullet.draw(screen)
            enemy.draw(screen)
            player.draw(screen)
            if player.sprite.health <= 0:
                game_over = True
                break

            pygame.display.update()
            dt = clock.tick(fps)/1000.0