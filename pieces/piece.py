import enum
import pygame


# Each piece is assigned a color: white or black.
# This enum represents those color choices.
class Color(enum.Enum):
    BLACK = 1
    WHITE = 2


# Generic class to represent a piece
# Every piece class must inherit from this class
class Piece:

    # Column and row represent the piece's location in the 2D board array.
    # Picture is the piece's GUI icon
    def __init__(self, color, column, row, picture):
        self.picture = pygame.image.load(picture)
        self.color = color
        self.column = column
        self.row = row
        self.val = 0
        self.moved = False

    # Can the piece move to a particular square on the board?
    # Each child class has its own implementation of this method.
    def can_move(self, board, column, row):
        return True

    # Draws the piece on the GUI.
    # Square_size is the size of one square on the GUI board.
    def draw(self, screen, square_size):
        x_location = self.row + (self.row * (square_size - 1))
        y_location = self.column + (self.column * (square_size - 1))
        self.picture = pygame.transform.scale(self.picture, (square_size, square_size))
        screen.blit(self.picture, (x_location, y_location))
        pygame.display.flip()

    # Given a location on the GUI board, check if the piece is
    # at that location.
    def intersects_grid(self, grid_size, x, y):
        if x // grid_size == self.row and \
                y // grid_size == self.column:
            return True
        return False

    # Can the piece currently move to capture the enemy king?
    # If so, check.
    def place_check(self, board, king_column, king_row):
        if self.can_move(board, king_column, king_row):
            return True
        return False

    # Returns a list of available moves that a piece may make, given a particular board
    def available_moves(self, board):
        return []
