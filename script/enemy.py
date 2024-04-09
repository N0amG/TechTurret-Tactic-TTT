import pygame as pg
import others

import turret
import random as rd
import time

from abc import ABC, abstractmethod

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
                    self.jeu.game_entities_list.append(Basic_Bot(self.jeu, y, x, self.id))
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

        
    def manual_spawn(self, y, x):
        self.jeu.game_entities_list.append(Basic_Bot(self.jeu, y, x, self.id))
        self.id += 1
        self.spawned += 1
            
    
class Bot(pg.sprite.Sprite):
    def __init__(self, jeu, x, y, id, vie, degats, vitesse, portee, cadence, name, path, nb_images = 8, coef = 3, flip = True, fps = 90):
        self.jeu = jeu
        self.entity_list = jeu.game_entities_list
        self.position = [x, y]
        self.animation = others.Animation(nb_images, path, x, y, (22*coef, 28*coef), flip, fps)
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
        self.name = name
        self.id = id
        self.last_shot = time.time()-self.cadence
        self.is_dead = False

    def __str__(self):
        return f"Bot id : {self.id}"
    

    def update(self):
        self.animation.update()
    
    def move(self):
        self.update()
        self.image = self.animation.image
        
        
        for entity in self.entity_list:
            if isinstance(entity, turret.Turret) and self.rect.colliderect(entity.rect):
                return self.attack(entity)
        
        self.position[0] -= self.vitesse
        self.animation.rect.x, self.animation.rect.y = self.position[0], self.position[1]
        self.rect.x, self.rect.y = self.position[0], self.position[1]
        
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
        #pg.draw.rect(fenetre, (255,0,0), (self.rect.x, self.rect.y, self.rect.width, self.rect.height), 1)
        
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
        

import pygame as pg

class Basic_Bot(Bot):
    def __init__(self, jeu, x, y, id):
        super().__init__(jeu, x, y, id, vie = 100, degats=20, vitesse= 0.05, portee = 0, cadence = 2, path ="enemy/basic_bot_frames/frame_", name="Basic_Bot", fps=70)


class Drone_Bot(Bot, others.Animation):
    def __init__(self, jeu, x, y, id):
        super().__init__(jeu, x, y, id, vie = 25, degats=10, vitesse= 0.15, portee = 0, cadence = 0.5, path ="enemy/drone_bot_frames/frame_", name="Drone_Bot", coef = 3, flip= False)
    
    def move(self):
        self.update()
        self.image = self.animation.image
        
        self.position[0] -= self.vitesse
        self.animation.rect.x, self.animation.rect.y = self.position[0], self.position[1]
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
        
   
        
    
        

if __name__ == "__main__":
    import game
    jeu = game.Game()
    jeu.run()