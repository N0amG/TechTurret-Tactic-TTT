import pygame as pg
import json

class Animation(pg.sprite.Sprite):
    # path : str -> exemple : 'enemy/drone/frame_'
    def __init__(self, jeu, nb_images : int, path : str, name : str, x : int, y : int , proportion : tuple, flip: bool, fps : int = 70 ,
                starting_frame : int = 0, loop : bool = True, duration : int = 0, reverse : bool = False, entity = None):
        super().__init__()
        self.jeu = jeu
        
        self.name = name
        self.entity = entity
        self.proportion = proportion
        self.fps = fps
        self.flip = flip
        self.loop = loop
        self.reverse = reverse
        
        self.current_frame = starting_frame
        self.last_update = pg.time.get_ticks()
        self.nb_images = nb_images
        self.get_images(nb_images, path)
        self.image = self.images[self.current_frame]
        self.rect = self.image.get_rect()
        
        self.rect.x = x
        self.rect.y = y
        self.position = (x, y)
        
        self.duration = duration
        self.start_timer = pg.time.get_ticks()
        
        if name == "death_beam":
            self.is_active = True
        
        self.is_dead = False
        

    def get_images(self, nb_images, path) -> list:
        images = []
        for i in range(nb_images):
            image = pg.transform.scale(pg.image.load(f'assets/images/{path}{i}.png'), self.proportion)
            if self.flip:
                image = pg.transform.flip(image, True, False)
            
            images.append(image.convert_alpha())
        if self.reverse:
            self.images = images[::-1]
            return
        self.images = images
        
    
    def update(self):
        now = pg.time.get_ticks()
        if self.entity != None:
            if self.entity.is_dead:
                self.is_dead = True
                return 
        if now - self.last_update > 9000 // self.fps:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.images)
            self.image = self.images[self.current_frame]
            
        if self.loop == False:
            if self.duration != 0:
                if pg.time.get_ticks() - self.start_timer > self.duration * 1000:
                    self.is_dead = True
            else:
                if self.current_frame == self.nb_images - 1:
                    #évite les artefacts visuels
                    self.is_dead = True

    
    def render(self, fenetre):

        # hitbox
        #pg.draw.rect(fenetre, (255,0,0), (self.rect.x, self.rect.y, self.rect.width, self.rect.height), 1)
        
        if self.name == "StealthBlack_Bot":
            if self.entity.stealth:
                if self.entity.rect.x >= self.jeu.matrice_tourelle[4][0][0]:
                    self.image = self.image.convert_alpha()
                    self.image.set_alpha(70)
        
        fenetre.blit(self.image, self.rect)


class TITAN_Animation(pg.sprite.Sprite):
    def __init__(self, jeu, path : str, name : str, x : int, y : int , proportion : tuple, flip: bool, fps : int = 70 ,
                starting_frame : int = 0, loop : bool = True, duration : int = 0, reverse : bool = False, entity = None):
        self.jeu = jeu
        self.path = path
        
        self.name = name
        self.entity = entity
        self.titan = entity
        
        self.proportion = proportion
        self.fps = fps
        self.flip = flip
        self.loop = loop
        
        self.loop_count = 0
        self.loop_number = 0
        self.stay_at_last_frame = False
        self.is_animation_done = False
        
        self.starting_frame_of_loop= 0
        self.ending_frame_of_loop = 0
        
        self.reverse = reverse
        self.current_frame = starting_frame
        self.last_update = pg.time.get_ticks()
        self.position = (x, y)
        self.duration = duration
        self.start_timer = pg.time.get_ticks()
        self.is_dead = False
        
        self.state_list = self.titan.state_list
        self.state = self.titan.state
        self.state_images = {"moving" : 4, "standing" : 4, "attack_1" : 7, "attack_2" : 8,
                                    "shield" : 10, "death_beam" : 5, "damaged" : 5, "death" : 10}
        self.state_images = {key:self.get_images(self.state_images[key], key) for key in self.state_images.keys()}
        self.image = self.state_images["moving"][0]
        
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = self.titan.animation_position
        
        

    def get_images(self, nb_images, state) -> list:
        images = []
        for i in range(nb_images):
            image = pg.transform.scale(pg.image.load(f'assets/images/enemy/titan/titan_{state}_frames/frame_{i}.png'), self.proportion)
            if self.flip:
                image = pg.transform.flip(image, True, False)
            
            images.append(image.convert_alpha())
        if self.reverse:
            return images[::-1]
        return images

    def get_state(self):
        if self.titan.state != self.state:
            self.state = self.titan.state
            self.current_frame = 0
            self.loop_count = 0
            self.loop_number = 0
            self.image = self.state_images[self.state][self.current_frame]
            self.is_animation_done = False
            self.get_state_properties()
        
    def get_state_properties(self):
        
        if self.state == "moving":
            self.starting_frame_of_loop = 0
            self.ending_frame_of_loop = 0
        
        elif self.state == "standing":
            self.starting_frame_of_loop = 0
            self.ending_frame_of_loop = 0
        
        elif self.state == "attack_1":
            self.starting_frame_of_loop = 2
            self.ending_frame_of_loop = 6
        
        elif self.state == "attack_2":
            self.starting_frame_of_loop = 0
            self.ending_frame_of_loop = 0
            
        elif self.state == "shield":
            self.starting_frame_of_loop = len(self.state_images[self.state]) - 3
            self.ending_frame_of_loop = 0
        
        elif self.state == "death_beam":
            self.starting_frame_of_loop = len(self.state_images[self.state]) - 2
            self.ending_frame_of_loop = 0
        
        elif self.state == "damaged":
            self.starting_frame_of_loop = 0
            self.ending_frame_of_loop = 0
            self.loop_number = self.titan.phase+1

        elif self.state == "death":
            self.starting_frame_of_loop = len(self.state_images[self.state]) - 2
            self.loop_number = 3
            self.ending_frame_of_loop = 0
            self.stay_at_last_frame = True
        
    
    def update(self):
        
        now = pg.time.get_ticks()
        self.get_state()
        self.rect.x, self.rect.y = self.titan.animation_position
        
        if self.entity != None:
            if self.entity.is_dead:
                self.is_dead = True
                return
        
        if now - self.last_update > 9000 // self.fps:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.state_images[self.state])
            
            if self.current_frame + self.starting_frame_of_loop == self.starting_frame_of_loop:
                self.loop_count += 1
                
            if self.starting_frame_of_loop > 0:     
                if self.current_frame == 0:
                    self.current_frame = self.starting_frame_of_loop

            if self.ending_frame_of_loop > 0:
                if self.current_frame == self.ending_frame_of_loop:
                    self.current_frame = self.starting_frame_of_loop

            if self.loop_number > 0:
                if self.loop_count >= self.loop_number:
                    self.stay_at_last_frame = True
                    self.is_animation_done = True

                if self.stay_at_last_frame:
                    if self.loop_count >= self.loop_number:
                        self.current_frame = len(self.state_images[self.state]) - 1
                        
            self.image = self.state_images[self.state][self.current_frame]
            
        if self.loop == False:
            if self.duration != 0:
                if pg.time.get_ticks() - self.start_timer > self.duration * 1000:
                    self.is_dead = True
            else:
                if self.current_frame == len(self.state_images[self.state]) - 1:
                    #évite les artefacts visuels
                    self.is_dead = True
        
        #print(self.loop_number, self.loop_count)

    def render(self, fenetre):
        # hitbox
        #pg.draw.rect(fenetre, (255,0,0), (self.rect.x, self.rect.y, self.rect.width, self.rect.height), 1)
        fenetre.blit(self.image, self.rect)


class MouseManager:
    def __init__(self, scene, scene_name):
        self.scene = scene
        self.scene_name = scene_name
        
        self.play_cond = False
        self.quit_cond = False
        self.pause_cond = False
        self.sound_cond = False
        self.music_cond = False
        
        self.resume_cond = False
        self.info_cond = False
        self.credit_cond = False
        self.stats_cond = False
        
        self.settings_cond = False
        self.lower_sound_cond = False
        self.upper_sound_cond = False
        self.lower_music_cond = False
        self.upper_music_cond = False
        
        
        self.mouse_position = pg.mouse.get_pos()
        self.mouse_button_state = None
        self.last_mouse_event = None
        
        self.mouse_selection = None
        self.previous_mouse_selection = None #('matrix', 0, 0)

    def update(self):
        self.mouse_position = pg.mouse.get_pos()
        self.mouse_button_state = pg.mouse.get_pressed()
        self.last_mouse_event = pg.mouse.get_rel()

        self.handle_mouse_event()

        if self.mouse_button_state[2]:
            self.previous_mouse_selection = None #('matrix', 0, 0)
            self.mouse_selection = None

        #print(self.previous_mouse_selection, self.mouse_selection)
        
        
    def game_mouse_manager(self):
        if self.mouse_button_state[0]:
            
            if self.scene.pause_button.rect.collidepoint(self.mouse_position):
                self.scene.pause_button.state = "pressed"
                self.pause_cond = True
            else:
                self.scene.pause_button.state = "normal"
                self.pause_cond = False
                
            if not self.scene.paused:
                # Récupération de la position de la souris dans la matrice
                mouse_matrix_x = (self.mouse_position[0] - (295+self.scene.largeur_interface -81//2)) // 81
                mouse_matrix_y = (self.mouse_position[1] - (160 -101//2)) // 101
                
                # Vérification que la souris est bien dans la matrice
                if mouse_matrix_y >= 0 and mouse_matrix_y < 5 and mouse_matrix_x >= 0 and mouse_matrix_x < 10:
                    #print(mouse_matrix_y, mouse_matrix_x)
                    if self.mouse_selection != None and self.mouse_selection[0] != "matrix":
                        self.previous_mouse_selection = self.mouse_selection
                    self.mouse_selection = ("matrix", mouse_matrix_x, mouse_matrix_y)
                    return mouse_matrix_x, mouse_matrix_y
                
                elif 50 < self.mouse_position[0] < self.scene.largeur_interface - 50 and self.mouse_position[1] > self.scene.taille_fenetre[1] - 87:
                    self.previous_mouse_selection = self.mouse_selection
                    self.mouse_selection = ("red_cross", None)

                elif self.scene.wave_ended and self.scene.next_wave_button_rect.collidepoint(self.mouse_position):
                    self.previous_mouse_selection = self.mouse_selection
                    self.mouse_selection = ("next_wave_button", None)

                else:
                    for i in range(len(self.scene.liste_rect_shop)):
                        if self.scene.liste_rect_shop[i].collidepoint(self.mouse_position):
                            #print("shop", i)
                            self.previous_mouse_selection = self.mouse_selection
                            self.mouse_selection = ("shop", i)
                            return i  # Retourne le mot "shop" et l'index de la tourelle

            
            #Si le jeu est en pause et que le clic gauche est appuyé
            else:
                
                if self.scene.quit_button.rect.collidepoint(self.mouse_position):
                    self.scene.quit_button.state = "pressed"
                    self.quit_cond = True
                else:
                    self.scene.quit_button.state = "normal"
                    self.quit_cond = False

                if self.scene.resume_button.rect.collidepoint(self.mouse_position):
                    self.scene.resume_button.state = "pressed"
                    self.resume_cond = True
                else:
                    self.scene.resume_button.state = "normal"
                    self.resume_cond = False
                
                if self.scene.info_button.rect.collidepoint(self.mouse_position):
                    self.scene.info_button.state = "pressed"
                    self.info_cond = True
                else:
                    self.scene.info_button.state = "normal"
                    self.info_cond = False
                
                if self.scene.settings_button.rect.collidepoint(self.mouse_position):
                    self.scene.settings_button.state = "pressed"
                    self.settings_cond = True
                else:
                    self.scene.settings_button.state = "normal"
                    self.settings_cond = False


        elif not self.mouse_button_state[0]:
            # Action du bouton play
            if self.pause_cond and self.scene.pause_button.rect.collidepoint(self.mouse_position):
                self.scene.pause_button.state = "normal"
                self.mouse_selection = "pause"
                self.pause_cond = False
            else:
                self.scene.pause_button.state = "normal"
                self.mouse_selection = None
                self.pause_cond = False
            
            if not self.scene.paused:
                pass


            # Si le clic gauche de la souris est relâché pendant que le jeu est en pause
            else:
                if self.quit_cond and self.scene.quit_button.rect.collidepoint(self.mouse_position):
                    self.scene.quit_button.state = "normal"
                    self.scene.quit = True
                    self.quit_cond = False
                else:
                    self.scene.quit_button.state = "normal"
                    self.quit_cond = False

                
                if self.resume_cond and self.scene.resume_button.rect.collidepoint(self.mouse_position):
                    self.scene.resume_button.state = "normal"
                    self.scene.paused = False
                    self.resume_cond = False
                else:
                    self.scene.resume_button.state = "normal"
                    self.resume_cond = False
                
                if self.info_cond and self.scene.info_button.rect.collidepoint(self.mouse_position):
                    self.scene.info_button.state = "normal"
                    self.scene.is_info_menu_open = True
                    self.scene.menu.info_menu.switch_to_info()
                    self.info_cond = False
                else:
                    self.scene.info_button.state = "normal"
                    self.info_cond = False

                if self.settings_cond and self.scene.settings_button.rect.collidepoint(self.mouse_position):
                    self.scene.settings_button.state = "normal"
                    self.scene.is_settings_menu_open = True
                    self.settings_cond = False
                else:
                    self.scene.settings_button.state = "normal"
                    self.settings_cond = False

    def start_menu_mouse_manager(self):
        if self.mouse_button_state[0]:
            # Collision avec le bouton play
            if self.scene.play_button.rect.collidepoint(self.mouse_position):
                self.play_cond = True
                self.scene.play_button.state = "pressed"
            else:
                self.play_cond = False
                self.scene.play_button.state = "normal"
            # Collision avec le bouton quit
            if self.scene.quit_button.rect.collidepoint(self.mouse_position):
                self.quit_cond = True
                self.scene.quit_button.state = "pressed"
            else:
                self.quit_cond = False
                self.scene.quit_button.state = "normal"

            if self.scene.info_button.rect.collidepoint(self.mouse_position):
                    self.scene.info_button.state = "pressed"
                    self.info_cond = True
            else:
                self.scene.info_button.state = "normal"
                self.info_cond = False
            
            if self.scene.settings_button.rect.collidepoint(self.mouse_position):
                    self.scene.settings_button.state = "pressed"
                    self.settings_cond = True
            else:
                self.scene.settings_button.state = "normal"
                self.settings_cond = False
            
            if self.scene.credit_button.rect.collidepoint(self.mouse_position):
                    self.scene.credit_button.state = "pressed"
                    self.credit_cond = True
            else:
                self.scene.credit_button.state = "normal"
                self.credit_cond = False

            if self.scene.stats_button.rect.collidepoint(self.mouse_position):
                    self.scene.stats_button.state = "pressed"
                    self.stats_cond = True
            else:
                self.scene.stats_button.state = "normal"
                self.stats_cond = False
                
        elif not self.mouse_button_state[0]:
            # Action du bouton play
            if self.play_cond and self.scene.play_button.rect.collidepoint(self.mouse_position):
                self.scene.start_game()
                self.play_cond = False
            else:
                self.play_cond = False
                self.scene.play_button.state = "normal"
            # Action du bouton quit
            if self.quit_cond and self.scene.quit_button.rect.collidepoint(self.mouse_position):
                self.scene.quit_game()
            else:
                self.quit_cond = False
                self.scene.quit_button.state = "normal"

            if self.info_cond and self.scene.info_button.rect.collidepoint(self.mouse_position):
                    self.scene.info_button.state = "normal"
                    self.scene.is_info_menu_open = True
                    self.scene.info_menu.switch_to_info()
                    self.info_cond = False
            else:
                self.scene.info_button.state = "normal"
                self.info_cond = False

            if self.settings_cond and self.scene.settings_button.rect.collidepoint(self.mouse_position):
                    self.scene.settings_button.state = "normal"
                    self.scene.is_settings_menu_open = True
                    self.settings_cond = False
            else:
                self.scene.settings_button.state = "normal"
                self.settings_cond = False
            
            if self.credit_cond and self.scene.credit_button.rect.collidepoint(self.mouse_position):
                    self.scene.credit_button.state = "normal"
                    self.scene.is_info_menu_open = True
                    self.scene.info_menu.switch_to_credit()
                    self.credit_cond = False
            else:
                self.scene.credit_button.state = "normal"
                self.credit_cond = False
            
            if self.stats_cond and self.scene.stats_button.rect.collidepoint(self.mouse_position):
                    self.scene.stats_button.state = "normal"
                    self.scene.info_menu.switch_to_stats()
                    self.scene.is_info_menu_open = True
                    self.stats_cond = False
            else:
                self.scene.stats_button.state = "normal"
                self.stats_cond = False
                
    def info_menu_mouse_manager(self):
        if self.mouse_button_state[0]:
            # Collision avec le bouton play
            if self.scene.quit_button.rect.collidepoint(self.mouse_position):
                self.quit_cond = True
                self.scene.quit_button.state = "pressed"
            else:
                self.quit_cond = False
                self.scene.quit_button.state = "normal"

            if self.scene.state == "credit" and self.scene.scroll_speed_button.rect.collidepoint(self.mouse_position) and self.scene.is_scroll_speed_button_active:
                self.scene.scroll_speed = 1.5
                self.scene.scroll_speed_button.state = "pressed"

            else:
                self.scene.scroll_speed = 0.5
                self.scene.scroll_speed_button.state = "normal"
            

        elif not self.mouse_button_state[0]:
            # Action du bouton quit
            if self.quit_cond and self.scene.quit_button.rect.collidepoint(self.mouse_position):
                self.scene.quit_interface()
                self.quit_cond = False
            else:
                self.quit_cond = False
                self.scene.quit_button.state = "normal"

            if self.scene.state == "credit":
                self.scene.scroll_speed = 0.5
                self.scene.scroll_speed_button.state = "normal"

    
    def settings_menu_mouse_manager(self):
        if self.mouse_button_state[0]:
            if self.scene.quit_button.rect.collidepoint(self.mouse_position):
                self.quit_cond = True
                self.scene.quit_button.state = "pressed"
            else:
                self.quit_cond = False
                self.scene.quit_button.state = "normal"

            if self.scene.mute_sound_button.rect.collidepoint(self.mouse_position):
                self.scene.mute_sound_button.state = "pressed"
                self.scene.demute_sound_button.state = "pressed"
                self.sound_cond = True
            else:
                self.scene.mute_sound_button.state = "normal"
                self.scene.demute_sound_button.state = "normal"
                self.sound_cond = False

            
            # lower and upper sound button
            if self.scene.lower_sound_button.rect.collidepoint(self.mouse_position):
                self.scene.lower_sound_button.state = "pressed"
                self.lower_sound_cond = True
            else:
                self.scene.lower_sound_button.state = "normal"
                self.lower_sound_cond = False
            
            if self.scene.upper_sound_button.rect.collidepoint(self.mouse_position):
                self.scene.upper_sound_button.state = "pressed"
                self.upper_sound_cond = True
            else:
                self.scene.upper_sound_button.state = "normal"
                self.upper_sound_cond = False

            #lower and upper music button
            
            if self.scene.lower_music_button.rect.collidepoint(self.mouse_position):
                self.scene.lower_music_button.state = "pressed"
                self.lower_music_cond = True
            else:
                self.scene.lower_music_button.state = "normal"
                self.lower_music_cond = False
            
            if self.scene.upper_music_button.rect.collidepoint(self.mouse_position):
                self.scene.upper_music_button.state = "pressed"
                self.upper_music_cond = True
            else:
                self.scene.upper_music_button.state = "normal"
                self.upper_music_cond = False
            
            if self.scene.mute_music_button.rect.collidepoint(self.mouse_position):
                self.scene.mute_music_button.state = "pressed"
                self.scene.demute_music_button.state = "pressed"
                self.music_cond = True
            else:
                self.scene.mute_music_button.state = "normal"
                self.scene.demute_music_button.state = "normal"
                self.music_cond = False
                
        elif not self.mouse_button_state[0]:
            if self.quit_cond and self.scene.quit_button.rect.collidepoint(self.mouse_position):
                self.scene.quit_interface()
                self.quit_cond = False
            else:
                self.quit_cond = False
                self.scene.quit_button.state = "normal"

            if self.sound_cond and self.scene.mute_sound_button.rect.collidepoint(self.mouse_position):
                self.scene.mute_sound_button.state = "normal"
                self.scene.demute_sound_button.state = "normal"
                self.scene.file_manager.set_setting("is_sound_active", not self.scene.file_manager.get_setting("is_sound_active"))
                self.sound_cond = False
            else:
                self.scene.mute_sound_button.state = "normal"
                self.scene.demute_sound_button.state = "normal"
                self.sound_cond = False

            # lower and upper sound button
            if self.lower_sound_cond and self.scene.lower_sound_button.rect.collidepoint(self.mouse_position):
                self.scene.lower_sound_button.state = "normal"
                self.scene.sound_volume_down()
                self.lower_sound_cond = False
            else:
                self.lower_sound_cond = False
                self.scene.lower_sound_button.state = "normal"
            
            if self.upper_sound_cond and self.scene.upper_sound_button.rect.collidepoint(self.mouse_position):
                self.scene.upper_sound_button.state = "normal"
                self.upper_sound_cond = False
                self.scene.sound_volume_up()
            else:
                self.upper_sound_cond = False
                self.scene.upper_sound_button.state = "normal"
                
            # lower and upper music button
            if self.lower_music_cond and self.scene.lower_music_button.rect.collidepoint(self.mouse_position):
                self.scene.lower_music_button.state = "normal"
                self.scene.music_volume_down()
                self.lower_music_cond = False
            else:
                self.lower_music_cond = False
                self.scene.lower_music_button.state = "normal"
            
            if self.upper_music_cond and self.scene.upper_music_button.rect.collidepoint(self.mouse_position):
                self.scene.upper_music_button.state = "normal"
                self.upper_music_cond = False
                self.scene.music_volume_up()
            else:
                self.upper_music_cond = False
                self.scene.upper_music_button.state = "normal"
            
            if self.music_cond and self.scene.mute_music_button.rect.collidepoint(self.mouse_position):
                self.scene.mute_music_button.state = "normal"
                self.scene.demute_music_button.state = "normal"
                
                self.scene.file_manager.set_setting("is_music_active", not self.scene.file_manager.get_setting("is_music_active"))
                self.music_cond = False
            else:
                self.scene.mute_music_button.state = "normal"
                self.scene.demute_music_button.state = "normal"
                self.music_cond = False
            
    def handle_mouse_event(self):
        if self.scene_name == "game":
            self.game_mouse_manager()
            
        elif self.scene_name == "start_menu":
            self.start_menu_mouse_manager()

        elif self.scene_name == "info_menu":
            self.info_menu_mouse_manager()
        
        elif self.scene_name == "settings_menu":
            self.settings_menu_mouse_manager()

    def previous_selection_on_mouse(self):
        self.mouse_position = pg.mouse.get_pos()
        
        image_list = self.scene.liste_tourelle_image
            
        if self.mouse_selection != None:
            if self.mouse_selection[0] == "shop":
                image = image_list[self.mouse_selection[1]]
                image.set_alpha(160)
                self.scene.fenetre.blit(image, (self.mouse_position[0]- image.get_width()//2, self.mouse_position[1]- image.get_height()//2))
                return True
            if self.mouse_selection[0] == "red_cross":
                image = pg.transform.scale(pg.image.load("assets/images/others/red_cross.png").convert_alpha(), (50, 50))
                image.set_alpha(160)
                self.scene.fenetre.blit(image, (self.mouse_position[0]- image.get_width()//2, self.mouse_position[1]- image.get_height()//2))
                return True
        
        if self.previous_mouse_selection != None:
            if self.previous_mouse_selection[0] == "shop":
                image = image_list[self.previous_mouse_selection[1]]
                image.set_alpha(160)
                self.scene.fenetre.blit(image, (self.mouse_position[0]- image.get_width()//2, self.mouse_position[1]- image.get_height()//2))        
                return True
            if self.previous_mouse_selection[0] == "red_cross":
                image = pg.transform.scale(pg.image.load("assets/images/others/red_cross.png").convert_alpha(), (50, 50))
                image.set_alpha(160)
                self.scene.fenetre.blit(image, (self.mouse_position[0]- image.get_width()//2, self.mouse_position[1]- image.get_height()//2))
                return True
        
        
        
        return False

class Button:
    def __init__(self, x, y, image_normal, image_pressed, scale=(200, 100)):
        # Charger les images
        self.image_normal = pg.image.load(image_normal)
        self.image_pressed = pg.image.load(image_pressed)

        # Redimensionner les images
        self.image_normal = pg.transform.scale(self.image_normal, scale).convert_alpha()
        self.image_pressed = pg.transform.scale(self.image_pressed, scale).convert_alpha()

        # Créer le rectangle du bouton
        self.rect = self.image_normal.get_rect()

        # Positionner le rectangle
        self.rect.x = x
        self.rect.y = y

        # L'état du bouton est initialisé à "normal"
        self.state = "normal"

    def render(self, fenetre):
        # Dessiner le bouton avec l'image correspondant à son état
        if self.state == "normal":
            fenetre.blit(self.image_normal, self.rect.topleft)
        else:
            fenetre.blit(self.image_pressed, self.rect.topleft)
    
    def handle_event(self, event):
        # Si la souris est sur le bouton et que le bouton gauche de la souris est pressé,
        # changer l'état du bouton à "pressed"
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.state = "pressed"

        # Si le bouton gauche de la souris est relâché et que la souris est toujours sur le bouton,
        # changer l'état du bouton à "normal" et retourner True pour indiquer que le bouton a été cliqué
        elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.state = "normal"
                return True


class FileManager:
    def __init__(self, file_path):
        self.file_path = file_path

    def read_json(self):
        with open(self.file_path, 'r') as file:
            data = json.load(file)
        return data

    def get_setting(self, parameter_name):
        data = self.read_json()
        if parameter_name in data:
            return data[parameter_name]
        else:
            return None
    
    def set_setting(self, parameter_name, value):
        data = self.read_json()
        data[parameter_name] = value
        with open(self.file_path, 'w') as file:
            json.dump(data, file, indent=4)

if __name__ == '__main__':
    import menu
    import game
    menu1 = menu.StartMenu()
    menu1.run()
