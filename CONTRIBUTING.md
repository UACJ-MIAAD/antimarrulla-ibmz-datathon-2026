# 🤝 Guía de contribución · Los Antimarrulla

Reglas cortas para que 24 horas de trabajo no terminen en 24 horas de conflictos de merge.

## 1. Ramas

- `main` siempre debe correr. Nadie hace push directo a `main`.
- Una rama por integrante o por feature:

| Tipo | Ejemplo |
|------|---------|
| Por integrante | `javier/coordinacion`, `yazmin/datos` |
| Por feature | `feat/modelo-base`, `feat/demo-ui`, `infra/linuxone-setup` |
| Corrección urgente | `fix/demo-crash` |

```bash
git checkout main && git pull
git checkout -b feat/modelo-base
```

## 2. Pull requests

- Todo cambio entra a `main` por **pull request**.
- **Revisión obligatoria de otro miembro** (no tú mismo). Revisar = leer, correr y entender.
- PR pequeño > PR gigante. Si tu PR toca más de ~300 líneas, pártelo.
- Título del PR con el mismo formato que los commits.
- A partir de la **hora 20**, solo entran PRs de corrección, documentación y pitch. Nada de features nuevas.

## 3. Commits

En español, formato **`tipo: descripción`**, en minúsculas y en presente:

| Tipo | Uso | Ejemplo |
|------|-----|---------|
| `datos` | Carga, limpieza, transformación de datos | `datos: limpieza inicial del dataset` |
| `modelo` | Entrenamiento, evaluación, métricas | `modelo: baseline de regresión logística` |
| `infra` | LinuxONE, despliegue, entorno, cifrado | `infra: configura entorno python en linuxone` |
| `demo` | Interfaz y demo en vivo | `demo: pantalla dividida cifrado vs predicción` |
| `docs` | README, docs/, comentarios | `docs: registra decisión de la idea` |
| `pitch` | Slides, guion, video | `pitch: primer borrador del guion` |
| `fix` | Corrección de errores | `fix: maneja valores nulos en edad` |
| `chore` | Mantenimiento, dependencias | `chore: agrega tenseal a requirements` |

Commits frecuentes y pequeños. Un commit cada 30–60 min de trabajo es buena señal para los jueces.

## 4. ⚠️ Fechas del historial

**Todo commit de código debe ser del 17–18 de octubre de 2026.** El historial de commits es la evidencia de que construimos durante el evento.

- No reescribas historia (`git rebase` sobre `main`, `git push --force`) después de que algo se publicó.
- No traigas código de proyectos anteriores. Ideas e investigación sí; código no.
- Antes de commitear revisa que tu reloj del sistema esté bien.

## 5. Datos y secretos

- Nada de datasets grandes ni datos sensibles en el repo. Ver [data/README.md](data/README.md).
- Credenciales, llaves y tokens viven en `.env` (ignorado por git). **Nunca** en el código.
- Si subiste un secreto por error: avisa en el canal, rota la llave y luego limpia.

## 6. Ritmo del equipo

| Momento | Qué pasa |
|---------|----------|
| Hora 0–1 | Reunión de decisión de idea → [docs/DECISION.md](docs/DECISION.md) |
| Cada 4 h | Stand-up de 10 min: qué hice, qué sigue, qué me bloquea |
| **Hora 18** | **Deadline interno: demo funcional de punta a punta** |
| Hora 20 | Congelamiento de features |
| Hora 22–24 | Video, slides, checklist y entrega |

Bloqueado más de 30 minutos = pedir ayuda. Aquí no hay marrulla, hay equipo.
