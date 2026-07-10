import { useEffect, useMemo, useState } from 'react';

export type AppRoute =
  | '/login'
  | '/operation'
  | '/markets'
  | '/markets/data'
  | '/markets/intelligence'
  | '/connections/polarium'
  | '/diagnostics'
  | '/branding'
  | '/developer/brand-center'
  | '/labs/polarium'
  | '/settings';

const routes: AppRoute[] = ['/login', '/operation', '/markets', '/markets/data', '/markets/intelligence', '/connections/polarium', '/diagnostics', '/branding', '/developer/brand-center', '/labs/polarium', '/settings'];

function normalizePath(pathname: string): AppRoute {
  if (pathname === '/branding') return '/developer/brand-center';
  return routes.includes(pathname as AppRoute) ? (pathname as AppRoute) : '/operation';
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
