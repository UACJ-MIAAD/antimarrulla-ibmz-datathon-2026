# 🎯 Criterios de evaluación y cómo exprimirlos

> Fuente: *Participant Guidebook – IBM Z Datathon 2026*, sección "Judging Evaluation Criteria and Standardized Scoring Rubric". Jueces: principalmente expertos y líderes de IBM, con rúbrica estandarizada global.

## Rúbrica estándar · 40 pts

**4 criterios × 10 puntos.** Cada uno se califica en 4 niveles: 0–3 *Developing*, 4–6 *Proficient*, 7–8 *Advanced*, 9–10 *Exceptional*.

| # | Criterio | Pts | Dueño interno |
|---|----------|----:|---------------|
| 1 | Valor para la comunidad y alineación con el tema | 10 | Javier + todos |
| 2 | Novedad y originalidad de la idea | 10 | Todo el equipo |
| 3 | Diseño técnico y uso de LinuxONE Community Cloud + paquetes open source de IA/ML | 10 | Carlos (LinuxONE) + Álvaro (modelado) + Yazmin (datos) |
| 4 | Ejecución y entrega / calidad del pitch (video) | 10 | Javier (pitch) + Yazmin (demo) |
| | **Total** | **40** | |

> **Antes de construir:** la guía marca como **prerrequisito obligatorio** completar los **dos labs de IA/ML** que da la organización (*Predictive AI Hybrid AI scenarios (multi-model)* y *Predictive AI + Generative AI*). Se hacen al arranque, antes de escribir nuestro código.

---

## 1. Valor para la comunidad y alineación con el tema · 10 pts

**Preguntas que se hace el juez:** ¿qué problema real resuelven?, ¿quién se beneficia?, ¿qué tan claro se ve el tema elegido en la idea y en la ejecución?

| Nivel | Qué lo distingue |
|-------|------------------|
| 9–10 | Solución de impacto a una necesidad crítica, "Tech for Good", tema integrado sin costuras |
| 7–8 | Problema real con beneficios claros y fuerte alineación al tema |
| 4–6 | Atiende una necesidad pero el tema se nota poco o el beneficio es difuso |

Estrategias:
- Nombrar a la **persona beneficiada** y la comunidad concreta (pacientes con diabetes en México, familias que reciben remesas en Juárez, personas vulnerables).
- Respaldar el problema con **datos con fuente** (el video lo exige: "data to support the problem").
- Decir explícitamente el tema: "Esto es *AI Secured* porque…" y que el diseño lo demuestre (los datos sensibles nunca se exponen).
- Todo bajo el lema oficial **AI for Good**.

## 2. Novedad y originalidad · 10 pts

**Requisitos del criterio:** ideas nuevas, **construido por completo durante el datathon**, **código creado desde cero en la ventana del evento**.

| Nivel | Qué lo distingue |
|-------|------------------|
| 9–10 | Muy innovador, gran originalidad, componentes de punta a punta |
| 7–8 | Concepto único e innovador |
| 4–6 | Esfuerzo creativo pero idea común o predecible |

Estrategias:
- Evitar el "detector de fraude genérico": darle un giro local y una privacidad medible.
- Historial de commits frecuente del 17–18 oct como evidencia de que todo nació en el evento.
- Solución **de punta a punta** (datos → modelo en LinuxONE → demo), no un notebook suelto.

## 3. Diseño técnico y uso de LinuxONE + IA/ML · 10 pts

**Qué revisan:** solidez de la arquitectura; IA/ML **corriendo en LinuxONE Community Cloud**; uso de paquetes open source de IA/ML; aprovechamiento de capacidades de la plataforma (**contenedores, seguridad, escalabilidad y cómputo**) **con capturas de pantalla como evidencia**.

| Nivel | Qué lo distingue |
|-------|------------------|
| 9–10 | Arquitectura avanzada, explota a fondo la plataforma y la IA/ML en LinuxONE; aprovecha al máximo seguridad y/o cómputo |
| 7–8 | Arquitectura fuerte, uso sólido de LinuxONE y de paquetes de IA/ML en LinuxONE |
| 4–6 | Arquitectura básica; usa LinuxONE pero con poca IA/ML corriendo ahí |
| 0–3 | Uso mínimo o nulo de LinuxONE |

Estrategias:
- **Entrenar e inferir en la VM de LinuxONE** (Jupyter Lab ML de la Community Cloud), no en la laptop.
- Inspirarse en los labs: un enfoque **híbrido multi-modelo** o **predictivo + generativo** puntúa naturalmente aquí.
- Contenerizar el servicio (Podman/Docker) y mostrarlo.
- Seguridad: cifrado de datos, llaves fuera del código, acceso mínimo. Es el corazón del Tema 2.
- **Carpeta de evidencias** `submission/evidencias/` con capturas: VM corriendo, `uname -m` → `s390x`, entrenamiento, contenedor, métricas, uso de recursos.
- Diagrama de arquitectura (flowchart opcional pero recomendado en la entrega).

## 4. Ejecución, entrega y calidad del pitch · 10 pts

**Qué revisan en el video:** calidad y efectividad de la presentación, claridad, pitch convincente, **demo incluida**, ejecución del equipo y **respetar el límite de tiempo (máx. 3 min)**.

| Nivel | Qué lo distingue |
|-------|------------------|
| 9–10 | Presentación muy profesional y orquestada, pitch excelente, demo convincente |
| 7–8 | Entrega clara y profesional, demo sólida, buen pitch |
| 4–6 | Funciona, pero la demo o la comunicación están sin pulir |

Estrategias:
- Guion en [submission/PITCH.md](../submission/PITCH.md) cubriendo lo que pide la guía: problema, datos que lo respaldan, solución, **cómo usa IBM Z** (stack, **instancia LinuxONE y modelo en pantalla**).
- Ensayar con cronómetro: **2:50** como meta. Pasarse de 3:00 cuesta puntos.
- Audio limpio y ritmo; mostrar, no contar.

---

## 🏅 AI Innovation Excellence Awards (rúbrica adicional · 20 pts)

Premio aparte para proyectos con puntaje alto, sobre todo en **Novedad** y **Diseño técnico en LinuxONE**. No necesariamente lo gana el primer lugar regional.

| Criterio | Pts | Nivel máximo |
|----------|----:|--------------|
| Innovación y originalidad de la IA | 10 | Uso de IA verdaderamente novedoso y poco convencional que distingue al proyecto |
| Impacto transformador y excelencia técnica | 10 | Solución de punta a punta, sofisticada en LinuxONE, escalable y con impacto real |

Traducción antimarrulla: si la IA es atrevida **y** corre de verdad en LinuxONE, competimos por dos premios a la vez.

## ✅ Autoevaluación (llenar en la hora 21)

| Criterio | Máx | Nuestra estimación | Qué falta para subir |
|----------|----:|-------------------:|----------------------|
| Valor comunitario y tema | 10 | | |
| Novedad y originalidad | 10 | | |
| Diseño técnico y LinuxONE | 10 | | |
| Ejecución y pitch | 10 | | |
| **Total** | **40** | | |
