import pygame as pg


class Animation(pg.sprite.Sprite):
    # path : str -> exemple : 'enemy/drone/frame_'
    def __init__(self, nb_images : int, path : str, x : int, y : int , proportion : tuple, flip, fps : int):
        super().__init__()
        self.proportion = proportion
        self.fps = fps
        self.flip = flip
        self.current_frame = 0
        self.last_update = pg.time.get_ticks()
        
        self.images = self.get_images(nb_images, path)
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
    
    def get_images(self, nb_images, path) -> list:
        images = []
        for i in range(nb_images):
            image = pg.transform.scale(pg.image.load(f'assets/images/{path}{i}.png'), self.proportion)
            if self.flip:
                image = pg.transform.flip(image, True, False)
                
            images.append(image.convert_alpha())
        return images
    
    def update(self):
        now = pg.time.get_ticks()
        if now - self.last_update > 9000 // self.fps:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.images)
            self.image = self.images[self.current_frame]
    
    def render(self, fenetre):

        # hitbox
        #pg.draw.rect(fenetre, (255,0,0), (self.rect.x, self.rect.y, self.rect.width, self.rect.height), 1)
        
        fenetre.blit(self.image, self.rect)



if __name__ == "__main__":
    import game
    jeu = game.Game()
    jeu.run()