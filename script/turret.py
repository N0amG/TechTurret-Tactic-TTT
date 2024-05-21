import pygame as pg
import time
import math
import enemy
import others
from random import randint, random
from abc import ABC, abstractmethod
from pygame import BLEND_RGB_ADD


class Turret_selection:
    def __new__(cls, jeu, x, y, name):
        file_manager = others.FileManager("settings/settings.json")
        file_manager.set_setting("turrets_built", file_manager.get_setting("turrets_built") + 1)
        
        if name == "Basic Turret":
            return Basic_Turret(jeu, x, y)
        
        elif name == "Laser Turret":
            return Laser_Turret(jeu, x, y)
        
        elif name == "BlackHole Turret":
            return BlackHole_Turret(jeu, x, y)
        
        elif name == "Plasma Turret":
            return Plasma_Turret(jeu, x, y)
        
        elif name == "Shield":
            return Shield(jeu, x, y)
        
        elif name == "Omni Turret":
            return Omni_Turret(jeu, x, y)
        
        elif name == "AntiMatter Turret":
            return
            #return AntiMatter_Turret(jeu, x, y)
        
        else:
            return None

class Turret:
    def __init__(self, jeu, x, y, vie, degats, portee, cadence, prix, name):
        # Ajoutez ici les attributs spécifiques à la classe Turret
        self.jeu = jeu
        self.entity_list = jeu.game_entities_list
        self.position = [x, y]
        self.vie = vie
        self.vie_max = vie
        self.degats = degats
        self.portee = portee
        self.cadence = cadence
        self.prix = prix
        self.name = name
        self.last_shot = time.time()-self.cadence
        
        self.is_disabled : bool = False
        self.disabled_duration : int = 0
        self.disabled_start = 0
        
        self.summon_time = time.time()
        self.is_dead = False

        
    def __str__(self):
        return f"{self.name} : {self.vie} vie"
    
    def get_damage(self, degats):
        self.vie -= degats
        if self.vie <= 0:
            self.is_dead = True
            return True
        else:
            return False

    @abstractmethod
    def shoot(self):
        pass
        
    def render(self, fenetre):
        fenetre.blit(self.image, self.position)

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
        
class Projectile:
    def __init__(self, jeu, x, y, degats, vitesse, name):
        self.jeu = jeu
        self.position = [x, y]
        self.degats = degats
        self.vitesse = vitesse
        self.name = name
        self.is_dead = False

    def move(self):
        for bot in self.jeu.game_entities_list:
            if isinstance(bot, enemy.Bot):
                if self.is_colliding(bot):
                    if isinstance(bot, enemy.Drone_Bot):
                        break
                    else:
                        return bot.get_damage(self.degats)
        self.position[0] += self.vitesse
        self.rect.x += self.vitesse
        if self.position[0] > self.jeu.taille_fenetre[0]:
            self.is_dead = True
            
    def is_colliding(self, cible):
        if self.rect.colliderect(cible.rect):
            if isinstance(cible, enemy.Drone_Bot):
                if isinstance(self, BlackHole_Projectile):
                    return True
                return False
            if isinstance(cible, enemy.StealthBlack_Bot):
                if cible.stealth == True:
                    return False
            return True
        else: return False

    def render(self, fenetre):
        # Dessiner le rectangle sur la surface
        pg.draw.rect(self.jeu.fenetre, self.color, self.rect)
        if isinstance(self, Laser_Projectile):
            pg.draw.rect(self.jeu.fenetre, self.color2, self.rect2)
        
        #dessiner la hitbox pour le debug
        #pg.draw.rect(fenetre, (255,0,0), (self.rect.x, self.rect.y, self.rect.width, self.rect.height), 1)



class Basic_Turret(Turret):
    
    def __init__(self, jeu, x, y):
        super().__init__(jeu, x, y, vie = 200, degats =20, portee=750, cadence=5, prix=100, name = "Tourelle")
        self.image = pg.image.load("assets/images/turrets/basic_turret.png").convert_alpha()
        self.image = pg.transform.scale(self.image, (75, 100))
        self.position[0] = (self.position[0] - self.image.get_width()// 2) 
        self.position[1] = (self.position[1] - self.image.get_height()// 2) 
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = self.position[0], self.position[1]
        
    def shoot(self):
        if not self.is_disabled:
            shoot = False
            for entity in self.jeu.game_entities_list:
                if isinstance(entity, enemy.Bot):
                    if not isinstance(entity, enemy.Drone_Bot):
                        if isinstance(entity, enemy.StealthBlack_Bot):
                            if entity.stealth == True:
                                continue
                        if isinstance(entity, enemy.TITAN_Boss):
                            if entity.state == "death":
                                continue
                        if entity.position[0] <= self.position[0] + self.portee and self.rect.colliderect((self.position[0], entity.position[1], entity.rect.width, entity.rect.height)):
                            shoot = True
                            break
            if shoot:
                if time.time() - self.last_shot >= self.cadence:
                    self.last_shot = time.time()
                    return Basic_Projectile(jeu=self.jeu, x=self.position[0]+self.rect.width//2, y=self.position[1]+self.rect.height//2, degats=self.degats)
            return None
        else:
            if (time.time() - self.disabled_start)  >= self.disabled_duration:
                self.is_disabled = False
                self.disabled_duration = 0
        
class Basic_Projectile(Projectile): 
    def __init__(self, jeu, x, y, degats):
        super().__init__(jeu, x, y, degats, vitesse = 10, name="basic_projectile")
        # Définir la couleur en RGB
        self.color = (100, 100, 100)  
        # Définir le rectangle
        self.rect = pg.Rect(self.position[0], self.position[1], 24, 12)  # x, y, largeur, hauteur

    def is_colliding(self, cible):
        if self.rect.colliderect(cible.rect):
            if not isinstance(cible, enemy.Drone_Bot):
                if isinstance(cible, enemy.StealthBlack_Bot):
                    if cible.stealth == True:
                        return False
                self.is_dead = True
                return True
        else: return False


class Laser_Turret(Turret):
    
    def __init__(self, jeu, x, y):
        super().__init__(jeu, x, y, vie = 125, degats= 0.1, portee=750, cadence=4, prix=200, name = "Tourelle_Laser")
        self.image = pg.image.load("assets/images/turrets/laser_turret.png").convert_alpha()
        self.image = pg.transform.scale(self.image, (75, 100))
        self.position[0] = (self.position[0] - self.image.get_width()// 2) 
        self.position[1] = (self.position[1] - self.image.get_height()// 2) 
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = self.position[0], self.position[1]
    
    def shoot(self):
        if not self.is_disabled:
            shoot = False
            for entity in self.jeu.game_entities_list:
                if isinstance(entity, enemy.Bot):
                    if not isinstance(entity, enemy.Drone_Bot):
                        if isinstance(entity, enemy.TITAN_Boss):
                            if entity.state == "death":
                                continue
                        if isinstance(entity, enemy.StealthBlack_Bot):
                            if entity.stealth == True:
                                continue
                        if entity.position[0] <= self.position[0] + self.portee and self.rect.colliderect((self.position[0], entity.position[1], entity.rect.width, entity.rect.height)):
                            shoot = True
                            break
            if shoot:
                if time.time() - self.last_shot >= self.cadence:
                    self.last_shot = time.time()
                    return Laser_Projectile(jeu=self.jeu, x=self.position[0]+self.rect.width, y=self.position[1]+self.rect.height//2 -5, degats=self.degats)
            return None
        else:
            if (time.time() - self.disabled_start)  >= self.disabled_duration:
                self.is_disabled = False
                self.disabled_duration = 0
     
class Laser_Projectile(Projectile): 
   
    def __init__(self, jeu, x, y, degats):
        super().__init__(jeu, x, y, degats, vitesse = 5, name="basic_projectile")
        # Définir la couleur en RGB
        self.color = (255, 0, 0)  
        # Définir le rectangle
        self.rect = pg.Rect(self.position[0], self.position[1]+2, 750, 16)  # x, y, largeur, hauteur
        self.duree = 2
        self.last_time = time.time()
        self.damage = False
        self.height_substraction = 0
        self.color2 = (255, 150, 0)
        self.rect2 = pg.Rect(self.position[0], self.position[1]+6, 750, 8)  # x, y, largeur, hauteur
        
    def move(self):
        if self.damage == False:
            for bot in self.jeu.game_entities_list:
                if isinstance(bot, enemy.Bot):
                    if self.is_colliding(bot):
                        bot.get_damage(self.degats)
                        #self.damage = True
        self.height_substraction += 1 *self.vitesse
        
        if self.height_substraction >= 60:
            self.height_substraction = 0
            self.rect.height -= 1
            self.rect2.height -= 1
            self.rect.y = self.position[1] + 2
            self.rect2.y = self.position[1] + 6
            
        if time.time() - self.last_time >= self.duree:
            self.last_time = time.time()
            self.is_dead = True


class Plasma_Turret(Turret):
    
    def __init__(self, jeu, x, y):
        super().__init__(jeu, x, y, vie = 100, degats= 0.75, portee=210, cadence=0, prix=350, name = "Tourelle_Plasma")
        self.image = pg.image.load("assets/images/turrets/plasma_turret.png").convert_alpha()
        self.image = pg.transform.scale(self.image, (75, 100))
        self.position[0] = (self.position[0] - self.image.get_width()// 2) 
        self.position[1] = (self.position[1] - self.image.get_height()// 2) 
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = self.position[0], self.position[1]
        self.plasma_projectile = Plasma_Projectile(jeu=self.jeu, tourelle = self, x=self.position[0]+self.rect.width+2, y=self.position[1]+self.rect.height//2, degats=self.degats)
        self.jeu.game_entities_list.append(self.plasma_projectile)
    
    def shoot(self):
        self.last_shot = time.time()
        if not self.is_disabled:
            shoot = False
            for entity in self.jeu.game_entities_list:
                if isinstance(entity, enemy.Bot):
                    if not isinstance(entity, enemy.Drone_Bot):
                        if isinstance(entity, enemy.TITAN_Boss):
                            if entity.state == "death":
                                continue
                        if isinstance(entity, enemy.StealthBlack_Bot):
                            if entity.stealth == True:
                                continue
                        if entity.position[0] <= self.position[0] + self.portee and self.rect.colliderect((self.position[0], entity.position[1], entity.rect.width, entity.rect.height)):
                            shoot = True
                            break
            if shoot:
                self.plasma_projectile.state = "active"
                
            else:
                self.plasma_projectile.state = "unactive"
                self.plasma_projectile.particles = []
                
            return None
        else:
            self.plasma_projectile.state = "unactive"
            if (time.time() - self.disabled_start)  >= self.disabled_duration:
                self.is_disabled = False
                self.disabled_duration = 0
    
class Plasma_Projectile(Projectile):
    def __init__(self, jeu, tourelle, x, y, degats):
        super().__init__(jeu, x, y, degats, vitesse = 2, name="plasma_projectile")
        self.rect = pg.Rect(self.position[0], self.position[1]-10, 135, 24)
        self.dispersion = randint(-1, 1) / 2
        # [loc, velocity, timer]
        self.particles = []
        self.last_particle = time.time()
        self.tourelle = tourelle
        self.cible_x = 0
        self.cible_width = 0
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
        if not self.jeu.paused:
            if self.state == "active":
                self.particles.append([[self.position[0], self.position[1]], [2, randint(0, 10) / 12 - 0.5], randint(6, 9)])

                for particle in self.particles:
                    particle[0][0] += particle[1][0] * self.vitesse
                    particle[0][1] += particle[1][1] * self.vitesse
                    particle[2] -= 0.1
                    pg.draw.circle(fenetre, (255, 255, 255), [int(particle[0][0]), int(particle[0][1])], int(particle[2]))

                    radius = particle[2] * 2
                    fenetre.blit(self.circle_surf(radius, (20, 20, 60)), (int(particle[0][0] - radius), int(particle[0][1] - radius)), special_flags=BLEND_RGB_ADD)

                    if particle[2] <= 0 or particle[0][0] >= self.cible_x + self.cible_width:
                        self.particles.remove(particle)
        else:
            for particle in self.particles:
                pg.draw.circle(fenetre, (255, 255, 255), [int(particle[0][0]), int(particle[0][1])], int(particle[2]))
                radius = particle[2] * 2
                fenetre.blit(self.circle_surf(radius, (20, 20, 60)), (int(particle[0][0] - radius), int(particle[0][1] - radius)), special_flags=BLEND_RGB_ADD)

    def move(self):
        if self.state == "active":
            distance_min = self.rect.width
            cible = None
            for entity in self.jeu.game_entities_list:

                if isinstance(entity, enemy.Bot):
                    if self.is_colliding(entity):
                        if cible == None:
                            cible = entity
                            distance_min = ((entity.position[0] - self.position[0])**2 + (entity.position[1] - self.position[1])**2)**0.5

                        distance = ((entity.position[0] - self.position[0])**2 + (entity.position[1] - self.position[1])**2)**0.5
                        
                        if distance < distance_min:
                            distance_min = distance
                            cible = entity
            if cible != None:
                degat =  max(0, (self.tourelle.portee - distance_min) / self.tourelle.portee) * self.degats  # Les dégâts augmentent lorsque l'ennemi se rapproche
                self.cible_x = cible.position[0]
                self.cible_width = cible.rect.width/2
                if self.jeu.game_entities_list.index(self) < self.jeu.game_entities_list.index(cible):
                    self.jeu.game_entities_list.remove(self)
                    self.jeu.game_entities_list.append(self)
            
                return cible.get_damage(degat)

            if self.position[0] > self.jeu.taille_fenetre[0]:
                self.is_dead = True        

                
class BlackHole_Turret(Turret):
    
    def __init__(self, jeu, x, y):
        super().__init__(jeu, x, y, vie = 300, degats= 0.2, portee=1000, cadence=15, prix=300, name = "Tourelle_Blackhole")
        self.image = pg.image.load("assets/images/turrets/blackHole_turret.png").convert_alpha()
        self.image = pg.transform.scale(self.image, (75, 100))
        self.position[0] = (self.position[0] - self.image.get_width()// 2) 
        self.position[1] = (self.position[1] - self.image.get_height()// 2) 
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = self.position[0], self.position[1]
        
        
    def shoot(self):
        if not self.is_disabled:
            shoot = False
            for entity in self.jeu.game_entities_list:
                if isinstance(entity, enemy.Bot):
                    if isinstance(entity, enemy.TITAN_Boss):
                        if entity.state == "death":
                            continue
                    if isinstance(entity, enemy.StealthBlack_Bot):
                        if entity.stealth == True:
                            continue
                    if entity.position[0] <= self.position[0] + self.portee and self.rect.colliderect((self.position[0], entity.position[1], entity.rect.width, entity.rect.height)):
                        shoot = True
                        break
            if shoot:
                if time.time() - self.last_shot >= self.cadence:
                    self.last_shot = time.time()
                    return BlackHole_Projectile(jeu=self.jeu, blackhole_turret=self, x=self.position[0]+self.rect.width, y=self.position[1]+self.rect.height//2 -5, degats=self.degats)
            return None
        else:
            if (time.time() - self.disabled_start)  >= self.disabled_duration:
                self.is_disabled = False
                self.disabled_duration = 0

class BlackHole_Projectile(Projectile):
        
        def __init__(self, jeu, blackhole_turret, x, y, degats):
            super().__init__(jeu, x, y, degats, vitesse = 10, name="blackHole_projectile")
            self.color = (0, 0, 0)
            self.blackhole_turret = blackhole_turret
            self.rect = pg.Rect(self.position[0], self.position[1], 24, 12)  # x, y, largeur, hauteur
            self.last_time = time.time()
            self.range = 350
            self.is_dead = False
            self.duree = 5
            self.state = "projectile" # or "blackhole"
            self.image = pg.transform.scale(pg.image.load('assets/images/projectiles/blackhole_projectile.png'), (60, 60)).convert_alpha()
            self.attraction_force = 0.75
            self.kill_margin = 125
            self.target = self.find_shoot_spot()
            
        def find_shoot_spot(self):
            self.bot_list = []
            for entity in self.jeu.game_entities_list:
                if isinstance(entity, enemy.Bot) or isinstance(entity, enemy.TITAN_Boss):                
                    if self.rect.colliderect((self.position[0], entity.position[1], entity.rect.width, entity.rect.height)):
                        self.bot_list.append(entity)
            
            if len(self.bot_list) > 0:
                self.bot_list.sort(key=lambda bot: bot.position[0]+bot.rect.width)
                self.target_width = self.bot_list[-1].rect.width
                
                # pour résoudre de le problème du dernier bot qui est trop proche du bord de l'écran
                while self.bot_list and self.bot_list[-1].position[0] + self.bot_list[-1].rect.width > self.jeu.taille_fenetre[0] - self.kill_margin:
                    self.bot_list.pop()
                
                if len(self.bot_list) == 0:
                    self.is_dead = True
                    self.blackhole_turret.last_shot -= self.last_time
                    return None
                
                self.cible = self.bot_list[-1]
                return self.bot_list[-1].position
                
        def move(self):
            
            if self.state == "projectile":
                if self.target is not None:
                    if self.position[0] < self.target[0] + self.target_width:
                        self.position[0] += self.vitesse
                        self.rect.x += self.vitesse
                        self.rect.y = self.position[1]    
                    else:
                        self.state = "blackhole"
                        self.rect = self.image.get_rect()
                        self.rect.x, self.rect.y = self.position[0], self.position[1]-30
                        self.position[1] = self.rect.y
                        self.last_time = time.time()
                
                if self.position[0] > self.jeu.taille_fenetre[0]-self.kill_margin:
                    self.is_dead = True
            
            
            else:
                    
                diff = list(filter(lambda elt: isinstance(elt, enemy.Bot),filter(lambda elt: elt not in self.bot_list, self.jeu.game_entities_list)))
                if len(diff):
                    for bot in diff:
                        if self.rect.colliderect((self.position[0], bot.position[1], bot.rect.width, bot.rect.height)):
                            self.bot_list.append(bot)

                for bot in self.bot_list:
                    
                    if bot.position[0] <= self.position[0] + self.range and bot.position[0] >= self.position[0] - self.range - self.target_width:
                        if bot.position[0] > self.position[0]:
                            bot.position[0] -= self.attraction_force
                            if isinstance(bot, enemy.TITAN_Boss):
                                bot.animation_position[0] -= self.attraction_force
                        else:
                            bot.position[0] += self.attraction_force
                            if isinstance(bot, enemy.TITAN_Boss):
                                bot.animation_position[0] += self.attraction_force
                        
                        bot.rect.x = bot.position[0]
                        if not isinstance(bot, enemy.TITAN_Boss):
                            bot.animation.rect.x = bot.position[0]
                        if isinstance(bot, enemy.Ender_Bot):
                            bot.blackhole_counter = True
                            
                    if self.is_colliding(bot):
                        bot.get_damage(self.degats, source="blackhole")
                
                if time.time() - self.last_time >= self.duree:
                    self.last_time = time.time()
                    self.is_dead = True
                    for bot in self.bot_list:
                        if isinstance(bot, enemy.Ender_Bot):
                            bot.blackhole_counter = False
                        
        def render(self, fenetre):
            
            # Dessiner la hitbox 
            #pg.draw.rect(fenetre, (255, 0, 0), self.rect)
            
            # Dessiner l'image sur la fenêtre         
            if self.state == "blackhole":
                fenetre.blit(self.image, (self.position[0], self.position[1]))
            else:
                if not self.is_dead:
                    pg.draw.rect(self.jeu.fenetre, self.color, self.rect)


class Shield(Turret):
    
    def __init__(self, jeu, x, y):
        super().__init__(jeu, x, y, vie = 500, degats= 0, portee=0, cadence=0, prix=250, name = "Bouclier")
        self.image = pg.image.load("assets/images/turrets/shield/shield.png").convert_alpha()
        self.image = pg.transform.scale(self.image, (75, 100))
        self.position[0] = (self.position[0] - self.image.get_width()// 2) 
        self.position[1] = (self.position[1] - self.image.get_height()// 2) 
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = self.position[0], self.position[1]
    
    def shoot(self):
        self.last_shot = time.time()
        if self.is_disabled:
            self.image = pg.image.load("assets/images/turrets/shield/disabled_shield.png").convert_alpha()
            self.image = pg.transform.scale(self.image, (75, 100))
            self.rect.x, self.rect.y = (-100, -100)
            if (time.time() - self.disabled_start)  >= self.disabled_duration:
                self.is_disabled = False
                self.disabled_duration = 0
                self.image = pg.image.load("assets/images/turrets/shield/shield.png").convert_alpha()
                self.image = pg.transform.scale(self.image, (75, 100))
                self.rect.x, self.rect.y = self.position[0], self.position[1]
                
                
class Omni_Turret(Turret):
        def __init__(self, jeu, x, y):
            super().__init__(jeu, x, y, vie = 200, degats= 5, portee="inf", cadence=1, prix=450, name = "Tourelle_Omni")
            self.image = pg.image.load("assets/images/turrets/omni_turret.png").convert_alpha()
            self.image = pg.transform.scale(self.image, (75, 100))
            self.position[0] = (self.position[0] - self.image.get_width()// 2) 
            self.position[1] = (self.position[1] - self.image.get_height()// 2) 
            self.rect = self.image.get_rect()
            self.rect.x, self.rect.y = self.position[0], self.position[1]
            
        def shoot(self):
            if not self.is_disabled:
                shoot = False
                
                self.entity_list = self.jeu.game_entities_list[:]
                self.entity_list.sort(key=lambda bot: bot.position[0])
                for entity in self.entity_list:
                    if isinstance(entity, enemy.Bot):
                        if not isinstance(entity, enemy.Drone_Bot):
                            if isinstance(entity, enemy.TITAN_Boss):
                                if entity.state == "death":
                                    continue
                            if isinstance(entity, enemy.StealthBlack_Bot):
                                if entity.stealth == True:
                                    continue
                            shoot = True
                            cible = entity
                            break
                if shoot:
                    if time.time() - self.last_shot >= self.cadence:
                        self.last_shot = time.time()
                        return Omni_Projectile(jeu=self.jeu, x=self.position[0]+self.rect.width//2, y=self.position[1]+self.rect.height//2 , degats=self.degats, cible = cible)
                return None
            else:
                if (time.time() - self.disabled_start)  >= self.disabled_duration:
                    self.is_disabled = False
                    self.disabled_duration = 0
        
class Omni_Projectile(Projectile):
    
    def __init__(self, jeu, x, y, degats, cible):
        super().__init__(jeu, x, y, degats, vitesse = 25, name="omni_projectile")
        self.image = pg.image.load("assets/images/projectiles/omni_projectile.png").convert_alpha()
        self.image = pg.transform.scale(self.image, (20*3, 5*3))
        self.rect = self.image.get_rect()
        self.cible = cible
        self.vx, self.vy = 0, 0

        
    def move(self):
        if self.is_colliding(self.cible):
            self.cible.get_damage(self.degats)
            self.is_dead = True
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

    def render(self, fenetre):
        angle = math.degrees(math.atan2(self.vy, self.vx)) 
        fenetre.blit(pg.transform.rotate(self.image, -angle), (self.position[0], self.position[1]))
        #afficher la hitbox
        #pg.draw.rect(fenetre, (255,0,0), (self.rect.x, self.rect.y, self.rect.width, self.rect.height), 1)





'''

Developpement de la tourelle antimatière en pause, car le projectile ne fonctionne pas correctement. 

class AntiMatter_Turret(Turret):
        
    def __init__(self, jeu, x, y):
        super().__init__(jeu, x, y, vie = 200, degats= 50, portee=1000, cadence=10, prix=500, name = "Tourelle_AntiMatter")
        self.image = pg.image.load("assets/images/turrets/antimatter_turret.png").convert_alpha()
        self.image = pg.transform.scale(self.image, (75, 100))
        self.position[0] = (self.position[0] - self.image.get_width()// 2) 
        self.position[1] = (self.position[1] - self.image.get_height()// 2) 
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = self.position[0], self.position[1]
        self.cible = None
    
    def shoot(self):
        shoot = False
        for entity in reversed(self.jeu.game_entities_list):
            if isinstance(entity, enemy.Bot):
                if entity.position[0] <= self.position[0] + self.portee and self.rect.colliderect((self.position[0], entity.position[1], entity.rect.width, entity.rect.height)):
                    shoot = True
                    self.cible = entity
                    break
        if shoot:
            if time.time() - self.last_shot >= self.cadence:
                self.last_shot = time.time()
                return AntiMatter_Projectile(jeu=self.jeu,cible = entity, x=self.position[0]+self.rect.width, y=self.position[1]+self.rect.height//2 -5, tourelle = self, degats=self.degats)
        return None

class AntiMatter_Projectile(Projectile):
            
    def __init__(self, jeu, cible, x, y, tourelle, degats):
        super().__init__(jeu, x, y, degats, vitesse = 1, name="antimatter_projectile")
        self.color = (0, 0, 0)  
        self.range = 500            
        self.is_dead = False
        self.duree = 5
        self.state = "projectile" # or "explosion"
        self.image = pg.transform.scale(pg.image.load('assets/images/projectiles/antimatter_projectile.png'), (60, 60)).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.y = y-20
        self.tourelle = tourelle
        self.target = cible.position[:]
        self.liste_points = []
    
    def f(self, x):
        a = self.target[0]
        return -(x - self.tourelle.position[0]) * (x - a)
    
    def trajectory(self, x):
        # b = self.tourelle.position[1] - self.rect.height - 100
        b = 200
        a = self.target[0]
        
        return (b / self.f(a/2)) * self.f(x)
    
    def derive(self, x):
        a = self.target[0]
        return -2*x + a + self.tourelle.position[0]
    
    def derive_trajectory(self, x):
        a = self.target[0]
        b = x / 2
        return -b/2

    def move(self):
        if self.state == "projectile":
            if self.position[0] < self.target[0]:
                self.position[0] += self.vitesse
                self.position[1] = self.f(self.position[0])/600
                # self.position[1] = - self.jeu.taille_fenetre[1] + self.trajectory(self.position[0])
                self.liste_points.append([
                    self.position[0],
                    self.position[1]
                ])
                self.rect.x = self.position[0]
            else:
                self.state = "explosion"
                self.last_time = time.time()
            
            if self.position[0] > self.jeu.taille_fenetre[0]:
                self.is_dead = True
        

    
    def render(self, fenetre):
        angle = self.derive_trajectory(self.position[0]) - 110
        #print("angle", angle)
        rotated_image = pg.transform.rotate(self.image, angle)
        fenetre.blit(rotated_image, (self.position[0], self.position[1]))
        
        for point in self.liste_points:
            pg.draw.circle(fenetre, (255, 0, 0), point, 2)
            
        #afficher la hitbox
        pg.draw.rect(fenetre, (255,0,0), (self.rect.x, self.rect.y, self.rect.width, self.rect.height), 1)

'''

if __name__ == "__main__":
    import game
    jeu = game.Game()
    jeu.run()