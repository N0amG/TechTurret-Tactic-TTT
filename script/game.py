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
        
        self.file_manager = others.FileManager("settings/settings.json")
        
        self.is_info_menu_open = False
        
        # gestion de la souris
        self.mouse_manager = others.MouseManager(scene=self, scene_name="game")
        
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
        
        self.is_settings_menu_open = False
        
        self.quit = False
        
        self.next_wave_button_render() # appel de la méthode pour créer les attribut
        
        self.button_init()
        
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
        
        
        # Mise en place du shop
        # Kama = monnaie du jeu
        self.kamas = 300_000 # start a 300 ?
        self.last_kama_time = time.time()
        self.kama_image = pg.image.load("assets/images/others/kama.png")
        
        #score = score du joueur : nombre de kama accumulé
        self.score = 0
        
        self.liste_rect_shop = []
        self.render_shop_interface()
        self.red_cross_draw()
        
        # Font pour le rendu du texte de la monnaie
        self.font_kamas = pg.font.Font("assets/fonts\Peaberry-Font-v2.0\Peaberry-Font-v2.0\Peaberry Font Family\Peaberry Monospace\PeaberryMono.ttf", 30)
        # Surface pour le rendu de la monnaie (texte + image)
        self.kamas_surface = None
        
        # Gérer les vagues d'ennemis
        self.wave = 1
        
        self.file_manager.set_setting("total_games_played", self.file_manager.get_setting("total_games_played")+1)
        
        self.wave_ended = False
        self.bot_wave_spawner = enemy.Bot_Wave_Spawner(jeu=self)
        
        
        self.music_manager()
        
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
            
            if self.mouse_manager.mouse_selection == "pause":
                    self.paused = not self.paused
                    self.mouse_manager.mouse_selection = None
            else:   
                for event in pg.event.get():
                    
                    if event.type == pg.QUIT:
                        running = False
                        sys.exit()
                    
                    if event.type == self.menu.total_play_time_timer:
                        self.menu.add_play_time()
                        
                    if pg.mouse.get_pressed()[0] or pg.mouse.get_pressed()[2]:
                        if not self.is_game_over and not self.paused:
                            self.mouse_manager.update()
                        
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
                                                    self.kama_loot(entity)
                                                    entity.is_dead = True
                                                    self.game_entities_list.remove(entity)
                                                    break

                                
                                if self.wave_ended and self.mouse_manager.mouse_selection != None and self.mouse_manager.mouse_selection[0] == "next_wave_button":
                                    self.wave_ended = False
                                    self.wave += 1
                                    self.add_wave_to_stats()
                                    self.add_max_wave_to_stats()
                    
                    elif event.type == pg.KEYDOWN:
                        if event.key == pg.K_ESCAPE:
                            self.is_game_over = True
                            self.is_player_win = False
            
            if self.quit:
                running = False


            # Logique du jeu
            self.music_manager()
            
            if self.is_settings_menu_open:
                self.menu.settings_menu.run()
                self.is_settings_menu_open = False
                
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
                        self.add_killed_bot_to_stats()
                        
                    
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
    
    def first_music_init(self):
        pg.mixer.music.load("assets/musics/first_part.ogg")
        self.file_manager.set_setting("current_music", "first_part")
        if self.file_manager.get_setting('is_music_active'):
            pg.mixer.music.set_volume(self.file_manager.get_setting('music_volume'))
        else:
            pg.mixer.music.set_volume(0)
        pg.mixer.music.play(-1)
    
    def second_music_init(self):
        pg.mixer.music.load("assets/musics/second_part.ogg")
        self.file_manager.set_setting("current_music", "second_part")
        if self.file_manager.get_setting('is_music_active'):
            pg.mixer.music.set_volume(self.file_manager.get_setting('music_volume'))
        else:
            pg.mixer.music.set_volume(0)
        pg.mixer.music.play(-1)
    
    def boss_music_init(self):
        pg.mixer.music.load("assets/musics/boss.ogg")
        self.file_manager.set_setting("current_music", "boss")
        if self.file_manager.get_setting('is_music_active'):
            pg.mixer.music.set_volume(self.file_manager.get_setting('music_volume'))
        else:
            pg.mixer.music.set_volume(0)
        pg.mixer.music.play(-1)
    
    def music_manager(self):
        
        if self.paused:
            pg.mixer.music.pause()
            return
        else: 
            pg.mixer.music.unpause()
        
        if self.wave <= 2 and self.file_manager.get_setting('current_music') != "first_part" :
            return self.first_music_init()
        elif 2 < self.wave < 10 and self.file_manager.get_setting('current_music') != "second_part":
            return self.second_music_init()
        
        elif self.wave == 10 and self.file_manager.get_setting('current_music') != "boss":
            return self.boss_music_init()
        
        if self.file_manager.get_setting('is_music_active'):
            pg.mixer.music.set_volume(self.file_manager.get_setting('music_volume'))
        else:
            pg.mixer.music.set_volume(0)
            
    def add_killed_bot_to_stats(self):
        killed_bot = self.file_manager.get_setting("killed_bot")
        killed_bot += 1
        self.file_manager.set_setting("killed_bot", killed_bot)
        
    def add_wave_to_stats(self):
        wave = self.file_manager.get_setting("total_wave")
        wave += 1
        self.file_manager.set_setting("total_wave", wave)
    
    def add_max_wave_to_stats(self):
        max_wave = self.file_manager.get_setting("max_wave")
        if self.wave > max_wave:
            max_wave = self.wave
            self.file_manager.set_setting("max_wave", max_wave)
            
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

    def kama_loot(self, entity = None):
        # Donner 25 kamas toutes les 5  secondes
        if time.time() - self.last_kama_time >= 5 and self.wave_ended == False:
            self.kamas += 25
            self.last_kama_time = time.time()

        if entity is not None:
            if isinstance(entity, turret.Turret):
                self.kamas += entity.prix//2
                self.file_manager.set_setting("turrets_sold", self.file_manager.get_setting("turrets_sold")+1)
                
            elif isinstance(entity, enemy.Bot):
                self.kamas += entity.point//2
                self.score += entity.point
                self.add_best_score_to_stats()
            
    def add_best_score_to_stats(self):
        best_score = self.file_manager.get_setting("best_score")
        if self.score > best_score:
            best_score = self.score
            self.file_manager.set_setting("best_score", best_score)
        
    def next_wave_button_render(self):
        self.next_wave_button_image = pg.image.load("assets/images/others/next_wave_button.png")
        self.next_wave_button_image = pg.transform.scale(self.next_wave_button_image, (32*2, 24*2))
        self.next_wave_button_rect = self.next_wave_button_image.get_rect()
        self.next_wave_button_rect.bottomright = (self.taille_fenetre[0] - 50, self.taille_fenetre[1] - 10)
        self.fenetre.blit(self.next_wave_button_image, self.next_wave_button_rect)

    def button_init(self):
        square_size = (1000, 600)
        square_x = self.taille_fenetre[0] // 2 - square_size[0] // 2.25
        square_y = self.taille_fenetre[1] // 2 - square_size[1] // 2.25

        # Bouton pause
        self.pause_button = others.Button(x=self.taille_fenetre[0] - 60 , y=10, 
                                          image_normal = "assets\images\Button Kit/16x16 buttons Style 2 menu icons/16x16 Menu Buttons (116).png", 
                                          image_pressed="assets\images\Button Kit/16x16 buttons Style 2 menu icons/16x16 Menu Buttons (115).png", scale = (50, 50))
        
        self.play_button = others.Button(x=self.taille_fenetre[0] - 60 , y=10, 
                                         image_normal="assets\images\Button Kit/16x16 buttons Style 2 menu icons/16x16 Menu Buttons (106).png",
                                         image_pressed="assets\images\Button Kit/16x16 buttons Style 2 menu icons/16x16 Menu Buttons (105).png", scale = (50, 50))
        
        self.quit_button = others.Button(square_x + square_size[0]//2.1, square_y + square_size[1]//2, 
                                    "assets/images/Button Kit/32x16 buttons Style 1 with symbols/32x16 Button (19).png", 
                                    "assets/images/Button Kit/32x16 buttons Style 1 with symbols/32x16 Button (18).png")
        
        self.resume_button = others.Button(square_x + square_size[0]//4.5, square_y + square_size[1] //4, 
                                    "assets/images/Button Kit/32x16 buttons Style 1 with symbols/32x16 Button (59).png", 
                                    "assets/images/Button Kit/32x16 buttons Style 1 with symbols/32x16 Button (58).png")
        
        self.info_button = others.Button(square_x + square_size[0]//4.5, square_y + square_size[1]//2, 
                                    "assets/images/Button Kit/32x16 buttons Style 1 with symbols/32x16 Button (17).png", 
                                    "assets/images/Button Kit/32x16 buttons Style 1 with symbols/32x16 Button (16).png")
        
        self.settings_button = others.Button(square_x + square_size[0]//2.1, square_y + square_size[1] //4,
                                      "assets/images/Button Kit/32x16 buttons Style 1 with symbols/32x16 Button (61).png",
                                      "assets/images/Button Kit/32x16 buttons Style 1 with symbols/32x16 Button (60).png")

        
    def pause_menu(self):
        square_size = (1000, 600)
        square_x = self.taille_fenetre[0] // 2 - square_size[0] // 2.25
        square_y = self.taille_fenetre[1] // 2 - square_size[1] // 2.25

        surface = pg.Surface((square_size[0], square_size[1]))
        surface.fill((0, 0, 0))
        surface.set_alpha(200)

        self.fenetre.blit(surface, (square_x, square_y))
        
        
        self.quit_button.render(self.fenetre)
        
        self.resume_button.render(self.fenetre)

        
        self.info_button.render(self.fenetre)
        
        if self.is_info_menu_open:
            self.is_info_menu_open = False
            self.info_menu()
        
        if self.pause_button.state == "pressed":
            self.play_button.state = "pressed"
        else:
            self.play_button.state = "normal"
            
        self.play_button.render(self.fenetre)
        
        self.settings_button.render(self.fenetre)
        
    def info_menu(self):
        self.menu.info_menu.run()
    
    def render(self):
        # Dessiner sur la fenêtre
        self.fenetre.blit(self.fond_ecran, (self.largeur_interface, 0))  # Dessine l'image du fond d'écran aux coordonnées (0, 0)
        
        self.render_shop_interface()
        self.red_cross_draw()
                
        self.render_wave()
        
        
        
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
        else:
            self.pause_button.render(self.fenetre)
        # Mettre à jour l'affichage
        pg.display.flip()

if __name__ == '__main__':
    import menu
    menu = menu.StartMenu()
    jeu = Game(menu)
    jeu.run()
    menu.run()