import pygame as pg
import sys

import game
import others

class Menu:
    
    def __init__(self):
        pg.init()
        
        # Créer la fenêtre
        self.fond_ecran = pg.image.load("assets/images/others/background.png")  

        # Définir la taille de la fenêtre
        largeur = self.fond_ecran.get_width() -100
        hauteur = self.fond_ecran.get_height()
        self.taille_fenetre = (largeur, hauteur)
        self.fenetre = pg.display.set_mode(self.taille_fenetre)
        pg.display.set_caption("TTT - TechTurret Tactics")

        # Définir les FPS (images par seconde)
        self.fps = 75
        self.clock = pg.time.Clock()
        
        self.mouse_manager = others.MouseManager(scene = self, scene_name="menu")
        
        self.file_manager = others.FileManager("settings\settings.json")
        
        self.quit = False
        
        self.button_init()

        self.is_sound_active = True
        
        self.is_music_active = True
        
    def run(self):
        running = True
        while running:
            self.clock.tick(self.fps)
            # Gérer les événements
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                        
            # Gérer les changements
            self.update()
            # Afficher le menu
            self.render()
            
            if self.quit:
                running = False

        pg.quit()
        sys.exit()
        
    def button_init(self):
        self.play_button = others.Button(self.taille_fenetre[0]//3, self.taille_fenetre[1]//1.5, 
                                  "assets/images/Button Kit/32x16 buttons Style 1 with symbols/32x16 Button (9).png", 
                                  "assets/images/Button Kit/32x16 buttons Style 1 with symbols/32x16 Button (8).png")
        self.quit_button = others.Button(self.taille_fenetre[0]//2, self.taille_fenetre[1]//1.5, 
                                  "assets/images/Button Kit/32x16 buttons Style 1 with symbols/32x16 Button (19).png", 
                                  "assets/images/Button Kit/32x16 buttons Style 1 with symbols/32x16 Button (18).png")
        

    def logo_title(self):
        
        font = pg.font.Font("assets/fonts/Peaberry-Font-v2.0/Peaberry-Font-v2.0/Peaberry Font Family/Peaberry Monospace/PeaberryMono.ttf", 50)
        self.logo_text = font.render("TechTurretTactic", True, (255, 255, 255))

        
        self.logo_frame = pg.image.load("assets/images/Button Kit/32x16 buttons Style 1 with symbols/32x16 Button (1 - Frame).png")
        self.logo_frame = pg.transform.scale(self.logo_frame, (self.logo_text.get_width() + 70, self.logo_text.get_height() + 50))
        
        self.logo_background = pg.Surface((self.logo_frame.get_width() -30, self.logo_frame.get_height()-20))
        # Remplissez cette surface avec du noir
        self.logo_background.fill((0, 0, 0))
        
        self.fenetre.blit(self.logo_background,(self.taille_fenetre[0]//2.5 - self.logo_text.get_width()//4, self.taille_fenetre[1]//3 - 20))
        self.fenetre.blit(self.logo_frame, (self.taille_fenetre[0]//2.5 - self.logo_text.get_width()//4 - 35, self.taille_fenetre[1]//3 - 30))
        self.fenetre.blit(self.logo_text, (self.taille_fenetre[0]//2.5 - self.logo_text.get_width()//4, self.taille_fenetre[1]//3))
    
    def button_render(self):
        # Dessiner le bouton
        self.play_button.render(self.fenetre)
        self.quit_button.render(self.fenetre)

    def quit_game(self):
        self.quit = True
        
    def update(self):
        self.mouse_manager.update()
        for event in pg.event.get():
            if self.play_button.handle_event(event):
                self.start_game()

    
    def render(self):
        self.fenetre.fill((50,50,50))
        self.logo_title()
        self.button_render()
        pg.display.flip()
        
    def start_game(self):
        # Créer une nouvelle instance de Game et la lancer
        jeu = game.Game(menu=self)
        jeu.run()  # Supposons que vous ayez une méthode run dans votre classe Game



if __name__ == '__main__':
    menu = Menu()
    menu.run()
    