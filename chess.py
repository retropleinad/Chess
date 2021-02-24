import time

import pygame

from queue import Queue

import ai
from pieces.rook import Rook
from pieces.knight import Knight
from pieces.bishop import Bishop
from pieces.queen import Queen
from pieces.king import King
from pieces.pawn import Pawn
from pieces.piece import Color

length = 64
NUM_SQUARES = 8

# X, Y
screen_size = (length * NUM_SQUARES, length * NUM_SQUARES)

BLACK = (80, 38, 0)
WHITE = (191, 126, 74)
HIGHLIGHT = (150, 150, 25)

last_screen = None

num_players = 1

images = {
    "black_pawn": "sprites/black_pawn.png",
    "black_rook": "sprites/black_rook.png",
    "black_knight": "sprites/black_knight.png",
    "black_bishop": "sprites/black_bishop.png",
    "black_queen": "sprites/black_queen.png",
    "black_king": "sprites/black_king.png",
    "white_pawn": "sprites/white_pawn.png",
    "white_rook": "sprites/white_rook.png",
    "white_knight": "sprites/white_knight.png",
    "white_bishop": "sprites/white_bishop.png",
    "white_queen": "sprites/white_queen.png",
    "white_king": "sprites/white_king.png"
}


# The chess class contains groupings of functions and objects pertaining to the inner workings of the
# chess game, primarily in regards to moving pieces around the game board.
class Chess:

    # Pieces are stored in lists to more quickly access them.
    # Pieces are stored in a 2D array to more quickly work with piece location.
    # Pointers to kings are saved in order to improve the efficiency of castling and check.
    def __init__(self):
        self.board = [[None for i in range(NUM_SQUARES)] for j in range(NUM_SQUARES)]
        self.place_pieces(Color.BLACK)
        self.place_pieces(Color.WHITE)
        self.white_pieces = []
        self.black_pieces = []
        self.pieces_to_list(Color.BLACK)
        self.pieces_to_list(Color.WHITE)
        self.white_king = self.board[7][4]
        self.black_king = self.board[0][4]
        self.passant_q = Queue()
        self.turn = Color.WHITE
        self.in_checkmate = False
        self.player_move = True
        self.turns_passed = 0

    # Places the pieces in the 2D array.
    # NOT on the board GUI.
    def place_pieces(self, color):
        column = 0
        color_string = "black"
        if color == Color.WHITE:
            column = 7
            color_string = "white"
        self.board[column][0] = Rook(color, column, 0, images[color_string + "_rook"])
        self.board[column][1] = Knight(color, column, 1, images[color_string + "_knight"])
        self.board[column][2] = Bishop(color, column, 2, images[color_string + "_bishop"])
        self.board[column][3] = Queen(color, column, 3, images[color_string + "_queen"])
        self.board[column][4] = King(color, column, 4, images[color_string + "_king"])
        self.board[column][5] = Bishop(color, column, 5, images[color_string + "_bishop"])
        self.board[column][6] = Knight(color, column, 6, images[color_string + "_knight"])
        self.board[column][7] = Rook(color, column, 7, images[color_string + "_rook"])
        if color == Color.BLACK:
            column = 1
        else:
            column = 6
        for i in range(0, NUM_SQUARES):
            self.board[column][i] = Pawn(color, column, i, images[color_string + "_pawn"])

    # Adds white pieces to the white list, and black pieces to the black list.
    def pieces_to_list(self, color):
        if color == Color.BLACK:
            for i in range(0, 2):
                for j in range(0, NUM_SQUARES):
                    self.black_pieces.append(self.board[i][j])
        else:
            for i in range(6, NUM_SQUARES):
                for j in range(0, NUM_SQUARES):
                    self.white_pieces.append(self.board[i][j])

    # Draws pieces in their starting position on the GUI.
    def draw_pieces(self, screen):
        for i in range(0, 2):
            for j in range(0, NUM_SQUARES):
                self.board[i][j].draw(screen, length)
        for i in range(6, 8):
            for j in range(0, NUM_SQUARES):
                self.board[i][j].draw(screen, length)

    # Takes a position and returns any piece that may be at that location.
    def select_piece(self, position):
        if self.turn == Color.WHITE:
            for white in self.white_pieces:
                if white.intersects_grid(length, position[0], position[1]):
                    return white
        else:
            for black in self.black_pieces:
                if black.intersects_grid(length, position[0], position[1]):
                    return black
        return None

    # In order to move:
    # 1.) Check if you are in check
    # 2.) Check if the desired move is a castle
    # 3.) Check if the piece can move (check)
    # 4.) Set the old coordinates to None
    # 5.) Change the piece's internal coordinates (check)
    # 6.) Change the piece's position in the 2D array
    # 7.) Clear the square
    # 8.) Draw the piece on a new square
    # 9.) Remove any captured piece from its list
    # 10.) See if the move placed your opponent in check/mate
    def move_piece(self, screen, piece, position):
        if isinstance(piece, Pawn):
            print(piece.available_moves(self.board))
        if not self.player_move:
            new_x = position[1]
            new_y = position[0]
        else:
            new_x = position[0] // length
            new_y = position[1] // length
        screen.blit(last_screen, (0, 0))
        if self.self_in_check(piece, new_y, new_x):
            return False
        elif isinstance(piece, King) and new_x == 6 and self.castle(screen, new_y):
            pass
        elif not piece.can_move(self.board, new_y, new_x):
            return False
        self.make_passant(screen, piece)
        self.empty_passants()
        self.set_en_passant(piece, new_y)
        self.board[piece.column][piece.row] = None
        erase_square(screen, piece)
        piece.column = new_y
        piece.row = new_x
        self.board[new_y][new_x] = piece
        erase_square(screen, piece)
        piece.draw(screen, length)
        self.remove_from_list(piece.color, new_y, new_x)
        piece.moved = True
        self.turns_passed += 1
        if isinstance(piece, Pawn):
            piece = self.pawn_to_queen(screen, piece)
        if self.opponent_in_check(piece, self.board):
            if self.checkmate(piece):
                draw_checkmate(screen)
            else:
                draw_check(screen)  # change this around
        return True

    # Removes a piece from its list if it is captured.
    def remove_from_list(self, capturing_color, column, row):
        if capturing_color == Color.BLACK:
            for piece in self.white_pieces:
                if piece.column == column and piece.row == row:
                    self.white_pieces.remove(piece)
        else:
            for piece in self.black_pieces:
                if piece.column == column and piece.row == row:
                    self.black_pieces.remove(piece)

    # Check if the move will place yourself in check...
    # If true, do not allow for the move....
    # First, move the piece to the desired location.
    # Then, cycle through enemy pieces and see if they can attack the king.
    # Then move the piece back, as well as any piece that was at that location.
    # If the offending piece would be captured, don't check for it.
    # This is called before we check can_move.
    # Also factor in special moves.
    def self_in_check(self, piece, new_y, new_x):
        current_y = piece.column
        current_x = piece.row
        temp = self.board[new_y][new_x]
        self.board[current_y][current_x] = None
        self.board[new_y][new_x] = piece
        check = False
        if piece.color == Color.BLACK:
            pieces = self.white_pieces
            king = self.black_king
        else:
            pieces = self.black_pieces
            king = self.white_king
        if piece is king:
            king.column = new_y
            king.row = new_x
        for p in pieces:
            if p.column != new_y or p.row != new_x:
                if p.place_check(self.board, king.column, king.row):
                    check = True
                    break
        if piece is king:
            king.column = current_y
            king.row = current_x
        self.board[current_y][current_x] = piece
        self.board[new_y][new_x] = temp
        return check

    # Check if moving this piece will place your opponent in check...
    # Call AFTER moving your piece.
    # Cycle to see if any of your pieces will place the opponent in check.
    # Also factor in special moves.
    def opponent_in_check(self, piece, board):
        if piece.color == Color.BLACK:
            pieces = self.black_pieces
            king = self.white_king
        else:
            pieces = self.white_pieces
            king = self.black_king
        for p in pieces:
            if p.place_check(board, king.column, king.row):
                return True
        return False

    # Check ONLY after check: Pass in the piece placing the king in check.
    # First, check to see if the king can move to any surrounding squares and not be in check.
    # If not, get the offending piece's type and coords from the list.
    # See if any piece can move to block (or capture) it.
    def checkmate(self, piece):
        if piece.color == Color.BLACK:
            pieces = self.white_pieces
            king = self.white_king
        else:
            pieces = self.black_pieces
            king = self.black_king
        if self.can_king_move(king):
            return False
        elif isinstance(piece, Rook):
            return not self.can_block_rook(piece, king, pieces)
        elif isinstance(piece, Bishop):
            return not self.can_block_bishop(piece, king, pieces)
        elif isinstance(piece, Queen):
            return not self.can_block_queen(piece, king, pieces)
        elif isinstance(piece, Knight):
            return not self.can_capture_knight(piece, pieces)
        return True

    # Method to check if the king can move out of the way of check.
    # Cycle through the 3x3 square around the king and see if he can move:
    # 1.) Check to make sure the king is not on the edge of the map
    # 2.) Check to see if the king can normally move there
    # 3.) See if the king can move there and not be in check
    def can_king_move(self, king):
        king_y = king.column
        king_x = king.row
        for i in range(king_y - 1, king_y + 2):
            for j in range(king_x - 1, king_x + 2):
                if 0 <= i < NUM_SQUARES and 0 <= j < NUM_SQUARES and \
                        king.can_move(self.board, i, j):
                    print(str(i) + "," + str(j))
                    if not self.self_in_check(king, i, j):
                        return True
        return False

    # 1.) Check which direction the rook is placing the king in check from
    # 2.) Check for each space between the king (exclusive) and rook (inclusive)
    # if any piece can move there and if that move won't be check.
    def can_block_rook(self, rook, king, pieces):
        king_y = king.column
        king_x = king.row
        rook_y = rook.column
        rook_x = rook.row
        if rook_y == king_y:
            if rook_x > king_x:
                roof = rook_x + 1
                floor = king_x
            else:
                roof = king_x + 1
                floor = rook_x
            for x in range(floor, roof):
                for piece in pieces:
                    if piece.can_move(self.board, rook_y, x) and \
                            not self.self_in_check(piece, rook_y, x):
                        return True
        else:
            if rook_y > king_y:
                roof = rook_y + 1
                floor = king_y
            else:
                roof = king_y + 1
                floor = rook_y
            for y in range(floor, roof):
                for piece in pieces:
                    if piece.can_move(self.board, y, rook_x) and \
                            not self.self_in_check(piece, y, rook_x):
                        return True
        self.in_checkmate = True
        return False

    # Compare the bishop's location to the king's and see if a piece can either
    # capture the bishop or move between the king and bishop.
    def can_block_bishop(self, bishop, king, pieces):
        king_y = king.column
        king_x = king.row
        bishop_y = bishop.column
        bishop_x = bishop.row
        if bishop_y > king_y:
            if bishop_x > king_x:
                floor_col = king_y
                floor_row = king_x
                roof_col = bishop_y
                roof_row = bishop_x
            else:
                floor_col = king_y
                floor_row = bishop_x
                roof_col = bishop_y
                roof_row = king_x
        else:
            if bishop_x > king_x:
                floor_col = bishop_y
                floor_row = king_x
                roof_col = king_y
                roof_row = bishop_x
            else:
                floor_col = bishop_y
                floor_row = bishop_x
                roof_col = king_y
                roof_row = king_x
        return self.bishop_block_helper(floor_col, floor_row, roof_col, roof_row, pieces)

    # Deduces which direction the king is from the bishop and produces iterators
    # then checks each square between the bishop (inclusive) and the king (exclusive)
    # to see if a piece can capture the bishop or block it from taking the king.
    def bishop_block_helper(self, floor_col, floor_row, roof_col, roof_row, pieces):
        column_iterator = int((roof_col - floor_col) / abs(roof_col - floor_col))
        row_iterator = int((roof_row - floor_row) / abs(roof_row - floor_row))
        i = int(floor_col)
        j = int(floor_row)
        while i != roof_col + column_iterator and j != roof_row + row_iterator:
            for piece in pieces:
                if piece.can_move(self.board, i, j) and \
                        not self.self_in_check(piece, i, j):
                    return True
            i += column_iterator
            j += row_iterator
        self.in_checkmate = True
        return False

    # Tests to see if a piece can block or capture the queen to prevent checkmate.
    # Because the queen moves like a rook or bishop, we treat her as one, depending
    # on the direction she is attacking the king from.
    def can_block_queen(self, queen, king, pieces):
        if queen.column == king.column or \
                queen.row == king.row:
            return self.can_block_rook(queen, king, pieces)
        return self.can_block_bishop(queen, king, pieces)

    # See if anyone can capture the knight, and the piece moving to capture the knight
    # will not leave the king in check.
    def can_capture_knight(self, knight, pieces):
        knight_y = knight.column
        knight_x = knight.row
        for piece in pieces:
            if piece.can_move(self.board, knight_y, knight_x) and \
                    not self.self_in_check(piece, knight_y, knight_x):
                return True
        self.in_checkmate = True
        return False

    # Is the king in his starting spot?
    # Is the rook in his starting spot?
    # Are the column and row suitable for castling?
    def castle(self, screen, new_y):
        if self.turn == Color.WHITE:
            return self.white_castle(screen, new_y)
        return self.black_castle(screen, new_y)

    # Specifically to test if the white king can castle:
    # Is the king in his starting spot?
    # Is the rook in his starting spot?
    # Are the column and row suitable for castling
    def white_castle(self, screen, new_y):
        last_index = NUM_SQUARES - 1
        if self.board[7][4] is self.white_king and new_y == last_index and \
                isinstance(self.board[last_index][last_index], Rook) and \
                self.board[7][7].color == Color.WHITE and \
                self.move_piece(screen, self.board[last_index][last_index], (5 * length, last_index * length)):
            self.turn = Color.WHITE
            return True
        return False

    # Specifically to test if the black king can castle:
    # Is the king in his starting spot?
    # Is the rook in his starting spot?
    # Are the column and row suitable for castling
    def black_castle(self, screen, new_y):
        last_index = NUM_SQUARES - 1
        if self.board[0][4] is self.black_king and new_y == 0 and \
                isinstance(self.board[0][last_index], Rook) and \
                self.board[0][last_index].color == Color.BLACK and \
                self.move_piece(screen, self.board[0][last_index], (5 * length, 0)):
            self.turn = Color.BLACK
            return True
        return False

    # Check to see if the piece is a pawn moving up 2 spaces from the front line.
    # Check to see if neighbors exist and if they're pawns of a different color.
    # If so, set their can_en_passant to true.
    def set_en_passant(self, piece, column):
        if isinstance(piece, Pawn) and \
                (piece.column + 2 or piece.column - 2 == column):
            if piece.row - 1 >= 0 and \
                    isinstance(self.board[column][piece.row - 1], Pawn) and \
                    self.board[column][piece.row - 1].color != piece.color:
                piece.receive_passant(True)
                self.passant_q.put(piece)
            elif piece.row + 1 < NUM_SQUARES and \
                    isinstance(self.board[column][piece.row + 1], Pawn) and \
                    self.board[column][piece.row + 1].color != piece.color:
                piece.receive_passant(True)
                self.passant_q.put(piece)

    # Because chess rules allow a pawn to en passant only during the turn after the
    # opponent's pawn moves, the queue of pawns that may en passant is emptied afterwards.
    def empty_passants(self):
        while not self.passant_q.empty():
            self.passant_q.get().receive_passant(False)

    # Check to see if the piece's neighbors exist,
    # if the neighbors are pawns,
    # and if they may be captured via en passant.
    def make_passant(self, screen, piece):
        if isinstance(piece, Pawn):
            if piece.row != 0 and \
                    isinstance(self.board[piece.column][piece.row - 1], Pawn) and \
                    self.board[piece.column][piece.row - 1].can_be_passant:
                erase_square(screen, self.board[piece.column][piece.row - 1])
                self.board[piece.column][piece.row - 1] = None
                return True
            elif piece.row != NUM_SQUARES - 1 and \
                    isinstance(self.board[piece.column][piece.row + 1], Pawn) and \
                    self.board[piece.column][piece.row + 1].can_be_passant:
                erase_square(screen, self.board[piece.column][piece.row + 1])
                self.board[piece.column][piece.row + 1] = None
                return True
        return False

    # Be sure to run check over the new queen.
    # Call after the pawn has moved.
    # Remove the pawn from the list and the gui.
    # Then give a queen the pawn's coords, add her to the list and gui.
    def pawn_to_queen(self, screen, pawn):
        pawn_y = pawn.column
        pawn_x = pawn.row
        if pawn.color == Color.BLACK and pawn_y == NUM_SQUARES - 1:
            self.black_pieces.remove(pawn)
            erase_square(screen, pawn)
            self.board[pawn_y][pawn_x] = Queen(Color.BLACK, pawn_y, pawn_x, images["black_queen"])
            self.black_pieces.append(self.board[pawn_y][pawn_x])
            self.board[pawn_y][pawn_x].draw(screen, length)
        elif pawn.color == Color.WHITE and pawn_y == 0:
            self.white_pieces.remove(pawn)
            erase_square(screen, pawn)
            self.board[pawn_y][pawn_x] = Queen(Color.WHITE, pawn_y, pawn_x, images["white_queen"])
            self.white_pieces.append(self.board[pawn_y][pawn_x])
            self.board[pawn_y][pawn_x].draw(screen, length)
        pawn = self.board[pawn_y][pawn_x]
        return pawn

    # Returns a list of pieces that the AI is allowed to move.
    def get_ai_pieces(self):
        return self.black_pieces


# Paints over any graphic that currently covers a square.
# Primarily used to remove piece graphics when they move or are captured.
def erase_square(screen, piece):
    square = pygame.Surface((length, length))
    if piece.column % 2 == 0:
        if piece.row % 2 == 0:
            square.fill(WHITE)
        else:
            square.fill(BLACK)
    else:
        if piece.row % 2 == 0:
            square.fill(BLACK)
        else:
            square.fill(WHITE)
    screen.blit(square, (piece.row * length, piece.column * length))
    pygame.display.flip()


# Outputs "Check!" on the screen when a king is placed in check.
# Centering the message:
# Take the screen width / 2 and subtract message length / 2
def draw_check(screen):
    copy = screen.copy()
    font = pygame.font.SysFont("Arial Black", 50)
    text_color = (150, 150, 0)
    check = font.render("Check!", False, text_color)
    message_x = screen_size[0] / 2 - check.get_width() / 2
    screen.blit(check, (message_x, 200))
    pygame.display.flip()
    time.sleep(1)
    screen.blit(copy, (0, 0))


# Outputs "Checkmate!" on the screen when a king is placed in checkmate.
def draw_checkmate(screen):
    font = pygame.font.SysFont("Arial Black", 50)
    text_color = (150, 150, 0)
    checkmate = font.render("Checkmate!", False, text_color)
    checkmate_x = screen_size[0] / 2 - checkmate.get_width() / 2
    play_again = font.render("Play Again? <Y/N>", False, text_color)
    play_again_x = screen_size[0] / 2 - play_again.get_width() / 2
    screen.blit(checkmate, (checkmate_x, 125))
    screen.blit(play_again, (play_again_x, 200))
    pygame.display.flip()


# Draws an empty checkerboard.
# Alternates between drawing white and black squares.
def draw_squares(screen, size):
    i = 0
    color = True
    while i < screen_size[0]:
        j = 0
        while j < screen_size[1]:
            if color:
                square = pygame.Surface((size, size))
                square.fill(WHITE)
                screen.blit(square, (i, j))
                color = False
            else:
                square = pygame.Surface((size, size))
                square.fill(BLACK)
                screen.blit(square, (i, j))
                color = True
            j += size
        color = not color
        i += size


# When the program opens, draw a screen asking if there are one or two players
# This method draws the screen, while the helper method checks for input
def select_players(screen):
    font_color = (0, 0, 150)
    draw_squares(screen, length)
    button_color = (150, 150, 150, 200)
    font = pygame.font.SysFont("Arial Black", 35)
    welcome = font.render("Welcome to Chess!", False, font_color)
    one_player_text = font.render("One Player", False, font_color)
    two_player_text = font.render("Two Players", False, font_color)
    welcome_x = screen_size[0] / 2 - welcome.get_width() / 2
    one_player_x = screen_size[0] / 2 - one_player_text.get_width() / 2
    two_player_x = screen_size[0] / 2 - two_player_text.get_width() / 2
    one_button_rect = (one_player_x - 10, 250, one_player_text.get_width() + 20, one_player_text.get_height())
    two_button_rect = (two_player_x - 10, 350, two_player_text.get_width() + 20, two_player_text.get_height())
    screen.blit(welcome, (welcome_x, 66))
    pygame.draw.rect(screen, button_color, one_button_rect)
    pygame.draw.rect(screen, button_color, two_button_rect)
    screen.blit(one_player_text, (one_player_x, 250))
    screen.blit(two_player_text, (two_player_x, 350))
    pygame.display.flip()
    select_players_helper(one_button_rect, two_button_rect)


# Helper method for select_players to check if the player selected the button's
# location on the board then set numbers of players accordingly.
def select_players_helper(one_button_rect, two_button_rect):
    run = True
    global num_players
    while run:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONUP:
                position = pygame.mouse.get_pos()
                if one_button_rect[0] < position[0] < one_button_rect[0] + one_button_rect[2] and \
                        one_button_rect[1] < position[1] < one_button_rect[1] + one_button_rect[3]:
                    num_players = 1
                    run = False
                elif two_button_rect[0] < position[0] < two_button_rect[0] + two_button_rect[2] and \
                        two_button_rect[1] < position[1] < two_button_rect[1] + two_button_rect[3]:
                    num_players = 2
                    run = False


# If the player successfully moves their piece, then take an AI turn
# Return the selected piece or None if there isn't one
def take_turn(screen, game, selected_piece):
    piece = None
    if game.player_move:
        piece = player_turn(screen, game, selected_piece)
    if not game.player_move and not game.in_checkmate:
        global last_screen
        last_screen = screen.copy()
        ai.mini_max(game, 3, screen)
    else:
        return piece


# If a piece is selected, then move it.
# Otherwise, continue to try and select a piece.
# This method exists specifically for a player to select a piece from the GUI
def player_turn(screen, game, selected_piece):
    position = pygame.mouse.get_pos()
    if selected_piece is not None and ((num_players == 2 and game.turn == selected_piece.color)
                                       or (num_players == 1 and game.turn == Color.WHITE)):
        if game.move_piece(screen, selected_piece, position):
            game.turn = Color.BLACK if game.turn == Color.WHITE else Color.WHITE
            if num_players == 1:
                game.player_move = False
            return None
    selected_piece = game.select_piece(position)
    if selected_piece is not None:
        global last_screen
        last_screen = screen.copy()
        top_left_x = selected_piece.row * length
        top_left_y = selected_piece.column * length
        pygame.draw.rect(screen, HIGHLIGHT, (top_left_x, top_left_y, length, length), 5)
    return selected_piece


# Initiates the game, runs the main loop.
# Checks to see if the window should be closed, if a player can move a piece,
# or if players would like to play another round.
def main():
    pygame.init()
    clock = pygame.time.Clock()
    fps = 60
    screen = pygame.display.set_mode(screen_size)
    pygame.display.set_caption("Chess")
    select_players(screen)
    draw_squares(screen, length)
    game = Chess()
    game.draw_pieces(screen)
    run = True
    selected_piece = None
    while run:
        pygame.display.flip()
        clock.tick(fps)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.MOUSEBUTTONUP and not game.in_checkmate:
                selected_piece = take_turn(screen, game, selected_piece)
            elif event.type == pygame.KEYDOWN and game.in_checkmate:
                if event.key == pygame.K_n:
                    run = False
                if event.key == pygame.K_y:
                    draw_squares(screen, length)
                    game = Chess()
                    game.draw_pieces(screen)
                    selected_piece = None
    pygame.quit()


if __name__ == '__main__':
    main()
