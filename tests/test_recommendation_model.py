import torch

from app.services.recommendation_model import (
    ProductEncoder,
    create_product_encoder,
)


def test_product_encoder_output_shape():
    model = ProductEncoder(
        input_dim=5,
        hidden_dim=32,
        embedding_dim=16,
    )

    features = torch.tensor(
        [
            [0.5, 0.9, 100.0, 10.0, 8.0],
            [0.2, 0.8, 80.0, 8.0, 7.0],
        ],
        dtype=torch.float32,
    )

    output = model(features)

    assert output.shape == (2, 16)


def test_product_encoder_handles_single_product():
    model = ProductEncoder()

    features = torch.tensor(
        [[0.5, 0.9, 100.0, 10.0, 8.0]],
        dtype=torch.float32,
    )

    output = model(features)

    assert output.shape == (1, 16)


def test_create_product_encoder():
    model = create_product_encoder(
        input_dim=5,
        hidden_dim=32,
        embedding_dim=16,
    )

    assert isinstance(model, ProductEncoder)


def test_product_encoder_is_deterministic_in_eval_mode():
    torch.manual_seed(42)

    model = ProductEncoder()
    model.eval()

    features = torch.tensor(
        [[0.5, 0.9, 100.0, 10.0, 8.0]],
        dtype=torch.float32,
    )

    output_1 = model(features)
    output_2 = model(features)

    assert torch.equal(output_1, output_2)
