"""Arma un BORRADOR del video (sin audio) con los tiempos del guion, para ensayar y montar la voz encima.

No es el video final: le faltan las voces y la captura real de LinuxONE (va un marcador amarillo en su lugar).
Salida: dist/video/borrador_montaje_sin_audio.mp4 (no se versiona). Requiere ffmpeg.

Uso: python -m tamizaje.video_borrador
"""
import json, os, subprocess, tempfile
from .rutas import RAIZ

# (imagen, segundos, segmento del guion) — mismos tiempos que submission/PITCH.md (total 170 s)
GUION = [
    ("site/assets/slides/s-1.jpg", 10, "1 · Portada"),
    ("site/assets/slides/s-2.jpg", 25, "2 · El problema"),
    ("site/assets/slides/s-3.jpg", 20, "3 · La solución"),
    ("site/assets/slides/s-4.jpg", 25, "4 · Cifrado homomórfico"),
    ("site/assets/slides/s-5.jpg", 15, "5 · Por qué IBM Z"),
    ("submission/video/marcador_linuxone.png", 15, "5 · Pantalla de LinuxONE (PENDIENTE: grabar en la VM)"),
    ("site/assets/slides/s-6.jpg", 10, "6 · Demo"),
    ("submission/evidencias/local/local-docker-aarch64_ui_pantalla_dividida_C.png", 25, "6 · Demo real (reemplazar por grabación en LinuxONE)"),
    ("site/assets/slides/s-7.jpg", 8, "7 · Datos y modelo"),
    ("site/assets/slides/s-8.jpg", 17, "8 · Impacto y cierre"),
]


def main():
    salida_dir = os.path.join(RAIZ, "dist", "video"); os.makedirs(salida_dir, exist_ok=True)
    salida = os.path.join(salida_dir, "borrador_montaje_sin_audio.mp4")
    filtro = "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2:color=0x0e0e13,fps=25,format=yuv420p"
    tmp = tempfile.mkdtemp(prefix="tamizaje-video-")
    clips = []
    for k, (img, seg, _) in enumerate(GUION):
        clip = os.path.join(tmp, f"{k:02d}.mp4")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-t", str(seg), "-i", os.path.join(RAIZ, img), "-vf", filtro,
                        "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", clip], check=True)
        clips.append(clip)
    lista = os.path.join(tmp, "lista.txt")
    with open(lista, "w") as f:
        f.writelines(f"file '{c}'\n" for c in clips)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lista, "-c", "copy", "-movflags", "+faststart", salida], check=True)
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", salida], capture_output=True, text=True, check=True).stdout
    dur = float(json.loads(out)["format"]["duration"])
    assert dur <= 180, f"el borrador dura {dur:.1f} s (> 180)"
    print(f"borrador: {os.path.relpath(salida, RAIZ)} · {dur:.1f} s · sin audio · con marcador de LinuxONE pendiente")


if __name__ == "__main__":
    main()
