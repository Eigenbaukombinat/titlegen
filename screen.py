import pygame
from pygame.locals import *
from utils import align_rect

from PIL import GifImagePlugin
import random
from PIL import Image
import time

from scr_config import SIZE_X, SIZE_Y, SIZE


pygame.mixer.init(44100, -16, 2, 512)
pygame.init()
FNT_ORB = pygame.font.Font('Orbitron-Black.otf', 80)
FNT_ORB_40 = pygame.font.Font('Orbitron-Black.otf', 40)
FNT_ORB_30 = pygame.font.Font('Orbitron-Black.otf', 30)
FNT_ORB_20 = pygame.font.Font('Orbitron-Black.otf', 20)
FNT_MNT = pygame.font.Font('Montserrat-Regular.otf', 40)


GREEN = (0, 255, 0)
WHITE = (255, 255, 255)

# primary colors gradations
PURPLE = [(178, 57, 255), (103, 2, 149), (68, 9, 105), (36, 0, 56)]
BLUE = [(104,0,231), (65,0,139), (42,0,94), (20,0,47)]
TURQUOISE = [(5,185,236), (0,118,169), (2,93,132), (0,42,58)]

# secondary colors
THEME1 = [(253,41,79), (22,10,254), (255,235,216), (1,2,42)]
THEME2 = [(255,249,0), ()]


DEFAULT_HAUFEN = [
'   -***',
'   -#*-',
'  .-##-',
'  .*##-',
'  .**#.',
'  -**-.',
]

TEST_HAUFEN = [
'-#-#-#-',
'#-#-#-#',
'-#-#-#-',
'#-#-#-#',
'-#-#-#-',
'#-#-#-#',
]

HAUFEN_TV = HAUFEN_TV_1 = [
'.*  -# ',
' .*-#  ',
'******#',
'-#   -#',
'- .  *#',
'--***##',
]
HAUFEN_TV_2 = [
'.*  -# ',
' .*-#  ',
'******#',
'*.-. -#',
'- *#*-#',
'--***##',
]
HAUFEN_TV_3 = [
'.*  -# ',
' .*-#  ',
'******#',
'-.-* .#',
'--* *##',
'--***##',
]


HAUFEN_ALPAKA = [
' *...# ',
'**# #*#',
'**---*#',
'-....-#',
'-....-#',
' -***# ',
]

HAUFEN_CHAOSZONE = [
'    -. ',
'##  ##.',
' ## *##',
'  ##* #',
'## ##  ',
'    ## ',
]


def render_pixelhaufen(width, height, alpha, haufen, color, x=0, y=0, margin=0):
    target = pygame.Surface(SIZE, pygame.SRCALPHA)
    pixel_size = int(width / 7)
    color_map = {}
    for num, ind in enumerate('.-*#'):
        color_map[ind] = color[3-num]
    hx_init = hx = int(pixel_size / 2) + 1
    hy_init = hy = int(pixel_size / 2) + 1
    for line in haufen:
        hx = hx_init
        for char in line:
            if char != ' ':
                pygame.draw.rect(target, color_map[char] + (alpha,), (hx+x+margin,hy+y+margin,pixel_size,pixel_size))
            hx += pixel_size
        hy += pixel_size

    pygame.draw.rect(target, WHITE, (x+margin+pixel_size-(pixel_size/3), y+margin, hx-hx_init-pixel_size+(pixel_size/2), hy-hy_init), 2)
    return target



class Pixelhaufen(pygame.sprite.Sprite):

    color = PURPLE
    size = 100
    haufen = DEFAULT_HAUFEN

    def __init__(self, size=100, alpha=100, haufen=DEFAULT_HAUFEN, color=PURPLE, **align_kw):
        super().__init__()
        self.color = color
        self.align_kw = align_kw
        self.size = size
        self.haufen = haufen
        self.alpha = alpha

    def reset_pos(self):
        pass

    def render_haufen(self, x=0, y=0, margin=0):
        return render_pixelhaufen(self.size, self.size, self.alpha, self.haufen, self.color, x, y, margin)

    def update(self):
        size = sx, sy = (self.size, self.size)
        x, y, margin = align_rect(size, **self.align_kw)
        target = self.render_haufen(x, y, margin)
        self.image = target
        self.rect = target.get_rect()




class Text(pygame.sprite.Sprite):

    txt_color = GREEN

    def reset_pos(self):
        x, y, margin = align_rect(self.image.get_size(), **self.align_kw)
        self.rect.x = x
        self.rect.y = y

    def __init__(self, txt, font=FNT_MNT, txt_color=GREEN, **align_kw):
        super().__init__()
        self.align_kw = align_kw
        self.txt_color = txt_color
        self.image = self.get_text_surface(txt, font)
        self.rect = self.image.get_rect()
        self.reset_pos()

    def get_text_surface(self, text, font=FNT_MNT):
        txt = font.render(text, True, self.txt_color)
        alpha_img = pygame.Surface(txt.get_size(), pygame.SRCALPHA)
        alpha_img.fill((255, 255, 255, 255))
        txt.blit(alpha_img, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        return txt



class TextWithHaufen(Text):

    color = BLUE
    txt_color = WHITE
    variants = ()
    speed = 10 # change haufen every 10 frames
    pos = 0
    cur_haufen = 0

    def __init__(self, txt, haufen_spec=DEFAULT_HAUFEN, font=FNT_MNT, color=BLUE, txt_color=WHITE, **align_kw):
        super().__init__(txt, font, txt_color, **align_kw)
        self.color = color
        txt = self.get_text_surface(txt, font)
        wt, ht = txt.get_size()
        txt_measure = self.get_text_surface('CHAOS', font)
        wt, ign = txt_measure.get_size()
        x, y, margin = align_rect(txt.get_size(), **self.align_kw)
        self.color = color
        self.txt = txt
        self.x = x
        self.wt = wt
        self.y = y
        self.ht = ht
        self.margin = margin
        self.add_haufen(haufen_spec, self.color)

    def add_haufen(self, spec, color):
        haufen = render_pixelhaufen(self.wt, self.ht, 255, spec, color, self.x, self.y, self.margin)
        haufen.blit(self.txt, (self.x+self.margin+(self.wt/7)+1, self.y+self.margin+self.wt-self.ht-(self.wt/7))) #special_flags=pygame.BLEND_RGBA_MULT
        self.variants += (haufen,)
        self.image = haufen
        self.rect = haufen.get_rect()
        return len(self.variants)

    def remove_haufen(self):
        self.cur_haufen = -1
        self.variants = ()

    def reset_pos(self):
        pass

    def update(self):
        self.pos += 1
        if self.pos == self.speed:
            self.cur_haufen += 1
            if self.cur_haufen >= len(self.variants):
                self.cur_haufen = 0
            if self.cur_haufen == -1:
                self.image = self.txt
                self.rect = self.txt.get_rect()
            else:
                self.image = self.variants[self.cur_haufen]
                self.rect = self.image.get_rect()
            self.pos = 0

class Lower3rd(Text):

    frames = 60
    cur_frame = 0

    def reset_pos(self):
        self.cur_frame = 0
        self.rect.x = 0
        self.rect.y = SIZE_Y - 100

    def update(self):
        fr = self.frames - self.cur_frame
        x = ((fr/4))**2.7

        if self.cur_frame == self.frames:
            self.remove()
            return
        self.rect.x = SIZE_X - x - 500
        self.cur_frame += 1


class ImageAnimation(pygame.sprite.Sprite):
    """Render a sequence of images as an animation in pixel style.
    Does also extract frames from animated gifs."""

    frames = ()
    cur_frame = 0
    speed = 10 # change image every 10 frames
    pos = 0
    color = GREEN

    def get_images(self, fns, mode='L'):
        result = []
        for fn in fns:
            imageObject = Image.open(fn)
            if hasattr(imageObject, 'is_animated') and imageObject.is_animated:
                for frame in range(0,imageObject.n_frames):
                    imageObject.seek(frame)
                    result.append(imageObject.copy().convert(mode))
            else:
                result.append(imageObject.convert(mode))
        return result


    def __init__(self, fns, effect=True, color=GREEN, speed=10, mono=False, scale=1, fit_to_screen=False, ani_speed=10, **align_kw):
        self.mono = mono
        self.color = color
        self.align_kw = align_kw
        self.speed = ani_speed
        if effect:
            #convert to grayscale
            mode = 'L'
        else:
            mode = 'RGBA'
        imgs = self.get_images(fns, mode)
        for img in imgs:
            if scale != 1:
                w, h = img.size
                img = img.resize((int(w * scale), int(h * scale)))
            if fit_to_screen and img.size != SIZE:
                img = img.resize(SIZE)
            if effect:
                target = self.render_image(img)
            else:
                target = pygame.image.fromstring(
                        img.tobytes(), img.size, img.mode)
            rect = target.get_rect()
            self.frames += ((target, rect),)
        self.image = target
        self.rect = rect
        self.cur_frame = 1

        super().__init__()

    def reset_pos(self):
        pass

    def render_image(self, img):
        target = pygame.Surface(SIZE, pygame.SRCALPHA)
        size = sx, sy = img.size
        x, y, margin = align_rect(size, **self.align_kw)
        for img_x in range(0, sx, 7):
            for img_y in range(0, sy, 7):
                col = img.getpixel((img_x,img_y))
                if self.mono:
                    if col < 100:
                        col = 255
                    else:
                        col = 0
                if col > 0:
                    pygame.draw.rect(target, self.color + (col,), (img_x+x+margin,img_y+y+margin,6,6))
        return target


    def update(self):
        self.pos += 1
        if self.pos == self.speed:
            self.remove()
            if self.cur_frame >= len(self.frames):
                self.cur_frame = 0
            self.image = self.frames[self.cur_frame][0]
            self.rect = self.frames[self.cur_frame][1]
            self.cur_frame += 1
            self.pos = 0


class FlyingAnimation(ImageAnimation):
    """Extend ImageAnimation: Animations flying from bottom to top
    with slightly increased speed. This can not be toggled, started
    sprites are running until they are out of sight. Configure max instances
    with max_instances."""

    fly_start = SIZE_Y
    fly_end = 0
    fly_pos = SIZE_Y
    fly_speed = 5
    max_instances = 10
    x_pos = 0
    finished = False
    running = False

    def __init__(self, *args, effect=True, random_x_pos=True,fly_speed=3, **kw):
        super().__init__(*args, effect=effect, **kw)
        self.fly_end = 0 - self.image.get_size()[1]
        self.fly_speed = self.fly_speed_reset = fly_speed
        self.random_x_pos = random_x_pos
        self.reset_x()

    def reset_x(self):
        if self.random_x_pos:
            # this does not work, surface is always fullscreen. :(
            max_x = SIZE_X-self.image.get_size()[0]
            # meh
            max_x = SIZE_X - 100
            self.x_pos = random.randint(0, max_x)

    def reset_pos(self):
        self.fly_pos = SIZE_Y
        self.fly_speed = self.fly_speed_reset
        self.finished = False
        self.running = False
        self.reset_x()
        self.rect.y = SIZE_Y

    def update(self):
        super().update()
        self.running = True
        self.fly_speed += 0.06
        self.fly_pos -= int(self.fly_speed)
        if self.fly_pos <= self.fly_end:
            self.finished = True

        self.rect.y = self.fly_pos
        self.rect.x = self.x_pos



class TGen(object):

    def __init__(self):
        flags = pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.FULLSCREEN
        self.screen = pygame.display.set_mode(SIZE)
        pygame.mouse.set_visible(False)
        pygame.display.set_caption('rc3 title generator output')
        self.all_sprites = pygame.sprite.Group()
        self.clock = clock = pygame.time.Clock()
        self.clear()

    def clear(self):
        # clear the screen
        pygame.draw.rect(self.screen, (0,0,0), (0,0,1920,1080))

    def show_text(self, txt, font=FNT_MNT, **align_kw):
        """print text with given font on the given position"""
        margin = align_kw.get('margin', 0)
        x, y, margin = align_rect(txt.get_size(), **align_kw)
        self.screen.blit(txt, (x+margin,y+margin))

    def render_text(self, text, font=FNT_MNT, **align_kw):
        txt = self.get_text_surface(text, font)
        self.show_text(txt, font, **align_kw)


    def main(self):
        senderlogo = TextWithHaufen('CZTV', haufen_spec=HAUFEN_TV, halign='left', valign='top', margin=10, font=FNT_ORB_20, txt_color=WHITE)
        #senderlogo.add_haufen(DEFAULT_HAUFEN)
        registry = dict(
            merkel=ImageAnimation(['images/cyber.jpg'], fit_to_screen=True, color=TURQUOISE[1]),
            ph1=ImageAnimation(['images/pesthoernchen.jpg'], halign='center', color=PURPLE[0]),
            ph2=ImageAnimation(['images/pesthoernchen.jpg'], halign='right'),
            ph3=ImageAnimation(['images/pesthoernchen.jpg'], halign='right', valign="bottom", margin=40),
            ph4=ImageAnimation(['images/pesthoernchen.jpg'], halign='center',  margin=40),
            chaoszone=ImageAnimation(['images/chaoszone.png'], halign='center',  valign="middle"),
            winkekatze=ImageAnimation(['images/winkekatze.png','images/winkekatze2.png'], halign='center',  valign="middle"),
            bb=Lower3rd('Hallo ballo', color=BLUE[0]),
            bb2=Lower3rd('Hallo ballo blabla blubberdiblubb'),
            # t2=TextWithHaufen('Blubb', x=0, y=0),
            t2=senderlogo,
            ph=Pixelhaufen(size=100, x=SIZE_X-400, y=40, color=TURQUOISE),
        )

        keys = {
            K_a: 'merkel',
            K_s: 'ph1',
            K_d: 'ph2',
            K_f: 'ph3',
            K_r: 'bb',
            K_t: 'bb2',
            K_w: 'winkekatze',
            K_c: 'chaoszone',
            K_b: 't2',
            K_p: 'ph',
        }

        multi_registry = dict(
            gif=(FlyingAnimation, (['images/herz.gif'],), dict(ani_speed=1, fly_speed=3, scale=0.6, color=THEME1[0])),
            grrr=(FlyingAnimation, (['images/angry.gif'],), dict(effect=False, ani_speed=5, fly_speed=2, scale=1.2)),
            img=(FlyingAnimation, (['images/chaoszone_logo.png'],), dict(effect=False, ani_speed=1, fly_speed=2, scale=0.7)),
        )

        multi_keys = {
            K_g: 'gif',
            K_h: 'grrr',
            K_j: 'img',
        }

        multi_cache = dict(gif=[], grrr=[], img=[])
        multi_running = dict(gif=[], grrr=[], img=[])

        # "multi" dinger pre-rendern
        for name, spr in multi_registry.items():
            klass, args, kw = spr
            for x in range(klass.max_instances):
                multi_cache[name].append(klass(*args, **kw))


        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    return
                if event.type == KEYDOWN:
                    if event.key == K_q:
                        return
                    if event.key in keys:
                        # dinge ein und ausblenden
                        name = keys.get(event.key)
                        sprite = registry.get(name)
                        if sprite in self.all_sprites:
                            self.all_sprites.remove(sprite)
                        else:
                            sprite.reset_pos()
                            self.all_sprites.add(sprite)
                    if event.key in multi_keys:
                        # dinge einblenden die von selbst wieder verschwinden
                        name = multi_keys.get(event.key)
                        cached_sprites = multi_cache.get(name)
                        found = False
                        for spr in cached_sprites:
                            if not spr.running:
                                found = True
                                break
                        if found:
                            self.all_sprites.add(spr)

                    if event.key == K_k:
                        senderlogo.remove_haufen()
                        senderlogo.add_haufen(DEFAULT_HAUFEN, PURPLE)
                    if event.key == K_l:
                        senderlogo.remove_haufen()
                        senderlogo.add_haufen(HAUFEN_TV_1, TURQUOISE)
                        senderlogo.add_haufen(HAUFEN_TV_2, TURQUOISE)
                        senderlogo.add_haufen(HAUFEN_TV_3, TURQUOISE)
                    if event.key == K_j:
                        senderlogo.remove_haufen()
                        senderlogo.add_haufen(HAUFEN_ALPAKA, BLUE)
                    if event.key == K_h:
                        senderlogo.remove_haufen()
                        senderlogo.add_haufen(HAUFEN_CHAOSZONE, PURPLE)
            for name, cache in multi_cache.items():
                for spr in cache:
                    if spr.finished:
                        spr.reset_pos()
                        self.all_sprites.remove(spr)

            self.clear()
            self.all_sprites.update()
            self.all_sprites.draw(self.screen)
            self.clock.tick(60)
            pygame.display.flip()

if __name__ == '__main__':
    TGen().main()
