from pieces.queen import Queen


# Represent a rook piece
# Inherits from queen to reuse code for horizontal movement checking
class Rook(Queen):

    # Inherited constructor
    # Update the piece value
    def __init__(self, color, column, row, picture):
        super().__init__(color, column, row, picture)
        self.val = 5

    # The rook is allowed to move horizontally to any square that is
    # unobstructed and does not contain a friendly piece.
    def can_move(self, board, column, row):
        return super().check_horizontal(board, column, row)

    # Returns a list of available moves that a piece may make, given a particular board.
    # First, check every square to the right of the rook.
    # Then, check every square to the left of the rook.
    # Then, check every square above the rook.
    # Finally, check every square below the rook.
    # For each iteration, stop the iteration whenever you reach an inaccessible square.
    def available_moves(self, board):
        return super().horizontal_moves(board)