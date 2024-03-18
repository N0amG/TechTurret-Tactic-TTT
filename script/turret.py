import pygame as pg
import time
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
        else:
            return None

class Turret:
    def __init__(self, jeu, x, y, vie, degats, portee, cadence, prix, name):
        # Ajoutez ici les attributs spécifiques à la classe Turret
        self.jeu = jeu
        self.entity_list = jeu.game_entities_list
        self.position = [x, y]
        self.vie = vie
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
        #hitbox
        #pg.draw.rect(fenetre, (255,0,0), (self.rect.x, self.rect.y, self.rect.width, self.rect.height), 1)

        # Calcul du pourcentage de vie
        pourcentage_vie = self.vie / 100
        
        # Calcul de la largeur de la barre verte en fonction du pourcentage de vie
        largeur_barre_verte = round(self.rect.width * pourcentage_vie)

        # Calcul de la position de départ de la barre rouge
        position_barre_rouge = (self.rect.x + largeur_barre_verte, self.rect.y)

        # Dessin de la barre verte
        pg.draw.rect(fenetre, (0, 255, 0), (self.rect.x, self.rect.y, self.rect.width, 5))

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
        super().__init__(jeu, x, y, vie = 100, degats =20, portee=750, cadence=2, prix=100, name = "Tourelle")
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
        super().__init__(jeu, x, y, vie = 250, degats= 0.2, portee=1050, cadence=0, prix=350, name = "Tourelle_Laser")
        self.image = pg.image.load("assets/images/turrets/plasma_turret.png")
        self.image = pg.transform.scale(self.image, (75, 100))
        self.position[0] = (self.position[0] - self.image.get_width()// 2) 
        self.position[1] = (self.position[1] - self.image.get_height()// 2) 
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = self.position[0], self.position[1]
        self.last_shot = time.time()

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
                return Plasma_Projectile(jeu=self.jeu, x=self.position[0]+self.rect.width, y=self.position[1]+self.rect.height//2 -5, degats=self.degats)
        return None
    
class Plasma_Projectile(Projectile):
    def __init__(self, jeu, x, y, degats):
        super().__init__(jeu, x, y, degats, vitesse = 0, name="plasma_projectile")
        self.color = (255, 0, 0)
        self.rect = pg.Rect(self.position[0], self.position[1], 75, 24)
        self.damage = False
        self.dispersion = randint(-1, 1) / 2
        # [loc, velocity, timer]
        self.particles = []
        self.last_particle = time.time()
        self.delais = 0.1
        
    def circle_surf(self, radius, color):
        surf = pg.Surface((radius * 2, radius * 2))
        pg.draw.circle(surf, color, (radius, radius), radius)
        surf.set_colorkey((0, 0, 0))
        return surf

    def render(self, fenetre):
        
        min_radius = 1 # Définissez ceci à la taille maximale que vous voulez pour vos particules
        
        if time.time() - self.last_particle >= self.delais:
            self.last_particle = time.time()
            self.delais = random() 
            self.particles.append([[self.position[0] + randint(0, 20), self.position[1]], [randint(1, 10)/randint(1, 5), 0], randint(3,7)])  # Initialise le rayon à 1
            
        for particle in self.particles:
            particle[0][0] += particle[1][0]
            particle[0][1] += particle[1][1] + self.dispersion
            particle[2] -=  random() * 0.2  # Augmente le rayon jusqu'à max_radius
            pg.draw.circle(fenetre, (255, 255, 255), [int(particle[0][0]), int(particle[0][1])], int(particle[2]))
            radius = particle[2] * 2
            fenetre.blit(self.circle_surf(radius, (20, 20, 60)), (int(particle[0][0] - radius), int(particle[0][1] - radius)), special_flags=BLEND_RGB_ADD)

            if particle[2]-2 < min_radius:
                self.particles.remove(particle)
        
        
            
                
class BlackHole_Turret(Turret):
    
    def __init__(self, jeu, x, y):
        super().__init__(jeu, x, y, vie = 350, degats= 0.03, portee=1000, cadence=20, prix=300, name = "Tourelle_Blackhole")
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


