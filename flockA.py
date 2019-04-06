import pygame
from pygame.locals import *
import math
import random

GAME_SIZE = 750
V_MAX = 5.0
A_MAX = 0.05
X_DEST = 375.0
Y_DEST = 375.0
MOVE = True

def start_game():
    pygame.init()
    fenetre = pygame.display.set_mode((GAME_SIZE, GAME_SIZE))
    for i in range(50):
        Perso((350.0, 350.0), random.randint(10, 25), 3.0, 3.0, True)
    pygame.key.set_repeat(1, 1)
    clock = pygame.time.Clock()
    continuer = True
    while continuer:        
        clock.tick(60)
        center = [0, 0]
        n = float(len(Perso.persos))
        for p in Perso.persos:
            center[0] += p.x
            center[1] += p.y
        center[0] /= n
        center[1] /= n
        global MOVE
        dest = [Perso.persos[0].xDest, Perso.persos[0].yDest]
        diff = math.sqrt((center[0] - dest[0])**2 + (center[1] - dest[1])**2)
        if diff > 50: # REMPLACER PAR LE CHIFFRE CORRESPONDANT AU NB BOIDS
            MOVE = True            
        else:
            MOVE = False
        for p in Perso.persos:
                p.addRules(0.5, 3.0, 0.1, 1.0, 4.0) 
            #              cent dist velo goto limi      => adapter en fonction du nb de boids
#           for p in Perso.persos:                          ex: goto augmente avec nb boids qui
#               for r in p.rules:                           diminue
#                   p.xspeed += r[0]
#                   p.yspeed += r[1]
#               p.limitVelocity()
#               p.x += p.xspeed
#               p.y += p.yspeed
        fenetre.fill((255, 255, 255))
        for p in Perso.persos: p.draw(fenetre)            
        for event in pygame.event.get():
            keys = pygame.key.get_pressed()
            if event.type == QUIT:
                continuer = 0
            if event.type == KEYDOWN:
                if event.key == K_SPACE:
                    continuer = 0
        if pygame.mouse.get_pressed()[0]:
            pos = pygame.mouse.get_pos()
            for p in Perso.persos:
                p.xDest = pos[0]
                p.yDest = pos[1]
        pygame.display.flip()
    pygame.quit()


class Perso:

    persos = []

    def __init__(self, pos, size, xspeed, yspeed, solid):
        self.x, self.y = pos
        self.xDest = X_DEST
        self.yDest = Y_DEST
        self.size = size
        self.xspeed = xspeed
        self.yspeed = yspeed
        self.xacc = 0
        self.yacc = 0
        self.solid = solid
        self.rules = []
        self.color = (random.randint(1, 255), random.randint(1, 255), random.randint(1, 255))
        Perso.persos.append(self)

    def limitVelocity(self):
        v = math.sqrt(self.xspeed**2 + self.yspeed**2)
        if v > V_MAX:
            self.xspeed /= v
            self.yspeed /= v
            self.xspeed *= V_MAX
            self.yspeed *= V_MAX            

    def deleteRules(self):
        self.rules = []

    def draw(self, fenetre):
        pygame.draw.circle(fenetre, self.color, (int(self.x), int(self.y)), int(self.size))
        pygame.draw.line(fenetre, (255, 255, 255), (int(self.x), int(self.y)), (int(self.x+self.size*self.xspeed), int(self.y+self.size*self.yspeed)), 1)

    def addRuleCenterMass(self, factor):
        xMoy = 0
        yMoy = 0
        vx = 0
        vy = 0
        for p in Perso.persos:
            if p != self:
                xMoy += p.x
                yMoy += p.y
        nb = float(len(Perso.persos) - 1)
        xMoy /= nb
        yMoy /= nb        
        vx = (xMoy - self.x)
        vy = (yMoy - self.y)
        v = math.sqrt(vx**2 + vy**2)
        if v > 0:
            vx = (V_MAX*vx/v) - self.xspeed
            vy = (V_MAX*vy/v) - self.yspeed
        a = math.sqrt(vx**2 + vy**2)
        ax = 0
        ay = 0
        if a > 0:
            ax = A_MAX*vx/a
            ay = A_MAX*vy/a
        self.rules.append((factor*ax, factor*ay))


    def addRuleDistance(self, factor):        
        cx = 0
        cy = 0
        for p in Perso.persos:
            if p != self:
                distanceMax = self.size + p.size
                distance = math.sqrt((p.x - self.x)**2 + (p.y - self.y)**2)
                if  distance > 0 and distance < distanceMax:
                    x = self.x - p.x
                    y = self.y - p.y
                    norm = math.sqrt(x**2 + y**2)
                    cx += x/(norm*distance)
                    cy += y/(norm*distance)
        c = math.sqrt(cx**2 + cy**2)
        if c > 0:
            cx = (V_MAX*cx/c) - self.xspeed
            cy = (V_MAX*cy/c) - self.yspeed
        a = math.sqrt(cx**2 + cy**2)
        ax = 0
        ay = 0
        if a > 0:
            ax = A_MAX*cx/a
            ay = A_MAX*cy/a
        self.rules.append((factor*ax, factor*ay))


    def addRuleVelocity(self, factor):
        vxMoy = 0
        vyMoy = 0
        for p in Perso.persos:
            if p != self:
                vxMoy += p.xspeed
                vyMoy += p.yspeed
        nb = float(len(Perso.persos) - 1) 
        vxMoy /= nb
        vyMoy /= nb
        v = math.sqrt(vxMoy**2 + vyMoy**2)
        vx = 0
        vy = 0
        if v > 0:
            vx = (V_MAX*vxMoy/v) - self.xspeed
            vy = (V_MAX*vyMoy/v) - self.yspeed
        a = math.sqrt(vx**2 + vy**2)
        ax = 0
        ay = 0
        if a > 0:
            ax = A_MAX*vx/a
            ay = A_MAX*vy/a
        self.rules.append((factor*ax, factor*ay))


    def addRuleGoTo(self, factor):        
        vx = self.xDest - self.x
        vy = self.yDest - self.y
        v = math.sqrt(vx**2 + vy**2)
        if v > 0:
            vx = (V_MAX*vx/v) - self.xspeed
            vy = (V_MAX*vy/v) - self.yspeed
        a = math.sqrt(vx**2 + vy**2)
        ax = 0
        ay = 0
        if a > 0:
            ax = A_MAX*vx/a
            ay = A_MAX*vy/a
        self.rules.append((factor*ax, factor*ay))

    def addRuleLimits(self, factor):
        vx = 0
        vy = 0
        if self.x < 10:
            vx = 10
            self.x = 10
        if self.x > GAME_SIZE - 10:
            vx = -10
            self.x = GAME_SIZE - 10
        if self.y < 10:
            vy = 10
            self.y = 10
        if self.y > GAME_SIZE - 10:
            vy = -10
            self.y = GAME_SIZE - 10
        v = math.sqrt(vx**2 + vy**2)
        if v > 0:
            vx = (V_MAX*vx/v) - self.xspeed
            vy = (V_MAX*vy/v) - self.yspeed
        a = math.sqrt(vx**2 + vy**2)
        ax = 0
        ay = 0
        if a > 0:
            ax = A_MAX*vx/a
            ay = A_MAX*vy/a
        self.rules.append((factor*ax, factor*ay))

    def addRules(self, factor1, factor2, factor3, factor4, factor5):
        self.deleteRules()
        global MOVE
        if MOVE:
            self.addRuleCenterMass(factor1)
            self.addRuleDistance(factor2)
            self.addRuleVelocity(factor3)
            self.addRuleGoTo(factor4)
            self.addRuleLimits(factor5)
        else:
            self.xspeed /= 2
            self.yspeed /= 2
            self.addRuleDistance(10*factor2) #x*...: plus vite en place

            diff = math.sqrt((self.x - self.xDest)**2 + (self.y - self.yDest)**2)
            if diff > 150: # REMPLACER PAR LE CHIFFRE CORRESPONDANT AU NB BOIDS
                self.addRuleCenterMass(factor1*20)
                # Ici, les autres objets sont simplement poussés, ils ne doivent
                # pas orienter leur tete dans la direction dans laquelle ils sont
                # poussés.

            self.addRuleLimits(factor5)
            
        for r in self.rules:
            self.xspeed += r[0]
            self.yspeed += r[1]
            
        self.limitVelocity()

        self.x += self.xspeed
        self.y += self.yspeed        
                            
start_game()


















        
