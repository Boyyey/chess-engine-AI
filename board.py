import chess

class ChessBoard:
    def __init__(self):
        self.board = chess.Board()

    def reset(self):
        self.board.reset()

    def print_board(self):
        print(self.board)

    def get_legal_moves(self):
        return list(self.board.legal_moves)

    def make_move(self, move_uci):
        move = chess.Move.from_uci(move_uci)
        if move in self.board.legal_moves:
            self.board.push(move)
            return True
        return False

    def undo_move(self):
        if self.board.move_stack:
            self.board.pop()

    def fen(self):
        return self.board.fen() 