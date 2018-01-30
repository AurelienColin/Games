from os.path import join
import pygame
import pyganim
from pygame.locals import *
import sys

screenDim = (870,870)

def Launcher():
    pygame.init()
    screen = Screen(screenDim)

    #filename = input('Enter filename:')
    filename = "VisualNovel.txt"
    fullname = join('..', 'res', 'script', filename)
    file = open(fullname)
    lines = file.readlines()
    file.close()
    VNLoop(screen, lines)
    pass

def FormatText(text, l):
    name, text = text.split(':')
    lines, line = [], ''
    for word in text.split():
        if len(line + word)+1 < l:
            line += word + ' '
        else:
            lines.append(line)
            line = word + ' '
    lines.append(line)
    return name + ': ' + '; '.join(lines)

def VNLoop(screen, lines):
    on_screen = {}
    mainClock = pygame.time.Clock()
    for line in lines:
        change = False
        if ':' in line:  # This is a declaration
            pos = (int((screen.size[0]-300)/2),screen.size[1]-100)
            box = Dialog(FormatText(line, 42), [pos])
            current_dialog = screen.AddTextBox(box)
        else:  # A character enter or leave, or a music/sound is played
            change = True
            line = line.split()
            if line[0] == 'enter':
                char, file, transf, pos = line[1:]
                x, y = tuple([int(ele) for ele in pos.split(',')])
                if x < 0:
                    x = screen.size[0]+x
                if y < 0:
                    y = screen.size[1]+y
                img = pygame.image.load(join('..', 'res', 'sprite', file))
                if char == 'background':
                    img = pygame.transform.scale(img, screen.size)
                if transf == 'sym':
                    sprite = pygame.transform.flip(img, True, False)
                elif transf == 'raw':
                    sprite = img
                on_screen[char] = screen.AddSprite(sprite, (x, y))
            elif line[0] == 'leave':
                screen.RemoveObject(on_screen[line[1]])
            elif line[0] == 'music_on':
                music = pygame.mixer.Sound(join('..', 'res', 'music', line[1]))
                music.play(loops=-1)
            elif line[0] == 'music_off':
                music.stop()
            elif line[0] == 'sound':
                pygame.mixer.Sound(join('..', 'res', 'sound', line[1])).play()
        while change == False:
            screen.refresh()
            mainClock.tick(30)
            for event in pygame.event.get():
                if event.type == QUIT:  # The game is closed
                    pygame.quit()
                    sys.exit()
                if event.type == KEYDOWN:
                    if event.key == K_RETURN:
                        change = True
                        [screen.RemoveObject(index) for index in current_dialog]
    [screen.RemoveObject(i) for i in current_dialog + list(on_screen.values())]
    music.stop()
    pygame.quit()


class TextBox():
    def __init__(self, files, texts, dim, text_pos, pos, size=20, color={'default':(0,0,0)}):
        names = [join('..', 'res', 'textbox', file) for file in files]
        self.text = []
        self.string = []
        c = color['default']
        for j, text in enumerate(texts):
            text = text.split(';')
            self.string += [text[i] for i in range(len(text))]
            self.text += [Text(text[i], (text_pos[j][0], text_pos[j][1]+i*(size+2)),
                          size, color=c) for i in range(len(text))]
        for i, c in color.items():
            if type(i)==int:
                if i < 0:
                    i = len(self.text)+i
                self.text[i].ChangeColor(c)

        self.size = dim
        self.imgs = False
        f1, f2 = pygame.transform.smoothscale, pygame.image.load
        self.box = [f1(f2(names[i]), self.size[i]) for i in range(len(names))]
        self.imgs = False
        self.pos = pos

        decal = [min(0, screenDim[0]-self.size[0][0]-self.pos[0][0]),
                 min(0, screenDim[1]-self.size[0][1]-self.pos[0][1])]
        for i, xy in enumerate(self.pos):
            self.pos[i] = [xy[0]+decal[0], xy[1]+decal[1]]

class Dialog(TextBox):
    def __init__(self, text, pos):
        char_name, string = text.split(':')
        box = ['TextBox_Large.png']
        TextBox.__init__(self, box, [char_name, string], [(300,100)],
                         [(15, 10), (20, 30)], pos, size=17)

class Text():
    def __init__(self, text, pixel, size, color=(0,0,0)):
        font = pygame.font.SysFont('freesans', size)
        self.size = size
        self.text = text
        self.string = font.render(text, True, color)
        self.pixel = pixel

class Screen():
    def __init__(self, size):
        self.size = size
        self.display = pygame.display.set_mode(self.size, pygame.RESIZABLE)
        self.objects = []

    def RemoveObject(self, index):
        self.objects[index] = None

    def AddSprite(self, sprite, pos):
        if str(type(sprite))=="<class 'pyganim.PygAnimation'>":
            self.objects.append([sprite, pos, 'character'])
        else:
            self.objects.append([sprite, pos, 'sprite'])
        return len(self.objects)-1

    def AddTextBox(self, box):
        prec = len(self.objects)
        self.objects.append([box, box.pos[0], 'box'])
        if box.imgs:
            for img in box.imgs:
                self.objects.append([img[0], (box.pos[0][0]+img[1][0],
                                     box.pos[0][1]+img[1][1]), 'others'])
        for i, text in enumerate(box.text):
            self.objects.append([text.string, (text.pixel[0] + box.pos[0][0],
                                                 text.pixel[1] + box.pos[0][1]),
                                 'text', text.text])
        index = [i for i in range(prec, len(self.objects))]
        self.objects[prec].append(index)
        return index

    def refresh(self):
        sprites = [obj[:2] for obj in self.objects if obj and obj[2]=='sprite']
        box = [obj[:4] for obj in self.objects if obj and obj[2]=='box']
        [self.display.blit(ele, pos) for ele, pos in sprites]
        for ele, pos, t, index in box:
            for i in index:
                ele2, pos2=  self.objects[i][:2]
                if type(ele2) == pygame.Surface:
                    self.display.blit(ele2, pos2)
                elif type(ele2) != pyganim.PygAnimation :
                    for j in range(len(ele2.box)):
                        self.display.blit(ele2.box[j], ele2.pos[j])

        pygame.display.update()

if __name__ == '__main__':
    Launcher()