from app.core.config import settings
from app.models.account import CURRENCY_SYMBOLS, MIN_ENTRY_BY_CURRENCY
from app.models.risk import RiskCheckRequest, RiskCheckResponse, RiskLevel


class RiskManagerService:
    """Valida operações contra as regras oficiais de proteção de banca."""

    def check(self, request: RiskCheckRequest) -> RiskCheckResponse:
        """Calcula risco e decide se a operação pode ser considerada."""
        minimum_entry = MIN_ENTRY_BY_CURRENCY[request.account_currency]
        currency_symbol = CURRENCY_SYMBOLS[request.account_currency]
        max_entry_allowed = round(request.bankroll * (settings.risk_percentage / 100), 2)
        recommended_entry = round(request.entry_value if request.entry_value is not None else max(minimum_entry, max_entry_allowed), 2)

        risk_score = 10
        reasons: list[str] = []
        warnings: list[str] = []
        rules_checked = [
            f"Entrada máxima: {settings.risk_percentage}% da banca",
            f"Stop win diário: {settings.max_daily_wins} WINs",
            f"Stop loss diário: {settings.max_daily_losses} LOSSes",
            f"Gale máximo permitido: {settings.max_gale_allowed}",
            f"Entrada mínima por moeda ({request.account_currency}): {currency_symbol}{minimum_entry:.2f}",
        ]

        if request.daily_wins >= settings.max_daily_wins:
            risk_score += 70
            reasons.append("Stop win diário atingido. Encerrar operações para proteger o resultado.")

        if request.daily_losses >= settings.max_daily_losses:
            risk_score += 85
            reasons.append("Stop loss diário atingido. Operação bloqueada para proteger a banca.")

        if recommended_entry > max_entry_allowed:
            risk_score += 45
            reasons.append("Entrada acima do limite oficial de 5% da banca.")

        if recommended_entry < minimum_entry:
            risk_score += 70
            reasons.append(f"Entrada abaixo do mínimo para {request.account_currency}: {currency_symbol}{minimum_entry:.2f}.")

        if request.gale_used > settings.max_gale_allowed:
            risk_score += 60
            reasons.append("Limite de Gale excedido. Gale 2 ou recuperação agressiva não permitidos.")

        if request.payout < settings.minimum_payout:
            risk_score += 25
            warnings.append("Payout abaixo do mínimo recomendado para validação futura.")

        if request.daily_losses == settings.max_daily_losses - 1:
            risk_score += 15
            warnings.append("Atenção: próximo LOSS atinge o stop diário.")

        if request.daily_wins == settings.max_daily_wins - 1:
            warnings.append("Atenção: próximo WIN atinge a meta diária oficial.")

        risk_score = min(risk_score, 100)
        allowed = risk_score < 70 and not reasons

        if allowed:
            reasons.append("Operação dentro das regras iniciais de risco.")

        return RiskCheckResponse(
            decision="APPROVED" if allowed else "BLOCKED",
            allowed=allowed,
            risk_level=self._risk_level(risk_score),
            risk_score=risk_score,
            bankroll=round(request.bankroll, 2),
            recommended_entry=recommended_entry,
            max_entry_allowed=max_entry_allowed,
            daily_wins=request.daily_wins,
            daily_losses=request.daily_losses,
            gale_used=request.gale_used,
            rules_checked=rules_checked,
            reasons=reasons,
            warnings=warnings,
            account_currency=request.account_currency,
            minimum_entry=minimum_entry,
            currency_symbol=currency_symbol,
        )

    @staticmethod
    def _risk_level(score: int) -> RiskLevel:
        if score >= 85:
            return "CRITICAL"
        if score >= 60:
            return "HIGH"
        if score >= 30:
            return "MEDIUM"
        return "LOW"
