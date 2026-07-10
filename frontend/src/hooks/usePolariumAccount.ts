import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { debugPolariumWsMessage, getPolariumStatus, loginPolarium, logoutPolarium, syncPolarium } from '../services/api';

export function usePolariumAccount() {
  const queryClient = useQueryClient();
  const polarium = useQuery({ queryKey: ['polarium-status'], queryFn: getPolariumStatus, refetchInterval: 5000 });
  const invalidate = () => queryClient.invalidateQueries({ queryKey: ['polarium-status'] });

  const login = useMutation({
    mutationFn: ({ email, password, remember }: { email: string; password: string; remember: boolean }) =>
      loginPolarium({ email, password, remember_session: remember, force_demo: true }),
    onSuccess: invalidate
  });
  const logout = useMutation({ mutationFn: logoutPolarium, onSuccess: invalidate });
  const sync = useMutation({ mutationFn: syncPolarium, onSuccess: invalidate });
  const ingestPayload = useMutation({
    mutationFn: (payloadText: string) => {
      const parsed = JSON.parse(payloadText);
      return debugPolariumWsMessage({ payload: parsed, force_demo: true });
    },
    onSuccess: invalidate
  });

  return {
    polarium,
    login,
    logout,
    sync,
    ingestPayload,
    loading: login.isPending || logout.isPending || sync.isPending || ingestPayload.isPending
  };
}
