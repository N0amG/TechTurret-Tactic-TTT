import pygame as pg
import sys

import turret
import others
import enemy
import time


class Game:
    
    def __init__(self, menu):
        
        # Initialisation de pg
        pg.init()
        
        self.menu = menu
        
        # Définir les FPS (images par seconde)
        self.fps = 75
        self.clock = pg.time.Clock()

        # Charger l'image du fond d'écran
        self.fond_ecran = pg.image.load("assets/images/others/background.png")  

        # Définir la taille de la fenêtre
        largeur = self.fond_ecran.get_width() - 100
        hauteur = self.fond_ecran.get_height()
        self.taille_fenetre = (largeur, hauteur)

        # Créer la fenêtre
        self.fenetre = pg.display.set_mode(self.taille_fenetre)
        pg.display.set_caption("TTT - TechTurretTactic")

        self.matrice_tourelle = [[0 for j in range(10)] for i in range(5)]
        
        self.matrice_bot = [[0 for j in range(2)] for i in range(5)]
        
        self.game_entities_list = []
        
        # Décalages entre chaque colonne et chaque ligne
        taille_colonne = 81
        taille_ligne = 101
        
        self.largeur_interface = 175
        
        decalage_x = 160
        decalage_y = 295 + self.largeur_interface
        
        self.liste_tourelle = [("Basic Turret", 100), ("Laser Turret", 200), ("Shield", 250), ("Plasma Turret",350), ("Omni Turret", 450), ("BlackHole Turret", 500),] #("AntiMatter Turret", 750)
        self.liste_tourelle_image = [pg.transform.scale(pg.image.load(f"assets/images/turrets/{tourelle[0].lower().replace(' ', '_')}.png"), (75, 100)).convert_alpha() for tourelle in self.liste_tourelle]
        
        self.paused = False
        
        self.quit = False
        
        self.next_wave_button_render() # appel de la méthode pour créer les attribut
        
        self.pause_menu()
        
        # Créer une boucle pour générer les coordonnées de chaque élément
        for i in range(5):
            
            for j in range(10):
                # Calculer les coordonnées en utilisant les décalages
                coord_x = decalage_x + i * taille_ligne
                coord_y = decalage_y + j * taille_colonne

                self.matrice_tourelle[i][j] = (coord_x, coord_y)
            
            for k in range(2):
                coord_x = decalage_x + (i) * taille_ligne
                coord_y = decalage_y + (k+10) * taille_colonne
                self.matrice_bot[i][k] = (coord_x, coord_y)
        
        
        # Condition de victoire et de défaites
        self.is_game_over = False
        self.is_player_win = False
        
        
        # gestion de la souris
        self.mouse_manager = others.MouseManager(scene=self, scene_name="game")
        
        
        # Mise en place du shop
        # Kama = monnaie du jeu
        self.kamas = 300_000 # start a 300 ?
        self.last_kama_time = time.time()
        self.kama_image = pg.image.load("assets/images/others/kama.png")
        
        self.liste_rect_shop = []
        self.render_shop_interface()
        self.red_cross_draw()
        
        # Font pour le rendu du texte de la monnaie
        self.font_kamas = pg.font.Font("assets/fonts\Peaberry-Font-v2.0\Peaberry-Font-v2.0\Peaberry Font Family\Peaberry Monospace\PeaberryMono.ttf", 30)
        # Surface pour le rendu de la monnaie (texte + image)
        self.kamas_surface = None
        
        # Bouton pause
        self.pause_button = others.Button(x=self.taille_fenetre[0] - 60 , y=10, 
                                          image_normal = "assets\images\Button Kit/16x16 buttons Style 2 menu icons/16x16 Menu Buttons (116).png", 
                                          image_pressed="assets\images\Button Kit/16x16 buttons Style 2 menu icons/16x16 Menu Buttons (115).png", scale = (50, 50))
        
        # Gérer les vagues d'ennemis
        self.wave = 1
        
        self.wave_ended = False
        self.bot_wave_spawner = enemy.Bot_Wave_Spawner(jeu=self)
                
        #test et placement des éléments    
        #[[self.game_entities_list.append(turret.Turret_selection(self ,self.matrice_tourelle[j][i][1], self.matrice_tourelle[j][i][0], "Omni Turret")) for i in range(0,8)] for j in range(0,5)]
        #[[self.game_entities_list.append(turret.Turret_selection(self ,self.matrice_tourelle[j][i][1], self.matrice_tourelle[j][i][0], "Plasma Turret")) for i in range(7,8)] for j in range(0,5)]
        #self.game_entities_list.append(turret.Turret_selection(self ,self.matrice_tourelle[2][1][1], self.matrice_tourelle[2][1][0], "BlackHole Turret"))
        
        #self.bot_wave_spawner.manual_spawn(self.matrice_bot[1][1][1], self.matrice_bot[1][1][0], "incinerator")
        
        self.debug_bot_timer = None
        #self.debug_bot_timer = time.time()

    def run(self):
        # Boucle principale du jeu
        running = True
        while running:
            
            # Limiter le nombre d'images par seconde
            self.clock.tick(self.fps)
            #print(self.clock.get_fps())
            # Gestion des événements
            self.mouse_manager.update()
            
            if self.mouse_manager.mouse_selection == "Pause":
                    self.paused = not self.paused
                    self.mouse_manager.mouse_selection = None
            else:   
                for event in pg.event.get():
                    
                    if event.type == pg.QUIT:
                        running = False
                        sys.exit()
                        
                    if pg.mouse.get_pressed()[0] or pg.mouse.get_pressed()[2]:
                        if not self.is_game_over and not self.paused:
                            
                        
                        #print(f"{self.mouse_manager.previous_mouse_selection=}, {self.mouse_manager.mouse_selection=}")
                            
                            if not self.paused:
                                if self.mouse_manager.previous_mouse_selection is not None:
                                    
                                    if self.mouse_manager.mouse_selection != None and self.mouse_manager.mouse_selection[0] == "matrix":
                                        
                                        if self.mouse_manager.previous_mouse_selection[0] == "shop":
                                            turret_index = self.mouse_manager.previous_mouse_selection[1]
                                            if self.liste_tourelle[turret_index][0] != "":
                                                if self.kamas >= self.liste_tourelle[turret_index][1]:
                                                    x = self.matrice_tourelle[self.mouse_manager.mouse_selection[2]][self.mouse_manager.mouse_selection[1]][1]
                                                    y = self.matrice_tourelle[self.mouse_manager.mouse_selection[2]][self.mouse_manager.mouse_selection[1]][0]
                                                    cond = True
                                                    for entity in self.game_entities_list:
                                                        # Si l'endroit n'est pas djà occupé par une tourelle
                                                        if isinstance(entity, turret.Turret) and entity.rect.collidepoint(x, y):
                                                            cond = False
                                                            break
                                                    if cond:
                                                        self.kamas -= self.liste_tourelle[self.mouse_manager.previous_mouse_selection[1]][1]
                                                        tourelle = turret.Turret_selection(jeu = self, x=x , y=y, name = self.liste_tourelle[turret_index][0])
                                                        self.game_entities_list.append(tourelle)
                                                        
                                        
                                        elif self.mouse_manager.previous_mouse_selection[0] == "red_cross":
                                            # Récupérer les coordonnées de la tourelle à supprimer
                                            x = self.matrice_tourelle[self.mouse_manager.mouse_selection[2]][self.mouse_manager.mouse_selection[1]][1]
                                            y = self.matrice_tourelle[self.mouse_manager.mouse_selection[2]][self.mouse_manager.mouse_selection[1]][0]
                                            # Parcourir la liste des entités du jeu
                                            for entity in self.game_entities_list:
                                                # Si l'entité est une tourelle et qu'elle est à la position de la tourelle à supprimer
                                                if isinstance(entity, turret.Turret) and entity.rect.collidepoint(x,y):
                                                    # Supprimer la tourelle de la liste des entités du jeu
                                                    self.kamas += entity.prix // 2
                                                    entity.is_dead = True
                                                    self.game_entities_list.remove(entity)
                                                    break
                                print(f" sortie souris : {self.mouse_manager.mouse_selection}")
                                if self.wave_ended and self.mouse_manager.mouse_selection != None and self.mouse_manager.mouse_selection[0] == "next_wave_button":
                                    
                                    self.wave_ended = False
                                    self.wave += 1
                                        
                    elif event.type == pg.KEYDOWN:
                        if event.key == pg.K_ESCAPE:
                            self.is_game_over = True
                            self.is_player_win = False
                    
            if self.quit:
                running = False


            # Logique du jeu

            # Mise à jour du jeu
            if not self.paused:
                self.update()
                
                # Affichage du jeu
            self.render()

    def update(self):
        if not self.is_game_over and not self.paused:
            
            self.kama_loot()
                      
            # Réapparition manuel chronométré d'un bot pour débuggage et test
            #---------------------------------------------
            if self.debug_bot_timer is not None:
                if time.time() - self.debug_bot_timer >= 0 :
                    self.bot_wave_spawner.spawn(self.matrice_bot[2][1][1], self.matrice_bot[2][0][0], "kamikaze")
                    self.debug_bot_timer = None
            #---------------------------------------------

            for entity in self.game_entities_list:
                if entity.is_dead:
                    if isinstance(entity, enemy.Bot):
                        self.kama_loot(entity)
                    
                    self.game_entities_list.remove(entity)
                    
                else:
                    if isinstance(entity, turret.Turret):
                        projectile = entity.shoot()
                        if projectile is not None:
                            self.game_entities_list.append(projectile)
                            
                    elif isinstance(entity, turret.Projectile) or isinstance(entity, enemy.Bullet):
                        entity.move()
                        
                                    
                    elif isinstance(entity, enemy.Bot):
                        entity.move()

                    elif isinstance(entity, others.Animation):
                        entity.update()
                    
            if not self.wave_ended:
                self.bot_wave_spawner.update()
            
            else:
                if self.bot_wave_spawner.boss_wave == self.wave:
                    self.is_player_win = True
                    self.is_game_over = True
                    
    def render_debug(self):
        for i in range(5):
            for j in range(10):
                pg.draw.circle(self.fenetre, (0, 255, 0), (self.matrice_tourelle[i][j][1], self.matrice_tourelle[i][j][0]), 10)
        
        for i in range(5):
            for j in range(2):
                pg.draw.circle(self.fenetre, (255, 0, 0), (self.matrice_bot[i][j][1], self.matrice_bot[i][j][0]), 10)

        # Dessin de la grille
        for y in range(5):
            for x in range(10):
                rect = pg.Rect(x*81+295+self.largeur_interface -81//2, y*101+160 -101//2, 81, 101)
                pg.draw.rect(self.fenetre, (255, 255, 255), rect, 1)
                    
        #for entity in self.game_entities_list : print(entity.name)

    def render_wave(self):
        font = pg.font.Font("assets/fonts\Peaberry-Font-v2.0\Peaberry-Font-v2.0\Peaberry Font Family\Peaberry Monospace\PeaberryMono.ttf", 50)
        text = font.render(f"Wave {self.wave}", True, (255, 255, 255))
        text_rect = text.get_rect(topright=(self.taille_fenetre[0]//1.75, 10))
        self.fenetre.blit(text, text_rect)

    def render_game_over(self):
        font = pg.font.Font("assets/fonts\Peaberry-Font-v2.0\Peaberry-Font-v2.0\Peaberry Font Family\Peaberry Monospace\PeaberryMono.ttf", 100)
        text = font.render("Game Over", True, (255, 0, 0))
        text_rect = text.get_rect(center=(self.taille_fenetre[0] // 2, self.taille_fenetre[1] // 2 - 150))
        self.fenetre.blit(text, text_rect)

    def render_game_win(self):
        font = pg.font.Font("assets/fonts\Peaberry-Font-v2.0\Peaberry-Font-v2.0\Peaberry Font Family\Peaberry Monospace\PeaberryMono.ttf", 100)
        text = font.render("Win !!!", True, (0, 255, 0))
        text_rect = text.get_rect(center=(self.taille_fenetre[0] // 2, self.taille_fenetre[1] // 2 - 150))
        self.fenetre.blit(text, text_rect)
        
    def render_pause(self):
        font = pg.font.Font("assets/fonts\Peaberry-Font-v2.0\Peaberry-Font-v2.0\Peaberry Font Family\Peaberry Monospace\PeaberryMono.ttf", 100)
        text = font.render("Pause", True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.taille_fenetre[0] // 2 + 30, self.taille_fenetre[1] // 2 - 200))
        self.fenetre.blit(text, text_rect)

    def render_shop_interface(self):
        pg.draw.rect(self.fenetre, (68,95,144), (0, 0, self.largeur_interface, self.taille_fenetre[1]))
        
        font = pg.font.Font("assets/fonts\Peaberry-Font-v2.0\Peaberry-Font-v2.0\Peaberry Font Family\Peaberry Monospace\PeaberryMono.ttf", 15)
        
        for i in range(len(self.liste_tourelle)):
            rect = pg.draw.rect(self.fenetre, (255, 255, 255), (10, 10 + i * 83, 155, 75))
            self.liste_rect_shop.append(rect)
            tourelle = self.liste_tourelle[i]
            if tourelle[0] != "":
                text = font.render(tourelle[0], True, (0, 0, 0))
                text_rect = text.get_rect(center=(self.largeur_interface // 2, 40 + i * 83))
                self.fenetre.blit(text, text_rect)
                
                # Affichage du prix de la tourelle
                text_prix = font.render(str(tourelle[1]), True, (0, 0, 0))
                text_prix_rect = text_prix.get_rect(center=(self.largeur_interface // 2, 65 + i * 83))
                self.fenetre.blit(text_prix, text_prix_rect)

    def red_cross_draw(self):
        # Chargement de l'image "red_cross.png"
        red_cross_image = pg.image.load("assets/images/others/red_cross.png")
        red_cross_image = pg.transform.scale(red_cross_image, (75, 75))
        red_cross_rect = red_cross_image.get_rect()
        red_cross_rect.bottomleft = (50, self.taille_fenetre[1] - 10)
        self.fenetre.blit(red_cross_image, red_cross_rect)

    def update_kamas_display(self):
        # Mise à jour de la surface de la monnaie seulement si la valeur change
        current_kamas_surface = self.render_kamas_surface()
        if self.kamas_surface != current_kamas_surface:
            self.kamas_surface = current_kamas_surface

    def render_kamas_surface(self):
        # Création d'une surface pour le rendu de la monnaie (texte + image)
        surface = pg.Surface((200, 50), pg.SRCALPHA)
        surface.fill((0, 0, 0, 0))  # Fond transparent

        # Affichage du texte de la monnaie
        text = self.font_kamas.render(str(self.kamas), True, (0, 255, 255))
        text_rect = text.get_rect(topleft=(10, 10))
        surface.blit(text, text_rect)

        # Affichage de l'image de la monnaie
        surface.blit(self.kama_image, (text_rect.right + 5, 5))

        return surface

    def kama_loot(self, enemy = None):
        # Donner 50 kamas toutes les minutes
        if time.time() - self.last_kama_time >= 5 and self.wave_ended == False:
            self.kamas += 25
            self.last_kama_time = time.time()

        if enemy is not None:
            self.kamas += enemy.point

    def next_wave_button_render(self):
        self.next_wave_button_image = pg.image.load("assets/images/others/next_wave_button.png")
        self.next_wave_button_image = pg.transform.scale(self.next_wave_button_image, (32*2, 24*2))
        self.next_wave_button_rect = self.next_wave_button_image.get_rect()
        self.next_wave_button_rect.bottomright = (self.taille_fenetre[0] - 50, self.taille_fenetre[1] - 10)
        self.fenetre.blit(self.next_wave_button_image, self.next_wave_button_rect)

    def pause_menu(self):
        square_size = (1000, 600)
        square_x = self.taille_fenetre[0] // 2 - square_size[0] // 2.25
        square_y = self.taille_fenetre[1] // 2 - square_size[1] // 2.25

        surface = pg.Surface((square_size[0], square_size[1]))
        surface.fill((0, 0, 0))
        surface.set_alpha(200)

        
        self.sound_button = others.Button(square_x + square_size[0]//1.1, square_y + 50, 
                                  "assets\images\Button Kit/16x16 buttons Style 2 menu icons/16x16 Menu Buttons (6).png", 
                                  "assets\images\Button Kit/16x16 buttons Style 2 menu icons/16x16 Menu Buttons (5).png", (50,50))
        
        self.quit_button = others.Button(square_x + square_size[0]//2.75, square_y + square_size[1] - 100, 
                                  "assets/images/Button Kit/32x16 buttons Style 1 with symbols/32x16 Button (19).png", 
                                  "assets/images/Button Kit/32x16 buttons Style 1 with symbols/32x16 Button (18).png")

        
        self.sound_button.rect.x, self.sound_button.rect.y = square_x + square_size[0]//1.1, square_y + 50
        self.quit_button.rect.x, self.quit_button.rect.y = square_x + square_size[0]//2.75, square_y + square_size[1] - 100
        
        self.fenetre.blit(surface, (square_x, square_y))
        self.sound_button.render(self.fenetre)
        self.quit_button.render(self.fenetre)
        
    
    def render(self):
        # Dessiner sur la fenêtre
        self.fenetre.blit(self.fond_ecran, (self.largeur_interface, 0))  # Dessine l'image du fond d'écran aux coordonnées (0, 0)
        
        self.render_shop_interface()
        self.red_cross_draw()
                
        self.render_wave()
        
        self.pause_button.render(self.fenetre)
        
        # Affichage du "Game Over"
        if self.is_game_over:
            if self.is_player_win:
                self.render_game_win()
            else:
                self.render_game_over()

            
        else:
            #self.render_debug()
            
            # Affichage de la monnaie            
            self.update_kamas_display()
            self.fenetre.blit(self.kamas_surface, (self.largeur_interface // 2 + 200, 30))
            
            # Met à jour l'affichage
            cond = True
            for entity in self.game_entities_list:
                entity.render(self.fenetre)
                if not entity.is_dead and isinstance(entity, enemy.Bot):
                    cond = False

            if self.wave_ended and cond and not self.is_player_win:
                self.next_wave_button_render()
            
            if not self.paused:
                self.mouse_manager.previous_selection_on_mouse()
                
            
        if self.paused:
            self.pause_menu()
            self.render_pause()
        # Mettre à jour l'affichage
        pg.display.flip()

if __name__ == '__main__':
    import menu
    menu = menu.Menu()
    jeu = Game(menu)
    jeu.run()