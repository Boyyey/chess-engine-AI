import streamlit as st
import chess
import time
import os
import base64

ASSETS_PATH = os.path.join(os.path.dirname(__file__), 'assets')
PIECE_TO_PNG = {
    'P': 'pawn-w.png',
    'N': 'knight-w.png',
    'B': 'bishop-w.png',
    'R': 'rook-w.png',
    'Q': 'queen-w.png',
    'K': 'king-w.png',
    'p': 'pawn-b.png',
    'n': 'knight-b.png',
    'b': 'bishop-b.png',
    'r': 'rook-b.png',
    'q': 'queen-b.png',
    'k': 'king-b.png',
}

# Board rendering with PNGs
def render_board(board, selected=None, legal_sqs=None, square_px=56):
    sq_color = ["#f0d9b5", "#b58863"]
    table = f"<table style='border-collapse: collapse; margin:auto;'>"
    for r in range(8):
        table += "<tr>"
        for c in range(8):
            sq = chess.square(c, 7 - r)
            piece = board.piece_at(sq)
            color = sq_color[(r + c) % 2]
            style = f"background:{color};width:{square_px}px;height:{square_px}px;text-align:center;cursor:pointer;"
            if selected == sq:
                style += "border:3px solid #00bfff;"
            elif legal_sqs and sq in legal_sqs:
                style += "box-shadow:inset 0 0 10px #00bfff;"
            img_html = ''
            if piece:
                img_path = os.path.join(ASSETS_PATH, PIECE_TO_PNG[piece.symbol()])
                img_html = f"<img src='data:image/png;base64,{get_base64(img_path)}' width='{square_px-8}' height='{square_px-8}' style='vertical-align:middle;'/>"
            table += f"<td style='{style}' onClick=\"window.location.search='?move={sq}'\">{img_html}</td>"
        table += "</tr>"
    table += "</table>"
    return table

def get_base64(file_path):
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

# Streamlit app
st.set_page_config(page_title="Chess", layout="centered")
st.title("♟️ Streamlit Chess")

# Sidebar settings
st.sidebar.header("Settings")
time_control = st.sidebar.selectbox("Time Control (minutes)", [5, 10, 15], index=0)
if st.sidebar.button("Reset Game"):
    st.session_state.clear()
    st.rerun()

# Session state
if 'board' not in st.session_state:
    st.session_state.board = chess.Board()
    st.session_state.selected = None
    st.session_state.legal_sqs = []
    st.session_state.move_history = []
    st.session_state.clocks = [time_control*60, time_control*60]
    st.session_state.last_time = time.time()
    st.session_state.turn = 0  # 0=white, 1=black
    st.session_state.game_over = False
    st.session_state.result = ''

# Clocks
def update_clocks():
    if st.session_state.game_over:
        return
    now = time.time()
    dt = now - st.session_state.last_time
    st.session_state.clocks[st.session_state.turn] -= dt
    st.session_state.last_time = now
    if st.session_state.clocks[st.session_state.turn] < 0:
        st.session_state.clocks[st.session_state.turn] = 0
        st.session_state.game_over = True
        st.session_state.result = 'Black wins by timeout!' if st.session_state.turn == 0 else 'White wins by timeout!'

update_clocks()

# Game over detection
if st.session_state.board.is_checkmate():
    st.session_state.game_over = True
    winner = 'Black' if st.session_state.board.turn else 'White'
    st.session_state.result = f'{winner} wins by checkmate!'
elif st.session_state.board.is_stalemate():
    st.session_state.game_over = True
    st.session_state.result = 'Draw by stalemate!'
elif st.session_state.board.is_insufficient_material():
    st.session_state.game_over = True
    st.session_state.result = 'Draw by insufficient material!'

# Clocks display
col1, col2, col3 = st.columns([1,2,1])
with col1:
    st.markdown(f"**White:** {int(st.session_state.clocks[0]//60)}:{int(st.session_state.clocks[0]%60):02d}")
with col3:
    st.markdown(f"**Black:** {int(st.session_state.clocks[1]//60)}:{int(st.session_state.clocks[1]%60):02d}")

# Board and move list layout (compact)
colb, colm = st.columns([1.1,0.9], gap="small")
with colb:
    st.markdown(render_board(st.session_state.board, st.session_state.selected, st.session_state.legal_sqs, square_px=56), unsafe_allow_html=True)

# Move handling
query_params = st.query_params
if 'move' in query_params and not st.session_state.game_over:
    sq = int(query_params['move'][0])
    if st.session_state.selected is None:
        piece = st.session_state.board.piece_at(sq)
        if piece and ((st.session_state.board.turn and piece.color) or (not st.session_state.board.turn and not piece.color)):
            st.session_state.selected = sq
            st.session_state.legal_sqs = [move.to_square for move in st.session_state.board.legal_moves if move.from_square == sq]
    else:
        move = None
        for m in st.session_state.board.legal_moves:
            if m.from_square == st.session_state.selected and m.to_square == sq:
                move = m
                break
        if move:
            st.session_state.board.push(move)
            st.session_state.move_history.append(st.session_state.board.san(move))
            st.session_state.turn = 1 - st.session_state.turn
            st.session_state.selected = None
            st.session_state.legal_sqs = []
            st.session_state.last_time = time.time()
        else:
            st.session_state.selected = None
            st.session_state.legal_sqs = []
    st.query_params.clear()
    st.rerun()

# Move list
with colm:
    st.markdown("### Move List")
    moves = st.session_state.move_history
    for i in range(0, len(moves), 2):
        w = moves[i]
        b = moves[i+1] if i+1 < len(moves) else ''
        st.write(f"{i//2+1}. {w} {b}")
    if st.session_state.game_over:
        st.markdown(f"## {st.session_state.result}") 