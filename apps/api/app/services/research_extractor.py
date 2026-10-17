from dataclasses import dataclass


@dataclass(frozen=True)
class ExtractionResult:
    status: str
    fields: dict
    warnings: list[str]


class ResearchExtractor:
    """Adapter boundary for future screenshot-to-offer extraction.

    The research import must remain usable without an AI provider. A future
    vision implementation can return candidate fields here, while an admin
    still verifies them before an OfferSnapshot becomes trusted evidence.
    """

    async def extract(self, image_bytes: bytes, content_type: str) -> ExtractionResult:
        return ExtractionResult(
            status="manual_review_required",
            fields={},
            warnings=["Automatic screenshot extraction is not configured; verify fields manually."],
        )


extractor = ResearchExtractor()
