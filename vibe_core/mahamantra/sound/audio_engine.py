"""
AUDIO ENGINE - The Sound of the Chamber
=======================================

"Sabda-Brahma" - Transcendental Sound

Generates 16-bit PCM Audio Frames (432Hz Fundamental) based on the Divine Instruction Word (DIW).
Pure Python. No external dependencies.

MAPPING:
    - Pitch: VENU (6 bits) -> Scale degrees relative to 432Hz.
    - Timbre: VAMSI (9 bits) -> Waveform mixing (Sine/Saw/Square).
    - Rhythm: MURALI (4 bits) -> Envelope / Gate length.
"""

import math
import struct
from typing import Iterator

from vibe_core.mahamantra.protocols._seed import JIVA_CYCLE  # 432
from vibe_core.mahamantra.protocols.diw import CLUSTER_SHIFT

# Audio Constants
SAMPLE_RATE = 44100
FRAME_SIZE = 256  # Samples per control tick (Control Rate ~ 172Hz)
                  # 44100 / 256 = 172.2 Hz
BIT_DEPTH = 32767 # 16-bit signed

class PranaSoundEngine:
    """
    Stateful audio synthesizer.
    Receives DIW, emits PCM bytes.
    """
    
    def __init__(self):
        self.phase = 0.0
        self.current_diw = 0
        
        # LUT for Sine Wave (Fast lookup)
        self.sine_lut = [math.sin(2 * math.pi * i / 1024) for i in range(1024)]
        
    def _get_frequency(self, venu: int) -> float:
        """
        Map VENU (0-63) to Frequency.
        Root = 432Hz.
        Scale = Chromatic for now.
        """
        # Center around 432Hz (VENU=32)
        # Formula: f = 432 * 2^((venu - 32) / 12.0)
        return JIVA_CYCLE * (2 ** ((venu - 32) / 12.0))

    def synthesize(self, diw: int, num_frames: int = 1) -> bytes:
        """
        Generate PCM audio for the given DIW.
        
        Args:
            diw: 19-bit Divine Instruction Word (plus velocity/cluster)
            num_frames: How many control frames to generate
            
        Returns:
            bytes: Raw 16-bit LE PCM data
        """
        from vibe_core.mahamantra.protocols.diw import unpack as diw_unpack

        # 1. Decode DIW (canonical 6-9-4 format)
        components = diw_unpack(diw)
        venu = components.venu
        vamsi = components.vamsi
        
        # 2. Parameters
        freq = self._get_frequency(venu)
        
        # Vamsi controls timbre (Mix between Sine and "Fold")
        timbre = (vamsi / 512.0) 
        
        # 3. Generate Samples
        output = bytearray()
        
        samples_to_gen = num_frames * FRAME_SIZE
        phase_inc = (freq * 1024) / SAMPLE_RATE # 1024 is LUT size
        
        for _ in range(samples_to_gen):
            # Oscillator
            idx = int(self.phase) % 1024
            sine_val = self.sine_lut[idx]
            
            # Simple Fold/Distortion based on Timbre
            if timbre > 0.5:
                # Add some odd harmonics
                val = sine_val + (timbre - 0.5) * (1.0 if sine_val > 0 else -1.0)
            else:
                val = sine_val
            
            # Clip
            val = max(-1.0, min(1.0, val))
            
            # Scale to 16-bit
            pcm_val = int(val * BIT_DEPTH)
            output.extend(struct.pack("<h", pcm_val))
            
            self.phase += phase_inc
            
        return bytes(output)

    def stream(self, chamber) -> Iterator[bytes]:
        """
        Generator for continuous streaming.
        
        Args:
            chamber: Active SankirtanChamber
            
        Yields:
            chunks of PCM bytes

        GUARD: Reads the current DIW from the orchestrator's last state
        instead of calling step(). Singularity.tick() is the ONLY driver.
        AudioEngine is a consumer, not a driver.
        """
        orch = chamber._orchestrator
        while True:
            # Read current DIW — NEVER drive the orchestrator.
            # Singularity.tick() is the one path to the flute.
            diw = orch._prev_state | (orch._mode << CLUSTER_SHIFT)
            
            # Synthesize Audio Frame
            audio_chunk = self.synthesize(diw, num_frames=1)
            yield audio_chunk
