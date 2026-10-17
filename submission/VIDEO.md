# 🎬 Video (máx. 3 min) · montaje

> **Estado:** hay un **borrador sin audio** de 170 s (`make video-borrador` → `dist/video/borrador_montaje_sin_audio.mp4`, no se versiona) con los tiempos del [guion](PITCH.md). **El video final no está hecho**: faltan las voces del equipo y la grabación real en LinuxONE (en el borrador hay un marcador amarillo en su lugar).

## Storyboard (170 s)

| # | Tiempo | Imagen en el borrador | Qué grabar para el final | Voz |
|---|-------:|-----------------------|--------------------------|-----|
| 1 | 0:00–0:10 | Slide 1 | — | Yazmin |
| 2 | 0:10–0:35 | Slide 2 | — | Yazmin |
| 3 | 0:35–0:55 | Slide 3 | — | Carlos |
| 4 | 0:55–1:20 | Slide 4 | — | Carlos |
| 5 | 1:20–1:35 | Slide 5 | — | Álvaro |
| 5b | 1:35–1:50 | **Marcador** | Terminal en la VM: `uname -m` → `s390x`, `docker compose -f docker/compose.yml ps`, modelo cargado (`/api/estado`) | Álvaro |
| 6 | 1:50–2:00 | Slide 6 | — | Javier |
| 6b | 2:00–2:25 | Captura local de la UI | Grabación de la UI por el túnel SSH a LinuxONE con el paciente sintético C | Javier |
| 7 | 2:25–2:33 | Slide 7 | — | Yazmin |
| 8 | 2:33–2:50 | Slide 8 | — | Yazmin |

## Para cerrar el video

- [ ] Grabar 5b y 6b en LinuxONE (sin tokens ni contraseñas en pantalla) y reemplazar el marcador y la captura local.
- [ ] Grabar las voces con el guion de [PITCH.md](PITCH.md) y montarlas sobre el borrador.
- [ ] Medir la duración del archivo final (≤ 3:00) con `ffprobe`; revisar audio y legibilidad.
- [ ] Subirlo y probar el link en una ventana de incógnito.
- [ ] Anotar el link en [HACK2SKILL.md](HACK2SKILL.md).
