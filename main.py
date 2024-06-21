import pygame as pg
import pytmx
import sys
from os import path
from random import Random
from game_constants import *
from game_sprites import *
from time import *

class MyGame:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
        pg.display.set_caption("Ryan's Platform Shooter")
        self.clock = pg.time.Clock()
        self.game_level = 1
        self.game_previous_level = 0 # used to spawn platform guards and other enemies when moving to new level
        self.player_score = 0
        self.player_lives = PLAYER_LIVES
        self.player_newlife_total_score = 0

        # initialize game folders:
        self.game_folder = path.dirname(__file__)
        self.map_folder = path.join(self.game_folder, 'maps')
        self.img_folder = path.join(self.game_folder, 'img')
        self.sound_folder = path.join(self.game_folder, 'sound') 

        # Load the required images:
        self.player_img = pg.image.load(path.join(self.img_folder, PLAYER_IMG)).convert_alpha()
        self.bullet_img = pg.image.load(path.join(self.img_folder, BULLET_IMG)).convert_alpha()
        self.enemy_img =  pg.image.load(path.join(self.img_folder, ENEMY_IMG)).convert_alpha()
        self.platformguard_img =  pg.image.load(path.join(self.img_folder, PLATFORM_GUARD_IMG)).convert_alpha()
        self.enemy_bullet_img = pg.image.load(path.join(self.img_folder, ENEMY_BULLET_IMG)).convert_alpha()
        self.wall_img = pg.image.load(path.join(self.img_folder, WALL_IMG)).convert_alpha()
        self.title_font = None

        # Load the required sound effects:
        self.sound_player_gunshot = pg.mixer.Sound(path.join(self.sound_folder, SOUND_PLAYER_GUNSHOT))
        self.sound_player_hit = pg.mixer.Sound(path.join(self.sound_folder, SOUND_PLAYER_HIT))
        self.sound_enemy_gunshot = pg.mixer.Sound(path.join(self.sound_folder, SOUND_ENEMY_GUNSHOT))
        self.sound_enemy_hit = pg.mixer.Sound(path.join(self.sound_folder, SOUND_ENEMY_HIT))
        self.sound_enemy_crushed = pg.mixer.Sound(path.join(self.sound_folder, SOUND_ENEMY_CRUSHED))
        self.sound_life_earned = pg.mixer.Sound(path.join(self.sound_folder, SOUND_LIFE_EARNED))
        self.sound_level_complete = pg.mixer.Sound(path.join(self.sound_folder, SOUND_LEVEL_COMPLETE))

    def load_data(self):
        pass        

    def new(self):
        self.screen = pg.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))

        # initialize the required sprite groups for the game
        self.all_sprites = pg.sprite.Group()
        self.obstacles = pg.sprite.Group()
        self.players =  pg.sprite.Group()
        self.enemies = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
        self.enemybullets = pg.sprite.Group()

        # Load the tiled map:
        #
        # Note: To supported Tiled maps, need to install pytmx
        #       using command: 'pip install pytmx'
        #
        self.tiled_map = TiledMap(path.join(self.map_folder, 'TexturesGameMap.tmx'))
        self.tiled_map_img = self.tiled_map.make_map()
        self.tiled_map_rect = self.tiled_map_img.get_rect()

        # Create only the static objects (walls and obstacles) found in map:
        # NOTE: The following are spawned in start_level: 'player' and 'guard'
        for tile_object in self.tiled_map.tmxdata.objects:

            if tile_object.name == 'obstacle':
                Obstacle(self, tile_object.x+16, tile_object.y,
                         tile_object.width, tile_object.height)
                
            if tile_object.name == 'wall' or tile_object.name == 'ground':
                Wall(self, tile_object.x, tile_object.y,
                         tile_object.width, tile_object.height)

        self.viewPort = ViewPort(self.tiled_map.width, self.tiled_map.height)

    # start_level() is called whenever a new game or a new level is started.
    # Difficulty is increased on each level by increasing the number of enemies.
    def start_level(self):

        # Make sure all active bullets in the air are removed from previous game play:

        ## NOTE: The following do not work.
            #self.bullets.empty()  
            #self.enemybullets.empty()

        # get rid of all active player bullets:
        for each in self.bullets:
            each.kill()

        # get rid of all active enemy bullets:
        for each in self.enemybullets:
            each.kill()

        # save number of active enemies for following for loop.
        # this is required to preserve the enemies when player is killed.
        numEnemies = len(self.enemies)

        # spawn only if random number 1-100 falls below the spawn chance number:
        platformGuardSpawnChance = self.game_level * 10

        # Spawn the player and platform guards as specified in the map:
        for tile_object in self.tiled_map.tmxdata.objects:

            # Spawn the guards only if starting a new level:
            if (self.game_previous_level < self.game_level and numEnemies == 0): 
                if tile_object.name == 'guard':
                    if randint(1, 100) < platformGuardSpawnChance:
                        self.enemyPlayer = PlatformGuard(self, tile_object.x, tile_object.y,
                                                        tile_object.width, tile_object.height)
            if tile_object.name == 'player':
                if len(self.players) == 0:
                    self.player = Player(self, tile_object.x, tile_object.y)

        # Spawn the spinning enemies only if starting a new level:
        if (self.game_previous_level < self.game_level): 
            self.spawn_spinning_enemies()

        # Set previous leve to current level:
        self.game_previous_level = self.game_level

    def spawn_single_spinning_enemy(self):
            # Spawn each enemy in random location on map, 
            # but between the right half of display and the end of the map.
            enX = randint(int(DISPLAY_WIDTH/2), int(MAP_WIDTH-50))
            enY = randint(int(MAP_HEIGHT/2), int(MAP_HEIGHT-50))
            SpinningEnemy(self, vec(enX, enY), 0)
    
    def spawn_spinning_enemies(self):
        # Spawn a specific number of spinning enemies, dependent on level number.
        for i in range(self.game_level * 3):
            self.spawn_single_spinning_enemy()
       
    def run(self):
        # game loop - set self.playing = False to end the game
        self.playing = True
        while self.playing:
            self.dt = self.clock.tick(DESIRED_FPS) / 1000.0
            self.events()
            self.update()
            self.draw()

            # Was the player killed:
            if len(self.players) == 0:
                if self.player_lives > 1: # Any spare lives left?
                    self.player_lives -= 1 # decrease # lives and...
                    self.start_level() # restart with the same level, but respawn the player.
                else:  
                    # Else, end of game:
                    self.player_lives = 0  # shown on game over screen
                    self.playing = False
                
            if len(self.enemies) == 0:
                # kill the player sprite so that it can be respawned to original location:
                self.player.kill()

                # increase level and start playing.
                self.sound_level_complete.play()
                self.game_level += 1
                self.player_score += POINTS_LEVEL_BONUS
                self.start_level()

    def quit(self):
        pg.quit()
        sys.exit()

    def draw(self):
        self.screen.fill(BACKGROUND_COLOUR)
        self.draw_grid()
        self.all_sprites.draw(self.screen)
        pg.display.flip()     

    def draw_text(self, text, font_name, size, color, x, y, align="topleft"):
        font = pg.font.Font(font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(**{align: (x, y)})
        self.screen.blit(text_surface, text_rect)

    # process keyboard events:
    def events(self):
        # catch all events here
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.playing = False
                    #self.quit()

    def update(self):
        # update portion of the game loop
        self.all_sprites.update()
        self.viewPort.update(self.player)
 
    def draw_grid(self):
        for x in range(0, DISPLAY_WIDTH, TILE_SIZE):
            pg.draw.line(self.screen, LIGHTGRAY, (x, 0), (x, DISPLAY_HEIGHT))
        for y in range(0, DISPLAY_HEIGHT, TILE_SIZE):
            pg.draw.line(self.screen, LIGHTGRAY, (0, y), (DISPLAY_WIDTH, y))

    def draw(self):
        ## pg.display.set_caption("{:.2f}".format(self.clock.get_fps()))
        self.screen.blit(self.tiled_map_img, self.viewPort.apply_rect(self.tiled_map_rect))
        # self.draw_grid()
        for sprite in self.all_sprites:
            ##if isinstance(sprite, Mob):
            ##    sprite.draw_health()
            self.screen.blit(sprite.image, self.viewPort.apply(sprite))

        self.display_score()

        pg.display.flip()

    def display_score(self, colour = YELLOW):

        # Determine if player earned a bonus life:
        if self.player_score - self.player_newlife_total_score >= SCORE_NEW_LIFE:
            self.sound_life_earned.play()
            self.player_newlife_total_score += SCORE_NEW_LIFE
            self.player_lives += 1

        level_str = "Level: " + str(self.game_level)
        lives_str = "Lives: " + str(self.player_lives)
        score_str = "Score: " + str(self.player_score)
        enemies_str = "Enemies: " + str(len(self.enemies))
        entire_text =  level_str + "     " + lives_str + "     " + score_str+ "     " + enemies_str
        self.draw_text(entire_text, self.title_font, 24, colour,
                      25, 15, align="topleft") #"center")

    def display_start_screen(self):
        self.screen.fill(CYAN)
        self.draw_text("Ryan's Platform Shooter", self.title_font, 100, BLACK,
                       DISPLAY_WIDTH/2, DISPLAY_HEIGHT*.30, align="center")
                  
        self.draw_text("Press Enter to Begin", self.title_font, 60, BLACK,
                       DISPLAY_WIDTH/2, DISPLAY_HEIGHT*0.50, align="center")
        
        pointsTextHeight = DISPLAY_HEIGHT*0.70
        textSpacing = 32
        self.draw_text("---- POINTS ----", self.title_font, 30, BLACK, 
                       DISPLAY_WIDTH/2, pointsTextHeight, align="center")

        pointsTextHeight += textSpacing
        points_str = "Platform Guards: " + str(POINTS_GUARD) + "      Spinning Enemies: " + str(POINTS_ENEMY) + "      Level completion: " + str(POINTS_LEVEL_BONUS)
        self.draw_text(points_str, self.title_font, 25, BLACK, 
                       DISPLAY_WIDTH/2, pointsTextHeight, align="center")

        pointsTextHeight += textSpacing
        points_str = "Crushing enemies on impact:   Guards: " + str(POINTS_GUARD_BONUS) + "      Spinning Enemies: " + str(POINTS_ENEMY_BONUS)
        self.draw_text(points_str, self.title_font, 25, BLACK, 
                       DISPLAY_WIDTH/2, pointsTextHeight, align="center")
        
        pointsTextHeight += textSpacing
        points_str = "New life for every " + str(SCORE_NEW_LIFE) + " points earned."
        self.draw_text(points_str, self.title_font, 25, BLACK, 
                       DISPLAY_WIDTH/2, pointsTextHeight, align="center")

        pointsTextHeight += textSpacing * 1.5
        self.draw_text("---- KEYS ----", self.title_font, 30, BLACK, 
                       DISPLAY_WIDTH/2, pointsTextHeight, align="center")

        pointsTextHeight += textSpacing
        instr_str = "Left(a) & Right(d) = Move      Up(w) = Jump      Spacebar = Fire"
        self.draw_text(instr_str, self.title_font, 25, BLACK, 
                       DISPLAY_WIDTH/2, pointsTextHeight, align="center")
        
        pg.display.flip()
        self.wait_for_EnterKey()

    def display_game_over_screen(self):
        self.screen.fill(CYAN)
        self.display_score(BLACK)
        self.draw_text("GAME OVER", self.title_font, 100, BLACK,
                       DISPLAY_WIDTH/2, DISPLAY_HEIGHT/2, align="center")
        
        self.draw_text("Press Enter to Continue", self.title_font, 60, BLACK,
                       DISPLAY_WIDTH/2, DISPLAY_HEIGHT*3/4, align="center")
        pg.display.flip()
        self.wait_for_EnterKey()

    def wait_for_EnterKey(self):
        keepLooping = True
        pg.event.wait()
        while keepLooping:
            self.clock.tick(DESIRED_FPS)
            for keyevent in pg.event.get():
                if keyevent.type == pg.QUIT:
                    keepLooping = False
                    self.quit()
                if keyevent.type == pg.KEYUP:
                    if keyevent.key == pg.K_RETURN or keyevent.key == pg.K_KP_ENTER:
                        keepLooping = False

 
class TiledMap:
    def __init__(self, filename):
        tm = pytmx.load_pygame(filename, pixelalpha=True)
        self.width = tm.width * tm.tilewidth
        self.height = tm.height * tm.tileheight
        self.tmxdata = tm

    def render(self, surface):
        ti = self.tmxdata.get_tile_image_by_gid
        for layer in self.tmxdata.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid, in layer:
                    tile = ti(gid)
                    if tile:
                        surface.blit(tile, (x * self.tmxdata.tilewidth,
                                            y * self.tmxdata.tileheight))

    def make_map(self):
        temp_surface = pg.Surface((self.width, self.height))
        self.render(temp_surface)
        return temp_surface

class ViewPort:
    def __init__(self, width, height):
        self.viewport = pg.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, entity):
        return entity.rect.move(self.viewport.topleft)

    def apply_rect(self, rect):
        return rect.move(self.viewport.topleft)

    def update(self, target):
        x = int(DISPLAY_WIDTH / 2) - target.rect.centerx
        y = int(DISPLAY_HEIGHT / 2) - target.rect.centery

        # limit scrolling to map size
        x = min(0, x)  # left
        y = min(0, y)  # top
        x = max(-(self.width - DISPLAY_WIDTH), x)  # right
        y = max(-(self.height - DISPLAY_HEIGHT), y)  # bottom
        self.viewport = pg.Rect(x, y, self.width, self.height)


# create the game object
g = MyGame()
g.new()
while True:
    g.display_start_screen()
    g.start_level()
    g.run()
    g.display_game_over_screen()

    # Reset level and score to start new game:
    g.game_level = 1
    g.game_previous_level = 0
    g.player_score = 0
    g.player_lives = PLAYER_LIVES
