import MainLayout from './layouts/MainLayout';
import { useAppNavigation } from './hooks/useAppNavigation';
import Branding from './pages/Branding';
import CoreDemo from './pages/CoreDemo';
import Login from './pages/Login';
import Settings from './pages/Settings';
import Vision from './pages/Vision';
import { brand } from './branding/brand';
import { useEffect } from 'react';

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
    <MainLayout activeRoute={route} onNavigate={navigate}>
      {route === '/dashboard' && <Vision />}
      {route === '/vision' && <Vision />}
      {route === '/history' && <Vision />}
      {route === '/risk' && <Vision />}
      {route === '/developer/core-demo' && <CoreDemo />}
      {(route === '/developer/brand-center' || route === '/branding') && <Branding />}
      {route === '/settings' && <Settings />}
    </MainLayout>
  );
}
