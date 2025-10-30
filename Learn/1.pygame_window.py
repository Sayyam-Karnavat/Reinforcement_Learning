import pygame
import os
import random


pygame.init()
WIDTH , HEIGHT = 640 , 480


screen = pygame.display.set_mode((WIDTH , HEIGHT))
pygame.display.set_caption("Lesson - Pygame window")
clock = pygame.time.Clock()


running = True

while running:

    # Keep frame rate of game to 60 FPS
    dt = clock.tick(60)

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:
                running = False
        

    screen.fill((30,30,40,))


    # Simple text to show the pygame is running

    font = pygame.font.SysFont(None , 36)
    text = font.render("Pygame press ESC to quit" , True , (220 , 220 , 220))
    screen.blit(text , (40 , HEIGHT //2 - 18))


    # Flip display

    pygame.display.flip()

pygame.quit()




        
