import pygame
import random




SCREEN_WIDTH = 720
SCREEN_HEIGHT = 720



class Player:

    def __init__(self):
        self.player_height = 50
        self.player_width = 50

        self.player_color = (0,255,0)


        # Start the player at the middle of the screen
        # Players size is 50 x 50 rectangle
        self.rect = pygame.Rect((SCREEN_WIDTH //2) , (SCREEN_HEIGHT//2) , self.player_width , self.player_height)
        
        
        # Player movenment speed
        self.speed = 20

    
    def move(self, keys):

        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
        if keys[pygame.K_DOWN]:
            self.rect.y += self.speed
        if keys[pygame.K_UP]:
            self.rect.y -= self.speed
        # Check boundaries
        self.rect.x = max(0 , min((SCREEN_WIDTH - self.rect.width) , self.rect.x))
        self.rect.y = max(0 ,  min((SCREEN_WIDTH - self.rect.height) , self.rect.y))

    def draw(self,screen):
        pygame.draw.rect(screen , self.player_color , self.rect)



class Enemy1:
    '''
    This enemy moves from top to bottom
    '''
    def __init__(self):
        self.enemy_width = 20
        self.enemy_height = 20

        self.enemy_color = (255,0,0)
        
        # Spawn enemy at top of the screen anywhere on x axis , "0" since to be at top y should be zero
        self.rect = pygame.Rect(random.randint(0 , SCREEN_WIDTH) , 0 , self.enemy_width , self.enemy_height)

        # Enemy speed
        self.speed = 5


    def move(self):
        self.rect.y += self.speed
        
        if self.rect.y > (SCREEN_HEIGHT - self.rect.height):
            self.rect.y = 0
            self.rect.x = random.randint(0 , SCREEN_WIDTH)

    def draw(self , screen):
        pygame.draw.rect(screen , self.enemy_color , self.rect)

        


class Enemy2:
    '''
    This enemy moves from left to right horizontally
    '''
    def __init__(self):
        self.enemy_width = 20
        self.enemy_height = 20
        self.enemy_color = (255,0,0)
        
        # Spawn enemy starting at x axis  of the screen anywhere on y axis 
        self.rect = pygame.Rect( 0 , random.randint(0,SCREEN_HEIGHT) , self.enemy_width , self.enemy_height)

        self.speed = 5
    
    def move(self):
        self.rect.x += self.speed

        # Check co-ordinates
        if self.rect.x > (SCREEN_WIDTH - self.rect.width):
            self.rect.x = 0
            self.rect.y = random.randint(0 , SCREEN_HEIGHT)

    def draw(self , screen):
        pygame.draw.rect(screen , self.enemy_color , self.rect)



class Reward:

    def __init__(self):
        
        # make a reward rectangle
        self.reward_size = 10
        self.rect = pygame.Rect(random.randint(0 , SCREEN_WIDTH-self.reward_size) , random.randint(0 , SCREEN_HEIGHT-self.reward_size) , self.reward_size , self.reward_size)

        # color
        self.reward_color = (0,0,255)
    
    def draw(self , screen):
        pygame.draw.rect(screen , self.reward_color , self.rect)
    


pygame.init()


screen = pygame.display.set_mode((SCREEN_WIDTH , SCREEN_HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)


# Player 
player = Player()

# In total we are keeping 4 enemies 
enemy1 = [Enemy1() for _ in range(2)] # Vertically moving enemy from top to bottom
enemy2 = [Enemy2() for _ in range(2) ] # Horizontally moving enemy from left to right


# Create a reward
reward = Reward()

# Score
player_score = 0


running = True
while running:

    screen.fill((0,0,0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Reward spawning and respwaning after player collides with reward rectangle
    reward.draw(screen=screen)

    if player.rect.colliderect(reward.rect):
        player_score += 1

        # If player takes the reward then destroy current reward and respawn reward
        del reward

        # Respawn reward by creating it new object which will randomly allocate x and y axis
        reward = Reward()
    
    # Player movements and rendering
    key_pressed = pygame.key.get_pressed()
    player.move(keys=key_pressed)
    player.draw(screen=screen)


    # Enemy 1 movements and rendering
    for enemy in enemy1:
        enemy.move()
        enemy.draw(screen=screen)

        if player.rect.colliderect(enemy.rect):
            print("Game over ! Player collided with enemy 1")
            running = False

    # Enemy 2 movements and rendering
    for enemy in enemy2:
        enemy.move()
        enemy.draw(screen=screen)

        if player.rect.colliderect(enemy.rect):
            print("Game over ! Player collided with enemy 2")
            running = False

     # Display score
    score_text = font.render(f"Score: {player_score}", True, (255, 255, 255))
    screen.blit(score_text, (10, 10))
    
    
    pygame.display.flip() 
    clock.tick(60)


pygame.quit()

    

    