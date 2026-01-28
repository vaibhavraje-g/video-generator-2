import { Component, inject, signal, OnInit, OnDestroy, ViewChild, ElementRef, AfterViewChecked } from '@angular/core';
import { CommonModule, DatePipe } from '@angular/common';
import { ActivatedRoute, RouterLink, Router } from '@angular/router';
import { FormBuilder, Validators, ReactiveFormsModule } from '@angular/forms';
import { ApiService, Project, Video } from '../services/api.service';
import { ThemeService } from '../services/theme.service';
import { WebSocketService, VideoProgress } from '../services/websocket.service';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-project-detail',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterLink, DatePipe],
  template: `
    <div class="flex h-screen bg-white dark:bg-slate-950 overflow-hidden transition-colors duration-300">
      <!-- Sidebar (Collapsible) -->
      <aside 
        [class]="sidebarOpen() ? 'translate-x-0' : '-translate-x-full md:translate-x-0'"
        class="fixed md:relative z-40 w-64 h-full flex-col bg-gray-50 dark:bg-slate-900 border-r border-gray-200 dark:border-slate-800 transition-all duration-300 flex">
        <div class="p-4 border-b border-gray-200 dark:border-slate-800 flex items-center justify-between">
          <div class="flex items-center gap-2">
            <div class="w-8 h-8 rounded-lg bg-amber-600 flex items-center justify-center text-white font-bold shadow-sm">V</div>
            <span class="font-bold text-gray-900 dark:text-white">VidGen AI</span>
          </div>
          <!-- Close button (mobile) -->
          <button (click)="sidebarOpen.set(false)" class="md:hidden text-gray-500 hover:text-gray-700 dark:text-slate-400 dark:hover:text-white">
            <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        <div class="p-3">
          <a routerLink="/dashboard" class="flex items-center gap-2 w-full px-3 py-2 text-sm text-gray-700 dark:text-slate-300 hover:bg-gray-100 dark:hover:bg-slate-800 rounded-lg transition-colors border border-transparent hover:border-gray-200 dark:hover:border-slate-700/50">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            New Project
          </a>
        </div>

        <div class="flex-1 overflow-y-auto px-3 py-2 space-y-1">
          <h3 class="px-3 text-xs font-medium text-gray-500 dark:text-slate-500 uppercase tracking-wider mb-2">History</h3>
          @for (p of api.projects(); track p._id) {
            <a [routerLink]="['/projects', p._id]" 
               (click)="sidebarOpen.set(false)"
               [class.bg-gray-200]="p._id === project()?._id"
               [class.dark:bg-slate-800]="p._id === project()?._id"
               [class.text-gray-900]="p._id === project()?._id"
               [class.dark:text-white]="p._id === project()?._id"
               class="flex items-center gap-2 px-3 py-2 text-sm text-gray-600 dark:text-slate-400 hover:text-gray-900 dark:hover:text-white hover:bg-gray-200 dark:hover:bg-slate-800 rounded-lg transition-colors truncate group">
              <svg class="w-4 h-4 text-gray-400 dark:text-slate-600 group-hover:text-gray-600 dark:group-hover:text-slate-500 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
              </svg>
              <span class="truncate">{{ p.name }}</span>
            </a>
          }
        </div>

        <div class="p-4 border-t border-gray-200 dark:border-slate-800 space-y-2">
            <!-- Theme Toggle -->
           <button (click)="themeService.toggle()" class="flex items-center gap-2 text-sm text-gray-600 dark:text-slate-400 hover:text-gray-900 dark:hover:text-white w-full transition-colors px-2 py-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-slate-800">
             @if (themeService.isDark()) {
               <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                 <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
               </svg>
               <span>Light Mode</span>
             } @else {
               <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                 <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
               </svg>
               <span>Dark Mode</span>
             }
           </button>

           <!-- Profile Link -->
           <a routerLink="/profile" (click)="sidebarOpen.set(false)" class="flex items-center gap-2 text-sm text-gray-600 dark:text-slate-400 hover:text-gray-900 dark:hover:text-white w-full transition-colors px-2 py-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-slate-800">
             <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
               <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
             </svg>
             <span>Profile</span>
           </a>

           <button (click)="api.logout(); router.navigate(['/login'])" class="flex items-center gap-2 text-sm text-gray-600 dark:text-slate-400 hover:text-gray-900 dark:hover:text-white w-full transition-colors px-2 py-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-slate-800">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
            </svg>
            Sign Out
          </button>
        </div>
      </aside>

      <!-- Sidebar overlay (mobile) -->
      @if (sidebarOpen()) {
        <div (click)="sidebarOpen.set(false)" class="fixed inset-0 bg-black/50 z-30 md:hidden"></div>
      }

      <!-- Main Chat Interface -->
      <main class="flex-1 flex flex-col h-full relative">
        <!-- Chat Header -->
        <header class="h-14 border-b border-gray-200 dark:border-slate-800 bg-white/80 dark:bg-slate-900/50 backdrop-blur flex items-center justify-between px-4 z-10 transition-colors">
          <div class="flex items-center gap-3">
             <!-- Hamburger menu button -->
             <button (click)="sidebarOpen.set(!sidebarOpen())" class="text-gray-500 dark:text-slate-400 hover:text-gray-700 dark:hover:text-white">
               <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                 <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
               </svg>
             </button>
             <h2 class="font-semibold text-gray-900 dark:text-white truncate max-w-[200px] sm:max-w-md">{{ project()?.name }}</h2>
          </div>
          <button (click)="deleteProject()" class="text-gray-400 hover:text-red-500 dark:text-slate-500 dark:hover:text-red-400 transition-colors">
            <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
               <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
        </header>

        <!-- Chat Stream -->
        <div class="flex-1 overflow-y-auto p-4 space-y-6 scroll-smooth" #scrollContainer>
           @for (video of videos(); track video._id) {
             <!-- User Prompt Bubble -->
             <div class="flex justify-end">
               <div class="max-w-[85%] sm:max-w-[70%] bg-amber-100 dark:bg-slate-800 rounded-2xl rounded-tr-sm px-4 py-3 text-gray-900 dark:text-slate-200 shadow-sm dark:shadow-none">
                 <p>{{ video.topic }}</p>
                 <div class="mt-1 flex items-center justify-end gap-2 text-xs text-gray-500 dark:text-slate-500">
                    <span>{{ video.video_config?.aspect_ratio || "9:16" }}</span>
                    <span>•</span>
                    <span class="capitalize">{{ video.generator_id?.replace('_', ' ') || 'unknown' }}</span>
                    @if (video.video_config?.duration) {
                      <span>•</span>
                      <span class="capitalize">{{ video.video_config?.duration }}</span>
                    }
                 </div>
               </div>
             </div>

             <!-- AI Response Bubble -->
             <div class="flex justify-start">
                <div class="flex gap-3 max-w-lg">
                   <div class="w-8 h-8 rounded-full bg-amber-600/10 dark:bg-amber-600/20 flex-shrink-0 flex items-center justify-center">
                     <span class="text-amber-600 dark:text-amber-500 text-xs font-bold">AI</span>
                   </div>
                   <div class="space-y-2 w-full">
                      <!-- Video Processing State -->
                      <div class="bg-transparent border border-gray-200 dark:border-slate-800 rounded-xl p-3 w-full">
                         <!-- Shared Container for Video/Placeholder with consistent size -->
                         <div [ngStyle]="getContainerStyles(video.video_config?.aspect_ratio)" class="relative rounded-lg overflow-hidden bg-black mb-2 transition-all duration-300">
                           
                           @if (video.status === 'completed') {
                              <!-- Video Player -->
                              @if (video.video_url) {
                                <video 
                                  controls 
                                  class="w-full h-full object-contain"
                                  preload="metadata">
                                  <source [src]="getVideoUrl(video.video_url)" type="video/mp4">
                                  Your browser does not support the video tag.
                                </video>
                              } @else {
                                <!-- Loading state for completed but not yet loaded video -->
                                <div class="w-full h-full bg-gradient-to-br from-slate-800 to-slate-900 flex flex-col items-center justify-center">
                                  <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-amber-500 mb-3"></div>
                                  <span class="text-gray-400 dark:text-slate-400 text-sm">Loading video...</span>
                                </div>
                              }
                           } @else if (video.status === 'failed') {
                              <div class="w-full h-full flex flex-col items-center justify-center bg-slate-900 text-red-500 dark:text-red-400 p-4 text-center">
                                 <svg class="w-8 h-8 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
                                 <span class="font-medium">Generation failed</span>
                              </div>
                           } @else {
                              <!-- Blurred Placeholder with Progress -->
                              <div class="w-full h-full relative">
                                 <!-- Blurred gradient placeholder -->
                                 <div 
                                   class="absolute inset-0 w-full h-full bg-gradient-to-br from-amber-500/30 via-purple-500/20 to-slate-800 transition-all duration-500"
                                   [style.filter]="'blur(' + getBlurAmount(video._id) + 'px) brightness(0.7)'"
                                   [style.transform]="'scale(' + (1.1 - getProgress(video._id) * 0.001) + ')'"
                                 ></div>
                                 
                                 <!-- Overlay with progress info -->
                                 <div class="absolute inset-0 bg-black/30 flex flex-col items-center justify-center">
                                    <!-- Circular Progress Ring -->
                                    <div class="relative w-20 h-20">
                                       <svg class="w-20 h-20 transform -rotate-90" viewBox="0 0 100 100">
                                         <!-- Background circle -->
                                         <circle cx="50" cy="50" r="42" stroke-width="6" stroke="rgba(255,255,255,0.15)" fill="none"/>
                                         <!-- Progress circle -->
                                         <circle 
                                           cx="50" cy="50" r="42" stroke-width="6" 
                                           stroke="#f59e0b" fill="none"
                                           stroke-linecap="round"
                                           [attr.stroke-dasharray]="264"
                                           [attr.stroke-dashoffset]="264 - (264 * getProgress(video._id) / 100)"
                                           class="transition-all duration-300"
                                         />
                                       </svg>
                                       <span class="absolute inset-0 flex items-center justify-center text-white text-lg font-bold drop-shadow-lg">
                                         {{ getProgress(video._id) | number:'1.0-0' }}%
                                       </span>
                                    </div>
                                    
                                    <!-- Current step text -->
                                    <p class="mt-3 text-white/90 text-sm font-medium text-center px-4 drop-shadow-lg">
                                      {{ getStepText(video._id) }}
                                    </p>
                                    
                                    <!-- Pulsing dots -->
                                    <div class="mt-2 flex gap-1.5">
                                      <span class="w-2 h-2 bg-amber-500 rounded-full animate-pulse"></span>
                                      <span class="w-2 h-2 bg-amber-500 rounded-full animate-pulse" style="animation-delay: 0.15s"></span>
                                      <span class="w-2 h-2 bg-amber-500 rounded-full animate-pulse" style="animation-delay: 0.3s"></span>
                                    </div>
                                 </div>
                                 
                                 <!-- Status badge -->
                                 <div class="absolute top-3 left-3 px-2 py-1 bg-amber-500/90 text-white text-xs font-medium rounded-full flex items-center gap-1.5 shadow-lg">
                                    <span class="w-1.5 h-1.5 bg-white rounded-full animate-pulse"></span>
                                    {{ video.status === 'pending' ? 'Queued' : 'Generating' }}
                                 </div>
                              </div>
                           }
                         </div>

                         <!-- Actions Bar (Download / Completed Status) -->
                         @if (video.status === 'completed') {
                            <div class="flex items-center justify-between px-1">
                               <span class="text-green-600 dark:text-green-400 text-xs font-medium flex items-center gap-1">
                                  <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
                                  Completed
                               </span>
                               @if (video.video_url) {
                                 <a [href]="getVideoUrl(video.video_url)" target="_blank" class="text-xs text-amber-600 hover:text-amber-500 dark:text-amber-400 dark:hover:text-white transition-colors">Download MP4</a>
                               }
                            </div>
                         }


                         <!-- Script Preview -->
                         @if (video.current_step) {
                           <div class="mt-3 p-3 bg-gray-50 dark:bg-slate-900/50 rounded-lg text-sm text-gray-600 dark:text-slate-400 italic border-l-2 border-gray-300 dark:border-slate-700">
                             "{{ video.current_step }}"
                           </div>
                         }
                      </div>
                   </div>
                </div>
             </div>
           }
        </div>

        <!-- Input Area -->
        <div class="p-4 bg-white dark:bg-slate-950 border-t border-gray-200 dark:border-slate-800 transition-colors">
           <form [formGroup]="chatForm" (ngSubmit)="sendMessage()" class="max-w-4xl mx-auto relative">
              <div class="absolute left-3 bottom-3 flex gap-2">
                 <select formControlName="category" class="bg-gray-100 dark:bg-slate-900 border-none text-xs text-gray-600 dark:text-slate-400 hover:text-gray-900 dark:hover:text-white rounded py-1 px-2 focus:ring-0 cursor-pointer transition-colors max-w-[120px]">
                     <option value="explainer_shorts">Explainer</option>
                     <option value="frequency_generator">Frequency</option>
                     <option value="subliminal">Subliminal</option>
                 </select>

                 @if (chatForm.get('category')?.value === 'explainer_shorts') {
                  <select formControlName="style" class="bg-gray-100 dark:bg-slate-900 border-none text-xs text-gray-600 dark:text-slate-400 hover:text-gray-900 dark:hover:text-white rounded py-1 px-2 focus:ring-0 cursor-pointer transition-colors">
                      <option value="family_guy">Family Guy</option>
                      <option value="rick_morty">Rick & Morty</option>
                      <option value="south_park">South Park</option>
                      <option value="documentary">Documentary</option>
                      <option value="pixel_art">Pixel Art</option>
                   </select>
                 }

                 @if (chatForm.get('category')?.value === 'subliminal') {
                    <select formControlName="duration" class="bg-gray-100 dark:bg-slate-900 border-none text-xs text-gray-600 dark:text-slate-400 hover:text-gray-900 dark:hover:text-white rounded py-1 px-2 focus:ring-0 cursor-pointer transition-colors">
                      <option value="short">Short</option>
                      <option value="long">Long</option>
                    </select>
                 }

                  <select formControlName="aspectRatio" class="bg-gray-100 dark:bg-slate-900 border-none text-xs text-gray-600 dark:text-slate-400 hover:text-gray-900 dark:hover:text-white rounded py-1 px-2 focus:ring-0 cursor-pointer transition-colors">
                    <option value="16:9">16:9</option>
                    <option value="9:16">9:16</option>
                    <option value="1:1">1:1</option>
                 </select>
              </div>
              
              <textarea 
                 formControlName="prompt"
                 (keydown.enter)="$event.preventDefault(); sendMessage()"
                 placeholder="Message VidGen AI..." 
                 class="w-full bg-gray-50 dark:bg-slate-900 text-gray-900 dark:text-white rounded-xl border border-gray-300 dark:border-slate-800 pl-4 pr-12 pt-3 pb-10 focus:ring-2 focus:ring-amber-500/50 focus:border-amber-500/50 resize-none shadow-lg dark:shadow-none transition-colors"
                 rows="1"
                 style="min-height: 54px;"
              ></textarea>
              
              <button type="submit" [disabled]="chatForm.invalid || isProcessing()" class="absolute right-2 bottom-3 p-1.5 bg-amber-600 text-white rounded-lg hover:bg-amber-500 disabled:opacity-50 transition-colors">
                 @if (isProcessing()) {
                    <svg class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                 } @else {
                    <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 10l7-7m0 0l7 7m-7-7v18"/></svg>
                 }
              </button>
           </form>
           <p class="text-center text-xs text-gray-500 dark:text-slate-600 mt-2">VidGen AI can make mistakes. Consider checking important information.</p>
        </div>
      </main>
    </div>
  `
})
export class ProjectDetailComponent implements OnInit, OnDestroy, AfterViewChecked {
  public api: ApiService = inject(ApiService);
  public router: Router = inject(Router);
  public themeService: ThemeService = inject(ThemeService);
  private route: ActivatedRoute = inject(ActivatedRoute);
  private fb: FormBuilder = inject(FormBuilder);
  private wsService: WebSocketService = inject(WebSocketService);

  @ViewChild('scrollContainer') private scrollContainer!: ElementRef;

  project = signal<Project | null>(null);
  videos = signal<Video[]>([]);
  isProcessing = signal(false);
  
  // Real-time progress tracking
  activeVideoId = signal<string | null>(null);
  currentProgress = signal(0);
  currentStep = signal('');
  
  // UI state
  sidebarOpen = signal(false);
  
  private pollInterval: any;
  private shouldScroll = false;
  private wsSubscription: Subscription | null = null;

  chatForm = this.fb.group({
    prompt: ['', Validators.required],
    category: ['explainer_shorts'],
    style: ['family_guy'],
    aspectRatio: ['9:16'],
    duration: ['short']
  });

  ngOnInit() {
    this.route.paramMap.subscribe(params => {
      const id = params.get('id');
      if (id) {
        this.loadProject(id);
      }
    });
  }

  ngOnDestroy() {
    if (this.pollInterval) clearInterval(this.pollInterval);
    if (this.wsSubscription) this.wsSubscription.unsubscribe();
    this.wsService.disconnect();
  }

  ngAfterViewChecked() {
    if (this.shouldScroll) {
        this.scrollToBottom();
        this.shouldScroll = false;
    }
  }

  scrollToBottom(): void {
    try {
        this.scrollContainer.nativeElement.scrollTop = this.scrollContainer.nativeElement.scrollHeight;
    } catch(err) { }
  }

  async loadProject(id: string) {
    if (this.pollInterval) clearInterval(this.pollInterval);
    
    try {
      const p = await this.api.getProject(id);
      this.project.set(p);
      await this.refreshHistory();
      this.startPolling(id);
      this.shouldScroll = true;
    } catch (err) {
      console.error(err);
      this.router.navigate(['/dashboard']);
    }
  }

  async refreshHistory() {
    if (!this.project()) return;
    try {
      const v = await this.api.getProjectHistory(this.project()!._id);
      // Sort by created_at descending (newest first)
      v.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
      if (v.length > this.videos().length) this.shouldScroll = true;
      this.videos.set(v);
    } catch (err) {
      console.error('Failed to refresh history:', err);
    }
  }

  startPolling(id: string) {
    // Poll less frequently when WebSocket is active, more when not
    // This is a fallback mechanism
    this.pollInterval = setInterval(() => {
      // Only poll if WebSocket is not connected or if we need to check for updates
      if (!this.wsService.isConnected() || this.activeVideoId() === null) {
        this.refreshHistory();
      }
    }, 5000); // Poll every 5 seconds as fallback
  }

  async sendMessage() {
    if (this.chatForm.invalid || this.isProcessing() || !this.project()) return;

    this.isProcessing.set(true);
    const { prompt, category, style, aspectRatio, duration } = this.chatForm.value;

    // Map category to generator_id
    let generatorId = 'family_guy';
    if (category === 'explainer_shorts') {
      generatorId = style || 'family_guy';
    } else if (category === 'frequency_generator') {
      generatorId = 'frequency';
    } else if (category === 'subliminal') {
      generatorId = 'subliminal';
    }

    try {
      const video = await this.api.generateVideo({
        project_id: this.project()!._id,
        generator_id: generatorId,
        topic: prompt!,
        aspect_ratio: aspectRatio!,
        duration: duration!,
        output_format: 'mp4',
        quality: '1080p'
      });
      
      this.chatForm.patchValue({ prompt: '' });
      
      // Add video to list immediately
      const currentVideos = this.videos();
      this.videos.set([video, ...currentVideos]);
      this.shouldScroll = true;
      
      // Refresh history to ensure we have the latest
      await this.refreshHistory();
      
      // Subscribe to WebSocket for real-time progress
      if (video && video._id) {
        this.activeVideoId.set(video._id);
        this.currentProgress.set(0);
        this.currentStep.set('Starting...');
        
        // Cleanup existing subscription
        if (this.wsSubscription) {
          this.wsSubscription.unsubscribe();
        }
        
        this.wsSubscription = this.wsService.connect(video._id).subscribe({
          next: (progress: VideoProgress) => {
            if (progress.type === 'progress' && progress.status) {
              // Update progress signals
              if (progress.progress !== undefined) {
                this.currentProgress.set(progress.progress);
              }
              if (progress.current_step) {
                this.currentStep.set(progress.current_step);
              }
              
              // Update video in the list if it exists
              const currentVideos = this.videos();
              const videoIndex = currentVideos.findIndex(v => v._id === video._id);
              if (videoIndex >= 0) {
                const updatedVideos = [...currentVideos];
                updatedVideos[videoIndex] = {
                  ...updatedVideos[videoIndex],
                  status: progress.status,
                  progress: progress.progress ?? updatedVideos[videoIndex].progress,
                  current_step: progress.current_step ?? updatedVideos[videoIndex].current_step,
                  video_url: progress.video_url ?? updatedVideos[videoIndex].video_url,
                  error_message: progress.error_message ?? updatedVideos[videoIndex].error_message
                };
                this.videos.set(updatedVideos);
              }
              
              // Handle completion or failure
              if (progress.status === 'completed' || progress.status === 'failed') {
                this.activeVideoId.set(null);
                this.isProcessing.set(false);
                // Refresh history to get final state
                setTimeout(() => this.refreshHistory(), 500);
                this.shouldScroll = true;
              }
            }
          },
          error: (err) => {
            console.error('WebSocket error:', err);
            this.activeVideoId.set(null);
            this.isProcessing.set(false);
            // Fallback to polling if WebSocket fails
            console.log('Falling back to polling for video updates');
          }
        });
      }
    } catch (err) {
      console.error(err);
      this.isProcessing.set(false);
    }
  }

  async deleteProject() {
    if (!this.project() || !confirm('Are you sure you want to delete this chat?')) return;
    try {
      await this.api.deleteProject(this.project()!._id);
      this.router.navigate(['/dashboard']);
    } catch (err) {
      console.error(err);
    }
  }

  /**
   * Get current progress for a video (from WebSocket updates or stored progress)
   */
  getProgress(videoId: string): number {
    // If this is the active video being updated via WebSocket, use signed progress
    if (this.activeVideoId() === videoId) {
      return this.currentProgress();
    }
    // Otherwise, get from video record
    const video = this.videos().find(v => v._id === videoId);
    return video?.progress || 0;
  }

  /**
   * Calculate blur amount based on progress (20px at 0% → 0px at 100%)
   */
  getBlurAmount(videoId: string): number {
    const progress = this.getProgress(videoId);
    // Max blur of 20px, decreasing linearly with progress
    return Math.max(0, 20 - (progress * 0.2));
  }

  /**
   * Get the current step text for a video
   */
  getStepText(videoId: string): string {
    // If this is the active video, use the signal value
    if (this.activeVideoId() === videoId) {
      return this.currentStep() || 'Initializing...';
    }
    // Otherwise, get from video record
    const video = this.videos().find(v => v._id === videoId);
    return video?.current_step || 'Processing...';
  }

  /**
   * Get container styles for video aspect ratio
   * Returns precise width and height to prevent layout shifts
   */
  getContainerStyles(aspectRatio: string | undefined | null): { width: string, height: string, 'aspect-ratio': string } {
    switch (aspectRatio) {
      case '9:16':
        // Portrait video - Fixed height 400px, calculated width
        return { width: '225px', height: '400px', 'aspect-ratio': '9/16' };
      case '1:1':
        // Square video - Fixed size 350px
        return { width: '350px', height: '350px', 'aspect-ratio': '1/1' };
      case '16:9':
      default:
        // Landscape video - Fixed width 400px, calculated height
        return { width: '400px', height: '225px', 'aspect-ratio': '16/9' };
    }
  }

  getVideoUrl(videoUrl: string | null | undefined): string {
    if (!videoUrl) return '';
    // If already a full URL, return as is
    if (videoUrl.startsWith('http://') || videoUrl.startsWith('https://')) {
      return videoUrl;
    }
    // Otherwise, prepend the backend URL
    // Ensure we have a leading slash
    const path = videoUrl.startsWith('/') ? videoUrl : `/${videoUrl}`;
    return `http://localhost:8000${path}`;
  }
}


