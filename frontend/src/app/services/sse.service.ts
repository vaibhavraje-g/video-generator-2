import { Injectable, signal } from '@angular/core';
import { Subject, Observable } from 'rxjs';

export interface VideoProgressEvent {
  type?: 'progress' | 'connected' | 'complete' | 'error';
  video_id: string;
  status?: 'processing' | 'completed' | 'failed';
  progress?: number;
  current_step?: string;
  video_url?: string;
  error_message?: string;
  metadata?: Record<string, any>;
}

@Injectable({
  providedIn: 'root'
})
export class SseService {
  private eventSource: EventSource | null = null;
  private progressSubject = new Subject<VideoProgressEvent>();
  
  isConnected = signal(false);
  
  /**
   * Connect to Server-Sent Events stream for video progress updates
   */
  connect(videoId: string): Observable<VideoProgressEvent> {
    this.disconnect();
    
    const streamUrl = `http://localhost:8000/api/v1/videos/${videoId}/stream`;
    this.eventSource = new EventSource(streamUrl);
    
    this.eventSource.onopen = () => {
      console.log('[SSE] Stream connected for video:', videoId);
      this.isConnected.set(true);
    };
    
    // Listen for custom "progress" events
    this.eventSource.addEventListener('progress', (event: MessageEvent) => {
      try {
        const data: VideoProgressEvent = JSON.parse(event.data);
        this.progressSubject.next({ ...data, type: 'progress' });
      } catch (e) {
        console.error('Failed to parse SSE progress data:', e, event.data);
      }
    });

    // Listen for "complete" event
    this.eventSource.addEventListener('complete', (event: MessageEvent) => {
      try {
        const data: VideoProgressEvent = JSON.parse(event.data);
        this.progressSubject.next({ ...data, type: 'complete', status: 'completed', progress: 100 });
        this.disconnect();
      } catch (e) {
        console.error('Failed to parse SSE complete data:', e);
      }
    });

    // Listen for "error" or failure event
    this.eventSource.addEventListener('error', (event: MessageEvent | Event) => {
      if (event instanceof MessageEvent) {
        try {
          const data: VideoProgressEvent = JSON.parse(event.data);
          this.progressSubject.next({ ...data, type: 'error', status: 'failed' });
        } catch {
          // generic error
        }
      }
      this.isConnected.set(false);
    });

    // Default message handler
    this.eventSource.onmessage = (event: MessageEvent) => {
      try {
        const data: VideoProgressEvent = JSON.parse(event.data);
        this.progressSubject.next(data);
      } catch (e) {
        // Heartbeats or unparsed messages
      }
    };
    
    return this.progressSubject.asObservable();
  }
  
  /**
   * Disconnect from SSE stream
   */
  disconnect(): void {
    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
      this.isConnected.set(false);
      console.log('[SSE] Stream closed');
    }
  }
}
