import { Component, input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-agent-pipeline',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="p-4 rounded-lg bg-[#1E1F20] border border-[#2E3135] shadow-sm space-y-4"
         role="status" 
         aria-live="polite"
         [attr.aria-label]="isFrequency() ? 'Acoustic Frequency Synthesis Pipeline' : 'Multi-Agent Video Generation Pipeline'">
      
      <!-- Header: Title, Telemetry, and Percentage -->
      <div class="flex items-center justify-between pb-3 border-b border-[#2E3135]">
        <div class="flex items-center gap-2">
          <span class="w-2 h-2 rounded-full bg-[#D97757]"></span>
          <div>
            <h3 class="font-medium text-xs text-[#F1F3F4] uppercase tracking-wider">
              {{ isFrequency() ? 'Acoustic DSP Synthesis Pipeline' : 'Multi-Agent Synthesis Pipeline' }}
            </h3>
            <p class="text-[11px] text-[#80868B]">
              {{ isFrequency() ? 'Mathematical stereo phase alignment & Lissajous vectorscope' : 'Orchestrated script, voice cloning, and compositing workers' }}
            </p>
          </div>
        </div>

        <div class="flex items-center gap-2.5">
          <span class="text-xs font-mono font-semibold text-[#F1F3F4]">
            {{ progress() }}%
          </span>
          <span class="px-2 py-0.5 rounded-full text-[10px] font-mono bg-[#282A2D] text-[#BDC1C6] border border-[#3C4043]">
            SSE Stream
          </span>
        </div>
      </div>

      <!-- 4-Stage Stepper Grid -->
      <div class="grid grid-cols-2 md:grid-cols-4 gap-2" role="list">
        
        @if (!isFrequency()) {
          <!-- ================= EXPLAINER SHORTS STEPS ================= -->
          
          <!-- Step 1: Script Synthesis -->
          <div class="p-2.5 rounded-md border text-left transition-colors"
               role="listitem"
               [class.bg-[#131314]]="currentPhase() < 1"
               [class.border-[#2E3135]]="currentPhase() < 1"
               [class.stage-active]="currentPhase() === 1"
               [class.bg-[#282A2D]]="currentPhase() > 1"
               [class.border-[#3C4043]]="currentPhase() > 1">
            <div class="flex items-center justify-between mb-1">
              <span class="text-[10px] font-mono font-semibold text-[#80868B]">01</span>
              @if (currentPhase() > 1) {
                <svg class="w-3.5 h-3.5 text-[#81C995]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7"/>
                </svg>
              } @else if (currentPhase() === 1) {
                <svg class="w-3 h-3 text-[#D97757] animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
                </svg>
              }
            </div>
            <div class="font-medium text-xs text-[#F1F3F4]">Script Engine</div>
            <p class="text-[10px] text-[#80868B] mt-0.5">
              {{ currentPhase() > 1 ? 'Dialogue complete' : (currentPhase() === 1 ? 'Writing narrative...' : 'Queued') }}
            </p>
          </div>

          <!-- Step 2: Voice Cloner -->
          <div class="p-2.5 rounded-md border text-left transition-colors"
               role="listitem"
               [class.bg-[#131314]]="currentPhase() < 2"
               [class.border-[#2E3135]]="currentPhase() < 2"
               [class.stage-active]="currentPhase() === 2"
               [class.bg-[#282A2D]]="currentPhase() > 2"
               [class.border-[#3C4043]]="currentPhase() > 2">
            <div class="flex items-center justify-between mb-1">
              <span class="text-[10px] font-mono font-semibold text-[#80868B]">02</span>
              @if (currentPhase() > 2) {
                <svg class="w-3.5 h-3.5 text-[#81C995]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7"/>
                </svg>
              } @else if (currentPhase() === 2) {
                <svg class="w-3 h-3 text-[#D97757] animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
                </svg>
              }
            </div>
            <div class="font-medium text-xs text-[#F1F3F4]">Voice Cloning</div>
            <p class="text-[10px] text-[#80868B] mt-0.5">
              {{ currentPhase() > 2 ? 'Audio synthesized' : (currentPhase() === 2 ? 'Cloning voices (:8004)...' : 'Queued') }}
            </p>
          </div>

          <!-- Step 3: Visual Director -->
          <div class="p-2.5 rounded-md border text-left transition-colors"
               role="listitem"
               [class.bg-[#131314]]="currentPhase() < 3"
               [class.border-[#2E3135]]="currentPhase() < 3"
               [class.stage-active]="currentPhase() === 3"
               [class.bg-[#282A2D]]="currentPhase() > 3"
               [class.border-[#3C4043]]="currentPhase() > 3">
            <div class="flex items-center justify-between mb-1">
              <span class="text-[10px] font-mono font-semibold text-[#80868B]">03</span>
              @if (currentPhase() > 3) {
                <svg class="w-3.5 h-3.5 text-[#81C995]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7"/>
                </svg>
              } @else if (currentPhase() === 3) {
                <svg class="w-3 h-3 text-[#D97757] animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
                </svg>
              }
            </div>
            <div class="font-medium text-xs text-[#F1F3F4]">Scene Director</div>
            <p class="text-[10px] text-[#80868B] mt-0.5">
              {{ currentPhase() > 3 ? 'Timing aligned' : (currentPhase() === 3 ? 'Composing visual cuts...' : 'Queued') }}
            </p>
          </div>

          <!-- Step 4: Video Compositor -->
          <div class="p-2.5 rounded-md border text-left transition-colors"
               role="listitem"
               [class.bg-[#131314]]="currentPhase() < 4"
               [class.border-[#2E3135]]="currentPhase() < 4"
               [class.stage-active]="currentPhase() >= 4 && progress() < 100"
               [class.bg-[#282A2D]]="progress() >= 100"
               [class.border-[#3C4043]]="progress() >= 100">
            <div class="flex items-center justify-between mb-1">
              <span class="text-[10px] font-mono font-semibold text-[#80868B]">04</span>
              @if (progress() >= 100) {
                <svg class="w-3.5 h-3.5 text-[#81C995]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7"/>
                </svg>
              } @else if (currentPhase() >= 4) {
                <svg class="w-3 h-3 text-[#D97757] animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
                </svg>
              }
            </div>
            <div class="font-medium text-xs text-[#F1F3F4]">FFmpeg Mux</div>
            <p class="text-[10px] text-[#80868B] mt-0.5">
              {{ progress() >= 100 ? '1080p rendered' : (currentPhase() >= 4 ? 'Multiplexing streams...' : 'Queued') }}
            </p>
          </div>

        } @else {
          <!-- ================= FREQUENCY / ACOUSTIC STEPS ================= -->

          <!-- Step 1: Acoustic DSP Analysis -->
          <div class="p-2.5 rounded-md border text-left transition-colors"
               role="listitem"
               [class.bg-[#131314]]="currentPhase() < 1"
               [class.border-[#2E3135]]="currentPhase() < 1"
               [class.stage-active]="currentPhase() === 1"
               [class.bg-[#282A2D]]="currentPhase() > 1"
               [class.border-[#3C4043]]="currentPhase() > 1">
            <div class="flex items-center justify-between mb-1">
              <span class="text-[10px] font-mono font-semibold text-[#80868B]">01</span>
              @if (currentPhase() > 1) {
                <svg class="w-3.5 h-3.5 text-[#81C995]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7"/>
                </svg>
              } @else if (currentPhase() === 1) {
                <svg class="w-3 h-3 text-[#D97757] animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
                </svg>
              }
            </div>
            <div class="font-medium text-xs text-[#F1F3F4]">DSP Parameters</div>
            <p class="text-[10px] text-[#80868B] mt-0.5">
              {{ currentPhase() > 1 ? 'Carrier & beat identified' : (currentPhase() === 1 ? 'Parsing frequencies...' : 'Queued') }}
            </p>
          </div>

          <!-- Step 2: Pure Sine Audio Synthesis -->
          <div class="p-2.5 rounded-md border text-left transition-colors"
               role="listitem"
               [class.bg-[#131314]]="currentPhase() < 2"
               [class.border-[#2E3135]]="currentPhase() < 2"
               [class.stage-active]="currentPhase() === 2"
               [class.bg-[#282A2D]]="currentPhase() > 2"
               [class.border-[#3C4043]]="currentPhase() > 2">
            <div class="flex items-center justify-between mb-1">
              <span class="text-[10px] font-mono font-semibold text-[#80868B]">02</span>
              @if (currentPhase() > 2) {
                <svg class="w-3.5 h-3.5 text-[#81C995]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7"/>
                </svg>
              } @else if (currentPhase() === 2) {
                <svg class="w-3 h-3 text-[#D97757] animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
                </svg>
              }
            </div>
            <div class="font-medium text-xs text-[#F1F3F4]">Audio Synthesis</div>
            <p class="text-[10px] text-[#80868B] mt-0.5">
              {{ currentPhase() > 2 ? 'Stereo wave synthesized' : (currentPhase() === 2 ? 'Binaural synthesis...' : 'Queued') }}
            </p>
          </div>

          <!-- Step 3: Lissajous Cymatics Visualizer -->
          <div class="p-2.5 rounded-md border text-left transition-colors"
               role="listitem"
               [class.bg-[#131314]]="currentPhase() < 3"
               [class.border-[#2E3135]]="currentPhase() < 3"
               [class.stage-active]="currentPhase() === 3"
               [class.bg-[#282A2D]]="currentPhase() > 3"
               [class.border-[#3C4043]]="currentPhase() > 3">
            <div class="flex items-center justify-between mb-1">
              <span class="text-[10px] font-mono font-semibold text-[#80868B]">03</span>
              @if (currentPhase() > 3) {
                <svg class="w-3.5 h-3.5 text-[#81C995]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7"/>
                </svg>
              } @else if (currentPhase() === 3) {
                <svg class="w-3 h-3 text-[#D97757] animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
                </svg>
              }
            </div>
            <div class="font-medium text-xs text-[#F1F3F4]">Phase Visualizer</div>
            <p class="text-[10px] text-[#80868B] mt-0.5">
              {{ currentPhase() > 3 ? 'Lissajous calculated' : (currentPhase() === 3 ? 'Rendering vectorscope...' : 'Queued') }}
            </p>
          </div>

          <!-- Step 4: Lossless Multiplexing -->
          <div class="p-2.5 rounded-md border text-left transition-colors"
               role="listitem"
               [class.bg-[#131314]]="currentPhase() < 4"
               [class.border-[#2E3135]]="currentPhase() < 4"
               [class.stage-active]="currentPhase() >= 4 && progress() < 100"
               [class.bg-[#282A2D]]="progress() >= 100"
               [class.border-[#3C4043]]="progress() >= 100">
            <div class="flex items-center justify-between mb-1">
              <span class="text-[10px] font-mono font-semibold text-[#80868B]">04</span>
              @if (progress() >= 100) {
                <svg class="w-3.5 h-3.5 text-[#81C995]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7"/>
                </svg>
              } @else if (currentPhase() >= 4) {
                <svg class="w-3 h-3 text-[#D97757] animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
                </svg>
              }
            </div>
            <div class="font-medium text-xs text-[#F1F3F4]">Lossless Mux</div>
            <p class="text-[10px] text-[#80868B] mt-0.5">
              {{ progress() >= 100 ? '1080p master ready' : (currentPhase() >= 4 ? 'Encoding 320k AAC...' : 'Queued') }}
            </p>
          </div>

        }

      </div>

      <!-- Linear Solid Progress Bar & Current Status Line -->
      <div class="space-y-1.5 pt-1">
        <div class="w-full bg-[#282A2D] rounded-full h-1.5 overflow-hidden">
          <div class="bg-[#D97757] h-1.5 rounded-full transition-all duration-200"
               [style.width.%]="progress()"></div>
        </div>

        <div class="flex items-center justify-between text-[11px] text-[#80868B]">
          <span class="truncate max-w-[85%] font-medium text-[#BDC1C6]">
            {{ stepText() || (isFrequency() ? 'Synthesizing acoustic frequency master...' : 'Initializing pipeline workers...') }}
          </span>
          <span class="text-[#81C995] text-[10px] font-mono flex items-center gap-1 flex-shrink-0">
            <span class="w-1.5 h-1.5 rounded-full bg-[#81C995]"></span>
            Live
          </span>
        </div>
      </div>

    </div>
  `
})
export class AgentPipelineComponent {
  progress = input<number>(0);
  stepText = input<string>('');
  pipelineType = input<'explainer' | 'frequency'>('explainer');

  isFrequency(): boolean {
    return this.pipelineType() === 'frequency';
  }

  currentPhase(): number {
    const p = this.progress();
    if (p >= 80) return 4;
    if (p >= 50) return 3;
    if (p >= 20) return 2;
    return 1;
  }
}
