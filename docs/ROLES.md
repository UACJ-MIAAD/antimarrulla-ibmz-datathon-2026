# 👥 Roles, responsabilidades y turnos

> Somos **4**, el mínimo de las bases. Roles **tentativos**: se ajustan en la reunión de decisión según la idea elegida. Nadie es dueño exclusivo de nada; todos revisan PRs de todos.

## Roles

### 🧭🎤 Líder / coordinación + documentación y pitch · Javier Augusto Rebull Saucedo
- Modera la reunión de decisión (hora 1) y llena [DECISION.md](DECISION.md).
- Cuida el reloj: stand-ups cada 4 horas, deadline de demo en la hora 18, congelamiento en la 20.
- Desbloquea: si alguien lleva 30 min atorado, reasigna o se sienta con esa persona.
- README, créditos de librerías y declaración de IA al día.
- Guion ([submission/PITCH.md](../submission/PITCH.md)), slides ([submission/SLIDES.md](../submission/SLIDES.md)) y video pitch.
- Dueño de la narrativa de impacto comunitario y del [CHECKLIST_ENTREGA.md](CHECKLIST_ENTREGA.md).
- Integración final en `main` y envío de la entrega.

### 📊🎨 Datos + frontend / demo · Yazmin Ivonne Flores Martinez
- **Horas 0–10 · Datos:** obtiene el dataset, documenta fuente y licencia en `data/README.md`; limpieza, EDA y particiones (por "banco" u "hospital" según la idea); notebook `notebooks/01_eda.ipynb` con gráficas para el pitch. Vigila que nada sensible llegue al repo.
- **Desde la hora 10 · Demo:** interfaz de la demo (pantalla dividida, paneles por banco o chat), datos de demo precargados, flujo de 60 segundos sin fallas y video de respaldo (plan B).

### 🧠 Modelado ML · Álvaro Hernández Jarquín
- Baseline en las primeras 6 horas.
- Versión con privacidad (cifrado homomórfico, federado o la que aplique).
- Tabla de métricas: baseline vs. modelo privado, con el costo de la privacidad.
- Semillas fijas y script reproducible en `src/`.
- Apoya a Yazmin con datos en las horas 8–10 para liberarla hacia la demo.

### 🖥️ Backend / infra LinuxONE · Carlos Enrique Gonzalez Moran
- Lleva el entorno de LinuxONE desde el setup del 16 oct: accesos de todo el equipo, Python, dependencias en s390x.
- Hora 0–2: confirma qué librerías críticas corren en s390x (alarma temprana).
- Servicio que corre en IBM Z (inferencia, agregador o asistente) y su cifrado.
- Mide latencia/rendimiento en LinuxONE para la slide de arquitectura.
- Segunda revisión técnica del checklist de entrega.

---

## ⏱️ Plan de las 24 horas

| Hora | Javier · líder + pitch | Yazmin · datos + demo | Álvaro · modelado ML | Carlos · LinuxONE |
|------|------------------------|-----------------------|----------------------|-------------------|
| 0–1 | **Reunión de decisión** | Reunión | Reunión | Reunión |
| 1–4 | Alcance, tablero y README del proyecto | Dataset + EDA | Setup de modelado | Validar librerías en s390x |
| 4–8 | Stand-up · integración · historia y persona | Limpieza y particiones | **Baseline** | Servicio base en LinuxONE |
| 8–10 | Stand-up · revisión de PRs | Cierre de datos + boceto de demo | Apoyo a datos + versión con privacidad | Cifrado + conexión |
| 10–12 | Borrador de guion | Esqueleto de UI | Versión con privacidad | Cifrado + conexión |
| 12–16 | Stand-up · riesgos · slides v1 | UI conectada al servicio real | Métricas y ajuste | Despliegue del modelo |
| 16–18 | **Empuje a demo** · arquitectura | Pulido de la demo | Congelar modelo | Pruebas de punta a punta |
| **18** | 🚩 **DEMO FUNCIONAL** | | | |
| 18–20 | Ensayo general · slides v2 | Video de respaldo de la demo | Tabla final de métricas | Medición de latencia |
| 20 | 🧊 **Congelamiento de features** | | | |
| 20–22 | **Grabación del video** · checklist | Ensayo de demo · prueba de quickstart | `pip freeze` | Limpieza del repo |
| 22–24 | **Envío** · links y formularios | Revisión final | Revisión final | Revisión final del checklist técnico |

## 😴 Turnos de descanso

Dormir es estrategia, no flojera. Cada quien toma **un bloque de 3 horas** entre la hora 8 y la 17, de a uno por bloque, para que **siempre haya 3 personas despiertas**.

| Bloque | Descansa | Se quedan de guardia |
|--------|----------|----------------------|
| Horas 8–11 | Carlos | Javier, Yazmin, Álvaro |
| Horas 11–14 | Álvaro | Javier, Yazmin, Carlos |
| Horas 14–17 | Yazmin | Javier, Álvaro, Carlos |
| Horas 5–8 | Javier | Yazmin, Álvaro, Carlos |

Reglas:
- Antes de dormir: commit, push y un mensaje en el canal con "dónde me quedé".
- Javier no descansa durante el empuje a demo (16–18) ni en el envío (22–24).
- Pausas de 10 minutos cada 2 horas: agua, estirarse, alejarse de la pantalla.
- Si alguien está fundido, se le manda a dormir. Ese es un acto antimarrulla.
