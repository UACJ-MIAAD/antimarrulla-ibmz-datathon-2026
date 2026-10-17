# 📈 Épica E5 · Pronóstico y planeación financiera

> **Prioridad: Plus.** Se construye en paralelo al núcleo cifrado (E3) y nunca a costa de la demo de la hora 18.
> Historias US-5.1 a US-5.5 en [site/status.json](../site/status.json) · responsables: Yazmin (datos y planeación), Carlos (modelos), Javier (dashboard).

## Para qué

Tamizar antes cambia cuántos casos llegan y cuándo. Para que una secretaría de salud **presupueste** la atención, necesita saber cuántos casos nuevos de diabetes esperar **en las próximas 52 semanas**, por estado y sexo, y cuánto cuesta atenderlos.

## Datos (ya en el repo)

`data/sinave/tipo{1,2}/products.csv`: **111 series semanales** por tipo de diabetes (T1 y T2), 2014 → 2026 semana 30.

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
3. **Selección por serie:** el modelo con menor **SMAPE** en las últimas 13 semanas observadas (validación hacia atrás). Si dos modelos quedan a menos de 5% de SMAPE, desempata el MAE.
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

El ajuste de las 111 series corre en **LinuxONE** (en el contenedor del servicio de riesgo, o en uno propio) y se exporta como JSON para el dashboard. Así suma al criterio técnico: más cómputo de IA/ML corriendo en IBM Z.

## Reglas

- El código se escribe **durante el evento**. Tomamos ideas de enfoque de trabajos previos del equipo (horizonte, selección por SMAPE, respaldo regional), **no código**.
- Si en la hora 12 la demo cifrada (E3 + E6) va atrasada, E5 se congela en lo que tenga (por ejemplo, solo la curva nacional de T2) y se presenta como siguiente paso.
