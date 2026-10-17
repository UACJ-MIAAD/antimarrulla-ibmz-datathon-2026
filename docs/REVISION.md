# 🔎 Revisión del código por otro integrante

> Los PR 1 y 2 entraron a `main` por excepción del capitán, sin revisión de otro integrante ([CRONOLOGIA.md](CRONOLOGIA.md)). Esa excepción queda registrada; esta revisión **sigue pendiente** y no se da por hecha hasta que alguien la deje escrita (comentario en GitHub o en este archivo con nombre y fecha).

## 1. Correr un clon limpio (30 min)

```bash
git clone https://github.com/UACJ-MIAAD/antimarrulla-ibmz-datathon-2026.git revision && cd revision
make verify        # todas las pruebas + verificación de artefactos y re-entrenamiento
make demo          # hospital + servicio en contenedores; prueba de humo
make medir-api     # mide la API del hospital desplegado (deja un .json/.md en submission/evidencias/metricas/)
make demo-down
```

## 2. Leer, en este orden

1. `src/tamizaje/esquema.py` y `src/tamizaje/contrato.py`: entradas y punto fijo.
2. `src/tamizaje/protocolo.py`: hospital (llave privada) y servicio (sin llave).
3. `tests/test_protocolo.py`: pruebas a)–e).
4. `src/tamizaje/servicio.py`, `src/tamizaje/hospital.py`, `src/tamizaje/boveda.py`, `docker/compose.yml`.

## 3. Preguntas de comprensión (cada integrante debe poder responderlas ante un juez)

1. ¿Por qué el hospital no escala las 21 entradas y solo los pesos se multiplican por 10⁹?
2. ¿Qué garantiza la prueba "entero descifrado idéntico" y qué garantiza la "cota de error frente al flotante"? ¿Por qué son distintas?
3. ¿Dónde vive la llave privada Paillier? ¿Y la llave AES de la bóveda? ¿Qué contenedor tiene cada una?
4. ¿Qué ve el servicio de riesgo? ¿Qué queda en sus logs?
5. En la demo, ¿quién puede leer los datos del hospital? (Pista: misma VM, administrador dentro de la frontera de confianza.)
6. ¿Qué cifra AES-256-GCM y qué **no** cifra la app (logs, discos, respaldos)?
7. ¿Qué aporta CPACF y qué no? ¿Lo hemos medido en LinuxONE?
8. ¿Por qué el umbral se fija en validación y no en prueba? ¿Qué significa un VPP de 29.7%?
9. ¿Qué evaluó ENSANUT y por qué no valida el modelo de 21 variables?
10. ¿Qué mide `make medir` y qué mide `make medir-api`? ¿Cuál de los dos es el recorrido de dos contenedores?

> PR 5 y PR 6 (17 oct) los revisó y fusionó su propio autor (cuenta AzraelNogo); tampoco cuentan como revisión de otro integrante.

Los PR 3 y 4 también entraron por decisiones previas del capitán; una excepción histórica no es una aprobación técnica. La revisión actual debe identificar **commit, alcance y comandos ejecutados**. Las verificaciones de Codex son auditoría asistida, no firma de un integrante. Antes de enviar, los cuatro confirman que comprenden protocolo, límites y uso de IA.

## 4. Registro de revisiones

| Integrante | Fecha y hora | Qué corrió | Comentarios |
|------------|--------------|------------|-------------|
| _pendiente_ | | | |
