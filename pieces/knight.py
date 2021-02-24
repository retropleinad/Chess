from pieces.piece import Piece


class Knight(Piece):

    # Inherited constructor
    # Update the piece value
    def __init__(self, color, column, row, picture):
        super().__init__(color, column, row, picture)
        self.val = 3

    # Is the square in a 2 by 3 or a 3 by 2?
    # Is there a friendly piece in that square?
    # Otherwise, it can move.
    def can_move(self, board, column, row):
        if column >= len(board) or row >= len(board) or column < 0 or row < 0 or \
                (board[column][row] is not None and board[column][row].color == self.color):
            return False
        elif (self.column + 2 == column and self.row + 1 == row) or \
                (self.column + 2 == column and self.row - 1 == row) or \
                (self.column - 2 == column and self.row + 1 == row) or \
                (self.column - 2 == column and self.row - 1 == row) or \
                (self.column + 1 == column and self.row + 2 == row) or \
                (self.column + 1 == column and self.row - 2 == row) or \
                (self.column - 1 == column and self.row + 2 == row) or \
                (self.column - 1 == column and self.row - 2 == row):
            return True
        return False

    # Returns a list of available moves that a piece may make, given a particular board
    def available_moves(self, board):
        moves = []
        i = 2
        while i > -3:
            j = 2
            while j > -3:
                if self.can_move(board, self.column + i, self.row + j):
                    moves.append((self.column + i, self.row + j))
                j -= 1
            i -= 1
        return moves