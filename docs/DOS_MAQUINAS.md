# 🖧 Prueba de dos máquinas: el servicio nunca ve datos en claro

> Complementa la demo de [LINUXONE.md](LINUXONE.md), que corre los dos contenedores en **la misma VM**. Aquí el
> servicio de riesgo corre en **una VM** y el hospital en **otra**, con **pacientes sintéticos por defecto**. El CDC
> público se usa solo al pedir `DATOS=cdc` para un benchmark. La auditoría contrasta la evidencia capturada;
> no es una prueba formal de ausencia de fugas ni reemplaza las capturas del proveedor.

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
make ensayo-dos-maquinas        # con el venv: otro proceso, 20 sintéticos, auditoría en modo ensayo
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

Preferir un túnel SSH en la VM B (`ssh -N -L 8443:localhost:8443 USUARIO@IP_VM_A`) y
en el paso 3 `SERVICIO_URL=https://localhost:8443`; el certificado ya incluye `localhost`.
Si se usa conexión directa, restringir el acceso a la IP del hospital (por ejemplo, `sudo ufw allow from <IP_VM_B> to any port 8443 proto tcp`), sin abrir la UI ni desactivar la comprobación de certificados.

## 3. VM B (hospital): mandar sintéticos cifrados

```bash
make hospital-remoto-docker SERVICIO_URL=https://<IP de la VM A>:8443 N=200
```

Genera 200 sintéticos deterministas (semilla 2026), cifra cada uno, lo manda por TLS 1.3 mutuo, descifra y compara
con el cálculo en claro. Imprime enteros idénticos y latencia p50/p95. No informa AUC en sintéticos porque no tienen
etiqueta clínica observada. Antes de medir verifica el hash del modelo y del código remoto. La terminal de la VM A muestra ids, tamaños y
`llave_privada_en_memoria=False`.

Para un **benchmark separado** con el CDC público anonimizado: `make hospital-remoto-docker SERVICIO_URL=https://<IP de la VM A>:8443 N=200 DATOS=cdc`. Solo en este modo se calculan AUC y sensibilidad si hay ambas clases. No usarlo como la demo de pacientes sintéticos ni como validación clínica.

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
7. IDs de host presentes y distintos. Los nombres de contenedor no acreditan dos máquinas; deben contrastarse con las dos VM. Un `machine-id` declarado no certifica por sí solo el proveedor ni impide suplantación por el administrador.
8. Enteros idénticos al cálculo en claro y las mismas métricas cuando existen etiquetas CDC.
9. Hash de la bitácora del hospital y conteos coherentes con su resumen.
10. Hashes de código y modelo coincidentes entre hospital, salud y evidencia del servicio.

Termina en **APROBADA** o **FALLIDA** (código de salida 1). Haz commit del reporte; la evidencia cruda
(`~/.tamizaje-dos-maquinas/evidencia_servicio`, ~27 KB por solicitud) se queda fuera del repo.

## Qué sí y qué no demuestra

- **Sí:** los registros capturados muestran cifrados y permiten contrastar bytes, versiones y resultados. La búsqueda de llaves se limita a objetos Python detectables; no certifica que nunca hubo una llave ni examina al administrador/hipervisor.
- **No:** no mide CPACF ni sustituye las capturas de [LINUXONE.md](LINUXONE.md). La comprobación de memoria busca
  objetos `PaillierPrivateKey` en el proceso de Python del servicio; es evidencia, no una prueba formal.
- La tabla de tiempos incluye la red entre las dos VM. Si alguna VM no es s390x, el reporte lo dice arriba.
- Este ensayo usa un cliente de hospital directo: no incluye navegador, API de la UI ni bóveda. Para el recorrido completo de la aplicación se conserva `make medir-api-docker`; no comparar ambos tiempos como si fueran la misma operación.
- La bitácora del hospital guarda resultados descifrados. Para auditarla se copian esos resultados a una carpeta del operador, fuera del proceso del servicio: esa copia posterior no forma parte del recorrido de inferencia privada. No publicar bitácoras que provengan de pacientes privados.
- El ensayo usa sintéticos; si se elige CDC, `registro_id` permite reconstruir la fila pública desde `data/cdc_891/`. Los datos no adquieren mayor anonimato por cambiar el nombre de la columna.
