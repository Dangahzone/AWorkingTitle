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
        self.manager = pygame_gui.UIManager((width, height), 'data/themes/button_theming_test_theme.json')
        self.clock = pygame.time.Clock()
        self.background = pygame.Surface((width, height))
        self.background.fill(self.manager.get_theme().get_colour('dark_bg'))
        self.mainmenurunning = True
        self.start_game_clicked = False
        self.menu_options = {
            "#new_game": "New Game",
            "#load_game": "Load Game",
            "#settings": "Settings",
            "#quit": "Quit"
        }
        self.settingsrunning = False
        self.settingsoptions = {
            "#resolution": "Resolution",
            "#fps": "FPS",
            "#back": "Back"  
        }
        self.running = True
        self.levels["settings"] = Level(os.path.join('assets', 'settings_background.png'), self.width, self.height)
        self.create_ui()

    
    
    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                self.mainmenurunning = False
            self.manager.process_events(event)
    
            

            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.ui_components["#new_game"]:
                    self.start_game_clicked = True
                elif event.ui_element == self.ui_components["#settings"]:
                    self.settingsrunning = True
                    self.mainmenurunning = False
                    self.manager.clear_and_reset()
                    self.create_buttons()
                    self.create_resolution_dropdown()
                elif event.ui_element == self.ui_components["#quit"]:
                    pygame.quit()
                    self.mainmenurunning = False

                elif event.ui_element == self.back_button:
                    self.return_to_main_menu()
                # Add any other button events you want to handle here

            if event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
                if event.ui_element == self.resolution_dropdown:
                    self.check_resolution_changed()







    def scale_background(self, new_width, new_height):
        if (new_width, new_height) != (self.width, self.height):
            self.background_image = pygame.transform.scale(self.original_background, (new_width, new_height))
            self.width = new_width
            self.height = new_height

    def update_resolution(self, new_width, new_height):
        self.width = new_width
        self.height = new_height
        self.game_window = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
        
        # Iterate through the levels and update their background images
        for level_key, level_instance in self.levels.items():
            level_instance.scale_background(self.width, self.height)  # Use the Level instance's method

    def initialize_levels(self):
        for level_instance in self.levels.values():  # Iterate over values, not items
            level_instance.scale_background(self.width, self.height)
    
    def do_command(self, command):
        # Parse command into verb and direction
        direction, verb = extract_direction_and_verb(command, ["go", "move", "travel"])

        if verb and not direction:
            return "Invalid direction."

        if direction in self.directions:
            new_level = self.directions[direction]
            if new_level != self.current_level_key:
                self.player_position = new_level
                self.current_level_key = new_level
                return "You moved to the " + direction + "."
            else:
                return "You are already there."
        else:
            return "You can't go that way."


    def handle_game_input(self):
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            
            elif event.type == WINDOWRESIZED:
                self.width, self.height = self.width, self.height
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if self.input_text.strip():
                        return self.input_text.strip()
                    command = self.input_text.strip().lower()
                    if command == "quit":
                        self.quitting_confirmation = True
                        self.input_text = ""
                        return "Are you sure you want to quit? (yes/no)"
                        
                elif event.key == pygame.K_BACKSPACE:
                    self.input_text = self.input_text[:-1]
                elif event.unicode.isprintable():
                    self.input_text += event.unicode

        return ""


    def draw_objects(self):
        self.game_window.fill(self.background_colour)
        current_level = self.levels[self.current_level_key]
        bg_rect = current_level.background_image.get_rect(center=(self.width // 2, self.height // 2))
        self.game_window.blit(current_level.background_image, bg_rect)
        self.draw_player_position()

        # Render input text on the screen
        font = pygame.font.Font(None, 24)
        input_text_surface = font.render(self.input_text, True, (255, 255, 255))
        input_text_rect = input_text_surface.get_rect(topleft=(10, self.height - 30))
        self.game_window.blit(input_text_surface, input_text_rect)

        # Display the quit message in the center of the screen
        if self.quitting_confirmation:
            quit_message = "Are you sure you want to quit? (yes/no)"
            quit_font = pygame.font.Font(None, 36)
            quit_surface = quit_font.render(quit_message, True, (255, 255, 255))
            quit_rect = quit_surface.get_rect(center=(self.width // 2, self.height // 2))
            self.game_window.blit(quit_surface, quit_rect)


    def game_loop(self):
        send_input = self.handle_game_input()

        if send_input:

            if self.quitting_confirmation:
                if self.input_text.lower() == "yes":
                    self.game_state = 'main menu'
                else:
                    self.quitting_confirmation = False
            else:
                # Parse all the commands and handle them
                commands = self.input_text.split(';')
                for command in commands:
                    command = command.strip()
                    if command.lower() == "quit":
                        self.quitting_confirmation = True
                    elif command.lower() == "look":
                        self.output_text = f"You are currently at: {self.player_position}."
                    else:
                        self.output_text = self.do_command(command)

                    if self.output_text:
                        self.display_message(self.output_text)
                        pygame.time.delay(2000)
                        self.output_text = ""

                self.input_text = ""


        self.draw_objects()
        pygame.display.flip()

        if self.quitting:
            in_game = False

        self.clock.tick(self.FPS)    







    def update_player_position(self, command):
        direction, verb = extract_direction_and_verb(command, ["go", "move", "travel"])

        if not verb and not direction:
            return "Invalid command."

        if verb and not direction:
            return "Invalid direction."

        if direction in self.directions:
            new_level = self.directions[direction]
            if new_level != self.current_level_key:
                self.player_position = new_level
                self.current_level_key = new_level
                return "You moved to the " + direction + "."
            else:
                return "You are already there."
        else:
            return "You can't go that way."
        

        
    def display_message(self, message):
        font = pygame.font.Font(None, 36)
        text_surface = font.render(message, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(self.width // 2, self.height // 2))
        self.game_window.blit(text_surface, text_rect)
        

    def display_output(self, output):
        font = pygame.font.Font(None, 24)
        text_surface = font.render(output, True, (255, 255, 255))
        text_rect = text_surface.get_rect(topleft=(10, 50))  # Position for displaying the output
        self.game_window.blit(text_surface, text_rect)
        pygame.display.update()


    def draw_player_position(self):
        font = pygame.font.Font(None, 36)
        text = font.render(f"Player Position: {self.player_position}", True, (255, 255, 255))
        text_rect = text.get_rect(topleft=(10, 10))
        self.game_window.blit(text, text_rect)

    def load_levels(self):
        level1_background = os.path.join('assets', 'level1_background.png')
        level2_background = os.path.join('assets', 'level2_background.png')
        level3_background = os.path.join('assets', 'level3_background.png')
        level4_background = os.path.join('assets', 'level4_background.png')
        level5_background = os.path.join('assets', 'level5_background.png')
        level6_background = os.path.join('assets', 'level6_background.png')
        level7_background = os.path.join('assets', 'level7_background.png')
        level8_background = os.path.join('assets', 'level8_background.png')
        default_background = os.path.join('assets', 'default_background.png')

        self.levels["level1"] = Level(level1_background, self.width, self.height)
        self.levels["level2"] = Level(level2_background, self.width, self.height)
        self.levels["level3"] = Level(level3_background, self.width, self.height)
        self.levels["level4"] = Level(level4_background, self.width, self.height)
        self.levels["level5"] = Level(level5_background, self.width, self.height)
        self.levels["level6"] = Level(level6_background, self.width, self.height)
        self.levels["level7"] = Level(level7_background, self.width, self.height)
        self.levels["level8"] = Level(level8_background, self.width, self.height)
        self.levels["default"] = Level(default_background, self.width, self.height)


    def change_level(self, level_key):
        if level_key in self.levels:
            self.current_level_key = level_key
            self.background_colour = pygame.Color("#F0F0F0")  # Reset background color on level change


    def quit_game(self):
        if self.waiting_for_quit:
            if self.input_text.lower() == "yes":
                self.quitting = True  # Set the quitting flag to True to exit the game loop
            self.waiting_for_quit = False
        elif self.quitting_confirmation:
            if self.input_text.lower() == "yes":
                self.waiting_for_quit = True
                self.display_message("Are you sure you want to quit? (yes/no)")
            else:
                self.quitting_confirmation = False
        else:
            pygame.quit()
            quit()


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




    def draw_menu(self):
        self.game_window.blit(self.background, (0, 0))
        self.manager.update(0)
        self.manager.draw_ui(self.game_window)
 



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


        center_x = self.width // 2
        center_y = self.height // 2
        button_width = 200
        button_height = 40
        spacing = 20


        self.back_button.set_relative_position(
            (center_x - button_width // 2, center_y + button_height // 2)
        )
        # Update positions of other UI components as needed


    def check_resolution_changed(self):
        resolution_string = self.resolution_dropdown.selected_option.split('x')
        resolution_width = int(resolution_string[0])
        resolution_height = int(resolution_string[1])
        self.resize_window(resolution_width, resolution_height)
        

    def create_buttons(self):
        # Calculate the center position of the screen
        center_x = self.width // 2
        center_y = self.height // 2

        button_width = 200
        button_height = 40
        spacing = 20




        back_button_pos = (center_x - button_width // 2, center_y + button_height // 2)
        self.back_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(back_button_pos, (button_width, button_height)),
            text="Back",
            manager=self.manager,
            object_id="#back"  
        )



    def return_to_main_menu(self):
        self.mainmenurunning = True
        self.manager.clear_and_reset()
        pygame.display.flip()




