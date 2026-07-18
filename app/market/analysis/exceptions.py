from __future__ import annotations


class AnalysisError(Exception):
    error_code = "ANALYSIS_ERROR"


class InvalidProviderData(AnalysisError):
    error_code = "INVALID_PROVIDER_DATA"


class AnalysisUnavailable(AnalysisError):
    error_code = "ANALYSIS_UNAVAILABLE"


class StatisticsError(AnalysisError):
    error_code = "STATISTICS_ERROR"
