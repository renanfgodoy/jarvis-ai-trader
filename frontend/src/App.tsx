import MainLayout from './layouts/MainLayout';
import { useAppNavigation } from './hooks/useAppNavigation';
import Branding from './pages/Branding';
import PolariumConnections from './pages/connections/PolariumConnections';
import Diagnostics from './pages/Diagnostics';
import Login from './pages/Login';
import Operation from './pages/Operation';
import PolariumLab from './pages/labs/PolariumLab';
import Settings from './pages/Settings';

export default function App() {
  const { route, navigate } = useAppNavigation();

  if (route === '/login') {
    return <Login onEnter={() => navigate('/operation')} />;
  }

  return (
    <MainLayout activeRoute={route} onNavigate={navigate}>
      {route === '/connections/polarium' && <PolariumConnections />}
      {route === '/diagnostics' && <Diagnostics />}
      {route === '/branding' && <Branding />}
      {route === '/labs/polarium' && <PolariumLab />}
      {route === '/settings' && <Settings />}
      {route === '/operation' && <Operation />}
    </MainLayout>
  );
}
