import pygame as pg
import others

import turret
import random as rd
import time

from abc import ABC, abstractmethod
from pygame import BLEND_RGB_ADD
import math

import matplotlib.pyplot as plt

class Bot_Wave_Spawner:
    def __init__(self, jeu):
        self.jeu = jeu
        self.spawned = 0
        self.bot_id = 0
        self.spawn_rate = 8
        self.bot_quantity = 10
        self.last_spawn = 0
        
        self.bot_price_dict = {"basic" : 50, "assault" : 75,  "drone" : 100, "kamikaze" : 125, "tank" : 175, "emp" : 200, "incinerator" : 200, "ender" : 250, "stealth" : 250, "titan" : 0}
        
        self.wave_points = 500
        self.available_points = 500
        
        self.available_bots = ["basic",]
        self.bots_to_unlock = ["assault", "drone", "kamikaze", "tank", "emp", "incinerator", "ender", "stealth"][::-1]
        
        self.sub_wave = 1 # total of 3 subwaves per wave. 1 = beetween 2 and 3 bots, 2 = 1/3 of the total bots minus those of subwave 1, 3 = 2/3 of the total bots
        
        self.boss_wave = 10
        
        self.first_sub_wave_rd = rd.randint(2, 3)
        
        self.list_of_bots_to_spawn = self.sort_bots(self.generate_next_bots_list())

    def update(self):
        
        if not self.jeu.wave_ended:
            if self.spawned >= self.bot_quantity or self.available_points <= self.bot_price_dict["basic"] or (self.jeu.wave == self.boss_wave and self.spawned >= 1):
                cond = True
                for bot in self.jeu.game_entities_list:
                    if isinstance(bot, Bot):
                        cond = False
                        break
                if cond:
                    self.end_of_wave()
                    return 3
            
            if self.boss_wave == self.jeu.wave and self.spawned == 0:
                    self.boss_spawn()
                    return 4
            
            elif self.next_spawn() and not self.boss_wave == self.jeu.wave:
                if self.list_of_bots_to_spawn:
                    
                    # Choisissez une coordonnée aléatoire dans la ligne
                    x, y = rd.randint(0,len(self.jeu.matrice_bot)-1), rd.randint(0,len(self.jeu.matrice_bot[0])-1)
                    x, y = self.jeu.matrice_bot[x][y]
                
                    self.spawn(y, x, self.list_of_bots_to_spawn.pop(0))
                    
                    #self.end_of_wave()
                    return 1

            else:
                return 2
        else:
            return False
    
    def next_spawn(self):
        #print(self.sub_wave_cut, self.spawned, self.sub_wave, " | S.R : ", self.spawn_rate)
        if self.spawned < self.bot_quantity:
            nb_bot = 0
            for bot in self.jeu.game_entities_list:
                if isinstance(bot, Bot):
                    nb_bot += 1
                    
            if time.time() - self.last_spawn >= self.spawn_rate:
                #print("still executing")
                
                # Permet de passer à la sous-vague suivante
                if self.sub_wave == 1:
                    if nb_bot >= 1:
                        return False
                    
                    elif self.spawned >= self.sub_wave_cut[0] and nb_bot == 0:
                        self.sub_wave = 2
                        self.spawn_rate -= 0.5
                        
                elif self.sub_wave == 2:
                    if nb_bot >= 2 or (self.spawned >= self.sub_wave_cut[1] and nb_bot > 0):
                        return False
                    

                    if self.spawned >= self.sub_wave_cut[1] and nb_bot == 0:
                        self.sub_wave = 3
                        self.spawn_rate -= 0.5
                        
                return True

                
            # Permet d'ajouter des bots si il y en a trop peu
            cond = False
                
            if self.sub_wave == 2:
                if nb_bot < 4 and self.spawned < self.sub_wave_cut[1]:
                    cond = True
                
                if self.spawned >= self.sub_wave_cut[1] and nb_bot > 0:
                        return False

            if self.sub_wave == 3:
                if nb_bot < 5:
                    cond = True
            #print("still executing 2")

            return cond
        #print("still executing 3")
        return False

    def boss_spawn(self):
        self.spawn(self.jeu.matrice_bot[1][1][1], self.jeu.matrice_bot[1][1][0], "titan")
        self.spawned += 1

    def end_of_wave(self):
        self.jeu.wave_ended = True
        self.spawned = 0
        self.sub_wave = 1
        self.spawn_rate = 8
        
        if self.jeu.wave <= 3:
            self.bot_quantity += 3
            self.wave_points += 300
            
        elif self.jeu.wave <= 6:
            self.bot_quantity += 4
            self.wave_points += 1000
            
        elif self.jeu.wave <= 9:
            self.bot_quantity += 5
            self.wave_points += 1500
                      
        
        self.spawn_rate -= self.jeu.wave*0.5
        if self.spawn_rate < 4: self.spawn_rate = 4
            
        if self.bots_to_unlock:
            self.available_bots.append(self.bots_to_unlock.pop())
        
        self.available_points = self.wave_points
        self.list_of_bots_to_spawn = self.sort_bots(self.generate_next_bots_list())

    def spawn(self, y, x, bot_type):
        
        if self.available_points >= self.bot_price_dict[bot_type]:
            if bot_type == "drone":
                self.jeu.game_entities_list.append(Drone_Bot(self.jeu, y, x, self.bot_id))
            elif bot_type == "assault":
                self.jeu.game_entities_list.append(Assault_Bot(self.jeu, y, x, self.bot_id))
            elif bot_type == "kamikaze":
                self.jeu.game_entities_list.append(Kamikaze_Bot(self.jeu, y, x, self.bot_id))
            elif bot_type == "tank":
                self.jeu.game_entities_list.append(Tank_Bot(self.jeu, y, x, self.bot_id))
            elif bot_type == "emp":
                self.jeu.game_entities_list.append(EMP_Bot(self.jeu, y, x, self.bot_id))
            elif bot_type == "incinerator":
                self.jeu.game_entities_list.append(Incinerator_Bot(self.jeu, y, x, self.bot_id))
            elif bot_type == "ender":
                self.jeu.game_entities_list.append(Ender_Bot(self.jeu, y, x, self.bot_id))
            elif bot_type == "stealth":
                self.jeu.game_entities_list.append(StealthBlack_Bot(self.jeu, y, x, self.bot_id))
            elif bot_type == "titan":
                self.jeu.game_entities_list.append(TITAN_Boss(self.jeu, y, x, self.bot_id))
            else:
                self.jeu.game_entities_list.append(Basic_Bot(self.jeu, y, x, self.bot_id))
        
            self.bot_id += 1
            self.spawned += 1
            self.last_spawn = time.time()
            if bot_type != "titan": self.available_points -= self.bot_price_dict[bot_type]
            #print(self.list_of_bots_to_spawn)
            #print(f"subwave : {self.sub_wave} | {self.spawned} / {self.bot_quantity} bots spawned")
            return True
        
        else:
            #print(self.list_of_bots_to_spawn)
            #print(f"subwave : {self.sub_wave} | {self.spawned} / {self.bot_quantity} bots spawned")
            return False
        
    def manual_spawn(self, y, x, bot_type):
        if bot_type == "drone":
            self.jeu.game_entities_list.append(Drone_Bot(self.jeu, y, x, self.bot_id))
        elif bot_type == "assault":
            self.jeu.game_entities_list.append(Assault_Bot(self.jeu, y, x, self.bot_id))
        elif bot_type == "kamikaze":
            self.jeu.game_entities_list.append(Kamikaze_Bot(self.jeu, y, x, self.bot_id))
        elif bot_type == "tank":
            self.jeu.game_entities_list.append(Tank_Bot(self.jeu, y, x, self.bot_id))
        elif bot_type == "emp":
            self.jeu.game_entities_list.append(EMP_Bot(self.jeu, y, x, self.bot_id))
        elif bot_type == "incinerator":
            self.jeu.game_entities_list.append(Incinerator_Bot(self.jeu, y, x, self.bot_id))
        elif bot_type == "ender":
            self.jeu.game_entities_list.append(Ender_Bot(self.jeu, y, x, self.bot_id))
        elif bot_type == "stealth":
            self.jeu.game_entities_list.append(StealthBlack_Bot(self.jeu, y, x, self.bot_id))
        elif bot_type == "titan":
            self.jeu.game_entities_list.append(TITAN_Boss(self.jeu, y, x, self.bot_id))
        else:
            self.jeu.game_entities_list.append(Basic_Bot(self.jeu, y, x, self.bot_id))

    def generate_next_bots_list(self):
        bots_to_spawn = []
        # Triez la liste des types de robots en fonction de leur coût, du moins cher au plus cher. uniquement parmi les bots disponibles
        sorted_bots = sorted((item for item in self.bot_price_dict.items() if item[0] in self.available_bots), key=lambda item: item[1])

        while self.available_points > 0 and self.spawned < self.bot_quantity:
            # Si c'est le début de la vague, générer un certain nombre de robots "basic" ou "assault".
            if self.spawned < self.first_sub_wave_rd:
                bot_types = ['basic']
                bot_type = rd.choices(
                    population=bot_types,
                    weights=[self.bot_price_dict[bot] for bot in bot_types if bot in self.bot_price_dict], k=1)[0]
            else:

                # Calculez le nombre maximal de chaque type de robot que vous pouvez vous permettre avec les points disponibles
                # et le nombre maximal de robots autorisés à apparaître. Stockez ces valeurs dans un dictionnaire.
                max_bots = {bot[0]: min(self.available_points // bot[1], self.bot_quantity - self.spawned) for bot in sorted_bots}

                # Choisissez un type de robot à apparaître. La probabilité de choisir un type de robot spécifique pourrait être
                # inversement proportionnelle à son coût (c'est-à-dire que les robots moins chers sont plus susceptibles d'être choisis,
                # mais il y a toujours une chance que les robots plus chers soient choisis).
                bot_type = rd.choices(
                    population=list(max_bots.keys()),
                    weights=[(self.bot_price_dict[bot] + self.jeu.wave) / (self.bot_price_dict[bot] + 1) for bot in max_bots.keys()],
                    k=1
                )[0]

            # Si le nombre maximal de ce type de robot n'a pas encore été atteint, déduisez son coût des points disponibles et
            # incrémentez le nombre de robots apparus.
            if self.available_points >= self.bot_price_dict[bot_type]:
                self.available_points -= self.bot_price_dict[bot_type]
                self.spawned += 1
                bots_to_spawn.append(bot_type)
            else:
                affordable_bots = [bot for bot in self.available_bots if self.bot_price_dict[bot] <= self.available_points]
                if affordable_bots:
                    bot_type = max(affordable_bots, key=self.bot_price_dict.get)
                    self.available_points -= self.bot_price_dict[bot_type]
                    self.spawned += 1
                    bots_to_spawn.append(bot_type)
                else:
                    break
                    
        
        self.available_points = self.wave_points
        self.spawned = 0
        
        self.sub_wave_cut = [self.first_sub_wave_rd, len(bots_to_spawn)//2, len(bots_to_spawn)]
        #print(len(bots_to_spawn), self.sub_wave_cut)
        
        
        
        # Retournez la liste des types de robots à faire apparaître.
        return bots_to_spawn


    def sort_bots(self, bots):
        bot_depart = [self.get_index(bot) for bot in bots]
        # Calculez la fréquence de chaque type de robot
        probas = {bot : (self.get_index(bot)) / (len(self.bot_price_dict)) for bot in bots}
        for i in range(len(bots)):
            min_idx = i
            for j in range(i+1, len(bots)):
                nb = rd.randint(0, len(self.bot_price_dict)-1)/10
                if probas[bots[min_idx]] > nb:
                    min_idx = j
            bots[i], bots[min_idx] = bots[min_idx], bots[i]
            
        bot_intermediaire = [self.get_index(bot) for bot in bots]
        # Déplacez les bots avec l'index le plus élevé vers la droite au moins une fois
        sorted_indexes = sorted(self.get_index(bot) for bot in bots)
        top_tier_index = sorted_indexes[int(len(sorted_indexes) * 2 / 3)]  # L'index qui représente le début du tiers supérieur
        for _ in range(bots.count(self.available_bots[top_tier_index])):  # Répétez pour chaque bot avec un index dans le tiers supérieur
            nb_decalage = rd.randint(1, (len(bots)-1))
            for i in range(len(bots) - 1):  # -1 pour éviter de dépasser la fin de la liste
                if self.get_index(bots[i]) >= top_tier_index:
                    bots[i], bots[i+1] = bots[i+1], bots[i]
                    nb_decalage -= 1
                    if nb_decalage == 0:
                        break

        bot_trie = [self.get_index(bot) for bot in bots]
        
        #self.draw_graph(bot_depart,bot_intermediaire, bot_trie)
        return bots
    
    def get_index(self, bot_type):
        keys_list = list(self.bot_price_dict.keys())
        return keys_list.index(bot_type)
    
    def draw_graph(self, bots_depart, bot_intermediaire ,bot_trie):
        plt.figure()
    
        # Créer le graphique du haut
        plt.subplot(3, 1, 1)  # 2 lignes, 1 colonne, graphique n°1
        plt.bar(range(len(bots_depart)), bots_depart)
        plt.title('Bots Depart')

        # Créer le graphique du milieu
        plt.subplot(3, 1, 2)  # 2 lignes, 1 colonne, graphique n°1
        plt.bar(range(len(bot_intermediaire)), bot_intermediaire)
        plt.title('Bots inter')
        
        # Créer le graphique du bas
        plt.subplot(3, 1, 3)  # 2 lignes, 1 colonne, graphique n°2
        plt.bar(range(len(bot_trie)), bot_trie)
        plt.title('Bot Trie')
    
        # Afficher le graphique
        plt.show()

class Bot(pg.sprite.Sprite):
    def __init__(self, jeu, x, y, id, vie, point, degats, vitesse, portee, cadence, name, path, nb_images = 8, coef = (66, 84), flip = True, fps = 90):
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
        self.point = point
        self.degats = degats
        self.vitesse = vitesse
        self.portee = portee
        self.cadence = cadence

        self.id = id
        self.last_shot = time.time()-self.cadence
        self.is_dead = False
        
        self.show_hitbox = False


    def __str__(self):
        return f"Bot id : {self.id}, name : {self.name}"
    
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

    def get_damage(self, degats, source=None):
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

        # Calcul de la largeur de la bbotse verte en fonction du pourcentage de vie
        largeur_bbotse_verte = round(self.rect.width * pourcentage_vie)

        # Calcul de la position de départ de la bbotse rouge
        position_bbotse_rouge = (self.rect.x + largeur_bbotse_verte, self.rect.y)

        # Dessin de la bbotse verte
        pg.draw.rect(fenetre, (0, 255, 0), (self.rect.x, self.rect.y, largeur_bbotse_verte, 5))  # Utilisez la largeur de la bbotse verte pour le troisième argument

        # Dessin de la bbotse rouge
        pg.draw.rect(fenetre, (255, 0, 0), (position_bbotse_rouge[0], position_bbotse_rouge[1], self.rect.width - largeur_bbotse_verte, 5))


class Basic_Bot(Bot):
    def __init__(self, jeu, x, y, id):
        super().__init__(jeu, x, y, id, vie = 100, point = 50, degats=20, vitesse= 0.4, portee = 0, cadence = 2, path ="enemy/basic_bot_frames/frame_", name="Basic_Bot")


class Assault_Bot(Bot):
    def __init__(self, jeu, x, y, id):
        super().__init__(jeu, x, y, id, vie = 200, point = 75,degats=25, vitesse= 0.25, portee = 300, cadence = 3, path ="enemy/assault_bot_frames/frame_", name="Assault_Bot")
    
    def update(self):
        self.animation.update()
        self.shoot()
    
    def shoot(self):
        if time.time() - self.last_shot >= self.cadence:
            for entity in self.entity_list:
                if isinstance(entity, turret.Turret) and self.rect.colliderect((entity.rect.x + self.portee, entity.rect.y, entity.rect.width, entity.rect.height)):
                    self.last_shot = time.time()
                    bullet = Bullet(self.jeu, self.rect.x, self.rect.y + self.rect.height/2 , self.degats)
                    self.jeu.game_entities_list.append(bullet)


class Bullet: 
   
    def __init__(self, jeu, x, y, degats, name="bullet"):
        self.jeu = jeu
        self.entity_list = jeu.game_entities_list
        self.position = [x, y]
        self.degats = degats
        self.vitesse = 5
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


class Drone_Bot(Bot):
    def __init__(self, jeu, x, y, id):
        super().__init__(jeu, x, y, id, vie = 10, point = 150, degats=10, vitesse= 1.25, portee = 0, cadence = 0.6, path ="enemy/drone_bot_frames/frame_", name="Drone_Bot", coef = (66*0.9, 84*0.8), flip= False, fps= 90)
    
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

    def get_damage(self, degats, source=None):
        # drone est immunisé aux dégats
        if source == "blackhole":
            return super().get_damage(degats)
 
    def render(self, fenetre):
        
        self.animation.render(fenetre)
        
        # hitbox
        if self.show_hitbox:
            pg.draw.rect(fenetre, (0,255,0), (self.rect.x, self.rect.y, self.rect.width, self.rect.height), 1)
        
        if self.vie == self.vie_max:
            return
        
        # Calcul du pourcentage de vie
        pourcentage_vie = self.vie / self.vie_max  # Utilisez la vie maximale de la tourelle pour calculer le pourcentage de vie

        # Calcul de la largeur de la bbotse verte en fonction du pourcentage de vie
        largeur_bbotse_verte = round(self.rect.width * pourcentage_vie)

        # Calcul de la position de départ de la bbotse rouge
        position_bbotse_rouge = (self.rect.x + largeur_bbotse_verte, self.rect.y)

        # Dessin de la bbotse verte
        pg.draw.rect(fenetre, (0, 255, 0), (self.rect.x, self.rect.y-35, largeur_bbotse_verte, 5))  # Utilisez la largeur de la bbotse verte pour le troisième argument

        # Dessin de la bbotse rouge
        pg.draw.rect(fenetre, (255, 0, 0), (position_bbotse_rouge[0], position_bbotse_rouge[1]-35, self.rect.width - largeur_bbotse_verte, 5))

class Kamikaze_Bot(Bot):
    def __init__(self, jeu, x, y, id):
        super().__init__(jeu, x, y, id, vie = 50, point = 100,degats=150, vitesse= 0.75, portee = 0, cadence = 0, path ="enemy/kamikaze_bot_frames/frame_", name="Kamikaze_Bot")
    
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
        super().__init__(jeu, x, y, id, vie = 400, point = 250, degats=50, vitesse= 0.25, portee = 0, cadence = 6, coef= (66, 84), path ="enemy/tank_bot/tank_bot_frames/frame_", name="Tank_Bot", fps= 40)
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
        super().__init__(jeu, x, y, id, vie = 100, point = 150, degats=25, vitesse= 0.60, portee = 0, cadence = 20, path ="enemy/emp_bot_frames/frame_", name="EMP_Bot")
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
        super().__init__(jeu, x, y, id, vie = 150, point = 175,degats=2, vitesse= 0.40, portee = 210, cadence = 5, path ="enemy/incinerator_bot/unactive_incinerator_bot/frame_", name="Incinerator_Bot")
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
        if shoot and self.fire_projectile.state == "unactive":
            self.fire_projectile.state = "active"
            self.animation.get_images(8, "enemy/incinerator_bot/active_incinerator_bot/frame_")
            
        elif not shoot and self.fire_projectile.state == "active":
            self.fire_projectile.state = "unactive"
            self.animation.get_images(8, "enemy/incinerator_bot/unactive_incinerator_bot/frame_")
            self.fire_projectile.particles = []
            
        return None

class Fire_Projectile:
    def __init__(self, jeu, tourelle, x, y, degats, vitesse = 2, name="fire_projectile"):
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
                self.particles.append([[self.position[0], self.position[1]], [2, rd.randint(0, 10) / 12 - 0.5], rd.randint(6, 9)])

                for particle in self.particles:
                    particle[0][0] -= particle[1][0] * self.vitesse
                    particle[0][1] += particle[1][1] * self.vitesse
                    particle[2] -= 0.1
                    pg.draw.circle(fenetre, (255, 255, 25), [int(particle[0][0]), int(particle[0][1])], int(particle[2]))

                    radius = particle[2] * 2
                    fenetre.blit(self.circle_surf(radius, (100, 20, 20)), (int(particle[0][0] - radius), int(particle[0][1] - radius)), special_flags=BLEND_RGB_ADD)

                    if particle[2] <= 0 or particle[0][0] <= self.cible_x + self.cible_width:
                        self.particles.remove(particle)
        else:
            for particle in self.particles:
                pg.draw.circle(fenetre, (255, 255, 25), [int(particle[0][0]), int(particle[0][1])], int(particle[2]))
                radius = particle[2] * 2
                fenetre.blit(self.circle_surf(radius, (100, 20, 20)), (int(particle[0][0] - radius), int(particle[0][1] - radius)), special_flags=BLEND_RGB_ADD)
                
    def move(self):
        if self.state == "active":
            distance_min = self.rect.width
            cible = None
            for entity in reversed(self.jeu.game_entities_list):

                if isinstance(entity, turret.Turret):
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

            if self.position[0] < 0:  # Check if the projectile has passed the left edge of the window
                self.is_dead = True   

    def is_colliding(self, cible):
        if self.rect.colliderect(cible.rect):
            return True
        else: return False


class Ender_Bot(Bot):
    def __init__(self, jeu, x, y, id):
        super().__init__(jeu, x, y, id, vie = 180, point = 200,degats=70, vitesse= 0.5, portee = 10, cadence = 2.5, path ="enemy/ender_bot_frames/frame_", name="Ender_Bot", fps= 60)
        self.special_ability_cooldown = 5
        self.last_ability_use = time.time() - self.special_ability_cooldown  # The last time the special ability was used
        self.ability_state = "unactive"
        self.blackhole_counter = False
            
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
        self.update()
        
        if self.ability_state == "active":
            if self.teleportation_animation_start != None:
                if self.teleportation_animation_start.is_dead:

                    self.teleportation_animation_start = None
                    
                    if not self.blackhole_counter:
                        # Teleport the enemy to a new position
                        line = rd.randint(0,len(self.jeu.matrice_bot)-1)
                        while self.jeu.matrice_bot[line][0][0] - self.rect.height//2 == self.position[1]:
                            line = rd.randint(0,len(self.jeu.matrice_bot)-1)
                        self.position[1] = self.jeu.matrice_bot[line][0][0] - self.rect.height//2
                        self.rect.y = self.position[1]
                        self.animation.rect.y = self.position[1]
                        self.teleportation_animation_end = others.Animation(self.jeu, 16, "projectiles/teleportation_frames/frame_", "teleportation", self.rect.x-30, self.rect.y-20, (120, 160), flip=False, loop= False, fps=120, reverse=True)
                        self.jeu.game_entities_list.append(self.teleportation_animation_end)
                
                if self.teleportation_animation_start == None and self.blackhole_counter:
                    self.ability_state = "unactive"
                    self.last_ability_use = time.time()  # Update the last ability use time
                    
            if self.teleportation_animation_end != None:
                if self.teleportation_animation_end.is_dead:
                    self.ability_state = "unactive"
                    self.last_ability_use = time.time()  # Update the last ability use time
                    self.teleportation_animation_end = None
        else:
            return super().move()
    
    def get_damage(self, degats, source=None):
        if self.vie - degats >= 0:
            self.special_ability()
        return super().get_damage(degats)


class StealthBlack_Bot(Bot):
    def __init__(self, jeu, x, y, id):
        super().__init__(jeu, x, y, id, vie = 200, point = 225, degats=70, vitesse= 0.75, portee = 0, cadence = 5, path ="enemy/stealth_black_bot_frames/frame_", name="StealthBlack_Bot")
        self.animation.entity = self
        self.stealth = True
        self.stealth_cooldown = 5
        self.last_shot = 0
        
    def update(self):
        self.animation.update()
        
        if time.time() - self.last_shot >= self.stealth_cooldown:
            self.stealth = True

    
    def attack(self, cible):
        self.stealth = False
        return super().attack(cible)

    def get_damage(self, degats, source=None):
        if self.stealth:
            return False
        return super().get_damage(degats)


class TITAN_Boss(Bot):
    def __init__(self, jeu, x, y, id):
        super().__init__(jeu, x, y, id, vie = 5000, point = 2500,degats=0, vitesse= 0.25, portee = 0, cadence = 5, path ="enemy/titan/titan_moving_frames/frame_", nb_images=4, coef = (160*5, 96*5), name="TITAN_Boss", fps= 45)

        self.state_list = ["moving", "standing" , "attack_1", "attack_2",
                           "shield", "death_beam", "damaged", "death"]
        
        self.cooldown_dict = {"punch" : 2, "attack_1" : 15, "attack_2" : 20, "shield" : 25, "death_beam" : 100}
        self.duration_dict = {"attack_1" : 8, "attack_2" : 5, "shield" : 10, "death_beam" : 11, "damaged" : 2, "death" : 7}
        self.last_time_ability_dict = {"punch" : 0, "attack_1" : 0, "attack_2" : 0, "shield" : 0, "death_beam" : 0}

        self.last_shot = time.time()
        
        self.projectile_list = []
        
        self.next_state= "" # in [attack_1, attack_2, shield, death_beam]
        self.next_state_start = None
        
        self.state = self.state_list[0]
        self.state_start = time.time()
        
        self.phase = 0
        self.phase_cond = True
        #self.position[0] += 300
        
        self.animation_position = [self.position[0], self.position[1]]
        self.animation = others.TITAN_Animation(jeu=jeu, path="enemy/titan/", name="TITAN_Boss", x = x, y = y, proportion=(160*5, 96*5), flip=True, fps= 40, entity=self)
        
        
        self.position = [self.position[0] + 225, self.position[1] + 190]
        self.rect = pg.Rect(self.position[0], self.position[1], 360, 300)

        self.death_beam_projectile = None

        self.show_hitbox = False
        self.show_life = False
    
    def update(self):
                
        self.animation.update()
        #ajouter un systeme de destruction des tourelles en contact et de l'avancer si n'y a plus de tourelles
        
        if self.state == "damaged":
            pass
        
        elif self.collision_detection() or self.collision_detection_infront():
            if self.vie > 0:
                self.state = self.state_list[0]
            
        elif self.phase == 0: self.phase_0()
                
        elif self.phase == 1: self.phase_1()
        
        elif self.phase == 2: self.phase_2()
        
        elif self.phase == 3: self.phase_3()
        
        self.state_action()

        self.life_counter()
    
    def state_action(self):
        
        if self.state == "death":
            self.death()
        elif self.state == "damaged":
            self.end_damaged()
        elif self.state == "standing":
            pass
        elif self.state == "moving":
            self.moving_forward()
        elif self.state == "attack_1":
            self.attack_1()
        elif self.state == "attack_2":
            self.attack_2()
        elif self.state == "shield":
            pass
        elif self.state == "death_beam":
            self.death_beam()
            
        if self.projectile_list:
            self.projectile_move()

    def choose_next_state(self, state_list, max_delay = 8):
        state_list_copy = state_list.copy()
        state_cooldown_list = []
        for state in state_list_copy:
            cooldown = self.last_time_ability_dict[state] + self.cooldown_dict[state]
            if cooldown > time.time():
                state_list.remove(state)
                state_cooldown_list.append((state, cooldown))
        
        # si aucun état n'est disponible on prend celui qui a le cooldown le plus bas
        if state_list == []:
            state_tuple = min(state_cooldown_list, key=lambda item: item[1])
            self.next_state = state_tuple[0]
            self.next_state_start = state_tuple[1] + rd.randint(0, max_delay)
            self.last_time_ability_dict[self.next_state] = self.next_state_start
            return
        
        self.next_state = rd.choice(state_list)
        self.next_state_start = time.time() + rd.randint(0, max_delay)
        self.last_time_ability_dict[self.next_state] = self.next_state_start
        
    def switch_to_next_state(self):
        self.state = self.next_state
        self.state_start = time.time()
        self.animation.get_state()
    
    def phase_0(self):
        if self.state == self.state_list[0] and self.phase == 0:
            if self.position[0] <= 1080:
                self.phase = 1

    def phase_1(self):
        if self.state == self.state_list[0]: 
            self.state = self.state_list[1]
            self.state_start = time.time()
            self.choose_next_state(["attack_1", "attack_2"])
            
        if self.state == self.state_list[1]:
            if time.time() >= self.next_state_start:
                self.switch_to_next_state()
                self.next_state= ""
                self.next_state_start = None

    
        if self.state != "standing" and time.time() - self.state_start >= self.duration_dict[self.state] and self.next_state== "":
            self.state = self.state_list[1]
            self.state_start = time.time()
            self.animation.get_state()
            self.choose_next_state(["attack_1", "attack_2"])
        
    def phase_2(self):
        if self.phase_cond or self.state == self.state_list[0]: 
            self.state = self.state_list[1]
            self.state_start = time.time()
            self.choose_next_state(["attack_1", "attack_2", "shield"])
            self.phase_cond = False
            
        if self.state == self.state_list[1]:
            if time.time() >= self.next_state_start:
                self.switch_to_next_state()
                self.next_state= ""
                self.next_state_start = None

    
        if self.state != "standing" and time.time() - self.state_start >= self.duration_dict[self.state] and self.next_state== "":
            self.state = self.state_list[1]
            self.state_start = time.time()
            self.animation.get_state()
            self.choose_next_state(["attack_1", "attack_2", "shield"])
    
    def phase_3(self):
        if self.phase_cond or self.state == self.state_list[0]: 
            self.state = self.state_list[1]
            self.state_start = time.time()
            if self.phase_cond :
                self.choose_next_state(["death_beam"])
                self.phase_cond = False
            else : 
                self.choose_next_state(["attack_1", "attack_2", "shield", "death_beam"])
            
        if self.state == self.state_list[1]:
            if time.time() >= self.next_state_start:
                self.switch_to_next_state()
                self.next_state= ""
                self.next_state_start = None

    
        if self.state != "standing" and time.time() - self.state_start >= self.duration_dict[self.state] and self.next_state== "":
            self.state = self.state_list[1]
            self.state_start = time.time()
            self.animation.get_state()
            self.choose_next_state(["attack_1", "attack_2", "shield", "death_beam"])
    
    def moving_forward(self):
        if self.state == self.state_list[0]:
            self.position[0] -= self.vitesse
            self.animation_position[0] -= self.vitesse
            
            self.rect.x, self.rect.y = self.position[0], self.position[1]
            self.animation.rect.x, self.animation.rect.y = self.animation_position
    
    def projectile_move(self):
        for projectile in self.projectile_list:
            projectile.move()
            if projectile.is_dead:
                self.projectile_list.remove(projectile)
    
    def life_counter(self):
        if self.vie == self.vie_max:
            self.life_steps = [self.vie_max/3 * i for i in range(0, 3)]
            #print(self.life_steps)
        
        if self.vie <= self.life_steps[0] and self.phase == 3:
            self.state = self.state_list[6]
            self.state_start = time.time()
            self.animation.get_state()
            self.phase = 4
            self.phase_cond = True

            # kamas distribué a la fin de l'animation de mort automatiquement
            
        elif self.vie <= self.life_steps[1] and self.phase == 2:
            self.state = self.state_list[6]
            self.state_start = time.time()
            self.animation.get_state()
            self.phase = 3
            self.phase_cond = True
            
            self.jeu.kamas += 1000
            
        elif self.vie <= self.life_steps[2] and self.phase == 1:
            self.state = self.state_list[6]
            self.state_start = time.time()
            self.animation.get_state()
            self.phase = 2
            self.phase_cond = True

            self.jeu.kamas += 500
    def end_damaged(self):
        if self.animation.is_animation_done:
            if self.vie > 0:
                self.animation.is_animation_done = False
                self.state = self.state_list[1]
                self.state_start = time.time()
                self.animation.get_state()
            else:
                self.state = self.state_list[7]
                self.state_start = time.time()
                self.animation.get_state()
    
    def attack_1(self):
        if (time.time()-self.last_shot) >= 0.5:
            self.last_shot = time.time()
            target_list = []
            for entity in self.entity_list:
                if isinstance(entity, turret.Turret):
                    target_list.append(entity)
            
            if target_list:
                target = rd.choice(target_list)
                bullet = TITAN_Basic_Projectile(self.jeu, self.position[0] + self.rect.width//2, self.position[1] + self.rect.height//2, 25, 7.5, target, "titan_basic_projectile")
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
                bullet = TITAN_Missile(self.jeu, self.position[0] + self.rect.width//2, self.position[1] + self.rect.height//2, 100, 5, target, "titan_basic_projectile")
                self.entity_list.append(bullet)
                self.jeu.game_entities_list.append(bullet)
                self.projectile_list.append(bullet)

    def death_beam(self):
        if time.time() - self.state_start >= 3:
            if self.death_beam_projectile == None:
                self.death_beam_projectile = TITAN_Death_Beam(self)
            else:
                self.death_beam_projectile.update()
                if self.death_beam_projectile.is_dead:
                    self.death_beam_projectile = None

    #update methode call at each loop in the main game loop
    def move(self):
        
        self.update()
       
        
        if self.position[0] <= self.jeu.largeur_interface + 30:
            self.jeu.is_game_over = True
            self.is_dead = True

    def get_damage(self, degats, source=None):
        if self.state == self.state_list[4] or self.state == self.state_list[6] or self.state == self.state_list[7]:
            return 
        
        self.vie -= degats
        if self.vie <= 0:
            return True
        else:
            return False
    
    def death(self):
        if self.animation.is_animation_done and time.time() - self.state_start >= self.duration_dict[self.state]:
            self.is_dead = True
            self.jeu.is_game_win = True
    
    def collision_detection(self):
        cond = True
        for entity in self.entity_list:
            if isinstance(entity, turret.Turret):
                if self.is_colliding(entity):
                    self.colliding_damage(entity)
                cond = False
        return cond
    
    def collision_detection_infront(self):
        cond = True
        for entity in self.entity_list:
            if isinstance(entity, turret.Turret):
                if self.rect.colliderect((self.rect.x, entity.rect.y, entity.rect.width, entity.rect.height)) and entity.rect.x <= self.rect.x + self.rect.width:
                    cond = False
                    break
        return cond
    
    def is_colliding(self, cible):
        if self.rect.colliderect(cible.rect):
            return True
        else: return False
    
    def colliding_damage(self, cible):
        if time.time() - self.last_time_ability_dict['punch'] >= self.cooldown_dict['punch']:
            if cible.vie == cible.vie_max and cible.vie_max <= 250 and time.time() - cible.summon_time > 0.5:
                self.jeu.kamas += cible.prix
            cible.get_damage(250)
            self.last_time_ability_dict['punch'] = time.time()

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

        # Calcul de la largeur de la bbotse verte en fonction du pourcentage de vie
        largeur_bbotse_verte = round(self.rect.width * pourcentage_vie)

        # Calcul de la position de départ de la bbotse rouge
        position_bbotse_rouge = (self.rect.x + largeur_bbotse_verte, self.rect.y)

        # Dessin de la bbotse verte
        pg.draw.rect(fenetre, (0, 255, 0), (self.rect.x, self.rect.y, largeur_bbotse_verte, 5))  # Utilisez la largeur de la bbotse verte pour le troisième argument

        # Dessin de la bbotse rouge
        pg.draw.rect(fenetre, (255, 0, 0), (position_bbotse_rouge[0], position_bbotse_rouge[1], self.rect.width - largeur_bbotse_verte, 5))

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
        #pg.draw.rect(fenetre, (255,0,0), (self.rect.x, self.rect.y, self.rect.width, self.rect.height), 1)

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
        self.jeu.game_entities_list.append(others.Animation(self.jeu, 17, "projectiles/explosion_frames/frame_", "explosion", self.rect.x, self.rect.y, (250, 250), flip=False, loop= False, fps=120))

class TITAN_Death_Beam(pg.sprite.Sprite):
    def __init__(self, titan):
        super().__init__()
        self.titan = titan
        self.jeu = titan.jeu
        self.entity_list = titan.entity_list
        self.position = [self.titan.position[0]-100, self.titan.position[1]-80]
        self.is_dead = False
        self.fps = 50
        self.prop = 7
        self.rect = pg.Rect(self.position[0], self.position[1], 64, 64)
        self.animation_list= [others.Animation(self.jeu, 13, "projectiles/titan_projectile/death_beam/death_beam_spawn_frames/frame_", "death_beam", self.rect.x, self.rect.y, (64*self.prop, 64*self.prop), flip=True, loop= False, fps=self.fps)]
        self.jeu.game_entities_list.append(self.animation_list[0])
        
        self.damaged_turret = []
        self.target_turret = []
    
    
    def add_next_animation(self):
        current_animation = self.animation_list[-1]
        if current_animation.position[0] < self.jeu.largeur_interface + 250:
            if current_animation.current_frame == 12:
                self.is_dead = True
                return
            
        elif not self.is_dead and current_animation.current_frame == 0:
            
            self.animation_list.append(others.Animation(self.jeu, 13, "projectiles/titan_projectile/death_beam/death_beam_frames/frame_", "death_beam", current_animation.rect.x - 32*self.prop, self.rect.y, (32*self.prop, 64*self.prop), flip=True, loop= False, fps=self.fps))
            self.jeu.game_entities_list.append(self.animation_list[-1])
    
    def damage_turret(self):
        if self.target_turret != []:
            self.target_turret = list(set(self.target_turret))
            for turret in self.target_turret:
                if turret not in self.damaged_turret:
                    turret.get_damage(250)
            self.damaged_turret = self.target_turret[:]
            self.target_turret = []
    
    def turret_collision(self):
        for frame in self.animation_list:
            for entity in self.entity_list:
                if isinstance(entity, turret.Turret) and frame.rect.colliderect(entity.rect):
                    if frame.current_frame == 9 and frame.is_active:
                        if self.titan.rect.colliderect((self.titan.rect.x, entity.rect.y, entity.rect.width, entity.rect.height)):
                            self.target_turret.append(entity)
            if frame.current_frame == 9:
                frame.is_active = False
        self.damage_turret()
        
    def update(self):
        self.add_next_animation()
        self.turret_collision()
        
if __name__ == "__main__":
    import game
    jeu = game.Game()
    jeu.run()