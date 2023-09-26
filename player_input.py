import pygame

def get_player_input(game_window, input_text):

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                input_text = input_text[:-1]
            elif event.key == pygame.K_q:
                return "quit"
            else:
                input_text += event.unicode
                print(input_text)


    pygame.display.update()
    return input_text