type JobStatus = 'queued' | 'running' | 'succeeded' | 'failed';

export interface JobRecord {
  id: string;
  status: JobStatus;
  progress: number;
  createdAt: number;
  updatedAt: number;
  resultUrl?: string;
  error?: string;
  clientToken?: string;
}

// シンプルなインメモリジョブストア（開発用）
const jobs = new Map<string, JobRecord>();
const clientTokenToJobId = new Map<string, string>();

export function getJob(jobId: string): JobRecord | undefined {
  return jobs.get(jobId);
}

export function getJobIdByClientToken(clientToken: string): string | undefined {
  return clientTokenToJobId.get(clientToken);
}

export function createJob(params: { clientToken?: string }): JobRecord {
  const id = `job_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
  const now = Date.now();
  const record: JobRecord = {
    id,
    status: 'queued',
    progress: 0,
    createdAt: now,
    updatedAt: now,
    clientToken: params.clientToken,
  };
  jobs.set(id, record);
  if (params.clientToken) clientTokenToJobId.set(params.clientToken, id);
  return record;
}

export function updateJob(jobId: string, patch: Partial<JobRecord>): JobRecord | undefined {
  const current = jobs.get(jobId);
  if (!current) return undefined;
  const updated: JobRecord = { ...current, ...patch, updatedAt: Date.now() };
  jobs.set(jobId, updated);
  return updated;
}

export function simulateProgress(jobId: string, onComplete: (final: JobRecord) => void) {
  let tick = 0;
  // 1.5秒間隔で進捗更新、最大3分（120 ticks）
  const intervalMs = 1500;
  const maxTicks = Math.floor((3 * 60 * 1000) / intervalMs);
  updateJob(jobId, { status: 'running', progress: 5 });

  const timer = setInterval(() => {
    const job = getJob(jobId);
    if (!job) {
      clearInterval(timer);
      return;
    }
    tick += 1;
    const nextProgress = Math.min(95, (job.progress || 0) + Math.random() * 8 + 2);
    updateJob(jobId, { progress: nextProgress });

    if (tick >= maxTicks) {
      clearInterval(timer);
      // タイムアウト扱い
      const final = updateJob(jobId, { status: 'failed', error: 'Timeout after 3 minutes' });
      if (final) onComplete(final);
    }
  }, intervalMs);

  return () => clearInterval(timer);
}


