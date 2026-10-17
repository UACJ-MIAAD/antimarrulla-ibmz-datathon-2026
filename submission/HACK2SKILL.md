# 📋 Texto para el envío en Hack2skill

> Lo llena **el líder del equipo registrado en Hack2skill**, desde el dashboard del equipo, después de que los 4 revisen la versión final ([CHECKLIST_ENTREGA.md](../docs/CHECKLIST_ENTREGA.md)). Este archivo solo prepara el texto; no confirma nada del portal.

## Título

`Los Antimarrulla_IBM Z Datathon 2026 Project`

## Tema

T2 · AI Secured: Innovation Without Exposure

## Descripción corta

Tamizaje a ciegas: una IA que calcula el riesgo de diabetes sobre datos cifrados. El hospital cifra los 21 indicadores del paciente con cifrado homomórfico Paillier y se queda con la llave; el servicio de riesgo en IBM LinuxONE evalúa el modelo sin descifrar nada y devuelve un puntaje cifrado que solo el hospital puede abrir.

## Planteamiento del problema

En México, 18.3% de los adultos vive con diabetes y 1 de cada 3 no lo sabe (ENSANUT 2022). En 2024 se registraron 112,577 muertes por diabetes, la segunda causa de muerte del país (microdatos DGIS/INEGI), y 11,550 egresos por diabetes en hospitales de la Secretaría de Salud incluyeron una amputación de miembro inferior (18.4%). Los hospitales tienen los datos para detectar el riesgo antes, pero no pueden compartirlos con un servicio externo de IA sin exponer a sus pacientes.

## Solución

1. El hospital valida y cifra las 21 variables del paciente (enteros, esquema `cdc21-v1`) con su llave pública Paillier de 2048 bits.
2. El servicio de riesgo, sin llave privada, calcula el logit de una regresión logística sobre los cifrados (`Enc(z) = ∏ Enc(xᵢ)^Wᵢ · Enc(B)`) y re-aleatoriza el resultado.
3. El hospital descifra el entero, calcula el riesgo y muestra los factores que más pesan. Es tamizaje, no diagnóstico.

Resultados (mediciones locales y trazables del 17 oct, commit 7937f9f; no LinuxONE): en 2,000 pacientes de prueba, 2,000 de 2,000 enteros descifrados son idénticos a la referencia y el ROC-AUC es el mismo en claro y cifrado (0.808); por la API del hospital en dos contenedores, 129 ms (p50) por solicitud. Modelo en prueba: ROC-AUC 0.826, sensibilidad 0.805, especificidad 0.691. _[Reemplazar por la medición de LinuxONE al tenerla.]_

## Uso de IBM Z / LinuxONE

Diseñado para dos contenedores en la VM de LinuxONE (Ubuntu 24.04, s390x): el del hospital con la llave Paillier y la bóveda AES-256-GCM, y el servicio de riesgo sin llaves, conectados por TLS 1.3 mutuo; la aritmética homomórfica son exponenciaciones con enteros de miles de bits. **Al día de hoy está probado en contenedores locales; falta correrlo y medirlo en LinuxONE.** En la demo ambos contenedores comparten la VM, así que quien la administra queda dentro del entorno de confianza y solo se usan pacientes sintéticos. _[Agregar la evidencia de `make medir-docker` en LinuxONE.]_

## Stack

Python 3.12 · scikit-learn · python-paillier (`phe`) + gmpy2 · cryptography (TLS 1.3, AES-256-GCM) · Docker sobre Ubuntu 24.04 (s390x) · `make`.

## Enlaces

| Campo | Valor |
|-------|-------|
| Repo de GitHub | https://github.com/UACJ-MIAAD/antimarrulla-ibmz-datathon-2026 |
| Video (máx. 3 min) | **Pendiente**: hay borrador sin audio y storyboard en [VIDEO.md](VIDEO.md); faltan voces y la grabación en LinuxONE |
| Pitch deck en PDF | [`Los Antimarrulla_IBM Z Datathon 2026 Project.pdf`](Los%20Antimarrulla_IBM%20Z%20Datathon%202026%20Project.pdf) |
| Flowchart (opcional) | [flowchart/arquitectura.pdf](flowchart/arquitectura.pdf) |
| Prototipo (opcional) | Prototipo interactivo: se corre con `make demo` y se abre en `http://127.0.0.1:8080` (no hay URL pública: la UI solo escucha en localhost). Es distinto del video de la demo |
| Recursos open source | Tabla de [Créditos y librerías](../README.md#créditos-y-librerías) |
| Uso de IA | Sección [Uso de IA](../README.md#uso-de-ia) |
