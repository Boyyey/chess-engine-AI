import chess
import numpy as np
import ml_model

# Piece values for classic evaluation
PIECE_VALUES = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: 0
}

# Piece-square tables (example for pawns, can be extended)
PAWN_TABLE = np.array([
    0, 0, 0, 0, 0, 0, 0, 0,
    5, 5, 5, 5, 5, 5, 5, 5,
    1, 1, 2, 3, 3, 2, 1, 1,
    0.5, 0.5, 1, 2.5, 2.5, 1, 0.5, 0.5,
    0, 0, 0, 2, 2, 0, 0, 0,
    0.5, -0.5, -1, 0, 0, -1, -0.5, 0.5,
    0.5, 1, 1, -2, -2, 1, 1, 0.5,
    0, 0, 0, 0, 0, 0, 0, 0
])

# Modular evaluation function
class Evaluator:
    def __init__(self, use_ml=False, ml_model=None):
        self.use_ml = use_ml
        self.ml_model = ml_model  # Should be a loaded PyTorch model

    def evaluate(self, board: chess.Board):
        if self.use_ml and self.ml_model:
            return ml_model.evaluate_board_ml(self.ml_model, board)
        else:
            return self.evaluate_classic(board)

    def evaluate_classic(self, board: chess.Board):
        score = 0
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                value = PIECE_VALUES.get(piece.piece_type, 0)
                if piece.color == chess.WHITE:
                    score += value
                    if piece.piece_type == chess.PAWN:
                        score += PAWN_TABLE[square] * 0.1
                else:
                    score -= value
                    if piece.piece_type == chess.PAWN:
                        score -= PAWN_TABLE[chess.square_mirror(square)] * 0.1
        return score

    def evaluate_ml(self, board: chess.Board):
        # Placeholder for ML model evaluation
        # Example: return float(self.ml_model.predict(board_to_tensor(board)))
        return 0

# To use a trained ML model:
# from ml_model import load_model
# ml = load_model('ml_model.pth')
# evaluator = Evaluator(use_ml=True, ml_model=ml)

# Minimax with alpha-beta pruning
class MyEngine:
    def __init__(self, evaluator: Evaluator, depth=2):
        self.evaluator = evaluator
        self.depth = depth

    def choose_move(self, board: chess.Board):
        best_score = float('-inf') if board.turn == chess.WHITE else float('inf')
        best_move = None
        for move in board.legal_moves:
            board.push(move)
            score = self.minimax(board, self.depth-1, float('-inf'), float('inf'), not board.turn)
            board.pop()
            if board.turn == chess.WHITE:
                if score > best_score:
                    best_score = score
                    best_move = move
            else:
                if score < best_score:
                    best_score = score
                    best_move = move
        return best_move

    def minimax(self, board, depth, alpha, beta, maximizing):
        if depth == 0 or board.is_game_over():
            return self.evaluator.evaluate(board)
        if maximizing:
            max_eval = float('-inf')
            for move in board.legal_moves:
                board.push(move)
                eval = self.minimax(board, depth-1, alpha, beta, False)
                board.pop()
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for move in board.legal_moves:
                board.push(move)
                eval = self.minimax(board, depth-1, alpha, beta, True)
                board.pop()
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval 