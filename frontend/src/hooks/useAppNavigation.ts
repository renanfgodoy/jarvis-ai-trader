import { useEffect, useMemo, useState } from 'react';

export type AppRoute =
  | '/login'
  | '/dashboard'
  | '/operation'
  | '/markets'
  | '/market-chart'
  | '/analysis'
  | '/replay'
  | '/connections/polarium'
  | '/branding'
  | '/developer/brand-center'
  | '/labs/polarium'
  | '/settings';

const routes: AppRoute[] = ['/login', '/dashboard', '/operation', '/markets', '/market-chart', '/analysis', '/replay', '/branding', '/developer/brand-center', '/settings'];

function normalizePath(pathname: string): AppRoute {
  if (pathname === '/branding') return '/developer/brand-center';
  if (pathname === '/markets/data' || pathname === '/markets/intelligence') return '/markets';
  if (pathname === '/diagnostics') return '/dashboard';
  if (pathname === '/connections/polarium' || pathname === '/labs/polarium') return '/dashboard';
  if (pathname === '/' || pathname === '/operation') return '/dashboard';
  return routes.includes(pathname as AppRoute) ? (pathname as AppRoute) : '/dashboard';
}

export function useAppNavigation() {
  const [route, setRoute] = useState<AppRoute>(() => normalizePath(window.location.pathname));

  useEffect(() => {
    const onPopState = () => setRoute(normalizePath(window.location.pathname));
    window.addEventListener('popstate', onPopState);
    return () => window.removeEventListener('popstate', onPopState);
  }, []);

  return useMemo(() => ({
    route,
    navigate: (nextRoute: AppRoute) => {
      if (nextRoute === route) return;
      window.history.pushState({}, '', nextRoute);
      setRoute(nextRoute);
    }
  }), [route]);
}
