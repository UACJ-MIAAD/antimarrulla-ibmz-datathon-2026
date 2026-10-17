# 🖧 Prueba de dos máquinas: el servicio nunca ve datos en claro

> Complementa la demo de [LINUXONE.md](LINUXONE.md), que corre los dos contenedores en **la misma VM**. Aquí el
> servicio de riesgo corre en **una VM** y el hospital en **otra**, con **registros reales** de la partición de prueba
> del CDC, y al final una auditoría deja en `submission/evidencias/dos_maquinas/` la prueba de que el servicio solo
> manejó cifrados.

| | VM A · servicio de riesgo | VM B · hospital |
|---|---|---|
| Tiene | certificado TLS del servicio | llave privada Paillier (en memoria) y certificado de cliente |
| No tiene | llave privada Paillier, certificado del hospital | — |
| Corre | `tamizaje.servicio` con `SERVICIO_EVIDENCIA` | `tamizaje.dos_maquinas hospital` |
| Deja | bytes exactos recibidos/enviados + bitácora de auditoría | bitácora con hashes y resultados descifrados + resumen |

Las dos VM necesitan el repo en `main` y Docker (`tests/instance/04_docker_check.sh`). Todo corre en las imágenes de
Ubuntu 24.04, así que no hay que compilar nada en s390x.

## 0. Ensayo en una sola máquina (opcional, 2 min)

```bash
make ensayo-dos-maquinas        # con el venv: servicio en otro proceso, 20 registros, auditoría en modo ensayo
```

Debe terminar con **ENSAYO APROBADO**. No es evidencia: solo comprueba el flujo.

## 1. VM A (servicio): certificados con su IP

```bash
make secretos-dos-maquinas SERVICIO_IP=<IP pública de la VM A>
```

Crea `~/.tamizaje-dos-maquinas/servicio/certs` (CA, certificado del servicio con esa IP) y **mueve** las credenciales
del hospital a `~/.tamizaje-dos-maquinas/para_hospital`. Cópialas a la VM B y bórralas de la A:

```bash
scp -r ~/.tamizaje-dos-maquinas/para_hospital USUARIO@IP_VM_B:~/.tamizaje-dos-maquinas/
rm -r ~/.tamizaje-dos-maquinas/para_hospital
```

(Si no hay SSH entre las VM, pásalas por tu laptop con dos `scp`.)

## 2. VM A: arrancar el servicio

```bash
make servicio-remoto-docker     # se queda en primer plano mostrando cada solicitud; Ctrl+C al terminar
```

Si la VM tiene firewall: `sudo ufw allow 8443/tcp`. Desde la VM B, `nc -vz IP_VM_A 8443` debe conectar.
Si la red solo deja pasar el puerto 22, usa un túnel en la VM B (`ssh -N -L 8443:localhost:8443 USUARIO@IP_VM_A`) y
en el paso 3 `SERVICIO_URL=https://localhost:8443`; el certificado ya incluye `localhost`.

## 3. VM B (hospital): mandar registros reales cifrados

```bash
make hospital-remoto-docker SERVICIO_URL=https://<IP de la VM A>:8443 N=200
```

Toma 200 registros estratificados y reproducibles de la partición de prueba del CDC (semilla 2026), cifra cada uno,
lo manda por TLS 1.3 mutuo, descifra y compara con el cálculo en claro. Al final imprime enteros idénticos, ROC-AUC
flotante vs. cifrado y latencia p50/p95. Mientras corre, la terminal de la VM A muestra solo ids, tamaños y
`llave_privada_en_memoria=False`.

## 4. Auditoría (en la VM A)

Copia la bitácora del hospital a la VM A y audita:

```bash
scp -r USUARIO@IP_VM_B:~/.tamizaje-dos-maquinas/bitacora_hospital ~/.tamizaje-dos-maquinas/
make auditar-dos-maquinas-docker
```

El reporte (`auditoria_<fecha>.md` y `.json`, más un par solicitud/respuesta de muestra) queda en
`submission/evidencias/dos_maquinas/`. Comprueba:

1. Lo que guardó el servicio es **exactamente** lo que mandó y recibió el hospital (SHA-256 en los dos lados).
2. Cada solicitud trae solo los campos del protocolo: 21 cifrados del tamaño de la llave, ningún valor en claro.
3. Cifrado aleatorizado: todos los cifrados son distintos aunque los valores en claro se repiten muchísimo.
4. Ningún resultado descifrado (entero z, logit, probabilidad) ni vector de entrada aparece en logs o archivos del servicio.
5. El proceso del servicio no tenía ninguna llave privada Paillier en memoria (al arrancar y en cada solicitud).
6. Canal TLS 1.3 con certificado de cliente `hospital`.
7. Dos máquinas distintas (nombre de host o `machine-id`).
8. Enteros idénticos al cálculo en claro y las mismas métricas cifrado vs. flotante.

Termina en **APROBADA** o **FALLIDA** (código de salida 1). Haz commit del reporte; la evidencia cruda
(`~/.tamizaje-dos-maquinas/evidencia_servicio`, ~27 KB por solicitud) se queda fuera del repo.

## Qué sí y qué no demuestra

- **Sí:** con los mismos bytes en ambos lados, el servicio recibió y devolvió solo cifrados, no tenía con qué
  descifrar y aun así el hospital obtuvo exactamente el resultado del modelo.
- **No:** no mide CPACF ni sustituye las capturas de [LINUXONE.md](LINUXONE.md). La comprobación de memoria busca
  objetos `PaillierPrivateKey` en el proceso de Python del servicio; es evidencia, no una prueba formal.
- La tabla de tiempos incluye la red entre las dos VM. Si alguna VM no es s390x, el reporte lo dice arriba.
- La auditoría del lado del hospital no guarda los vectores de entrada; los registros del CDC son públicos y anónimos,
  y cualquiera puede reconstruirlos con `cdc_id` desde `data/cdc_891/`.
