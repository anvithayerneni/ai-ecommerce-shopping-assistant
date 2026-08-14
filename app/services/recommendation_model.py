from __future__ import annotations

import torch
from torch import nn


class ProductEncoder(nn.Module):
    """
    Small neural encoder for structured product features.

    Input:
        Structured product feature vector.

    Output:
        Dense product representation.
    """

    def __init__(
        self,
        input_dim: int = 5,
        hidden_dim: int = 32,
        embedding_dim: int = 16,
    ) -> None:
        super().__init__()

        self.network = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, embedding_dim),
        )

    def forward(
        self,
        features: torch.Tensor,
    ) -> torch.Tensor:
        return self.network(features)


def create_product_encoder(
    input_dim: int = 5,
    hidden_dim: int = 32,
    embedding_dim: int = 16,
) -> ProductEncoder:
    """
    Create a product encoder with the configured dimensions.
    """

    return ProductEncoder(
        input_dim=input_dim,
        hidden_dim=hidden_dim,
        embedding_dim=embedding_dim,
    )
