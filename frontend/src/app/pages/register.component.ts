import { Component, inject, signal } from '@angular/core';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { ApiService } from '../services/api.service';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [ReactiveFormsModule, RouterLink],
  template: `
    <div class="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8 bg-[#131314] text-[#E3E3E3] font-sans">
      <div class="w-full max-w-sm space-y-6">
        <!-- Brand Header -->
        <div class="text-center space-y-2">
          <div class="mx-auto w-10 h-10 rounded-md bg-[#D97757] flex items-center justify-center text-white shadow-sm">
            <svg class="w-5 h-5 text-[#FAF8F5]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z"/>
            </svg>
          </div>
          <div>
            <h2 class="text-xl font-editorial font-semibold tracking-tight text-[#F1F3F4]">Create Account</h2>
            <p class="text-xs text-[#80868B] mt-1">
              Join VidGen AI Studio
            </p>
          </div>
        </div>

        <!-- Register Surface -->
        <div class="app-surface rounded-lg p-6 bg-[#1E1F20] border border-[#2E3135] shadow-sm">
          <form [formGroup]="registerForm" (ngSubmit)="onSubmit()" class="space-y-4">
            <div>
              <label for="username" class="block text-xs font-medium text-[#BDC1C6] mb-1.5">Username</label>
              <input id="username" type="text" formControlName="username" 
                     class="app-input w-full rounded-md py-2 px-3 text-[#F1F3F4] text-sm placeholder-[#5F6368] border border-[#3C4043] bg-[#18191B] focus:border-[#D97757] focus:outline-none focus:ring-1 focus:ring-[#D97757] transition-colors" 
                     placeholder="johndoe">
            </div>

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
                     placeholder="Minimum 6 characters">
            </div>

            @if (error()) {
              <div class="rounded-md bg-[#F28B82]/10 border border-[#F28B82]/30 p-2.5 text-center">
                <p class="text-xs font-medium text-[#F28B82]">{{ error() }}</p>
              </div>
            }

            <div class="pt-2">
              <button type="submit" [disabled]="isLoading() || registerForm.invalid" 
                      class="btn-primary w-full flex justify-center items-center py-2.5 px-4 rounded-md text-xs font-medium focus-visible:ring-2 focus-visible:ring-[#D97757] disabled:opacity-50">
                @if (isLoading()) {
                  <span class="flex items-center gap-2">
                    <svg class="animate-spin h-3.5 w-3.5 text-[#FAF8F5]" fill="none" viewBox="0 0 24 24">
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Creating account...
                  </span>
                } @else {
                  Create Account
                }
              </button>
            </div>
          </form>

          <div class="mt-5 pt-4 border-t border-[#2E3135] text-center">
            <a routerLink="/login" class="text-xs text-[#80868B] hover:text-[#FAF8F5] transition-colors">
              Already have an account? <span class="font-medium text-[#D97757] hover:text-[#C16446]">Sign in</span>
            </a>
          </div>
        </div>

      </div>
    </div>
  `
})
export class RegisterComponent {
  private fb: FormBuilder = inject(FormBuilder);
  private api = inject(ApiService);
  private router: Router = inject(Router);

  isLoading = signal(false);
  error = signal('');

  registerForm = this.fb.group({
    username: ['', Validators.required],
    email: ['', [Validators.required, Validators.email]],
    password: ['', [Validators.required, Validators.minLength(6)]]
  });

  async onSubmit() {
    if (this.registerForm.invalid) return;

    this.isLoading.set(true);
    this.error.set('');

    try {
      const { email, username, password } = this.registerForm.value;
      await this.api.register(email!, username!, password!);
      this.router.navigate(['/dashboard']);
    } catch (err: any) {
      this.error.set(err.message || 'Registration failed');
    } finally {
      this.isLoading.set(false);
    }
  }
}