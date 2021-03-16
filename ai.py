import sys
from random import randrange

from pieces.bishop import Bishop
from pieces.knight import Knight
from pieces.pawn import Pawn
from pieces.piece import Color


# Takes each move for each piece and puts it in a format that is easier to work with.
# Returns a list of tuples where the tuple's first index is a reference to the piece,
# and the second index is the move.
def move_list(game, color):
    if color == Color.WHITE:
        pieces = game.white_pieces
    else:
        pieces = game.black_pieces
    moves = []
    for piece in pieces:
        piece_moves = piece.available_moves(game.board)
        for move in piece_moves:
            moves.append((piece, move))
    return moves


# Randomly moves a piece on the board
def rand_turn(game, screen):
    moves = move_list(game, Color.BLACK)
    index = randrange(len(moves))
    try_move = True
    while try_move:
        if game.move_piece(screen, moves[index][0], moves[index][1]):
            try_move = False
        else:
            moves.remove(moves[index])
            index = randrange(len(moves))
    game.player_move = True
    game.turn = Color.WHITE


# Minimax decision tree algorithm for determining which move the computer should make.
# White tries to maximize the advantage, while black tries to minimize it
# Double check colors are right
# First index returns the value, second index returns the piece, third index returns the move
def mini_max(game, turns, screen):
    move = minimax_helper(game, turns, True)
    game.move_piece(screen, piece=move[1], position=move[2][1])
    game.turn = Color.WHITE
    game.player_move = True


"""    if game.turns_passed < 20:
        current_score = early_eval(game.white_pieces, game.black_pieces)
    elif len(game.black_pieces) > 8 and len(game.white_pieces) > 8:
        current_score = middle_eval(game, game.white_pieces, game.black_pieces)
    else:
        current_score = endgame_eval(game.white_pieces, game.black_pieces)"""


# We fundamentally want to maximize our score, while white wants to minimize it.
# First: Update the move_list method
# Get a list of each possible move, and edit the board to simulate that move happening.
#       a.) Change the piece's internal coords
#       b.) Save any piece that may be at the desired coords
#       c.) Remove the old piece from its list
#       c.) Change the piece's location on the board
#       d.) Call the recursive function
#       e.) Change the piece's internal coords
#       f.) Change the piece's board location to its old location
#       f.) Add the old piece back to its list
#       g.) Place the old piece back on the board
# Also change pieces' internal coords before and after the recursive call
# Base case: return the score and the piece/move combo
def minimax_helper(game, turns, maximize):
    if turns == 0 or game.in_checkmate:
        current_score = basic_eval(game.white_pieces, game.black_pieces)
        return [current_score]
    if maximize:
        return black_minimax(game, turns)
    else:
        return white_minimax(game, turns)


iterator = 0


# Potential problem: evaluating score before base case but probably not
# Black tries to maximize
def black_minimax(game, turns):
    moves = move_list(game, Color.BLACK)
    max_score = -sys.maxsize - 1
    best_moves = []

    for i in range(0, len(moves)):
        # Create coordinates for the piece's potential new location
        new_y = moves[i][1][0]
        new_x = moves[i][1][1]

        # Store the piece's current location (before the move)
        current_piece = moves[i][0]
        old_y = current_piece.column
        old_x = current_piece.row

        # Temporarily change the piece's location
        current_piece.column = new_y
        current_piece.row = new_x

        # Check if an enemy piece is currently in the square you would like to move to
        old_piece = game.board[new_y][new_x]
        removed = False
        if old_piece is not None and old_piece in game.white_pieces:
            game.white_pieces.remove(old_piece)
            removed = True

        # Move the piece on the board
        game.board[new_y][new_x] = current_piece

        # Find the best next move AFTER this move
        next_move = minimax_helper(game, turns - 1, False)

        # If the board state is better than our current board state, make it our new best move
        if next_move[0] == max_score:
            best_moves.append([next_move[0], current_piece, moves[i]])
        if next_move[0] > max_score:
            max_score = next_move[0]
            best_moves = [[next_move[0], current_piece, moves[i]]]

        # Move the piece back to where it belongs
        current_piece.column = old_y
        current_piece.row = old_x

        # If we removed a piece, add it back
        if old_piece is not None and removed:
            game.white_pieces.append(old_piece)
        game.board[old_y][old_x] = current_piece
        if removed or old_piece is None:
            game.board[new_y][new_x] = old_piece

    # If there are multiple best removes, randomly select one
    if len(best_moves) > 1:
        return best_moves[randrange(len(best_moves))]
    return best_moves[0]


# White tries to minimize
def white_minimax(game, turns):
    moves = move_list(game, Color.WHITE)
    min_score = sys.maxsize
    best_moves = []

    for i in range(0, len(moves)):
        # Create coordinates for the piece's potential new location
        new_y = moves[i][1][0]
        new_x = moves[i][1][1]

        # Store the piece's current location (before the move)
        current_piece = moves[i][0]
        old_y = current_piece.column
        old_x = current_piece.row

        # Temporarily change the piece's location
        current_piece.column = new_y
        current_piece.row = new_x

        # Check if an enemy piece is currently in the square you would like to move to
        old_piece = game.board[new_y][new_x]
        removed = False
        if old_piece is not None and old_piece in game.black_pieces:
            game.black_pieces.remove(old_piece)
            removed = True
        # Move the piece on the board
        game.board[new_y][new_x] = current_piece

        # Find the best next move AFTER this move
        next_move = minimax_helper(game, turns - 1, True)

        # If the board state is better than our current board state, make it our new best move
        if next_move[0] == min_score:
            best_moves.append([next_move[0], current_piece, moves[i]])
        if next_move[0] < min_score:
            min_score = next_move[0]
            best_moves = [[next_move[0], current_piece, moves[i]]]

        # Move the piece back to where it belongs
        current_piece.column = old_y
        current_piece.row = old_x

        # If we removed a piece, add it back
        if old_piece is not None and removed:
            game.black_pieces.append(old_piece)
        game.board[old_y][old_x] = current_piece
        if removed or old_piece is None:
            game.board[new_y][new_x] = old_piece

    # If there are multiple best removes, randomly select one
    if len(best_moves) > 1:
        return best_moves[randrange(len(best_moves))]
    return best_moves[0]


# Formula for weighting moves in the mini_max algorithm.
# Temporarily returns sum of the values of black pieces - the sum of the value of white pieces.
def basic_eval(white_pieces, black_pieces):
    total_value = 0
    for piece in white_pieces:
        total_value -= piece.val
    for piece in black_pieces:
        total_value += piece.val
    return total_value


def basic_board_eval(board):
    total_value = 0
    for i in range(len(board)):
        for j in range(len(board)):
            if board[i][j] is not None:
                if board[i][j].color == Color.WHITE:
                    total_value -= board[i][j].val
                else:
                    total_value += board[i][j].val
    return total_value


# Principles:
# 1.) Knights and bishops come before queens and rooks
# 2.) Try to develop pieces towards the center
# 3.) Try not to move a piece twice before move 10
# 4.) Don't bring your queen out too early
# 5.) Castle before move 10
# 6.) Attack towards the center
# 7.) "Connect" your rooks: Make it so there are no pieces between them
def early_eval(white_pieces, black_pieces):
    total_value = 0
    for piece in white_pieces:
        total_value -= piece.val
        if isinstance(piece, Bishop) and piece.column != 0:
            total_value -= .1
        if isinstance(piece, Knight) and piece.column != 0:
            total_value -= .1
        if piece.moved:
            total_value -= .1
        if 1 < piece.row < 6:
            total_value -= .1
        if piece.column < 6:
            total_value -= .1
    for piece in black_pieces:
        total_value += piece.val
        if isinstance(piece, Bishop) and piece.column != 0:
            print(piece.val)
            total_value += .1
        if isinstance(piece, Knight) and piece.column != 0:
            total_value += .1
        if piece.moved:
            total_value += .1
        if 1 < piece.row < 6:
            total_value += .1
        if piece.column > 1:
            total_value += .1
    return total_value


# Middle Game Principles
# Ability for pieces to move becomes important
# Try to get a pawn close to promotion
def middle_eval(game, white_pieces, black_pieces):
    total_value = 0
    for piece in white_pieces:
        total_value -= piece.val
        moves = len(piece.available_moves(game.board))
        total_value -= moves * .05
        if isinstance(piece, Pawn):
            total_value -= 1
    for piece in black_pieces:
        total_value += piece.val
        moves = len(piece.available_moves(game.board))
        total_value += moves * .05
        if isinstance(piece, Pawn):
            total_value += 1
    return total_value


# Try to promote a pawn
def endgame_eval(white_pieces, black_pieces):
    total_value = 0
    for piece in white_pieces:
        total_value -= piece.val
        if isinstance(piece, Pawn):
            total_value += 1.5
    for piece in black_pieces:
        total_value += piece.val
        if isinstance(piece, Pawn):
            total_value += 1.5
    return total_value
