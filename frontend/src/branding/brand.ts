import faviconUrl from './assets/friday-trade-favicon.svg';
import logoUrl from './assets/friday-trade-logo.svg';
import symbolUrl from './assets/friday-trade-symbol.svg';

export const brand = {
  name: 'Friday Trade',
  shortName: 'Friday',
  tagline: 'Trade Smarter.',
  descriptor: 'Professional AI Trading Platform',
  subtitle: 'Professional AI Trading Platform',
  version: '0.24.0',
  environment: 'Desenvolvimento',
  operator: 'Renan Godoy',
  operatorName: 'Renan Godoy',
  assets: {
    logo: logoUrl,
    symbol: symbolUrl,
    favicon: faviconUrl
  },
  logo: {
    wordmark: 'Friday Trade',
    descriptor: 'Trade Smarter.',
    ariaLabel: 'Friday Trade logo'
  },
  icon: {
    symbol: 'friday-trade-symbol',
    ariaLabel: 'Friday Trade symbol'
  },
  colors: {
    background: '#05070D',
    surface: '#08111F',
    surfaceElevated: '#0D1726',
    primary: '#22D3EE',
    primaryStrong: '#0EA5E9',
    text: '#FFFFFF',
    muted: '#94A3B8',
    success: '#34D399',
    warning: '#F59E0B',
    danger: '#F87171'
  },
  typography: {
    display: 'Inter, ui-sans-serif, system-ui',
    body: 'Inter, ui-sans-serif, system-ui',
    mono: 'JetBrains Mono, ui-monospace, SFMono-Regular'
  }
} as const;

export type Brand = typeof brand;
