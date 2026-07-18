import { api } from './api';
import type { CoreDemoExecutionRequest, CoreDemoResponse } from '../types/coreDemo';

export async function executeCoreDemo(request: CoreDemoExecutionRequest, signal?: AbortSignal): Promise<CoreDemoResponse> {
  const requestId = crypto.randomUUID();
  const { data } = await api.post<CoreDemoResponse>(
    '/core/demo/execute',
    {
      ...request,
      request_id: requestId,
      provider: 'mock',
      metadata: {
        ...request.metadata,
        request_source: 'friday_core_demo_frontend'
      }
    },
    { signal }
  );
  return data;
}
