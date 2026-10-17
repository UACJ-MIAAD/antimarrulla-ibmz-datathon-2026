"""The service must keep serving while another client is slow or stalled in its TLS handshake."""
import socket, threading, time
from screening import hospital, protocol, secrets_setup, service


def _patient(model):
    return {n: 0 if n not in ("BMI", "GenHlth", "Age", "Education", "Income") else 12 if n == "BMI" else 1 for n in model["variables"]}


def test_stalled_handshake_does_not_block_other_clients(tmp_path, model, keys):
    secrets_setup.generate(str(tmp_path))
    c = tmp_path / "certs"
    srv, _ = service.create_server("127.0.0.1", 0, model, str(c / "service.pem"), str(c / "service.key"), str(c / "ca.pem"))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    port = srv.server_address[1]
    stalled = socket.create_connection(("127.0.0.1", port))  # connects, never sends a ClientHello
    try:
        time.sleep(0.3)
        cli = hospital.ServiceClient(f"https://localhost:{port}", str(c / "ca.pem"), str(c / "hospital.pem"), str(c / "hospital.key"), timeout=5)
        h = protocol.hospital(model, keys=keys)
        t0 = time.perf_counter()
        request, _ = h.prepare(_patient(model))
        cli.evaluate(request)  # before the fix this waited behind the stalled handshake and timed out
        assert time.perf_counter() - t0 < 5
    finally:
        stalled.close()
        srv.shutdown(); srv.server_close()


def test_parallel_requests_all_succeed(tmp_path, model, keys):
    secrets_setup.generate(str(tmp_path))
    c = tmp_path / "certs"
    srv, _ = service.create_server("127.0.0.1", 0, model, str(c / "service.pem"), str(c / "service.key"), str(c / "ca.pem"))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    url = f"https://localhost:{srv.server_address[1]}"
    errors = []

    def one():
        try:
            h = protocol.hospital(model, keys=keys)
            cli = hospital.ServiceClient(url, str(c / "ca.pem"), str(c / "hospital.pem"), str(c / "hospital.key"), timeout=20)
            request, x = h.prepare(_patient(model))
            resp, _, _ = cli.evaluate(request)
            h.decrypt(resp)
        except Exception as e:  # noqa: BLE001
            errors.append(repr(e))

    try:
        ts = [threading.Thread(target=one) for _ in range(8)]
        [t.start() for t in ts]; [t.join(60) for t in ts]
        assert not errors
    finally:
        srv.shutdown(); srv.server_close()
