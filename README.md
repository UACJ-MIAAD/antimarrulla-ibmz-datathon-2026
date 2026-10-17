# 🛡️ Los Antimarrulla · IBM Z Datathon 2026

> **"Combatimos la flojera y la procrastinación."**
> 24 horas, un mainframe y cero excusas.

Repositorio oficial del equipo **Los Antimarrulla** (UACJ · Maestría en Inteligencia Artificial y Analítica de Datos, MIAAD) para el **IBM Z Datathon 2026**. Aquí vive todo: la estrategia, las reglas, las ideas candidatas, el código que construimos durante el evento y los materiales de la entrega.

---

## 👥 Equipo

| # | Integrante | Rol tentativo | Responsabilidad principal |
|---|------------|---------------|---------------------------|
| 1 | **Javier Augusto Rebull Saucedo** | 🧭 Líder / coordinación + 🎤 documentación y pitch | Decisiones, ritmo del equipo, integración final, README, slides, guion, video y entrega |
| 2 | **Álvaro Hernández Jarquín** | 🧠 Modelado ML | Entrenamiento, evaluación y explicabilidad del modelo |
| 3 | **Carlos Gonzalez** | 🖥️ Backend / infra LinuxONE | Entorno IBM Z, despliegue, cifrado y servicios |
| 4 | **Yazmin Ivonne Flores Martinez** | 📊 Datos + 🎨 frontend / demo | Dataset, limpieza, EDA y privacidad; desde la hora 10, interfaz de la demo en vivo |

> Somos 4: el mínimo permitido por las bases. Cuatro antimarrullas rinden por seis.

Detalle de responsabilidades por hora y plan de turnos: **[docs/ROLES.md](docs/ROLES.md)**.

---

## 🏁 La competición en una tabla

| Concepto | Detalle |
|----------|---------|
| Evento | IBM Z Datathon 2026 · Shooting Stars Foundation, impulsado por IBM |
| Fechas | **17–18 de octubre de 2026** · 24 horas continuas |
| Modalidad | Virtual (participamos desde México 🇲🇽) |
| Setup técnico obligatorio | **16 de octubre** · acceso a LinuxONE / IBM Z |
| Premios | +$50,000 USD · campeones regionales (Americas, EMEA, APAC) + reconocimientos por universidad |
| Equipo | 4 a 6 estudiantes universitarios 18+, cualquier carrera |
| Entregables | Repo público · demo/presentación · pitch en video grabado durante el evento |
| Nuestro tema candidato | 🔐 **AI Secured: Innovation Without Exposure** (las 3 ideas caen aquí) |

Más detalle: [COMPETENCIA](docs/COMPETENCIA.md) · [REGLAS](docs/REGLAS.md) · [CRITERIOS](docs/CRITERIOS.md) · [TEMAS](docs/TEMAS.md)

---

## 🗺️ Mapa del repo

```
.
├── README.md                ← estás aquí
├── CONTRIBUTING.md          ← ramas, PRs y formato de commits
├── LICENSE                  ← MIT
├── requirements.txt
├── .github/                 ← plantilla de pull request
├── docs/
│   ├── COMPETENCIA.md       ← fechas, formato, premios, elegibilidad
│   ├── REGLAS.md            ← lo que NO podemos romper
│   ├── CRITERIOS.md         ← rúbrica + cómo exprimir cada punto
│   ├── TEMAS.md             ← los 3 retos oficiales
│   ├── IDEAS.md             ← nuestras 3 ideas + matriz de decisión
│   ├── DECISION.md          ← acta de la idea elegida (se llena en la hora 1)
│   ├── ROLES.md             ← quién hace qué, turnos y descanso
│   ├── CHECKLIST_ENTREGA.md ← nada se entrega sin palomear esto
│   └── LINKS.md             ← enlaces oficiales y de comunidad
├── src/                     ← código del proyecto (se escribe DURANTE el evento)
├── notebooks/               ← exploración y experimentos
├── data/                    ← SOLO datos pequeños y públicos (lee data/README.md)
└── submission/
    ├── PITCH.md             ← guion del pitch de 3 minutos
    └── SLIDES.md            ← estructura de las slides
```

---

## ⚡ Quickstart

```bash
# 1. Clonar
git clone https://github.com/UACJ-MIAAD/antimarrulla-ibmz-datathon-2026.git
cd antimarrulla-ibmz-datathon-2026

# 2. Entorno virtual (Python 3.10+)
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Dependencias base
pip install -r requirements.txt

# 4. Exploración
jupyter notebook notebooks/
```

En LinuxONE (s390x) los pasos son los mismos; si algún paquete no trae wheel para s390x, se documenta aquí la alternativa que usamos.

> 🔧 _Esta sección se actualiza durante el evento con el comando exacto para correr la demo._

---

## 🧪 Proyecto

> _Se completa tras la reunión de decisión (hora 1). Ver [docs/DECISION.md](docs/DECISION.md)._

- **Nombre del proyecto:** _por definir_
- **Tema oficial:** _por definir_
- **Problema:** _por definir_
- **Solución:** _por definir_
- **Uso de IBM Z / LinuxONE:** _por definir_
- **Cómo correr la demo:** _por definir_

---

## 🤝 Cómo trabajamos

Resumen (detalle en [CONTRIBUTING.md](CONTRIBUTING.md)):

1. **Una rama por integrante o por feature**; nada directo a `main`.
2. **Pull request revisado por otro miembro** antes de fusionar.
3. **Commits en español** con formato `tipo: descripción` → `datos: limpieza inicial del dataset`.
4. **Todo commit de código es del 17–18 de octubre.** El historial es evidencia ante los jueces.
5. ⏰ **Hora 1:** reunión de decisión de idea. ⏰ **Hora 18:** deadline interno de demo funcional.

---

## 📚 Créditos, librerías y uso de IA

Las reglas permiten librerías open source y asistentes de IA generativa **siempre que se declaren**. Esta tabla se mantiene al día durante el evento.

| Herramienta / librería | Licencia | Para qué la usamos |
|------------------------|----------|--------------------|
| pandas, NumPy, scikit-learn, matplotlib, Jupyter | BSD / PSF | Datos, modelado y visualización |
| _agregar aquí_ | | |

| Asistente de IA | Para qué se usó | Quién revisó |
|-----------------|-----------------|--------------|
| Claude (Anthropic) | Estructura inicial del repo y redacción base de la documentación | Equipo |
| _agregar aquí_ | | |

Todo el código asistido por IA fue leído, entendido y probado por el equipo. Si no lo podemos explicar, no se sube.

---

## 📄 Licencia

[MIT](LICENSE) · Hecho con cafeína y disciplina en Ciudad Juárez, Chihuahua.
