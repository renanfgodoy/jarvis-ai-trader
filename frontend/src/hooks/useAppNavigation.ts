import { useEffect, useMemo, useState } from 'react';

export type AppRoute =
  | '/login'
  | '/operation'
  | '/connections/polarium'
  | '/diagnostics'
  | '/branding'
  | '/labs/polarium'
  | '/settings';

const routes: AppRoute[] = ['/login', '/operation', '/connections/polarium', '/diagnostics', '/branding', '/labs/polarium', '/settings'];

function normalizePath(pathname: string): AppRoute {
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
