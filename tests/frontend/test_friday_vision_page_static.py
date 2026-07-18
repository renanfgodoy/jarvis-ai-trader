from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_vision_page_uses_functional_upload_and_analysis_flow() -> None:
    source = read("frontend/src/pages/Vision.tsx")

    assert "VisionUploader" in source
    assert "VisionAnalysisPanel" in source
    assert "analyzeVisionScreenshot" in source
    assert "AbortController" in source
    assert "crypto.randomUUID" in source
    assert "FRIDAY ESTÁ ANALISANDO" in source
    assert "ANALISAR GRÁFICO" in source


def test_vision_uploader_supports_file_drag_drop_clipboard_preview_and_cleanup() -> None:
    source = read("frontend/src/components/vision/VisionUploader.tsx")

    assert 'type="file"' in source
    assert "onDrop" in source
    assert "clipboardData" in source
    assert "window.addEventListener('paste'" in source
    assert "closest('input, textarea, [contenteditable=\"true\"]')" in source
    assert "URL.createObjectURL" in source
    assert "URL.revokeObjectURL" in source
    assert "localStorage" not in source
    assert "sessionStorage" not in source


def test_vision_api_uses_backend_formdata_request_id_and_no_openai_browser_call() -> None:
    source = read("frontend/src/services/visionApi.ts")

    assert "new FormData()" in source
    assert "'X-Request-ID'" in source
    assert "/vision/analyze" in source
    assert "openai" not in source.lower()
    assert "VITE_OPENAI_API_KEY" not in source


def test_vision_panel_shows_risk_warning_and_structured_fields() -> None:
    source = read("frontend/src/components/vision/VisionAnalysisPanel.tsx")

    assert "Confiança visual" in source
    assert "Condição de entrada" in source
    assert "Condição de invalidação" in source
    assert "A análise não garante resultado" in source
    assert "Possível cenário comprador" in source
    assert "Não operar neste contexto" in source
