import { Component, inject, signal } from '@angular/core';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { ApiService } from '../services/api.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [ReactiveFormsModule, RouterLink],
  template: `
    <div class="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8 bg-[#131314] text-[#E3E3E3] font-sans">
      <div class="w-full max-w-sm space-y-6">
        <!-- Brand Header -->
        <div class="text-center space-y-2">
          <div class="mx-auto w-10 h-10 rounded-md bg-[#D97757] flex items-center justify-center text-white shadow-sm">
            <svg class="w-5 h-5 text-[#FAF8F5]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"/>
            </svg>
          </div>
          <div>
            <h2 class="text-xl font-editorial font-semibold tracking-tight text-[#F1F3F4]">VidGen Studio</h2>
            <p class="text-xs text-[#80868B] mt-1">
              Autonomous Video & DSP Audio Synthesis Platform
            </p>
          </div>
        </div>

        <!-- Login Form Surface -->
        <div class="app-surface rounded-lg p-6 bg-[#1E1F20] border border-[#2E3135] shadow-sm">
          <form [formGroup]="loginForm" (ngSubmit)="onSubmit()" class="space-y-4">
            <div>
              <label for="email" class="block text-xs font-medium text-[#BDC1C6] mb-1.5">Email address</label>
              <input id="email" type="email" formControlName="email" 
                     class="app-input w-full rounded-md py-2 px-3 text-[#F1F3F4] text-sm placeholder-[#5F6368] border border-[#3C4043] bg-[#18191B] focus:border-[#D97757] focus:outline-none focus:ring-1 focus:ring-[#D97757] transition-colors" 
                     placeholder="name@company.com">
            </div>

            <div>
              <label for="password" class="block text-xs font-medium text-[#BDC1C6] mb-1.5">Password</label>
              <input id="password" type="password" formControlName="password" 
                     class="app-input w-full rounded-md py-2 px-3 text-[#F1F3F4] text-sm placeholder-[#5F6368] border border-[#3C4043] bg-[#18191B] focus:border-[#D97757] focus:outline-none focus:ring-1 focus:ring-[#D97757] transition-colors" 
                     placeholder="••••••••">
            </div>

            @if (error()) {
              <div class="rounded-md bg-[#F28B82]/10 border border-[#F28B82]/30 p-2.5 text-center">
                <p class="text-xs font-medium text-[#F28B82]">{{ error() }}</p>
              </div>
            }

            <div class="space-y-2.5 pt-2">
              <button type="submit" [disabled]="isLoading()" 
                      class="btn-primary w-full flex justify-center items-center py-2.5 px-4 rounded-md text-xs font-medium focus-visible:ring-2 focus-visible:ring-[#D97757] disabled:opacity-50">
                @if (isLoading()) {
                  <span class="flex items-center gap-2">
                    <svg class="animate-spin h-3.5 w-3.5 text-[#FAF8F5]" fill="none" viewBox="0 0 24 24">
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Signing in...
                  </span>
                } @else {
                  Sign In
                }
              </button>

              <!-- Guest Showcase Access Button -->
              <button type="button" (click)="bypassLogin()" 
                      class="btn-secondary w-full flex items-center justify-center gap-2 py-2 px-3 rounded-md text-xs font-medium text-[#BDC1C6] bg-[#131314] hover:bg-[#282A2D] border border-[#3C4043] hover:border-[#5F6368] transition-colors focus-visible:ring-1 focus-visible:ring-[#D97757]">
                <svg class="w-3.5 h-3.5 text-[#D97757]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
                </svg>
                <span>Instant Showcase Access</span>
              </button>
            </div>
          </form>

          <div class="mt-5 pt-4 border-t border-[#2E3135] text-center">
            <a routerLink="/register" class="text-xs text-[#80868B] hover:text-[#FAF8F5] transition-colors">
              Don't have an account? <span class="font-medium text-[#D97757] hover:text-[#C16446]">Register</span>
            </a>
          </div>
        </div>

      </div>
    </div>
  `
})
export class LoginComponent {
  private fb: FormBuilder = inject(FormBuilder);
  private api = inject(ApiService);
  private router: Router = inject(Router);

  isLoading = signal(false);
  error = signal('');

  loginForm = this.fb.group({
    email: ['', [Validators.required, Validators.email]],
    password: ['', [Validators.required, Validators.minLength(6)]]
  });

  async onSubmit() {
    if (this.loginForm.invalid) return;

    this.isLoading.set(true);
    this.error.set('');

    try {
      const { email, password } = this.loginForm.value;
      await this.api.login(email!, password!);
      this.router.navigate(['/dashboard']);
    } catch (err: any) {
      this.error.set(err.message || 'Failed to login');
    } finally {
      this.isLoading.set(false);
    }
  }

  async bypassLogin() {
    localStorage.setItem('vidgen_token', 'dev_token');
    const dummyUser = {
      _id: 'guest_reviewer',
      email: 'reviewer@portfolio.ai',
      username: 'Portfolio Reviewer'
    };
    localStorage.setItem('vidgen_user', JSON.stringify(dummyUser));
    window.location.href = '/#/dashboard';
    window.location.reload();
  }
}