import os
import struct
import sys
import wave

# WAV files are produced by the runtime's "audio_wav" debug-server command
# (tap 0=spu_out, 1=cd_in, 2=host) — see runtime/include/audio_trace.h.
base = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "build-release")
for name in ("fmv_xa.wav", "fmv_spu.wav", "fmv_host.wav"):
    path = os.path.join(base, name)
    with wave.open(path, "rb") as wav:
        frames = wav.getnframes()
        rate = wav.getframerate()
        pcm = struct.unpack("<" + "h" * (frames * 2), wav.readframes(frames))
    diffs = [abs(pcm[i] - pcm[i - 2]) for i in range(2, len(pcm))]
    zero_frames = sum(pcm[i] == 0 and pcm[i + 1] == 0
                      for i in range(0, len(pcm), 2))
    print(name, "frames", frames, "seconds", round(frames / rate, 2),
          "maxdiff", max(diffs), "diff>12000", sum(x > 12000 for x in diffs),
          "zero_frames", zero_frames)
