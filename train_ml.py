import torch
import torch.optim as optim
import torch.nn as nn
import ml_model
import numpy as np

# Dummy data: list of (board_tensor, score)
def generate_dummy_data(num=1000):
    X = np.random.randn(num, 8*8*12).astype(np.float32)
    y = np.random.uniform(-10, 10, size=(num, 1)).astype(np.float32)
    return torch.tensor(X), torch.tensor(y)

def train():
    model = ml_model.BoardMLP()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    loss_fn = nn.MSELoss()
    X, y = generate_dummy_data(2000)
    epochs = 10
    for epoch in range(epochs):
        model.train()
        optimizer.zero_grad()
        out = model(X)
        loss = loss_fn(out, y)
        loss.backward()
        optimizer.step()
        print(f"Epoch {epoch+1}/{epochs} Loss: {loss.item():.4f}")
    ml_model.save_model(model, 'ml_model.pth')
    print("Model saved to ml_model.pth")

if __name__ == '__main__':
    train() 