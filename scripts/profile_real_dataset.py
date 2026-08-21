import re

from datasets import load_dataset


DATASET_NAME = "Tokuhn/TSMPD-US-Public-v1_1"
SAMPLE_SIZE = 1000

PRICE_PATTERN = re.compile(
    r"\$\s?(\d+(?:,\d{3})*(?:\.\d{2})?)"
)


def extract_price(text: str) -> float | None:
    match = PRICE_PATTERN.search(text)

    if not match:
        return None

    return float(
        match.group(1).replace(",", "")
    )


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

    prices = [
        price
        for product in records
        if (
            price := extract_price(
                product.get("paragraph", "")
            )
        ) is not None
    ]

    embedding_dimensions = sorted(
        {
            len(product.get("embedding", []))
            for product in records
        }
    )

    unique_uids = len(
        {
            product.get("uid")
            for product in records
        }
    )

    unique_titles = len(
        {
            product.get("title")
            for product in records
        }
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

    print(f"Sample size: {len(records)}")
    print(f"Missing vendor: {missing_vendor}")
    print(f"Missing title: {missing_title}")
    print(f"Missing paragraph: {missing_paragraph}")
    print(f"Prices found: {len(prices)}")
    print(f"Embedding dimensions: {embedding_dimensions}")
    print(f"Unique UIDs: {unique_uids}")
    print(f"Unique titles: {unique_titles}")

    if prices:
        print()
        print("Price statistics:")
        print(f"Min: ${min(prices):,.2f}")
        print(f"Max: ${max(prices):,.2f}")
        print(
            f"Average: ${sum(prices) / len(prices):,.2f}"
        )

        sorted_prices = sorted(prices)

        median = sorted_prices[len(sorted_prices) // 2]

        print(f"Median: ${median:,.2f}")

        print()
        print("Lowest 10 prices:")

        for price in sorted_prices[:10]:
            print(f"${price:,.2f}")

        print()
        print("Highest 10 prices:")

        for price in sorted_prices[-10:]:
            print(f"${price:,.2f}")


if __name__ == "__main__":
    main()