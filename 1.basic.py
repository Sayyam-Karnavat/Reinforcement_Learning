'''
- Game loop :- It repeatedly updates the game state,
handles the inputs and renders draws the screen.Typically runs at 30-60 frames per second (FPS).


- Events and Input: Games respond to user actions like key presses or mouse clicks.

- Rendering: Drawing graphics on the screen using shapes, images, or text.


- RL Connection: In RL, a game is an "environment" where an agent takes "actions" based on the current "state" and receives "rewards." We'll build games that can be framed this way (e.g., state as positions/scores, actions as moves, rewards as points).


'''


import pygame
import random


SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600


# Initialize the pygame
pygame.init()

# Setup the display 
screen = pygame.display.set_mode((SCREEN_WIDTH ,SCREEN_HEIGHT))


pygame.display.set_caption("Controllabe Rectangle")

# Set the clock
clock = pygame.time.Clock() # Created this clock for FPS control


# Rectangle properties (position and size)

player_x = 400
player_y = 300
player_speed = 20
player_width = 50
player_height = 50




# Main loop

running = True

while running:

    # Handle events like closing the window


    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False


        
        # Get key states
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            player_x -= player_speed

        if keys[pygame.K_RIGHT]:
            player_x += player_speed

        if keys[pygame.K_DOWN]:
            player_y += player_speed

        if keys[pygame.K_UP]:
            player_y -= player_speed

    
    # Boundary check

    if player_x < 0:
        player_x = 0
    
    if player_x > (SCREEN_WIDTH - player_width) : # since rectangle width is 50
        player_x = (SCREEN_WIDTH - player_width)
    
    if player_y < 0 :
        player_y = 0

    if player_y > (SCREEN_HEIGHT - player_height):
        player_y = (SCREEN_HEIGHT - player_height)



    

    # Fill the entire screen with the white color to clear screen
    screen.fill((255,255,255)) 


    # Draw rectangle (color : red)
    pygame.draw.rect(screen , (255,0,0) , (player_x , player_y , 50 , 50))



    # Update the display
    pygame.display.flip() # "Flip" to show the new frame

    # Limit the FPS to 60
    clock.tick(60)


# Quit pygame
pygame.quit()

        