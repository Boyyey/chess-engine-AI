import torch
import torch.nn as nn
import numpy as np
import chess

class BoardMLP(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(8*8*12, 128)
        self.fc2 = nn.Linear(128, 64)
        self.fc3 = nn.Linear(64, 1)
        self.relu = nn.ReLU()

    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.relu(self.fc2(x))
        x = self.fc3(x)
        return x

def board_to_tensor(board: chess.Board):
    # 12 planes: [P,N,B,R,Q,K,p,n,b,r,q,k] for each square
    piece_map = board.piece_map()
    tensor = np.zeros((12, 8, 8), dtype=np.float32)
    for square, piece in piece_map.items():
        idx = piece_type_to_index(piece)
        row = 7 - (square // 8)
        col = square % 8
        tensor[idx, row, col] = 1.0
    return torch.tensor(tensor.flatten()).unsqueeze(0)

def piece_type_to_index(piece):
    offset = 0 if piece.color == chess.WHITE else 6
    return offset + {
        chess.PAWN: 0,
        chess.KNIGHT: 1,
        chess.BISHOP: 2,
        chess.ROOK: 3,
        chess.QUEEN: 4,
        chess.KING: 5
    }[piece.piece_type]

def evaluate_board_ml(model, board):
    model.eval()
    with torch.no_grad():
        x = board_to_tensor(board)
        out = model(x)
        return float(out.item())

def save_model(model, path):
    torch.save(model.state_dict(), path)

def load_model(path):
    model = BoardMLP()
    model.load_state_dict(torch.load(path, map_location=torch.device('cpu')))
    model.eval()
    return model 