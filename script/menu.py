import pygame as pg
import sys

import game
import others
import time

class StartMenu:
    
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
        
        self.mouse_manager = others.MouseManager(scene = self, scene_name="start_menu")
        
        self.file_manager = others.FileManager("settings\settings.json")
        
        self.quit = False
        
        self.button_init()

        self.is_sound_active = True
        
        self.is_music_active = True
        
        self.info_menu = InfoMenu(self)
        
        self.is_info_menu_open = False
        
        self.settings_menu = SettingsMenu(self)
        
        self.total_play_time_timer = pg.USEREVENT + 1
        
        pg.time.set_timer(self.total_play_time_timer, 1000)
        
        self.is_settings_menu_open = False
        
        self.stats_initialization()
        
        self.music_init()
        
    def run(self):
        running = True
        while running:
            self.clock.tick(self.fps)
            # Gérer les événements
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                    sys.exit()
                
                if event.type == self.total_play_time_timer:
                    self.add_play_time()     
            # Gérer les changements
            self.update()
            # Afficher le menu
            self.render()
            
            if self.is_info_menu_open:
                self.info_menu.run()
                self.is_info_menu_open = False
            
            self.music_manager()
            
            if self.is_settings_menu_open:
                self.settings_menu.run()
                self.is_settings_menu_open = False
            if self.quit:
                running = False

        pg.quit()
        sys.exit()
    
    def music_manager(self):
        pg.mixer.music.unpause()
        if self.file_manager.get_setting('current_music') != "menu":
            return self.music_init()
            
        if not self.file_manager.get_setting('is_music_active'):
            pg.mixer.music.set_volume(0)
        else:
            pg.mixer.music.set_volume(self.file_manager.get_setting('music_volume'))

    def music_init(self):
        pg.mixer.init()
        pg.mixer.music.load("assets/musics/menu.ogg")
        self.file_manager.set_setting('current_music', "menu")
        if self.file_manager.get_setting('is_music_active'):
            pg.mixer.music.set_volume(self.file_manager.get_setting('music_volume'))
        else:
            pg.mixer.music.set_volume(0)
        pg.mixer.music.play(-1)
    
    def add_play_time(self):
        
        play_time = self.file_manager.get_setting('total_play_time')
        play_time += 1
        self.file_manager.set_setting('total_play_time', round(play_time))
        
    def stats_initialization(self):
        if self.file_manager.get_setting('is_this_first_game') == True:
            
            self.file_manager.set_setting('is_this_first_game', False)
            self.file_manager.set_setting('total_play_time', 0)
            self.file_manager.set_setting('total_games_played', 0)
            self.file_manager.set_setting('killed_bot', 0)
            self.file_manager.set_setting('turrets_built', 0)
            self.file_manager.set_setting('turrets_sold', 0)
            self.file_manager.set_setting('sound_volume', 0.5)
            self.file_manager.set_setting('music_volume', 0.5)
            self.file_manager.set_setting('is_sound_active', True)
            self.file_manager.set_setting('is_music_active', True)
            self.file_manager.set_setting('max_wave', 0)
            self.file_manager.set_setting('best_score', 0)
            self.file_manager.set_setting('total_wave', 0)
            self.file_manager.set_setting('difficulty', "normal")
            self.file_manager.set_setting('ressource_pack', "default")
            
    def button_init(self):
        
        self.play_button = others.Button(self.taille_fenetre[0]//3, self.taille_fenetre[1]//1.5, 
                                  "assets/images/Button Kit/32x16 buttons Style 1 with symbols/32x16 Button (9).png", 
                                  "assets/images/Button Kit/32x16 buttons Style 1 with symbols/32x16 Button (8).png")
        self.info_button = others.Button(self.taille_fenetre[0]//3, self.taille_fenetre[1]//1.2,
                                  "assets/images/Button Kit/32x16 buttons Style 1 with symbols/32x16 Button (17).png", 
                                  "assets/images/Button Kit/32x16 buttons Style 1 with symbols/32x16 Button (16).png")
        self.quit_button = others.Button(self.taille_fenetre[0]//2, self.taille_fenetre[1]//1.2, 
                                  "assets/images/Button Kit/32x16 buttons Style 1 with symbols/32x16 Button (19).png", 
                                  "assets/images/Button Kit/32x16 buttons Style 1 with symbols/32x16 Button (18).png")
        
        self.settings_button = others.Button(self.taille_fenetre[0]//2, self.taille_fenetre[1]//1.5,
                                      "assets/images/Button Kit/32x16 buttons Style 1 with symbols/32x16 Button (61).png",
                                      "assets/images/Button Kit/32x16 buttons Style 1 with symbols/32x16 Button (60).png")
        
        
        self.credit_button = others.Button(self.taille_fenetre[0]-75, 30, 
                                  "assets\images\Button Kit/16x16 buttons Style 2 menu icons/16x16 Menu Buttons (26).png", 
                                  "assets\images\Button Kit/16x16 buttons Style 2 menu icons/16x16 Menu Buttons (25).png", scale=(50,50))

        self.stats_button = others.Button(self.taille_fenetre[0]-75, 90,
                                    "assets\images\Button Kit/16x16 buttons Style 2 menu icons/16x16 Menu Buttons (96).png", 
                                    "assets\images\Button Kit/16x16 buttons Style 2 menu icons/16x16 Menu Buttons (95).png", scale=(50,50))
        
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
        self.info_button.render(self.fenetre)
        self.settings_button.render(self.fenetre)
        
        self.credit_button.render(self.fenetre)
        
        self.stats_button.render(self.fenetre)

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
    
    def get_sound_state(self):
        return self.file_manager.get_setting('is_sound_active')

    def get_music_state(self):
        return self.file_manager.get_setting('is_music_active')
    
class InfoMenu:
    def __init__(self, previous_scene):
        pg.init()
        
        self.previous_scene = previous_scene
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
                
        self.mouse_manager = others.MouseManager(scene = self, scene_name="info_menu")
        
        self.file_manager = others.FileManager("settings\settings.json")
        
        self.quit = False
        
        self.button_init()
        
        self.logo_title()
        
        self.state = "info" # info, credit, stats

        self.scroll_pos = self.fenetre.get_height()
        
        self.scroll_speed = 0.5

    def run(self):
        running = True
        while running:
            self.clock.tick(self.fps)
            # Gérer les événements
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                    sys.exit()
                if event.type == self.previous_scene.total_play_time_timer:
                        self.previous_scene.add_play_time()
                if event.type == pg.MOUSEBUTTONDOWN:
                    if event.button == 4:
                        if self.scroll_pos < 120:
                            self.scroll_pos += 10
                    if event.button == 5:
                        if self.scroll_pos > -300:
                            self.scroll_pos -= 10
                    
            # Gérer les changements
            self.update()
            # Afficher le menu
            self.render()

            
            if self.quit:
                running = False
                self.quit = False

    def update(self):
        self.mouse_manager.update()
        self.is_sound_active = self.previous_scene.get_sound_state()
        self.is_music_active = self.previous_scene.get_music_state()


    def button_init(self):
        self.quit_button = others.Button(self.taille_fenetre[0]//1.2, self.taille_fenetre[1]//1.2, 
                                  "assets/images/Button Kit/32x16 buttons Style 1 with symbols/32x16 Button (19).png", 
                                  "assets/images/Button Kit/32x16 buttons Style 1 with symbols/32x16 Button (18).png")
        
        self.scroll_speed_button = others.Button(self.taille_fenetre[0]//1.08, self.taille_fenetre[1]//1.5,
                                    "assets\images\Button Kit/16x16 buttons Style 2 menu icons/16x16 Menu Buttons (100).png", 
                                    "assets\images\Button Kit/16x16 buttons Style 2 menu icons/16x16 Menu Buttons (99).png", scale=(50,50))
        
        self.is_scroll_speed_button_active = True
    

    def logo_title(self):
        
        font = pg.font.Font("assets/fonts/Peaberry-Font-v2.0/Peaberry-Font-v2.0/Peaberry Font Family/Peaberry Monospace/PeaberryMono.ttf", 50)
        self.logo_text = font.render("TechTurretTactic", True, (255, 255, 255))

        
        self.logo_frame = pg.image.load("assets/images/Button Kit/32x16 buttons Style 1 with symbols/32x16 Button (1 - Frame).png")
        self.logo_frame = pg.transform.scale(self.logo_frame, (self.logo_text.get_width() + 70, self.logo_text.get_height() + 50))
        
        self.logo_background = pg.Surface((self.logo_frame.get_width() -30, self.logo_frame.get_height()-25))
        # Remplissez cette surface avec du noir
        self.logo_background.fill((0, 0, 0))
        
        pg.draw.rect(self.fenetre, (0,0,0), (0, 0, self.fenetre.get_width(), self.fenetre.get_height()//5))

        self.fenetre.blit(self.logo_background,(self.taille_fenetre[0]//2.5 - self.logo_text.get_width()//4, 35))
        self.fenetre.blit(self.logo_frame, (self.taille_fenetre[0]//2.5 - self.logo_text.get_width()//4 - 35, 20))
        self.fenetre.blit(self.logo_text, (self.taille_fenetre[0]//2.5 - self.logo_text.get_width()//4, 50))

        
    def sub_title(self):
            font = pg.font.Font("assets/fonts/Peaberry-Font-v2.0/Peaberry-Font-v2.0/Peaberry Font Family/Peaberry Monospace/PeaberryMono.ttf", 40)
            self.sub_text = font.render("Information :", True, (255, 255, 255))
            
            self.fenetre.blit(self.sub_text, (self.taille_fenetre[0]//2.2 - self.sub_text.get_width()//4, 130))

    def information_text(self):
        """
        This function renders and displays informational text on the game screen.

        It creates multiple text objects using a specified font and color,
        then positions them on the screen using the `fenetre.blit` method.
        """

        font = pg.font.Font("assets/fonts/Peaberry-Font-v2.0/Peaberry-Font-v2.0/Peaberry Font Family/Peaberry Monospace/PeaberryMono.ttf", 30)
        text_color = (255, 255, 255)  # White color for text

        # Informative text with clear and concise wording
        info_text1 = font.render("TechTurretTactic: A Tower Defense Strategy Game", True, text_color)
        info_text2 = font.render("Place turrets to defend your base from enemy bots.", True, text_color)
        info_text3 = font.render("Tip:  Delete turrets for half cost recovery!", True, text_color)
        info_text4 = font.render("Left click to select and interact with elements.", True, text_color)
        info_text5 = font.render("Hold left click for continuous interaction (be careful!).", True, text_color)
        info_text6 = font.render("Right click to deselect elements or cancel actions.", True, text_color)
        info_text7 = font.render("Good Luck !", True, text_color) 

        self.fenetre.blit(info_text1, (20, 220))
        self.fenetre.blit(info_text2, (20, 270))
        self.fenetre.blit(info_text3, (20, 350))
        self.fenetre.blit(info_text4, (20, 430))
        self.fenetre.blit(info_text5, (20, 480))
        self.fenetre.blit(info_text6, (20, 530))
        self.fenetre.blit(info_text7, (20, 620))

    def info_text_render(self):
        self.logo_title()
        self.sub_title()
        self.information_text()
    
    def info_button_render(self):
        # Dessiner le bouton
        self.quit_button.render(self.fenetre)
        

    def credit_text(self):
        credits = """
        Credits:
        
        Team:
        
        Development: Triskel
        
        Musician: Sakey
        
        Sound Designer: Oopally
        
        Graphics: Lucas / Triskel
        
        
        
        External (Open Source Assets):
        
        Elthen: Boss animations
        
        Animated enemy pack: Mounir Tohami
        
        Pixel Font: Peaberry 
        
        
        And more for little animations and sprites.


        Alpha Tester List:

        Leo
        Elouann
        Assia
        Lucas
        Remi
        Mey
        Manon
        Tom
        
        
        
        
        
        
        
        
        
        Thanks to all of you for your help and support <3
        
        """
        # Generate the credit text
        credit_text = credits

        # Split the credit text into lines
        lines = credit_text.split('\n')

        # Load the font
        font = pg.font.Font("assets/fonts/Peaberry-Font-v2.0/Peaberry-Font-v2.0/Peaberry Font Family/Peaberry Monospace/PeaberryMono.ttf", 30)
        text_color = (255, 255, 255)
        
        # Render each line and blit it to the screen
        for i, line in enumerate(lines):
            text_surface = font.render(line, True, text_color)
            self.fenetre.blit(text_surface, (50, self.scroll_pos + i * 30))

        # Scroll the text up
        if self.scroll_pos > -len(lines) * (30-9):
            self.scroll_pos -= self.scroll_speed
    
    def credit_text_render(self):
        self.credit_text()
        self.logo_title()
        
    def switch_to_info(self):
        self.state = "info"
    
    def credit_music_init(self):
        pg.mixer.music.load("assets/musics/credits.ogg")
        self.file_manager.set_setting('current_music', "credits")

        self.credit_music_start = time.time()
        pg.mixer.music.set_volume(0)
        
        pg.mixer.music.play()            
    
    def credit_music(self):
        if self.file_manager.get_setting('current_music') != "credits":
            return self.credit_music_init()
        else:
            if not self.file_manager.get_setting('is_music_active'):
                pg.mixer.music.set_volume(0)
            else:
                if time.time() - self.credit_music_start < 3:
                    volume = (time.time() - self.credit_music_start)/2 / 3
                    volume = max(0.0, min(self.file_manager.get_setting('music_volume'), volume))
                    pg.mixer.music.set_volume(volume)
                else :
                    pg.mixer.music.set_volume(self.file_manager.get_setting('music_volume'))
                
    def switch_to_credit(self):
        self.state = "credit"
        self.scroll_pos = self.fenetre.get_height()
        self.scroll_speed = 0.5
        self.is_scroll_speed_button_active = True
        self.credit_music_init()
    
    def credit_button_render(self):
        # Dessiner le bouton
        self.quit_button.render(self.fenetre)
        if self.scroll_pos > -self.fenetre.get_height()*1.5:
            self.scroll_speed_button.render(self.fenetre)
        else:
            self.is_scroll_speed_button_active = False
    
    def switch_to_stats(self):
        self.state = "stats"
        self.scroll_pos = self.logo_frame.get_rect().y + self.logo_frame.get_rect().height + 30

    def stats_text(self):
        total_seconds = self.file_manager.get_setting('total_play_time')
        hours, remainder = divmod(total_seconds, 3600)
        minutes, _ = divmod(remainder, 60)

        if hours:
            time_str = f"{hours}h {minutes}m"
        else:
            time_str = f"{minutes}m"

        stats = f"""

        Total play time: {time_str}
        
        Total games played: {self.file_manager.get_setting('total_games_played')}
        
        Max wave reached: {self.file_manager.get_setting('max_wave')}
        
        Total wave finish: {self.file_manager.get_setting('total_wave')}
        
        Best score: {self.file_manager.get_setting('best_score')}
        
        Killed bots: {self.file_manager.get_setting('killed_bot')}
        
        Turrets built: {self.file_manager.get_setting('turrets_built')}
        
        Turrets sold: {self.file_manager.get_setting('turrets_sold')}
        
        """
        # Generate the credit text
        stats_text = stats

        # Split the credit text into lines
        lines = stats_text.split('\n')
        
        # Load the font
        font = pg.font.Font("assets/fonts/Peaberry-Font-v2.0/Peaberry-Font-v2.0/Peaberry Font Family/Peaberry Monospace/PeaberryMono.ttf", 30)
        text_color = (255, 255, 255)
        
        square_size = (1000, 600)
        square_x = self.taille_fenetre[0] // 2 - square_size[0] // 1.75
        square_y = self.taille_fenetre[1] // 2 - square_size[1] // 2.25

        surface = pg.Surface((square_size[0], square_size[1]))
        surface.fill((0, 0, 0))
        surface.set_alpha(100)

        self.fenetre.blit(surface, (square_x, square_y))
        
        # Render each line and blit it to the screen
        for i, line in enumerate(lines):
            text_surface = font.render(line, True, text_color)
            self.fenetre.blit(text_surface, (50, self.scroll_pos + i * 30))

    
    def stats_sub_title(self):
            font = pg.font.Font("assets/fonts/Peaberry-Font-v2.0/Peaberry-Font-v2.0/Peaberry Font Family/Peaberry Monospace/PeaberryMono.ttf", 40)
            self.sub_text = font.render("Statistics :", True, (255, 255, 255))
            
            pg.draw.rect(self.fenetre, (0,0,0), (self.sub_text.get_rect().x , 130, self.fenetre.get_width(), 40))
            self.fenetre.blit(self.sub_text, (self.taille_fenetre[0]//2.2 - self.sub_text.get_width()//4, 130))

    
    def stats_text_render(self):
        self.stats_text()
        self.logo_title()
        self.stats_sub_title()
        
    def quit_interface(self):
        self.quit = True

    
    def render(self):
        self.fenetre.fill((0,0,0))
        
        if self.state == "info":
            self.info_text_render()
            self.info_button_render()
        
        elif self.state == "stats":
            self.stats_text_render()
            self.quit_button.render(self.fenetre)
        
        else:
            self.credit_text_render()
            self.credit_button_render()
            self.credit_music()
                        
        pg.display.flip()

class SettingsMenu:
    
    def __init__(self, previous_scene):
        pg.init()
        
        # Créer la fenêtre
        self.fond_ecran = pg.image.load("assets/images/others/background.png")  

        self.previous_scene = previous_scene
        
        # Définir la taille de la fenêtre
        largeur = self.fond_ecran.get_width() -100
        hauteur = self.fond_ecran.get_height()
        self.taille_fenetre = (largeur, hauteur)
        self.fenetre = pg.display.set_mode(self.taille_fenetre)
        pg.display.set_caption("TTT - TechTurret Tactics")

        # Définir les FPS (images par seconde)
        self.fps = 75
        self.clock = pg.time.Clock()
        
        self.mouse_manager = others.MouseManager(scene = self, scene_name="settings_menu")
        
        self.file_manager = others.FileManager("settings\settings.json")
        
        self.quit = False
        
        self.text_render()
        
        self.button_init()
        
        self.is_sound_active = self.get_sound_state()
        
        self.is_music_active = self.get_music_state()
        
    def run(self):
        running = True
        while running:
            self.clock.tick(self.fps)
            # Gérer les événements
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                    sys.exit()
                
                if event.type == self.previous_scene.total_play_time_timer:
                        self.previous_scene.add_play_time()   
            # Gérer les changements
            self.update()
            # Afficher le menu
            self.render()
            
            pg.mixer.music.pause()
            
            if not self.file_manager.get_setting('is_music_active'):
                pg.mixer.music.set_volume(0)
            else:
                pg.mixer.music.set_volume(self.file_manager.get_setting('music_volume'))
                
            if self.quit:
                running = False
                self.quit = False
                
    
    def update(self):
        self.mouse_manager.update()
        self.is_sound_active = self.get_sound_state()
        self.is_music_active = self.get_music_state()
    
    def quit_interface(self):
        self.quit = True
    
    
    def text_render(self):
        font = pg.font.Font("assets/fonts/Peaberry-Font-v2.0/Peaberry-Font-v2.0/Peaberry Font Family/Peaberry Monospace/PeaberryMono.ttf", 40)
        text_color = (255, 255, 255)
        
        sound_text = font.render(f"Sound : {int(self.file_manager.get_setting('sound_volume')*10)}", True, text_color)
        
        music_text = font.render(f"Music : {int(self.file_manager.get_setting('music_volume')*10)}", True, text_color)
        
        self.sound_text_rect = sound_text.get_rect()
        self.sound_text_rect.topleft = (self.taille_fenetre[0]//2.45, self.taille_fenetre[1]//4)
        
        self.music_text_rect = music_text.get_rect()
        self.music_text_rect.topleft = (self.taille_fenetre[0]//2.45, self.taille_fenetre[1]//3)
        
        self.fenetre.blit(sound_text, self.sound_text_rect)
        self.fenetre.blit(music_text, self.music_text_rect)
        
    def button_init(self):
        
        
        self.quit_button = others.Button(self.taille_fenetre[0]/1.18, self.taille_fenetre[1]/1.18, 
                                  "assets/images/Button Kit/32x16 buttons Style 1 with symbols/32x16 Button (19).png", 
                                  "assets/images/Button Kit/32x16 buttons Style 1 with symbols/32x16 Button (18).png")


        # arrow for up and down sound
        self.lower_sound_button = others.Button(self.sound_text_rect.x - 75, self.sound_text_rect.y-8,
                                    "assets\images\Button Kit/16x16 buttons Style 2 menu icons/16x16 Menu Buttons (110).png", 
                                    "assets\images\Button Kit/16x16 buttons Style 2 menu icons/16x16 Menu Buttons (109).png", (50,50))
        
        self.upper_sound_button = others.Button(self.sound_text_rect.x + 270, self.sound_text_rect.y-8,
                                    "assets\images\Button Kit/16x16 buttons Style 2 menu icons/16x16 Menu Buttons (106).png", 
                                    "assets\images\Button Kit/16x16 buttons Style 2 menu icons/16x16 Menu Buttons (105).png", (50,50))
        
        self.mute_demute_button_pos = (self.upper_sound_button.rect.x + self.upper_sound_button.rect.width + 20, self.upper_sound_button.rect.y)
        
        self.mute_sound_button = others.Button(self.mute_demute_button_pos[0], self.mute_demute_button_pos[1],
                                    "assets\images\Button Kit/16x16 buttons Style 2 menu icons/16x16 Menu Buttons (8).png", 
                                    "assets\images\Button Kit/16x16 buttons Style 2 menu icons/16x16 Menu Buttons (7).png", (50,50))
        
        self.demute_sound_button = others.Button(self.mute_demute_button_pos[0], self.mute_demute_button_pos[1],
                                    "assets\images\Button Kit/16x16 buttons Style 2 menu icons/16x16 Menu Buttons (6).png", 
                                    "assets\images\Button Kit/16x16 buttons Style 2 menu icons/16x16 Menu Buttons (5).png", (50,50))
        
        # arrow for up and down music
        self.lower_music_button = others.Button(self.music_text_rect.x - 75, self.music_text_rect.y-8,
                                    "assets\images\Button Kit/16x16 buttons Style 2 menu icons/16x16 Menu Buttons (110).png", 
                                    "assets\images\Button Kit/16x16 buttons Style 2 menu icons/16x16 Menu Buttons (109).png", (50,50))
        
        self.upper_music_button = others.Button(self.music_text_rect.x + 270, self.music_text_rect.y-8,
                                    "assets\images\Button Kit/16x16 buttons Style 2 menu icons/16x16 Menu Buttons (106).png", 
                                    "assets\images\Button Kit/16x16 buttons Style 2 menu icons/16x16 Menu Buttons (105).png", (50,50))
        
        
        self.mute_demute_button_pos = (self.upper_music_button.rect.x + self.upper_music_button.rect.width + 20, self.upper_music_button.rect.y)
        
        self.demute_music_button = others.Button(self.mute_demute_button_pos[0], self.mute_demute_button_pos[1],
                                    "assets\images\Button Kit/16x16 buttons Style 2 menu icons/16x16 Menu Buttons (118).png",
                                    "assets\images\Button Kit/16x16 buttons Style 2 menu icons/16x16 Menu Buttons (117).png", (50,50))
        
        self.mute_music_button = others.Button(self.mute_demute_button_pos[0], self.mute_demute_button_pos[1],
                                    "assets\images\Button Kit/16x16 buttons Style 2 menu icons/16x16 Menu Buttons (4).png",
                                    "assets\images\Button Kit/16x16 buttons Style 2 menu icons/16x16 Menu Buttons (3).png", (50,50))
        
    def button_render(self):
        # Dessiner le bouton
        self.quit_button.render(self.fenetre)
        
        self.lower_sound_button.render(self.fenetre)
        self.upper_sound_button.render(self.fenetre)
        
        self.lower_music_button.render(self.fenetre)
        self.upper_music_button.render(self.fenetre)
        
        if self.is_sound_active:
            self.mute_sound_button.render(self.fenetre)
        else:
            self.demute_sound_button.render(self.fenetre)
        
        if self.is_music_active:
            self.mute_music_button.render(self.fenetre)
        else:
            self.demute_music_button.render(self.fenetre)
        
    
    def sound_volume_up(self):
        volume = self.file_manager.get_setting('sound_volume')
        if volume < 1:
            volume += 0.1
        self.file_manager.set_setting('sound_volume', round(volume,2))
        self.text_render()
        
    def sound_volume_down(self):
        volume = self.file_manager.get_setting('sound_volume')
        if volume > 0:
            volume -= 0.1
        self.file_manager.set_setting('sound_volume', round(volume,2))
        self.text_render()

    def music_volume_up(self):
        volume = self.file_manager.get_setting('music_volume')
        if volume < 1:
            volume += 0.1
        self.file_manager.set_setting('music_volume', round(volume,2))
                
        self.text_render()
        
    def music_volume_down(self):
        volume = self.file_manager.get_setting('music_volume')
        if volume > 0:
            volume -= 0.1
        self.file_manager.set_setting('music_volume', round(volume,2))
        
        self.text_render()

    def get_sound_state(self):
        return self.file_manager.get_setting('is_sound_active')

    def get_music_state(self):
        return self.file_manager.get_setting('is_music_active')

    def logo_title(self):
        
        font = pg.font.Font("assets/fonts/Peaberry-Font-v2.0/Peaberry-Font-v2.0/Peaberry Font Family/Peaberry Monospace/PeaberryMono.ttf", 50)
        self.logo_text = font.render("TechTurretTactic", True, (255, 255, 255))

        
        self.logo_frame = pg.image.load("assets/images/Button Kit/32x16 buttons Style 1 with symbols/32x16 Button (1 - Frame).png")
        self.logo_frame = pg.transform.scale(self.logo_frame, (self.logo_text.get_width() + 70, self.logo_text.get_height() + 50))
        
        self.logo_background = pg.Surface((self.logo_frame.get_width() -30, self.logo_frame.get_height()-25))
        # Remplissez cette surface avec du noir
        self.logo_background.fill((0, 0, 0))
        
        self.fenetre.blit(self.logo_background,(self.taille_fenetre[0]//2.5 - self.logo_text.get_width()//4, 35))
        self.fenetre.blit(self.logo_frame, (self.taille_fenetre[0]//2.5 - self.logo_text.get_width()//4 - 35, 20))
        self.fenetre.blit(self.logo_text, (self.taille_fenetre[0]//2.5 - self.logo_text.get_width()//4, 50))
        
    def sub_title(self):
            font = pg.font.Font("assets/fonts/Peaberry-Font-v2.0/Peaberry-Font-v2.0/Peaberry Font Family/Peaberry Monospace/PeaberryMono.ttf", 40)
            self.sub_text = font.render("Settings :", True, (255, 255, 255))
            
            self.fenetre.blit(self.sub_text, (self.taille_fenetre[0]//2.2 - self.sub_text.get_width()//4, 130))

    def render(self):
        self.fenetre.fill((50,50,50))
        
        self.logo_title()
        
        self.text_render()
        
        self.button_render()
        
        pg.display.flip()

        
    
if __name__ == '__main__':
    menu = StartMenu()

    menu.run()
    