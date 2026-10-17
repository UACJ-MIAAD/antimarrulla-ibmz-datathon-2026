<p align="center">
  <img src="assets/logo.png" alt="Logo de Los Antimarrulla" width="320">
</p>

# Los Antimarrulla · IBM Z Datathon 2026

> **"Combatimos la flojera y la procrastinación."**
> 24 horas, un mainframe y cero excusas.

**Sitio público con plan, estatus en vivo y pitch:** https://antimarrulla-tamizaje.netlify.app

Repositorio oficial del equipo **Los Antimarrulla** (UACJ · Maestría en Inteligencia Artificial y Analítica de Datos, MIAAD) para el **IBM Z Datathon 2026**. Aquí vive todo: la estrategia, las reglas, las ideas candidatas, el código que construimos durante el evento y los materiales de la entrega.

---

## Equipo

| Participante | Nombre | Correo |
|--------------|--------|--------|
| Participante 1 (capitán) | Javier Augusto Rebull Saucedo | al263483@alumnos.uacj.mx |
| Participante 2 | Álvaro Hernández Jarquín | al263150@alumnos.uacj.mx |
| Participante 3 | Carlos Enrique Gonzalez Moran | al271771@alumnos.uacj.mx |
| Participante 4 | Yazmin Ivonne Flores Martinez | al261548@alumnos.uacj.mx |

---

## La competición en una tabla

| Concepto | Detalle |
|----------|---------|
| Evento | IBM Z Datathon 2026 · Shooting Stars Foundation, impulsado por IBM |
| Fechas | **17–18 de octubre de 2026** · 24 horas continuas |
| Modalidad | Híbrido (8 sedes + virtual); nosotros: virtual, región Americas, desde México |
| Horario (hora Juárez) | Arranque del equipo **17 oct 7:00** · meta de envío **18 oct 7:00** · **cierre en Hack2skill 18 oct 10:30** |
| Setup técnico obligatorio | **16 de octubre** · LinuxONE Community Cloud |
| Premios | Por región: **US$1,000 / 750 / 500** + IBM Z Day + 6 meses de IBM Z · bolsa global +$50,000 USD con premios especiales y AI Innovation Excellence |
| Evaluación | 4 criterios × 10 pts = 40 pts ([CRITERIOS](docs/CRITERIOS.md)) |
| Equipo | 4 a 6 estudiantes universitarios 18+, cualquier carrera |
| Entregables | Video de máx. 3 min · link al repo · **pitch deck en PDF** `Los Antimarrulla_IBM Z Datathon 2026 Project.pdf` · links open source |
| Nuestro proyecto | **Tamizaje a ciegas** · Tema 2: **AI Secured: Innovation Without Exposure** |

Más detalle: [COMPETENCIA](docs/COMPETENCIA.md) · [REGLAS](docs/REGLAS.md) · [CRITERIOS](docs/CRITERIOS.md) · [TEMAS](docs/TEMAS.md)

---

## Mapa del repo

```
.
├── README.md                ← estás aquí
├── CONTRIBUTING.md          ← ramas, PRs y formato de commits
├── LICENSE                  ← MIT
├── requirements.txt
├── .github/                 ← plantilla de pull request
├── assets/                  ← logo del equipo
├── docs/
│   ├── COMPETENCIA.md       ← fechas, formato, premios, elegibilidad
│   ├── REGLAS.md            ← lo que NO podemos romper
│   ├── CRITERIOS.md         ← rúbrica oficial de 40 pts + estrategias
│   ├── TEMAS.md             ← los 3 retos oficiales
│   ├── PROYECTO.md          ← diseño de Tamizaje a ciegas: cifrado, arquitectura, plan
│   ├── FUENTES_DATOS.md     ← CDC, SINAVE (incidencia) y EDR INEGI (mortalidad)
│   ├── MODELO_DATOS.md      ← esquema estrella, llaves, armonización y mart de la cascada
│   ├── DECISION.md          ← acta: por qué elegimos Tamizaje a ciegas
│   ├── IDEAS.md             ← ideas candidatas + matriz de decisión
│   ├── Ranking_Ideas_Antimarrulla.pptx ← 11 ideas calificadas por jueces ciegos
│   ├── ROLES.md             ← quién hace qué, turnos y descanso
│   ├── CHECKLIST_ENTREGA.md ← nada se entrega sin palomear esto
│   └── LINKS.md             ← enlaces oficiales y de comunidad
├── src/                     ← código del proyecto (se escribe DURANTE el evento)
├── notebooks/               ← exploración y experimentos
├── data/                    ← datos públicos listos para usar (inventario en data/README.md)
│   ├── cdc_891/             ← entrenamiento del modelo (CDC, 253,680 registros)
│   ├── sinave/              ← casos nuevos semanales de diabetes T1 y T2, 2014–2026
│   ├── defunciones/         ← muertes por diabetes 2024
│   ├── egresos_ssa/         ← hospitalizaciones por diabetes 2024 en SSA (+ procedimientos)
│   ├── egresos_sector/      ← hospitalizaciones por diabetes 2024 de todo el sector (IMSS, ISSSTE…)
│   ├── sis_cronicas/        ← control de diabetes por unidad médica, 2021–2023
│   ├── imss_detecciones/    ← tamizajes de diabetes del IMSS, 2000–2023
│   ├── conapo/              ← población y marginación (denominadores)
│   ├── historicos/          ← muertes 2017–2024 y hospitalizaciones 2018–2024 agregadas
│   ├── catalogos/           ← entidades (tabla de cruce) y CLUES
│   ├── geo/                 ← polígonos de los 32 estados
│   └── marts/               ← cascada de la diabetes por entidad y año
├── site/                    ← sitio público (Netlify): plan, estatus en vivo, pitch y mapa
│   └── status.json          ← EL ESTATUS DEL PLAN: edítalo y haz commit; el sitio lo lee en vivo
└── submission/
    ├── Los_Antimarrulla_Pitch_Tamizaje.pptx ← presentación del proyecto (8 slides)
    ├── PITCH.md             ← guion del video de máx. 3 minutos
    ├── SLIDES.md            ← estructura de las slides
    └── evidencias/          ← capturas de LinuxONE para los jueces
```

---

## Quickstart

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

>  _Esta sección se actualiza durante el evento con el comando exacto para correr la demo._

---

## Proyecto

### Tamizaje a ciegas

> **La IA ve el riesgo. Nadie ve al paciente.**

- **Tema oficial:** T2 · AI Secured: Innovation Without Exposure
- **Problema:** en México, 18.3% de los adultos vive con diabetes, 1 de cada 3 no lo sabe y es la 2.ª causa de muerte (112,577 defunciones en 2024) y causó más de 11 mil amputaciones solo en hospitales de la Secretaría de Salud. Los hospitales tienen los datos para detectar el riesgo antes, pero no pueden compartirlos.
- **Solución:** el hospital cifra los 21 indicadores del paciente con **cifrado homomórfico (Paillier)** y se queda con la llave. LinuxONE calcula el riesgo de diabetes **sobre los datos cifrados**, sin poder leerlos. El hospital descifra el resultado y **Granite** lo explica en lenguaje claro. Es tamizaje, no diagnóstico.
- **Uso de IBM Z / LinuxONE:** dos contenedores Docker en LinuxONE (hospital con llave · servicio de riesgo sin llave); aritmética homomórfica con enteros de miles de bits; AES-256-GCM en reposo acelerado por CPACF; TLS 1.3 en tránsito.
- **Datos (ya en `data/`):** CDC Diabetes Health Indicators (UCI 891) para entrenar el modelo; para el contexto mexicano, casos nuevos **SINAVE** 2014–2026, **muertes** y **hospitalizaciones** por diabetes 2024 (todo el sector, incluido el ISSSTE), control en el **SIS**, tamizajes del **IMSS** y población de **CONAPO**. Los archivos completos de la DGIS están en el Release [`datos-2024`](https://github.com/UACJ-MIAAD/antimarrulla-ibmz-datathon-2026/releases/tag/datos-2024).
- **Hallazgo clave:** en 2024 hubo 22 muertes por diabetes por cada 100 casos nuevos notificados en el país: **44 en Michoacán contra 9 en Sinaloa**. Donde se notifica poco, la diabetes probablemente se detecta tarde ([detalle](docs/FUENTES_DATOS.md#32-la-brecha-de-detección-por-estado-2024)).
- **Métrica estrella:** AUC cifrado vs. AUC en claro (la privacidad no cuesta precisión).
- **Cómo correr la demo:** _se documenta durante el evento._

Diseño completo: [docs/PROYECTO.md](docs/PROYECTO.md) · Por qué la elegimos: [docs/DECISION.md](docs/DECISION.md) · Datos: [docs/FUENTES_DATOS.md](docs/FUENTES_DATOS.md) · Pitch: [submission/Los_Antimarrulla_Pitch_Tamizaje.pptx](submission/Los_Antimarrulla_Pitch_Tamizaje.pptx)

---

## Cómo trabajamos

Resumen (detalle en [CONTRIBUTING.md](CONTRIBUTING.md)):

1. **Una rama por integrante o por feature**; nada directo a `main`.
2. **Pull request revisado por otro miembro** antes de fusionar.
3. **Commits en español** con formato `tipo: descripción` → `datos: limpieza inicial del dataset`.
4. **Todo commit de código es del 17–18 de octubre.** El historial es evidencia ante los jueces.
5. **Hora 1:** reunión de decisión de idea. **Hora 18:** deadline interno de demo funcional.

---

## Créditos y librerías

Las reglas permiten librerías open source **siempre que se citen**. Esta tabla se mantiene al día durante el evento.

| Herramienta / librería | Licencia | Para qué la usamos |
|------------------------|----------|--------------------|
| pandas, NumPy, scikit-learn, matplotlib, Jupyter | BSD / PSF | Datos, modelado y visualización |
| [python-paillier (`phe`)](https://github.com/data61/python-paillier) | GPLv3 (partes Apache 2.0) | Cifrado homomórfico Paillier (ruta garantizada) |
| [cryptography](https://github.com/pyca/cryptography) | Apache 2.0 / BSD | AES-256-GCM en reposo |
| [ucimlrepo](https://github.com/uci-ml-repo/ucimlrepo) | MIT | Descarga del dataset CDC (UCI 891) |
| [dbfread](https://github.com/olemb/dbfread) | MIT | Lectura de microdatos EDR de INEGI (DBF) |
| [TenSEAL](https://github.com/OpenMined/TenSEAL) / [OpenFHE](https://github.com/openfheorg/openfhe-development) | Apache 2.0 / BSD-2 | Ruta CKKS opcional |
| [llama.cpp](https://github.com/ggerganov/llama.cpp) + IBM Granite | MIT / Apache 2.0 | Explicación generativa del resultado |
| _agregar aquí_ | | |

---

## Licencia

[MIT](LICENSE) · Hecho con cafeína y disciplina en Ciudad Juárez, Chihuahua.
