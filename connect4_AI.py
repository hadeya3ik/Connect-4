import math
import numpy as np
import pygame
import random
import sys

ROW = 6
COL = 7
SQUARESIZE = 100
RADIUS = int(SQUARESIZE /2 -5)
HEIGHT = (ROW + 1) * SQUARESIZE + 100
WIDTH = COL * SQUARESIZE + 100

BG_COLOUR = (41,50,65,255)
BUTTON_COLOUR = (155,195,219)
CIRCLE_COLOUR = (92,116,148)
AI_COLOUR =  (234,107,76)
PLAYER_COLOUR =  (124,202,179)
BOARD_COLOUR = (76,105,140)

BUTTON_WIDTH = 425 
BUTTON_HEIGHT = 50 
BUTTON_X = 180 
BUTTON_Y = 250
PADDING = 100 

EASY_MODE = 1 
MEDIUM_MODE = 3 
HARD_MODE = 5

MIN =  -10000000000000
MAX = 100000000000000

#player 2 is yellow and is the AI

def init_board():
    board = np.zeros((ROW, COL), dtype="int32")
    return board

def get_sym(n):
    symbol_map = {1: 'X', 2: 'O'}
    return symbol_map.get(n, ' ')

def print_board(board):
    print(" ", end="")
    for i in range(1, COL + 1):
        print("[" + str(i) + "] ", end="")
    print("")
    for i in range(ROW):
        print("|", end=" ")
        for j in range(COL):
            symbol = get_sym(board[i, j])
            print(symbol, "|", end=" ")
        print("")
    print()

def move(board, player, col_pos):
    col_pos -= 1
    arr = (board[:, col_pos])[::-1]
    empty_indices = np.where(arr == 0)
    if len(empty_indices[0]) != 0:
        col_index = ROW - empty_indices[0][0]
        board[col_index - 1, col_pos] = player
        return True
    else:
        return False

def is_winning(row):
    return np.all(row == 1) or np.all(row == 2)

def check_win(board):
    # diagonal
    for i in range(ROW - 3):
        for j in range(COL - 3):
            if is_winning(board[np.arange(i, i + 4), np.arange(j, j + 4)]) or \
                    is_winning(board[np.arange(i, i + 4), np.arange(j + 3, j - 1, -1)]):
                return True

    # horizontal
    for i in range(ROW):
        for j in range(COL - 3):
            if is_winning(board[i, j:j + 4]):
                return True

    # vertical
    for i in range(COL):
        for j in range(ROW - 3):
            if is_winning(board[j:j + 4, i]):
                return True
    return False

def get_empty_col(board): 
    arr = []
    for i in range(1, COL + 1): 
        if move(board, 0, i): 
            arr.append(i)
    return arr

def eval_score(arr, player, level):
    score = -1000
    if (np.count_nonzero(arr == player) == 4): 
        score += 100
    elif ((np.count_nonzero(arr == player) == 3) and (np.count_nonzero(arr == 0) == 1)): 
        score += 5
    elif ((np.count_nonzero(arr == player) == 2) and (np.count_nonzero(arr == 0) == 2)): 
        score += 2

    opp_player = 1 
    if player == 1: 
        opp_player += 1 

    if ((np.count_nonzero(arr == opp_player) == 3) and (np.count_nonzero(arr == 0) == 1)):
        score -= 4
        if level == HARD_MODE: 
            score -= 2
        elif level == MEDIUM_MODE: 
            score -= 1

    return score
    
def score_position(board, player, level):
    '''gives the score of the board'''
    score = 0
    #if level != EASY_MODE: 
    score += np.count_nonzero(board[:, COL // 2] == player) * 6

    # diagonal
    for i in range(ROW - 3):
        for j in range(COL - 3):
            score += eval_score(board[np.arange(i, i + 4), np.arange(j, j + 4)], player, level)
            score += eval_score(board[np.arange(i, i + 4), np.arange(j + 3, j - 1, -1)], player, level)

    # horizontal
    for i in range(ROW):
        for j in range(COL - 3):
            score += eval_score(board[i, j:j + 4], player, level)

    # vertical
    for i in range(COL):
        for j in range(ROW - 3):
            score += eval_score(board[j:j + 4, i], player, level)

    return score

def terminal(board):
    valid_locations = get_empty_col(board)
    for col in valid_locations:
        for player in [2, 1]:
            temp = np.copy(board)
            move(temp, player, col)
            if is_winning(temp):
                return True
    return False
     
def minimax(board, depth, alpha, beta, maximizingPlayer, future_depth):
    empty_cols = get_empty_col(board)
    if depth == 0 or terminal(board):
        if terminal(board):
            for col in empty_cols:
                for player in [2, 1]:
                    temp = np.copy(board)
                    move(temp, player, col)
                    if is_winning(temp):
                        return (None, MAX) if player == 2 else (None, MIN)
            return (None, 0)
        else:
            return (None, score_position(board, 2, future_depth))
    if maximizingPlayer:
        value = -math.inf
        column = random.choice(empty_cols)
        for col in empty_cols:
            temp = np.copy(board)
            move(temp, 2, col)
            score = minimax(temp, depth - 1, alpha, beta, False, future_depth)[1]
            if score > value:
                value = score
                column = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return column, value
    else:  # Minimizing player
        value = math.inf
        column = random.choice(empty_cols)
        for col in empty_cols:
            temp = np.copy(board)
            move(temp, 1, col)
            score = minimax(temp, depth - 1, alpha, beta, True, future_depth)[1]
            if score < value:
                value = score
                column = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return column, value

def display_board(screen, board):
    pygame.draw.rect(screen, BUTTON_COLOUR, (25, SQUARESIZE + 25, SQUARESIZE * COL + 50, SQUARESIZE * ROW + 50))
    for c in range(COL):
        for r in range(ROW):
            rect_x = c * SQUARESIZE + 50
            rect_y = (r + 1) * SQUARESIZE + 50
            circle_x = int(rect_x + SQUARESIZE / 2)
            circle_y = int(rect_y + SQUARESIZE / 2)
            pygame.draw.rect(screen, BOARD_COLOUR, (rect_x, rect_y, SQUARESIZE, SQUARESIZE))

            if board[r][c] == 0:
                pygame.draw.circle(screen, CIRCLE_COLOUR, (circle_x, circle_y), RADIUS)
            elif board[r][c] == 1:
                pygame.draw.circle(screen, AI_COLOUR, (circle_x, circle_y), RADIUS)
            elif board[r][c] == 2:
                pygame.draw.circle(screen, PLAYER_COLOUR, (circle_x, circle_y), RADIUS)
    pygame.display.update()

def display_win(screen, player):
    pygame.time.wait(500)
    pygame.draw.rect(screen, BG_COLOUR, (0,0,WIDTH, SQUARESIZE))
    pygame.draw.rect(screen, BG_COLOUR, (25, SQUARESIZE + 25, SQUARESIZE * COL + 50, SQUARESIZE * ROW + 50))
    pygame.display.update()
    
    if player == 2:
        text_color = AI_COLOUR 
    elif player == 1:
        text_color = PLAYER_COLOUR
    
    font = pygame.font.Font("Pokemon GB.ttf", 32)
    text = font.render("Player " + str(player) + " wins!", True, text_color)
    text_rect = text.get_rect(center=(WIDTH // 2, (SQUARESIZE * ROW + 200) // 2))
    
    screen.blit(text, text_rect)
    pygame.display.update()
    pygame.time.wait(1000)
    pygame.display.update()
    exit(sys)

def start_game(screen, play_with_ai, ai_depth):
    game_over = False
    board = init_board()
    display_board(screen, board)
    player = random.randint(1,2)
    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEMOTION:
                pygame.draw.rect(screen, BG_COLOUR, (0,0,WIDTH, SQUARESIZE))
                posx = event.pos[0]
                if (player == 2):
                    pygame.draw.circle(screen, PLAYER_COLOUR, (posx, int(SQUARESIZE/2)), RADIUS) 
                if not(play_with_ai) and player == 1: 
                    pygame.draw.circle(screen, AI_COLOUR, (posx, int(SQUARESIZE/2)), RADIUS) 
                    
            pygame.display.update() 

            if event.type == pygame.MOUSEBUTTONDOWN:
                print(event.pos)
                posx = event.pos[0] - 50
                col = int(math.floor(posx / SQUARESIZE)) + 1
                move(board, player, col)
                if check_win(board): 
                    print("player", player, "wins!")
                    game_over = True
                print_board(board)
                display_board(screen, board)
                player = 2 if player == 1 else 1
                if play_with_ai: 
                    print("AI's turn")

        # AI
        if play_with_ai : 
            if (player == 1) and not game_over:
                print("AI's turn")
                col = minimax(board, ai_depth, -math.inf, math.inf, True, ai_depth)[0]
                if col == None : 
                    col = random.randint(1,2)
                pygame.time.wait(100)
                move(board, player, col)
                if check_win(board): 
                    print("player", player, "wins!")
                    game_over = True
                print_board(board)
                display_board(screen, board)
                player = 2 if player == 1 else 1

    if game_over:
        pass
        display_win(screen, player)

def display_level(screen):
    screen.fill(BG_COLOUR)
    font = pygame.font.Font("Pokemon GB.ttf", 24)
    
    easy_button_color = BUTTON_COLOUR
    medium_button_color = BUTTON_COLOUR
    hard_button_color = BUTTON_COLOUR

    easy_text = font.render("Easy", True, BG_COLOUR)
    medium_text = font.render("Medium", True, BG_COLOUR)
    hard_text = font.render("Hard", True, BG_COLOUR)

    easy_button_rect = pygame.Rect(BUTTON_X, BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT)
    medium_button_rect = pygame.Rect(BUTTON_X, BUTTON_Y + PADDING, BUTTON_WIDTH, BUTTON_HEIGHT)
    hard_button_rect = pygame.Rect(BUTTON_X, BUTTON_Y + PADDING*2, BUTTON_WIDTH, BUTTON_HEIGHT)

    easy_text_rect = easy_text.get_rect(center=easy_button_rect.center)
    medium_text_rect = medium_text.get_rect(center=medium_button_rect.center)
    hard_text_rect = hard_text.get_rect(center=hard_button_rect.center)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if easy_button_rect.collidepoint(event.pos):
                    start_game(screen, True, EASY_MODE)
                elif medium_button_rect.collidepoint(event.pos):
                    start_game(screen, True, MEDIUM_MODE)
                elif hard_button_rect.collidepoint(event.pos):
                    start_game(screen, True, HARD_MODE)
                break

        # Check if the mouse is hovering over each button
        if easy_button_rect.collidepoint(pygame.mouse.get_pos()):
            easy_button_color = AI_COLOUR
        else:
            easy_button_color = BUTTON_COLOUR

        if medium_button_rect.collidepoint(pygame.mouse.get_pos()):
            medium_button_color = AI_COLOUR
        else:
            medium_button_color = BUTTON_COLOUR

        if hard_button_rect.collidepoint(pygame.mouse.get_pos()):
            hard_button_color = AI_COLOUR
        else:
            hard_button_color = BUTTON_COLOUR

        # Draw buttons with updated colors
        pygame.draw.rect(screen, easy_button_color, easy_button_rect)
        pygame.draw.rect(screen, medium_button_color, medium_button_rect)
        pygame.draw.rect(screen, hard_button_color, hard_button_rect)

        # Blit button text on top of the buttons
        screen.blit(easy_text, easy_text_rect)
        screen.blit(medium_text, medium_text_rect)
        screen.blit(hard_text, hard_text_rect)

        pygame.display.update()

def display_home_screen(screen):
    screen.fill(BG_COLOUR)
    font = pygame.font.Font("Pokemon GB.ttf", 24)

    singleplayer_button_rect = pygame.Rect(BUTTON_X, BUTTON_X + PADDING + PADDING // 3, BUTTON_WIDTH, BUTTON_HEIGHT)
    multiplayer_button_rect = pygame.Rect(BUTTON_X, BUTTON_X + PADDING * 2 + PADDING // 3, BUTTON_WIDTH, BUTTON_HEIGHT)
    singleplayer_button_color = BUTTON_COLOUR
    multiplayer_button_color = BUTTON_COLOUR

    singleplayer_text = font.render("MultiPlayer", True, BG_COLOUR)
    multiplayer_text = font.render("Single player", True, BG_COLOUR)
    singleplayer_text_rect = singleplayer_text.get_rect(center=singleplayer_button_rect.center)
    multiplayer_text_rect = multiplayer_text.get_rect(center=multiplayer_button_rect.center)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if singleplayer_button_rect.collidepoint(event.pos):
                    start_game(screen, False, None)
                elif multiplayer_button_rect.collidepoint(event.pos):
                    display_level(screen)
                break

        if singleplayer_button_rect.collidepoint(pygame.mouse.get_pos()):
            singleplayer_button_color = AI_COLOUR
        else:
            singleplayer_button_color = BUTTON_COLOUR

        if multiplayer_button_rect.collidepoint(pygame.mouse.get_pos()):
            multiplayer_button_color = AI_COLOUR
        else:
            multiplayer_button_color = BUTTON_COLOUR

        pygame.draw.rect(screen, singleplayer_button_color, singleplayer_button_rect)
        pygame.draw.rect(screen, multiplayer_button_color, multiplayer_button_rect)
        screen.blit(singleplayer_text, singleplayer_text_rect)
        screen.blit(multiplayer_text, multiplayer_text_rect)

        pygame.display.update()
    
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    display_home_screen(screen)

if __name__ == "__main__":
    main()

