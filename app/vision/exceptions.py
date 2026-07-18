from __future__ import annotations


class VisionError(Exception):
    error_code = "VISION_ERROR"

    def __init__(self, message: str | None = None, *, error_code: str | None = None) -> None:
        super().__init__(message or error_code or self.error_code)
        if error_code:
            self.error_code = error_code


class VisionAnalysisUnavailableError(VisionError):
    error_code = "VISION_ANALYSIS_UNAVAILABLE"


class VisionValidationError(VisionError):
    error_code = "VISION_VALIDATION_ERROR"


class VisionProviderError(VisionError):
    error_code = "VISION_PROVIDER_UNAVAILABLE"


class VisionRateLimitError(VisionError):
    error_code = "VISION_RATE_LIMIT"


class VisionDuplicateRequestError(VisionError):
    error_code = "VISION_DUPLICATE_REQUEST"
