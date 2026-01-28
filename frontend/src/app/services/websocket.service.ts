import { Injectable, signal } from '@angular/core';
import { Subject, Observable } from 'rxjs';

export interface VideoProgress {
  type: 'progress' | 'connected' | 'pong';
  video_id: string;
  status?: 'processing' | 'completed' | 'failed';
  progress?: number;
  current_step?: string;
  video_url?: string;
  error_message?: string;
  message?: string;
}

@Injectable({
  providedIn: 'root'
})
export class WebSocketService {
  private socket: WebSocket | null = null;
  private progressSubject = new Subject<VideoProgress>();
  private pingInterval: any = null;
  
  isConnected = signal(false);
  
  /**
   * Connect to video progress WebSocket
   */
  connect(videoId: string): Observable<VideoProgress> {
    // Close existing connection if any
    this.disconnect();
    
    const wsUrl = `ws://localhost:8000/api/v1/videos/${videoId}/ws`;
    this.socket = new WebSocket(wsUrl);
    
    this.socket.onopen = () => {
      console.log('WebSocket connected for video:', videoId);
      this.isConnected.set(true);
    };
    
    this.socket.onmessage = (event) => {
      try {
        const data: VideoProgress = JSON.parse(event.data);
        
        // Handle different message types
        if (data.type === 'connected') {
          console.log('WebSocket connected:', data.message);
          // Send initial ping to keep connection alive
          this.ping();
          // Set up periodic ping
          if (this.pingInterval) clearInterval(this.pingInterval);
          this.pingInterval = setInterval(() => this.ping(), 30000); // Ping every 30 seconds
        } else if (data.type === 'pong') {
          // Connection is alive
        } else if (data.type === 'progress') {
          this.progressSubject.next(data);
          
          // Auto-disconnect on completion or failure
          if (data.status === 'completed' || data.status === 'failed') {
            if (this.pingInterval) clearInterval(this.pingInterval);
            this.disconnect();
          }
        } else {
          // Unknown message type, try to handle as progress
          this.progressSubject.next(data as VideoProgress);
        }
      } catch (e) {
        console.error('Failed to parse WebSocket message:', e, event.data);
      }
    };
    
    this.socket.onerror = (error) => {
      console.error('WebSocket error:', error);
      this.isConnected.set(false);
    };
    
    this.socket.onclose = () => {
      console.log('WebSocket disconnected');
      this.isConnected.set(false);
    };
    
    return this.progressSubject.asObservable();
  }
  
  /**
   * Disconnect from WebSocket
   */
  disconnect(): void {
    if (this.pingInterval) {
      clearInterval(this.pingInterval);
      this.pingInterval = null;
    }
    if (this.socket) {
      this.socket.close();
      this.socket = null;
      this.isConnected.set(false);
    }
  }
  
  /**
   * Send a ping to keep connection alive
   */
  ping(): void {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send('ping');
    }
  }
}
