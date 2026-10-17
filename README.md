<p align="center">

> **Release update (October 17):** [English delivery plan](docs/PLAN_CIERRE.md). Hack2Skill submissions are open from October 16, 23:45 UTC until October 18, 16:30 UTC (12:30 EDT / 10:30 Ciudad Juárez / 18:30 SAST). Internal target: October 18, 13:00 UTC. All authored release material must be in English; the migration and independent review remain open under US-7.9. Existing historical evidence is preserved.
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

**Siguiente acción del equipo:** [Plan de cierre, responsables y plan B](docs/PLAN_CIERRE.md). Primero evidencia de LinuxONE, labs, revisión independiente y video; formulario y segunda VM quedan como extras.

---

## Mapa del repo

```
.
├── README.md                ← estás aquí
├── CONTRIBUTING.md          ← ramas, PRs y formato de commits
├── LICENSE                  ← MIT
├── requirements.txt         ← versiones verificadas
├── Makefile                 ← interfaz única: make verify · make demo · make medir · make package
├── artefactos/              ← particiones 70/15/15, esquema, modelo exportado y sus métricas
├── docker/                  ← imagen Ubuntu 24.04 (amd64, arm64, s390x) y compose de la demo
├── tests/                   ← pruebas del protocolo, el servicio y la integración
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
│   ├── PRONOSTICO.md        ← épica E5: pronóstico a 52 semanas y planeación financiera
│   ├── DECISION.md          ← acta: por qué elegimos Tamizaje a ciegas
│   ├── IDEAS.md             ← ideas candidatas + matriz de decisión
│   ├── Ranking_Ideas_Antimarrulla.pptx ← 11 ideas calificadas por jueces ciegos
│   ├── ROLES.md             ← quién hace qué, turnos y descanso
│   ├── LINUXONE.md          ← pasos para correr todo en la VM s390x
│   ├── CHECKLIST_ENTREGA.md ← nada se entrega sin palomear esto
│   └── LINKS.md             ← enlaces oficiales y de comunidad
├── src/
│   ├── tamizaje/            ← modelo, protocolo Paillier, servicio, hospital, UI, bóveda y mediciones
│   └── datos/               ← scripts reproducibles de los datos derivados
├── notebooks/               ← exploración y experimentos
├── data/                    ← datos públicos listos para usar (inventario en data/README.md)
│   ├── cdc_891/             ← entrenamiento del modelo (CDC, 253,680 registros)
│   ├── sinave/              ← casos nuevos semanales de diabetes T1 y T2, 2014–2026
│   ├── defunciones/         ← muertes por diabetes 2024
│   ├── egresos_ssa/         ← hospitalizaciones por diabetes 2024 en SSA (+ procedimientos)
│   ├── egresos_sector/      ← hospitalizaciones por diabetes 2024 de la base sectorial (IMSS, ISSSTE…)
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
    └── evidencias/          ← mediciones y capturas (locales hoy; LinuxONE al correr ahí)
```

---

## Cómo correrlo

Requisitos: Python 3.12, Docker y `make`. Probado el 17 oct 2026 en macOS arm64 (host y contenedores Linux arm64) y en un clon limpio. **Aún no se ha corrido en LinuxONE**: los pasos para la VM s390x están en [docs/LINUXONE.md](docs/LINUXONE.md).

```bash
git clone https://github.com/UACJ-MIAAD/antimarrulla-ibmz-datathon-2026.git
cd antimarrulla-ibmz-datathon-2026
make verify      # crea .venv, corre todas las pruebas y verifica artefactos y re-entrenamiento
make demo        # genera secretos en ~/.tamizaje, construye la imagen, levanta hospital + servicio y corre la prueba de humo
open http://127.0.0.1:8080   # UI de pantalla dividida (pacientes sintéticos)
make medir       # misma muestra CDC: métricas + tiempos del logit en claro/punto fijo y del recorrido cifrado
make package     # paquete de entrega en dist/
make demo-down
```

Sin Python en el host (por ejemplo, en la VM): `make verify-docker`, `make demo-docker` y `make medir-docker` hacen lo mismo dentro de las imágenes Ubuntu 24.04.

---

## Proyecto

### Tamizaje a ciegas

> **La IA ve el riesgo. Nadie ve al paciente.**
>
> **Alcance de esa promesa:** el servicio de riesgo recibe únicamente cifrados y nunca tiene la llave Paillier. El MVP usa dos contenedores en una misma máquina (LinuxONE es el destino pendiente de evidencia); quien administra el host queda dentro de confianza. La demo usa sintéticos; el CDC público se reserva a benchmarks explícitos. Detalle en [PROYECTO.md](docs/PROYECTO.md).

- **Tema oficial:** T2 · AI Secured: Innovation Without Exposure
- **Problema:** en México, 18.3% de los adultos vive con diabetes, 1 de cada 3 no lo sabe y es la 2.ª causa de muerte (112,577 defunciones registradas en 2024). En hospitales de la Secretaría de Salud, 11,550 egresos por diabetes (18.4%) incluyeron una amputación de miembro inferior. Los hospitales tienen los datos para detectar el riesgo antes, pero no pueden compartirlos.
- **Solución:** el hospital cifra los 21 indicadores del paciente con **cifrado homomórfico (Paillier)** y se queda con la llave. El servicio de riesgo (diseñado para LinuxONE) calcula el riesgo de diabetes **sobre los datos cifrados**, sin poder leerlos. El hospital descifra el resultado y muestra los factores que más pesan; la explicación con **Granite** es un extra que aún no está integrado. Es tamizaje, no diagnóstico.
- **Uso de IBM Z / LinuxONE:** diseñado para dos contenedores en la VM de LinuxONE (hospital con la llave Paillier y la bóveda AES-256-GCM · servicio de riesgo sin llaves) con TLS 1.3 mutuo; la aritmética homomórfica son enteros de miles de bits. **Hoy está probado en contenedores locales y en CI x86_64; la ejecución en LinuxONE está pendiente** ([docs/LINUXONE.md](docs/LINUXONE.md)). CPACF existe en IBM Z, pero su uso efectivo no está medido.
- **Datos (ya en `data/`):** CDC Diabetes Health Indicators (UCI 891) para entrenar el modelo; para el contexto mexicano, casos nuevos **SINAVE** 2014–2026, **muertes** y **hospitalizaciones** por diabetes 2024 (base sectorial reportada, incluido el ISSSTE), control en el **SIS**, tamizajes del **IMSS** y población de **CONAPO**. Los archivos completos de la DGIS están en el Release [`datos-2024`](https://github.com/UACJ-MIAAD/antimarrulla-ibmz-datathon-2026/releases/tag/datos-2024).
- **Indicador exploratorio:** en 2024 se registraron 22 muertes por diabetes (ocurridas y registradas en el año, de residentes en México) por cada 100 casos nuevos notificados en el país, con **44 en Michoacán y 9 en Sinaloa**. No es letalidad ni una medición de subdiagnóstico: mezcla cohortes distintas y no está ajustado por edad ([detalle y límites](docs/FUENTES_DATOS.md#32-muertes-por-cada-100-casos-notificados-por-estado-2024--exploratorio)).
- **Métrica estrella:** AUC cifrado vs. AUC en claro sobre los mismos pacientes. Mediciones **locales**, no LinuxONE, del commit `655763f`: 2,000/2,000 enteros idénticos a la referencia de punto fijo y ROC-AUC 0.808 en las tres variantes; API en dos contenedores, 200/200 resultados y 131.8 ms p50. Las cifras pertenecen a esa versión y no se transfieren automáticamente a cambios posteriores. Detalle en [submission/evidencias/metricas/](submission/evidencias/metricas/README.md).
- **Cómo correr la demo:** ver [Cómo correrlo](#cómo-correrlo).

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
| [pandas](https://github.com/pandas-dev/pandas), [NumPy](https://github.com/numpy/numpy), [scikit-learn](https://github.com/scikit-learn/scikit-learn), [matplotlib](https://github.com/matplotlib/matplotlib), [Jupyter](https://github.com/jupyter/notebook) | BSD / PSF | Datos, modelado y visualización |
| [python-paillier (`phe`)](https://github.com/data61/python-paillier) | GPLv3 (partes Apache 2.0) | Cifrado homomórfico Paillier (ruta garantizada) |
| [gmpy2](https://github.com/aleaxit/gmpy) | LGPL-3.0-or-later | Aritmética de enteros grandes que `phe` usa para acelerar Paillier |
| [pytest](https://github.com/pytest-dev/pytest) | MIT | Pruebas |
| [Ubuntu 24.04](https://hub.docker.com/_/ubuntu) (imagen de contenedor) y sus paquetes `python3-*` | Varias (libres) | Base de los contenedores en amd64, arm64 y s390x |
| [cryptography](https://github.com/pyca/cryptography) | Apache 2.0 / BSD | AES-256-GCM en reposo y certificados TLS de la demo |
| [ucimlrepo](https://github.com/uci-ml-repo/ucimlrepo) | MIT | Descarga del dataset CDC (UCI 891) |
| [dbfread](https://github.com/olemb/dbfread) | MIT | Lectura de microdatos EDR de INEGI (DBF) |
| [TenSEAL](https://github.com/OpenMined/TenSEAL) / [OpenFHE](https://github.com/openfheorg/openfhe-development) | Apache 2.0 / BSD-2 | Ruta CKKS (extra): **no usada todavía** |
| [llama.cpp](https://github.com/ggerganov/llama.cpp) + IBM Granite | MIT / Apache 2.0 | Explicación generativa (extra): **no integrada todavía** |
| [statsmodels](https://github.com/statsmodels/statsmodels) | BSD | Pronóstico ETS (épica E5, extra) |

---

## Licencias

- **Código propio:** [MIT](LICENSE).
- **Dependencia `python-paillier` (`phe`):** GPLv3 (con partes Apache 2.0). Si distribuimos una obra combinada con `phe` (por ejemplo, una imagen de contenedor), esa distribución debe cumplir la GPLv3: no se presenta como "solo MIT" y se conservan sus avisos y su texto de licencia.
- **Datos:** cada fuente conserva su licencia y exige atribución; indicamos los cambios (recortes, agregados y armonizaciones) en `data/README.md` y `src/datos/`. CDC/BRFSS: dominio público (UCI remite a la fuente; Kaggle lo marca CC0). DGIS, IMSS, CONAPO: CC BY 4.0 o libre uso con cita. Natural Earth: dominio público. ENSANUT: no se redistribuye.

## Licencia

[MIT](LICENSE) · Hecho con cafeína y disciplina en Ciudad Juárez, Chihuahua.
