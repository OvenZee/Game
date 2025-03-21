import pygame
import random
import sqlite3
import os
import mysql.connector


# tento příkaz nás připojí do databáze
def connect_db():
    mydb = mysql.connector.connect(
        host = "dbs.spskladno.cz"
        ,user = "student22"
        ,password = "spsnet"
        ,database = "vyuka22"
    )
    return mydb

pygame.font.init()

# GLOBALS VARS
s_width = 800
s_height = 700
play_width = 300  # meaning 300 // 10 = 30 width per block
play_height = 600  # meaning 600 // 20 = 30 height per block
block_size = 30

top_left_x = (s_width - play_width) // 2
top_left_y = s_height - play_height


win = pygame.display.set_mode((s_width, s_height))


# SHAPE FORMATS
S = [['.....',
      '.....',
      '..00.',
      '.00..',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '...0.',
      '.....']] 


Z = [['.....',
      '.....',
      '.00..',
      '..00.',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '.0...',
      '.....']]

I = [['..0..',
      '..0..',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '0000.',
      '.....',
      '.....',
      '.....']]

O = [['.....',
      '.....',
      '.00..',
      '.00..',
      '.....']]

J = [['.....',
      '.0...',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..00.',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '...0.',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '.00..',
      '.....']]

L = [['.....',
      '...0.',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '..00.',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '.0...',
      '.....'],
     ['.....',
      '.00..',
      '..0..',
      '..0..',
      '.....']]

T = [['.....',
      '..0..',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '..0..',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '..0..',
      '.....']]

shapes = [S, Z, I, O, J, L, T]
shape_colors = [(0, 255, 0), (255, 0, 0), (0, 255, 255), (255, 255, 0), (255, 165, 0), (0, 0, 255), (128, 0, 128)]  # index 0 - 6 represent shape

def update_score(player_id, score):  # Update the score and save to DB
    connection = connect_db()
    cursor = connection.cursor()

    try:
        # Insert the score into the 1score table
        cursor.execute("""
            INSERT INTO `1score` (player_id, score)
            VALUES (%s, %s)
            """, (player_id, score))

        connection.commit()
        print(f"Score {score} for player {player_id} inserted successfully.")

    except mysql.connector.Error as err:
        print(f"Error: {err}")

    finally:
        cursor.close()
        connection.close()







class Piece(object):  # class for the pieces
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = shape_colors[shapes.index(shape)]
        self.rotation = 0

def create_grid(locked_pos={}):  # This makes it easier to draw where the piecies are
    grid = [[(0,0,0) for _ in range(10)] for _ in range(20)]

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if (j, i) in locked_pos:
                c = locked_pos[(j,i)]
                grid[i][j] = c
    return grid


def convert_shape_format(shape):  # this converts the shape formats into shapes the computer understands
    positions = []
    format = shape.shape[shape.rotation % len(shape.shape)]

    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                positions.append((shape.x + j, shape.y + i))

    for i, pos in enumerate(positions):
        positions[i] = (pos[0] - 2, pos[1] - 4)

    return positions


def valid_space(shape, grid): # this checks if the space is valid for being entered
    accepted_pos = [[(j, i) for j in range(10) if grid[i][j] == (0,0,0)] for i in range(20)]
    accepted_pos = [j for sub in accepted_pos for j in sub]

    formatted = convert_shape_format(shape)

    for pos in formatted:
        if pos not in accepted_pos:
            if pos[1] > -1:
                return False
    return True


def check_lost(positions): # does what it says it does 
    for pos in positions:
        x, y = pos
        if y < 1:
            return True

    return False

def get_shape(): # this is how we get random shapes
    return Piece(5, 0, random.choice(shapes))

def draw_text_middle(surface, text, size, color): # just here to make it easier to display text in the middle of the screen when we need it
    font = pygame.font.SysFont("comicsans", size, bold=True)
    label = font.render(text, 1, color)

    surface.blit(label, (top_left_x + play_width /2 - (label.get_width()/2), top_left_y + play_height/2 - label.get_height()/2))


def draw_grid(surface, grid): # this draws the grey grid lines to make the game better visually
    sx = top_left_x
    sy = top_left_y

    for i in range(len(grid)):
        pygame.draw.line(surface, (128,128,128), (sx, sy + i*block_size), (sx+play_width, sy+ i*block_size))
        for j in range(len(grid[i])):
            pygame.draw.line(surface, (128, 128, 128), (sx + j*block_size, sy),(sx + j*block_size, sy + play_height))


def clear_rows(grid, locked): # this is how we clear the rows by checking if a row is full and also check for how many rows we cleared

    inc = 0
    for i in range(len(grid)-1, -1, -1):
        row = grid[i]
        if (0,0,0) not in row:
            inc += 1
            ind = i
            for j in range(len(row)):
                try:
                    del locked[(j,i)]
                except:
                    continue

    if inc > 0:
        for key in sorted(list(locked), key=lambda x: x[1])[::-1]:
            x, y = key
            if y < ind:
                newKey = (x, y + inc)
                locked[newKey] = locked.pop(key)

    return inc


def draw_next_shape(shape, surface): # this displays the next shape that youre gonna get
    font = pygame.font.SysFont('comicsans', 30)
    label = font.render('Next Shape', 1, (255,255,255))

    sx = top_left_x + play_width + 50
    sy = top_left_y + play_height/2 - 100
    format = shape.shape[shape.rotation % len(shape.shape)]

    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                pygame.draw.rect(surface, shape.color, (sx + j*block_size, sy + i*block_size, block_size, block_size), 0)

    surface.blit(label, (sx + 10, sy - 30))





# Function to handle login screen
def login_screen(win):
    """Displays the login screen where users can log in with their credentials."""
    run = True
    username = ''
    password = ''
    active_field = 'username'  # 'username' or 'password'
    color_inactive = (150, 150, 150)
    color_active = (0, 255, 0)
    input_box_username = pygame.Rect(200, 200, 140, 32)
    input_box_password = pygame.Rect(200, 250, 140, 32)
    color_username = color_inactive
    color_password = color_inactive

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.display.quit()
            if event.type == pygame.KEYDOWN:
                if active_field == 'username':
                    if event.key == pygame.K_BACKSPACE:
                        username = username[:-1]
                    elif event.key == pygame.K_RETURN:
                        active_field = 'password'  # Switch to password input
                    else:
                        username += event.unicode
                elif active_field == 'password':
                    if event.key == pygame.K_BACKSPACE:
                        password = password[:-1]
                    elif event.key == pygame.K_RETURN:
                        # Check credentials in the database
                        connection = connect_db()
                        cursor = connection.cursor()
                        cursor.execute("SELECT * FROM `1users` WHERE username = %s AND password = %s", (username, password))
                        result = cursor.fetchone()
                        if result:
                            print("Login successful!")
                            return username  # Return the username of the logged-in user
                        else:
                            print("Invalid credentials")
                            username = ''
                            password = ''
                            active_field = 'username'  # Go back to username input
                    else:
                        password += event.unicode

        # Fill screen with black
        win.fill((0, 0, 0))

        # Title
        font = pygame.font.SysFont("comicsans", 60)
        label = font.render("Login", 1, (255, 255, 255))
        win.blit(label, (top_left_x + play_width / 2 - (label.get_width() / 2), top_left_y + 50))

        # Username input box
        if active_field == 'username':
            color_username = color_active
        else:
            color_username = color_inactive

        draw_input_box(win, username, input_box_username, color_username)

        # Password input box
        if active_field == 'password':
            color_password = color_active
        else:
            color_password = color_inactive

        draw_input_box(win, '*' * len(password), input_box_password, color_password)

        # Button for login
        pygame.display.update()



def register_screen(win):
    """Displays the register screen where new users can create an account."""
    run = True
    username = ''
    password = ''
    active_field = 'username'  # 'username' or 'password'
    color_inactive = (150, 150, 150)
    color_active = (0, 255, 0)
    input_box_username = pygame.Rect(200, 200, 140, 32)
    input_box_password = pygame.Rect(200, 250, 140, 32)
    color_username = color_inactive
    color_password = color_inactive

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.display.quit()
            if event.type == pygame.KEYDOWN:
                if active_field == 'username':
                    if event.key == pygame.K_BACKSPACE:
                        username = username[:-1]
                    elif event.key == pygame.K_RETURN:
                        active_field = 'password'  # Switch to password input
                    else:
                        username += event.unicode
                elif active_field == 'password':
                    if event.key == pygame.K_BACKSPACE:
                        password = password[:-1]
                    elif event.key == pygame.K_RETURN:
                        # Register the new user in the database
                        connection = connect_db()
                        cursor = connection.cursor()
                        try:
                            cursor.execute("INSERT INTO `1users` (username, password) VALUES (%s, %s)", (username, password))
                            connection.commit()
                            print("Registration successful!")
                            return username  # Return the newly registered username
                        except mysql.connector.Error as err:
                            print(f"Error: {err}")
                            username = ''
                            password = ''
                            active_field = 'username'  # Go back to username input
                    else:
                        password += event.unicode

        # Fill screen with black
        win.fill((0, 0, 0))

        # Title
        font = pygame.font.SysFont("comicsans", 60)
        label = font.render("Register", 1, (255, 255, 255))
        win.blit(label, (top_left_x + play_width / 2 - (label.get_width() / 2), top_left_y + 50))

        # Username input box
        if active_field == 'username':
            color_username = color_active
        else:
            color_username = color_inactive

        draw_input_box(win, username, input_box_username, color_username)

        # Password input box
        if active_field == 'password':
            color_password = color_active
        else:
            color_password = color_inactive

        draw_input_box(win, '*' * len(password), input_box_password, color_password)

        # Button for registration
        pygame.display.update()

def gt_id(username):
    connection = connect_db()
    cursor = connection.cursor()
    cursor.execute("SELECT id FROM 1users WHERE username = %s", (username,))
    result = cursor.fetchone()
    if result:
        return result[0]  # Return player ID
    else:
        print("Player not found!")
        return None

def draw_input_box(win, text, box, color):
    """Helper function to draw the input box."""
    pygame.draw.rect(win, color, box, 2)
    font = pygame.font.SysFont("comicsans", 32)
    txt_surface = font.render(text, True, (255, 255, 255))
    win.blit(txt_surface, (box.x + 5, box.y + 5))


# Function to save score to the database
def save_score(username, score):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS scores (
                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                      username TEXT NOT NULL,
                      points INTEGER NOT NULL)''')

    cursor.execute("INSERT INTO scores (username, points) VALUES (?, ?)", (username, score))
    conn.commit()
    conn.close()

def main_menu(win): 
    run = True
    while run:
        action = menu_screen(win)  # Získáme akci, kterou uživatel zvolil.
        
        if action == 'start':
            username = login_screen(win)  # Získejte uživatelské jméno po přihlášení
            if username:
                main(win, username)  # Začíná hra
                break  # Ukončíme menu po zahájení hry

        elif action == 'register':
            username = register_screen(win)  # Získejte nové uživatelské jméno po registraci
            if username:
                print(f"Welcome, {username}!")  # Zobrazí pozdrav po registraci
                main(win, username)  # Začíná hra po registraci
                break  # Ukončíme menu po registraci a zahájení hry

        elif action == None:  # Pokud uživatel klikne na 'Quit'
            run = False
            pygame.display.quit()

def draw_window(surface, grid, score=0, last_score = 0):
    surface.fill((0, 0, 0))

    pygame.font.init()
    font = pygame.font.SysFont('comicsans', 60)
    label = font.render('Tetris', 1, (255, 255, 255))

    surface.blit(label, (top_left_x + play_width / 2 - (label.get_width() / 2), 30))

    # current score
    font = pygame.font.SysFont('comicsans', 30)
    label = font.render('Score: ' + str(score), 1, (255,255,255))

    sx = top_left_x + play_width + 50
    sy = top_left_y + play_height/2 - 100

    surface.blit(label, (sx + 20, sy + 160))
    # last score
    label = font.render('High Score: ' + str(last_score), 1, (255, 255, 255))


    sx = top_left_x - 200
    sy = top_left_y + 200

    surface.blit(label, (sx + 20, sy + 160))

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            pygame.draw.rect(surface, grid[i][j], (top_left_x + j*block_size, top_left_y + i*block_size, block_size, block_size), 0)

    pygame.draw.rect(surface, (255, 0, 0), (top_left_x, top_left_y, play_width, play_height), 5)

    draw_grid(surface, grid)
    #pygame.display.update()

def menu_screen(win):
    """Displays the main menu with options to start game, login, register, or quit."""
    run = True
    while run:
        # Fill the screen with black
        win.fill((0, 0, 0))

        # Title
        font = pygame.font.SysFont("comicsans", 60)
        label = font.render("TETRIS GAME", 1, (255, 255, 255))
        win.blit(label, (top_left_x + play_width / 2 - (label.get_width() / 2), top_left_y + 50))

        # Menu options
        font = pygame.font.SysFont("comicsans", 40)
        start_text = font.render("Start Game", 1, (255, 255, 255))
        register_text = font.render("Register", 1, (255, 255, 255))
        quit_text = font.render("Quit", 1, (255, 255, 255))

        # Buttons
        start_button = pygame.Rect(top_left_x + play_width / 2 - 100, top_left_y + 150, 200, 50)
        register_button = pygame.Rect(top_left_x + play_width / 2 - 100, top_left_y + 220, 200, 50)
        quit_button = pygame.Rect(top_left_x + play_width / 2 - 100, top_left_y + 290, 200, 50)

        # Draw buttons
        pygame.draw.rect(win, (0, 255, 0), start_button)
        pygame.draw.rect(win, (0, 0, 255), register_button)
        pygame.draw.rect(win, (255, 0, 0), quit_button)

        # Draw text on buttons
        win.blit(start_text, (start_button.x + 50, start_button.y + 10))
        win.blit(register_text, (register_button.x + 50, register_button.y + 10))
        win.blit(quit_text, (quit_button.x + 50, quit_button.y + 10))

        pygame.display.update()

        # Event handling for button clicks
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.display.quit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()

                # Check if 'Start Game' button is clicked
                if start_button.collidepoint(mouse_x, mouse_y):
                    return 'start'

                # Check if 'Register' button is clicked
                if register_button.collidepoint(mouse_x, mouse_y):
                    return 'register'

                # Check if 'Quit' button is clicked
                if quit_button.collidepoint(mouse_x, mouse_y):
                    run = False
                    pygame.display.quit()

    return None  # Return None if no button clicked


# Main Game Loop
def main(win, username):  # game loop
    locked_positions = {}
    grid = create_grid(locked_positions)

    change_piece = False
    run = True
    current_piece = get_shape()
    next_piece = get_shape()
    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = 0.27
    level_time = 0
    score = 0
    player_id = None  # Initialize player_id

    while run:
        # If player hasn't logged in yet, ask for login
        if player_id is None:
            player_id = gt_id(username)

        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime()
        level_time += clock.get_rawtime()
        clock.tick()

        if level_time / 1000 > 5:
            level_time = 0
            if level_time > 0.12:
                level_time -= 0.005

        if fall_time / 1000 > fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not(valid_space(current_piece, grid)) and current_piece.y > 0:
                current_piece.y -= 1
                change_piece = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.display.quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not(valid_space(current_piece, grid)):
                        current_piece.x += 1
                if event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if not(valid_space(current_piece, grid)):
                        current_piece.x -= 1
                if event.key == pygame.K_DOWN:
                    current_piece.y += 1
                    if not(valid_space(current_piece, grid)):
                        current_piece.y -= 1
                if event.key == pygame.K_UP:
                    current_piece.rotation += 1
                    if not(valid_space(current_piece, grid)):
                        current_piece.rotation -= 1

        shape_pos = convert_shape_format(current_piece)

        for i in range(len(shape_pos)):
            x, y = shape_pos[i]
            if y > -1:
                grid[y][x] = current_piece.color

        if change_piece:
            for pos in shape_pos:
                p = (pos[0], pos[1])
                locked_positions[p] = current_piece.color
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False
            score += clear_rows(grid, locked_positions) * 10

        draw_window(win, grid, score)
        draw_next_shape(next_piece, win)
        pygame.display.update()

        if check_lost(locked_positions):
            draw_text_middle(win, "YOU LOST!", 80, (255,255,255))
            pygame.display.update()
            pygame.time.delay(1500)
            run = False
            if player_id is not None:  # Make sure the player_id is not None
                update_score(player_id, score)  # Save the player's score


# Start the game
pygame.display.set_caption('Tetris')
main_menu(win)

# Start the game

pygame.display.set_caption('Tetris')
main_menu(win)
