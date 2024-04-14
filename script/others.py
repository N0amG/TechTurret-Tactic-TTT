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
        self.get_images(nb_images, path)
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
        self.images = images
        if self.reverse:
            self.images = self.images[::-1]
    
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
        
        fenetre.blit(self.image, self.rect)

        if self.name == "impulse":
            self.jeu.render_shop_interface()
            self.jeu.red_cross_draw()



if __name__ == "__main__":
    import game
    jeu = game.Game()
    jeu.run()