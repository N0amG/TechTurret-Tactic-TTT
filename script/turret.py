import pygame as pg
import time
import math
import enemy
from random import randint, random
from abc import ABC, abstractmethod
from pygame import BLEND_RGB_ADD

class Turret_selection:
    def __new__(cls, jeu, x, y, name):
        if name == "Turret":
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
            return AntiMatter_Turret(jeu, x, y)
        
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
                if self.is_colliding(bot.rect):
                    return bot.get_damage(self.degats)
        self.position[0] += self.vitesse
        self.rect.x += self.vitesse
        if self.position[0] > self.jeu.taille_fenetre[0]:
            self.is_dead = True
            
    def is_colliding(self, cible : pg.rect):
        if self.rect.colliderect(cible): 
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
        super().__init__(jeu, x, y, vie = 200, degats =20, portee=750, cadence=2, prix=100, name = "Tourelle")
        self.image = pg.image.load("assets/images/turrets/basic_turret.png")
        self.image = pg.transform.scale(self.image, (75, 100))
        self.position[0] = (self.position[0] - self.image.get_width()// 2) 
        self.position[1] = (self.position[1] - self.image.get_height()// 2) 
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = self.position[0], self.position[1]
        
    def shoot(self):
        shoot = False
        for entity in self.jeu.game_entities_list:
            if isinstance(entity, enemy.Bot):
                if entity is not None:
                    if entity.position[0] <= self.position[0] + self.portee and self.rect.colliderect((self.position[0], entity.position[1], entity.rect.width, entity.rect.height)):
                        shoot = True
                        break
        if shoot:
            if time.time() - self.last_shot >= self.cadence:
                self.last_shot = time.time()
                return Basic_Projectile(jeu=self.jeu, x=self.position[0]+self.rect.width//2, y=self.position[1]+self.rect.height//2, degats=self.degats)
        return None

class Basic_Projectile(Projectile): 
   
    def __init__(self, jeu, x, y, degats):
        super().__init__(jeu, x, y, degats, vitesse = 1, name="basic_projectile")
        # Définir la couleur en RGB
        self.color = (100, 100, 100)  
        # Définir le rectangle
        self.rect = pg.Rect(self.position[0], self.position[1], 24, 12)  # x, y, largeur, hauteur

    def is_colliding(self, cible : pg.rect):
        if self.rect.colliderect(cible): 
            self.is_dead = True
            return True
        else: return False


class Laser_Turret(Turret):
    
    def __init__(self, jeu, x, y):
        super().__init__(jeu, x, y, vie = 125, degats= 0.02, portee=750, cadence=4, prix=200, name = "Tourelle_Laser")
        self.image = pg.image.load("assets/images/turrets/laser_turret.png")
        self.image = pg.transform.scale(self.image, (75, 100))
        self.position[0] = (self.position[0] - self.image.get_width()// 2) 
        self.position[1] = (self.position[1] - self.image.get_height()// 2) 
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = self.position[0], self.position[1]
    
    def shoot(self):
        shoot = False
        for entity in self.jeu.game_entities_list:
            if isinstance(entity, enemy.Bot):
                if entity is not None:
                    if entity.position[0] <= self.position[0] + self.portee and self.rect.colliderect((self.position[0], entity.position[1], entity.rect.width, entity.rect.height)):
                        shoot = True
                        break
        if shoot:
            if time.time() - self.last_shot >= self.cadence:
                self.last_shot = time.time()
                return Laser_Projectile(jeu=self.jeu, x=self.position[0]+self.rect.width, y=self.position[1]+self.rect.height//2 -5, degats=self.degats)
        return None
     
class Laser_Projectile(Projectile): 
   
    def __init__(self, jeu, x, y, degats):
        super().__init__(jeu, x, y, degats, vitesse = 1, name="basic_projectile")
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
                    if self.is_colliding(bot.rect):
                        bot.get_damage(self.degats)
                        #self.damage = True
        self.height_substraction += 1
        
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
        super().__init__(jeu, x, y, vie = 100, degats= 0.15, portee=210, cadence=0, prix=350, name = "Tourelle_Plasma")
        self.image = pg.image.load("assets/images/turrets/plasma_turret.png")
        self.image = pg.transform.scale(self.image, (75, 100))
        self.position[0] = (self.position[0] - self.image.get_width()// 2) 
        self.position[1] = (self.position[1] - self.image.get_height()// 2) 
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = self.position[0], self.position[1]
        self.plasma_projectile = Plasma_Projectile(jeu=self.jeu, tourelle = self, x=self.position[0]+self.rect.width+2, y=self.position[1]+self.rect.height//2, degats=self.degats)
        self.jeu.game_entities_list.append(self.plasma_projectile)
    
    def shoot(self):
        shoot = False
        for entity in self.jeu.game_entities_list:
            if isinstance(entity, enemy.Bot):
                if entity is not None:
                    if entity.position[0] <= self.position[0] + self.portee and self.rect.colliderect((self.position[0], entity.position[1], entity.rect.width, entity.rect.height)):
                        shoot = True
                        break
        if shoot:
            self.plasma_projectile.state = "active"
            
        else:
            self.plasma_projectile.state = "unactive"
            self.plasma_projectile.particles = []
            
        return None
    
class Plasma_Projectile(Projectile):
    def __init__(self, jeu, tourelle, x, y, degats):
        super().__init__(jeu, x, y, degats, vitesse = 0, name="plasma_projectile")
        self.rect = pg.Rect(self.position[0], self.position[1]-10, 135, 24)
        self.dispersion = randint(-1, 1) / 2
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
            self.particles.append([[self.position[0], self.position[1]], [2, randint(0, 10) / 12 - 0.5], randint(6, 9)])

            for particle in self.particles:
                particle[0][0] += particle[1][0]
                particle[0][1] += particle[1][1]
                particle[2] -= 0.1
                pg.draw.circle(fenetre, (255, 255, 255), [int(particle[0][0]), int(particle[0][1])], int(particle[2]))

                radius = particle[2] * 2
                fenetre.blit(self.circle_surf(radius, (20, 20, 60)), (int(particle[0][0] - radius), int(particle[0][1] - radius)), special_flags=BLEND_RGB_ADD)

                if particle[2] <= 0 or particle[0][0] >= self.cible_x:
                    self.particles.remove(particle)
                   
    def move(self):
        if self.state == "active":
            for bot in self.jeu.game_entities_list:
                if isinstance(bot, enemy.Bot):
                    if self.is_colliding(bot.rect):
                        distance = ((bot.position[0] - self.position[0])**2 + (bot.position[1] - self.position[1])**2)**0.5
                        degat =  max(0, (self.tourelle.portee - distance) / self.tourelle.portee) * self.degats  # Les dégâts augmentent lorsque l'ennemi se rapproche
                        self.cible_x = bot.position[0]
                        return bot.get_damage(degat)

            if self.position[0] > self.jeu.taille_fenetre[0]:
                self.is_dead = True        

                
class BlackHole_Turret(Turret):
    
    def __init__(self, jeu, x, y):
        super().__init__(jeu, x, y, vie = 300, degats= 0.03, portee=1000, cadence=20, prix=300, name = "Tourelle_Blackhole")
        self.image = pg.image.load("assets/images/turrets/blackHole_turret.png")
        self.image = pg.transform.scale(self.image, (75, 100))
        self.position[0] = (self.position[0] - self.image.get_width()// 2) 
        self.position[1] = (self.position[1] - self.image.get_height()// 2) 
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = self.position[0], self.position[1]
        
        
    def shoot(self):
        shoot = False
        for entity in self.jeu.game_entities_list:
            if isinstance(entity, enemy.Bot):
                if entity is not None:
                    if entity.position[0] <= self.position[0] + self.portee and self.rect.colliderect((self.position[0], entity.position[1], entity.rect.width, entity.rect.height)):
                        shoot = True
                        break
        if shoot:
            if time.time() - self.last_shot >= self.cadence:
                self.last_shot = time.time()
                return BlackHole_Projectile(jeu=self.jeu, x=self.position[0]+self.rect.width, y=self.position[1]+self.rect.height//2 -5, degats=self.degats)
        return None

class BlackHole_Projectile(Projectile):
        
        def __init__(self, jeu, x, y, degats):
            super().__init__(jeu, x, y, degats, vitesse = 1, name="blackHole_projectile")
            self.color = (0, 0, 0)  
            self.rect = pg.Rect(self.position[0], self.position[1], 24, 12)  # x, y, largeur, hauteur
            self.last_time = time.time()
            self.range = 500            
            self.is_dead = False
            self.last_time = time.time()
            self.duree = 5
            self.state = "projectile" # or "blackhole"
            self.image = pg.transform.scale(pg.image.load('assets/images/projectiles/blackhole_projectile.png'), (60, 60))
            self.target = self.find_shoot_spot()
            self.attraction_force = 0.075
        
        def find_shoot_spot(self):
            self.bot_list = []
            for entity in self.jeu.game_entities_list:
                if isinstance(entity, enemy.Bot):                
                    if self.rect.colliderect((self.position[0], entity.position[1], entity.rect.width, entity.rect.height)):
                        self.bot_list.append(entity)
            
            if len(self.bot_list) > 0:
                self.bot_list.sort(key=lambda bot: bot.position[0])
                return self.bot_list[-1].position
                
        def move(self):
            
            if self.state == "projectile":
                if self.target is not None:
                    if self.position[0] < self.target[0]:
                        self.position[0] += self.vitesse
                        self.rect.x += self.vitesse
                        self.rect.y = self.position[1]    
                    else:
                        self.state = "blackhole"
                        self.rect = self.image.get_rect()
                        self.rect.x, self.rect.y = self.position[0], self.position[1]-30
                        self.position[1] = self.rect.y
                        self.last_time = time.time()
                
                if self.position[0] > self.jeu.taille_fenetre[0]:
                    self.is_dead = True
            
            
            else:
                
                if time.time() - self.last_time >= self.duree:
                    self.last_time = time.time()
                    self.is_dead = True
                    
                
                diff = list(filter(lambda elt: isinstance(elt, enemy.Bot),filter(lambda elt: elt not in self.bot_list, self.jeu.game_entities_list)))
                if len(diff):
                    for bot in diff:
                        if self.rect.colliderect((self.position[0], bot.position[1], bot.rect.width, bot.rect.height)):
                            self.bot_list.append(bot)
                
                for bot in self.bot_list:
                    if self.is_colliding(bot.rect):
                        bot.get_damage(self.degats)
                    
                    if bot.position[0] <= self.position[0] + self.range and bot.position[0] >= self.position[0] - self.range:
                        if bot.position[0] > self.position[0]:
                            bot.position[0] -= self.attraction_force 
                        else:
                            bot.position[0] += self.attraction_force                 
        
        def render(self, fenetre):
            
            # Dessiner la hitbox 
            #pg.draw.rect(fenetre, (255, 0, 0), self.rect)
            
            # Dessiner l'image sur la fenêtre         
            if self.state == "blackhole":
                fenetre.blit(self.image, (self.position[0], self.position[1]))
            else:
                pg.draw.rect(self.jeu.fenetre, self.color, self.rect)


class Shield(Turret):
    
    def __init__(self, jeu, x, y):
        super().__init__(jeu, x, y, vie = 500, degats= 0, portee=0, cadence=0, prix=250, name = "Bouclier")
        self.image = pg.image.load("assets/images/turrets/shield.png")
        self.image = pg.transform.scale(self.image, (75, 100))
        self.position[0] = (self.position[0] - self.image.get_width()// 2) 
        self.position[1] = (self.position[1] - self.image.get_height()// 2) 
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = self.position[0], self.position[1]
    

class Omni_Turret(Turret):
        def __init__(self, jeu, x, y):
            super().__init__(jeu, x, y, vie = 200, degats= 5, portee="inf", cadence=0.5, prix=450, name = "Tourelle_Omni")
            self.image = pg.image.load("assets/images/turrets/omni_turret.png")
            self.image = pg.transform.scale(self.image, (75, 100))
            self.position[0] = (self.position[0] - self.image.get_width()// 2) 
            self.position[1] = (self.position[1] - self.image.get_height()// 2) 
            self.rect = self.image.get_rect()
            self.rect.x, self.rect.y = self.position[0], self.position[1]
            
        def shoot(self):
            shoot = False
            
            for entity in reversed(self.jeu.game_entities_list):
                if isinstance(entity, enemy.Bot):
                    shoot = True
                    cible = entity

            if shoot:
                if time.time() - self.last_shot >= self.cadence:
                    self.last_shot = time.time()
                    return Omni_Projectile(jeu=self.jeu, x=self.position[0]+self.rect.width/2, y=self.position[1]+self.rect.height/2 , degats=self.degats, cible = cible)
            return None
    
class Omni_Projectile(Projectile):
    
    def __init__(self, jeu, x, y, degats, cible):
        super().__init__(jeu, x, y, degats, vitesse = 2, name="omni_projectile")
        self.image = pg.image.load("assets/images/projectiles/omni_projectile.png")
        self.image = pg.transform.scale(self.image, (20*3, 5*3))
        self.rect = self.image.get_rect()
        self.cible = cible
        self.vx, self.vy = 0, 0
    def move(self):
        if self.is_colliding(self.cible.rect):
            self.cible.get_damage(self.degats)
            self.is_dead = True
        else:
            if self.position[0] -self.vitesse >= self.cible.position[0] + self.cible.rect.width/2:
                vx = -self.vitesse
            elif self.position[0] + self.vitesse <= self.cible.position[0] + self.cible.rect.width/2:
                vx = self.vitesse
            else:
                vx = 0
            
            
            if self.position[1] -self.vitesse >= self.cible.position[1] + self.cible.rect.height/2:
                vy = -self.vitesse
            elif self.position[1] + self.vitesse <= self.cible.position[1] + self.cible.rect.height/2:
                vy = self.vitesse
            else:
                vy = 0
            
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



# // Lance Roquette a atnimatire, trajectorie parabolique, degats de zone en 3*3, explosion, gros dégat, cadence lente, portée moyenne, prix élevé

class AntiMatter_Turret(Turret):
        
        def __init__(self, jeu, x, y):
            super().__init__(jeu, x, y, vie = 200, degats= 50, portee=1000, cadence=10, prix=500, name = "Tourelle_AntiMatter")
            self.image = pg.image.load("assets/images/turrets/antimatter_turret.png")
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
            self.image = pg.transform.scale(pg.image.load('assets/images/projectiles/antimatter_projectile.png'), (60, 60))
            self.rect = self.image.get_rect()
            self.rect.y = y-20
            self.tourelle = tourelle
            self.target = cible.position[:]
            self.liste_points = []
        
        def f(self, x):
            a = self.target[0]
            return -x**2 + x * a + x * self.tourelle.position[0] - self.tourelle.position[0] * a
        
        def trajectory(self, x):
            b = self.tourelle.position[1] - 100
            a = self.target[0]
            print(a)
            return (b / self.f(a/2)) * self.f(x) + self.rect.height//2
        
        def derive(self, x):
            a = self.target[0]
            return -2*x + a
        
        def derive_trajectory(self, x):
            a = self.target[0]
            b = x /2
            return -b/2

        def move(self):
            if self.state == "projectile":
                if self.position[0] < self.target[0]:
                    self.position[0] += self.vitesse
                    self.position[1] = self.jeu.taille_fenetre[1] - self.trajectory(self.position[0]) - self.tourelle.position[1]
                    self.liste_points.append([self.position[0], self.position[1]])
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



if __name__ == "__main__":
    import game
    jeu = game.Game()
    jeu.run()