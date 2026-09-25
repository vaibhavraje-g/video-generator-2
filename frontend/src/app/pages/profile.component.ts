import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink, Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../services/api.service';
import { ThemeService } from '../services/theme.service';

@Component({
  selector: 'app-profile',
  standalone: true,
  imports: [CommonModule, RouterLink, FormsModule],
  template: `
    <div class="min-h-screen bg-[#131314] text-[#E3E3E3] font-sans">
      
      <!-- Header -->
      <header class="bg-[#1E1F20] border-b border-[#2E3135] sticky top-0 z-20 h-14 flex items-center">
        <div class="max-w-4xl mx-auto px-4 w-full flex items-center justify-between">
          <div class="flex items-center gap-3">
            <a routerLink="/dashboard" 
               aria-label="Back to dashboard"
               class="text-[#80868B] hover:text-[#F1F3F4] p-1 rounded hover:bg-[#282A2D] transition-colors focus-visible:ring-1 focus-visible:ring-[#D97757]">
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
              </svg>
            </a>
            <div>
              <h1 class="text-xs sm:text-sm font-editorial font-semibold text-[#F1F3F4]">System Telemetry & Architecture</h1>
              <p class="text-[10px] font-mono text-[#80868B]">VidGen Studio Production Node</p>
            </div>
          </div>
          
          <button (click)="logout()" class="btn-secondary px-2.5 py-1 text-xs">
            Sign Out
          </button>
        </div>
      </header>

      <!-- Main Content -->
      <main class="max-w-4xl mx-auto px-4 py-6 space-y-5">
        
        <!-- User Identity Panel -->
        <div class="p-4 sm:p-5 rounded-lg bg-[#1E1F20] border border-[#2E3135] space-y-4">
          <div class="flex items-center justify-between pb-3 border-b border-[#2E3135]">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 rounded-md bg-[#282A2D] border border-[#3C4043] flex items-center justify-center text-[#FAF8F5] font-semibold text-sm">
                {{ getUserInitials() }}
              </div>
              <div>
                <h2 class="text-sm font-semibold text-[#F1F3F4]">{{ api.currentUser()?.username || 'Operator' }}</h2>
                <p class="text-xs font-mono text-[#80868B]">{{ api.currentUser()?.email || 'operator@vidgen.internal' }}</p>
              </div>
            </div>

            <span class="px-2.5 py-0.5 rounded-full bg-[#81C995]/10 text-[#81C995] border border-[#81C995]/30 text-[10px] font-mono">
              Authenticated Session
            </span>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
            <div>
              <span class="block text-[11px] font-mono text-[#80868B] mb-1">Operator Identifier</span>
              <input 
                type="text" 
                [value]="api.currentUser()?.username || 'Operator'"
                disabled
                class="app-input w-full p-2 text-xs font-mono text-[#BDC1C6] bg-[#18191B] border border-[#3C4043]">
            </div>
            <div>
              <span class="block text-[11px] font-mono text-[#80868B] mb-1">Email Endpoint</span>
              <input 
                type="email" 
                [value]="api.currentUser()?.email || 'operator@vidgen.internal'"
                disabled
                class="app-input w-full p-2 text-xs font-mono text-[#BDC1C6] bg-[#18191B] border border-[#3C4043]">
            </div>
          </div>
        </div>

        <!-- Studio Metrics Grid -->
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <div class="p-3.5 rounded-lg bg-[#1E1F20] border border-[#2E3135]">
            <span class="text-[10px] font-mono uppercase tracking-wider text-[#80868B] block mb-1">Total Projects</span>
            <p class="text-xl font-mono font-semibold text-[#F1F3F4]">{{ api.projects().length }}</p>
            <span class="text-[10px] text-[#80868B] mt-1 block">Active MongoDB Workspaces</span>
          </div>

          <div class="p-3.5 rounded-lg bg-[#1E1F20] border border-[#2E3135]">
            <span class="text-[10px] font-mono uppercase tracking-wider text-[#80868B] block mb-1">Rendered Videos</span>
            <p class="text-xl font-mono font-semibold text-[#F1F3F4]">{{ getTotalVideos() }}</p>
            <span class="text-[10px] text-[#80868B] mt-1 block">H.264 / AAC 320k Masters</span>
          </div>

          <div class="p-3.5 rounded-lg bg-[#1E1F20] border border-[#2E3135]">
            <span class="text-[10px] font-mono uppercase tracking-wider text-[#80868B] block mb-1">Active Clusters</span>
            <p class="text-xl font-mono font-semibold text-[#81C995]">4 / 4</p>
            <span class="text-[10px] text-[#80868B] mt-1 block">FastAPI, Cloner, FFmpeg, Mongo</span>
          </div>
        </div>

        <!-- Architecture & Microservices Table -->
        <div class="p-4 sm:p-5 rounded-lg bg-[#1E1F20] border border-[#2E3135] space-y-3">
          <h3 class="text-xs font-semibold uppercase tracking-wider text-[#BDC1C6]">
            System Architecture & Service Mapping
          </h3>

          <div class="overflow-x-auto">
            <table class="w-full text-left text-xs font-mono">
              <thead>
                <tr class="border-b border-[#2E3135] text-[10px] text-[#80868B]">
                  <th class="py-2 pr-4 font-semibold">Service</th>
                  <th class="py-2 pr-4 font-semibold">Role / Protocol</th>
                  <th class="py-2 pr-4 font-semibold">Port</th>
                  <th class="py-2 font-semibold">Status</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-[#2E3135] text-[#BDC1C6] text-[11px]">
                <tr>
                  <td class="py-2 pr-4 font-medium text-[#F1F3F4]">FastAPI Core API</td>
                  <td class="py-2 pr-4 text-[#80868B]">REST, SSE Stream, Video Dispatch</td>
                  <td class="py-2 pr-4 text-[#80868B]">:8000</td>
                  <td class="py-2 text-[#81C995]">Online</td>
                </tr>
                <tr>
                  <td class="py-2 pr-4 font-medium text-[#F1F3F4]">Zero-Shot Voice Cloner</td>
                  <td class="py-2 pr-4 text-[#80868B]">Local Neural TTS Cloning Worker</td>
                  <td class="py-2 pr-4 text-[#80868B]">:8004</td>
                  <td class="py-2 text-[#81C995]">Online</td>
                </tr>
                <tr>
                  <td class="py-2 pr-4 font-medium text-[#F1F3F4]">FFmpeg 8.1 Engine</td>
                  <td class="py-2 pr-4 text-[#80868B]">Lissajous Cymatics, Showwaves, H.264 Mux</td>
                  <td class="py-2 pr-4 text-[#80868B]">Native CLI</td>
                  <td class="py-2 text-[#81C995]">Active</td>
                </tr>
                <tr>
                  <td class="py-2 pr-4 font-medium text-[#F1F3F4]">MongoDB Community</td>
                  <td class="py-2 pr-4 text-[#80868B]">Projects, Videos, User Collections</td>
                  <td class="py-2 pr-4 text-[#80868B]">:27017</td>
                  <td class="py-2 text-[#81C995]">Connected</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Project Management & Cleanup -->
        <div class="p-4 sm:p-5 rounded-lg bg-[#1E1F20] border border-[#2E3135] space-y-3">
          <div>
            <h3 class="text-xs font-semibold text-[#BDC1C6]">Workspace Management</h3>
            <p class="text-[11px] text-[#80868B] mt-0.5">Delete workspace projects and generated test media records.</p>
          </div>

          <div class="pt-1">
            <button 
              (click)="deleteAllConversations()"
              [disabled]="isDeleting()"
              class="px-3 py-1.5 rounded-md bg-[#F28B82]/10 hover:bg-[#F28B82]/20 text-[#F28B82] border border-[#F28B82]/30 text-xs font-medium transition-colors disabled:opacity-40">
              @if (isDeleting()) {
                <span>Deleting Projects...</span>
              } @else {
                <span>Delete All Projects</span>
              }
            </button>
          </div>
        </div>

      </main>
    </div>
  `
})
export class ProfileComponent {
  public api = inject(ApiService);
  public themeService = inject(ThemeService);
  private router = inject(Router);

  isDeleting = signal(false);

  getUserInitials(): string {
    const user = this.api.currentUser();
    if (!user) return 'OP';
    return (user.username || user.email || 'OP').substring(0, 2).toUpperCase();
  }

  getTotalVideos(): number {
    return this.api.projects().length;
  }

  async deleteAllConversations() {
    if (!confirm('Are you sure you want to delete all workspace projects? This cannot be undone.')) {
      return;
    }
    
    this.isDeleting.set(true);
    try {
      for (const p of this.api.projects()) {
        await this.api.deleteProject(p._id);
      }
      await this.api.refreshProjects();
    } catch (err) {
      console.error('Error clearing projects:', err);
    } finally {
      this.isDeleting.set(false);
    }
  }

  logout() {
    this.api.logout();
    this.router.navigate(['/login']);
  }
}
