# 🗳️ Acta de decisión

> Insumos: [IDEAS.md](IDEAS.md) y el ranking de 11 ideas con jueces ciegos ([Ranking_Ideas_Antimarrulla.pptx](Ranking_Ideas_Antimarrulla.pptx)).

## Datos de la reunión

| Campo | Valor |
|-------|-------|
| Fecha | 17 de octubre de 2026 (antes del kick-off de las 7:00, hora Juárez) |
| Asistentes | Javier, Álvaro, Carlos, Yazmin |
| Moderó | Javier Augusto Rebull Saucedo |

## Ranking que usamos para decidir

Tres jueces ciegos simulados con IA (perfiles: experto IBM Z, líder AI for Good, investigador de IA y seguridad) calificaron 11 ideas anonimizadas con la rúbrica oficial de 40 pts. Top 5:

| # | Idea | Tema | Total /40 | AI Innovation /20 | Factibilidad /5 |
|---|------|------|----------:|------------------:|----------------:|
| 1 | Transferencias sin fronteras (remesas + OFAC/AML) | T1 · T2 | 29.3 | 13.7 | 3.0 |
| **2** | **Diagnóstico sobre datos cifrados (diabetes)** | **T2** | **29.0** | **15.0** | **2.7** |
| 3 | Antifraude federado en remesas | T2 | 28.3 | 13.0 | 4.0 |
| 4 | Escudo antifraude SPEI | T1 | 28.0 | 12.0 | 4.7 |
| 5 | Escáner post-cuántico para banca | T2 | 27.3 | 10.7 | 3.7 |

## Idea elegida

- **Idea:** #2 del ranking · Diagnóstico sobre datos cifrados
- **Nombre del proyecto:** **Tamizaje a ciegas**
- **Tema oficial:** **T2 · AI Secured: Innovation Without Exposure**
- **Frase de una línea:** *La IA ve el riesgo. Nadie ve al paciente.*

## Por qué esta idea

1. **Es la que mejor encarna el Tema 2.** Es la única que demuestra "IA sobre datos que nadie ve" con una métrica verificable: AUC cifrado vs. AUC en claro.
2. **Tiene el techo más alto en el premio AI Innovation Excellence** (15.0 / 20, el mejor de las 11) y fue la ganadora del juez de innovación.
3. **Consistencia:** los tres jueces le dieron 29 / 40; no depende del gusto de un solo perfil.
4. **Impacto en México medible:** 18.3% de los adultos vive con diabetes, 1 de cada 3 no lo sabe y es la 2.ª causa de muerte (detalle en [FUENTES_DATOS.md](FUENTES_DATOS.md)).
5. **El equipo ya trabaja con datos de diabetes** (incidencia SINAVE y mortalidad EDR): ventaja real para la narrativa y los datos.

## Por qué no las otras

- **#1 Remesas:** mejor promedio, pero dos de tres jueces la ven como T1 y su alcance (tres capas) es el más arriesgado para 24 h.
- **#3 Federado:** demo muy visual, pero FedAvg sobre fraude es un clásico de hackatón (novedad 5.7).
- **#4 SPEI:** la más factible, pero la menos original del top 4.

## El riesgo #1 y cómo lo neutralizamos

Los jueces marcaron la misma debilidad: **TenSEAL/SEAL puede no compilar en s390x** y frenar todo el proyecto. La respuesta de diseño:

| Ruta | Tecnología | Cuándo |
|------|------------|--------|
| **Garantizada** | **Paillier con `python-paillier` (`phe`)**: Python puro, corre en s390x sin compilar nada; basta para una regresión logística | Desde la hora 1 |
| Ambiciosa (extra) | CKKS con TenSEAL u OpenFHE | En la **hora 2** se comprueba si está disponible en LinuxONE |

- **Comprobación:** hora 2. Si CKKS no está disponible, seguimos con Paillier sin tocar el MVP.
- **Plan B de proyecto:** ninguno; la ruta Paillier ya es el plan B técnico.

## Alcance

| Mínimo viable (hora 18, obligatorio) | Deseable (si sobra tiempo) | Fuera de alcance |
|--------------------------------------|----------------------------|------------------|
| Regresión logística entrenada con datos públicos (CDC) | Ruta CKKS con TenSEAL/OpenFHE | Diagnóstico clínico definitivo |
| Inferencia cifrada con Paillier en LinuxONE | Granite explicando el resultado al paciente | Datos reales de pacientes |
| Pantalla dividida: servidor (cifrado) vs. hospital (riesgo) | Mapa de incidencia SINAVE y mortalidad EDR por entidad | App móvil |
| Métrica: AUC en claro vs. cifrado + latencia por paciente | Procesamiento por lotes y pacientes/minuto | Entrenamiento cifrado |
| Dos contenedores Docker en LinuxONE con capturas de evidencia | | |

## Uso de IBM Z comprometido

- Todo corre en **LinuxONE Community Cloud** (s390x) en **dos contenedores Docker**: el del hospital (llave privada) y el servicio de riesgo (sin llave).
- **Cómputo pesado:** la aritmética homomórfica son exponenciaciones modulares con enteros de miles de bits.
- **Cifrado por hardware:** AES-256-GCM en reposo vía OpenSSL, que en IBM Z puede usar CPACF. `openssl speed` solo mide la CLI: la evidencia es la de [PROYECTO.md](PROYECTO.md) (`lscpu`, `cpacfinfo`, versiones de OpenSSL de la CLI y de `cryptography`, y la medición dentro de la app).
- **Labs obligatorios:** el patrón "predictivo + generativo" del lab 2 se reflejaría en Granite explicando el resultado (extra, aún no integrado).

## Dataset

| Uso | Dataset | Licencia |
|-----|---------|----------|
| Entrenar el modelo | CDC Diabetes Health Indicators (UCI ID 891): 253,680 registros, 21 indicadores | Dominio público (UCI remite a la fuente; Kaggle lo marca CC0) |
| Contexto e impacto en México | Incidencia SINAVE (SUIVE-1, Anuarios de Morbilidad DGE) y mortalidad EDR (INEGI) | Información pública; citar fuente |

Detalle en [FUENTES_DATOS.md](FUENTES_DATOS.md) y [data/README.md](../data/README.md).

## Firmas (✅ = de acuerdo)

| Integrante | ✅ |
|------------|:--:|
| Javier Augusto Rebull Saucedo | |
| Álvaro Hernández Jarquín | |
| Carlos Enrique Gonzalez Moran | |
| Yazmin Ivonne Flores Martinez | |

## Decisiones tras la auditoría externa (17 oct)

| # | Tema | Decisión | Consecuencia |
|---|------|----------|--------------|
| 1 | Épica E5 (pronóstico a 52 semanas) y ruta CKKS | **Se quedan como extra (Plus).** No se saca nada del plan. | El MVP sigue siendo Paillier + demo de la hora 18. E5 y CKKS no bloquean el MVP; si en la hora 12 la demo cifrada va atrasada, E5 se congela en lo que tenga ([PRONOSTICO.md](PRONOSTICO.md)). |
| 2 | Declaración de uso de IA | **Pendiente:** se quitó del README el 17 oct; el equipo decide dónde va. | Las reglas piden declararla ([REGLAS.md](REGLAS.md) §4). |
| 3 | Frontera de confianza | **Hospital y servicio de riesgo en la misma VM**, con la frontera declarada. | Quien administra la VM queda dentro de la frontera; la demo usa solo pacientes sintéticos. Detalle en [PROYECTO.md](PROYECTO.md) y en la slide 5. |
| 4 | Correos del equipo en el README | **Se quedan**, con acuerdo de los cuatro. | Sin cambios. |

