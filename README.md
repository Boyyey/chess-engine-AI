# ♟️ Chess Engine with GUI

A simple, modern Python chess engine and GUI! Play chess against a basic AI, powered by minimax, with a beautiful board rendered in Pygame. Great for learning, tinkering, and extending with your own ideas! 🧠🎨

---

## 🚀 Features
- Play chess with a clean graphical interface
- Basic AI using minimax and material evaluation
- Move validation and undo support
- Easy to extend (add ML, new evaluation, etc.)

---

## 🧠 AI/ML Pipeline

This project is a full-stack chess AI/ML showcase:

- **Custom engine**: Modular minimax with alpha-beta pruning, classic and ML evaluation.
- **Neural network evaluation**: PyTorch MLP model for board evaluation (`ml_model.py`).
- **Self-play data generation**: `selfplay.py` generates labeled board positions for training.
- **Training script**: `train_ml.py` trains the neural network on self-play data.
- **Plug-and-play ML**: Easily switch between classic and ML evaluation in the GUI settings.

### Pipeline Diagram

```
[Self-Play Engine] --(positions, scores)--> [Training Script] --(trained model)--> [GUI/Engine]
```

### How to Use the ML Engine

1. **Generate self-play data:**
   ```bash
   python selfplay.py
   # Produces selfplay_data.npz
   ```
2. **Train the neural network:**
   ```bash
   python train_ml.py
   # Produces ml_model.pth
   ```
3. **Use the trained model in the GUI:**
   - The GUI will automatically use `ml_model.pth` if you select ML evaluation in the settings (press `S`, then `E`).

### Code Snippet: Loading the ML Model
```python
from ml_model import load_model
ml = load_model('ml_model.pth')
evaluator = Evaluator(use_ml=True, ml_model=ml)
```

---

## 🛠️ Setup

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/chess-engine.git
cd chess-engine
```

### 2. Create a virtual environment (recommended)
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate
```

### 3. Install requirements
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Add chess piece images
- Download chess piece PNGs (e.g., from [Wikimedia Commons](https://commons.wikimedia.org/wiki/Category:PNG_chess_pieces/Standard_transparent))
- Place them in the `assets/` folder as:
  - `wP.png`, `wN.png`, `wB.png`, `wR.png`, `wQ.png`, `wK.png`
  - `bP.png`, `bN.png`, `bB.png`, `bR.png`, `bQ.png`, `bK.png`

---

## 🏃 Usage

```bash
python gui.py
```
- Click to select and move pieces.
- Play against the AI (classic or ML evaluation).
- Press `S` for settings (change AI difficulty, evaluation, etc.).

---

## 📁 Project Structure
```
chess-engine/
├── board.py          # Board logic (python-chess wrapper)
├── engine.py         # Minimax & evaluation
├── myengine.py       # Custom AI/ML engine
├── ml_model.py       # PyTorch neural network
├── train_ml.py       # Training script
├── selfplay.py       # Self-play data generation
├── gui.py            # Pygame interface
├── assets/           # Piece images (PNGs)
├── requirements.txt  # Dependencies
└── README.md         # This file
```

---

## 🙏 Credits
- [python-chess](https://python-chess.readthedocs.io/)
- [pygame](https://www.pygame.org/)
- [PyTorch](https://pytorch.org/)
- [Wikimedia Commons](https://commons.wikimedia.org/wiki/Category:PNG_chess_pieces/Standard_transparent)

---

## 🌟 Contributing
Pull requests and suggestions are welcome! Open an issue or fork the repo to get started.

---

## 📜 License
MIT 
