import pygame
import sys
import os
import time
from board import ChessBoard
import chess
import myengine

# --- Config ---
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
BOARD_COLORS = [
    ((240, 217, 181), (181, 136, 99)),  # Default
    ((235, 236, 208), (119, 153, 84)),  # Green
    ((255, 255, 255), (0, 0, 0)),       # Classic
]
TIME_CONTROLS = [300, 600, 900]  # 5, 10, 15 minutes

# --- Main GUI Class ---
class ChessGUI:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1200, 800), pygame.RESIZABLE)
        pygame.display.set_caption('Chess Engine')
        self.clock = pygame.time.Clock()
        self.board = ChessBoard()
        self.selected_square = None
        self.legal_moves = []
        self.last_move = None
        self.running = True
        self.images = {}
        self.settings_open = False
        self.board_color_idx = 0
        self.show_move_highlight = True
        self.show_last_move_highlight = True
        self.show_coordinates = False
        self.show_clocks = True
        self.game_over = False
        self.result_text = ""
        self.move_history = []
        self.time_control_idx = 0
        self.time_left = [float(TIME_CONTROLS[self.time_control_idx]), float(TIME_CONTROLS[self.time_control_idx])]
        self.last_tick = time.time()
        self.active_color = 0  # 0=white, 1=black
        self.ai_depth = 2
        self.ai_eval_type = 'classic'  # or 'ml'
        self.evaluator = myengine.Evaluator(use_ml=False)
        self.engine = myengine.MyEngine(self.evaluator, depth=self.ai_depth)
        self.human_color = 0  # 0=white, 1=black (for now, only white)
        self.load_images()
        self.sidebar_scroll = 0
        self.sidebar_max_scroll = 0

    def load_images(self):
        for piece, filename in PIECE_TO_PNG.items():
            path = os.path.join(ASSETS_PATH, filename)
            if os.path.exists(path):
                self.images[piece] = pygame.image.load(path).convert_alpha()
            else:
                print(f"Warning: No PNG found for piece '{piece}' at {filename} in assets folder.")

    def get_layout(self):
        w, h = self.screen.get_size()
        board_size = min(h-60, w*0.65)
        sq_size = int(board_size // 8)
        board_left = 40
        board_top = (h - board_size) // 2
        sidebar_left = board_left + board_size + 40
        sidebar_width = w - sidebar_left - 40
        return board_left, board_top, board_size, sq_size, sidebar_left, sidebar_width

    def draw_board(self, board_left, board_top, sq_size):
        c1, c2 = BOARD_COLORS[self.board_color_idx % len(BOARD_COLORS)]
        for r in range(8):
            for c in range(8):
                color = c1 if (r + c) % 2 == 0 else c2
                pygame.draw.rect(self.screen, color, pygame.Rect(board_left + c*sq_size, board_top + r*sq_size, sq_size, sq_size))
        if self.show_coordinates:
            self.draw_coordinates(board_left, board_top, sq_size)

    def draw_coordinates(self, board_left, board_top, sq_size):
        font = pygame.font.SysFont(None, int(sq_size*0.3))
        files = 'abcdefgh'
        ranks = '87654321'
        for i in range(8):
            label = font.render(files[i], True, (80, 80, 80))
            self.screen.blit(label, (board_left + i*sq_size + sq_size//2 - label.get_width()//2, board_top + 8*sq_size + 2))
            label = font.render(ranks[i], True, (80, 80, 80))
            self.screen.blit(label, (board_left - 18, board_top + i*sq_size + sq_size//2 - label.get_height()//2))

    def draw_pieces(self, board_left, board_top, sq_size):
        board_fen = self.board.fen().split(' ')[0]
        rows = board_fen.split('/')
        for r, row in enumerate(rows):
            c = 0
            for char in row:
                if char.isdigit():
                    c += int(char)
                elif char in self.images:
                    img = pygame.transform.smoothscale(self.images[char], (sq_size, sq_size))
                    self.screen.blit(img, (board_left + c*sq_size, board_top + r*sq_size))
                    c += 1

    def draw_highlights(self, board_left, board_top, sq_size):
        overlay = pygame.Surface((sq_size, sq_size), pygame.SRCALPHA)
        # Selected piece
        if self.selected_square and self.show_move_highlight:
            s_row, s_col = self.selected_square
            overlay.fill((0, 200, 255, 60))
            self.screen.blit(overlay, (board_left + s_col*sq_size, board_top + s_row*sq_size))
            # Grey circles for possible moves
            for move in self.legal_moves:
                to_row, to_col = 7 - (move.to_square // 8), move.to_square % 8
                center = (board_left + to_col*sq_size + sq_size//2, board_top + to_row*sq_size + sq_size//2)
                pygame.draw.circle(self.screen, (120, 120, 120, 120), center, sq_size//6)
        # Last move
        if self.last_move and self.show_last_move_highlight:
            from_sq, to_sq = self.last_move
            f_row, f_col = from_sq
            t_row, t_col = to_sq
            overlay.fill((255, 255, 0, 60))
            self.screen.blit(overlay, (board_left + f_col*sq_size, board_top + f_row*sq_size))
            self.screen.blit(overlay, (board_left + t_col*sq_size, board_top + t_row*sq_size))
        # King in check
        if self.board.board.is_check():
            king_square = self.board.board.king(self.board.board.turn)
            if king_square is not None:
                row, col = 7 - (king_square // 8), king_square % 8
                overlay.fill((255, 0, 0, 80))
                self.screen.blit(overlay, (board_left + col*sq_size, board_top + row*sq_size))

    def draw_clocks(self, board_left, board_top, board_size, sq_size):
        if not self.show_clocks:
            return
        font = pygame.font.SysFont(None, int(sq_size*0.7))
        # White clock (bottom)
        w_time = self.format_time(self.time_left[0])
        w_color = (255, 255, 255) if self.active_color == 0 else (180, 180, 180)
        w_rect = pygame.Rect(board_left, board_top + board_size + 10, board_size, int(sq_size*0.8))
        pygame.draw.rect(self.screen, (40, 40, 40), w_rect, border_radius=8)
        w_label = font.render(f"White: {w_time}", True, w_color)
        self.screen.blit(w_label, (board_left + 20, board_top + board_size + 18))
        # Black clock (top)
        b_time = self.format_time(self.time_left[1])
        b_color = (255, 255, 255) if self.active_color == 1 else (180, 180, 180)
        b_rect = pygame.Rect(board_left, board_top - int(sq_size*0.8) - 10, board_size, int(sq_size*0.8))
        pygame.draw.rect(self.screen, (40, 40, 40), b_rect, border_radius=8)
        b_label = font.render(f"Black: {b_time}", True, b_color)
        self.screen.blit(b_label, (board_left + 20, board_top - int(sq_size*0.8) - 2))

    def format_time(self, t):
        mins = int(t) // 60
        secs = int(t) % 60
        return f"{mins}:{secs:02d}"

    def draw_move_list(self, sidebar_left, board_top, sq_size, sidebar_width):
        font = pygame.font.SysFont(None, int(sq_size*0.45))  # Smaller font
        y = board_top - self.sidebar_scroll
        sidebar_height = 8*sq_size + 40
        padding = 18
        pygame.draw.rect(self.screen, (30, 30, 30), (sidebar_left, board_top, sidebar_width, sidebar_height), border_radius=12)
        # Title
        title_font = pygame.font.SysFont(None, int(sq_size*0.6))
        title = title_font.render("Move List", True, (255, 255, 255))
        self.screen.blit(title, (sidebar_left + padding, y + 10))
        y += 38
        # Divider
        pygame.draw.line(self.screen, (80, 80, 80), (sidebar_left + padding, y), (sidebar_left + sidebar_width - padding, y), 2)
        y += 18  # Extra space after divider
        for idx, move in enumerate(self.move_history):
            move_str = f"{(idx//2)+1}. {move}" if idx % 2 == 0 else move
            color = (255, 255, 0) if idx == len(self.move_history)-1 else (220, 220, 220)
            label = font.render(move_str, True, color)
            self.screen.blit(label, (sidebar_left + padding, y))
            y += int(sq_size*0.38) + 6  # More vertical spacing
        # Calculate max scroll
        self.sidebar_max_scroll = max(0, y - board_top - sidebar_height + 40)
        # Always show scrollbar track
        bar_x = sidebar_left + sidebar_width - 16
        pygame.draw.rect(self.screen, (80, 80, 80), (bar_x, board_top, 12, sidebar_height), border_radius=6)
        # Draw scrollbar thumb if needed
        if self.sidebar_max_scroll > 0:
            bar_height = max(40, sidebar_height * sidebar_height // (y - board_top))
            scroll_y = board_top + int(self.sidebar_scroll * (sidebar_height - bar_height) / self.sidebar_max_scroll)
            pygame.draw.rect(self.screen, (180, 180, 180), (bar_x, scroll_y, 12, bar_height), border_radius=6)
        else:
            # Show full thumb if not scrollable
            pygame.draw.rect(self.screen, (180, 180, 180), (bar_x, board_top, 12, sidebar_height), border_radius=6)

    def draw_settings_menu(self, sidebar_left, board_top, sq_size, sidebar_width):
        overlay = pygame.Surface((sidebar_width, 8*sq_size + 40), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220))
        self.screen.blit(overlay, (sidebar_left, board_top))
        font = pygame.font.SysFont(None, int(sq_size*0.8))
        text = font.render('Settings', True, (255, 255, 255))
        y = board_top + 20 - self.sidebar_scroll
        self.screen.blit(text, (sidebar_left + sidebar_width//2 - text.get_width()//2, y))
        font2 = pygame.font.SysFont(None, int(sq_size*0.6))
        y += 60
        options = [
            (f'R - Reset Game', None),
            (f'C - Change Board Color', None),
            (f'T - Change Time Control: {TIME_CONTROLS[self.time_control_idx]//60} min', None),
            (f'M - Toggle Move Highlight: {"ON" if self.show_move_highlight else "OFF"}', None),
            (f'L - Toggle Last Move Highlight: {"ON" if self.show_last_move_highlight else "OFF"}', None),
            (f'O - Toggle Coordinates: {"ON" if self.show_coordinates else "OFF"}', None),
            (f'K - Toggle Clocks: {"ON" if self.show_clocks else "OFF"}', None),
            (f'ESC - Close Settings', None),
        ]
        for label, _ in options:
            opt = font2.render(label, True, (255, 255, 255))
            self.screen.blit(opt, (sidebar_left + 30, y))
            y += int(sq_size*0.7)
        # Calculate max scroll for settings
        self.sidebar_max_scroll = max(0, y - board_top - (8*sq_size + 40) + 40)
        # Draw scrollbar if needed
        sidebar_height = 8*sq_size + 40
        if self.sidebar_max_scroll > 0:
            bar_height = max(40, sidebar_height * sidebar_height // (y - board_top))
            scroll_y = board_top + int(self.sidebar_scroll * (sidebar_height - bar_height) / self.sidebar_max_scroll)
            pygame.draw.rect(self.screen, (80, 80, 80), (sidebar_left + sidebar_width - 16, board_top, 12, sidebar_height), border_radius=6)
            pygame.draw.rect(self.screen, (180, 180, 180), (sidebar_left + sidebar_width - 16, scroll_y, 12, bar_height), border_radius=6)

    def draw_game_over(self, w, h):
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        font = pygame.font.SysFont(None, 60)
        text = font.render(self.result_text, True, (255, 255, 255))
        self.screen.blit(text, (w//2 - text.get_width()//2, h//2 - 60))
        font2 = pygame.font.SysFont(None, 36)
        btn = font2.render('N - New Game', True, (255, 255, 255))
        self.screen.blit(btn, (w//2 - btn.get_width()//2, h//2 + 10))

    def check_game_over(self):
        if self.time_left[0] <= 0:
            self.game_over = True
            self.result_text = 'Black wins by timeout!'
        elif self.time_left[1] <= 0:
            self.game_over = True
            self.result_text = 'White wins by timeout!'
        elif self.board.board.is_checkmate():
            self.game_over = True
            winner = 'Black' if self.board.board.turn else 'White'
            self.result_text = f'{winner} wins by checkmate!'
        elif self.board.board.is_stalemate():
            self.game_over = True
            self.result_text = 'Draw by stalemate!'
        elif self.board.board.is_insufficient_material():
            self.game_over = True
            self.result_text = 'Draw by insufficient material!'
        elif self.board.board.is_seventyfive_moves():
            self.game_over = True
            self.result_text = 'Draw by 75-move rule!'
        elif self.board.board.is_fivefold_repetition():
            self.game_over = True
            self.result_text = 'Draw by 5-fold repetition!'
        elif self.board.board.is_variant_draw():
            self.game_over = True
            self.result_text = 'Draw!'
        else:
            self.game_over = False
            self.result_text = ''

    def update_clocks(self):
        if self.settings_open or self.game_over:
            self.last_tick = time.time()
            return
        now = time.time()
        dt = now - self.last_tick
        self.last_tick = now
        self.active_color = 0 if self.board.board.turn else 1
        self.time_left[self.active_color] -= dt
        if self.time_left[self.active_color] < 0:
            self.time_left[self.active_color] = 0

    def draw_sidebar(self, sidebar_left, board_top, sq_size, sidebar_width, sidebar_height):
        # Sidebar background
        pygame.draw.rect(self.screen, (30, 30, 30), (sidebar_left, board_top, sidebar_width, sidebar_height), border_radius=12)
        y = board_top
        padding = 18
        # Clocks
        font_clock = pygame.font.SysFont(None, int(sq_size*0.6))
        w_time = self.format_time(self.time_left[0])
        b_time = self.format_time(self.time_left[1])
        w_color = (255, 255, 255) if self.active_color == 0 else (180, 180, 180)
        b_color = (255, 255, 255) if self.active_color == 1 else (180, 180, 180)
        w_label = font_clock.render(f"White: {w_time}", True, w_color)
        b_label = font_clock.render(f"Black: {b_time}", True, b_color)
        self.screen.blit(w_label, (sidebar_left + padding, y + 10))
        self.screen.blit(b_label, (sidebar_left + padding, y + 10 + w_label.get_height() + 8))
        y += 10 + w_label.get_height() + 8 + b_label.get_height() + 18
        # Move List Title
        title_font = pygame.font.SysFont(None, int(sq_size*0.6))
        title = title_font.render("Move List", True, (255, 255, 255))
        self.screen.blit(title, (sidebar_left + padding, y))
        y += 38
        y += 18  # Extra space after title
        # Move List
        font = pygame.font.SysFont(None, int(sq_size*0.45))
        for idx, move in enumerate(self.move_history):
            move_str = f"{(idx//2)+1}. {move}" if idx % 2 == 0 else move
            color = (255, 255, 0) if idx == len(self.move_history)-1 else (220, 220, 220)
            label = font.render(move_str, True, color)
            self.screen.blit(label, (sidebar_left + padding, y))
            y += int(sq_size*0.38) + 6
        # Settings (if open) - now handled in draw_settings_overlay

    def draw_settings_overlay(self, w, h, sidebar_left, board_top, sq_size, sidebar_width, sidebar_height):
        # Black overlay
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        # Settings panel
        pygame.draw.rect(self.screen, (30, 30, 30), (sidebar_left, board_top, sidebar_width, sidebar_height), border_radius=12)
        y = board_top + 30
        padding = 18
        font2 = pygame.font.SysFont(None, int(sq_size*0.6))
        settings_title = font2.render('Settings', True, (255, 255, 255))
        self.screen.blit(settings_title, (sidebar_left + padding, y))
        y += 38
        options = [
            (f'R - Reset Game', None),
            (f'C - Change Board Color', None),
            (f'T - Change Time Control: {TIME_CONTROLS[self.time_control_idx]//60} min', None),
            (f'D - AI Difficulty: {self.ai_depth}', None),
            (f'E - Evaluation: {self.ai_eval_type.upper()}', None),
            (f'M - Toggle Move Highlight: {"ON" if self.show_move_highlight else "OFF"}', None),
            (f'L - Toggle Last Move Highlight: {"ON" if self.show_last_move_highlight else "OFF"}', None),
            (f'O - Toggle Coordinates: {"ON" if self.show_coordinates else "OFF"}', None),
            (f'K - Toggle Clocks: {"ON" if self.show_clocks else "OFF"}', None),
            (f'ESC - Close Settings', None),
        ]
        for label, _ in options:
            opt = font2.render(label, True, (255, 255, 255))
            self.screen.blit(opt, (sidebar_left + padding, y))
            y += int(sq_size*0.7)

    def ai_move(self):
        # Only play if not game over and it's AI's turn
        if not self.game_over and self.board.board.turn == (self.human_color == 1):
            move = self.engine.choose_move(self.board.board)
            if move:
                san = self.board.board.san(move)
                self.board.make_move(move.uci())
                self.move_history.append(san)
                # Update last move for highlight
                from_sq = 7 - (move.from_square // 8), move.from_square % 8
                to_sq = 7 - (move.to_square // 8), move.to_square % 8
                self.last_move = (from_sq, to_sq)

    def run(self):
        last_settings_open = self.settings_open
        while self.running:
            self.update_clocks()
            self.check_game_over()
            w, h = self.screen.get_size()
            board_left, board_top, board_size, sq_size, sidebar_left, sidebar_width = self.get_layout()
            sidebar_height = 8*sq_size + 40
            # If it's AI's turn, make the AI move
            if not self.settings_open and not self.game_over and self.board.board.turn == (self.human_color == 1):
                self.ai_move()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                elif event.type == pygame.KEYDOWN:
                    if self.game_over and event.key == pygame.K_n:
                        self.board.reset()
                        self.selected_square = None
                        self.last_move = None
                        self.game_over = False
                        self.result_text = ''
                        self.move_history = []
                        self.time_left = [float(TIME_CONTROLS[self.time_control_idx]), float(TIME_CONTROLS[self.time_control_idx])]
                        self.last_tick = time.time()
                    if event.key == pygame.K_s:
                        self.settings_open = not self.settings_open
                    if self.settings_open:
                        if event.key == pygame.K_r:
                            self.board.reset()
                            self.selected_square = None
                            self.last_move = None
                            self.game_over = False
                            self.result_text = ''
                            self.move_history = []
                            self.time_left = [float(TIME_CONTROLS[self.time_control_idx]), float(TIME_CONTROLS[self.time_control_idx])]
                            self.last_tick = time.time()
                        elif event.key == pygame.K_c:
                            self.board_color_idx = (self.board_color_idx + 1) % len(BOARD_COLORS)
                        elif event.key == pygame.K_t:
                            self.time_control_idx = (self.time_control_idx + 1) % len(TIME_CONTROLS)
                            self.time_left = [float(TIME_CONTROLS[self.time_control_idx]), float(TIME_CONTROLS[self.time_control_idx])]
                            self.last_tick = time.time()
                        elif event.key == pygame.K_d:
                            self.ai_depth = (self.ai_depth % 4) + 1  # Cycle 1-4
                            self.engine.depth = self.ai_depth
                        elif event.key == pygame.K_e:
                            self.ai_eval_type = 'ml' if self.ai_eval_type == 'classic' else 'classic'
                            self.evaluator.use_ml = (self.ai_eval_type == 'ml')
                        elif event.key == pygame.K_m:
                            self.show_move_highlight = not self.show_move_highlight
                        elif event.key == pygame.K_l:
                            self.show_last_move_highlight = not self.show_last_move_highlight
                        elif event.key == pygame.K_o:
                            self.show_coordinates = not self.show_coordinates
                        elif event.key == pygame.K_k:
                            self.show_clocks = not self.show_clocks
                        elif event.key == pygame.K_ESCAPE:
                            self.settings_open = False
                elif event.type == pygame.MOUSEBUTTONDOWN and not self.settings_open and not self.game_over:
                    mx, my = event.pos
                    if board_left <= mx < board_left + 8*sq_size and board_top <= my < board_top + 8*sq_size:
                        col = (mx - board_left) // sq_size
                        row = (my - board_top) // sq_size
                        piece = self.get_piece_at(row, col)
                        if self.selected_square is None:
                            if piece and ((self.board.board.turn and piece.isupper()) or (not self.board.board.turn and piece.islower())):
                                self.selected_square = (row, col)
                                self.legal_moves = self.get_legal_moves_for_square(row, col)
                        else:
                            if (row, col) == self.selected_square:
                                self.selected_square = None
                                self.legal_moves = []
                            else:
                                move = None
                                for m in self.legal_moves:
                                    to_row, to_col = 7 - (m.to_square // 8), m.to_square % 8
                                    if (row, col) == (to_row, to_col):
                                        move = m
                                        break
                                if move:
                                    san = self.board.board.san(move)  # Get SAN before pushing
                                    self.board.make_move(move.uci())
                                    self.move_history.append(san)
                                    self.last_move = (self.selected_square, (row, col))
                                    self.selected_square = None
                                    self.legal_moves = []
                                else:
                                    if piece and ((self.board.board.turn and piece.isupper()) or (not self.board.board.turn and piece.islower())):
                                        self.selected_square = (row, col)
                                        self.legal_moves = self.get_legal_moves_for_square(row, col)
                                    else:
                                        self.selected_square = None
                                        self.legal_moves = []
            self.screen.fill((30, 30, 30))
            self.draw_board(board_left, board_top, sq_size)
            self.draw_pieces(board_left, board_top, sq_size)
            self.draw_highlights(board_left, board_top, sq_size)
            # Draw sidebar (clocks, move list)
            if not self.settings_open:
                self.draw_sidebar(sidebar_left, board_top, sq_size, sidebar_width, sidebar_height)
            else:
                self.draw_settings_overlay(w, h, sidebar_left, board_top, sq_size, sidebar_width, sidebar_height)
            if self.game_over:
                self.draw_game_over(w, h)
            pygame.display.flip()
            self.clock.tick(60)
        pygame.quit()
        sys.exit()

    def get_piece_at(self, row, col):
        board_fen = self.board.fen().split(' ')[0]
        rows = board_fen.split('/')
        fen_row = rows[row]
        c = 0
        for char in fen_row:
            if char.isdigit():
                c += int(char)
            else:
                if c == col:
                    return char
                c += 1
        return None

    def get_legal_moves_for_square(self, row, col):
        moves = []
        for move in self.board.get_legal_moves():
            from_row, from_col = 7 - (move.from_square // 8), move.from_square % 8
            if (from_row, from_col) == (row, col):
                moves.append(move)
        return moves

if __name__ == '__main__':
    gui = ChessGUI()
    gui.run() 