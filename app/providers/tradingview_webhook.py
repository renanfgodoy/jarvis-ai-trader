from datetime import datetime, timezone

from app.models.provider import TradingViewWebhookPayload, TradingViewWebhookResponse


class TradingViewWebhookProvider:
    """Provider responsável por receber alertas enviados pelo TradingView.

    Importante: esta classe não faz scraping, não consome APIs privadas e não
    executa ordens. Ela apenas normaliza alertas recebidos por webhook para que
    outros módulos do J.A.R.V.I.S possam validar com IA e Risk Manager.
    """

    name = "TradingView"

    def __init__(self) -> None:
        self._queue: list[TradingViewWebhookPayload] = []

    def receive(self, payload: TradingViewWebhookPayload) -> TradingViewWebhookResponse:
        """Recebe, normaliza e coloca um alerta em fila em memória."""
        queued_at = datetime.now(timezone.utc)
        self._queue.append(payload)

        return TradingViewWebhookResponse(
            received=True,
            provider=self.name,
            status="queued",
            symbol=payload.symbol,
            timeframe=payload.timeframe,
            signal=payload.signal,
            price=payload.price,
            strategy=payload.strategy,
            queued_at=queued_at,
            message="TradingView webhook recebido e enfileirado para análise.",
        )

    def queued_count(self) -> int:
        """Retorna quantidade de alertas em memória nesta execução da API."""
        return len(self._queue)
