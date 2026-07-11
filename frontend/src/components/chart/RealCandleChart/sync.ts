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
  next: TCandle[]
): RealCandleSyncResult<TCandle> {
  const action = classifyRealCandleSync(previous, next);
  return {
    action,
    candles: action === 'unchanged' ? previous : next
  };
}
