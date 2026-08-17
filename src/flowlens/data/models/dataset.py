"""Dataset metadata model for the canonical industrial data contract."""

from datetime import date, datetime

from sqlalchemy import BigInteger, CheckConstraint, Date, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from flowlens.data import Base


class DatasetVersion(Base):
    """One complete synthetic dataset generation run."""

    __tablename__ = "dataset_version"
    __table_args__ = (
        CheckConstraint("period_start < period_end", name="valid_period"),
        CheckConstraint("seed >= 0", name="seed_nonnegative"),
        CheckConstraint(
            "profile IN ('test', 'ci', 'demo')",
            name="profile_allowed",
        ),
    )

    dataset_version_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    seed: Mapped[int] = mapped_column(BigInteger)
    generator_version: Mapped[str] = mapped_column(String(32))
    profile: Mapped[str] = mapped_column(String(16))
    period_start: Mapped[date] = mapped_column(Date)
    period_end: Mapped[date] = mapped_column(Date)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    content_hash: Mapped[str] = mapped_column(String(128))
    row_count_total: Mapped[int] = mapped_column(BigInteger)
