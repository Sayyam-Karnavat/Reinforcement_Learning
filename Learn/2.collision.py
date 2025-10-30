import pygame
import random


SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600




class Player:
    def __init__(self):
        self.rect = pygame.Rect(400 , 300 , 50 , 50) # This is the bounding box of our player in the form of rectangle
        self.speed = 20
    
    def move(self , keys):
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
        if keys[pygame.K_UP]:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN]:
            self.rect.y += self.speed
        
        # Check boundaries
        self.rect.x = max(0 , min((SCREEN_WIDTH - self.rect.width) , self.rect.x))
        self.rect.y = max(0 , min((SCREEN_HEIGHT - self.rect.height) , self.rect.y))

    def draw(self , screen):
        pygame.draw.rect(screen , (0,255, 0) , self.rect)



class Enemy:
    def __init__(self):
        # Spawn enemy randomly of height and width as 30 at top
        self.rect = pygame.Rect(random.randint(0,750) , 0 , 30 , 30)
        self.speed = 5
    def update(self):
        self.rect.y += self.speed


        if self.rect.y > SCREEN_HEIGHT: # Enemy moved out of the screen
            self.rect.y = 0
            self.rect.x = random.randint(0,750) # Again randomly spawn the enemy

    
    def draw(self , screen):
        pygame.draw.rect(screen , (255,0,0) , self.rect)



pygame.init()


screen = pygame.display.set_mode((SCREEN_WIDTH , SCREEN_HEIGHT))
pygame.display.set_caption("Avoidance Game")
clock = pygame.time.Clock()


player = Player()
enemies = [Enemy() for _ in range(5)] # Create 5 enemies


running = True

while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    
    # Update the movement of player and also render the rectangle of player
    keys = pygame.key.get_pressed()
    player.move(keys=keys)
    
    screen.fill((0,0,0))

    player.draw(screen=screen)




    for enemy in enemies:
        enemy.update()
        enemy.draw(screen=screen)

        if player.rect.colliderect(enemy.rect):
            print("Collision! Game over") 
            running = False
    
    pygame.display.flip()
    clock.tick(60)


pygame.quit()


