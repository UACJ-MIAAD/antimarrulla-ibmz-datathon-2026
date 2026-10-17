# 🎯 Criterios de evaluación y cómo exprimirlos

**Total base: 70 pts · Bonus: hasta +10 pts.**

| Criterio | Puntos | Dueño interno |
|----------|-------:|---------------|
| Manejo de datos y metodología | 20 | Yazmin (datos) + Álvaro (modelado) |
| Innovación y creatividad | 20 | Todo el equipo |
| Integración con tecnología IBM Z | 15 | Carlos (infra LinuxONE) |
| Presentación y storytelling | 10 | Javier (pitch) |
| Reproducibilidad y documentación | 5 | Javier (docs) + Álvaro (scripts) |
| **Bonus** · narrativa de impacto comunitario | +5 | Javier |
| **Bonus** · demo en vivo pulida | +3 | Yazmin (demo) + Carlos (LinuxONE) |
| **Bonus** · repo open source bien documentado | +2 | Javier |

> Lectura rápida: **datos + innovación = 40 de 70.** Ahí se gana. IBM Z vale 15: si se siente "pegado con cinta", se pierde.

---

## 1. Manejo de datos y metodología · 20 pts

**Qué buscan:** que entendamos los datos y que el pipeline sea riguroso.

Estrategias:
- **EDA visible** en `notebooks/01_eda.ipynb`: distribución de clases, nulos, sesgos, outliers.
- **Baseline primero**, mejora después. Mostrar "baseline vs. modelo final" en una tabla.
- **Validación honesta:** train/test separados antes de cualquier transformación; validación cruzada cuando el dataset sea chico.
- **Métricas adecuadas al problema:** en fraude y salud no basta la accuracy → recall, precisión, F1, AUC-PR, matriz de confusión.
- **Clases desbalanceadas:** decir cómo se trataron (pesos, umbral, re-muestreo) y por qué.
- **Privacidad como parte de la metodología:** medir el costo en precisión de cifrar o federar (por ejemplo, "en texto plano 0.82 AUC, cifrado 0.81").
- **Limitaciones declaradas.** Un juez confía más en quien reconoce lo que su modelo no hace.

## 2. Innovación y creatividad · 20 pts

**Qué buscan:** algo que no hayan visto 40 veces en el día.

Estrategias:
- Enmarcar el problema desde un ángulo local y concreto (frontera, remesas, salud en Juárez) en lugar de genérico.
- Combinar dos ideas que rara vez se juntan: privacidad fuerte + utilidad real medible.
- Un "momento wow" en la demo: algo que el juez pueda **ver** (datos ilegibles a la izquierda, predicción correcta a la derecha).
- Nombre de proyecto memorable y una frase que lo resuma.

## 3. Integración con tecnología IBM Z · 15 pts

**Qué buscan:** que IBM Z sea **estructural**, no decorativo. Si se puede quitar IBM Z sin que cambie nada, son puntos perdidos.

Estrategias:
- Correr el pipeline en **LinuxONE** (s390x) y mostrarlo en la demo (terminal, `uname -m`, logs).
- Usar capacidades propias de la plataforma cuando estén disponibles en el entorno del evento (confirmarlo en el setup del 16 oct):
  - Cifrado acelerado por hardware (CPACF) y cifrado generalizado.
  - Cómputo confidencial / entornos aislados (Secure Execution, Hyper Protect).
  - Inferencia de IA en el chip (IBM Z Integrated Accelerator for AI) y herramientas como Snap ML o el IBM Z Deep Learning Compiler.
- Una slide de arquitectura que marque en color qué piezas viven en IBM Z y **por qué ahí**.
- Medir algo: latencia, throughput o costo del cifrado en LinuxONE vs. laptop.

## 4. Presentación y storytelling · 10 pts

Estrategias:
- Estructura **Problema → Persona → Solución → Demo → Impacto → Próximos pasos** ([submission/PITCH.md](../submission/PITCH.md)).
- Abrir con una persona y un dato, no con la arquitectura.
- Ensayar con cronómetro. 3 minutos son 3 minutos.
- Una idea por slide, letra grande, cero párrafos.

## 5. Reproducibilidad y documentación · 5 pts

Estrategias:
- `README` con quickstart que funcione en máquina limpia (alguien que no escribió el código lo prueba en la hora 21).
- `requirements.txt` con versiones fijadas al final del evento (`pip freeze`).
- Semillas aleatorias fijas.
- Instrucciones para obtener el dataset (link + script de descarga), ya que no se sube al repo.

---

## 🎁 Bonus (hasta +10)

| Bonus | Pts | Cómo lo aseguramos |
|-------|----:|--------------------|
| Narrativa de impacto comunitario | +5 | Conectar con una comunidad real (pacientes con diabetes en México, familias que reciben remesas, personas en situación vulnerable en Juárez). Dar cifras públicas con fuente. |
| Demo en vivo pulida | +3 | Ensayo completo en la hora 19. Plan B grabado por si falla la red. Datos de demo precargados. |
| Repo open source bien documentado | +2 | Este repo: licencia MIT, README claro, créditos, CONTRIBUTING, historial limpio. |

## ✅ Autoevaluación (llenar en la hora 21)

| Criterio | Máx | Nuestra estimación | Qué falta para subir |
|----------|----:|-------------------:|----------------------|
| Datos y metodología | 20 | | |
| Innovación | 20 | | |
| IBM Z | 15 | | |
| Storytelling | 10 | | |
| Reproducibilidad | 5 | | |
| Bonus | 10 | | |
| **Total** | **80** | | |
