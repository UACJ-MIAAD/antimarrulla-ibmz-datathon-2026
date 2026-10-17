# 👥 Roles, responsabilidades y turnos

> Roles **tentativos**: se ajustan en la reunión de decisión según la idea elegida. Nadie es dueño exclusivo de nada; todos revisan PRs de todos.

## Roles

### 🧭 Líder / coordinación · Javier Augusto Rebull Saucedo
- Modera la reunión de decisión (hora 1) y llena [DECISION.md](DECISION.md).
- Cuida el reloj: stand-ups cada 4 horas, deadline de demo en la hora 18, congelamiento en la 20.
- Desbloquea: si alguien lleva 30 min atorado, reasigna o se sienta con esa persona.
- Integración final en `main` y envío de la entrega.
- Dueño de la narrativa de impacto comunitario junto con pitch.

### 📊 Datos · Yazmin Ivonne Flores Martinez
- Obtiene el dataset, documenta fuente y licencia en `data/README.md`.
- Limpieza, EDA y particiones (incluidas las particiones por "banco" o "hospital" según la idea).
- Notebook `notebooks/01_eda.ipynb` con gráficas que sirvan para el pitch.
- Vigila privacidad: nada sensible en el repo.

### 🧠 Modelado ML · Álvaro Hernández Jarquín
- Baseline en las primeras 6 horas.
- Versión con privacidad (cifrado homomórfico, federado o la que aplique).
- Tabla de métricas: baseline vs. modelo privado, con el costo de la privacidad.
- Semillas fijas y script reproducible en `src/`.

### 🖥️ Backend / infra LinuxONE · Carlos Gonzalez
- Lleva el entorno de LinuxONE desde el setup del 16 oct: accesos de todo el equipo, Python, dependencias en s390x.
- Hora 0–2: confirma qué librerías críticas corren en s390x (alarma temprana).
- Servicio que corre en IBM Z (inferencia, agregador o asistente) y su cifrado.
- Mide latencia/rendimiento en LinuxONE para la slide de arquitectura.

### 🎨 Frontend / demo · _Integrante 5 (por confirmar)_
- Interfaz de la demo (pantalla dividida, paneles por banco o chat).
- Datos de demo precargados y flujo de 60 segundos sin fallas.
- Graba el video de respaldo de la demo (plan B).

### 🎤 Documentación + pitch · _Integrante 6 (por confirmar)_
- README, créditos de librerías y declaración de IA al día.
- Guion ([submission/PITCH.md](../submission/PITCH.md)) y slides ([submission/SLIDES.md](../submission/SLIDES.md)).
- Graba y edita el video pitch.
- Dueño del [CHECKLIST_ENTREGA.md](CHECKLIST_ENTREGA.md).

### Plan B si somos 4

| Rol huérfano | Lo absorbe | Cuándo |
|--------------|-----------|--------|
| Frontend / demo | Yazmin (Datos) | Desde la hora 10, cuando los datos ya están estables |
| Documentación + pitch | Javier (Líder) | Todo el evento; guion y video desde la hora 18 |

---

## ⏱️ Plan de las 24 horas

| Hora | Líder | Datos | Modelado ML | Backend / LinuxONE | Frontend / demo | Docs + pitch |
|------|-------|-------|-------------|--------------------|-----------------|--------------|
| 0–1 | **Reunión de decisión** | Reunión | Reunión | Reunión | Reunión | Reunión |
| 1–4 | Alcance y tablero | Dataset + EDA | Setup de modelado | Validar librerías en s390x | Boceto de la demo | README del proyecto |
| 4–8 | Stand-up · integración | Limpieza y particiones | **Baseline** | Servicio base en LinuxONE | Esqueleto de UI | Historia y persona |
| 8–12 | Stand-up · revisión de PRs | Apoyo a modelado | Versión con privacidad | Cifrado + conexión | UI conectada a datos falsos | Borrador de guion |
| 12–16 | Stand-up · riesgos | Gráficas para pitch | Métricas y ajuste | Despliegue del modelo | UI conectada al servicio real | Slides v1 |
| 16–18 | **Empuje a demo** | Validación de resultados | Congelar modelo | Pruebas de punta a punta | Pulido | Arquitectura |
| **18** | 🚩 **DEMO FUNCIONAL** | | | | | |
| 18–20 | Ensayo general | Revisión de datos/licencias | Tabla final de métricas | Medición de latencia | Video de respaldo | Slides v2 |
| 20 | 🧊 **Congelamiento de features** | | | | | |
| 20–22 | Checklist | Prueba de quickstart | `pip freeze` | Limpieza del repo | Ensayo de demo | **Grabación del video** |
| 22–24 | **Envío** | Revisión final | Revisión final | Revisión final | Revisión final | Links y formularios |

## 😴 Turnos de descanso

Dormir es estrategia, no flojera. Cada quien toma **un bloque de 3 horas** entre la hora 8 y la 16, escalonados para que **nunca haya menos de 4 personas despiertas** (o 3 si somos 4).

| Bloque | Descansan | Se quedan de guardia |
|--------|-----------|----------------------|
| Horas 8–11 | Docs + pitch, Frontend / demo | Líder, Datos, Modelado, Backend |
| Horas 11–14 | Datos, Backend / LinuxONE | Líder, Modelado, Frontend, Docs |
| Horas 14–17 | Modelado ML, Líder | Datos, Backend, Frontend, Docs |

Reglas:
- Antes de dormir: commit, push y un mensaje en el canal con "dónde me quedé".
- El líder no descansa durante el empuje a demo (16–18) ni en el envío (22–24).
- Pausas de 10 minutos cada 2 horas: agua, estirarse, alejarse de la pantalla.
- Si alguien está fundido, se le manda a dormir. Ese es un acto antimarrulla.
