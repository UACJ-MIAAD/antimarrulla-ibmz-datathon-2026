# 📈 Épica E5 · Pronóstico y planeación financiera

> **Prioridad: Plus.** Se construye en paralelo al núcleo cifrado (E3) y nunca a costa de la demo de la hora 18.
> Historias US-5.1 a US-5.5 en [site/status.json](../site/status.json) · responsables: Yazmin (datos y planeación), Carlos (modelos), Javier (dashboard).

> **Estado (17 oct 2026):** lo implementado está en [Implementación](#implementación-17-oct-2026). El diseño de abajo es el plan original; de él **no** se implementó: SARIMA, Prophet, la vista de mapa, el total T1 + T2 y la ejecución en LinuxONE (el ajuste corrió en local).

## Para qué

Tamizar antes cambia cuántos casos llegan y cuándo. Para que una secretaría de salud **presupueste** la atención, necesita saber cuántos casos nuevos de diabetes esperar **en las próximas 52 semanas**, por estado y sexo, y cuánto cuesta atenderlos.

## Datos (ya en el repo)

`data/sinave/tipo{1,2}/products.csv`: **111 series semanales por tipo** de diabetes (**222 entre T1 y T2**), 2014 → 2026 semana 30. **La última observación es la semana del 27 de julio de 2026**: al momento del evento hay ~12 semanas sin datos, así que el horizonte real cubre ~12 semanas de *nowcast* + 52 de pronóstico. Las series no son independientes: estados, regiones, nacional y sexos son agregaciones unas de otras.

| Nivel | Series |
|-------|-------:|
| Estado × {hombres, mujeres, general} | 96 |
| Región SINAVE (centro, norte, occidente, sureste) × {hombres, mujeres, general} | 12 |
| Nacional × {hombres, mujeres, general} | 3 |

## Enfoque

1. **Horizonte:** 52 semanas epidemiológicas hacia adelante, con intervalos de predicción del 80% y 95%.
2. **Modelos candidatos** (todos open source y con ruta para s390x):
   - Referencia: ingenuo estacional (misma semana del año anterior).
   - **ETS / Holt-Winters** y **SARIMA** (`statsmodels`): ruta segura en LinuxONE.
   - Prophet solo si se instala en s390x (depende de `cmdstan`; probarlo en la hora 2 junto con TenSEAL).
3. **Selección por serie:** el modelo con menor **SMAPE** en validación hacia atrás. Un backtest de 13 semanas **no valida por sí solo un horizonte de 52**: usar además origen móvil con horizontes de 13, 26 y 52 semanas sobre 2023–2025 y reportar el error por horizonte. Si dos modelos quedan a menos de 5% de SMAPE, desempata el MAE.
4. **Series con pocos casos** (menos de 5 casos en 52 semanas, típico de T1 en estados chicos): se usa la proporción del estado dentro de su **región** aplicada al pronóstico regional.
5. **Coherencia jerárquica:** los estados suman a su región y las regiones al nacional (reconciliación *bottom-up* o proporcional).
6. **COVID:** 2020–2021 se marcan como periodo atípico (variable indicadora o se excluyen del ajuste).
7. **Enteros:** los pronósticos se redondean a casos enteros, sin negativos.

## Planeación financiera

`presupuesto(estado, sexo, semana) = casos_pronosticados × costo_unitario`

- El **costo unitario es un parámetro editable** en el dashboard (por ejemplo, costo anual de atención por paciente nuevo). **No se inventa:** se captura con su fuente (literatura o tabuladores oficiales) y se muestra en pantalla.
- Escenarios: base (pronóstico), conservador (banda superior del 80%) y estrés (banda superior del 95%).
- Totales acumulados por trimestre y por año, por estado y sexo.

## Dashboard (US-5.5)

| Control | Opciones |
|---------|----------|
| Tipo | T1 · T2 · total |
| Geografía | Nacional · región · estado |
| Sexo | Hombres · mujeres · general |
| Costo unitario | Campo editable con fuente |

| Vista | Contenido |
|-------|-----------|
| Curva | Real 2014–2026 + pronóstico 52 semanas con bandas |
| Mapa | Casos esperados por 100,000 habitantes en 52 semanas, usando `data/geo/estados_mx.geojson` |
| Tabla | Casos y presupuesto por trimestre (base, conservador, estrés) |
| Calidad | SMAPE del modelo elegido y número de semanas de validación |

## Dónde corre

El ajuste de las 222 series corre en **LinuxONE** (en el contenedor del servicio de riesgo, o en uno propio) y se exporta como JSON para el dashboard. Así suma al criterio técnico: más cómputo de IA/ML corriendo en IBM Z.

## Reglas

- El código se escribe **durante el evento**. Tomamos ideas de enfoque de trabajos previos del equipo (horizonte, selección por SMAPE, respaldo regional), **no código**.
- Si en la hora 12 la demo cifrada (E3 + E6) va atrasada, E5 se congela en lo que tenga (por ejemplo, solo la curva nacional de T2) y se presenta como siguiente paso.

## Implementación (17 oct 2026)

`make pronostico` → `src/tamizaje/pronostico.py` → `artefactos/pronostico/e5_pronostico_v1.json` y el tablero [site/pronostico.html](../site/pronostico.html). Corrió en local (macOS), no en LinuxONE.

| Decisión | Implementado |
|----------|--------------|
| Horizonte | Última observación 27 jul 2026: **63 pasos** = 11 semanas de puente hasta la semana de referencia (17 oct) + **52 semanas** (19 oct 2026 a 11 oct 2027) |
| Ajuste | Solo 2022 en adelante (COVID fuera); semanas no observadas interpoladas linealmente y contadas por serie |
| Modelos | Ingenuo estacional y ETS Holt-Winters aditivo con tendencia amortiguada (s = 52). 148 series ETS, 74 ingenuo estacional |
| Selección | Backtest con hasta 4 orígenes de 52 semanas (≥ 104 de ajuste); SMAPE h1–52, empate a 5% → MAE. **Es selección, no un error independiente** |
| Bandas 80/95 | **Exploratorias**: cuantiles de los errores de la selección por tramo (h > 52 usa el último). Marginales por serie y semana |
| Pocos casos | < 5 casos en 52 semanas → proporción dentro de su región (ninguna serie lo necesitó) |
| Coherencia | Proporcional de arriba abajo por tipo y sexo: nacional → regiones → estados. "General" no se fuerza a hombres + mujeres |
| Evaluación | **Anidada y fuera de muestra**: en 2 orígenes (17 feb y 19 may 2025) el sistema completo (selección, bandas, respaldo y reconciliación) se corre solo con datos previos y se compara contra las 63 semanas reales siguientes |
| Presupuesto | Casos × costo unitario **solo con fuente**: sin costo documentado no se calcula. Los escenarios suman límites semanales y **no son un intervalo conjunto** |

**Evaluación fuera de muestra del sistema reconciliado** (promedio de series y orígenes):

| Nivel | SMAPE h1–13 | h14–26 | h27–52 | h53–63 | h12–63 | Cobertura real 80% (h12–63) | Cobertura real 95% (h12–63) |
|-------|------------:|-------:|-------:|-------:|-------:|----------------------------:|----------------------------:|
| Nacional | 14.6% | 13.7% | 12.9% | 13.3% | 13.1% | 64% | 87% |
| Regiones | 23.2% | 23.7% | 25.6% | 26.4% | 25.0% | 65% | 81% |
| Estados | 59.0% | 58.1% | 60.0% | 61.3% | 59.7% | 63% | 79% |

Lectura: las bandas son **más angostas de lo que dicen** (80% nominal cubre ~63–65%; 95% cubre 79–87%), y a nivel estado el error es alto (incluye T1 con pocos casos). Solo 2 orígenes: es una evaluación orientativa.

Nacional, 52 semanas (punto): T2 general 574,746 casos (últimas 52 observadas: 555,474); T1 general 3,834 (últimas 52: 3,857). Casos **notificados**, no casos reales.
