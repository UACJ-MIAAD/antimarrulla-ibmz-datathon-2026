"""Assemble a SILENT DRAFT video using the script timings.
The final video still requires authorized English narration and real LinuxONE footage.
A clearly labeled placeholder occupies the missing VM segment. Output:
dist/video/silent_edit_draft.mp4 (untracked). Requires ffmpeg.
Run: python -m screening.video_draft
"""
import json, os, subprocess, tempfile
from .paths import ROOT

# (image, seconds, script segment), matching submission/PITCH.md: 170 seconds total
SCRIPT = [
    ("site/assets/slides/s-1.jpg", 10, "1 · Cover"),
    ("site/assets/slides/s-2.jpg", 25, "2 · The problem"),
    ("site/assets/slides/s-3.jpg", 20, "3 · The solution"),
    ("site/assets/slides/s-4.jpg", 25, "4 · Homomorphic encryption"),
    ("site/assets/slides/s-5.jpg", 15, "5 · Why IBM Z"),
    ("submission/video/linuxone_placeholder.png", 15, "5 · LinuxONE screen (PENDING: record on the VM)"),
    ("site/assets/slides/s-6.jpg", 10, "6 · Demo"),
    ("submission/evidence/local/english_demo_synthetic_C.png", 25, "6 · Actual demo (replace with LinuxONE recording)"),
    ("site/assets/slides/s-7.jpg", 8, "7 · Data and model"),
    ("site/assets/slides/s-8.jpg", 17, "8 · Impact and closing"),
]


def main():
    output_dir = os.path.join(ROOT, "dist", "video"); os.makedirs(output_dir, exist_ok=True)
    output = os.path.join(output_dir, "silent_edit_draft.mp4")
    selection = "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2:color=0x0e0e13,fps=25,format=yuv420p"
    tmp = tempfile.mkdtemp(prefix="screening-video-")
    clips = []
    for k, (img, seg, _) in enumerate(SCRIPT):
        clip = os.path.join(tmp, f"{k:02d}.mp4")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-t", str(seg), "-i", os.path.join(ROOT, img), "-vf", selection,
                        "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", clip], check=True)
        clips.append(clip)
    items = os.path.join(tmp, "clips.txt")
    with open(items, "w") as f:
        f.writelines(f"file '{c}'\n" for c in clips)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", items, "-c", "copy", "-movflags", "+faststart", output], check=True)
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", output], capture_output=True, text=True, check=True).stdout
    dur = float(json.loads(out)["format"]["duration"])
    assert dur <= 180, f"draft duration: {dur:.1f} s (> 180)"
    print(f"draft: {os.path.relpath(output, ROOT)} · {dur:.1f} s · silent · LinuxONE footage pending")


if __name__ == "__main__":
    main()
