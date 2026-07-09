from app.models.account import (
    CURRENCY_SYMBOLS,
    MIN_ENTRY_BY_CURRENCY,
    AccountCurrency,
    AutoTradeGateRequest,
    AutoTradeGateResponse,
)


class AutoTradeGateService:
    """Gate central de segurança antes de analisar, sinalizar ou executar.

    Regra oficial: o operador primeiro escolhe M1/M5/M15. Só depois, ao ativar
    AutoTrade, o J.A.R.V.I.S pode analisar, gerar sinal e encaminhar para execução
    DEMO. Conta real permanece bloqueada nesta fase.
    """

    def check(self, request: AutoTradeGateRequest) -> AutoTradeGateResponse:
        reasons: list[str] = []
        warnings: list[str] = []
        minimum_entry = MIN_ENTRY_BY_CURRENCY[request.currency]
        entry_value = round(request.entry_value if request.entry_value is not None else max(minimum_entry, request.balance * 0.05), 2)
        currency_symbol = CURRENCY_SYMBOLS[request.currency]
        can_analyze = True

        if request.timeframe not in ("M1", "M5", "M15"):
            can_analyze = False
            reasons.append("Selecione o timeframe operacional: M1, M5 ou M15.")

        if not request.autotrade_requested:
            can_analyze = False
            reasons.append("AutoTrade ainda não foi ativado. O robô não deve gerar sinal antes do clique.")

        if request.account_type != "DEMO":
            reasons.append("Conta REAL bloqueada. AutoTrade só é permitido em conta DEMO nesta fase.")

        if entry_value < minimum_entry:
            reasons.append(f"Entrada mínima para {request.currency}: {currency_symbol}{minimum_entry:.2f}.")

        if entry_value > request.balance:
            reasons.append("Entrada maior que o saldo disponível.")

        if not request.risk_approved:
            reasons.append("Risk Manager não aprovou a operação.")

        if request.score < request.minimum_score:
            reasons.append(f"Score insuficiente: {request.score}% abaixo do mínimo de {request.minimum_score}%.")

        if not request.asset_valid:
            reasons.append("Ativo inválido ou indisponível para o timeframe selecionado.")

        if not request.websocket_online:
            reasons.append("WebSocket offline. AutoTrade bloqueado para evitar execução sem dados ao vivo.")

        if not request.execution_ready:
            reasons.append("Execution Engine não está READY.")

        if request.currency == "BRL":
            warnings.append("Conta em BRL detectada: entrada mínima operacional R$5,00.")
        elif request.currency == "USD":
            warnings.append("Conta em USD detectada: entrada mínima operacional US$1,00.")

        allowed = not reasons and can_analyze
        status = "READY" if allowed else ("WAITING" if not request.autotrade_requested or not request.timeframe else "BLOCKED")

        if allowed:
            reasons.append("AutoTrade Gate aprovado para análise e execução DEMO controlada.")

        return AutoTradeGateResponse(
            allowed=allowed,
            status=status,
            symbol=request.symbol.strip().upper(),
            timeframe=request.timeframe,
            account_type=request.account_type,
            currency=request.currency,
            currency_symbol=currency_symbol,
            balance=round(request.balance, 2),
            entry_value=entry_value,
            minimum_entry=minimum_entry,
            score=request.score,
            minimum_score=request.minimum_score,
            can_analyze=allowed,
            autotrade_enabled=allowed,
            reasons=reasons,
            warnings=warnings,
            safety_rules=self.safety_rules(request.currency),
        )

    @staticmethod
    def safety_rules(currency: AccountCurrency = "BRL") -> list[str]:
        minimum = MIN_ENTRY_BY_CURRENCY[currency]
        symbol = CURRENCY_SYMBOLS[currency]
        return [
            "Operar somente em conta DEMO durante desenvolvimento.",
            "Selecionar timeframe M1, M5 ou M15 antes de qualquer análise.",
            "Gerar sinal apenas após o usuário ativar AutoTrade.",
            f"Respeitar entrada mínima da moeda: {symbol}{minimum:.2f}.",
            "AutoTrade depende de Risk Manager aprovado, score mínimo, ativo válido, WebSocket online e Execution Engine READY.",
        ]
