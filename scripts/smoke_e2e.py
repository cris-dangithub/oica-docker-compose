"""Prueba HTTP y WebSocket de una cartilla pequeña, solo en entorno de pruebas.
Uso: python3 scripts/smoke_e2e.py http://localhost:8080 entrada.xlsx
"""
import base64
import hashlib
import json
import os
from pathlib import Path
import socket
import struct
import sys
import time
import urllib.request
from urllib.parse import urlsplit


def request(base, path, data=None, method=None, headers=None):
    req = urllib.request.Request(base + path, data=data, method=method, headers=headers or {})
    with urllib.request.urlopen(req, timeout=30) as response:
        return response.read()


def json_request(base, path, data=None, method=None):
    return json.loads(request(base, path, None if data is None else json.dumps(data).encode(), method,
                              {'Content-Type': 'application/json'}))


class ProgressSocket:
    """Cliente mínimo RFC6455 para comprobar upgrade y eventos Socket.IO."""
    def __init__(self, base):
        url = urlsplit(base)
        if url.scheme != 'http':
            raise ValueError('Este smoke test usa HTTP en un stack desechable')
        self.socket = socket.create_connection((url.hostname, url.port or 80), timeout=10)
        self.stream = self.socket.makefile('rb')
        key = base64.b64encode(os.urandom(16)).decode()
        headers = (f'GET /socket.io/?EIO=4&transport=websocket HTTP/1.1\r\nHost: {url.netloc}\r\n'
                   f'Origin: {base}\r\nUpgrade: websocket\r\nConnection: Upgrade\r\n'
                   f'Sec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n')
        self.socket.sendall(headers.encode())
        assert b'101' in self.stream.readline(), 'Nginx no permitió el upgrade WebSocket'
        response_headers = {}
        while (line := self.stream.readline()) != b'\r\n':
            if not line: raise RuntimeError('Conexión cerrada en handshake')
            name, value = line.decode().split(':', 1)
            response_headers[name.lower()] = value.strip()
        expected = base64.b64encode(hashlib.sha1((key+'258EAFA5-E914-47DA-95CA-C5AB0DC85B11').encode()).digest()).decode()
        assert response_headers['sec-websocket-accept'] == expected
        assert self.receive().startswith('0')
        self.send('40')
        self.events = []

    def receive(self):
        header = self.stream.read(2)
        if len(header) != 2: raise RuntimeError('WebSocket cerrado')
        length = header[1] & 127
        if length == 126: length = struct.unpack('!H', self.stream.read(2))[0]
        elif length == 127: length = struct.unpack('!Q', self.stream.read(8))[0]
        return self.stream.read(length).decode()

    def send(self, text):
        payload = text.encode()
        mask = os.urandom(4)
        length = len(payload)
        header = bytes([0x81, 0x80 | length]) if length < 126 else bytes([0x81, 0xFE]) + struct.pack('!H', length)
        self.socket.sendall(header + mask + bytes(c ^ mask[i % 4] for i,c in enumerate(payload)))

    def wait_complete(self, task_id):
        self.send('42' + json.dumps(['subscribe_task', {'task_id': task_id}]))
        deadline = time.monotonic() + 180
        self.socket.settimeout(180)
        while time.monotonic() < deadline:
            packet = self.receive()
            if packet == '2': self.send('3')
            if packet.startswith('42'):
                event, data = json.loads(packet[2:])
                if event == 'task_update':
                    self.events.append(data)
                    if data['state'] in ('SUCCESS', 'completed'): return
                    if data['state'] == 'FAILURE' or data['state'].startswith('error_'):
                        raise AssertionError(data)
        raise TimeoutError('No llegó la finalización por WebSocket')

    def close(self):
        self.stream.close()
        self.socket.close()


def main():
    base = sys.argv[1].rstrip('/')
    path = Path(sys.argv[2])
    assert request(base, '/'), 'Frontend vacío'
    assert json_request(base, '/api/health')['status'] == 'healthy'
    # Socket.IO debe soportar también el transporte de polling.
    assert request(base, '/socket.io/?EIO=4&transport=polling').startswith(b'0')
    ws = ProgressSocket(base)
    boundary = 'oica-' + os.urandom(12).hex()
    body = (f'--{boundary}\r\nContent-Disposition: form-data; name="perfil"\r\n\r\nrapido\r\n'
            f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="smoke.xlsx"\r\n'
            'Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet\r\n\r\n').encode()
    body += path.read_bytes() + f'\r\n--{boundary}--\r\n'.encode()
    uploaded = json.loads(request(base, '/api/upload', body, 'POST', {'Content-Type': f'multipart/form-data; boundary={boundary}'}))
    file_id, task_id = uploaded['file_id'], uploaded['task_id']
    ws.wait_complete(task_id)
    assert ws.events, 'No llegaron eventos de progreso'
    ws.close()
    for _ in range(20):
        status = json_request(base, f'/api/status/{task_id}')
        if status['state'] == 'SUCCESS': break
        time.sleep(1)
    assert status['state'] == 'SUCCESS', status
    detail = json_request(base, f'/api/file/{file_id}')
    assert detail['processing_status'] == 'completed', detail
    result = detail['processing_results'][0]
    for kind, signature in [('excel', b'PK'), ('pdf', b'%PDF'), ('imagen', b'\x89PNG')]:
        content = request(base, f"/api/descargar-{kind}/{result['storage_uuid']}")
        assert content.startswith(signature), kind
    filtered = json_request(base, '/api/files?perfil=rapido&status=completed&search=smoke')
    assert any(item['id'] == file_id for item in filtered['files'])
    job = json_request(base, f'/api/reprocess/{file_id}', {'perfil':'rapido'}, 'POST')
    for _ in range(180):
        state = json_request(base, f"/api/status/{job['task_id']}")
        if state['state'] in ('SUCCESS', 'FAILURE'): break
        time.sleep(1)
    assert state['state'] == 'SUCCESS', state
    detail = json_request(base, f'/api/file/{file_id}')
    assert detail['total_versions'] == 2, detail
    if '--keep' not in sys.argv:
        request(base, f'/api/file/{file_id}', method='DELETE')
    else:
        print(f'Archivo conservado para comprobar persistencia: {file_id}')
    print('OK: web, salud, polling, WebSocket, carga, artefactos, filtros y reprocesamiento.')


if __name__ == '__main__':
    main()
