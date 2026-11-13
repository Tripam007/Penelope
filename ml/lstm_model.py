"""
PENELOPE ML Engine - Small LSTM Sequence Model for Hydrology & Flash Floods
Provides PyTorch model architecture and pure-NumPy inference forward pass.
"""

from typing import Tuple, Dict, Any
import numpy as np


class NumpyLSTMInference:
    """
    Pure NumPy inference engine for trained LSTM weights.
    Ensures 100% zero-dependency cross-platform execution on all OS environments.
    """
    def __init__(self, weights: Dict[str, np.ndarray]):
        self.weights = weights
        # Shapes: input_size=4, hidden_size=32
        self.w_ih_l0 = weights.get("lstm.weight_ih_l0")
        self.w_hh_l0 = weights.get("lstm.weight_hh_l0")
        self.b_ih_l0 = weights.get("lstm.bias_ih_l0")
        self.b_hh_l0 = weights.get("lstm.bias_hh_l0")
        self.fc_w = weights.get("head.weight")
        self.fc_b = weights.get("head.bias")

    @staticmethod
    def _sigmoid(x: np.ndarray) -> np.ndarray:
        return 1.0 / (1.0 + np.exp(-np.clip(x, -25.0, 25.0)))

    def forward(self, sequence: np.ndarray) -> float:
        """
        Sequence shape: (24, 4) or (batch, 24, 4)
        Returns: predicted flash flood probability (0.0 to 1.0)
        """
        if sequence.ndim == 2:
            sequence = np.expand_dims(sequence, axis=0)

        batch_size, seq_len, _ = sequence.shape
        hidden_size = 32

        # Initialize states
        h = np.zeros((batch_size, hidden_size), dtype=np.float32)
        c = np.zeros((batch_size, hidden_size), dtype=np.float32)

        for t in range(seq_len):
            x_t = sequence[:, t, :]  # (batch, 4)

            # Gates: i, f, g, o
            gates = np.dot(x_t, self.w_ih_l0.T) + self.b_ih_l0 + np.dot(h, self.w_hh_l0.T) + self.b_hh_l0

            i_gate = self._sigmoid(gates[:, 0:hidden_size])
            f_gate = self._sigmoid(gates[:, hidden_size:2*hidden_size])
            g_gate = np.tanh(gates[:, 2*hidden_size:3*hidden_size])
            o_gate = self._sigmoid(gates[:, 3*hidden_size:4*hidden_size])

            c = f_gate * c + i_gate * g_gate
            h = o_gate * np.tanh(c)

        logits = np.dot(h, self.fc_w.T) + self.fc_b
        prob = self._sigmoid(logits)
        return float(prob[0, 0])


try:
    import torch
    import torch.nn as nn

    class SmallHydrologyLSTM(nn.Module):
        def __init__(self, input_size: int = 4, hidden_size: int = 32, num_layers: int = 1):
            super().__init__()
            self.lstm = nn.LSTM(
                input_size=input_size,
                hidden_size=hidden_size,
                num_layers=num_layers,
                batch_first=True
            )
            self.head = nn.Linear(hidden_size, 1)

        def forward(self, x: torch.Tensor) -> torch.Tensor:
            out, (h_n, c_n) = self.lstm(x)
            last_hidden = out[:, -1, :]
            logits = self.head(last_hidden)
            return torch.sigmoid(logits)

except Exception:
    SmallHydrologyLSTM = None  # Fallback gracefully if torch c-extensions blocked
