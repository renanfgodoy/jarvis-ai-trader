# Market Analysis Engine

This package is the first architecture layer for Friday AI Platform market intelligence.

It consumes only Provider V2 neutral models and produces `MarketAnalysis`.

## Scope

Implemented in this sprint:

- data normalization;
- market snapshot;
- basic statistics;
- health evaluation;
- metadata generation;
- typed analysis result.

Out of scope:

- indicators;
- strategies;
- CALL or PUT;
- signals;
- probability engine;
- AutoTrade;
- frontend integration;
- Chart API integration.

## Flow

```text
Provider Models
  -> AnalysisContext
  -> MarketAnalysisEngine
  -> MarketAnalysis
```

The engine must not import concrete providers such as Pocket or Polarium.
