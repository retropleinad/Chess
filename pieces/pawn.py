from pieces.piece import Piece, Color


class Pawn(Piece):

    # Adds in an additional boolean to keep track of whether or not the
    # opponent's pawns may capture this one via en passant.
    # Additionally, set the piece value to 1
    def __init__(self, color, column, row, picture):
        super().__init__(color, column, row, picture)
        self.can_be_passant = False
        self.val = 1

    # Check to make sure we pass the board a valid square.
    # Can move two from starting line.
    # Can move diagonally to capture.
    # Else can move forwards by one.
    def can_move(self, board, column, row):
        if not 0 <= column < len(board) or not 0 <= row < len(board):
            return False
        elif self.color == Color.BLACK:
            return self.can_black_move(board, column, row)
        return self.can_white_move(board, column, row)

    # Can move two from starting line.
    # Can move forwards by one.
    # Can move left by one to capture.
    # Can move right by one to capture.
    def can_black_move(self, board, column, row):
        if self.column == 1 and column == 3 and self.row == row and \
                board[self.column + 1][self.row] is None and \
                board[self.column + 2][self.row] is None:
            return True
        elif self.column == column - 1 and self.row == row and \
                board[self.column + 1][self.row] is None:
            return True
        return self.can_black_capture(board, column, row)

    # Tests if black can move to another square to capture a piece
    # Acceptable squares are diagonally one square in front of the pawn
    def can_black_capture(self, board, column, row):
        if self.column == column - 1 and self.row == row + 1 and row >= 0 and \
                board[self.column + 1][self.row - 1] is not None and \
                board[self.column + 1][self.row - 1].color == Color.WHITE:
            return True
        elif self.column == column - 1 and self.row == row - 1 and row <= 7 and \
                board[self.column + 1][self.row + 1] is not None and \
                board[self.column + 1][self.row + 1].color == Color.WHITE:
            return True
        return self.can_en_passant(board, column, row)

    # Locally checks if the pawn can move forwards by two unobstructed pieces
    # from its starting line, as well as if it can move forwards by one
    # unobstructed piece.
    # Then it calls another method to check for captures.
    def can_white_move(self, board, column, row):
        if self.column == 6 and column == 4 and self.row == row and \
                board[self.column - 1][self.row] is None and \
                board[self.column - 2][self.row] is None:
            return True
        elif self.column == column + 1 and self.row == row and \
                board[self.column - 1][self.row] is None:
            return True
        return self.can_white_capture(board, column, row)

    # Locally checks if the pawn can capture by moving up one square diagonally.
    # Then calls to see if the pawn may perform an en passant.
    def can_white_capture(self, board, column, row):
        if self.column == column + 1 and self.row == row + 1 and row >= 0 and \
                board[self.column - 1][self.row - 1] is not None and \
                board[self.column - 1][self.row - 1].color == Color.BLACK:
            return True
        elif self.column == column + 1 and self.row == row - 1 and row <= 7 and \
                board[self.column - 1][self.row + 1] is not None and \
                board[self.column - 1][self.row + 1].color == Color.BLACK:
            return True
        return self.can_en_passant(board, column, row)

    # First, check if the board next to the pawn is out of range.
    # Then check if the board next to you is a pawn of a different color that you can passant.
    # Finally, check to see if the tile in front of you is empty.
    def can_en_passant(self, board, column, row):
        return True if self.left_en_passant(board, column, row) else self.right_en_passant(board, column, row)

    # First, check if the board next to the pawn is out of range.
    # Then check if the board next to you is a pawn of a different color that you can passant.
    # Finally, check to see if the tile in front of you is empty.
    # Checks specifically for a piece moving to the left of the board.
    def left_en_passant(self, board, column, row):
        if self.row != 0 and isinstance(board[self.column][self.row - 1], Pawn) and \
                board[self.column][self.row - 1].can_be_passant:
            if self.color == Color.BLACK:
                if self.row == row + 1 and self.column == column - 1:
                    return True
            elif self.row == row + 1 and self.column == column + 1:
                return True
        return False

    # First, check if the board next to the pawn is out of range.
    # Then check if the board next to you is a pawn of a different color that you can passant.
    # Finally, check to see if the tile in front of you is empty.
    # Checks specifically for a piece moving to the right of the board.
    def right_en_passant(self, board, column, row):
        if self.row != 7 and isinstance(board[self.column][self.row + 1], Pawn) and \
                board[self.column][self.row + 1].can_be_passant:
            if self.color == Color.BLACK:
                if self.row == row - 1 and self.column == column - 1:
                    return True
            elif self.row == row - 1 and self.column == column + 1:
                return True
        return False

    # Setter method for the boolean value that determines whether or not the opponent's
    # pawn may perform an en passant on this pawn.
    def receive_passant(self, var):
        self.can_be_passant = var

    # Returns a list of available moves that a piece may make, given a particular board
    # Check a 2 squares in front of the pawn and squares immediately diagonally to the
    # right and left.
    def available_moves(self, board):
        if self.color == Color.BLACK:
            return self.available_moves_helper(board, 1)
        return self.available_moves_helper(board, -1)

    # Pass -1 as direction for white pieces, 1 for black pieces
    def available_moves_helper(self, board, direction):
        moves = []
        column = self.column + direction
        if self.can_move(board, column, self.row):
            moves.append((column, self.row))
        if self.can_move(board, column + direction, self.row):
            moves.append((column + direction, self.row))
        if self.can_move(board, column, self.row + 1):
            moves.append((column, self.row + 1))
        if self.can_move(board, column, self.row - 1):
            moves.append((column, self.row - 1))
        return moves
