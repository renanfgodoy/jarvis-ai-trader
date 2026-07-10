import MainLayout from './layouts/MainLayout';
import { useAppNavigation } from './hooks/useAppNavigation';
import Branding from './pages/Branding';
import PolariumConnections from './pages/connections/PolariumConnections';
import Diagnostics from './pages/Diagnostics';
import Login from './pages/Login';
import AIAnalysis from './pages/AIAnalysis';
import MarketData from './pages/MarketData';
import MarketIntelligence from './pages/MarketIntelligence';
import Markets from './pages/Markets';
import Operation from './pages/Operation';
import PolariumLab from './pages/labs/PolariumLab';
import Replay from './pages/Replay';
import Settings from './pages/Settings';
import { brand } from './branding/brand';
import { useEffect } from 'react';
import { MarketDataProvider } from './market-data/MarketDataContext';

export default function App() {
  const { route, navigate } = useAppNavigation();

  useEffect(() => {
    document.title = `${brand.name} | ${brand.tagline}`;
    let favicon = document.querySelector<HTMLLinkElement>('link[rel="icon"]');
    if (!favicon) {
      favicon = document.createElement('link');
      favicon.rel = 'icon';
      document.head.appendChild(favicon);
    }
    favicon.type = 'image/svg+xml';
    favicon.href = brand.assets.favicon;
  }, []);

  if (route === '/login') {
    return <Login onEnter={() => navigate('/dashboard')} />;
  }

  return (
    <MarketDataProvider>
      <MainLayout activeRoute={route} onNavigate={navigate}>
        {route === '/connections/polarium' && <PolariumConnections />}
        {route === '/dashboard' && <Operation />}
        {route === '/markets' && <Markets />}
        {route === '/markets/data' && <MarketData />}
        {route === '/markets/intelligence' && <MarketIntelligence />}
        {route === '/analysis' && <AIAnalysis />}
        {route === '/replay' && <Replay />}
        {route === '/diagnostics' && <Diagnostics />}
        {(route === '/developer/brand-center' || route === '/branding') && <Branding />}
        {route === '/labs/polarium' && <PolariumLab />}
        {route === '/settings' && <Settings />}
        {route === '/operation' && <Operation />}
      </MainLayout>
    </MarketDataProvider>
  );
}
