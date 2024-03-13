import pygame as pg
import time
import enemy

class Turret_selection:
    def __new__(cls, jeu, x, y, name):
        if name == "Turret":
            return Basic_Turret(jeu, x, y)
        
        elif name == "":
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
    
    def get_damage(self, degats):
        self.vie -= degats
        if self.vie <= 0:
            self.is_dead = True
            return True
        else:
            return False
    
    def render(self, fenetre):
        fenetre.blit(self.image, self.position)
        #hitbox
        #pg.draw.rect(fenetre, (255,0,0), (self.rect.x, self.rect.y, self.rect.width, self.rect.height), 1)

        # Calcul du pourcentage de vie
        pourcentage_vie = self.vie / 100
        
        # Calcul de la largeur de la barre verte en fonction du pourcentage de vie
        largeur_barre_verte = self.rect.width * pourcentage_vie
        
        # Calcul de la position de départ de la barre rouge
        position_barre_rouge = (self.rect.x + largeur_barre_verte, self.rect.y)
        
        # Dessin de la barre verte
        pg.draw.rect(fenetre, (0, 255, 0), (self.rect.x, self.rect.y, largeur_barre_verte, 5))
        
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
            self.is_dead = True
            return True
        else: return False

    def render(self, fenetre):
        # Dessiner le rectangle sur la surface
        pg.draw.rect(self.jeu.fenetre, self.color, self.rect)



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

        
class Laser_Turret(Turret):
    
    def __init__(self, jeu, x, y):
        super().__init__(jeu, x, y, vie = 125, degats= 40, portee=750, cadence=4, prix=150, name = "Tourelle_Laser")
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
                return Laser_Projectile(jeu=self.jeu, x=self.position[0]+self.rect.width//2, y=self.position[1]+self.rect.height//2, degats=self.degats)
        return None
    
class Laser_Projectile(Projectile): 
   
    def __init__(self, jeu, x, y, degats):
        super().__init__(jeu, x, y, degats, vitesse = 1, name="basic_projectile")
        # Définir la couleur en RGB
        self.color = (255, 0, 0)  
        # Définir le rectangle
        self.rect = pg.Rect(self.position[0], self.position[1], 750, 15)  # x, y, largeur, hauteur
        self.duree = 5
        self.last_time = time.time()
        
    def move(self):
        for bot in self.jeu.game_entities_list:
            if isinstance(bot, enemy.Bot):
                if self.is_colliding(bot.rect):
                    bot.get_damage(self.degats)
       
        #self.rect.height -= 0.1
        if self.last_time - time.time() >= self.duree:
            self.last_time = time.time()
            self.is_dead = True
    
    
    def render(self, fenetre):
        # Dessiner le rectangle sur la surface
        pg.draw.rect(self.jeu.fenetre, self.color, self.rect)