import pygame as pg
import others

import turret
import random as rd
import time

from abc import ABC, abstractmethod
from pygame import BLEND_RGB_ADD
import math

class Bot_Wave_Spawner:
    def __init__(self, jeu):
        self.jeu = jeu
        self.spawned = 0
        self.id = 0
        self.spawn_rate = 5
        self.bot_quantity = 6
        self.last_spawn = time.time()
        
    def update(self):
        if not self.jeu.wave_ended:
            if time.time() - self.last_spawn >= self.spawn_rate or self.spawned < self.bot_quantity//3:
                self.last_spawn = time.time()
                if self.spawned < self.bot_quantity:
                    #print(f"random x : {rd.randint(0, len(self.jeu.matrice_bot[0][0])-1)}\nrandom y : {rd.randint(0, len(self.jeu.matrice_bot[0])-1)}")
                    # Choisissez une coordonnée aléatoire dans la ligne
                    x, y = rd.randint(0,len(self.jeu.matrice_bot)-1), rd.randint(0,len(self.jeu.matrice_bot[0])-1)
                    x, y = self.jeu.matrice_bot[x][y]
                    #self.jeu.game_entities_list.append(Basic_Bot(self.jeu, y, x, self.id))
                    self.id += 1
                    self.spawned += 1
                    return True
                else:
                    self.jeu.wave_ended = True
                    self.spawned = 0
                    self.bot_quantity += 2
                    return 3
            else:
                return 2
        else:
            return False
    
    def manual_spawn(self, y, x, bot_type):
        
        if bot_type == "drone":
            self.jeu.game_entities_list.append(Drone_Bot(self.jeu, y, x, self.id))
        elif bot_type == "assault":
            self.jeu.game_entities_list.append(Assault_Bot(self.jeu, y, x, self.id))
        elif bot_type == "kamikaze":
            self.jeu.game_entities_list.append(Kamikaze_Bot(self.jeu, y, x, self.id))
        elif bot_type == "tank":
            self.jeu.game_entities_list.append(Tank_Bot(self.jeu, y, x, self.id))
        elif bot_type == "emp":
            self.jeu.game_entities_list.append(EMP_Bot(self.jeu, y, x, self.id))
        elif bot_type == "incinerator":
            self.jeu.game_entities_list.append(Incinerator_Bot(self.jeu, y, x, self.id))
        elif bot_type == "ender":
            self.jeu.game_entities_list.append(Ender_Bot(self.jeu, y, x, self.id))
        elif bot_type == "stealth":
            self.jeu.game_entities_list.append(StealthBlack_Bot(self.jeu, y, x, self.id))
        elif bot_type == "titan":
            self.jeu.game_entities_list.append(TITAN_Boss(self.jeu, y, x, self.id))
        else:
            self.jeu.game_entities_list.append(Basic_Bot(self.jeu, y, x, self.id))
        self.id += 1
        self.spawned += 1


class Bot(pg.sprite.Sprite):
    def __init__(self, jeu, x, y, id, vie, degats, vitesse, portee, cadence, name, path, nb_images = 8, coef = (66, 84), flip = True, fps = 90):
        self.jeu = jeu
        self.entity_list = jeu.game_entities_list
        self.name = name
        self.position = [x, y]
        self.path = path
        self.animation = others.Animation(self.jeu, nb_images, path, name, x, y, coef, flip, fps)
        self.image = self.animation.image
        self.position[0] = (self.position[0] - self.image.get_width()// 2)
        self.position[1] = (self.position[1] - self.image.get_height()// 2) 
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = self.position[0], self.position[1]
            
        self.vie = vie
        self.vie_max = vie
        self.point = round(((vie+degats+vitesse*1000+cadence)//4)/25)*25 # moyenne des stats arrondi a 25 près
        self.degats = degats
        self.vitesse = vitesse
        self.portee = portee
        self.cadence = cadence

        self.id = id
        self.last_shot = time.time()-self.cadence
        self.is_dead = False
        
        self.show_hitbox = False

    def __str__(self):
        return f"Bot id : {self.id}"
    
    def update(self):
        self.animation.update()
    
    def move(self):
        
        self.update()        
        
        for entity in self.entity_list:
            if isinstance(entity, turret.Turret) and self.rect.colliderect(entity.rect):
                return self.attack(entity)
        
        self.position[0] -= self.vitesse
        self.rect.x, self.rect.y = self.position[0], self.position[1]
        self.animation.rect.x, self.animation.rect.y = self.position[0], self.position[1]
        
        if self.position[0] <= self.jeu.largeur_interface + 30:
            if not isinstance(self, Drone_Bot):
                self.jeu.is_game_over = True
            self.is_dead = True
            
    def attack(self, cible):
        if time.time() - self.last_shot >= self.cadence:
            self.last_shot = time.time()
            cible.get_damage(self.degats)

    def get_damage(self, degats):
        self.vie -= degats
        if self.vie <= 0:
            self.is_dead = True
            return True
        else:
            return False
    
    def render(self, fenetre):
        
        self.animation.render(fenetre)
        
        # hitbox
        if self.show_hitbox:
            pg.draw.rect(fenetre, (0,255,0), (self.rect.x, self.rect.y, self.rect.width, self.rect.height), 1)
        
        if self.vie == self.vie_max:
            return
        
        # Calcul du pourcentage de vie
        pourcentage_vie = self.vie / self.vie_max  # Utilisez la vie maximale de la tourelle pour calculer le pourcentage de vie

        # Calcul de la largeur de la barre verte en fonction du pourcentage de vie
        largeur_barre_verte = round(self.rect.width * pourcentage_vie)

        # Calcul de la position de départ de la barre rouge
        position_barre_rouge = (self.rect.x + largeur_barre_verte, self.rect.y)

        # Dessin de la barre verte
        pg.draw.rect(fenetre, (0, 255, 0), (self.rect.x, self.rect.y, largeur_barre_verte, 5))  # Utilisez la largeur de la barre verte pour le troisième argument

        # Dessin de la barre rouge
        pg.draw.rect(fenetre, (255, 0, 0), (position_barre_rouge[0], position_barre_rouge[1], self.rect.width - largeur_barre_verte, 5))


class Basic_Bot(Bot):
    def __init__(self, jeu, x, y, id):
        super().__init__(jeu, x, y, id, vie = 100, degats=20, vitesse= 0.08, portee = 0, cadence = 2, path ="enemy/basic_bot_frames/frame_", name="Basic_Bot")

class Drone_Bot(Bot):
    def __init__(self, jeu, x, y, id):
        super().__init__(jeu, x, y, id, vie = 25, degats=10, vitesse= 0.3, portee = 0, cadence = 0.5, path ="enemy/drone_bot_frames/frame_", name="Drone_Bot", coef = (66*0.9, 84*0.8), flip= False, fps= 90)
    
    def move(self):
        self.update()
        self.image = self.animation.image
        
        self.position[0] -= self.vitesse
        self.animation.rect.x, self.animation.rect.y = self.position[0], self.position[1] - self.rect.height//2
        self.rect.x, self.rect.y = self.position[0], self.position[1]
        
        for entity in self.entity_list:
            if isinstance(entity, turret.Turret) and self.rect.colliderect(entity.rect):
                self.attack(entity)
        
        if self.position[0] <= self.jeu.largeur_interface + 30:
            if not isinstance(self, Drone_Bot):
                self.jeu.is_game_over = True
            self.is_dead = True

    def get_damage(self, degats):
        # drone est immunisé aux dégats
        pass

class Assault_Bot(Bot):
    def __init__(self, jeu, x, y, id):
        super().__init__(jeu, x, y, id, vie = 200, degats=25, vitesse= 0.05, portee = 300, cadence = 3, path ="enemy/assault_bot_frames/frame_", name="Assault_Bot")
        self.bullet_list = []
    
    def update(self):

        self.animation.update()
        self.shoot()
        for bullet in self.bullet_list:
            bullet.move()
            if bullet.is_dead:
                self.bullet_list.remove(bullet)
    
    def shoot(self):
        if time.time() - self.last_shot >= self.cadence:
            for entity in self.entity_list:
                if isinstance(entity, turret.Turret) and self.rect.colliderect((entity.rect.x + self.portee, entity.rect.y, entity.rect.width, entity.rect.height)):
                    self.last_shot = time.time()
                    bullet = Bullet(self.jeu, self.rect.x, self.rect.y + self.rect.height/2 , self.degats)
                    self.bullet_list.append(bullet)
                    self.entity_list.append(bullet)

class Bullet: 
   
    def __init__(self, jeu, x, y, degats, name="bullet"):
        self.jeu = jeu
        self.entity_list = jeu.game_entities_list
        self.position = [x, y]
        self.degats = degats
        self.vitesse = 1
        self.name = name
        self.is_dead = False
        # Définir la couleur en RGB
        self.color = (200, 20, 20)  
        # Définir le rectangle
        self.rect = pg.Rect(self.position[0], self.position[1], 24, 5)  # x, y, largeur, hauteur
    
    def move(self):
        for entity in self.entity_list:
            if isinstance(entity, turret.Turret):
                if self.is_colliding(entity):
                    self.is_dead = True
                    return entity.get_damage(self.degats)
        self.position[0] -= self.vitesse
        self.rect.x -= self.vitesse
        
        if self.position[0] < 0:
            self.is_dead = True
            
    def is_colliding(self, cible):
        if self.rect.colliderect(cible.rect):
            self.is_dead = True
            return True
        else: return False
    
    def render(self, fenetre):
        # Dessiner le rectangle sur la surface
        pg.draw.rect(self.jeu.fenetre, self.color, self.rect)

class Kamikaze_Bot(Bot):
    def __init__(self, jeu, x, y, id):
        super().__init__(jeu, x, y, id, vie = 50, degats=150, vitesse= 0.15, portee = 0, cadence = 0, path ="enemy/kamikaze_bot_frames/frame_", name="Kamikaze_Bot")
    
    def attack(self, cible):
        if self.rect.colliderect(cible.rect):
            self.rect = pg.Rect(self.rect.x - self.rect.width, self.rect.y - self.rect.height, 3 * self.rect.width, 3 * self.rect.height)
            for entity in self.entity_list:
                if isinstance(entity, turret.Turret) and self.rect.colliderect(entity.rect):
                    entity.get_damage(self.degats)
            self.is_dead = True
            self.entity_list.append(others.Animation(self.jeu, 17, "projectiles/explosion_frames/frame_", "explosion", self.rect.x, self.rect.y, (250, 250), flip=False, loop= False, fps=120))

class Tank_Bot(Bot):
    def __init__(self, jeu, x, y, id):
        super().__init__(jeu, x, y, id, vie = 400, degats=50, vitesse= 0.03, portee = 0, cadence = 6, coef= (66, 84), path ="enemy/tank_bot/tank_bot_frames/frame_", name="Tank_Bot", fps= 40)
        self.impact_list = []
    
    def update(self):

        self.animation.update()
        self.shoot()
        for impact in self.impact_list:
            impact.update()
            if impact.is_dead:
                self.impact_list.remove(impact)
                self.animation.get_images(8, "enemy/tank_bot/tank_bot_frames/frame_")
    
    def shoot(self):
        if time.time() - self.last_shot >= self.cadence:
            for entity in self.entity_list:
                if isinstance(entity, turret.Turret) and self.rect.colliderect((entity.rect.x + self.portee, entity.rect.y, entity.rect.width, entity.rect.height)):
                    entity.get_damage(self.degats)
                    self.last_shot = time.time()
                    impact = others.Animation(self.jeu, 16, "projectiles/impact_frames/frame_", "impact", self.rect.x - 2 * self.rect.width, self.rect.y - self.rect.height, (250, 250), flip=False, loop= False, fps=120)
                    self.animation.get_images(8, "enemy/tank_bot/tank_bot_attack_frames/frame_")
                    self.impact_list.append(impact)
                    self.entity_list.append(impact)

class EMP_Bot(Bot):
    def __init__(self, jeu, x, y, id):
        super().__init__(jeu, x, y, id, vie = 100, degats=25, vitesse= 0.12, portee = 0, cadence = 20, path ="enemy/emp_bot_frames/frame_", name="EMP_Bot")
        self.affected_turret = [] # liste des positions des effets

    def update(self):
        self.animation.update()
        self.shoot()

    
    def shoot(self):
        
        if time.time() - self.last_shot >= self.cadence:
        
            for entity in self.entity_list:
                
                if isinstance(entity, turret.Turret) and self.rect.colliderect((entity.rect.x + self.portee, entity.rect.y, entity.rect.width, entity.rect.height)):
                    self.entity_list.sort(key=lambda turret: turret.position[1])
                    for entity_2 in self.entity_list:
                        if isinstance(entity_2, turret.Turret) and entity_2.position[1] == entity.position[1] and entity_2.position[0]  <= self.position[0] - self.rect.width:
                            self.affected_turret.append(entity_2)
                            entity_2.get_damage(self.degats)
                            entity_2.is_disabled = True
                            entity_2.disabled_start = time.time()
                            entity_2.disabled_duration = (10 + entity_2.last_shot + entity_2.cadence - entity_2.disabled_start)
                            
                    self.last_shot = time.time()
                    self.entity_list.append(others.Animation(self.jeu, 24, "projectiles/emp_imulse_frames/frame_", "impulse", self.rect.x - 1000, self.rect.y - self.rect.height, (1000, 250), flip=True, loop= False, fps=80))
                    self.is_dead = True
                    
                    for turret_ in self.affected_turret:
                        self.entity_list.append(others.Animation(self.jeu, 11, "projectiles/turret_desactivation_frames/frame_", "turret_desactivation", turret_.position[0] - 10, turret_.position[1] -10 , (100, 120), flip=False, loop= False, fps=80, duration= turret_.disabled_duration, entity= turret_))
                    return

class Incinerator_Bot(Bot):
    def __init__(self, jeu, x, y, id):
        super().__init__(jeu, x, y, id, vie = 150, degats=0.4, vitesse= 0.08, portee = 210, cadence = 5, path ="enemy/incinerator_bot/unactive_incinerator_bot/frame_", name="Incinerator_Bot")
        self.fire_projectile = Fire_Projectile(jeu=self.jeu, tourelle = self, x=self.position[0]+self.rect.width, y=self.position[1]+self.rect.height//2, degats=self.degats)
        self.jeu.game_entities_list.append(self.fire_projectile)
    
    def update(self):
        #actualisation de la position du projectile
        self.fire_projectile.position = [self.position[0] , self.position[1]+self.rect.height//1.5]
        self.fire_projectile.rect.x, self.fire_projectile.rect.y = self.fire_projectile.position[0] - self.fire_projectile.rect.width + 5, self.fire_projectile.position[1] - self.fire_projectile.rect.height//2
        self.animation.update()
        self.shoot()
        self.fire_projectile.move()
                    
    def shoot(self):
        self.last_shot = time.time()
        shoot = False
        for entity in self.jeu.game_entities_list:
            if isinstance(entity, turret.Turret):
                if entity.position[0] >= self.position[0] - self.portee and self.rect.colliderect((self.position[0], entity.position[1], entity.rect.width, entity.rect.height)):
                    shoot = True
                    break
        if shoot:
            self.fire_projectile.state = "active"
            self.animation.get_images(8, "enemy/incinerator_bot/active_incinerator_bot/frame_")

            
        else:
            self.fire_projectile.state = "unactive"
            self.animation.get_images(8, "enemy/incinerator_bot/unactive_incinerator_bot/frame_")
            self.fire_projectile.particles = []
            
        return None

class Fire_Projectile:
    def __init__(self, jeu, tourelle, x, y, degats, vitesse = 1, name="fire_projectile"):
        self.jeu = jeu
        self.position = [x, y]
        self.degats = degats
        self.vitesse = vitesse
        self.name = name
        self.is_dead = False
        self.rect = pg.Rect(self.position[0], self.position[1]-10, 135, 24)
        self.dispersion = rd.randint(-1, 1) / 2
        # [loc, velocity, timer]
        self.particles = []
        self.last_particle = time.time()
        self.tourelle = tourelle
        self.cible_x = 0
        self.state = "unactive" or "active"
        
    def circle_surf(self, radius, color):
        surf = pg.Surface((radius * 2, radius * 2))
        pg.draw.circle(surf, color, (radius, radius), radius)
        surf.set_colorkey((0, 0, 0))
        return surf

    def render_debug(self, fenetre):
        pg.draw.rect(fenetre, (255, 0, 0), self.rect)
    
    def render(self, fenetre):
        if self.tourelle not in self.jeu.game_entities_list:
            self.is_dead = True
            self.jeu.game_entities_list.remove(self)
            return
        
        #self.render_debug(fenetre)
        
        if self.state == "active":
            self.particles.append([[self.position[0], self.position[1]], [2, rd.randint(0, 10) / 12 - 0.5], rd.randint(6, 9)])

            for particle in self.particles:
                particle[0][0] -= particle[1][0]
                particle[0][1] += particle[1][1]
                particle[2] -= 0.1
                pg.draw.circle(fenetre, (255, 255, 25), [int(particle[0][0]), int(particle[0][1])], int(particle[2]))

                radius = particle[2] * 2
                fenetre.blit(self.circle_surf(radius, (100, 20, 20)), (int(particle[0][0] - radius), int(particle[0][1] - radius)), special_flags=BLEND_RGB_ADD)

                if particle[2] <= 0 or particle[0][0] <= self.cible_x:
                    self.particles.remove(particle)
                   
    def move(self):
        if self.state == "active":
            for entity in self.jeu.game_entities_list:
                if isinstance(entity, turret.Turret):
                    if self.is_colliding(entity):
                        distance = ((entity.position[0] - self.position[0])**2 + (entity.position[1] - self.position[1])**2)**0.5
                        degat =  max(0, (self.tourelle.portee - distance) / self.tourelle.portee) * self.degats  # Les dégâts augmentent lorsque l'ennemi se rapproche
                        self.cible_x = entity.position[0]
                        return entity.get_damage(degat)

            if self.position[0] < 0:  # Check if the projectile has passed the left edge of the window
                self.is_dead = True   

    def is_colliding(self, cible):
        if self.rect.colliderect(cible.rect):
            return True
        else: return False

class Ender_Bot(Bot):
    def __init__(self, jeu, x, y, id):
        super().__init__(jeu, x, y, id, vie = 180, degats=80, vitesse= 0.1, portee = 10, cadence = 3, path ="enemy/ender_bot_frames/frame_", name="Ender_Bot", fps= 60)
        self.special_ability_cooldown = 5
        self.last_ability_use = time.time() - self.special_ability_cooldown  # The last time the special ability was used
        self.ability_state = "unactive"
            
    def update(self):
        self.animation.update()

    def special_ability(self):
        if self.ability_state == "unactive" and time.time() - self.last_ability_use >= self.special_ability_cooldown:
            self.ability_state = "active"
            #create the animation
            self.teleportation_animation_start = others.Animation(self.jeu, 16, "projectiles/teleportation_frames/frame_", "teleportation", self.rect.x-30, self.rect.y-20, (120, 160), flip=False, loop= False, fps=120)
            self.jeu.game_entities_list.append(self.teleportation_animation_start)
            self.teleportation_animation_end = None
        
    def move(self):
        
        if self.ability_state == "active":
            if self.teleportation_animation_start != None:
                if self.teleportation_animation_start.is_dead:

                    self.teleportation_animation_start = None
                    # Teleport the enemy to a new position
                    line = rd.randint(0,len(self.jeu.matrice_bot)-1)
                    while self.jeu.matrice_bot[line][0][0] - self.rect.height//2 == self.position[1]:
                        line = rd.randint(0,len(self.jeu.matrice_bot)-1)
                    self.position[1] = self.jeu.matrice_bot[line][0][0] - self.rect.height//2
                    self.rect.y = self.position[1]
                    self.animation.rect.y = self.position[1]
                    self.teleportation_animation_end = others.Animation(self.jeu, 16, "projectiles/teleportation_frames/frame_", "teleportation", self.rect.x-30, self.rect.y-20, (120, 160), flip=False, loop= False, fps=120, reverse=True)
                    self.jeu.game_entities_list.append(self.teleportation_animation_end)
            
            if self.teleportation_animation_end != None:
                if self.teleportation_animation_end.is_dead:
                    self.ability_state = "unactive"
                    self.last_ability_use = time.time()  # Update the last ability use time
                    self.teleportation_animation_end = None
        else:
            return super().move()
    
    def get_damage(self, degats):
        if self.vie - degats >= 0:
            self.special_ability()
        return super().get_damage(degats)

class StealthBlack_Bot(Bot):
    def __init__(self, jeu, x, y, id):
        super().__init__(jeu, x, y, id, vie = 200, degats=50, vitesse= 0.15, portee = 0, cadence = 5, path ="enemy/stealth_black_bot_frames/frame_", name="StealthBlack_Bot")
        self.animation.entity = self
        self.stealth = True
        self.stealth_cooldown = 5
        
    def update(self):
        self.animation.update()

    
    def attack(self, cible):
        self.stealth = False
        return super().attack(cible)

    def get_damage(self, degats):
        if self.stealth:
            return False
        return super().get_damage(degats)


class TITAN_Boss(Bot):
    def __init__(self, jeu, x, y, id):
        super().__init__(jeu, x, y, id, vie = 2500, degats=0, vitesse= 0.25, portee = 0, cadence = 5, path ="enemy/titan/titan_moving_frames/frame_", nb_images=4, coef = (160*5, 96*5), name="TITAN_Boss", fps= 45)

        self.state_list = ["moving", "standing" , "attack_1", "attack_2",
                           "shield", "death_beam", "damaged", "death"]
        
        self.cooldown_dict = {"attack_1" : 5, "attack_2" : 10, "shield" : 10, "death_beam" : 15}
        self.duration_dict = {"attack_1" : 5, "attack_2" : 10, "shield" : 10, "death_beam" : 15}
        
        self.last_shot = time.time()
        
        self.projectile_list = []
        
        self.next_state= "" # in [attack_1, attack_2, shield, death_beam]
        self.next_state_start = None
        
        self.state = self.state_list[3]
        self.state_start = time.time()
        
        self.phase = 0
        #self.position[0] += 300
        
        self.animation_position = [self.position[0], self.position[1]]
        self.animation = others.TITAN_Animation(jeu=jeu, path="enemy/titan/", name="TITAN_Boss", x = x, y = y, proportion=(160*5, 96*5), flip=True, fps= 40, entity=self)
        
        
        self.position = [self.position[0] + 225, self.position[1] + 190]
        self.rect = pg.Rect(self.position[0], self.position[1], 360, 300)
        


        self.show_hitbox = False
        self.show_life = False
    
    def update(self):
                
        self.animation.update()
        #ajouter un systeme de destruction des tourelles en contact et de l'avancer si n'y a plus de tourelles
        
        if self.collision_detection():
            self.state = self.state_list[0]
            self.moving_forward()
        
        elif self.phase == 0: self.phase_0()
                
        elif self.phase == 1: self.phase_1()
        
        self.state_action()
        
        #gere le changement de phase (pas testé)
        if self.animation.is_animation_done:
            if self.state == self.state_list[6]:
                self.animation.is_animation_done = False
                self.state = self.state_list[1]
                self.phase += 1
                self.animation.get_state()
    
    def phase_0(self):
        if self.state == self.state_list[0] and self.phase == 0:
            if self.position[0] <= 1080:
                self.phase = 1

    def phase_1(self):
        if self.state == self.state_list[0]:
            self.state = self.state_list[1]
            self.state_start = time.time()
            self.next_state= "attack_1"
            self.next_state_start = time.time() + self.cooldown_dict[self.next_state] + rd.randint(0, 5) #time.time() auquel la prochaine attaque sera lancée
            
        if self.state == self.state_list[1]:
            if time.time() >= self.next_state_start:
                self.state = self.next_state
                self.animation.get_state()
                self.next_state= ""
                self.next_state_start = None
                self.state_start = time.time()
        
        if self.state != "standing" and time.time() - self.state_start >= self.duration_dict[self.state] and self.next_state== "":
            self.state = self.state_list[1]
            self.next_state = "attack_1"
            self.next_state_start = time.time() + self.cooldown_dict[self.next_state] + rd.randint(0, 5)
            self.animation.get_state()
            self.state_start = time.time()

    def moving_forward(self):
        if self.state == self.state_list[0]:
            self.position[0] -= self.vitesse
            self.animation_position[0] -= self.vitesse
            
            self.rect.x, self.rect.y = self.position[0], self.position[1]
            self.animation.rect.x, self.animation.rect.y = self.animation_position
    
    def state_action(self):
        if self.state == "standing":
            pass
        elif self.state == "moving":
            self.moving_forward()
        elif self.state == "attack_1":
            self.attack_1()
        elif self.state == "attack_2":
            self.attack_2()
        
        if self.projectile_list:
            for projectile in self.projectile_list:
                projectile.move()
                if projectile.is_dead:
                    self.projectile_list.remove(projectile)
    
    def attack_1(self):
        if (time.time()-self.last_shot) >= 0.5:
            self.last_shot = time.time()
            target_list = []
            for entity in self.entity_list:
                if isinstance(entity, turret.Turret):
                    target_list.append(entity)
            
            if target_list:
                target = rd.choice(target_list)
                bullet = TITAN_Basic_Projectile(self.jeu, self.position[0] + self.rect.width//2, self.position[1] + self.rect.height//2, 25, 1, target, "titan_basic_projectile")
                self.entity_list.append(bullet)
                self.jeu.game_entities_list.append(bullet)
                self.projectile_list.append(bullet)
    
    def attack_2(self):
        if (time.time()-self.last_shot) >= 1.5:
            self.last_shot = time.time()
            target_list = []
            for entity in self.entity_list:
                if isinstance(entity, turret.Turret):
                    target_list.append(entity)
            
            if target_list:
                target = rd.choice(target_list)
                bullet = TITAN_Missile(self.jeu, self.position[0] + self.rect.width//2, self.position[1] + self.rect.height//2, 100, 1, target, "titan_basic_projectile")
                self.entity_list.append(bullet)
                self.jeu.game_entities_list.append(bullet)
                self.projectile_list.append(bullet)
                
    
    #update methode call at each loop in the main game loop
    def move(self):
        
        self.update()
       
        
        if self.position[0] <= self.jeu.largeur_interface + 30:
            self.jeu.is_game_over = True
            self.is_dead = True


    def collision_detection(self):
        cond = True
        for entity in self.entity_list:
            if isinstance(entity, turret.Turret):
                if self.is_colliding(entity):
                    self.colliding_damage(entity)
                cond = False
        return cond
                
    def is_colliding(self, cible):
        if self.rect.colliderect(cible.rect):
            return True
        else: return False
    
    def colliding_damage(self, cible):
        cible.vie = 0
        cible.is_dead = True

    def render(self, fenetre):
        
        self.animation.render(fenetre)
        
        # hitbox
        if self.show_hitbox:
            pg.draw.rect(fenetre, (0,255,0), self.rect, 1)

        if self.vie == self.vie_max:
            return
        
        if not self.show_life:
            return
        # Calcul du pourcentage de vie
        pourcentage_vie = self.vie / self.vie_max  # Utilisez la vie maximale de la tourelle pour calculer le pourcentage de vie

        # Calcul de la largeur de la barre verte en fonction du pourcentage de vie
        largeur_barre_verte = round(self.rect.width * pourcentage_vie)

        # Calcul de la position de départ de la barre rouge
        position_barre_rouge = (self.rect.x + largeur_barre_verte, self.rect.y)

        # Dessin de la barre verte
        pg.draw.rect(fenetre, (0, 255, 0), (self.rect.x, self.rect.y, largeur_barre_verte, 5))  # Utilisez la largeur de la barre verte pour le troisième argument

        # Dessin de la barre rouge
        pg.draw.rect(fenetre, (255, 0, 0), (position_barre_rouge[0], position_barre_rouge[1], self.rect.width - largeur_barre_verte, 5))


class Projectile:
    def __init__(self, jeu, x, y, degats, vitesse, name):
        self.jeu = jeu
        self.position = [x, y]
        self.degats = degats
        self.vitesse = vitesse
        self.name = name
        self.is_dead = False

    def move(self):
        if self.is_colliding(self.cible):
            self.damage(self.cible)
        else:
            dx = self.cible.position[0] + self.cible.rect.width/2 - self.position[0]
            dy = self.cible.position[1] + self.cible.rect.height/2 - self.position[1]
            
            distance = (dx**2 + dy**2)**0.5  # Calculate the distance between the projectile and the target
            
            # Normalize the direction vector
            dx /= distance
            dy /= distance
            
            # Multiply the direction by the speed to get the velocity
            vx = self.vitesse * dx
            vy = self.vitesse * dy
            
            self.vx, self.vy = vx, vy
            
            self.position[0] += vx
            self.position[1] += vy
            self.rect.x, self.rect.y = self.position[0], self.position[1]
            
            if self.position[0] > self.jeu.taille_fenetre[0] or self.position[0] < 0:
                self.is_dead = True
            
    def is_colliding(self, cible):
        if self.rect.colliderect(cible.rect):
            return True
        else: return False

    def damage(self, cible):
        cible.get_damage(self.degats)
        self.is_dead = True

    def render(self, fenetre):
        angle = math.degrees(math.atan2(self.vy, self.vx)) 
        fenetre.blit(pg.transform.rotate(self.image, -angle), (self.position[0], self.position[1]))
        #afficher la hitbox
        pg.draw.rect(fenetre, (255,0,0), (self.rect.x, self.rect.y, self.rect.width, self.rect.height), 1)

class TITAN_Basic_Projectile(Projectile):
    
    def __init__(self, jeu, x, y, degats, vitesse, cible, name):
        super().__init__(jeu, x, y, degats, vitesse, name)
        self.image = pg.image.load("assets/images/projectiles/titan_projectile/basic_projectile.png").convert_alpha()
        self.image = pg.transform.scale(self.image, (8*5, 1*5))
        self.rect = self.image.get_rect()
        self.cible = cible
        self.vx, self.vy = 0, 0
        
class TITAN_Missile(Projectile):
    
    def __init__(self, jeu, x, y, degats, vitesse, cible, name):
        super().__init__(jeu, x, y, degats, vitesse, name)
        self.image = pg.image.load("assets/images/projectiles/titan_projectile/missile.png").convert_alpha()
        self.image = pg.transform.scale(self.image, ((66, 68)))
        self.rect = self.image.get_rect()
        self.cible = cible
        self.vx, self.vy = 0, 0
    
    def damage(self, cible):
        self.rect = pg.Rect(self.rect.x - self.rect.width, self.rect.y - self.rect.height, 3 * self.rect.width, 3 * self.rect.height)
        for entity in self.jeu.game_entities_list:
            if isinstance(entity, turret.Turret) and self.rect.colliderect(entity.rect):
                entity.get_damage(self.degats)
        self.is_dead = True
        #self.jeu.game_entities_list.append(others.Animation(self.jeu, 17, "projectiles/explosion_frames/frame_", "explosion", self.rect.x, self.rect.y, (250, 250), flip=False, loop= False, fps=120))


if __name__ == "__main__":
    import game
    jeu = game.Game()
    jeu.run()