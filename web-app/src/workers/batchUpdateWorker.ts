// Web Worker for batch update processing
// This worker handles the heavy computation for batch updates without blocking the UI

interface UpdateTask {
  id: string;
  symbol: string;
  type: "price" | "analysis" | "prediction";
  priority: number;
  data?: any;
}

interface UpdateProgress {
  completed: number;
  total: number;
  current: string;
  percentage: number;
  estimatedTimeRemaining: number;
  errors: string[];
}

interface WorkerMessage {
  type: "START_UPDATE" | "PAUSE_UPDATE" | "RESUME_UPDATE" | "STOP_UPDATE" | "GET_STATUS";
  payload?: {
    tasks: UpdateTask[];
    batchSize?: number;
    delayMs?: number;
  };
}

interface WorkerResponse {
  type: "PROGRESS" | "COMPLETE" | "ERROR" | "STATUS";
  payload?: {
    progress: UpdateProgress;
    result?: any;
    error?: string;
  };
}

class BatchUpdateWorker {
  private tasks: UpdateTask[] = [];
  private currentIndex = 0;
  private isRunning = false;
  private isPaused = false;
  private batchSize = 5;
  private delayMs = 1000;
  private startTime = 0;
  private errors: string[] = [];

  constructor() {
    self.addEventListener("message", this.handleMessage.bind(this));
  }

  private handleMessage(event: MessageEvent<WorkerMessage>) {
    const { type, payload } = event.data;

    switch (type) {
      case "START_UPDATE":
        this.startUpdate(payload?.tasks || [], payload?.batchSize, payload?.delayMs);
        break;
      case "PAUSE_UPDATE":
        this.pauseUpdate();
        break;
      case "RESUME_UPDATE":
        this.resumeUpdate();
        break;
      case "STOP_UPDATE":
        this.stopUpdate();
        break;
      case "GET_STATUS":
        this.sendStatus();
        break;
    }
  }

  private async startUpdate(tasks: UpdateTask[], batchSize = 5, delayMs = 1000) {
    this.tasks = tasks;
    this.currentIndex = 0;
    this.isRunning = true;
    this.isPaused = false;
    this.batchSize = batchSize;
    this.delayMs = delayMs;
    this.startTime = Date.now();
    this.errors = [];

    this.sendProgress();
    await this.processBatch();
  }

  private pauseUpdate() {
    this.isPaused = true;
    this.sendStatus();
  }

  private resumeUpdate() {
    this.isPaused = false;
    this.sendStatus();
    this.processBatch();
  }

  private stopUpdate() {
    this.isRunning = false;
    this.isPaused = false;
    this.sendStatus();
  }

  private async processBatch() {
    while (this.isRunning && !this.isPaused && this.currentIndex < this.tasks.length) {
      const batch = this.tasks.slice(this.currentIndex, this.currentIndex + this.batchSize);
      
      try {
        await this.processBatchItems(batch);
        this.currentIndex += batch.length;
        this.sendProgress();
        
        if (this.currentIndex < this.tasks.length) {
          await this.delay(this.delayMs);
        }
      } catch (error) {
          this.errors.push(`Batch processing error: ${error}`);
        }
    }

    if (this.currentIndex >= this.tasks.length && this.isRunning) {
      this.isRunning = false;
      this.sendComplete();
    }
  }

  private async processBatchItems(batch: UpdateTask[]) {
    const promises = batch.map(task => this.processTask(task));
    await Promise.allSettled(promises);
  }

  private async processTask(task: UpdateTask): Promise<void> {
    try {
      // Simulate different types of processing
      switch (task.type) {
        case "price":
          await this.updatePrice(task);
          break;
        case "analysis":
          await this.updateAnalysis(task);
          break;
        case "prediction":
          await this.updatePrediction(task);
          break;
      }
    } catch (error) {
      this.errors.push(`${task.symbol}: ${error}`);
    }
  }

  private async updatePrice(task: UpdateTask): Promise<void> {
    // Simulate price update API call
    await this.delay(Math.random() * 500 + 200);
    
    // Simulate occasional errors
    if (Math.random() < 0.05) {
      throw new Error("Price update failed");
    }
  }

  private async updateAnalysis(task: UpdateTask): Promise<void> {
    // Simulate analysis processing
    await this.delay(Math.random() * 1000 + 500);
    
    // Simulate occasional errors
    if (Math.random() < 0.03) {
      throw new Error("Analysis failed");
    }
  }

  private async updatePrediction(task: UpdateTask): Promise<void> {
    // Simulate prediction processing
    await this.delay(Math.random() * 800 + 300);
    
    // Simulate occasional errors
    if (Math.random() < 0.02) {
      throw new Error("Prediction failed");
    }
  }

  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  private sendProgress() {
    const progress: UpdateProgress = {
      completed: this.currentIndex,
      total: this.tasks.length,
      current: this.tasks[this.currentIndex]?.symbol || "",
      percentage: Math.round((this.currentIndex / this.tasks.length) * 100),
      estimatedTimeRemaining: this.calculateEstimatedTime(),
      errors: [...this.errors],
    };

    const response: WorkerResponse = {
      type: "PROGRESS",
      payload: { progress },
    };

    self.postMessage(response);
  }

  private sendComplete() {
    const progress: UpdateProgress = {
      completed: this.tasks.length,
      total: this.tasks.length,
      current: "",
      percentage: 100,
      estimatedTimeRemaining: 0,
      errors: [...this.errors],
    };

    const response: WorkerResponse = {
      type: "COMPLETE",
      payload: { progress },
    };

    self.postMessage(response);
  }

  private sendStatus() {
    const progress: UpdateProgress = {
      completed: this.currentIndex,
      total: this.tasks.length,
      current: this.tasks[this.currentIndex]?.symbol || "",
      percentage: Math.round((this.currentIndex / this.tasks.length) * 100),
      estimatedTimeRemaining: this.calculateEstimatedTime(),
      errors: [...this.errors],
    };

    const response: WorkerResponse = {
      type: "STATUS",
      payload: { progress },
    };

    self.postMessage(response);
  }

  private calculateEstimatedTime(): number {
    if (this.currentIndex === 0) return 0;
    
    const elapsed = Date.now() - this.startTime;
    const rate = this.currentIndex / elapsed;
    const remaining = this.tasks.length - this.currentIndex;
    
    return Math.round(remaining / rate);
  }
}

// Initialize the worker
new BatchUpdateWorker();
