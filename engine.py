from board import ChessBoard

piece_values = {
    'P': 1, 'N': 3, 'B': 3, 'R': 5, 'Q': 9, 'K': 0,
    'p': -1, 'n': -3, 'b': -3, 'r': -5, 'q': -9, 'k': 0
}

def evaluate_board(board: ChessBoard):
    fen = board.fen()
    board_part = fen.split(' ')[0]
    score = 0
    for c in board_part:
        if c in piece_values:
            score += piece_values[c]
    return score

def minimax(board: ChessBoard, depth, maximizing):
    if depth == 0 or board.board.is_game_over():
        return evaluate_board(board), None

    best_move = None
    if maximizing:
        max_eval = float('-inf')
        for move in board.get_legal_moves():
            board.make_move(move.uci())
            eval, _ = minimax(board, depth-1, False)
            board.undo_move()
            if eval > max_eval:
                max_eval = eval
                best_move = move
        return max_eval, best_move
    else:
        min_eval = float('inf')
        for move in board.get_legal_moves():
            board.make_move(move.uci())
            eval, _ = minimax(board, depth-1, True)
            board.undo_move()
            if eval < min_eval:
                min_eval = eval
                best_move = move
        return min_eval, best_move 