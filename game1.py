import pygame
import os
from pygame.locals import *
import re
import sys
import inspect
import pygame_gui




def extract_direction_and_verb(text, accepted_verbs):
    direction_pattern = re.compile(r'\b(north|south|east|west|northeast|northwest|southeast|southwest)\b', re.IGNORECASE)

    match = direction_pattern.search(text)
    if match:
        direction = match.group().lower()
        verb = None
        return direction, verb

    for verb in accepted_verbs:
        if verb in text:
            direction_match = direction_pattern.search(text[text.index(verb):])
            if direction_match:
                direction = direction_match.group().lower()
                return direction, verb

    return None, None

class Level:
    def __init__(self, background_image_path, width, height):
        self.original_background = pygame.image.load(background_image_path).convert_alpha()
        self.background_image = pygame.transform.scale(self.original_background, (width, height))
        self.width = width
        self.height = height

    def scale_background(self, new_width, new_height):
        if (new_width, new_height) != (self.width, self.height):
            self.background_image = pygame.transform.scale(self.original_background, (new_width, new_height))
            self.width = new_width
            self.height = new_height



class Game:
    def __init__(self, game_window, width, height):
        self.width = width
        self.height = height
        self.in_start_menu = True
        self.background_colour = pygame.Color("#F0F0F0")
        self.game_window = game_window
        self.main_menu = MainMenu(game_window, width, height)
        self.waiting_for_quit = False
        self.quitting_confirmation = False  # Flag to determine if player confirmed quitting
        self.quitting = False
        self.levels = {}
        self.previous_resolution = (width, height)  # Add a variable to track previous resolution
        self.current_level_key = 'default'  # starting level
        self.load_levels()
        self.clock = pygame.time.Clock()
        self.FPS = 60
        self.game_state = 'main menu'
        self.input_text = ''
        self.output_text = ''
        self.directions = {
            "north": "level1",
            "south": "level2",
            "east": "level3",
            "west": "level4",
            "north-east": "level5",
            "north-west": "level6",
            "south-east": "level7",
            "south-west": "level8",
        }
        self.player_position = "default"  
        # Add the 'settings' level key
        self.levels["settings"] = Level(os.path.join('assets', 'settings_background.png'), self.width, self.height)
        self.main_menu.create_ui()
    
    


class SettingsMenu:
    def __init__(self, game_window, width, height, main_menu):
        self.game_window = game_window
        self.width = width
        self.height = height
        self.manager = pygame_gui.UIManager((width, height), 'data/themes/button_theming_test_theme.json')
        self.clock = pygame.time.Clock()
        self.background = pygame.Surface((width, height))
        self.background.fill(self.manager.get_theme().get_colour('dark_bg'))
        self.running = True
        self.options = {
            "#resolution": "Resolution",
            "#fps": "FPS",
            "#back": "Back"  # Add the "Back" button
        }

        self.main_menu = main_menu  # Store the reference to the MainMenu instance

        self.create_buttons()
        self.create_resolution_dropdown()
    
    def create_resolution_dropdown(self):
        center_x = self.width // 2
        center_y = self.height // 2
        button_width = 200
        button_height = 40
        spacing = 20

        resolution_options = ["800x600", "1024x768", "1280x720", "1920x1080"]
        
        # Add the "Resolution" label
        resolution_label_pos = (center_x - button_width // 2, center_y - button_height * 3 - spacing)
        resolution_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(resolution_label_pos, (button_width, button_height)),
            text="Resolution",
            manager=self.manager,
            object_id="#resolution_label"
        )

        # Add the resolution dropdown
        dropdown_pos = (center_x - button_width // 2, center_y - button_height - spacing)
        self.resolution_dropdown = pygame_gui.elements.UIDropDownMenu(
            relative_rect=pygame.Rect(dropdown_pos, (button_width, button_height)),
            options_list=resolution_options,
            starting_option="800x600",
            manager=self.manager,
            object_id="#resolution_dropdown"
        )
        self.resolution_dropdown.set_relative_position(
            (center_x - button_width // 2, center_y - button_height - spacing)
        )

    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                self.running = False
            self.manager.process_events(event)

            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.back_button:
                    self.return_to_main_menu()
                # Add any other button events you want to handle here

            if event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
                if event.ui_element == self.resolution_dropdown:
                    self.check_resolution_changed()



    def resize_window(self, new_width, new_height):
        self.width = new_width
        self.height = new_height
        self.game_window = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
        self.manager.set_window_resolution((self.width, self.height))
        self.manager.clear_and_reset()
        self.background = pygame.Surface((self.width, self.height))
        self.background.fill(self.manager.get_theme().get_colour('dark_bg'))
        pygame.display.flip()

        # Recreate and reposition UI components
        self.create_buttons()
        self.create_resolution_dropdown()  # Recreate the resolution dropdown

        # Update positions of other UI components as needed
        center_x = self.width // 2
        center_y = self.height // 2
        button_width = 200
        button_height = 40
        spacing = 20

        # Update the back button position
        self.back_button.set_relative_position(
            (center_x - button_width // 2, center_y + button_height // 2)
        )
        # Update positions of other UI components as needed


    def check_resolution_changed(self):
        resolution_string = self.resolution_dropdown.selected_option.split('x')
        resolution_width = int(resolution_string[0])
        resolution_height = int(resolution_string[1])
        # Handle resolution change (e.g., apply new resolution to the game window)
        self.resize_window(resolution_width, resolution_height)
        

    def create_buttons(self):
        # Calculate the center position of the screen
        center_x = self.width // 2
        center_y = self.height // 2

        button_width = 200
        button_height = 40
        spacing = 20

        # Resolution dropdown


        # Back button
        back_button_pos = (center_x - button_width // 2, center_y + button_height // 2)
        self.back_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(back_button_pos, (button_width, button_height)),
            text="Back",
            manager=self.manager,
            object_id="#back"  # Button ID from the theme file
        )





    def run(self):
        while self.running:
            delta_time = self.clock.tick(60) / 1000.0
            self.process_events()

            self.game_window.blit(self.background, (0, 0))
            self.manager.update(delta_time)
            self.manager.draw_ui(self.game_window)
            pygame.display.flip()

            if not self.running:
                self.manager.clear_and_reset()


    def return_to_main_menu(self):
        self.running = False
        self.manager.clear_and_reset()
        pygame.display.flip()


class MainMenu:
    def __init__(self, game_window, width, height):
        self.game_window = game_window
        self.width = width
        self.height = height
        self.manager = pygame_gui.UIManager((width, height), 'data/themes/button_theming_test_theme.json')
        self.clock = pygame.time.Clock()
        self.background = pygame.Surface((width, height))
        self.background.fill(self.manager.get_theme().get_colour('dark_bg'))
        self.running = True
        self.start_game_clicked = False

        self.menu_options = {
            "#new_game": "New Game",
            "#load_game": "Load Game",
            "#settings": "Settings",
            "#quit": "Quit"
        }



    def create_ui(self):
        center_x = self.width // 2
        center_y = self.height // 2
        button_width = 200
        button_height = 40
        spacing = 20

        # Create UI components
        self.ui_components = {
            "#new_game": pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect((center_x - button_width // 2, center_y - button_height * 2 - spacing),
                                          (button_width, button_height)),
                text="New Game",
                manager=self.manager,
                object_id="#new_game"
            ),
            "#load_game": pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect((center_x - button_width // 2, center_y - button_height // 2 - spacing),
                                          (button_width, button_height)),
                text="Load Game",
                manager=self.manager,
                object_id="#load_game"
            ),
            "#settings": pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect((center_x - button_width // 2, center_y + button_height // 2),
                                          (button_width, button_height)),
                text="Settings",
                manager=self.manager,
                object_id="#settings"
            ),
            "#quit": pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect((center_x - button_width // 2, center_y + button_height * 1.5 + spacing),
                                          (button_width, button_height)),
                text="Quit",
                manager=self.manager,
                object_id="#quit"
            )
        }

    def resize_ui(self, new_width, new_height):
        self.width = new_width
        self.height = new_height
        self.game_window = pygame.display.set_mode((self.width, self.height))
        self.manager.set_window_resolution((self.width, self.height))
        
        # Redraw the background with the updated size
        self.background = pygame.Surface((self.width, self.height))
        self.background.fill(self.manager.get_theme().get_colour('dark_bg'))

        # Clear old GUI elements
        self.manager.clear_and_reset()

        # Recreate and reposition UI components
        self.create_ui()


        # Update positions of UI components
        center_x = self.width // 2
        center_y = self.height // 2
        button_width = 200
        button_height = 40
        spacing = 20

        for ui_id, ui_component in self.ui_components.items():
                ui_component.set_relative_position(
                    (center_x - button_width // 2, center_y - button_height * 2 - spacing)
                )
                center_y += button_height + spacing


    def open_settings(self):
        self.running = False  # Set the flag to False to exit the main menu loop
        settings_menu = SettingsMenu(self.game_window, self.width, self.height, self)  # Pass the MainMenu instance
        settings_menu.run()



    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                self.running = False
            self.manager.process_events(event)
            

            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.ui_components["#new_game"]:
                    self.start_game_clicked = True
                elif event.ui_element == self.ui_components["#settings"]:
                    self.open_settings()
                elif event.ui_element == self.ui_components["#quit"]:
                    pygame.quit()
                    self.running = False




    def draw_menu(self):
        self.game_window.blit(self.background, (0, 0))
        self.manager.update(0)
        self.manager.draw_ui(self.game_window)
