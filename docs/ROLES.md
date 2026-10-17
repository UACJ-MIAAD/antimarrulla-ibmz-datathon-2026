# 👥 Roles, responsabilidades y turnos

> Somos **4**, el mínimo de las bases. Nadie es dueño exclusivo de nada; todos revisan PRs de todos.
> El estatus de cada tarea vive en [site/status.json](../site/status.json) y se ve en vivo en https://antimarrulla-tamizaje.netlify.app

**Prioridad vigente:** seguir [PLAN_CIERRE.md](PLAN_CIERRE.md). El calendario de abajo conserva los bloques y descansos originales; las partes ya implementadas requieren evidencia y revisión, no volver a desarrollarse. Carlos lidera el servicio, Álvaro el hospital en la prueba opcional de dos hosts, Yazmin el formulario/pitch y Javier el cierre de entrega.

## Roles

### 🧭 Capitán · coordinación, documentación y entrega · Javier Augusto Rebull Saucedo
- Cuida el reloj: stand-ups cada 4 horas, demo funcional en la hora 18, congelamiento en la 20.
- Desbloquea: si alguien lleva 30 min atorado, reasigna o se sienta con esa persona.
- README, [DECISION.md](DECISION.md), créditos de librerías y [CHECKLIST_ENTREGA.md](CHECKLIST_ENTREGA.md) al día.
- UI de la demo (pantalla dividida servidor vs. hospital) y su integración con el servicio.
- Integración final en `main` y **envío en Hack2skill**.

### 🖥️ Infraestructura LinuxONE y cifrado · Álvaro Hernández Jarquín
- VM de LinuxONE (Ubuntu 24.04): accesos SSH de los 4, Python, Docker y dependencias en s390x.
- Horas 1–3: prueba `phe` (Paillier) en s390x. En la hora 2 **comprueba** si TenSEAL/OpenFHE están disponibles: CKKS es extra; si no están, se sigue con Paillier sin tocar el MVP.
- Dos contenedores (hospital con llave · servicio de riesgo sin llave), TLS 1.3 y bóveda AES-256-GCM (CPACF), listos **antes de su descanso de H8**.
- Latencia p50/p95 por paciente y **capturas de evidencia** de LinuxONE (`uname -m`, contenedores, `lscpu`/`cpacfinfo`, versiones de OpenSSL de la CLI y de `cryptography`).
- Segunda revisión técnica del checklist de entrega.

### 🧠 Modelado ML · Carlos Enrique Gonzalez Moran
- Labs obligatorios de IA (multi-model y predictivo + generativo) junto con Álvaro y Yazmin.
- Regresión logística en el CDC y **contrato numérico** (orden de las 21 variables, escala, error medido) en H3–H8. XGBoost solo como referencia si sobra tiempo.
- Pesos en punto fijo e **inferencia cifrada con Paillier**: un recorrido completo **antes de su descanso de H11**; métrica estrella: **AUC cifrado vs. en claro** sobre la misma muestra.
- Granite (llama.cpp) es un extra sin integrar; solo se retoma con LinuxONE, evidencia y video encaminados.
- Semillas fijas, scripts reproducibles en `src/` y `pip freeze` final.

### 📊🎤 Datos y pitch · Yazmin Ivonne Flores Martinez
- EDA y particiones del CDC; etapas de la atención, indicador exploratorio por estado y mapa con los datos mexicanos (`data/marts/`).
- Dueña de la narrativa de impacto: cifras con fuente en las slides.
- Slides v2 con capturas reales, **pitch deck en PDF** con el nombre oficial y **video de 2:50**.
- Vigila que nada sensible llegue al repo.

---

## ⏱️ Plan de las 24 horas

**Hora 0 = 17 oct, 7:00 hora Juárez.** Hora 18 = 18 oct, 1:00. Hora 24 = 18 oct, 7:00 (meta de envío). La entrega en Hack2skill cierra el **18 oct a las 10:30** (hora Juárez).

> Antes de escribir código propio, la guía exige completar los **2 labs de IA/ML** de la organización. Van en las horas 1–3.

| Hora | Javier · capitán | Álvaro · infra LinuxONE | Carlos · modelado | Yazmin · datos y pitch |
|------|------------------|-------------------------|-------------------|------------------------|
| 0–1 | **Arranque y alcance** · firmas en DECISION.md | Acceso de los 4 a la VM y al repo | Plan del modelo | Plan de datos y del pitch |
| 1–3 | Capturas de labs a `submission/evidencias/` | **Labs** · `phe` en s390x · H2: ¿CKKS disponible? (extra) | **Labs obligatorios** | **Labs** · EDA del CDC |
| 3–5 | Stand-up · boceto de la UI | **Dos contenedores Docker** | **Regresión logística** | Particiones 70/15/15 y esquema de 21 variables → **a Carlos en H5** |
| 5–8 | 😴 Descansa | **TLS 1.3 + bóveda AES-256-GCM** | **Contrato numérico** (escala y error medido) · XGBoost si sobra | Cifras por etapa y mapa |
| 8–11 | Stand-up · UI de pantalla dividida | 😴 Descansa | **Punto fijo + inferencia Paillier: recorrido completo antes de H11** | Slide de impacto · extra: series y presupuesto E5, preparación ENSANUT |
| 11–12 | UI de pantalla dividida | Servicio de riesgo con el código de Carlos | 😴 Descansa | Extras E5 / ENSANUT |
| 12–14 | 🚩 **H12: chequeo del recorrido** (petición → cálculo cifrado → descifrado → UI) · UI conectada | **Servicio conectado** · evidencias de CPACF | 😴 Descansa | **Slides v2** con capturas |
| 14–16 | UI conectada al servicio | Latencia p50/p95 · tamaño de cifrados | **Métricas claro vs. cifrado** sobre la muestra | 😴 Descansa |
| 16–18 | **Empuje a demo** | Capturas de evidencia · flowchart (extra) | Tabla de métricas · extras: Granite, respaldo regional E5 | 😴 hasta H17 · **guion final** H17–18 |
| **18** | 🚩 **DEMO FUNCIONAL** | | | |
| 18–20 | Ensayo general · checklist · extras: dashboard E5 y prototipo publicado | Medición final · capturas | Tabla final de métricas | Video de respaldo de la demo |
| 20 | 🧊 **Congelamiento de features** | | | |
| 20–22 | README de la demo · repo limpio | Revisión técnica del checklist | `pip freeze` · reproducibilidad | **Grabación del video (2:50)** · PDF del deck |
| 22–24 | **Envío en Hack2skill (meta 7:00)** · título `Los Antimarrulla_IBM Z Datathon 2026 Project` | Revisión final | Revisión final | Revisión final |

**Regla de extras.** Cada quien empieza un extra (E5, ENSANUT, Granite, CKKS, flowchart, prototipo) **solo cuando entregó su tarea MVP** del bloque. En el chequeo de H12, si no existe el recorrido completo (petición → cálculo cifrado → descifrado → resultado en la UI), **se pausan los extras** sin sacarlos del plan: Carlos vuelve a Paillier al regresar de su descanso (H14), Álvaro integra, Javier sigue con la UI y Yazmin junta evidencia y pitch.

**Plan por épicas e historias de usuario:** 7 épicas (E1 base · E2 infraestructura · E3 modelo cifrado · E4 datos e impacto · E5 pronóstico y planeación financiera · E6 demo · E7 pitch y entrega) en [site/status.json](../site/status.json), visibles en el sitio.

**Épica E5 (Plus):** Yazmin prepara las 222 series (111 por tipo), el pronóstico de base y el presupuesto después de entregar las particiones (H8–H12); Carlos agrega el respaldo regional solo con el MVP entregado (H16–H18) y Javier arma el dashboard solo si la demo de H18 pasó (H18–H20). Diseño en [PRONOSTICO.md](PRONOSTICO.md).

## 😴 Turnos de descanso

Dormir es estrategia, no flojera. Cada quien toma **un bloque de 3 horas**, de a uno por bloque, para que **siempre haya 3 personas despiertas**.

| Bloque | Descansa | Se quedan de guardia |
|--------|----------|----------------------|
| Horas 5–8 | Javier | Álvaro, Carlos, Yazmin |
| Horas 8–11 | Álvaro | Javier, Carlos, Yazmin |
| Horas 11–14 | Carlos | Javier, Álvaro, Yazmin |
| Horas 14–17 | Yazmin | Javier, Álvaro, Carlos |

Reglas:
- Antes de dormir: commit, push, actualizar [site/status.json](../site/status.json) y un mensaje en el canal con "dónde me quedé".
- Javier no descansa durante el empuje a demo (16–18) ni en el envío (22–24).
- Pausas de 10 minutos cada 2 horas: agua, estirarse, alejarse de la pantalla.
- Si alguien está fundido, se le manda a dormir. Ese es un acto antimarrulla.
