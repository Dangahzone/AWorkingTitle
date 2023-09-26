import pygame
from game import Game
import sys
import os
import pygame_gui
pygame.init()
from pygame.locals import *

def setup_game_window():
    
    resolution = (800,600)
    width, height = resolution

    game_window = pygame.display.set_mode((resolution), pygame.RESIZABLE)

    return game_window, width, height


def display_logo(game_window, width, height):
    logo_image = pygame.image.load("assets\logo.png")
    logo_image = pygame.transform.scale(logo_image, (width // 2, height // 2))

    game_window.fill((0, 0, 0))  # Fill the screen with black background

    # Calculate the position to center the logo
    logo_x = (width - logo_image.get_width()) // 2
    logo_y = (height - logo_image.get_height()) // 2

    game_window.blit(logo_image, (logo_x, logo_y))
    pygame.display.flip()
    pygame.time.delay(4000)  # Display the logo for 2 seconds




def main():
    pygame.init()

    # Set up the game window
    game_window, window_width, window_height = setup_game_window()
    pygame.display.set_caption('A Working Title')
   
    display_logo(game_window, window_width, window_height)

    game = Game(game_window, window_width, window_height)

    while True:
    #    for event in pygame.event.get():
    #        if event.type == QUIT:
    #            pygame.quit()
    #            sys.exit()

            # Get the current resolution
        current_resolution = (game_window.get_width(), game_window.get_height())
        
        if game.game_state == 'main menu':
            game.draw_menu()
            game.process_events()
            
            # Compare with the previous resolution
            if current_resolution != game.previous_resolution:
                game.previous_resolution = current_resolution
                game_window.fill((0, 0, 0))  # Clear the screen
                game.resize_ui(*current_resolution)  # Update UI positions

            
        elif game.game_state == 'ingame':
            game.update_resolution(game_window.get_width(), game_window.get_height())
            game.game_loop()

        #game state changes
        if game.start_game_clicked:
            game.game_state = 'ingame'
            game.start_game_clicked = False
            

        pygame.display.update()

        game.clock.tick(game.FPS)


if __name__ == '__main__':
    main()