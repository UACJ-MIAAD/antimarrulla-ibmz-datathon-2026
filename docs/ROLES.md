# 👥 Roles, responsabilidades y turnos

> Somos **4**, el mínimo de las bases. Nadie es dueño exclusivo de nada; todos revisan PRs de todos.
> El estatus de cada tarea vive en [site/status.json](../site/status.json) y se ve en vivo en https://antimarrulla-tamizaje.netlify.app

## Roles

### 🧭 Capitán · coordinación, documentación y entrega · Javier Augusto Rebull Saucedo
- Cuida el reloj: stand-ups cada 4 horas, demo funcional en la hora 18, congelamiento en la 20.
- Desbloquea: si alguien lleva 30 min atorado, reasigna o se sienta con esa persona.
- README, [DECISION.md](DECISION.md), créditos de librerías y [CHECKLIST_ENTREGA.md](CHECKLIST_ENTREGA.md) al día.
- UI de la demo (pantalla dividida servidor vs. hospital) y su integración con el servicio.
- Integración final en `main` y **envío en Hack2skill**.

### 🖥️ Infraestructura LinuxONE y cifrado · Álvaro Hernández Jarquín
- VM de LinuxONE (Ubuntu 24.04): accesos SSH de los 4, Python, Docker y dependencias en s390x.
- Horas 1–2: prueba `phe` (Paillier) y TenSEAL/OpenFHE en s390x → **decisión CKKS vs. Paillier en la hora 2**.
- Dos contenedores (hospital con llave · servicio de riesgo sin llave), TLS 1.3 y bóveda AES-256-GCM (CPACF).
- Latencia por paciente y **capturas de evidencia** de LinuxONE (`uname -m`, contenedores, `openssl speed`).
- Segunda revisión técnica del checklist de entrega.

### 🧠 Modelado ML · Carlos Enrique Gonzalez Moran
- Labs obligatorios de IA (multi-model y predictivo + generativo) junto con Álvaro y Yazmin.
- Regresión logística en el CDC (y XGBoost de referencia) en las primeras horas.
- Pesos en punto fijo e **inferencia cifrada con Paillier**; métrica estrella: **AUC cifrado vs. en claro**.
- Granite (llama.cpp) explicando el resultado al paciente.
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
| 1–3 | Capturas de labs a `submission/evidencias/` | **Labs** · `phe` en s390x · 🚩 H2 CKKS vs. Paillier | **Labs obligatorios** | **Labs** · EDA del CDC |
| 3–8 | Stand-up · boceto de la UI | **Dos contenedores Docker** | **Regresión logística** + XGBoost de referencia | Particiones 70/15/15 · cascada y mapa |
| 8–12 | Stand-up · UI de pantalla dividida | TLS 1.3 + bóveda AES-256-GCM | **Punto fijo + inferencia Paillier** | Slide de impacto con datos reales |
| 12–16 | Stand-up · UI conectada al servicio | Servicio de riesgo conectado | **AUC cifrado vs. en claro** | Slides v2 con capturas |
| 16–18 | **Empuje a demo** | Latencia y capturas de evidencia | Granite explica el resultado | Guion final |
| **18** | 🚩 **DEMO FUNCIONAL** | | | |
| 18–20 | Ensayo general · checklist | Medición final · capturas | Tabla final de métricas | Video de respaldo de la demo |
| 20 | 🧊 **Congelamiento de features** | | | |
| 20–22 | README de la demo · repo limpio | Revisión técnica del checklist | `pip freeze` · reproducibilidad | **Grabación del video (2:50)** · PDF del deck |
| 22–24 | **Envío en Hack2skill (meta 7:00)** · título `Los Antimarrulla_IBM Z Datathon 2026 Project` | Revisión final | Revisión final | Revisión final |

**Plan por épicas e historias de usuario:** 7 épicas (E1 base · E2 infraestructura · E3 modelo cifrado · E4 datos e impacto · E5 pronóstico y planeación financiera · E6 demo · E7 pitch y entrega) en [site/status.json](../site/status.json), visibles en el sitio.

**Épica E5 (Plus):** Yazmin prepara las 222 series (111 por tipo) y la planeación financiera (H3–H12), Carlos ajusta los modelos de pronóstico (H8–H12) y Javier arma el dashboard (H12–H16). Diseño en [PRONOSTICO.md](PRONOSTICO.md). Si en la hora 12 la demo cifrada va atrasada, E5 se congela.

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
