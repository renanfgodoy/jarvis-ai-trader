import type { CoreDemoResponse, ExecutionHistoryItem, PipelineStep } from '../../types/coreDemo';
import DebugPanel from './DebugPanel';
import ExecutionError from './ExecutionError';
import ExecutionHistory from './ExecutionHistory';
import PipelineViewer from './PipelineViewer';
import ResponseCard from './ResponseCard';

function requestIdFrom(response: CoreDemoResponse | null): string | null {
  if (!response) return null;
  return 'request_id' in response ? response.request_id : response.execution.execution.request_id;
}

export default function ExecutionPanel({
  response,
  error,
  pipeline,
  history
}: {
  response: CoreDemoResponse | null;
  error: string | null;
  pipeline: PipelineStep[];
  history: ExecutionHistoryItem[];
}) {
  return (
    <div className="grid gap-4 xl:grid-cols-[minmax(0,1.2fr)_minmax(320px,0.8fr)]">
      <div className="space-y-4">
        <ResponseCard response={response} />
        <ExecutionError message={error} requestId={requestIdFrom(response)} />
      </div>
      <div className="space-y-4">
        <PipelineViewer steps={pipeline} />
        <ExecutionHistory history={history} />
        <DebugPanel response={response} />
      </div>
    </div>
  );
}
