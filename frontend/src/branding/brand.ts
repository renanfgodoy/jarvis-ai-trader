export const brand = {
  name: 'J.A.R.V.I.S AI Trader',
  shortName: 'J.A.R.V.I.S',
  subtitle: 'Professional AI Trading Platform',
  descriptor: 'AI Trader',
  version: '0.24.0',
  environment: 'Desenvolvimento',
  operatorName: 'Renan',
  logo: {
    initials: 'JT',
    wordmark: 'J.A.R.V.I.S',
    descriptor: 'AI TRADER',
    ariaLabel: 'J.A.R.V.I.S AI Trader temporary logo'
  },
  icon: {
    symbol: 'signal-core',
    ariaLabel: 'Trading signal core icon'
  },
  colors: {
    background: '#05051f',
    surface: '#07082a',
    surfaceElevated: '#0b0b3a',
    primary: '#22d3ee',
    primaryStrong: '#0ea5e9',
    text: '#ffffff',
    muted: '#94a3b8',
    success: '#34d399',
    warning: '#f59e0b',
    danger: '#f87171'
  },
  nameSuggestions: [
    {
      name: 'Aionex Trade',
      concept:
        'Une IA, automação e execução profissional em um nome curto. Funciona bem em português e inglês por ter som tecnológico e leitura direta.'
    },
    {
      name: 'Quantora',
      concept:
        'Evoca análise quantitativa e tomada de decisão orientada por dados. O final aberto deixa espaço para a plataforma crescer além do trading inicial.'
    },
    {
      name: 'Nexora AI',
      concept:
        'Sugere próxima geração, orquestração e inteligência aplicada. É simples de pronunciar e pode sustentar uma marca premium sem prender o produto a um broker.'
    },
    {
      name: 'Vektor Trade',
      concept:
        'Remete a direção, precisão e movimento de mercado. O nome combina com scanners, sinais e módulos de decisão com leitura técnica.'
    },
    {
      name: 'Lumina Quant',
      concept:
        'Comunica clareza sobre dados complexos e análise algorítmica. Tem tom sofisticado e funciona para uma plataforma profissional com IA explicável.'
    },
    {
      name: 'Orionex',
      concept:
        'Nome curto, memorável e com sensação de infraestrutura robusta. Pode representar uma plataforma de automação financeira com visão de longo prazo.'
    },
    {
      name: 'TradePilot AI',
      concept:
        'Transmite assistência inteligente sem prometer execução autônoma irrestrita. É claro para usuários novos e ainda comporta controles de risco e replay.'
    },
    {
      name: 'Axion Markets',
      concept:
        'Passa ideia de ação, motor e arquitetura profissional. O nome abre espaço para múltiplos mercados, provedores e produtos derivados.'
    }
  ]
} as const;

export type Brand = typeof brand;
export type BrandNameSuggestion = (typeof brand.nameSuggestions)[number];
