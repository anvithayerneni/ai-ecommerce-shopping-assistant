import re

from datasets import load_dataset


DATASET_NAME = "Tokuhn/TSMPD-US-Public-v1_1"
SAMPLE_SIZE = 100


def main() -> None:
    dataset = load_dataset(
        DATASET_NAME,
        split="train",
        streaming=True,
    )

    records = []

    for product in dataset:
        records.append(product)

        if len(records) >= SAMPLE_SIZE:
            break

    price_pattern = re.compile(
        r"\$\s?\d+(?:,\d{3})*(?:\.\d{2})?"
    )

    missing_vendor = sum(
        not product.get("vendor")
        for product in records
    )

    missing_title = sum(
        not product.get("title")
        for product in records
    )

    missing_paragraph = sum(
        not product.get("paragraph")
        for product in records
    )

    price_found = sum(
        bool(
            price_pattern.search(
                product.get("paragraph", "")
            )
        )
        for product in records
    )

    embedding_dimensions = sorted(
        {
            len(product.get("embedding", []))
            for product in records
        }
    )

    unique_uids = len(
        {product.get("uid") for product in records}
    )

    unique_titles = len(
        {product.get("title") for product in records}
    )

    print(f"Sample size: {len(records)}")
    print(f"Missing vendor: {missing_vendor}")
    print(f"Missing title: {missing_title}")
    print(f"Missing paragraph: {missing_paragraph}")
    print(f"Price found: {price_found}")
    print(f"Embedding dimensions: {embedding_dimensions}")
    print(f"Unique UIDs: {unique_uids}")
    print(f"Unique titles: {unique_titles}")


if __name__ == "__main__":
    main()