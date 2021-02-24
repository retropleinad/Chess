from pieces.queen import Queen


# Represents a bishop piece.
# Inherits from Queen to reuse the diagonal movement method.
class Bishop(Queen):

    # Inherited constructor
    # Update the piece value
    def __init__(self, color, column, row, picture):
        super().__init__(color, column, row, picture)
        self.val = 3

    # Can the piece move to a particular square?
    # The piece may only move to a square that is diagonal from it,
    # that is not currently occupied by a friendly piece,
    # and every square on the way to that square must be empty.
    def can_move(self, board, column, row):
        return super().check_diagonal(board, column, row)

    # Returns a list of available moves that a piece may make, given a particular board
    def available_moves(self, board):
        return super().diagonal_moves(board)
