import faviconUrl from './assets/friday-trade-favicon.svg';
import logoUrl from './assets/friday-trade-logo.svg';
import symbolUrl from './assets/friday-trade-symbol.svg';

export const brand = {
  name: 'Friday AI Platform',
  shortName: 'Friday',
  tagline: 'Intelligence for better decisions.',
  descriptor: 'Modular AI Platform',
  subtitle: 'Modular AI Platform',
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
    wordmark: 'Friday AI Platform',
    descriptor: 'Intelligence for better decisions.',
    ariaLabel: 'Friday AI Platform logo'
  },
  icon: {
    symbol: 'friday-trade-symbol',
    ariaLabel: 'Friday AI Platform symbol'
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
