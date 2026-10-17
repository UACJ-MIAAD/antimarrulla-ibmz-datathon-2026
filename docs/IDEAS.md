# 💡 Ideas candidatas

Tres ideas, las tres en el **Tema 2: AI Secured: Innovation Without Exposure**. Aún **no** hay decisión: se toma en la primera hora del evento con la [matriz de decisión](#-matriz-de-decisión) y se registra en [DECISION.md](DECISION.md).

| | Idea | Una línea |
|---|------|-----------|
| A | 🩺 Diagnóstico médico sobre datos cifrados | Predecir riesgo de diabetes sin ver jamás los datos del paciente |
| B | 💸 Antifraude en remesas con aprendizaje federado | Tres bancos entrenan juntos sin compartir una sola transacción |
| C | 🤝 Asistente privado para personas vulnerables | Orientación confidencial, cifrada de extremo a extremo, sin logs |

---

## 🩺 Idea A · Diagnóstico médico sobre datos cifrados

**Tema:** 2 · AI Secured

### Problema
Los datos clínicos son de los más sensibles que existen, y por eso casi nunca se comparten para entrenar modelos. México tiene una de las prevalencias de diabetes más altas del mundo; detectar el riesgo a tiempo cambia vidas, pero los hospitales no pueden mandar expedientes a un tercero.

### Solución
Un modelo que predice riesgo de diabetes **entrenado y evaluado sobre datos que el equipo nunca ve en texto plano**:
- El "hospital" cifra los datos antes de enviarlos.
- El cómputo ocurre en un entorno protegido en LinuxONE, o directamente sobre datos cifrados con **cifrado homomórfico** (por ejemplo, regresión logística en esquema CKKS).
- Solo el hospital puede descifrar el resultado.

### Cómo se usa IBM Z de forma estructural
- El servicio de inferencia vive en **LinuxONE**; es la única pieza que toca los datos.
- Cifrado/descifrado acelerado por hardware (**CPACF**) y, si el entorno lo ofrece, ejecución en **entorno confidencial** (Secure Execution / Hyper Protect) para que ni el operador del servidor vea los datos.
- Métrica para la slide: costo en latencia del cifrado en LinuxONE vs. laptop.

### Demo en vivo
**Pantalla dividida:**
- Izquierda: lo que ve el servidor → bloques cifrados ilegibles.
- Derecha: lo que ve el hospital → predicciones de riesgo correctas, con su AUC comparado contra el modelo en texto plano.
- Botón "nuevo paciente": se captura un registro, se cifra, viaja, se predice y regresa en segundos.

### Dataset sugerido
- **CDC Diabetes Health Indicators** (BRFSS 2015, UCI ML Repository): ~250 mil registros, indicadores de salud y estilo de vida.
- **Pima Indians Diabetes** (UCI / Kaggle): 768 registros, ideal para prototipo rápido.

### Dificultad estimada
🟠 **Media-alta.** El modelo es sencillo; lo difícil es el cifrado homomórfico (rendimiento, parámetros) y que las librerías funcionen en s390x.

### Riesgos
| Riesgo | Mitigación |
|--------|-----------|
| Librería de cifrado homomórfico sin soporte en s390x | Probarlo en las primeras 2 horas; plan B: entorno confidencial + cifrado en reposo y en tránsito |
| Inferencia cifrada lenta | Modelo lineal, pocas variables, lotes pequeños en la demo |
| Narrativa médica exagerada | Presentarlo como herramienta de **tamizaje**, no de diagnóstico definitivo |

---

## 💸 Idea B · Antifraude en remesas con aprendizaje federado simplificado

**Tema:** 2 · AI Secured

### Problema
México es de los mayores receptores de remesas del mundo, y Ciudad Juárez vive en la frontera de ese flujo. Cada banco o remesadora ve solo su pedazo del fraude; juntar los datos ayudaría, pero compartir transacciones de clientes es inviable legal y comercialmente.

### Solución
**Tres "bancos" simulados** entrenan juntos un detector de fraude **sin compartir transacciones**:
- Cada banco entrena localmente con sus datos.
- Solo viajan los **ajustes del modelo** (pesos/gradientes) a un agregador.
- El agregador combina (promedio federado, FedAvg) y devuelve el modelo global mejorado.
- Opcional: ruido de privacidad diferencial en las actualizaciones.

### Cómo se usa IBM Z de forma estructural
- El **agregador central** corre en **LinuxONE**: es el "tercero de confianza" entre bancos, el papel que IBM Z juega en la banca real.
- Las actualizaciones viajan cifradas y se descifran solo dentro del agregador (CPACF; entorno confidencial si está disponible).
- El modelo global puede servir inferencia en tiempo real desde LinuxONE, cerca de donde ocurren las transacciones.

### Demo en vivo
- Tres paneles, uno por banco, cada uno con su recall de fraude **entrenando solo**.
- Se activan las rondas federadas: las métricas de los tres suben en vivo.
- Panel del agregador: muestra que solo recibe vectores de pesos, nunca filas de transacciones.
- Cierre: "Banco A detecta un patrón de fraude que solo había visto Banco C, sin que C le enseñara un solo dato".

### Dataset sugerido
- **PaySim** (Kaggle): transacciones sintéticas de dinero móvil, muy cercano al caso de remesas.
- **Credit Card Fraud Detection** (ULB, Kaggle): transacciones reales anonimizadas con PCA.
- Partición no idéntica entre bancos (cada uno con distinto perfil de fraude) para que la federación tenga valor.

### Dificultad estimada
🟢 **Media.** FedAvg con scikit-learn (`SGDClassifier`/regresión logística) se implementa a mano en pocas horas, sin depender de frameworks pesados.

### Riesgos
| Riesgo | Mitigación |
|--------|-----------|
| La federación no mejora a los bancos individuales | Diseñar particiones no idénticas; medir y mostrar la ganancia |
| Desbalance extremo de clases | Pesos de clase, métricas AUC-PR y recall |
| Parecer "solo un promedio" | Explicar la amenaza que se evita y mostrar el panel del agregador |

---

## 🤝 Idea C · Asistente privado para personas vulnerables

**Tema:** 2 · AI Secured

### Problema
Personas en situación de violencia, migrantes o personas con problemas de salud mental necesitan orientación, pero no buscan ayuda porque temen que su consulta quede registrada o expuesta. Un chatbot común guarda todo en texto plano.

### Solución
Un **chatbot de orientación** que:
- Cifra cada consulta **de extremo a extremo** en el dispositivo del usuario.
- Procesa la consulta solo dentro de un entorno protegido.
- **Cero logs en texto plano**: no queda rastro legible de quién preguntó qué.
- Responde con orientación y canales oficiales de ayuda (verificados y vigentes).

### Cómo se usa IBM Z de forma estructural
- El motor del asistente corre en **LinuxONE**, en un **entorno confidencial** si está disponible, de modo que ni los administradores pueden leer las conversaciones.
- Llaves de cifrado protegidas por el hardware de la plataforma.
- Logs de auditoría cifrados: se puede demostrar que el servicio funcionó sin revelar el contenido.

### Demo en vivo
- Izquierda: la conversación como la ve el usuario.
- Derecha: lo que ve un administrador con acceso total al servidor → solo texto cifrado.
- Prueba en vivo: buscar en los logs una palabra que el usuario escribió → **cero resultados**.

### Dataset sugerido
- Base de conocimiento curada por el equipo con recursos públicos oficiales (líneas de ayuda, instituciones, procedimientos), **verificando cada dato contra la fuente oficial**.
- Conjunto de preguntas de ejemplo escritas por el equipo para clasificar intenciones.
- Evitar datos de conversaciones reales.

### Dificultad estimada
🔴 **Alta.** Un modelo generativo grande en s390x es arriesgado en 24 horas; la versión factible usa **clasificación de intenciones + recuperación** sobre la base curada.

### Riesgos
| Riesgo | Mitigación |
|--------|-----------|
| Modelo de lenguaje que no corre en s390x o es lento | Clasificador ligero + recuperación; LLM solo si sobra tiempo |
| Respuestas incorrectas en temas delicados | Respuestas cerradas y revisadas; siempre derivar a canales oficiales |
| Parte de "datos y metodología" débil | Medir la clasificación de intenciones con métricas claras |
| Riesgo ético | Aviso claro: no sustituye atención profesional ni de emergencia |

---

## 📊 Matriz de decisión

Se llena **en la primera hora del evento**. Escala sugerida 1–5 en cada columna (5 = mejor). Todo el equipo vota y se anota el promedio.

| Idea | Factibilidad 24h | Fuerza de la demo | Puntos IBM Z | Impacto social | Decisión |
|------|:----------------:|:-----------------:|:------------:|:--------------:|:--------:|
| A · Diagnóstico sobre datos cifrados | | | | | |
| B · Antifraude federado en remesas | | | | | |
| C · Asistente privado | | | | | |

**Reglas de desempate:**
1. Si una idea saca 1–2 en factibilidad, queda fuera aunque gane lo demás.
2. Empate → gana la de mejor demo (es lo que el juez recuerda).
3. Empate persistente → decide el líder. Sin marrulla, sin rondas eternas: **15 minutos máximo**.
