import chess
import myengine
import ml_model
import numpy as np

NUM_GAMES = 10
MAX_MOVES = 80
DEPTH = 2

def play_game():
    board = chess.Board()
    evaluator = myengine.Evaluator(use_ml=False)
    engine = myengine.MyEngine(evaluator, depth=DEPTH)
    positions = []
    while not board.is_game_over() and len(positions) < MAX_MOVES:
        positions.append(board.copy())
        move = engine.choose_move(board)
        if move:
            board.push(move)
        else:
            break
    # Assign final score: 1=white win, -1=black win, 0=draw
    if board.is_checkmate():
        score = 1 if board.turn == chess.BLACK else -1
    else:
        score = 0
    return positions, score

def generate_selfplay_data(num_games=NUM_GAMES):
    X = []
    y = []
    for i in range(num_games):
        positions, result = play_game()
        for board in positions:
            X.append(ml_model.board_to_tensor(board).numpy().flatten())
            y.append([result])
        print(f"Game {i+1}/{num_games} complete, result: {result}")
    X = np.stack(X)
    y = np.stack(y)
    np.savez('selfplay_data.npz', X=X, y=y)
    print(f"Saved {len(X)} positions to selfplay_data.npz")

if __name__ == '__main__':
    generate_selfplay_data() 