import pygame as pg
from random import uniform, choice, randint
from game_constants import *
vec = pg.math.Vector2

# Base clas for walls and ground:
class Obstacle(pg.sprite.Sprite):
    def __init__(self, game, groups, x, y, w, h):
        self.groups = game.obstacles #groups
        pg.sprite.Sprite.__init__(self, self.groups)
        self.isObstacle = True
        self.isWall = False
        self.isGround = False
        self.game = game
        self.rect = pg.Rect(x, y, w, h)
        self.hit_rect = self.rect
        self.x = x
        self.y = y

class Wall(Obstacle):
    def __init__(self, game, x, y, w, h):
        self.groups = game.obstacles        
        Obstacle.__init__(self, game, self.groups, x, y, w, h)
        self.image = game.wall_img
        self.isWall = True
        self._layer = WALL_LAYER

class Ground(Obstacle):
    def __init__(self, game, x, y, w, h):
        self.groups = game.obstacles        
        Obstacle.__init__(self, game, self.groups, x, y, w, h)
        self.image = game.wall_img
        self.isGround = True
        self._layer = GROUND_LAYER

class SpinningEnemy(pg.sprite.Sprite):
    def __init__(self, game, position, direction):
        self.game = game
        self.groups = game.all_sprites, game.enemies
        pg.sprite.Sprite.__init__(self, self.groups)
        self._layer = BULLET_LAYER
        self.image = game.enemy_img.copy()
        self.isSpinningEnemy = True
        self.isPlatformGuard = False
        self.rect = self.image.get_rect()
        self.hit_rect = self.rect
        self.pos = position #vec(position)
        self.rect.center = position
        self.rotation = 0
        self.rotation_speed = randint(ENEMY_ROTATION_SPEED_MIN, ENEMY_ROTATION_SPEED_MAX)
        self.movement_speed = randint(ENEMY_MOVEMENT_SPEED_MIN, ENEMY_MOVEMENT_SPEED_MAX)
        self.stuckCount = 0
        self.directionVector = vec(0,0)
        self.last_shot = pg.time.get_ticks()

        # get rid of any enemy that spawns on top of an obstacly
        obstacle = pg.sprite.spritecollideany(self, self.game.obstacles)
        colleague = pg.sprite.spritecollideany(self, self.game.enemies)
        if obstacle or colleague != self:
            self.kill()
            # spawn a replacement enemy:
            self.game.spawn_single_spinning_enemy()

    # Rotate an image on its center, staying in the same location:
    def rotate_on_center(self, image, angle):
        orig_rect = image.get_rect()
        rot_image = pg.transform.rotate(image, angle)
        rot_rect = orig_rect.copy()
        rot_rect.center = rot_image.get_rect().center
        rot_image = rot_image.subsurface(rot_rect).copy()
        return rot_image

    def update(self):

        # calculate the new rotation position of the image
        self.rotation += self.rotation_speed * self.game.dt
        if (self.rotation >= 360):
            self.rotation = self.rotation - 360

        # rotate the image by the calculated amount
        self.image = self.rotate_on_center(self.game.enemy_img, self.rotation)
        #self.image = pg.transform.rotate(self.game.enemy_img, self.rotation)

        # Get the distance to the player:
        distanceToPlayer = pg.math.Vector2(self.pos).distance_to(self.game.player.pos)

        # Calculate the direction to the player:
        directionToPlayer =  (self.game.player.pos - self.pos).angle_to(vec(1, 0))

        # Enemy movement:
        oldpos = self.pos.copy()

        if self.stuckCount >= 0 and self.stuckCount < 10:
            self.directionVector = vec(1 * self.movement_speed * self.game.dt, 0).rotate(-directionToPlayer)
            self.directionVector = self.directionVector.rotate(randint(0, 45))
        else:
            self.stuckCount += 1

        self.pos = self.pos +  self.directionVector
        self.rect.center = self.pos

        # see if enemy movement bumps into anything:
        obstacle = pg.sprite.spritecollideany(self, self.game.obstacles) #game.all_sprites ??
        colleague = pg.sprite.spritecollideany(self, self.game.enemies)
        if obstacle or colleague != self:
            self.pos = oldpos.copy()
            self.rect.center = self.pos
            self.stuckCount += 1
            if (self.stuckCount > 10):
                self.directionVector = self.directionVector.rotate(randint(90, 270))
        else:
            if self.stuckCount > 10:
                self.stuckCount = -100

        # Determine if enemy should fire:
        if distanceToPlayer < ENEMY_MINIMUM_FIRE_DISTANCE_TO_PLAYER:
            now = pg.time.get_ticks()
            if now - self.last_shot > ENEMY_BULLET_RATE:
                self.last_shot = now
                dir = vec(1, 0).rotate(-directionToPlayer)
                EnemyBullet(self.game, self.pos, dir)

class Obstacle(pg.sprite.Sprite):
    def __init__(self, game, groups, x, y, w, h):
        self.groups = game.obstacles #groups
        pg.sprite.Sprite.__init__(self, self.groups)
        self.isObstacle = True
        self.isWall = False
        self.isGround = False
        self.game = game
        self.rect = pg.Rect(x, y, w, h)
        self.hit_rect = self.rect
        self.x = x
        self.y = y


# Platform Guard is an enemy of player that protects the platform on which it sits.
# Movement is limited to the horizontal platform.
class PlatformGuard(pg.sprite.Sprite):
    def __init__(self, game, x, y, w, h): # position, direction):
        self.game = game
        self.groups = game.all_sprites, game.enemies
        pg.sprite.Sprite.__init__(self, self.groups)
        self._layer = PLAYER_LAYER
        self.isSpinningEnemy = False
        self.isPlatformGuard = True
        self.image = game.platformguard_img.copy()
        self.pos = vec(x, y)
        self.rect = pg.Rect(x, y, w, h) #self.image.get_rect()
        self.hit_rect = self.rect #PLAYER_HIT_RECT
        self.x = x
        self.y = y
        #self.hit_rect.topleft = self.rect.topleft
        self.vel = vec(0, 0)
        self.movement_speed = self.movement_speed = randint(ENEMY_MOVEMENT_SPEED_MIN, ENEMY_MOVEMENT_SPEED_MAX)
        self.last_shot = pg.time.get_ticks()

    # guard moves towards player when it detects that the player is close.
    # guard also can fire at the player.
    def update(self):

        # Get the distance to the player:
        distanceToPlayer = pg.math.Vector2(self.pos).distance_to(self.game.player.pos)

        # Calculate the direction to the player:
        directionToPlayer =  (self.game.player.pos - self.pos).angle_to(vec(1, 0))
        vectorToPlayer =  vec(1 * self.movement_speed * self.game.dt, 0).rotate(-directionToPlayer)

        # Enemy movement:
        if distanceToPlayer <= ENEMY_MINIMUM_MOVE_DISTANCE_TOWARDS_PLAYER:
            
            oldpos = self.pos.copy()
            
            # dettermine horizontal direction
            if vectorToPlayer.x < 0:
                moveDirection = -1 # moving left
            elif vectorToPlayer.x > 0:
                moveDirection = 1 # moving right
            else:
                moveDirection = 0 # stationary

            # proceed only if character wants to move:
            if moveDirection != 0:
                self.pos = self.pos + vec(moveDirection, 0)
                self.rect.topleft = self.pos

                # see if enemy movement bumps into anything:
                obstacle = pg.sprite.spritecollideany(self, self.game.obstacles) #game.all_sprites ??
                colleague = pg.sprite.spritecollideany(self, self.game.enemies)
                if obstacle or colleague != self:
                    self.pos = oldpos.copy()
                    self.rect.topleft = self.pos
                else:
                    # Ensure that this player remains on top of a platform:
                    newpos = self.pos.copy()

                    # compensate for direction in which enemy player is moving:
                    if moveDirection == -1:
                        xoffset = 0
                    elif moveDirection == 1:
                        xoffset = 32

                    self.pos = self.pos + vec(xoffset, 20)
                    self.rect.topleft = self.pos
                    obstacle = pg.sprite.spritecollideany(self, self.game.obstacles)
                    if (not obstacle):
                        # Don't allow movement
                        self.pos = oldpos.copy()
                    else:
                        # Check from the right side:
                        self.rect.topright = self.pos
                        obstacle = pg.sprite.spritecollideany(self, self.game.obstacles)
                        if (not obstacle):
                            # Don't allow movement
                            self.pos = oldpos.copy()
                        else:
                            # allow movement as there is a platform below.
                            self.pos = newpos

                    # restore rect coordinates:
                    self.rect.topleft = self.pos

        # Determine if guard should fire:
        if distanceToPlayer <= ENEMY_MINIMUM_FIRE_DISTANCE_TO_PLAYER:
            now = pg.time.get_ticks()
            if now - self.last_shot > ENEMY_BULLET_RATE:
                self.last_shot = now
                dir = vec(1, 0).rotate(-directionToPlayer)
                dir = dir.rotate(randint(-10, 10))
                EnemyBullet(self.game, self.pos, dir)


class Bullet(pg.sprite.Sprite):
    def __init__(self, game, position, direction):
        self.game = game
        self.game.sound_player_gunshot.play()
        self.groups = game.all_sprites, game.bullets
        pg.sprite.Sprite.__init__(self, self.groups)
        self._layer = BULLET_LAYER
        self.image = game.bullet_img.copy()
        self.isBullet = True
        self.spawn_time = pg.time.get_ticks()
        self.rect = self.image.get_rect()
        self.hit_rect = self.rect
        self.pos = vec(position)
        self.velocity = direction * BULLET_SPEED * self.game.dt
        self.rect.center = position

    def update(self):
        self.pos += self.velocity# * self.game.dt
        self.rect.center = self.pos
        enemy = pg.sprite.spritecollideany(self, self.game.enemies)
        if enemy:

            self.game.sound_enemy_hit.play()

            # update the score
            if enemy.isPlatformGuard:
                self.game.player_score += POINTS_GUARD
            else:
                self.game.player_score += POINTS_ENEMY

            self.kill()  # kill the bullet
            enemy.kill() # enemy is killed
            
        elif pg.sprite.spritecollideany(self, self.game.obstacles):
            self.kill() # bullets can't go through obstacles

        if pg.time.get_ticks() - self.spawn_time > BULLET_LIFETIME:
            self.kill()

class EnemyBullet(pg.sprite.Sprite):
    def __init__(self, game, position, direction):
        self.game = game
        self.game.sound_enemy_gunshot.play()
        self.groups = game.all_sprites, game.enemybullets
        pg.sprite.Sprite.__init__(self, self.groups)
        self._layer = BULLET_LAYER
        self.image = game.enemy_bullet_img.copy()
        self.isBullet = True
        self.spawn_time = pg.time.get_ticks()
        self.rect = self.image.get_rect()
        self.hit_rect = self.rect
        self.pos = vec(position)
        self.velocity = direction * ENEMY_BULLET_SPEED * self.game.dt
        self.rect.center = position

    def update(self):
        self.pos += self.velocity# * self.game.dt
        self.rect.center = self.pos
        player = pg.sprite.spritecollideany(self, self.game.players)
        if player:
            self.game.sound_player_hit.play()
            self.kill()
            player.kill()

            ##self.game.playing = False # Game Over
        elif pg.sprite.spritecollideany(self, self.game.obstacles):
            self.kill()

        if pg.time.get_ticks() - self.spawn_time > BULLET_LIFETIME:
            self.kill()


class Player(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = PLAYER_LAYER
        self.groups = game.all_sprites, game.players
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.player_img.copy()
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        #self.rect.topleft = (x, y)
        self.hit_rect = PLAYER_HIT_RECT
        self.hit_rect.center = self.rect.center
        self.vel = vec(0, 0)
        self.pos = vec(x, y)
        self.jumpInAction = False
        self.jumpVelocity = vec(0.0)
        self.horiz_direction = 1
        self.gravity = 0.0
        self.last_shot = 0

    def get_keys(self):
        self.rot_speed = 0
        self.vel = vec(0, 0)
        self.x_direction = 0
        self.y_direction = 0

        if self.jumpInAction:
            if self.gravity < 0:
                self.gravity += GRAVITY_UP_INCREMENT
            else:
                self.gravity += GRAVITY_INCREMENT

            self.jumpVelocity = vec(0, self.gravity)

        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT] or keys[pg.K_a]:
            self.vel = vec(-PLAYER_SPEED, 0)
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            self.vel = vec(PLAYER_SPEED, 0)
        if keys[pg.K_UP] or keys[pg.K_w]:
            if not self.jumpInAction:
                self.jumpInAction = True
                self.jumpVelocity = vec(0, -PLAYER_INITIAL_JUMP_HEIGHT)
                self.gravity = PLAYER_JUMP_SPEED
        if keys[pg.K_SPACE]:
            # Player wants to shoot
            now = pg.time.get_ticks()
            if now - self.last_shot > BULLET_RATE and len(self.game.bullets) <= BULLET_MAX_ACTIVE:
                self.last_shot = now
                dir = vec(self.horiz_direction, 0) # 1 = right, -1 = left
                
                if (self.horiz_direction > 0):
                    pos = self.pos + BARREL_OFFSET_RIGHT
                else:
                    pos = self.pos + BARREL_OFFSET_LEFT

                # Spawn bullet:
                Bullet(self.game, pos, dir)

        self.vel += self.jumpVelocity  # combine with jump velocity

    def collide_hit_rect(self, first, second):
        return first.hit_rect.colliderect(second.rect)

    def collide_with_obstacles(self, group, direction):
        collision = False
        if direction == 'x':
            hits = pg.sprite.spritecollide(self, group, False, self.collide_hit_rect)
            if hits:
                if hits[0].rect.centerx > self.hit_rect.centerx:
                    collision = True
                if hits[0].rect.centerx < self.hit_rect.centerx:
                    collision = True
        if direction == 'y':
            hits = pg.sprite.spritecollide(self, group, False, self.collide_hit_rect)
            if hits:
                if hits[0].rect.centery > self.hit_rect.centery:
                    collision = True
                if hits[0].rect.centery < self.hit_rect.centery:
                    collision = True
        return collision

    def update(self):
        self.get_keys()
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        horiz_collision = False
        vert_collision = False

        if (self.vel.x != 0):
           oldpos = self.pos.copy()
           self.pos += vec(self.vel.x, 0) * self.game.dt
           self.hit_rect.centerx = self.pos.x
           self.hit_rect.centery = self.pos.y
           horiz_collision = self.collide_with_obstacles(self.game.obstacles, 'x')
           if horiz_collision:
               # restore old values
               self.pos = oldpos.copy()
               self.hit_rect.centerx = self.pos.x
               self.hit_rect.centery = self.pos.y
           else:
               if self.vel.x < 0:
                   self.image = pg.transform.flip(self.game.player_img, 1, 0)
                   self.horiz_direction = -1
               elif self.vel.x > 0:
                   self.image = self.game.player_img
                   self.horiz_direction = 1

        oldpos = self.pos.copy()
        if self.jumpInAction:
            self.pos += vec(0, self.vel.y) * self.game.dt
        else:
            if (self.gravity == 0):
                self.gravity = GRAVITY_INITIAL_DOWN_SPEED
            self.pos += (vec(0, self.vel.y)
                          + vec(0, self.gravity)) * self.game.dt # add last value of gravity

        self.hit_rect.centerx = self.pos.x
        self.hit_rect.centery = self.pos.y
        vert_collision = self.collide_with_obstacles(self.game.obstacles, 'y')
        if vert_collision:
            # restore old values
            self.pos = oldpos.copy()
            self.hit_rect.centerx = self.pos.x
            self.hit_rect.centery = self.pos.y

        if vert_collision and self.jumpInAction:
            if self.gravity > 0: # means we are going down and landed
                self.jumpVelocity = vec(0, 0)
                self.jumpInAction = False
                #self.gravity = 0.0 # don't change to 0, so that it can be used when falling off edge.
            else:
                self.gravity = GRAVITY_INITIAL_DOWN_SPEED #50  # hit a ceiling and must come back down

        self.rect.center = self.hit_rect.center # do we still need this?

        enemy = pg.sprite.spritecollideany(self, self.game.enemies)
        if enemy:
            # Special case where player touches an enemy.
            # Player collects points and kills enemy on touch!
            enemy.kill()
            self.game.sound_enemy_crushed.play()

            # update the score
            if enemy.isPlatformGuard:
                self.game.player_score += POINTS_GUARD_BONUS
            else:
                self.game.player_score += POINTS_ENEMY_BONUS


