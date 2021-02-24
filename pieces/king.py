from pieces.piece import Piece


# Represents a king piece.
class King(Piece):

    # Inherited constructor
    # Update the piece value
    def __init__(self, color, column, row, picture):
        super().__init__(color, column, row, picture)
        self.val = 10

    # Checks if the king can move to a square.
    # Allows movement to any square that is next to the king's current square,
    # as long as the new square does not hold a friendly piece.
    # Check is handled in chess.Chess
    def can_move(self, board, column, row):
        if self.column - 1 <= column <= self.column + 1 and 0 <= column < len(board) and \
                self.row - 1 <= row <= self.row + 1 and 0 <= row < len(board):
            if board[column][row] is not None and board[column][row].color == self.color:
                return False
            return True
        return False

    # Returns a list of available moves that a piece may make, given a particular board.
    # Cycle through the 3x3 square around the king.
    def available_moves(self, board):
        moves = []
        for i in range(self.column - 1, self.column + 2):
            for j in range(self.row - 1, self.row + 2):
                if self.can_move(board, i, j):
                    moves.append((i, j))
        return moves