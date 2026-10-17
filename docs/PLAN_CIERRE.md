# Plan de cierre y siguiente acción del equipo

> Corte: 17 de octubre de 2026. El código funciona en local; falta evidencia versionada de LinuxONE, labs, revisión humana y video final. Los mensajes de «6/6» y «8/8» describen pruebas preliminares reportadas por Carlos, no sustituyen resultados del protocolo de 21 variables ni capturas del proveedor. El estado por historia vive en `site/status.json`.

## Por dónde seguir ahora

**Javier / coordinación: dedica los próximos 15 minutos a cerrar quién tiene cada evidencia y quién sube el video.** Confirma el líder registrado en Hack2skill, abre el dashboard, reparte la tabla de abajo y prepara el guion con Yazmin. Revisa el formulario de asistencia y el estado real de los dos labs. El código y los extras no deben ocupar el margen reservado para el envío.

| Prioridad | Responsable | Siguiente acción concreta | Evidencia que permite cerrarla |
|-----------|-------------|--------------------------|-------------------------------|
| 1 | Carlos, con Álvaro | Fijar el mismo commit, correr `make verify-docker`, `make demo-docker`, `make medir-docker FINAL=1` y `make medir-api-docker FINAL=1` en la VM real | JSON/MD de mediciones, commit y hashes, dashboard Community Cloud y capturas declaradas en `submission/evidencias/linuxone/REGISTRO.json` |
| 1 | Equipo; Javier coordina | Confirmar realización de los dos labs y asistencia; completar lo pendiente con fechas reales; decidir el envío de la consulta factual al organizador | `submission/evidencias/labs/REGISTRO.json`, capturas y respuesta del organizador si aplica; no modificar fechas del historial |
| 2 | Otro integrante que no escribió el cambio revisado | Correr el clon fijado y revisar protocolo, llaves, datos y límites con `docs/REVISION.md` | Review en GitHub y registro con nombre, fecha, commit y comandos; no autoaprobación ni aprobación de Codex como integrante |
| 2 | Yazmin y Javier | Capturar el modelo y demo corriendo en LinuxONE, grabar voces y montar video final de 170–180 s | Archivo con audio, duración comprobada por `ffprobe`, enlace público probado en incógnito y `submission/VIDEO_REGISTRO.json` |
| 3 | Álvaro hospital; Carlos servicio | Solo con el MVP anterior resuelto, correr la prueba opcional en dos hosts, con sintéticos por defecto | Reporte estricto aprobado, IDs de host distintos y versiones coincidentes; un ensayo local no cierra esta historia |
| 3 | Yazmin | Pulir el formulario existente de 21 variables si queda margen: etiquetas comprensibles, códigos CDC explícitos, campos obligatorios y mensajes de validación | Captura y prueba sobre un paciente sintético; no subir expedientes reales ni añadir cargas masivas antes de la entrega |
| 4 | Javier, con los cuatro | Fijar versión final, sincronizar PDF/sitio/guion, completar declaración de IA, regenerar paquete y enviar desde el líder | `make package FINAL=1`, enlaces verificables y captura de confirmación de Hack2skill |

## Comandos y alcance

Las instrucciones de VM están en [LINUXONE.md](LINUXONE.md). El chequeo específico del proyecto es `make instance-claims`, o `python tests/instance/05_test_claims.py` con el Python del entorno configurado. Importa el código real y guarda resultados con procedencia en `submission/evidencias/instancia/`. No instala dependencias cuando se invoca directamente; `tests/instance/run_all.sh` sí incluye instalación y debe ejecutarlo el responsable de la VM.

`make medir` compara flotante, punto fijo y Paillier sobre la misma muestra del CDC; ahora también mide el tiempo del logit en claro y punto fijo, en microsegundos por paciente. El costo de evaluar cifrados se mide separado del cifrado, red, descifrado y bóveda. No comparar el tiempo del logit en claro con el recorrido HTTPS como si fueran la misma operación.

La demo y el ensayo de dos máquinas usan **sintéticos por defecto**. `DATOS=cdc` es un benchmark explícito sobre datos públicos anonimizados; sus AUC no describen pacientes sintéticos. En sintéticos se verifica exactitud numérica y transporte, sin inventar etiquetas ni métricas clínicas. La segunda VM es un extra: se conserva el MVP aprobado de dos contenedores en una VM con administrador dentro de confianza.

## Cortes y plan B

| Corte | EDT, Nueva York | Ciudad Juárez | Decisión |
|-------|-----------------|---------------|----------|
| Chequeo H12 | 17 oct 21:00 | 17 oct 19:00 | Si falta el recorrido real en LinuxONE, pausar formulario, segunda VM, Granite y CKKS; concentrar a Carlos y Álvaro en el MVP |
| Demo H18 | 18 oct 03:00 | 18 oct 01:00 | Capturar demo y evidencia; congelar el alcance del video |
| Congelamiento H20 | 18 oct 05:00 | 18 oct 03:00 | Solo correcciones, documentación y montaje; no nuevas funcionalidades |
| Meta interna de envío | 18 oct 09:00 | 18 oct 07:00 | Envío por el líder después de revisión de los cuatro |
| Cierre según calendario del repo | 18 oct 12:30 | 18 oct 10:30 | Verificar esta hora en el portal; conservar el margen de 3 h 30 min |

Si la segunda VM falla, usar el MVP de una VM, sin afirmar separación entre hosts. Si falla el formulario nuevo, usar los perfiles sintéticos y editor de 21 variables que ya existen. Si falta un costo con fuente, E5 conserva casos y bandas exploratorias, sin presupuesto. Si faltan capturas, voces o LinuxONE, registrar el bloqueo con responsable; un borrador o una medición del Mac no sustituyen esos entregables.

Se respeta el turno de descanso acordado en [ROLES.md](ROLES.md); antes de descansar, dejar commit, estado y responsable que continúa. Las actualizaciones del plan en una rama no se presentan como publicadas hasta verificar el despliegue. Netlify y su badge se conservan.
