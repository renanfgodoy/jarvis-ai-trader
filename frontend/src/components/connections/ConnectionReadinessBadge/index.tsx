import StatusBadge from '../../StatusBadge';
import type { ConnectionReadiness } from '../../../hooks/usePolariumConnection';

export default function ConnectionReadinessBadge({ readiness }: { readiness: ConnectionReadiness }) {
  if (readiness === 'ready') return <StatusBadge status="READY" tone="success" />;
  if (readiness === 'pending') return <StatusBadge status="EM PREPARO" tone="warning" />;
  return <StatusBadge status="BLOQUEADO" tone="danger" />;
}
