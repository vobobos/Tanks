import pygame
from pygame.math import Vector2
import math
import random

WIN_WIDTH = 500
WIN_HEIGHT  = 500
window = pygame.display.set_mode([WIN_WIDTH, WIN_HEIGHT])

class Tank:
    """
    Klasse for spilleren
    
    Attributter:
        x (int): startposisjon x-verdi
        y (int): startposisjon y-verdi
        dimension (int): bredde og lengde til tanken
        
        body (Rect): pygame Rect objekt som bruker de andre attributtene for å definere rektangelet
    """
    def __init__(self):
        self.x = 50
        self.y = 450

        self.dimension = 20


        self.body = pygame.Rect(self.x, self.y, self.dimension,self.dimension)
    
    def move(self, objects):
        """
        Metode for å bevege spilleren
        Når brukeren taster wasd beveger spilleren seg i gitt retning, dersom den kolliderer med
        et hinder beveger den seg tilbake slik at den ikke kan gå gjennom
        
        Parametre:
            objects (list): liste med Rect objekter som fungerer som hinder
        """
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] and self.body.y > 0:
            self.body.move_ip(0,-1)
            if self.body.collidelist(objects) != -1:
                self.body.move_ip(0,1)
        if keys[pygame.K_s] and self.body.y < WIN_HEIGHT-self.dimension:
            self.body.move_ip(0,1)
            if self.body.collidelist(objects) != -1:
                self.body.move_ip(0,-1)
        if keys[pygame.K_a] and self.body.x > 0:
            self.body.move_ip(-1,0)
            if self.body.collidelist(objects) != -1:
                self.body.move_ip(1,0)
        if keys[pygame.K_d] and self.body.x < WIN_WIDTH-self.dimension:
            self.body.move_ip(1,0)
            if self.body.collidelist(objects) != -1:
                self.body.move_ip(-1,0)
            
    def barrel(self):
        """
        Metode for å lage løpet til tanksen
        Bruker midten av spilleren som startpunkt og musposisjonen til å finne sluttpunktet
        til en linje med gitt lengde
        
        Attributter:
            start (tuple): x og y koordinater til midtpunktet av tanksen
            mouse (tuple): x og y koordinater til musens posisjon
            vector_angle (float): vinkelen mellom tanksen og musen
            length(int): lengden til løpet
            end (tuple): koordinatene til sluttpunktet av løpet
        """
        start = self.body.center
        mouse = pygame.mouse.get_pos()
        
        vector_angle = math.atan2(start[1] - mouse[1], mouse[0] - start[0])
        length = 25
        end = (self.body.center[0] + length * math.cos(vector_angle),  self.body.center[1] - length * math.sin(vector_angle))
        return(start, end)
         
    
    def draw(self):
        """
        Metode for å tegne tanksen og løpet
        """
        line = self.barrel()
        pygame.draw.rect(window, 'blue', self.body)
        pygame.draw.line(window, 'white', line[0], line[-1], width=2)







class Bullet:
    """
    Klasse for kuler, tar en bevegelsesvektor, startpunkt og mengden ganger den kan sprette som parametre
    
    Parametre:
        move (Vector2): startvektor som kulen skal bevege seg etter
        center (tuple): startposisjonen til kula
        bounceCount (int): Mengden ganger kula kan sprette før den forsvinner
        
    Attributter:
        x (float): x-verdien til startposisjonen
        y (float): y-verdien til startposisjonen
        dimensions (int): bredden til kula
        speed (int): farten til kula
        bounces (int): teller for hvor mange ganger kula har sprettet
        hasShot (bool): booleansk verdi for om kulen skal være aktiv eller ikke
        body (Rect): hitbox til kula
    """
    def __init__(self, move, center, bounceCount):
        self.x = center[0]
        self.y = center[1]
        self.dimensions = 6
        
        self.speed = 8
        self.move  = move

        self.bounces = 0
        self.bounceCount = bounceCount

        self.hasShot = False

        self.body = pygame.Rect(self.x,self.y,self.dimensions,self.dimensions)
    
    def angle(self, p1, p2):
        """
        Metode som bruker to punkt til å returnere vinkelen mellom de i en float
        """
        return math.atan2(p2[1] - p1[1], p2[0] - p1[0])
    
    def movement(self, angle):
        """
        Metode som returnerer en vektor etter en gitt vinkel og farten til kula
        """
        return Vector2(math.cos(angle)*self.speed, math.sin(angle)*self.speed)
    
    
    # Skrevet med hjelp av ChatGPT
    def calculate_normal(self, objects):
        """
        Metode som beregner normalvinkel i et støt ved å finne hvilken side som kolliderte

        Parametre:
            objects (list): en liste med objektene (hindrene) på banen

        Returnerer:
            Tuple: normalvinkelen etter hvilken dx/dy er lavest
        """
        for i in objects:
            intersection = self.body.clip(i)

            center = intersection.center

            dx = center[0] - (self.body.x + self.body.width / 2)
            dy = center[1] - (self.body.y + self.body.height / 2)

            if abs(dx) > abs(dy):
                return (-1,0) if dx < 0 else (1,0)
            else:
                return (0,-1) if dy < 0 else (0,1)

    
    def shoot(self, objects):
        """
        Metode som beveger kulen og reflekterer den når den kolliderer etter en normalvektor, 
        og deretter tegner kulen med radius lik halve bredden

        Parametre:
            objects (list): samme hindre som i metoden over
        """
        if self.body.x < 0:
            self.move.reflect_ip(Vector2(1,0))
            self.bounces += 1
        if self.body.x > WIN_WIDTH-self.dimensions:
            self.move.reflect_ip(Vector2(-1,0))
            self.bounces += 1
        if self.body.y < 0:
            self.move.reflect_ip(Vector2(0,1))
            self.bounces += 1
        if self.body.y > WIN_HEIGHT-self.dimensions:
            self.move.reflect_ip(Vector2(0,-1))
            self.bounces += 1

        if self.body.collidelist(objects) != -1:
            normal = self.calculate_normal(objects)
            self.move.reflect_ip(Vector2(normal))
            self.bounces += 1

        if self.bounces > self.bounceCount:
            self.hasShot = False
            self.move = Vector2(0,0)
            
        self.body.move_ip(self.move)
        pygame.draw.circle(window, 'grey', self.body.center, self.body.width/2)







class Enemy:
    """
    Klasse for fienden

    Parametre:
        x (int): startposisjon x
        y (int): startposisjon y
    
    Attributter:
        dimensions (int): bredde og lengde til fienden
        body (Rect): hitboxen til fienden
        point (list): sluttpunktet til løpet til fienden
        movement (tuple): bevegelsesvektor til fienden
        hasShot (bool): Booleansk verdi for om fienden har skutt eller ikke
        dir (int): integer som bestemmer retningen til fienden
    """
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.dimensions = 20
        self.body = pygame.Rect(self.x, self.y, self.dimensions, self.dimensions)
        self.point = [0,20]
        self.movement = (0,1)
        
        self.hasShot = False

        self.dir = 0
        
    def AI(self, obstacles):
        """
        Metode for hvordan fienden skal oppføre seg
        Dersom den kolliderer med noe skal den flytte seg et hakk tilbake og velge en tilfeldig retning å fortsette i

        Parametre:
            obstacles (list): Liste med alle hindrene på banen
        """
        if self.body.x <= 0 or self.body.x >= WIN_WIDTH-self.dimensions or self.body.y <= 0 or self.body.y >= WIN_HEIGHT-self.dimensions or self.body.collidelist(obstacles) != -1:
            self.body.move_ip(-self.movement[0], -self.movement[1])
            self.dir = random.randint(0,3)
            if self.dir   == 0:
                self.movement = (0,1)
                self.point = [0,20]
            elif self.dir == 1:
                self.movement = (1,0)
                self.point = [20,0]
            elif self.dir == 2:
                self.movement = (0,-1)
                self.point = [0,-20]
            elif self.dir == 3:
                self.movement = (-1,0)
                self.point = [-20,0]
            else:
                self.dir = 0
        self.body.move_ip(self.movement)
        
            
    def draw(self):
        """
        Metode for å tegne fienden og løpet dens
        """
        pygame.draw.rect(window, 'green', self.body)
        pygame.draw.line(window, 'white', self.body.center, (self.body.center[0]+self.point[0], self.body.center[1]+self.point[1]), width=2)
        



# Lager objekt for spilleren som skal brukes og en for kulen for å ha tilgang til metodene
tank = Tank()
bullet = Bullet([0,0], (0,0),0)

# Lister for fiendene, spillerens og fiendens prosjektiler, og hindrene i spillet
enemies = [Enemy(250,250), Enemy(250,100)]
projectiles = []
eproj = []
objects = [pygame.Rect(0,400,400,20), pygame.Rect(100,200,400,20)]

game = True
while game:
    window.fill((0,0,0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            game = False
        
        # Dersom brukeren trykker på mellomrom eller trykker ned musa og det er færre enn tre aktive prosjektiler, så skyter spillertanksen
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and len(projectiles) < 3 or event.type == pygame.MOUSEBUTTONDOWN and len(projectiles) < 3:
            end = pygame.mouse.get_pos()
            move = bullet.movement(bullet.angle(tank.body.center, end))
            projectiles.append(Bullet(move, tank.body.center,1))

    # Går gjennom alle fiendens prosjektiler og flytter de, dersom hasShot blir False i shoot metoden fjernes den fra listen siden den har kollidert med noe
    # Kolliderer den med spilleren så har hen tapt og spillet lukkes
    for i in eproj:
        i.hasShot = True
        i.shoot(objects)
        if not i.hasShot:
            eproj.remove(i)
        
        if i.body.colliderect(tank.body):
            game = False
    
    # Gjør det samme som over men for spillerens prosjektiler
    for i in projectiles:
        i.hasShot = True
        i.shoot(objects)
        if not i.hasShot:
            projectiles.remove(i)

    
    tank.move(objects)
    tank.draw()

    for i in enemies:
        i.AI(objects)
        i.draw()
        
        # Dersom fienden ikke har skutt så skyter den
        if not i.hasShot:
            i.hasShot = True
            eproj.append(Bullet(Vector2(i.movement[0]*2,i.movement[1]*2), (i.body.center[0]-bullet.dimensions/2, i.body.center[1]-bullet.dimensions/2),0))
        
        # Dersom det ikke fins noen fiendtlige prosjektiler lader alle fiendene om
        if len(eproj) == 0:
            i.hasShot = False
        
        # Sjekker om fienden kolliderer med spillerens prosjektiler og fjerner de hvis det er tilfellet
        for x in projectiles:
            if i.body.colliderect(x.body):
                projectiles.remove(x)
                enemies.remove(i)

    # Tegner alle hindrene med en kraftig rødfarge
    for i in objects:
        pygame.draw.rect(window, "red", i)

    pygame.time.Clock().tick(60)
    pygame.display.flip()

pygame.quit()