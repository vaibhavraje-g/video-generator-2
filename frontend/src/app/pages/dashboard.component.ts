import { Component, inject, signal } from '@angular/core';
import { RouterLink, Router } from '@angular/router';
import { FormBuilder, Validators, ReactiveFormsModule } from '@angular/forms';
import { ApiService } from '../services/api.service';
import { ThemeService } from '../services/theme.service';
import { CommonModule } from '@angular/common';
import { SidebarComponent } from '../components/sidebar/sidebar.component';

interface FrequencyChip {
  label: string;
  sub: string;
  prompt: string;
}

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [RouterLink, ReactiveFormsModule, CommonModule, SidebarComponent],
  template: `
    <div class="flex h-screen bg-[#131314] text-[#E3E3E3] overflow-hidden font-sans">
      
      <!-- Shared Studio Sidebar -->
      <app-sidebar 
        [isOpen]="sidebarOpen()"
        (sidebarClose)="sidebarOpen.set(false)">
      </app-sidebar>

      <!-- Main Creation Studio Canvas -->
      <main class="flex-1 flex flex-col relative h-full overflow-y-auto">
        
        <!-- Mobile Header Bar -->
        <header class="md:hidden h-14 border-b border-[#2E3135] bg-[#1E1F20] flex items-center justify-between px-4 z-20 sticky top-0">
          <div class="flex items-center gap-2.5">
            <button 
              (click)="sidebarOpen.set(true)"
              aria-label="Open studio sidebar"
              class="text-[#80868B] hover:text-[#F1F3F4] p-1 rounded hover:bg-[#282A2D] focus-visible:ring-1 focus-visible:ring-[#D97757]">
              <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
            <span class="font-editorial font-semibold text-xs text-[#F1F3F4]">VidGen Studio</span>
          </div>

          <div class="flex items-center gap-1.5">
            <span class="w-2 h-2 rounded-full bg-[#81C995]"></span>
            <span class="text-[10px] font-mono text-[#80868B] uppercase">Online</span>
          </div>
        </header>

        <!-- Studio Center Stage -->
        <div class="flex-1 flex flex-col items-center justify-center p-4 sm:p-6 md:p-8 max-w-3xl mx-auto w-full">
          <div class="w-full space-y-6">
            
            <!-- Page Header -->
            <div class="text-left space-y-1.5">
              <h1 class="text-2xl sm:text-3xl font-editorial font-semibold text-[#F1F3F4] tracking-tight">
                Studio Workspace
              </h1>
              <p class="text-xs text-[#80868B] leading-relaxed max-w-xl">
                Synthesize acoustic frequency soundscapes with binaural entrainment or compose multi-character explainer video shorts.
              </p>
            </div>

            <!-- Google AI Studio Segmented Engine Switcher -->
            <div class="flex items-center justify-start">
              <div class="inline-flex p-1 rounded-full bg-[#1E1F20] border border-[#2E3135]" role="tablist" aria-label="Synthesis Engine">
                <button type="button" 
                        role="tab"
                        [attr.aria-selected]="isFrequency()"
                        (click)="setCategory('frequency_generator')"
                        [class.bg-[#282A2D]]="isFrequency()"
                        [class.border]="isFrequency()"
                        [class.border-[#3C4043]]="isFrequency()"
                        [class.text-[#FAF8F5]]="isFrequency()"
                        [class.shadow-sm]="isFrequency()"
                        [class.text-[#80868B]]="!isFrequency()"
                        class="px-4 py-1.5 rounded-full text-xs font-medium transition-colors focus-visible:ring-1 focus-visible:ring-[#D97757]">
                  Acoustic Frequencies (DSP)
                </button>

                <button type="button" 
                        role="tab"
                        [attr.aria-selected]="!isFrequency()"
                        (click)="setCategory('explainer_shorts')"
                        [class.bg-[#282A2D]]="!isFrequency()"
                        [class.border]="!isFrequency()"
                        [class.border-[#3C4043]]="!isFrequency()"
                        [class.text-[#FAF8F5]]="!isFrequency()"
                        [class.shadow-sm]="!isFrequency()"
                        [class.text-[#80868B]]="isFrequency()"
                        class="px-4 py-1.5 rounded-full text-xs font-medium transition-colors focus-visible:ring-1 focus-visible:ring-[#D97757]">
                  Explainer Video Shorts
                </button>
              </div>
            </div>

            <!-- Creation Studio Form -->
            <div class="p-5 rounded-lg bg-[#1E1F20] border border-[#2E3135] shadow-sm space-y-4">
              <form [formGroup]="chatForm" (ngSubmit)="startChat()" class="space-y-4">
                
                <!-- Quick Frequency Preset Chips (Frequency Mode Only) -->
                @if (isFrequency()) {
                  <div class="space-y-1.5">
                    <label class="text-[11px] font-medium text-[#80868B] uppercase tracking-wider block">
                      Acoustic Calibration Presets:
                    </label>
                    <div class="flex flex-wrap gap-1.5">
                      @for (chip of frequencyChips; track chip.label) {
                        <button type="button"
                                (click)="applyFrequencyChip(chip)"
                                class="px-2.5 py-1 rounded-full text-xs font-medium bg-[#131314] hover:bg-[#282A2D] border border-[#2E3135] hover:border-[#5F6368] text-[#BDC1C6] hover:text-[#F1F3F4] transition-colors focus-visible:ring-1 focus-visible:ring-[#D97757]">
                          <span class="font-semibold text-[#F1F3F4]">{{ chip.label }}</span>
                          <span class="text-[#80868B] text-[10px] ml-1">({{ chip.sub }})</span>
                        </button>
                      }
                    </div>
                  </div>
                }

                <!-- Topic / Creative Prompt Field -->
                <div class="space-y-1">
                  <label for="promptInput" class="text-xs font-medium text-[#BDC1C6] block">
                    {{ isFrequency() ? 'Acoustic Prompt or Frequency Description' : 'Video Narrative Topic' }}
                  </label>
                  <textarea 
                    id="promptInput"
                    formControlName="prompt"
                    (keydown.enter)="$event.preventDefault(); startChat()"
                    [placeholder]="getPlaceholderText()" 
                    class="app-input w-full p-3.5 h-28 text-xs sm:text-sm leading-relaxed resize-none bg-[#18191B] border border-[#3C4043] rounded-md text-[#F1F3F4] focus:border-[#D97757] focus:ring-1 focus:ring-[#D97757]"
                  ></textarea>
                </div>

                <!-- Parameter Controls Bar -->
                <div class="flex flex-col sm:flex-row gap-3 items-center justify-between pt-3 border-t border-[#2E3135]">
                  <div class="flex flex-wrap gap-2 w-full sm:w-auto items-center">
                    
                    <!-- Voice Cast Selector (Explainer Mode Only) -->
                    @if (!isFrequency()) {
                      <label for="styleSelect" class="sr-only">Voice Persona</label>
                      <select id="styleSelect" formControlName="style" class="app-input px-2.5 py-1.5 text-xs text-[#BDC1C6] bg-[#18191B] border border-[#3C4043] rounded-md cursor-pointer">
                        <option value="family_guy">Voice: Family Guy Cast (Peter, Brian, Stewie)</option>
                        <option value="rick_morty">Voice: Rick & Morty</option>
                        <option value="south_park">Voice: South Park</option>
                        <option value="documentary">Voice: Cinematic Documentary</option>
                        <option value="pixel_art">Voice: Pixel Art Narrator</option>
                      </select>
                    } @else {
                      <div class="px-2.5 py-1 rounded-full text-[11px] font-mono text-[#BDC1C6] bg-[#131314] border border-[#2E3135]">
                        Lissajous Vectorscope + Waveform
                      </div>
                    }

                    <!-- Aspect Ratio Selector -->
                    <label for="aspectRatioSelect" class="sr-only">Aspect Ratio</label>
                    <select id="aspectRatioSelect" formControlName="aspectRatio" class="app-input px-2.5 py-1.5 text-xs text-[#BDC1C6] bg-[#18191B] border border-[#3C4043] rounded-md cursor-pointer">
                      <option value="9:16">9:16 Vertical (Shorts/Reels)</option>
                      <option value="16:9">16:9 Landscape (YouTube)</option>
                      <option value="1:1">1:1 Square (Feed)</option>
                    </select>

                    <span class="px-2 py-0.5 rounded-full text-[10px] font-mono text-[#80868B] bg-[#131314] border border-[#2E3135] hidden sm:inline-block">
                      1080p Master
                    </span>
                  </div>

                  <!-- Generate Action Button -->
                  <button type="submit" 
                          [disabled]="chatForm.invalid || isProcessing()" 
                          class="btn-primary w-full sm:w-auto px-4 py-2 text-xs flex items-center justify-center gap-1.5 focus-visible:ring-2 focus-visible:ring-[#D97757]">
                    @if (isProcessing()) {
                      <svg class="animate-spin h-3.5 w-3.5 text-[#FAF8F5]" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      <span>Synthesizing...</span>
                    } @else {
                      <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <span>{{ isFrequency() ? 'Synthesize Frequency Video' : 'Generate Video Short' }}</span>
                    }
                  </button>
                </div>
              </form>
            </div>

            <!-- Featured Configurations (Restrained Product Layout) -->
            <div class="space-y-2 pt-1">
              <span class="text-[11px] font-medium text-[#80868B] uppercase tracking-wider block">
                Featured Configurations
              </span>
              <div class="grid grid-cols-1 sm:grid-cols-3 gap-2.5">
                
                <button type="button" 
                        (click)="quickStartFrequency('432 Hz carrier with 10 Hz Alpha binaural beat for deep coding flow state')" 
                        class="p-3.5 rounded-lg bg-[#1E1F20] border border-[#2E3135] hover:border-[#5F6368] text-left transition-colors focus-visible:ring-1 focus-visible:ring-[#D97757]">
                  <div class="font-medium text-xs text-[#F1F3F4]">Alpha Flow (432Hz)</div>
                  <div class="text-[11px] text-[#80868B] mt-0.5 line-clamp-1">432Hz carrier with 10Hz Alpha beat for calm focus</div>
                </button>

                <button type="button" 
                        (click)="quickStartFrequency('40 Hz Gamma binaural beat with 528 Hz harmonic carrier for peak cognitive focus')" 
                        class="p-3.5 rounded-lg bg-[#1E1F20] border border-[#2E3135] hover:border-[#5F6368] text-left transition-colors focus-visible:ring-1 focus-visible:ring-[#D97757]">
                  <div class="font-medium text-xs text-[#F1F3F4]">Gamma Focus (40Hz)</div>
                  <div class="text-[11px] text-[#80868B] mt-0.5 line-clamp-1">40Hz Gamma beat with 528Hz carrier for study</div>
                </button>

                <button type="button" 
                        (click)="quickStartShort('How Black Holes warp space-time and create event horizons')" 
                        class="p-3.5 rounded-lg bg-[#1E1F20] border border-[#2E3135] hover:border-[#5F6368] text-left transition-colors focus-visible:ring-1 focus-visible:ring-[#D97757]">
                  <div class="font-medium text-xs text-[#F1F3F4]">Explainer: Astrophysics</div>
                  <div class="text-[11px] text-[#80868B] mt-0.5 line-clamp-1">How Black Holes warp space-time & event horizons</div>
                </button>

              </div>
            </div>

          </div>
        </div>
      </main>
    </div>
  `
})
export class DashboardComponent {
  public api = inject(ApiService);
  public router = inject(Router);
  public themeService = inject(ThemeService);
  private fb = inject(FormBuilder);

  isProcessing = signal(false);
  sidebarOpen = signal(false);

  chatForm = this.fb.group({
    prompt: ['', Validators.required],
    category: ['frequency_generator'],
    style: ['family_guy'],
    aspectRatio: ['9:16'],
    duration: ['short']
  });

  frequencyChips: FrequencyChip[] = [
    { label: '432 Hz', sub: 'Harmonic', prompt: '432 Hz pure harmonic tone with 10 Hz Alpha beat for calm focus' },
    { label: '528 Hz', sub: 'Clarity', prompt: '528 Hz harmonic frequency with 10 Hz Alpha flow state' },
    { label: 'Alpha 10Hz', sub: 'Flow State', prompt: 'Alpha brainwave entrainment (10 Hz) with 432 Hz carrier for deep flow' },
    { label: 'Theta 6Hz', sub: 'Meditation', prompt: 'Theta wave meditation beat (6 Hz) with 528 Hz carrier for mindfulness' },
    { label: 'Delta 2.5Hz', sub: 'Rest', prompt: 'Delta frequency (2.5 Hz) with 108 Hz carrier for deep restorative sleep' },
    { label: 'Gamma 40Hz', sub: 'Peak Focus', prompt: '40 Hz Gamma binaural beat for intense study and peak cognition' },
    { label: 'Schumann 7.83Hz', sub: 'Earth Resonance', prompt: 'Schumann resonance (7.83 Hz) with 432 Hz harmonic carrier' },
  ];

  isFrequency(): boolean {
    return this.chatForm.get('category')?.value === 'frequency_generator';
  }

  getPlaceholderText(): string {
    return this.isFrequency()
      ? "Enter carrier frequency and beat (e.g. '432 Hz carrier tone with 10 Hz Alpha binaural beat for deep coding flow')..."
      : "Enter topic (e.g. 'How Einstein and Bohr debated quantum entanglement and action at a distance')...";
  }

  setCategory(category: 'explainer_shorts' | 'frequency_generator') {
    this.chatForm.patchValue({ category });
  }

  applyFrequencyChip(chip: FrequencyChip) {
    this.chatForm.patchValue({ prompt: chip.prompt });
  }

  quickStartFrequency(prompt: string) {
    this.chatForm.patchValue({ 
      category: 'frequency_generator',
      prompt 
    });
    this.startChat();
  }

  quickStartShort(prompt: string) {
    this.chatForm.patchValue({ 
      category: 'explainer_shorts',
      prompt 
    });
    this.startChat();
  }

  async startChat() {
    if (this.chatForm.invalid || this.isProcessing()) return;

    this.isProcessing.set(true);
    const { prompt, category, style, aspectRatio, duration } = this.chatForm.value;
    
    let generatorId = 'family_guy';
    if (category === 'explainer_shorts') {
      generatorId = style || 'family_guy';
    } else if (category === 'frequency_generator') {
      generatorId = 'frequency';
    }

    try {
      const project = await this.api.createProject({ 
        name: (prompt || 'New Video').substring(0, 50),
        description: prompt || ''
      });
      
      this.api.generateVideo({
        project_id: project._id,
        generator_id: generatorId,
        topic: prompt!,
        aspect_ratio: aspectRatio!,
        duration: duration!,
        output_format: 'mp4',
        quality: '1080p'
      }).catch(err => console.error('Video generation error:', err));
      
      await this.router.navigate(['/projects', project._id]);
    } catch (err) {
      console.error(err);
      alert('Failed to start project');
    } finally {
      this.isProcessing.set(false);
    }
  }
}