# 🖥️ Correr Tamizaje a ciegas en LinuxONE (s390x)

> Estado (17 oct 2026): todo está probado en local (macOS arm64 y contenedores Linux arm64). **Todavía no se ha corrido en LinuxONE.** Estos son los pasos para hacerlo en la VM Ubuntu 24.04 de la Community Cloud. Responsable: Álvaro, con Carlos para las mediciones.

## 0. Antes de empezar

- [ ] Los **dos labs obligatorios** completados, con capturas en `submission/evidencias/` (la guía los exige antes de construir la solución propia).
- [ ] Acceso SSH de quien vaya a correrlo. Nunca pegar llaves, contraseñas ni tokens en el repo, en capturas o en el chat.

## 1. Preparar la VM (una sola vez)

```bash
sudo apt-get update
sudo apt-get install -y git make docker.io docker-compose-v2
sudo usermod -aG docker $USER      # cerrar sesión y volver a entrar
git clone https://github.com/UACJ-MIAAD/antimarrulla-ibmz-datathon-2026.git
cd antimarrulla-ibmz-datathon-2026
```

No hace falta instalar Python con pip en la VM: las imágenes usan Ubuntu 24.04 y sus paquetes `python3-*` de apt, que existen para s390x. Solo `phe` (Python puro) se instala con pip dentro de la imagen.

## 2. Verificar, levantar y medir

```bash
make verify-docker     # todas las pruebas + verificación de artefactos y re-entrenamiento, dentro de Linux s390x
make demo-docker       # secretos en ~/.tamizaje, imagen, hospital + servicio y prueba de humo
make medir-docker      # → submission/evidencias/metricas/medicion_linuxone-s390x_*.json y .md
```

La medición se etiqueta sola como `linuxone-s390x` cuando `uname -m` es `s390x`, y registra `lscpu`, `cpacfinfo` (si `s390-tools` está instalado en la imagen), versiones de OpenSSL de la CLI y de `cryptography`, commit y hashes.

## 3. Ver la UI sin exponer puertos

La demo solo escucha en `127.0.0.1:8080` de la VM. Desde la laptop:

```bash
ssh -L 8080:127.0.0.1:8080 <usuario>@<ip-de-la-vm>
# y abrir http://127.0.0.1:8080
```

## 4. Evidencia para jueces (capturas sin secretos)

Guardar en `submission/evidencias/linuxone/`:

| Captura | Comando |
|---------|---------|
| Arquitectura | `uname -m` → `s390x` y `lscpu` |
| CPACF disponible | `cpacfinfo -a` (paquete `s390-tools`) |
| OpenSSL de la CLI y de la app | `openssl version -a` y el campo `openssl_de_cryptography` de la medición |
| Contenedores corriendo | `docker compose -f docker/compose.yml ps` |
| El servicio no tiene la llave privada | `docker compose -f docker/compose.yml exec servicio ls /run/tamizaje` (solo certificado TLS, su llave TLS y la CA) |
| Logs sin datos de pacientes | `docker compose -f docker/compose.yml logs servicio` |
| UI con un paciente sintético | captura del navegador por el túnel SSH |
| Versiones efectivas | `docker run --rm tamizaje:dev dpkg -l 'python3-*' \| grep ^ii` |

> CPACF acelera AES; **no** acelera Paillier. Solo se atribuye aceleración por hardware a lo que la evidencia sostenga.

## 5. Después

- Hacer commit de `submission/evidencias/metricas/` y `submission/evidencias/linuxone/`.
- Actualizar las historias US-2.5, US-2.6, US-6.2 y US-6.3 en `site/status.json` solo con esa evidencia.
- Reemplazar en el deck y el guion las cifras locales por las de LinuxONE.
