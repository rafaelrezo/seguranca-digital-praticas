"""Laboratório local A22: duas contas e ordens fictícias, sem dependências."""

from http.server import BaseHTTPRequestHandler, HTTPServer
import json

HOST, PORT = "127.0.0.1", 3001
CONTAS = {"u1@lab.invalid": "senha-u1", "u2@lab.invalid": "senha-u2"}
TOKENS = {"lab-u1": "u1@lab.invalid", "lab-u2": "u2@lab.invalid"}
ORDENS = {
    "17": {"id": 17, "dono": "u1@lab.invalid", "descricao": "Inspecionar bomba"},
    "18": {"id": 18, "dono": "u2@lab.invalid", "descricao": "Revisar sensor"},
}


class Handler(BaseHTTPRequestHandler):
    def responder(self, codigo, dados):
        corpo = json.dumps(dados, ensure_ascii=False).encode("utf-8")
        self.send_response(codigo)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(corpo)))
        self.end_headers()
        self.wfile.write(corpo)

    def identidade(self):
        valor = self.headers.get("Authorization", "")
        return TOKENS.get(valor.removeprefix("Bearer ")) if valor.startswith("Bearer ") else None

    def ler_json(self):
        try:
            tamanho = int(self.headers.get("Content-Length", "0"))
            if tamanho > 1024:
                return None
            return json.loads(self.rfile.read(tamanho))
        except (ValueError, json.JSONDecodeError):
            return None

    def do_GET(self):
        if self.path == "/":
            return self.responder(200, {"aplicacao": "Ordens A22", "rotas": ["/api/ordens/17", "/api/ordens/18"]})
        if self.path == "/api/ordens":
            usuario = self.identidade()
            if not usuario:
                return self.responder(401, {"erro": "credencial ausente ou inválida"})
            return self.responder(200, {"ordens": [o for o in ORDENS.values() if o["dono"] == usuario]})
        if self.path.startswith("/api/ordens/"):
            usuario = self.identidade()
            if not usuario:
                return self.responder(401, {"erro": "credencial ausente ou inválida"})
            numero = self.path.removeprefix("/api/ordens/")
            ordem = ORDENS.get(numero)
            if not ordem:
                return self.responder(404, {"erro": "ordem inexistente"})
            # Falha intencional: autentica, mas não confere o dono na leitura.
            return self.responder(200, ordem)
        if self.path.startswith("/api/"):
            return self.responder(404, {"erro": "rota inexistente"})
        # Contraprova de calibração: rota desconhecida fora da API parece a raiz.
        return self.responder(200, {"aplicacao": "Ordens A22", "rotas": ["/api/ordens/17", "/api/ordens/18"]})

    def do_POST(self):
        if self.path == "/api/login":
            dados = self.ler_json()
            if not isinstance(dados, dict):
                return self.responder(400, {"erro": "JSON inválido"})
            email, senha = dados.get("email"), dados.get("senha")
            if CONTAS.get(email) != senha:
                return self.responder(401, {"erro": "credenciais inválidas"})
            token = "lab-u1" if email == "u1@lab.invalid" else "lab-u2"
            TOKENS[token] = email
            return self.responder(200, {"token": token, "tipo": "opaco; não é JWT"})
        if self.path == "/api/logout":
            token = self.headers.get("Authorization", "").removeprefix("Bearer ")
            if token not in TOKENS:
                return self.responder(401, {"erro": "credencial ausente ou inválida"})
            del TOKENS[token]
            return self.responder(200, {"estado": "sessão encerrada no servidor"})
        if self.path.endswith("/fechar") and self.path.startswith("/api/ordens/"):
            usuario = self.identidade()
            if not usuario:
                return self.responder(401, {"erro": "credencial ausente ou inválida"})
            return self.responder(403, {"erro": "somente supervisor pode fechar"})
        return self.responder(404, {"erro": "rota inexistente"})


if __name__ == "__main__":
    print(f"Ordens A22 em http://{HOST}:{PORT}; Ctrl+C encerra", flush=True)
    HTTPServer((HOST, PORT), Handler).serve_forever()
