import pygame as pg


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
        self.images = self.get_images(nb_images, path)
        self.image = self.images[self.current_frame]
        self.rect = self.image.get_rect()
        
        self.rect.x = x
        self.rect.y = y
        self.position = (x, y)
        
        self.duration = duration
        self.start_timer = pg.time.get_ticks()
        
        self.is_dead = False
        
    def get_images(self, nb_images, path) -> list:
        images = []
        for i in range(nb_images):
            image = pg.transform.scale(pg.image.load(f'assets/images/{path}{i}.png'), self.proportion)
            if self.flip:
                image = pg.transform.flip(image, True, False)
            
            images.append(image.convert_alpha())
        if self.reverse:
            return images[::-1]
        return images
        
    
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

        if self.name == "impulse":
            self.jeu.render_shop_interface()
            self.jeu.red_cross_draw()


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

if __name__ == "__main__":
    import game
    jeu = game.Game()
    jeu.run()