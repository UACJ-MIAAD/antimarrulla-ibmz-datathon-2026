# 🎤 Guion del video · Tamizaje a ciegas

> Presentación: [Los_Antimarrulla_Pitch_Tamizaje.pptx](Los_Antimarrulla_Pitch_Tamizaje.pptx) (8 slides; el guion también está en las notas del orador).
> **Límite duro: 3:00. Meta: 2:50.** ~130 palabras por minuto. El guion tiene **~300 palabras habladas (≈2:20)**: el resto queda para pausas y para mostrar la instancia, el modelo y los resultados.
>
> La guía exige que el video cubra: el problema, **datos que lo respaldan**, la solución y, sobre todo, **cómo aprovecha IBM Z**: stack tecnológico, **instancia LinuxONE y modelo en pantalla**.

| # | Slide | Tiempo | Acumulado | Quién habla |
|---|-------|-------:|----------:|-------------|
| 1 | Portada | 0:10 | 0:10 | Yazmin |
| 2 | El problema | 0:25 | 0:35 | Yazmin |
| 3 | La solución | 0:20 | 0:55 | Carlos |
| 4 | Cifrado homomórfico | 0:25 | 1:20 | Carlos |
| 5 | Por qué IBM Z (+ **pantalla de LinuxONE**) | 0:30 | 1:50 | Álvaro |
| 6 | Demo en vivo | 0:35 | 2:25 | Javier |
| 7 | Datos y modelo | 0:08 | 2:33 | Yazmin |
| 8 | Impacto y cierre | 0:17 | 2:50 | Yazmin |

---

## 1. Portada · 0:10
Somos Los Antimarrulla, de la UACJ. Nuestro proyecto es **Tamizaje a ciegas**: una IA que calcula el riesgo de diabetes sobre datos cifrados en IBM LinuxONE.

## 2. El problema · 0:25
En México, **18.3%** de los adultos vive con diabetes y **uno de cada tres** no lo sabe. Es la segunda causa de muerte: **112 mil** en 2024. Los hospitales tienen los datos para detectarla antes, pero no pueden compartirlos. ¿Y si la IA calculara el riesgo sin ver esos datos?

## 3. La solución · 0:20
El hospital cifra los 21 indicadores del paciente y se queda con la llave. LinuxONE calcula el riesgo sobre números cifrados; solo el hospital abre el resultado y ve los factores que más pesan. Es tamizaje: decide a quién hacerle primero una prueba de glucosa.

## 4. Cifrado homomórfico · 0:25
Usamos cifrado homomórfico Paillier: multiplicar cifrados suma sus valores y elevarlos a una potencia los multiplica. Así el servidor calcula el puntaje del modelo **sin descifrar nada**. Además, TLS 1.3 en tránsito y AES-256-GCM en reposo.

## 5. Por qué IBM Z · 0:30
*(Mostrar la terminal de la VM: `uname -m` → `s390x`, los dos contenedores corriendo y el modelo cargado.)*
*(Decir "corre en LinuxONE" solo si ya se grabó la VM; si no, "está hecho para LinuxONE".)* Todo corre en LinuxONE, en dos contenedores: el del hospital, con la llave, y el servicio de riesgo, sin ella. En la demo comparten VM; en producción, el del hospital vive en sus instalaciones. La aritmética homomórfica son exponenciaciones con enteros de miles de bits: cómputo pesado, justo para IBM Z.

## 6. Demo en vivo · 0:35
*(Pantalla dividida real: `make demo`, paciente sintético C.)*
A la izquierda, lo que ve el servicio de riesgo: 21 números cifrados y el puntaje cifrado que devuelve. A la derecha, lo que ve el hospital: el riesgo, la decisión frente al umbral y los factores que más pesan. En 2,000 pacientes de prueba, los 2,000 resultados descifrados son idénticos y el AUC cifrado es igual al de claro [**reemplazar por la medición de LinuxONE**].

## 7. Datos y modelo · 0:08
Entrenamos con 253 mil registros públicos de los CDC: AUC de 0.83 y 80% de sensibilidad. Los datos de pacientes solo llegan cifrados.

*(Si preguntan: en adultos mexicanos de ENSANUT, un modelo reducido baja a AUC 0.77 y subestima el riesgo; habría que recalibrar.)*

## 8. Impacto y cierre · 0:17
En 2024, más de 11 mil hospitalizaciones por diabetes en la Secretaría de Salud incluyeron una amputación. Queremos detectar antes sin entregar un solo expediente. **La IA ve el riesgo. Nadie ve al paciente.** Gracias.

---

## ✅ Antes de grabar

- [ ] Reemplazar las cifras locales de la demo por las de `make medir-docker` en LinuxONE (nunca inventar)
- [ ] Cronometrado en 2:50 o menos, dos veces seguidas, **con las pantallas** (instancia, modelo y resultado deben verse al menos 10 s en total); anotar la duración del archivo final
- [ ] Se ven en pantalla la instancia LinuxONE, los contenedores y el modelo
- [ ] Capturas de `lscpu`/`cpacfinfo` y de las versiones de OpenSSL (CLI y `cryptography`) en `evidencias/`
- [ ] Decir "tamizaje", nunca "diagnóstico"
- [ ] Audio probado
- [ ] Exportar las slides a PDF: `Los Antimarrulla_IBM Z Datathon 2026 Project.pdf` (obligatorio)
