from pieces.piece import Piece


# Represents a queen piece
# Rook and Bishop both extend Queen to reuse code for diagonal and horizontal can_move methods
class Queen(Piece):

    # Inherited constructor
    # Update the piece value
    def __init__(self, color, column, row, picture):
        super().__init__(color, column, row, picture)
        self.val = 9

    # The queen is allowed horizontally or diagonally to any unobstructed square
    # that does not currently hold a friendly piece.
    def can_move(self, board, column, row):
        if self.column == column or self.row == row:
            return self.check_horizontal(board, column, row)
        return self.check_diagonal(board, column, row)

    # Is the square diagonal from the queen?
    # Is there a friendly piece in that square?
    # Is there a piece in the way of the queen?
    def check_diagonal(self, board, column, row):
        distance = abs(self.column - column)
        if distance != abs(self.row - row) or \
                (board[column][row] is not None and board[column][row].color == self.color):
            return False
        i = self.column
        j = self.row
        while i != column and j != row:
            if board[i][j] is not None and i != self.column:
                return False
            i = i + 1 if i < column else i - 1
            j = j + 1 if j < row else j - 1
        return True

    # Is the desired square in the same column or row?
    # Is there a friendly piece on that square?
    # Are there any pieces between this square and that square?
    def check_horizontal(self, board, column, row):
        if (self.column != column and self.row != row) or \
                (board[column][row] is not None and board[column][row].color == self.color):
            return False
        elif column == self.column:
            return self.check_rows(board, column, row)
        return self.check_columns(board, column, row)

    # Checks if the queen can move horizontally to a square in another column.
    def check_columns(self, board, column, row):
        if column < self.column:
            for i in range(column + 1, self.column):
                if board[i][row] is not None:
                    return False
        else:
            for i in range(self.column + 1, column):
                if board[i][row] is not None:
                    return False
        return True

    # Checks if the queen can move horizontally to a square in another row.
    def check_rows(self, board, column, row):
        if row < self.row:
            for i in range(row + 1, self.row):
                if board[column][i] is not None:
                    return False
        else:
            for i in range(self.row + 1, row):
                if board[column][i] is not None:
                    return False
        return True

    # Returns a list of available moves that a piece may make, given a particular board
    def available_moves(self, board):
        return self.diagonal_moves(board) + self.horizontal_moves(board)

    # Returns a list of available diagonal moves that a piece may make, given a particular board
    def diagonal_moves(self, board):
        return self.diagonal_helper(board, 1, 1) + self.diagonal_helper(board, -1, 1) + \
               self.diagonal_helper(board, 1, -1) + self.diagonal_helper(board, -1, -1)

    # Helper method to determine available diagonal moves.
    # Checks each square between the bishop and the end of the board.
    # Pass column_direction as 1 to move down the board, -1 to move up.
    # Pass row_direction as 1 to move right, -1 to move left
    # Stop the iteration when you reach an inaccessible square.
    # Keep track of hitting enemies to prevent moving past enemy pieces.
    def diagonal_helper(self, board, column_direction, row_direction):
        moves = []
        column = self.column + column_direction
        row = self.row + row_direction
        access = True
        hit_enemy = False
        while 0 <= column < len(board) and 0 <= row < len(board) and access:
            if board[column][row] is None:
                moves.append((column, row))
            elif board[column][row].color != self.color and not hit_enemy:
                moves.append((column, row))
                hit_enemy = True
            else:
                access = False
            column += column_direction
            row += row_direction
        return moves

    # Returns the available horizontal moves that the queen may make.
    def horizontal_moves(self, board):
        return self.horizontal_right(board) + self.horizontal_left(board) + \
               self.horizontal_above(board) + self.horizontal_below(board)

    # Helper method to determine available horizontal moves to the right.
    # Returns a list of squares to the right of the rook that it may move to.
    # Stop the iteration when you reach an inaccessible square.
    # Keep track of hitting enemies to prevent moving past enemy pieces.
    def horizontal_right(self, board):
        moves = []
        access = True
        row = self.row + 1
        hit_enemy = False
        while access and row < len(board):
            if board[self.column][row] is None:
                moves.append((self.column, row))
            elif board[self.column][row].color != self.color and not hit_enemy:
                moves.append((self.column, row))
                hit_enemy = True
            else:
                access = False
            row += 1
        return moves

    # Helper method to determine available horizontal moves to the left.
    # Returns a list of squares to the left of the rook that it may move to.
    # Stop the iteration when you reach an inaccessible square.
    # Keep track of hitting enemies to prevent moving past enemy pieces.
    def horizontal_left(self, board):
        moves = []
        access = True
        row = self.row - 1
        hit_enemy = False
        while access and row >= 0:
            if board[self.column][row] is None:
                moves.append((self.column, row))
            elif board[self.column][row].color != self.color and not hit_enemy:
                moves.append((self.column, row))
                hit_enemy = True
            else:
                access = False
            row -= 1
        return moves

    # Helper method to determine available horizontal moves above.
    # Returns a list of squares above the rook that it may move to.
    # Stop the iteration when you reach an inaccessible square.
    # Keep track of hitting enemies to prevent moving past enemy pieces.
    def horizontal_above(self, board):
        moves = []
        access = True
        column = self.column + 1
        hit_enemy = False
        while access and column < len(board):
            if board[column][self.row] is None:
                moves.append((column, self.row))
            elif board[column][self.row].color != self.color and not hit_enemy:
                moves.append((column, self.row))
                hit_enemy = True
            else:
                access = False
            column += 1
        return moves

    # Helper method to determine available horizontal moves below.
    # Returns a list of squares below the rook that it may move to.
    # Stop the iteration when you reach an inaccessible square.
    # Keep track of hitting enemies to prevent moving past enemy pieces.
    def horizontal_below(self, board):
        moves = []
        access = True
        column = self.column - 1
        hit_enemy = False
        while access and column >= 0:
            if board[column][self.row] is None:
                moves.append((column, self.row))
            elif board[column][self.row].color != self.color and not hit_enemy:
                moves.append((column, self.row))
                hit_enemy = True
            else:
                access = False
            column -= 1
        return moves
