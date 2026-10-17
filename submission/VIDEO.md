# Video editing and recording

**Final video pending:** the English 170-second silent editing draft is not a completed submission. Authorized English narration and actual LinuxONE/model footage must still be recorded. Run `make video-draft` to generate `dist/video/silent_edit_draft.mp4` without audio. A clear English placeholder occupies the missing VM segment.

| Segment | Time | Draft image | Final recording | Voice |
|---------|------|-------------|-----------------|-------|
| 1 | 0:00–0:10 | Slide 1 | Introduction | Yazmin |
| 2 | 0:10–0:35 | Slide 2 | Problem | Yazmin |
| 3 | 0:35–0:55 | Slide 3 | Solution | Carlos |
| 4 | 0:55–1:20 | Slide 4 | Encryption | Carlos |
| 5 | 1:20–1:35 | Slide 5 | Architecture | Álvaro |
| 5b | 1:35–1:50 | English pending-footage marker | Actual VM: provider identity, `uname -m`, Compose containers and loaded model (`/api/state`) | Álvaro |
| 6 | 1:50–2:00 | Slide 6 | Results | Javier |
| 6b | 2:00–2:25 | Local English UI screenshot | English UI recorded through the LinuxONE SSH tunnel, synthetic profile C | Javier |
| 7 | 2:25–2:33 | Slide 7 | Data/model | Yazmin |
| 8 | 2:33–2:50 | Slide 8 | Close | Yazmin |

- [ ] Record 5b/6b on LinuxONE without credentials visible; replace the placeholder/local capture
- [ ] Record authorized English voices using [PITCH.md](PITCH.md)
- [ ] Review synchronization, legibility and audio
- [ ] Verify final duration with `ffprobe`, at most 180 seconds
- [ ] Publish and test the URL without a login
- [ ] Add the same URL to [HACK2SKILL.md](HACK2SKILL.md) and `submission/VIDEO_RECORD.json`, using `VIDEO_RECORD.example.json`

The silent draft has no consent or voice claims. Do not check “final video” until the actual narrated recording and access check exist.
