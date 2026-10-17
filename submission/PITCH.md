# 🎤 Guion del video · Tamizaje a ciegas

> Presentación: [Los_Antimarrulla_Pitch_Tamizaje.pptx](Los_Antimarrulla_Pitch_Tamizaje.pptx) (8 slides; el guion también está en las notas del orador).
> **Límite duro: 3:00. Meta: 2:50.** ~130 palabras por minuto → ~370 palabras.
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
| 7 | Datos y modelo | 0:12 | 2:37 | Yazmin |
| 8 | Impacto y cierre | 0:13 | 2:50 | Yazmin |

---

## 1. Portada · 0:10
Somos Los Antimarrulla, de la UACJ. Nuestro proyecto es **Tamizaje a ciegas**: una IA que calcula el riesgo de diabetes sobre datos cifrados en IBM LinuxONE.

## 2. El problema · 0:25
En México, **18.3%** de los adultos vive con diabetes y **uno de cada tres** no lo sabe. En 2024 murieron **112 mil** personas por diabetes, la segunda causa de muerte, y solo en hospitales de la Secretaría de Salud hubo **más de 11 mil amputaciones**. Los hospitales tienen los datos para detectarla antes, pero no pueden compartirlos. ¿Y si la IA pudiera calcular el riesgo sin ver jamás los datos del paciente?

## 3. La solución · 0:20
El hospital cifra los 21 indicadores del paciente y se queda con la llave. LinuxONE calcula el riesgo sobre números cifrados. El resultado regresa cifrado; solo el hospital lo abre, y Granite lo explica en lenguaje claro. Es tamizaje: decide a quién hacerle una prueba de glucosa primero.

## 4. Cifrado homomórfico · 0:25
Usamos cifrado homomórfico Paillier: multiplicar dos cifrados suma sus valores, y elevar un cifrado a una potencia lo multiplica. Con eso, el servidor calcula el puntaje del modelo **sin descifrar nada**. Sumamos TLS 1.3 en tránsito y AES-256-GCM acelerado por el hardware de IBM Z en reposo. Ni el servidor ni nosotros vemos un solo dato.

## 5. Por qué IBM Z · 0:30
*(Mostrar la terminal de la VM: `uname -m` → `s390x`, los dos contenedores corriendo y el modelo cargado.)*
Todo corre en LinuxONE, en dos contenedores: el del hospital, con la llave, y el servicio de riesgo, sin llave. La aritmética homomórfica son exponenciaciones con enteros de miles de bits: cómputo pesado y seguro, justo para lo que está hecho IBM Z.

## 6. Demo en vivo · 0:35
*(Pantalla dividida.)*
A la izquierda, lo que ve el servidor: solo números cifrados. A la derecha, lo que ve el hospital: riesgo alto, los factores principales y la explicación de Granite. Abajo, medido en vivo en LinuxONE: el AUC en claro contra el cifrado [**cifra real**], y la latencia por paciente [**cifra real**].

## 7. Datos y modelo · 0:12
Entrenamos con 253 mil registros públicos de los CDC. Los datos de pacientes solo llegan cifrados.

## 8. Impacto y cierre · 0:13
Detectar antes es evitar amputaciones y muertes. Tamizaje temprano, sin entregar un solo expediente. **La IA ve el riesgo. Nadie ve al paciente.** Somos Los Antimarrulla. Gracias.

---

## ✅ Antes de grabar

- [ ] Reemplazar las [**cifras reales**] de la demo con lo medido en LinuxONE (nunca inventar)
- [ ] Cronometrado en 2:50 o menos, dos veces seguidas
- [ ] Se ven en pantalla la instancia LinuxONE, los contenedores y el modelo
- [ ] Captura de `openssl speed -evp aes-256-gcm` en `evidencias/`
- [ ] Decir "tamizaje", nunca "diagnóstico"
- [ ] Audio probado
- [ ] Exportar las slides a PDF: `Los Antimarrulla_IBM Z Datathon 2026 Project.pdf` (obligatorio)
