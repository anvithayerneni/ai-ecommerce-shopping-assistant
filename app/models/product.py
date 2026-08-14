from sqlalchemy import Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    external_id: Mapped[str | None] = mapped_column(
    String(100),
    nullable=True,
    unique=True,
    index=True,
)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    brand: Mapped[str | None] = mapped_column(String(100), nullable=True)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)

    subcategory: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )

    price: Mapped[float] = mapped_column(Float, nullable=False)
    rating: Mapped[float | None] = mapped_column(Float, nullable=True)
    stock: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    tags: Mapped[str | None] = mapped_column(Text, nullable=True)
    features: Mapped[str | None] = mapped_column(Text, nullable=True)
    target_audience: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )
    use_cases: Mapped[str | None] = mapped_column(Text, nullable=True)
    color: Mapped[str | None] = mapped_column(String(100), nullable=True)
    material: Mapped[str | None] = mapped_column(String(100), nullable=True)

    search_text: Mapped[str | None] = mapped_column(Text, nullable=True)