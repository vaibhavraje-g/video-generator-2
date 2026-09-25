import { Component, inject, signal, OnInit, OnDestroy, ViewChild, ElementRef, AfterViewChecked } from '@angular/core';
import { CommonModule, DatePipe } from '@angular/common';
import { ActivatedRoute, RouterLink, Router } from '@angular/router';
import { FormBuilder, Validators, ReactiveFormsModule } from '@angular/forms';
import { ApiService, Project, Video } from '../services/api.service';
import { ThemeService } from '../services/theme.service';
import { SseService, VideoProgressEvent } from '../services/sse.service';
import { Subscription } from 'rxjs';
import { SidebarComponent } from '../components/sidebar/sidebar.component';
import { AgentPipelineComponent } from '../components/agent-pipeline/agent-pipeline.component';

@Component({
  selector: 'app-project-detail',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterLink, DatePipe, SidebarComponent, AgentPipelineComponent],
  template: `
    <div class="flex h-screen bg-[#131314] text-[#E3E3E3] overflow-hidden font-sans">
      
      <!-- Shared Studio Sidebar -->
      <app-sidebar 
        [isOpen]="sidebarOpen()"
        [activeProjectId]="project()?._id || null"
        (sidebarClose)="sidebarOpen.set(false)">
      </app-sidebar>

      <!-- Main Studio Workspace -->
      <main class="flex-1 flex flex-col h-full relative overflow-hidden bg-[#131314]">
        
        <!-- Studio Header -->
        <header class="h-14 border-b border-[#2E3135] bg-[#1E1F20] flex items-center justify-between px-4 sm:px-6 z-10 sticky top-0">
          <div class="flex items-center gap-3">
            <button 
              (click)="sidebarOpen.set(true)"
              aria-label="Open sidebar"
              class="md:hidden text-[#80868B] hover:text-[#F1F3F4] p-1 rounded hover:bg-[#282A2D] focus-visible:ring-1 focus-visible:ring-[#D97757]">
              <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
            <div>
              <h2 class="font-editorial font-semibold text-xs sm:text-sm text-[#F1F3F4] truncate max-w-[200px] sm:max-w-md">
                {{ project()?.name || 'Loading Project...' }}
              </h2>
              <div class="flex items-center gap-2 text-[10px] font-mono text-[#80868B]">
                <span>Studio Canvas</span>
                <span>•</span>
                <span>Server-Sent Events</span>
              </div>
            </div>
          </div>

          <div class="flex items-center gap-2">
            <!-- SSE Status Badge -->
            <div class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-mono border bg-[#131314]"
                 [class.border-emerald-700]="sseService.isConnected()"
                 [class.text-[#81C995]]="sseService.isConnected()"
                 [class.border-[#2E3135]]="!sseService.isConnected()"
                 [class.text-[#80868B]]="!sseService.isConnected()">
              <span class="w-1.5 h-1.5 rounded-full" 
                    [class.bg-[#81C995]]="sseService.isConnected()" 
                    [class.bg-[#80868B]]="!sseService.isConnected()"></span>
              <span>{{ sseService.isConnected() ? 'SSE Connected' : 'SSE Standby' }}</span>
            </div>

            <!-- Delete Project Button -->
            <button 
              (click)="deleteProject()" 
              title="Delete Project"
              aria-label="Delete Project"
              class="text-[#80868B] hover:text-[#F28B82] p-1.5 rounded hover:bg-[#282A2D] transition-colors focus-visible:ring-1 focus-visible:ring-[#F28B82]">
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          </div>
        </header>

        <!-- Generation & Video Stream Viewport -->
        <div class="flex-1 overflow-y-auto p-4 sm:p-6 space-y-6" #scrollContainer>
          @for (video of videos(); track video._id) {
            
            <!-- User Prompt Capsule -->
            <div class="flex justify-end">
              <div class="max-w-[92%] sm:max-w-[75%] bg-[#1E1F20] border border-[#2E3135] rounded-lg p-3.5 text-[#E3E3E3] shadow-sm">
                <div class="flex items-center justify-between mb-1.5 text-[10px] font-mono text-[#80868B]">
                  <span class="font-semibold text-[#D97757]">CREATIVE BRIEF</span>
                  <span>{{ video.created_at | date:'shortTime' }}</span>
                </div>
                <p class="text-xs sm:text-sm text-[#F1F3F4] leading-relaxed font-normal">{{ video.topic }}</p>
                <div class="mt-2 pt-2 border-t border-[#2E3135] flex flex-wrap items-center justify-end gap-2 text-[10px] font-mono text-[#80868B]">
                  <span class="px-2 py-0.5 rounded-full bg-[#131314] border border-[#2E3135]">Ratio: {{ video.video_config?.aspect_ratio || "9:16" }}</span>
                  <span class="px-2 py-0.5 rounded-full bg-[#131314] border border-[#2E3135]">{{ formatGeneratorName(video.generator_id) }}</span>
                  <span class="px-2 py-0.5 rounded-full bg-[#131314] text-[#BDC1C6] border border-[#2E3135]">1080p Master</span>
                </div>
              </div>
            </div>

            <!-- Studio Production Stage Output -->
            <div class="flex justify-start">
              <div class="max-w-2xl w-full">
                
                <div class="bg-[#1E1F20] rounded-lg p-4 sm:p-5 w-full border border-[#2E3135] shadow-sm">
                  
                  @if (video.status === 'completed') {
                    <!-- Completed Video Player Theater -->
                    <div class="space-y-3.5">
                      <div [ngStyle]="getContainerStyles(video.video_config?.aspect_ratio)" 
                           class="relative rounded-md overflow-hidden bg-black mx-auto shadow border border-[#2E3135] flex items-center justify-center">
                        @if (video.video_url) {
                          <video 
                            controls 
                            playsinline
                            class="w-full h-full object-contain"
                            preload="metadata">
                            <source [src]="getVideoUrl(video.video_url)" type="video/mp4">
                            Your browser does not support the video tag.
                          </video>
                        } @else {
                          <div class="w-full h-full flex flex-col items-center justify-center p-6 text-center text-[#80868B] space-y-2">
                            <div class="animate-spin rounded-full h-6 w-6 border-2 border-[#D97757] border-t-transparent"></div>
                            <span class="text-xs font-mono">Synchronizing media stream...</span>
                          </div>
                        }
                      </div>

                      <!-- Video Controls & Metadata Bar -->
                      <div class="pt-2.5 border-t border-[#2E3135] flex flex-wrap items-center justify-between gap-2.5">
                        <div class="flex items-center gap-2">
                          <span class="px-2.5 py-0.5 rounded-full bg-[#81C995]/10 text-[#81C995] border border-[#81C995]/30 text-[11px] font-mono font-medium flex items-center gap-1">
                            <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7" />
                            </svg>
                            Completed (100%)
                          </span>
                          <span class="text-[11px] font-mono text-[#80868B]">1080p Master</span>
                        </div>

                        <div class="flex items-center gap-2">
                          <button (click)="toggleManifest(video._id)" 
                                  class="btn-secondary px-2.5 py-1 text-xs flex items-center gap-1">
                            <svg class="w-3.5 h-3.5 text-[#80868B]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                            <span>Specs</span>
                          </button>

                          @if (video.video_url) {
                            <a [href]="getVideoUrl(video.video_url)" 
                               target="_blank" 
                               download 
                               class="btn-primary px-3 py-1 text-xs flex items-center gap-1">
                              <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                              </svg>
                              <span>Download MP4</span>
                            </a>
                          }
                        </div>
                      </div>

                      <!-- Technical Manifest Drawer -->
                      @if (isManifestOpen(video._id)) {
                        <div class="p-3 rounded-md bg-[#131314] border border-[#2E3135] text-[11px] font-mono space-y-2">
                          <div class="font-semibold text-[#BDC1C6] flex items-center justify-between border-b border-[#2E3135] pb-1">
                            <span>{{ video.generator_id === 'frequency' ? 'ACOUSTIC DSP EXECUTION TRACE' : 'MULTI-AGENT EXECUTION TRACE' }}</span>
                            <span class="text-[10px] text-[#80868B]">SSE Event Driven</span>
                          </div>
                          <div class="grid grid-cols-1 sm:grid-cols-2 gap-2 text-[#80868B] text-[10px]">
                            @if (video.generator_id === 'frequency') {
                              <div><span class="text-[#BDC1C6]">Acoustic Engine:</span> Native FFmpeg DSP + Lissajous Vectorscope</div>
                              <div><span class="text-[#BDC1C6]">Format & Ratio:</span> {{ video.video_config?.aspect_ratio || "9:16" }} • 1080p 60fps</div>
                              <div><span class="text-[#BDC1C6]">Audio Pipeline:</span> 320kbps Stereo Binaural Sine (Phase Aligned)</div>
                              <div><span class="text-[#BDC1C6]">Visualizer:</span> Real-Time Phase Vectorscope + Oscilloscope HUD</div>
                            } @else {
                              <div><span class="text-[#BDC1C6]">Generator Engine:</span> {{ formatGeneratorName(video.generator_id) }}</div>
                              <div><span class="text-[#BDC1C6]">Format & Ratio:</span> {{ video.video_config?.aspect_ratio || "9:16" }} • 1080p 60fps</div>
                              <div><span class="text-[#BDC1C6]">Audio Pipeline:</span> Zero-Shot Neural Voice Clone (:8004)</div>
                              <div><span class="text-[#BDC1C6]">Compositor:</span> FFmpeg Multi-Layer GPU/CPU Worker</div>
                            }
                          </div>
                        </div>
                      }
                    </div>
                  } @else if (video.status === 'failed') {
                    <!-- Error / Failed Pipeline Card -->
                    <div class="p-4 rounded-md bg-[#F28B82]/10 border border-[#F28B82]/30 text-left space-y-2">
                      <div class="flex items-center gap-2 text-[#F28B82] text-xs font-semibold">
                        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                        </svg>
                        <span>Pipeline Error</span>
                      </div>
                      <p class="text-xs text-[#80868B] leading-relaxed font-mono">
                        {{ video.error_message || 'Video pipeline interrupted. Please check input parameters and retry.' }}
                      </p>
                    </div>
                  } @else {
                    <!-- Stepper Component -->
                    <app-agent-pipeline 
                      [progress]="getProgress(video._id)"
                      [stepText]="getStepText(video._id)"
                      [pipelineType]="video.generator_id === 'frequency' ? 'frequency' : 'explainer'">
                    </app-agent-pipeline>
                  }

                </div>
              </div>
            </div>
          } @empty {
            <!-- Empty State -->
            <div class="h-full flex flex-col items-center justify-center text-center p-8 max-w-sm mx-auto space-y-3">
              <div class="w-10 h-10 rounded-md bg-[#1E1F20] border border-[#2E3135] flex items-center justify-center text-[#80868B]">
                <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
              </div>
              <h3 class="font-editorial font-medium text-sm text-[#F1F3F4]">Studio Ready</h3>
              <p class="text-xs text-[#80868B] leading-relaxed">
                Enter an acoustic frequency prompt or narrative topic below to begin generating.
              </p>
            </div>
          }
        </div>

        <!-- Studio Console (Clean, Docked Inspector) -->
        <div class="p-3 sm:p-4 bg-[#1E1F20] border-t border-[#2E3135]">
          <form [formGroup]="chatForm" (ngSubmit)="sendMessage()" class="max-w-4xl mx-auto space-y-2.5">
            
            <!-- Controls Bar: Category, Persona / DSP Tag, Aspect Ratio -->
            <div class="flex flex-wrap items-center gap-2">
              
              <!-- Category Selector -->
              <label for="consoleCategory" class="sr-only">Video Format</label>
              <select id="consoleCategory" formControlName="category" 
                      class="app-input px-2.5 py-1 text-xs text-[#BDC1C6] bg-[#18191B] border border-[#3C4043] rounded-md cursor-pointer">
                <option value="frequency_generator">Acoustic Frequencies (DSP)</option>
                <option value="explainer_shorts">Explainer Video Shorts</option>
              </select>

              <!-- Persona / Style Selector -->
              @if (chatForm.get('category')?.value === 'explainer_shorts') {
                <label for="consoleStyle" class="sr-only">Voice Persona</label>
                <select id="consoleStyle" formControlName="style" 
                        class="app-input px-2.5 py-1 text-xs text-[#BDC1C6] bg-[#18191B] border border-[#3C4043] rounded-md cursor-pointer">
                  <option value="family_guy">Cast: Family Guy (Peter, Brian, Stewie)</option>
                  <option value="rick_morty">Cast: Rick & Morty</option>
                  <option value="south_park">Cast: South Park</option>
                  <option value="documentary">Cast: Cinematic Documentary</option>
                  <option value="pixel_art">Cast: Pixel Art Narrator</option>
                </select>
              } @else {
                <div class="px-2.5 py-1 rounded-full text-[11px] font-mono text-[#BDC1C6] bg-[#131314] border border-[#2E3135]">
                  Lissajous Vectorscope + Waveform
                </div>
              }

              <!-- Aspect Ratio Selector -->
              <label for="consoleAspectRatio" class="sr-only">Aspect Ratio</label>
              <select id="consoleAspectRatio" formControlName="aspectRatio" 
                      class="app-input px-2.5 py-1 text-xs text-[#BDC1C6] bg-[#18191B] border border-[#3C4043] rounded-md cursor-pointer">
                <option value="9:16">9:16 Vertical (Shorts/Reels)</option>
                <option value="16:9">16:9 Landscape (YouTube)</option>
                <option value="1:1">1:1 Square (Feed)</option>
              </select>

              <span class="px-2 py-0.5 rounded-full text-[10px] font-mono text-[#80868B] bg-[#131314] border border-[#2E3135] hidden sm:inline-block">
                1080p Master
              </span>
            </div>

            <!-- Input Box & Action Button -->
            <div class="relative">
              <label for="consolePrompt" class="sr-only">Prompt Input</label>
              <textarea 
                id="consolePrompt"
                formControlName="prompt"
                (keydown.enter)="$event.preventDefault(); sendMessage()"
                [placeholder]="getPlaceholderText()" 
                class="app-input w-full pl-3 pr-12 py-2.5 text-xs sm:text-sm resize-none h-14 leading-relaxed bg-[#18191B] border border-[#3C4043] rounded-md text-[#F1F3F4] focus:border-[#D97757] focus:ring-1 focus:ring-[#D97757]"
              ></textarea>
              
              <button type="submit" 
                      [disabled]="chatForm.invalid || isProcessing()" 
                      aria-label="Generate"
                      class="btn-primary absolute right-2.5 top-1/2 -translate-y-1/2 w-8 h-8 rounded-md flex items-center justify-center focus-visible:ring-2 focus-visible:ring-[#D97757]">
                @if (isProcessing()) {
                  <svg class="animate-spin h-3.5 w-3.5 text-[#FAF8F5]" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                } @else {
                  <svg class="w-3.5 h-3.5 text-[#FAF8F5]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M14 5l7 7m0 0l-7 7m7-7H3"/>
                  </svg>
                }
              </button>
            </div>

            <div class="flex items-center justify-between text-[10px] text-[#80868B] font-mono">
              <span>Press Enter to generate</span>
              <span>SSE Real-Time Stream</span>
            </div>

          </form>
        </div>

      </main>
    </div>
  `
})
export class ProjectDetailComponent implements OnInit, OnDestroy, AfterViewChecked {
  public api: ApiService = inject(ApiService);
  public router: Router = inject(Router);
  public themeService: ThemeService = inject(ThemeService);
  public sseService: SseService = inject(SseService);
  private route: ActivatedRoute = inject(ActivatedRoute);
  private fb: FormBuilder = inject(FormBuilder);

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
  manifestOpenMap = signal<Record<string, boolean>>({});
  
  private pollInterval: any;
  private shouldScroll = false;
  private sseSubscription: Subscription | null = null;

  chatForm = this.fb.group({
    prompt: ['', Validators.required],
    category: ['frequency_generator'],
    style: ['family_guy'],
    aspectRatio: ['9:16'],
    duration: ['short']
  });

  isFrequency(): boolean {
    return this.chatForm.get('category')?.value === 'frequency_generator';
  }

  getPlaceholderText(): string {
    return this.isFrequency()
      ? "Enter frequency & beat (e.g. '432 Hz carrier with 10 Hz Alpha beat for deep coding flow')..."
      : "Enter topic (e.g. 'How Einstein debated quantum entanglement')...";
  }

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
    if (this.sseSubscription) {
      this.sseSubscription.unsubscribe();
      this.sseSubscription = null;
    }
    this.sseService.disconnect();
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

      // Auto-connect SSE if there is an in-flight video
      const inFlightVideo = this.videos().find(v => v.status === 'processing' || v.status === 'pending');
      if (inFlightVideo) {
        this.subscribeToSse(inFlightVideo._id);
      }
    } catch (err) {
      console.error(err);
      this.router.navigate(['/dashboard']);
    }
  }

  async refreshHistory() {
    if (!this.project()) return;
    try {
      const v = await this.api.getProjectHistory(this.project()!._id);
      v.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
      if (v.length > this.videos().length) this.shouldScroll = true;
      this.videos.set(v);
    } catch (err) {
      console.error('Failed to refresh history:', err);
    }
  }

  startPolling(id: string) {
    this.pollInterval = setInterval(() => {
      if (!this.sseService.isConnected() || this.activeVideoId() === null) {
        this.refreshHistory();
      }
    }, 5000);
  }

  subscribeToSse(videoId: string) {
    this.activeVideoId.set(videoId);
    this.currentProgress.set(0);
    this.currentStep.set('Initializing pipeline...');

    if (this.sseSubscription) {
      this.sseSubscription.unsubscribe();
    }

    this.sseSubscription = this.sseService.connect(videoId).subscribe({
      next: (event: VideoProgressEvent) => {
        if (event.progress !== undefined) {
          this.currentProgress.set(event.progress);
        }
        if (event.current_step) {
          this.currentStep.set(event.current_step);
        }

        const currentVideos = this.videos();
        const index = currentVideos.findIndex(v => v._id === videoId);
        if (index >= 0) {
          const updated = [...currentVideos];
          updated[index] = {
            ...updated[index],
            status: event.status ?? updated[index].status,
            progress: event.progress ?? updated[index].progress,
            current_step: event.current_step ?? updated[index].current_step,
            video_url: event.video_url ?? updated[index].video_url,
            error_message: event.error_message ?? updated[index].error_message
          };
          this.videos.set(updated);
        }

        if (event.status === 'completed' || event.type === 'complete') {
          this.activeVideoId.set(null);
          this.isProcessing.set(false);
          this.currentProgress.set(100);
          setTimeout(() => this.refreshHistory(), 600);
          this.shouldScroll = true;
        } else if (event.status === 'failed' || event.type === 'error') {
          this.activeVideoId.set(null);
          this.isProcessing.set(false);
          setTimeout(() => this.refreshHistory(), 600);
        }
      },
      error: (err) => {
        console.error('SSE streaming error:', err);
        this.activeVideoId.set(null);
        this.isProcessing.set(false);
      }
    });
  }

  async sendMessage() {
    if (this.chatForm.invalid || this.isProcessing() || !this.project()) return;

    this.isProcessing.set(true);
    const { prompt, category, style, aspectRatio, duration } = this.chatForm.value;

    let generatorId = 'family_guy';
    if (category === 'explainer_shorts') {
      generatorId = style || 'family_guy';
    } else if (category === 'frequency_generator') {
      generatorId = 'frequency';
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
      
      const currentVideos = this.videos();
      this.videos.set([video, ...currentVideos]);
      this.shouldScroll = true;
      
      await this.refreshHistory();
      
      if (video && video._id) {
        this.subscribeToSse(video._id);
      }
    } catch (err) {
      console.error('Failed to generate video:', err);
      this.isProcessing.set(false);
    }
  }

  async deleteProject() {
    if (!this.project() || !confirm('Are you sure you want to delete this project?')) return;
    try {
      await this.api.deleteProject(this.project()!._id);
      this.router.navigate(['/dashboard']);
    } catch (err) {
      console.error(err);
    }
  }

  getProgress(videoId: string): number {
    if (this.activeVideoId() === videoId) {
      return this.currentProgress();
    }
    const video = this.videos().find(v => v._id === videoId);
    return video?.progress || 0;
  }

  getStepText(videoId: string): string {
    if (this.activeVideoId() === videoId) {
      return this.currentStep() || 'Synthesizing creative assets...';
    }
    const video = this.videos().find(v => v._id === videoId);
    return video?.current_step || 'Processing...';
  }

  getContainerStyles(aspectRatio: string | undefined | null): { width: string, height: string, 'aspect-ratio': string } {
    switch (aspectRatio) {
      case '9:16':
        return { width: '260px', height: '460px', 'aspect-ratio': '9/16' };
      case '1:1':
        return { width: '360px', height: '360px', 'aspect-ratio': '1/1' };
      case '16:9':
      default:
        return { width: '460px', height: '260px', 'aspect-ratio': '16/9' };
    }
  }

  getVideoUrl(videoUrl: string | null | undefined): string {
    if (!videoUrl) return '';
    if (videoUrl.startsWith('http://') || videoUrl.startsWith('https://')) {
      return videoUrl;
    }
    const path = videoUrl.startsWith('/') ? videoUrl : `/${videoUrl}`;
    return `http://localhost:8000${path}`;
  }

  formatGeneratorName(generatorId: string | undefined): string {
    if (!generatorId) return 'Explainer Shorts';
    switch (generatorId) {
      case 'family_guy': return 'Family Guy Cast';
      case 'rick_morty': return 'Rick & Morty Cast';
      case 'south_park': return 'South Park Cast';
      case 'documentary': return 'Cinematic Documentary';
      case 'frequency': return 'Acoustic Frequency & Binaural Beats';
      default: return generatorId.replace('_', ' ');
    }
  }

  toggleManifest(videoId: string) {
    const current = this.manifestOpenMap();
    this.manifestOpenMap.set({
      ...current,
      [videoId]: !current[videoId]
    });
  }

  isManifestOpen(videoId: string): boolean {
    return !!this.manifestOpenMap()[videoId];
  }
}
