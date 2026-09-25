import { Component, inject, input, output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink, Router } from '@angular/router';
import { ApiService } from '../../services/api.service';
import { ThemeService } from '../../services/theme.service';
import { SseService } from '../../services/sse.service';

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [CommonModule, RouterLink],
  template: `
    <!-- Mobile Backdrop -->
    @if (isOpen()) {
      <div 
        (click)="closeSidebar()"
        (keydown.escape)="closeSidebar()"
        tabindex="0"
        aria-label="Close sidebar backdrop"
        class="fixed inset-0 bg-black/60 z-40 md:hidden transition-opacity"></div>
    }

    <!-- Sidebar Aside -->
    <aside 
      [class]="isOpen() ? 'translate-x-0' : '-translate-x-full md:translate-x-0'"
      aria-label="Studio Workspace Navigation"
      class="fixed md:relative z-50 w-64 h-full flex flex-col bg-[#18191B] border-r border-[#2E3135] transition-transform duration-200 ease-out select-none shadow-lg md:shadow-none">
      
      <!-- Brand & Studio Title -->
      <div class="h-14 px-4 border-b border-[#2E3135] flex items-center justify-between">
        <a routerLink="/dashboard" class="flex items-center gap-2.5 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-[#D97757] rounded p-1">
          <div class="w-7 h-7 rounded-md bg-[#D97757] flex items-center justify-center text-white flex-shrink-0 shadow-sm">
            <svg class="w-4 h-4 text-[#FAF8F5]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
            </svg>
          </div>
          <div>
            <span class="font-editorial font-semibold text-sm text-[#F1F3F4] block leading-tight">VidGen Studio</span>
            <span class="text-[10px] text-[#80868B] font-mono block">Video & Audio DSP</span>
          </div>
        </a>

        <!-- Mobile Close Button -->
        <button 
          (click)="closeSidebar()"
          aria-label="Close sidebar navigation"
          class="md:hidden text-[#80868B] hover:text-[#F1F3F4] p-1 rounded hover:bg-[#282A2D] transition-colors focus-visible:ring-2 focus-visible:ring-[#D97757]">
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Primary Action: New Project -->
      <div class="p-3 border-b border-[#2E3135]">
        <a routerLink="/dashboard" 
           (click)="closeSidebar()"
           class="btn-primary flex items-center justify-center gap-1.5 w-full py-2 px-3 text-xs text-center focus-visible:ring-2 focus-visible:ring-[#D97757]">
          <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          <span>New Project</span>
        </a>
      </div>

      <!-- Navigation & Workspace Projects -->
      <nav class="flex-1 overflow-y-auto p-3 space-y-4" aria-label="Workspace projects">
        
        <!-- Primary Navigation -->
        <div class="space-y-0.5">
          <a routerLink="/dashboard" 
             (click)="closeSidebar()"
             class="flex items-center gap-2 px-2.5 py-1.5 rounded-md text-xs font-medium text-[#BDC1C6] hover:text-[#F1F3F4] hover:bg-[#282A2D] transition-colors focus-visible:ring-2 focus-visible:ring-[#D97757]">
            <svg class="w-4 h-4 text-[#80868B]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/>
            </svg>
            <span>Studio Workspace</span>
          </a>

          <a routerLink="/profile" 
             (click)="closeSidebar()"
             class="flex items-center gap-2 px-2.5 py-1.5 rounded-md text-xs font-medium text-[#BDC1C6] hover:text-[#F1F3F4] hover:bg-[#282A2D] transition-colors focus-visible:ring-2 focus-visible:ring-[#D97757]">
            <svg class="w-4 h-4 text-[#80868B]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            <span>System Telemetry</span>
          </a>
        </div>

        <!-- Project History Section -->
        <div class="pt-2 border-t border-[#2E3135]">
          <div class="flex items-center justify-between px-2 mb-1.5">
            <span class="text-[10px] font-semibold uppercase tracking-wider text-[#80868B]">
              Workspace Projects
            </span>
            <span class="text-[10px] px-1.5 py-0.5 rounded-full bg-[#282A2D] text-[#BDC1C6] border border-[#3C4043] font-mono">
              {{ api.projects().length }}
            </span>
          </div>

          <div class="space-y-0.5">
            @for (p of api.projects(); track p._id) {
              <a [routerLink]="['/projects', p._id]" 
                 (click)="closeSidebar()"
                 [class.nav-item-active]="activeProjectId() === p._id"
                 [class.text-[#BDC1C6]]="activeProjectId() !== p._id"
                 class="flex items-center gap-2 px-2.5 py-1.5 text-xs font-medium hover:text-[#F1F3F4] hover:bg-[#282A2D] rounded-md transition-colors truncate group focus-visible:ring-2 focus-visible:ring-[#D97757]">
                <span class="w-1.5 h-1.5 rounded-full flex-shrink-0"
                      [class.bg-[#D97757]]="activeProjectId() === p._id"
                      [class.bg-[#5F6368]]="activeProjectId() !== p._id"></span>
                <span class="truncate flex-1">{{ p.name }}</span>
              </a>
            } @empty {
              <div class="p-3 text-center text-xs text-[#80868B] border border-dashed border-[#2E3135] rounded-md">
                No active projects.
              </div>
            }
          </div>
        </div>

      </nav>

      <!-- System Telemetry Status -->
      <div class="p-3 border-t border-[#2E3135] bg-[#131314] space-y-2.5">
        
        <div class="space-y-1.5 text-[11px] font-mono">
          <div class="text-[10px] font-semibold text-[#80868B] uppercase tracking-wider pb-1 border-b border-[#2E3135] flex items-center justify-between">
            <span>Cluster Status</span>
            <span class="text-[#81C995]">Online</span>
          </div>
          
          <div class="flex items-center justify-between text-[10px]">
            <span class="text-[#80868B]">SSE Stream:</span>
            <span class="flex items-center gap-1 font-medium" 
                  [class.text-[#81C995]]="sseService.isConnected()" 
                  [class.text-[#80868B]]="!sseService.isConnected()">
              <span class="w-1.5 h-1.5 rounded-full" 
                    [class.bg-[#81C995]]="sseService.isConnected()" 
                    [class.bg-[#80868B]]="!sseService.isConnected()"></span>
              {{ sseService.isConnected() ? 'Live' : 'Standby' }}
            </span>
          </div>

          <div class="flex items-center justify-between text-[10px]">
            <span class="text-[#80868B]">Voice Cloner:</span>
            <span class="text-[#81C995] font-medium">:8004 Active</span>
          </div>

          <div class="flex items-center justify-between text-[10px]">
            <span class="text-[#80868B]">Audio/Video DSP:</span>
            <span class="text-[#BDC1C6] font-medium">FFmpeg 8.1</span>
          </div>
        </div>

        <!-- User Profile Pill & Sign Out -->
        <div class="flex items-center justify-between pt-1.5 border-t border-[#2E3135]">
          <div class="flex items-center gap-2 truncate">
            <div class="w-6 h-6 rounded bg-[#282A2D] text-[#E3E3E3] flex items-center justify-center font-semibold text-xs border border-[#3C4043]">
              {{ getUserInitial() }}
            </div>
            <div class="truncate">
              <span class="text-xs font-medium text-[#E3E3E3] block truncate">{{ api.currentUser()?.username || 'Operator' }}</span>
            </div>
          </div>

          <button 
            (click)="logout()"
            title="Sign out"
            aria-label="Sign out"
            class="text-[#80868B] hover:text-[#F1F3F4] p-1 rounded hover:bg-[#282A2D] transition-colors focus-visible:ring-1 focus-visible:ring-[#D97757]">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
            </svg>
          </button>
        </div>

      </div>

    </aside>
  `
})
export class SidebarComponent {
  public api = inject(ApiService);
  public themeService = inject(ThemeService);
  public sseService = inject(SseService);
  private router = inject(Router);

  isOpen = input<boolean>(false);
  activeProjectId = input<string | null>(null);
  sidebarClose = output<void>();

  closeSidebar() {
    this.sidebarClose.emit();
  }

  getUserInitial(): string {
    const user = this.api.currentUser();
    if (!user) return 'O';
    return (user.username || user.email || 'O').charAt(0).toUpperCase();
  }

  logout() {
    this.api.logout();
    this.router.navigate(['/login']);
  }
}
