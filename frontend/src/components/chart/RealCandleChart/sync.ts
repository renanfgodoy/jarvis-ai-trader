export type RealCandleSyncAction = 'unchanged' | 'append' | 'update' | 'reset';

export type RealCandleSyncResult<TCandle> = {
  action: RealCandleSyncAction;
  candles: TCandle[];
};

type ComparableCandle = {
  time: number;
  open: number;
  high: number;
  low: number;
  close: number;
};

export function areRealCandlesEqual(left: ComparableCandle, right: ComparableCandle): boolean {
  return (
    left.time === right.time &&
    left.open === right.open &&
    left.high === right.high &&
    left.low === right.low &&
    left.close === right.close
  );
}

export function classifyRealCandleSync<TCandle extends ComparableCandle>(
  previous: TCandle[],
  next: TCandle[]
): RealCandleSyncAction {
  if (previous.length === 0 && next.length === 0) {
    return 'unchanged';
  }

  if (previous.length === 0 || next.length === 0) {
    return 'reset';
  }

  if (previous.length === next.length && previous.every((candle, index) => areRealCandlesEqual(candle, next[index]))) {
    return 'unchanged';
  }

  if (next.length === previous.length + 1 && previous.every((candle, index) => areRealCandlesEqual(candle, next[index]))) {
    return next[next.length - 1].time > previous[previous.length - 1].time ? 'append' : 'reset';
  }

  if (
    previous.length === next.length &&
    previous.slice(0, -1).every((candle, index) => areRealCandlesEqual(candle, next[index])) &&
    previous[previous.length - 1].time === next[next.length - 1].time
  ) {
    return 'update';
  }

  return 'reset';
}

export function reconcileRealCandleSeries<TCandle extends ComparableCandle>(
  previous: TCandle[],
  next: TCandle[],
  limit?: number
): RealCandleSyncResult<TCandle> {
  const candles = mergeCandlesByTime(previous, next, limit);
  const action = classifyRealCandleSync(previous, candles);
  return {
    action,
    candles: action === 'unchanged' ? previous : candles
  };
}

export function mergeCandlesByTime<TCandle extends ComparableCandle>(
  previous: TCandle[],
  next: TCandle[],
  limit?: number
): TCandle[] {
  if (!previous.length && !next.length) {
    return previous;
  }
  if (!next.length) {
    return trimToLatest(previous, limit);
  }

  const mergedByTime = new Map<number, TCandle>();
  for (const candle of previous) {
    mergedByTime.set(candle.time, candle);
  }
  for (const candle of next) {
    mergedByTime.set(candle.time, candle);
  }

  const merged = Array.from(mergedByTime.values()).sort((left, right) => left.time - right.time);
  return trimToLatest(merged, limit);
}

function trimToLatest<TCandle extends ComparableCandle>(candles: TCandle[], limit?: number): TCandle[] {
  if (typeof limit !== 'number' || limit <= 0 || candles.length <= limit) {
    return candles;
  }
  return candles.slice(candles.length - limit);
}
