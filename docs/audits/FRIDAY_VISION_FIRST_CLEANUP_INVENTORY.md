# Friday Vision-First Cleanup Inventory

Status: Sprint Friday Reset V1.0

## Summary

The Friday runtime is being reset from broker-first chart mirroring to a Vision-First workflow. This inventory documents broker-era files before removal or archival.

## KEEP

| Path | Responsibility | Runtime use | Tests | Decision | Justification |
| --- | --- | --- | --- | --- | --- |
| `app/main.py` | FastAPI app creation and lifespan | Yes | API tests | KEEP | Main app remains the HTTP entrypoint, with broker startup removed. |
| `app/api/router.py` | API route composition | Yes | API tests | KEEP | Keeps safe routes and includes Vision. |
| `app/api/routes/health.py` | Health check | Yes | Health tests | KEEP | Neutral application health. |
| `app/api/routes/system.py` | System metadata | Yes | Existing tests | KEEP | Neutral runtime support. |
| `app/api/routes/risk.py` | Risk domain | Yes | Risk tests | KEEP | Reusable for Vision decisions. |
| `app/market/analysis/` | Neutral market analysis contracts/statistics | No broker startup | Analysis tests | KEEP | Can be adapted to consume visual market interpretation later. |
| `frontend/src/components/` | Reusable UI components | Yes | Frontend build | KEEP | Visual shell remains useful. |
| `frontend/src/branding/` | Brand identity | Yes | Frontend build | KEEP | Product identity remains valid. |

## ADAPT

| Path | Responsibility | Runtime use | Tests | Decision | Justification |
| --- | --- | --- | --- | --- | --- |
| `app/core/config.py` | Settings | Yes | Config/API tests | ADAPT | Broker flags are deprecated; Vision flags added. |
| `frontend/src/App.tsx` | Route selection | Yes | Frontend build | ADAPT | Main flow now routes to Vision placeholder. |
| `frontend/src/hooks/useAppNavigation.ts` | Route normalization | Yes | Frontend build | ADAPT | Broker chart routes now normalize to `/vision`. |
| `frontend/src/components/Sidebar/index.tsx` | Navigation | Yes | Frontend build | ADAPT | Navigation now highlights Vision, History, Risk, Settings. |
| `app/api/routes/market_chart.py` | Old broker chart endpoint | Yes, retired response | Route tests pending | ADAPT | Retained temporarily as 410 Gone for clients during transition. |
| `app/api/routes/market_provider_v2.py` | Old provider status endpoint | Yes, retired response | Route tests pending | ADAPT | Retained temporarily as 410 Gone for clients during transition. |
| `app/api/routes/market_providers.py` | Old broker provider endpoints | Yes, retired response | Route tests pending | ADAPT | Retained temporarily as 410 Gone for clients during transition. |
| `tests/conftest.py` | Test collection policy | Yes, test-only | Full suite | ADAPT | Broker-runtime route tests are removed from active collection while preserved in the tree as archived validation history. |

## ARCHIVE

| Path | Responsibility | Runtime use | Tests | Decision | Justification |
| --- | --- | --- | --- | --- | --- |
| `app/market/providers/pocket/` | Pocket CDP/replay/read-only research | No after router cleanup | Pocket tests | ARCHIVE | Valuable protocol research; should not remain in runtime path long term. |
| `app/market/providers/polarium/` | Polarium CDP/runtime research | No after startup cleanup | Polarium tests | ARCHIVE | Valuable broker research; should move under `_archive/broker_integrations/polarium`. |
| `tools/pocket_discovery/` | Pocket HAR discovery | No | Tool tests | ARCHIVE | Research-only tooling. |
| `tools/pocket_parser/` | Pocket offline parser | No | Tool tests | ARCHIVE | Research-only parser. |
| `tools/pocket_live_observation/` | Pocket CDP observation CLI | No | Provider/tool tests | ARCHIVE | Research-only live observation. |
| `docs/ws/` | Polarium WebSocket evidence | No | N/A | ARCHIVE | Technical evidence belongs under broker archive. |
| `docs/POCKET_PROVIDER_V2_ADAPTER.md` | Pocket provider architecture | No | N/A | ARCHIVE | Broker-specific historical record. |
| `docs/PROVIDER_V2_ARCHITECTURE.md` | Broker provider abstraction | No | N/A | ARCHIVE | Broker-specific historical record. |
| `tests/api/test_iq_option_realtime_stream_route.py` | IQ Option SSE runtime assertions | No | Archived by `tests/conftest.py` | ARCHIVE | Asserts a retired provider runtime endpoint. |
| `tests/connector/polarium/live_session/test_authorized_session_runtime_foundation.py` | Polarium live-session route assertions | No | Archived by `tests/conftest.py` | ARCHIVE | Asserts retired Polarium session endpoints. |
| `tests/market/chart/test_market_chart_route.py` | Broker Chart API assertions | Retired 410 | Archived by `tests/conftest.py` | ARCHIVE | Chart API is no longer the principal Vision flow. |
| `tests/market/chart/test_market_chart_runtime_shared_store.py` | Shared CandleStore route assertions | Retired 410 | Archived by `tests/conftest.py` | ARCHIVE | Validates broker candle routing that is not active in Vision runtime. |
| `tests/market/chart/test_provider_v2_chart_route.py` | Provider V2 Chart API assertions | Retired 410 | Archived by `tests/conftest.py` | ARCHIVE | Validates retired provider-to-chart integration. |
| `tests/market/persistence/test_candle_integrity_audit.py` | Broker candle persistence audit route assertions | No active Vision runtime | Archived by `tests/conftest.py` | ARCHIVE | Candle integrity audit was tied to broker CandleStore persistence. |
| `tests/market/persistence/test_local_candle_persistence.py` | Broker candle SQLite persistence assertions | No active Vision runtime | Archived by `tests/conftest.py` | ARCHIVE | Candle persistence was broker-candle specific. |
| `tests/market/providers/test_iq_option_read_only_provider.py` | IQ Option provider runtime assertions | No | Archived by `tests/conftest.py` | ARCHIVE | Provider is no longer runtime-active. |
| `tests/market/runtime/test_authorized_browser_bridge_runtime.py` | Browser Bridge runtime assertions | No | Archived by `tests/conftest.py` | ARCHIVE | Browser Bridge is retired from runtime. |
| `tests/market/runtime/test_controlled_candle_stream_simulator.py` | Simulated candle runtime assertions | No | Archived by `tests/conftest.py` | ARCHIVE | Simulator is retired from runtime. |
| `tests/market/runtime/test_controlled_runtime_feed.py` | Development runtime-feed assertions | No | Archived by `tests/conftest.py` | ARCHIVE | Runtime feed is retired from runtime. |
| `tests/test_ai_decision.py` | Candle-based AI decision assertions | No | Archived by `tests/conftest.py` | ARCHIVE | Legacy candle decision engine is not the Vision multimodal engine. |
| `tests/test_asset_scanner.py` | Broker asset scanner assertions | No | Archived by `tests/conftest.py` | ARCHIVE | Scanner is not part of Vision-first baseline. |
| `tests/test_autotrade_gate.py` | AutoTrade gate assertions | No | Archived by `tests/conftest.py` | ARCHIVE | AutoTrade is out of the Vision-first runtime. |
| `tests/test_execution_engine.py` | Demo execution assertions | No | Archived by `tests/conftest.py` | ARCHIVE | Execution runtime is retired. |
| `tests/test_live_market_engine.py` | Demo live market assertions | No | Archived by `tests/conftest.py` | ARCHIVE | Demo live-candle generation is retired from runtime. |
| `tests/test_live_workspace.py` | Live workspace assertions | No | Archived by `tests/conftest.py` | ARCHIVE | Live workspace is not part of Vision-first baseline. |
| `tests/test_market_intelligence.py` | Candle-based intelligence assertions | No | Archived by `tests/conftest.py` | ARCHIVE | Legacy candle intelligence is separate from future Vision analysis. |
| `tests/test_market_reader.py` | Provider-backed Market Reader assertions | No | Archived by `tests/conftest.py` | ARCHIVE | Provider-backed market reader is retired from runtime. |
| `tests/test_polarium_connector.py` | Polarium connector route assertions | No | Archived by `tests/conftest.py` | ARCHIVE | Connector routes are retired. |
| `tests/test_polarium_diagnostics.py` | Polarium diagnostics route assertions | No | Archived by `tests/conftest.py` | ARCHIVE | Broker diagnostics are archive-only. |
| `tests/test_polarium_direct_login_lab.py` | Polarium direct lab assertions | No | Archived by `tests/conftest.py` | ARCHIVE | Direct login lab is archive-only. |
| `tests/test_polarium_oauth_lab.py` | Polarium OAuth lab assertions | No | Archived by `tests/conftest.py` | ARCHIVE | OAuth lab is archive-only. |
| `tests/test_provider_engine.py` | Provider engine assertions | No | Archived by `tests/conftest.py` | ARCHIVE | Provider engine routes are retired from runtime. |
| `tests/test_provider_manager.py` | Legacy provider manager assertions | No | Archived by `tests/conftest.py` | ARCHIVE | Legacy provider manager is retired from runtime. |
| `tests/test_quadcode_demo.py` | Quadcode demo provider assertions | No | Archived by `tests/conftest.py` | ARCHIVE | Broker demo route is retired. |
| `tests/test_real_market_data_foundation.py` | Real market data scanner assertions | No | Archived by `tests/conftest.py` | ARCHIVE | Scanner/data-provider workflow is retired. |
| `tests/test_signal_engine.py` | Technical indicator signal assertions | No | Archived by `tests/conftest.py` | ARCHIVE | Indicator-based signals are out of scope for reset. |

## DELETE

| Path | Responsibility | Runtime use | Tests | Decision | Justification |
| --- | --- | --- | --- | --- | --- |
| `__pycache__/` and `.pyc` under broker modules | Generated bytecode | No | N/A | DELETE | Generated artifacts only. Do not stage. |
| Old broker-only frontend static tests | Broker UI assertions | No | Frontend tests | DELETE | Should be removed or archived after Vision tests replace them. |

## Runtime Import Notes

- `app/main.py` no longer starts Polarium CDP or Provider V2.
- `app/api/router.py` no longer includes Polarium, runtime feed, simulator, Quadcode, scanner, or execution broker routes.
- Broker implementation files remain in the working tree for auditability and future archival.

## Archive Target

Broker research should be moved gradually into:

```text
_archive/broker_integrations/
  pocket/
  polarium/
  provider_v2/
  chart_realtime/
  protocol_discovery/
```
