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
    <div class="min-h-screen bg-gray-50 dark:bg-slate-950 transition-colors">
      <!-- Header -->
      <header class="bg-white dark:bg-slate-900 border-b border-gray-200 dark:border-slate-800 transition-colors">
        <div class="max-w-2xl mx-auto px-4 py-4 flex items-center justify-between">
          <div class="flex items-center gap-3">
            <a routerLink="/dashboard" class="text-gray-500 dark:text-slate-400 hover:text-gray-700 dark:hover:text-white transition-colors">
              <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
              </svg>
            </a>
            <h1 class="text-xl font-bold text-gray-900 dark:text-white">Profile</h1>
          </div>
          <button 
            (click)="themeService.toggle()" 
            class="p-2 text-gray-500 dark:text-slate-400 hover:text-gray-700 dark:hover:text-white transition-colors rounded-lg hover:bg-gray-100 dark:hover:bg-slate-800">
            @if (themeService.isDark()) {
              <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
              </svg>
            } @else {
              <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
              </svg>
            }
          </button>
        </div>
      </header>

      <!-- Main Content -->
      <main class="max-w-2xl mx-auto px-4 py-8">
        <!-- Profile Card -->
        <div class="bg-white dark:bg-slate-900 rounded-xl border border-gray-200 dark:border-slate-800 p-6 mb-6 transition-colors">
          <div class="flex items-center gap-4 mb-6">
            <div class="w-16 h-16 rounded-full bg-gradient-to-br from-amber-500 to-amber-600 flex items-center justify-center text-white text-2xl font-bold shadow-lg">
              {{ getUserInitials() }}
            </div>
            <div>
              <h2 class="text-xl font-semibold text-gray-900 dark:text-white">{{ api.currentUser()?.username || 'User' }}</h2>
              <p class="text-gray-500 dark:text-slate-400">{{ api.currentUser()?.email || 'No email' }}</p>
            </div>
          </div>

          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-slate-300 mb-1">Username</label>
              <input 
                type="text" 
                [value]="api.currentUser()?.username || ''"
                disabled
                class="w-full px-4 py-2 bg-gray-100 dark:bg-slate-800 border border-gray-200 dark:border-slate-700 rounded-lg text-gray-900 dark:text-white disabled:opacity-50">
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-slate-300 mb-1">Email</label>
              <input 
                type="email" 
                [value]="api.currentUser()?.email || ''"
                disabled
                class="w-full px-4 py-2 bg-gray-100 dark:bg-slate-800 border border-gray-200 dark:border-slate-700 rounded-lg text-gray-900 dark:text-white disabled:opacity-50">
            </div>
          </div>
        </div>

        <!-- Stats Card -->
        <div class="bg-white dark:bg-slate-900 rounded-xl border border-gray-200 dark:border-slate-800 p-6 mb-6 transition-colors">
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Statistics</h3>
          <div class="grid grid-cols-2 gap-4">
            <div class="bg-gray-50 dark:bg-slate-800 rounded-lg p-4 text-center">
              <p class="text-2xl font-bold text-amber-600">{{ api.projects().length }}</p>
              <p class="text-sm text-gray-500 dark:text-slate-400">Projects</p>
            </div>
            <div class="bg-gray-50 dark:bg-slate-800 rounded-lg p-4 text-center">
              <p class="text-2xl font-bold text-amber-600">{{ getTotalVideos() }}</p>
              <p class="text-sm text-gray-500 dark:text-slate-400">Videos</p>
            </div>
          </div>
        </div>

        <!-- Danger Zone -->
        <div class="bg-white dark:bg-slate-900 rounded-xl border border-red-200 dark:border-red-900/30 p-6 transition-colors">
          <h3 class="text-lg font-semibold text-red-600 dark:text-red-400 mb-2">Danger Zone</h3>
          <p class="text-sm text-gray-500 dark:text-slate-400 mb-4">These actions are irreversible. Please be certain.</p>
          
          <div class="space-y-3">
            <button 
              (click)="deleteAllConversations()"
              [disabled]="isDeleting()"
              class="w-full flex items-center justify-center gap-2 px-4 py-3 bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 rounded-lg hover:bg-red-100 dark:hover:bg-red-900/30 transition-colors disabled:opacity-50">
              @if (isDeleting()) {
                <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-red-600"></div>
                <span>Deleting...</span>
              } @else {
                <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
                <span>Delete All Conversations</span>
              }
            </button>

            <button 
              (click)="logout()"
              class="w-full flex items-center justify-center gap-2 px-4 py-3 bg-gray-100 dark:bg-slate-800 text-gray-700 dark:text-slate-300 rounded-lg hover:bg-gray-200 dark:hover:bg-slate-700 transition-colors">
              <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
              </svg>
              <span>Sign Out</span>
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
    if (!user) return 'U';
    const name = user.username || user.email || 'User';
    return name.charAt(0).toUpperCase();
  }

  getTotalVideos(): number {
    // Sum up video counts from all projects
    return this.api.projects().reduce((sum, p) => sum + (p.video_count || 0), 0);
  }

  async deleteAllConversations() {
    if (!confirm('Are you sure you want to delete ALL conversations? This action cannot be undone.')) {
      return;
    }

    this.isDeleting.set(true);
    try {
      // Delete all projects one by one
      const projects = this.api.projects();
      for (const project of projects) {
        await this.api.deleteProject(project._id);
      }
      await this.api.refreshProjects();
      alert('All conversations deleted successfully.');
    } catch (err) {
      console.error('Failed to delete conversations:', err);
      alert('Failed to delete some conversations. Please try again.');
    } finally {
      this.isDeleting.set(false);
    }
  }

  logout() {
    this.api.logout();
    this.router.navigate(['/login']);
  }
}
