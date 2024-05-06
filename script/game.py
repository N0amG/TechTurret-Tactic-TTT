import pygame as pg
import turret
import others
import enemy
import time


class Game:
    
    def __init__(self):
        
        # Initialisation de pg
        pg.init()
        
        # Définir les FPS (images par seconde)
        self.fps = 90
        self.clock = pg.time.Clock()

        # Charger l'image du fond d'écran
        self.fond_ecran = pg.image.load("assets/images/others/background.png")  

        # Définir la taille de la fenêtre
        largeur = self.fond_ecran.get_width() - 100
        hauteur = self.fond_ecran.get_height()
        self.taille_fenetre = (largeur, hauteur)

        # Créer la fenêtre
        self.fenetre = pg.display.set_mode(self.taille_fenetre)
        pg.display.set_caption("TTT - TechTurret Tactics")

        self.matrice_tourelle = [[0 for j in range(10)] for i in range(5)]
        
        self.matrice_bot = [[0 for j in range(2)] for i in range(5)]
        
        self.game_entities_list = []
        
        # Décalages entre chaque colonne et chaque ligne
        taille_colonne = 81
        taille_ligne = 101
        
        self.largeur_interface = 175
        
        decalage_x = 160
        decalage_y = 295 + self.largeur_interface
        
        self.liste_tourelle = [("Turret", 100), ("Laser Turret", 200), ("Shield", 250), ("Plasma Turret",350), ("Omni Turret", 450), ("BlackHole Turret", 500),] #("AntiMatter Turret", 750)
        
        self.paused = False
        
        self.next_wave_button_render() # appel de la méthode pour créer les attribut
        
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
        
        # Tracking de la souris
        self.previous_mouse_selection = None
        self.mouse_selection = None
        
        
        # Mise en place du shop
        # Kama = monnaie du jeu
        self.kamas = 5_000_000_000
        self.last_kama_time = time.time()
        self.kama_image = pg.image.load("assets/images/others/kama.png")
        
        self.liste_rect_shop = []
        self.render_shop_interface()
        self.red_cross_draw()
        
        # Font pour le rendu du texte de la monnaie
        self.font_kamas = pg.font.Font(None, 30)
        # Surface pour le rendu de la monnaie (texte + image)
        self.kamas_surface = None
        
        # Gérer les vagues d'ennemis
        self.wave = 1
        
        self.wave_ended = False
        self.bot_wave_spawner = enemy.Bot_Wave_Spawner(jeu=self)
        
        #test et placement des éléments    
        self.game_entities_list.append(turret.Turret_selection(self, self.matrice_tourelle[0][0][1], self.matrice_tourelle[0][0][0], "Turret"))
        #self.game_entities_list.append(turret.Plasma_Turret(self, self.matrice_tourelle[2][1][1], self.matrice_tourelle[2][1][0]))
        #[self.game_entities_list.append(turret.Basic_Turret(self ,self.matrice_tourelle[2][i][1], self.matrice_tourelle[2][i][0])) for i in range(4,5)]

        self.bot_wave_spawner.manual_spawn(self.matrice_bot[3][0][1], self.matrice_bot[1][0][0], "titan")
        
        #self.bot_wave_spawner.manual_spawn(self.matrice_bot[2][1][1], self.matrice_bot[2][1][0], "basic")
        self.debug_bot_timer = None
        #self.debug_bot_timer = time.time()

    def run(self):
        # Boucle principale du jeu
        running = True
        while running:
            # Gestion des événements
            for event in pg.event.get():
                
                if event.type == pg.QUIT:
                    running = False
                    
                elif event.type == pg.MOUSEBUTTONDOWN:
                    
                    self.mouse_detection()
                    #print(f"{self.previous_mouse_selection=}, {self.mouse_selection=}")
                    if event.button == 1:
                        
                        if self.previous_mouse_selection is not None:
                            
                            if self.mouse_selection[0] == "matrix":
                                
                                if self.previous_mouse_selection[0] == "shop":
                                    turret_index = self.previous_mouse_selection[1]
                                    if self.liste_tourelle[turret_index][0] != "":
                                        if self.kamas >= self.liste_tourelle[turret_index][1]:
                                            x = self.matrice_tourelle[self.mouse_selection[2]][self.mouse_selection[1]][1]
                                            y = self.matrice_tourelle[self.mouse_selection[2]][self.mouse_selection[1]][0]
                                            cond = True
                                            for entity in self.game_entities_list:
                                                # Si l'endroit n'est pas djà occupé par une tourelle
                                                if isinstance(entity, turret.Turret) and entity.rect.collidepoint(x, y):
                                                    cond = False
                                                    break
                                            if cond:
                                                self.kamas -= self.liste_tourelle[self.previous_mouse_selection[1]][1]
                                                tourelle = turret.Turret_selection(jeu = self, x=x , y=y, name = self.liste_tourelle[turret_index][0])
                                                self.game_entities_list.append(tourelle)
                                                
                                
                                elif self.previous_mouse_selection[0] == "red_cross":
                                    # Récupérer les coordonnées de la tourelle à supprimer
                                    x = self.matrice_tourelle[self.mouse_selection[2]][self.mouse_selection[1]][1]
                                    y = self.matrice_tourelle[self.mouse_selection[2]][self.mouse_selection[1]][0]
                                    # Parcourir la liste des entités du jeu
                                    for entity in self.game_entities_list:
                                        # Si l'entité est une tourelle et qu'elle est à la position de la tourelle à supprimer
                                        if isinstance(entity, turret.Turret) and entity.rect.collidepoint(x,y):
                                            # Supprimer la tourelle de la liste des entités du jeu
                                            self.kamas += entity.prix // 2
                                            entity.is_dead = True
                                            self.game_entities_list.remove(entity)
                                            break
                        
                            elif self.mouse_selection[0] == "next_wave_button":
                                self.wave_ended = False
                                self.wave += 1
                                
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        self.is_game_over = True
                        self.is_player_win = False
                    
                    elif event.key == pg.K_LCTRL:  # Si la touche Ctrl gauche est pressée
                        self.paused = not self.paused  # Inverse l'état de pause
                        print("paused")
                            


            # Logique du jeu

            # Mise à jour du jeu
            if not self.paused:
                self.update()
                
                # Affichage du jeu
            self.render()

        # Quitter pg
        pg.quit()

    def update(self):
        if not self.is_game_over:
            
            self.kama_loot()
                      
            # Réapparition manuel d'un bot pour débuger la tourelle BlackHole
            #---------------------------------------------
            if self.debug_bot_timer is not None:
                if time.time() - self.debug_bot_timer >= 0 :
                    self.bot_wave_spawner.manual_spawn(self.matrice_bot[2][1][1], self.matrice_bot[2][0][0], "kamikaze")
                    self.debug_bot_timer = None
            #---------------------------------------------
            
            cond = True
            for entity in self.game_entities_list:
                if entity.is_dead:
                    if isinstance(entity, enemy.Bot):
                        self.kama_loot(entity)
                        cond = False
                    self.game_entities_list.remove(entity)
                    
                else:
                    if isinstance(entity, turret.Turret):
                        projectile = entity.shoot()
                        if projectile is not None:
                            self.game_entities_list.append(projectile)
                            
                    elif isinstance(entity, turret.Projectile):
                        entity.move()
                        
                                    
                    elif isinstance(entity, enemy.Bot):
                        entity.move()

                    elif isinstance(entity, others.Animation):
                        entity.update()
                        
            if not self.wave_ended and cond:
                if self.bot_wave_spawner.update() == 3:
                    self.wave_ended = True

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
        font = pg.font.Font(None, 50)
        text = font.render(f"Wave {self.wave}", True, (255, 255, 255))
        text_rect = text.get_rect(topright=(self.taille_fenetre[0] - 10, 10))
        self.fenetre.blit(text, text_rect)

    def render_game_over(self):
        font = pg.font.Font(None, 100)
        text = font.render("Game Over", True, (255, 0, 0))
        text_rect = text.get_rect(center=(self.taille_fenetre[0] // 2, self.taille_fenetre[1] // 2 - 150))
        self.fenetre.blit(text, text_rect)

    def render_pause(self):
        font = pg.font.Font(None, 100)
        text = font.render("Pause", True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.taille_fenetre[0] // 2, self.taille_fenetre[1] // 2 - 150))
        self.fenetre.blit(text, text_rect)

    def render_shop_interface(self):
        pg.draw.rect(self.fenetre, (68,95,144), (0, 0, self.largeur_interface, self.taille_fenetre[1]))
        
        font = pg.font.Font(None, 27)
        
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
        if time.time() - self.last_kama_time >= 30 and self.wave_ended == False:
            self.kamas += 50
            self.last_kama_time = time.time()

        # Donner la moitié des PV d'un monstre tué en kamas
        if enemy is not None:
            self.kamas += enemy.point

    def next_wave_button_render(self):
        self.next_wave_button_image = pg.image.load("assets/images/others/next_wave_button.png")
        self.next_wave_button_image = pg.transform.scale(self.next_wave_button_image, (32*2, 24*2))
        self.next_wave_button_rect = self.next_wave_button_image.get_rect()
        self.next_wave_button_rect.bottomright = (self.taille_fenetre[0] - 50, self.taille_fenetre[1] - 10)
        self.fenetre.blit(self.next_wave_button_image, self.next_wave_button_rect)

    def mouse_detection(self):
        # Récupération des coordonnées de la souris
        mouse_x, mouse_y = pg.mouse.get_pos()

        # Récupération de la position de la souris dans la matrice
        mouse_matrix_x = (mouse_x - (295+self.largeur_interface -81//2)) // 81
        mouse_matrix_y = (mouse_y - (160 -101//2)) // 101
        
        # Vérification que la souris est bien dans la matrice
        if mouse_matrix_y >= 0 and mouse_matrix_y < 5 and mouse_matrix_x >= 0 and mouse_matrix_x < 10:
            #print(mouse_matrix_y, mouse_matrix_x)
            self.previous_mouse_selection = self.mouse_selection
            self.mouse_selection = ("matrix", mouse_matrix_x, mouse_matrix_y)
            return mouse_matrix_x, mouse_matrix_y
        
        elif 50 < mouse_x < self.largeur_interface - 50 and mouse_y > self.taille_fenetre[1] - 87:
            self.previous_mouse_selection = self.mouse_selection
            self.mouse_selection = ("red_cross", None)

        elif self.wave_ended and self.next_wave_button_rect.collidepoint(mouse_x, mouse_y):
            self.previous_mouse_selection = self.mouse_selection
            self.mouse_selection = ("next_wave_button", None)
    
        else:
            for i in range(len(self.liste_rect_shop)):
                if self.liste_rect_shop[i].collidepoint(mouse_x, mouse_y):
                    #print("shop", i)
                    self.previous_mouse_selection = self.mouse_selection
                    self.mouse_selection = ("shop", i)
                    return i  # Retourne le mot "shop" et l'index de la tourelle
            
            return None

    def render(self):
        # Dessiner sur la fenêtre
        self.fenetre.blit(self.fond_ecran, (self.largeur_interface, 0))  # Dessine l'image du fond d'écran aux coordonnées (0, 0)

        self.render_wave()
        
        # Affichage du "Game Over"
        if self.is_game_over:
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

            if self.wave_ended and cond:
                self.next_wave_button_render()
            
        if self.paused:
            self.render_pause()
        # Mettre à jour l'affichage
        pg.display.flip()


if __name__ == "__main__":
    game = Game()
    game.run()