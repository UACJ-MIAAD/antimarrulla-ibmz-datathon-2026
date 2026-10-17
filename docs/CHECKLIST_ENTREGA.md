# ✅ Checklist de entrega

> Nada se entrega sin palomear esta lista. Responsable: **Javier** (capitán), con una segunda revisión de **Álvaro** para la parte técnica y de **Yazmin** para video y PDF.
> Arrancar la revisión en la **hora 21**. Cierre en Hack2skill: **18 oct, 10:30 hora Juárez** → meta interna de envío: **7:00**.

## 🧪 Prerrequisitos (primeras horas)

- [ ] 🆕 Los 4 llenaron el **formulario de asistencia del kick-off**: https://forms.gle/hxTYwzJRqgwnWaPn8
- [ ] Ver la grabación del setup de LinuxONE (recomendada en el kick-off): https://www.youtube.com/watch?v=y9rZwSq8pw8

- [ ] Lab 1 completado: *Predictive AI Hybrid AI scenarios (multi-model)*
- [ ] Lab 2 completado: *Predictive AI + Generative AI*
- [ ] Capturas de ambos labs en `submission/evidencias/`
- [ ] VM de LinuxONE Community Cloud accesible para los 4 (registrada con el código `SSF2026`)

## 📦 Repositorio

- [ ] Repo **público** en GitHub (probar el link en una ventana de incógnito)
- [ ] Historial con **commits del 17–18 de octubre**, frecuentes y con formato `tipo: descripción`
- [ ] Ningún commit gigante de "todo el proyecto" al final
- [ ] Ramas fusionadas a `main` vía pull request con revisión
- [ ] `main` corre de punta a punta
- [ ] Sin datasets grandes ni datos sensibles (`git ls-files data/`)
- [ ] Sin credenciales, llaves ni tokens, incluido el de Jupyter Lab (buscar `key`, `token`, `password`, `secret`)
- [ ] `LICENSE` presente

## 📝 README y documentación

- [ ] Sección **Proyecto** completa: problema, solución, uso de IBM Z, cómo correr la demo
- [ ] Quickstart probado en máquina limpia por alguien que **no** escribió el código
- [ ] `requirements.txt` con versiones fijadas
- [ ] Instrucciones para obtener el dataset (fuente + licencia) en `data/README.md`
- [ ] Tabla de **librerías open source con sus links** (la guía lo exige en la entrega)
- [x] Declaración de **asistentes de IA** (sección *Uso de IA* al final del README) · actualizarla si se usa IA en el código del evento
- [ ] Diagrama de arquitectura / flowchart con las piezas que viven en LinuxONE
- [ ] [DECISION.md](DECISION.md) lleno

## 🖥️ Evidencias de LinuxONE (criterio técnico)

Capturas en `submission/evidencias/`:
- [ ] VM de LinuxONE corriendo (dashboard de la Community Cloud)
- [ ] `uname -m` → `s390x`
- [ ] `lscpu` y `cpacfinfo` (si está instalado)
- [ ] Versión de OpenSSL de la CLI **y** de la biblioteca que usa la app (`cryptography`)
- [ ] Tiempo de AES-256-GCM medido **dentro de la aplicación**
- [ ] Error numérico claro vs. cifrado y tamaño de la muestra cifrada
- [ ] Entrenamiento del modelo en LinuxONE
- [ ] Inferencia / servicio corriendo en LinuxONE
- [ ] Contenedor (Podman/Docker) si se usó
- [ ] Seguridad: cifrado, manejo de llaves, accesos
- [ ] Uso de recursos de cómputo (CPU/memoria) y métricas

## 🎥 Video pitch (obligatorio)

- [ ] **Máximo 3 minutos** (meta: 2:50)
- [ ] Cubre: **problema**, **datos que lo respaldan**, **solución** y **cómo aprovecha IBM Z**
- [ ] Muestra el **stack tecnológico**, la **instancia LinuxONE** y el **modelo** en pantalla
- [ ] Incluye la demo funcionando
- [ ] Grabado durante el fin de semana del evento
- [ ] Audio claro, sin ruido de fondo
- [ ] Subido y con link accesible (probar en incógnito)

## 🖼️ Pitch deck en PDF (obligatorio) y material opcional

- [ ] 🆕 **Exportar la presentación a PDF** con el nombre exacto `Los Antimarrulla_IBM Z Datathon 2026 Project.pdf` y subirla a Hack2skill

- [ ] Estructura de [submission/SLIDES.md](../submission/SLIDES.md)
- [ ] Flowchart de diseño (opcional en la entrega, pero suma al criterio técnico)
- [ ] Prototipo accesible (opcional)
- [ ] Slide de resultados con métricas reales (no inventadas)
- [ ] Slide de impacto comunitario con cifras y fuente

## 🖥️ Demo en vivo

- [ ] Ensayo completo cronometrado (hora 19)
- [ ] Datos de demo precargados
- [ ] Plan B: video de la demo por si falla la red o el entorno
- [ ] Sesión de LinuxONE abierta y probada antes de grabar

## 📋 Envío en Hack2skill

**Cómo se envía** (confirmado por el SME de SSF en Discord, 17 oct; [video del proceso](https://youtu.be/KIYu1iqtXTU)):
1. Abrir el **dashboard del equipo** en Hack2skill → sección de envío final del proyecto.
2. Llenar los detalles del proyecto y el planteamiento del problema.
3. Agregar el link del repo de GitHub.
4. Subir o enlazar el video de la demo (máx. 3 min).
5. Subir la presentación si el portal la pide (llevamos el PDF con el nombre oficial).
6. Revisar todo una vez y enviar antes del cierre.

> El envío es **por equipo**: lo hace **el líder del equipo registrado en Hack2skill** desde el dashboard, después de que los 4 revisen la versión final. Confirmar desde ya quién es el líder en la plataforma (por plan, Javier).

- [ ] Líder del equipo en Hack2skill confirmado y con acceso al dashboard
- [ ] Los 4 revisaron la versión final antes de enviar
- [ ] El video muestra el uso de LinuxONE (instancia, contenedores y modelo): es un requisito importante
- [ ] Título exacto: **`Los Antimarrulla_IBM Z Datathon 2026 Project`**
- [ ] Tema oficial seleccionado correctamente
- [ ] Link del video (máx. 3 min)
- [ ] 🆕 Pitch deck en PDF `Los Antimarrulla_IBM Z Datathon 2026 Project.pdf`
- [ ] Link del repo de GitHub (el código; la guía también acepta un zip)
- [ ] Links a los recursos open source usados
- [ ] Flowchart y prototipo adjuntos si los hay
- [ ] Los 4 integrantes vinculados al equipo
- [ ] Captura de la confirmación de envío guardada

## 🏁 Cierre y después

- [ ] Entrega enviada **a las 7:00 del 18 oct (hora Juárez)**, tres horas y media antes del cierre (10:30)
- [ ] Último commit anotado: `______`
- [ ] Ceremonia virtual de cierre: **17 oct, 23:00 hora Juárez** (1:00 EDT del 18 oct)
- [ ] Encuesta de retroalimentación / video antes del **23 oct**
- [ ] Anuncio de ganadores: **28 oct**, 8:00 hora Juárez (7:30 PM IST)
- [ ] Foto del equipo para el recuerdo 📸
