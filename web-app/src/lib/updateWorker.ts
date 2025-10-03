// シンプルな更新ワーカーのモック実装（Jest用）
let running = false;
let intervalMs = 60_000;
let errors: string[] = [];
let history: Array<{ timestamp: string; success: boolean }> = [];

export function startUpdateWorker() { running = true; }
export function stopUpdateWorker() { running = false; }
export function isUpdateWorkerRunning() { return running; }
export function getUpdateWorkerStatus() {
  return { running, lastUpdate: new Date().toISOString(), nextUpdate: new Date(Date.now() + intervalMs).toISOString() };
}
export function setUpdateWorkerInterval(ms: number) { if (ms <= 0) throw new Error("interval must be positive"); intervalMs = ms; }
export function getUpdateWorkerInterval() { return intervalMs; }
export function pauseUpdateWorker() { running = false; }
export function resumeUpdateWorker() { running = true; }
export function getUpdateWorkerProgress() { return { percentage: 0, current: 0, total: 0 }; }
export function getUpdateWorkerErrors() { return errors; }
export function clearUpdateWorkerErrors() { errors = []; }
export async function retryUpdateWorker(maxAttempts = 5) {
  let attempts = 0; let success = false;
  while (attempts < maxAttempts && !success) { attempts++; success = true; }
  history.push({ timestamp: new Date().toISOString(), success });
  return { success, attempts };
}
export function getUpdateWorkerHistory() { return history; }
export function clearUpdateWorkerHistory() { history = []; }


