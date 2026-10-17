"""Testes independentes da preparação e do dashboard de vendas.

Executar da raiz do workspace:
    .venv/Scripts/python.exe -m unittest discover -s projeto-dashboard/tests -v

Só usa a biblioteca padrão do Python e Node/Chrome instalados no ambiente.
Não altera arquivos do produto; o servidor HTTP e o perfil do navegador são
temporários.
"""

from __future__ import annotations

import csv
import hashlib
import http.server
import json
import os
import shutil
import socket
import socketserver
import struct
import subprocess
import tempfile
import threading
import time
import unittest
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "projeto-dashboard"
SITE = PROJECT / "site"
SOURCE = ROOT / "papelaria_limpa.csv"
DATA_FILE = SITE / "data" / "vendas.json"
REQUIRED_COLUMNS = {
    "id_venda", "data", "cidade", "categoria", "produto", "quantidade",
    "preco_unitario", "forma_pagamento", "valor_venda",
}
CENT = Decimal("0.01")


def cents(value: Decimal) -> Decimal:
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


def totals(rows: list[dict], dimension: str | None = None) -> dict:
    """Agregação independente com Decimal, sem importar o código do produto."""
    if dimension is None:
        return {"count": len(rows), "total": cents(sum(
            (Decimal(str(row["valor_venda"])) for row in rows), Decimal("0")
        ))}
    result: defaultdict[str, Decimal] = defaultdict(Decimal)
    for row in rows:
        result[str(row[dimension])] += Decimal(str(row["valor_venda"]))
    return {name: cents(value) for name, value in result.items()}


def load_source() -> tuple[list[str], list[dict[str, str]]]:
    with SOURCE.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return list(reader.fieldnames or []), list(reader)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class MarkupInventory(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: set[str] = set()
        self.labels: set[str] = set()
        self.links: list[str] = []
        self.scripts: list[str] = []
        self.html_lang: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs = dict(attrs)
        if tag == "html":
            self.html_lang = attrs.get("lang")
        if attrs.get("id"):
            self.ids.add(str(attrs["id"]))
        if tag == "label" and attrs.get("for"):
            self.labels.add(str(attrs["for"]))
        if tag == "link" and attrs.get("href"):
            self.links.append(str(attrs["href"]))
        if tag == "script" and attrs.get("src"):
            self.scripts.append(str(attrs["src"]))


def free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def start_http_server() -> tuple[subprocess.Popen, int]:
    port = free_port()
    process = subprocess.Popen(
        [os.fspath(Path(os.sys.executable)), "-m", "http.server", str(port),
         "--bind", "127.0.0.1", "--directory", os.fspath(SITE)],
        cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    base = f"http://127.0.0.1:{port}/"
    for _ in range(80):
        if process.poll() is not None:
            raise RuntimeError(f"Servidor HTTP encerrou com código {process.returncode}")
        try:
            with urllib.request.urlopen(base, timeout=0.5) as response:
                if response.status == 200:
                    return process, port
        except (OSError, urllib.error.URLError):
            time.sleep(0.1)
    process.terminate()
    raise RuntimeError("Servidor HTTP não respondeu em 8 segundos")


def stop_process(process: subprocess.Popen | None) -> None:
    if process is None or process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=5)


class CDPWebSocket:
    """Cliente mínimo CDP/WebSocket, usando somente a biblioteca padrão."""

    def __init__(self, url: str) -> None:
        parsed = urllib.parse.urlparse(url)
        self.sock = socket.create_connection((parsed.hostname, parsed.port), timeout=10)
        self.sock.settimeout(10)
        key = "dGVzdGVyLWRhc2hib2FyZC1jZHA="
        path = parsed.path + (f"?{parsed.query}" if parsed.query else "")
        request = (
            f"GET {path} HTTP/1.1\r\nHost: {parsed.hostname}:{parsed.port}\r\n"
            "Upgrade: websocket\r\nConnection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n"
            "Origin: http://localhost\r\n\r\n"
        )
        self.sock.sendall(request.encode("ascii"))
        response = bytearray()
        while b"\r\n\r\n" not in response:
            chunk = self.sock.recv(4096)
            if not chunk:
                raise RuntimeError("Chrome encerrou o handshake CDP")
            response.extend(chunk)
        if b" 101 " not in response.split(b"\r\n", 1)[0]:
            raise RuntimeError(f"Handshake CDP recusado: {response[:300]!r}")
        self.next_id = 0
        self.events: list[dict] = []

    def _send(self, message: dict) -> None:
        payload = json.dumps(message, separators=(",", ":")).encode("utf-8")
        mask = os.urandom(4)
        size = len(payload)
        if size < 126:
            header = bytes((0x81, 0x80 | size))
        elif size < 65536:
            header = bytes((0x81, 0x80 | 126)) + struct.pack("!H", size)
        else:
            header = bytes((0x81, 0x80 | 127)) + struct.pack("!Q", size)
        masked = bytes(byte ^ mask[index % 4] for index, byte in enumerate(payload))
        self.sock.sendall(header + mask + masked)

    def _read_exact(self, size: int) -> bytes:
        parts = bytearray()
        while len(parts) < size:
            chunk = self.sock.recv(size - len(parts))
            if not chunk:
                raise RuntimeError("Conexão CDP fechada durante leitura")
            parts.extend(chunk)
        return bytes(parts)

    def _receive(self) -> dict:
        first, second = self._read_exact(2)
        opcode = first & 0x0F
        size = second & 0x7F
        if size == 126:
            size = struct.unpack("!H", self._read_exact(2))[0]
        elif size == 127:
            size = struct.unpack("!Q", self._read_exact(8))[0]
        mask = self._read_exact(4) if second & 0x80 else None
        payload = self._read_exact(size)
        if mask:
            payload = bytes(byte ^ mask[index % 4] for index, byte in enumerate(payload))
        if opcode == 8:
            raise RuntimeError("Chrome fechou a sessão CDP")
        if opcode == 9:
            self.sock.sendall(bytes((0x8A, len(payload))) + payload)
            return self._receive()
        return json.loads(payload.decode("utf-8"))

    def command(self, method: str, params: dict | None = None) -> dict:
        self.next_id += 1
        command_id = self.next_id
        self._send({"id": command_id, "method": method, "params": params or {}})
        deadline = time.monotonic() + 15
        while time.monotonic() < deadline:
            message = self._receive()
            if message.get("id") == command_id:
                if "error" in message:
                    raise RuntimeError(f"CDP {method}: {message['error']}")
                return message.get("result", {})
            if "method" in message:
                self.events.append(message)
        raise TimeoutError(f"Timeout aguardando {method}")

    def evaluate(self, expression: str):
        result = self.command("Runtime.evaluate", {
            "expression": expression, "returnByValue": True, "awaitPromise": True,
            "userGesture": True,
        })
        if result.get("exceptionDetails"):
            raise AssertionError(f"Erro no JavaScript avaliado: {result['exceptionDetails']}")
        return result.get("result", {}).get("value")

    def close(self) -> None:
        try:
            self.sock.close()
        except OSError:
            pass


def find_chrome() -> str | None:
    candidates = [
        shutil.which("chrome"), shutil.which("msedge"), shutil.which("chromium"),
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ]
    return next((candidate for candidate in candidates if candidate and Path(candidate).is_file()), None)


class TestIndependentData(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source_hash_before = sha256(SOURCE)
        cls.source_columns, cls.csv_rows = load_source()
        cls.payload = json.loads(DATA_FILE.read_text(encoding="utf-8"))
        cls.sales = cls.payload["vendas"]

    @classmethod
    def tearDownClass(cls) -> None:
        if sha256(SOURCE) != cls.source_hash_before:
            raise AssertionError("O CSV original foi alterado durante a suíte de testes")

    def test_original_schema_values_types_missing_and_duplicates(self) -> None:
        self.assertTrue(REQUIRED_COLUMNS.issubset(self.source_columns))
        self.assertEqual(len(self.csv_rows), 180)
        self.assertEqual(len(self.sales), len(self.csv_rows), "Não descarte nem acrescente vendas")
        ids = [row["id_venda"] for row in self.csv_rows]
        self.assertEqual(len(ids), len(set(ids)), "Duplicatas devem ser explicitamente tratadas")
        prepared_ids = [row["id_venda"] for row in self.sales]
        self.assertEqual(prepared_ids, ids, "IDs/ordem devem preservar a fonte sem remoção silenciosa")

        for source, prepared in zip(self.csv_rows, self.sales):
            for column in REQUIRED_COLUMNS:
                self.assertNotEqual(source[column].strip(), "", f"Ausência em {column} / {source['id_venda']}")
            self.assertEqual(set(REQUIRED_COLUMNS) - set(prepared), set(), source["id_venda"])
            for column in ("data", "cidade", "categoria", "produto", "forma_pagamento", "id_venda"):
                self.assertEqual(str(prepared[column]), source[column], f"Divergência {column} / {source['id_venda']}")
            date.fromisoformat(str(prepared["data"]))
            self.assertIs(type(prepared["quantidade"]), int)
            self.assertGreater(prepared["quantidade"], 0)
            for column in ("preco_unitario", "valor_venda"):
                self.assertIn(type(prepared[column]), (int, float))
                self.assertTrue(Decimal(str(prepared[column])).is_finite())
                self.assertEqual(Decimal(source[column]), Decimal(str(prepared[column])))
            self.assertGreaterEqual(Decimal(str(prepared["preco_unitario"])), 0)
            calculated = cents(Decimal(str(prepared["quantidade"])) * Decimal(str(prepared["preco_unitario"])))
            self.assertEqual(calculated, cents(Decimal(str(prepared["valor_venda"]))))

    def test_known_miniature_oracle_and_independent_aggregations(self) -> None:
        # Mini-caso inteiramente conhecido, calculado a mão e fora do código do produto.
        mini = [
            {"cidade": "Norte", "categoria": "A", "valor_venda": "10.00"},
            {"cidade": "Norte", "categoria": "B", "valor_venda": "7.50"},
            {"cidade": "Sul", "categoria": "A", "valor_venda": "22.00"},
        ]
        self.assertEqual(totals(mini), {"count": 3, "total": Decimal("39.50")})
        self.assertEqual(totals(mini, "cidade"), {"Norte": Decimal("17.50"), "Sul": Decimal("22.00")})
        self.assertEqual(totals(mini, "categoria"), {"A": Decimal("32.00"), "B": Decimal("7.50")})

        source_sales = [{
            "cidade": row["cidade"], "categoria": row["categoria"],
            "valor_venda": cents(Decimal(row["quantidade"]) * Decimal(row["preco_unitario"])),
        } for row in self.csv_rows]
        prepared_totals = totals(self.sales)
        source_totals = totals(source_sales)
        self.assertEqual(source_totals, {"count": 180, "total": Decimal("20059.00")})
        self.assertEqual(prepared_totals, source_totals)
        self.assertEqual(totals(source_sales, "categoria"), {
            "Acessórios": Decimal("10517.00"), "Livros": Decimal("7438.00"),
            "Papelaria": Decimal("2104.00"),
        })
        self.assertEqual(totals(source_sales, "cidade"), {
            "Campinas": Decimal("8578.00"), "Santos": Decimal("6937.50"),
            "Sorocaba": Decimal("4543.50"),
        })
        self.assertEqual(self.payload["quantidade_vendas"], source_totals["count"])
        self.assertEqual(Decimal(str(self.payload["total_vendido"])), source_totals["total"])
        self.assertEqual(self.payload["fonte"], SOURCE.name)
        self.assertEqual(self.payload["definicao_venda"], "Uma linha válida da fonte corresponde a uma venda.")

    def test_original_is_still_byte_identical_at_end_of_data_checks(self) -> None:
        self.assertEqual(sha256(SOURCE), self.source_hash_before)


class TestStaticSiteAndHTTP(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.server, cls.port = start_http_server()
        cls.base = f"http://127.0.0.1:{cls.port}/"

    @classmethod
    def tearDownClass(cls) -> None:
        stop_process(cls.server)

    def test_html_contract_assets_and_local_http_resources(self) -> None:
        html_response = urllib.request.urlopen(self.base, timeout=5)
        self.assertEqual(html_response.status, 200)
        html = html_response.read().decode("utf-8")
        parser = MarkupInventory()
        parser.feed(html)
        self.assertEqual(parser.html_lang, "pt-BR")
        required_ids = {
            "filter-city", "filter-category", "clear-filters", "kpi-total", "kpi-count",
            "kpi-average", "category-chart", "city-chart", "sales-table-body",
            "results-count", "load-error",
        }
        self.assertTrue(required_ids.issubset(parser.ids), f"IDs ausentes: {required_ids - parser.ids}")
        self.assertTrue({"filter-city", "filter-category"}.issubset(parser.labels), "Filtros precisam de labels associados")
        self.assertIn("clear-filters", parser.ids)
        local_assets = parser.links + parser.scripts
        self.assertTrue(local_assets)
        for asset in local_assets:
            self.assertFalse(asset.startswith(("http://", "https://", "//")), f"Dependência externa: {asset}")
            with self.subTest(asset=asset):
                response = urllib.request.urlopen(urllib.parse.urljoin(self.base, asset), timeout=5)
                self.assertEqual(response.status, 200)
                self.assertGreater(len(response.read()), 0)
        for resource in ("./data/vendas.json",):
            response = urllib.request.urlopen(urllib.parse.urljoin(self.base, resource), timeout=5)
            self.assertEqual(response.status, 200)
            self.assertEqual(json.loads(response.read().decode("utf-8"))["quantidade_vendas"], 180)

    def test_javascript_syntax_with_node(self) -> None:
        node = shutil.which("node")
        if not node:
            self.skipTest("Node.js indisponível; verificação sintática PENDENTE")
        completed = subprocess.run([node, "--check", os.fspath(SITE / "app.js")], capture_output=True, text=True)
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)


class TestRealBrowser(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.server, cls.port = start_http_server()
        cls.base = f"http://127.0.0.1:{cls.port}/"
        cls.chrome = find_chrome()
        cls.temp = tempfile.TemporaryDirectory(prefix="tester-dashboard-")
        cls.browser = None
        cls.cdp = None
        cls.browser_problem = None
        if not cls.chrome:
            cls.browser_problem = "Chrome/Edge/Chromium não disponível"
            return
        profile = Path(cls.temp.name) / "profile"
        profile.mkdir()
        cls.browser = subprocess.Popen([
            cls.chrome, "--headless=new", "--disable-gpu", "--no-first-run",
            "--no-default-browser-check", "--remote-debugging-port=0",
            "--remote-allow-origins=*", f"--user-data-dir={profile}", "about:blank",
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        active_port_file = profile / "DevToolsActivePort"
        websocket_url = None
        for _ in range(120):
            if cls.browser.poll() is not None:
                cls.browser_problem = f"Navegador encerrou com código {cls.browser.returncode}"
                break
            if active_port_file.exists():
                try:
                    debug_port = int(active_port_file.read_text(encoding="ascii").splitlines()[0])
                    target_request = urllib.request.Request(
                        f"http://127.0.0.1:{debug_port}/json/new?about:blank", method="PUT"
                    )
                    with urllib.request.urlopen(target_request, timeout=2) as response:
                        websocket_url = json.loads(response.read().decode("utf-8"))["webSocketDebuggerUrl"]
                    break
                except (OSError, ValueError, KeyError, urllib.error.URLError):
                    pass
            time.sleep(0.1)
        if not websocket_url:
            cls.browser_problem = cls.browser_problem or "Chrome DevTools Protocol indisponível"
            return
        try:
            cls.cdp = CDPWebSocket(websocket_url)
            cls.cdp.command("Page.enable")
            cls.cdp.command("Runtime.enable")
            cls.cdp.command("Log.enable")
            cls.cdp.command("Page.navigate", {"url": cls.base})
            deadline = time.monotonic() + 15
            while time.monotonic() < deadline:
                state = cls.cdp.evaluate("document.readyState")
                loaded = cls.cdp.evaluate("document.querySelector('#results-count')?.textContent || ''")
                if state == "complete" and "vendas encontradas" in loaded:
                    return
                time.sleep(0.1)
            cls.browser_problem = "Página não terminou de carregar vendas em 15 segundos"
        except Exception as exc:  # navegador inacessível é bloqueio, nunca aprovação
            cls.browser_problem = f"Falha ao controlar o navegador: {type(exc).__name__}: {exc}"

    @classmethod
    def tearDownClass(cls) -> None:
        if cls.cdp:
            cls.cdp.close()
        stop_process(cls.browser)
        stop_process(cls.server)
        cls.temp.cleanup()

    def require_browser(self) -> None:
        if self.browser_problem or not self.cdp:
            self.skipTest(f"BLOQUEADO/PENDENTE: {self.browser_problem}")

    def js(self, script: str):
        self.require_browser()
        return self.cdp.evaluate(script)

    def reload_page(self) -> None:
        self.require_browser()
        self.cdp.command("Page.navigate", {"url": self.base})
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            if self.js("document.readyState") == "complete" and "vendas encontradas" in self.js("document.querySelector('#results-count')?.textContent || ''"):
                return
            time.sleep(0.1)
        self.fail("A página não voltou ao estado inicial após recarga")

    def expected_filtered(self, city: str = "", category: str = "") -> list[dict]:
        payload = json.loads(DATA_FILE.read_text(encoding="utf-8"))
        return [row for row in payload["vendas"]
                if (not city or row["cidade"] == city)
                and (not category or row["categoria"] == category)]

    def assert_render_matches(self, city: str = "", category: str = "") -> None:
        rows = self.expected_filtered(city, category)
        aggregate = totals(rows)
        average = cents(aggregate["total"] / aggregate["count"]) if rows else Decimal("0.00")
        result = self.js("""(() => ({
          total: document.querySelector('#kpi-total').textContent,
          count: document.querySelector('#kpi-count').textContent,
          average: document.querySelector('#kpi-average').textContent,
          resultCount: document.querySelector('#results-count').textContent,
          table: [...document.querySelectorAll('#sales-table-body tr')].map(tr => [...tr.cells].map(td => td.textContent.trim())),
          category: [...document.querySelectorAll('#category-chart .bar-row')].map(row => [row.querySelector('.bar-label').textContent, row.querySelector('.bar-value').textContent]),
          city: [...document.querySelectorAll('#city-chart .bar-row')].map(row => [row.querySelector('.bar-label').textContent, row.querySelector('.bar-value').textContent]),
          emptyMessages: [...document.querySelectorAll('.chart-empty')].map(node => node.textContent),
          errorVisible: !document.querySelector('#load-error').hidden,
          visibleText: document.body.innerText
        }))()""")
        self.assertFalse(result["errorVisible"], "Falha ao carregar os dados no dashboard")
        self.assertEqual(result["total"], self.format_currency(aggregate["total"]))
        self.assertEqual(result["count"], format(aggregate["count"], ",d").replace(",", "."))
        self.assertEqual(result["average"], self.format_currency(average))
        self.assertIn(str(aggregate["count"]), result["resultCount"].replace(".", ""))
        self.assertEqual(len(result["table"]), max(1, len(rows)))
        if rows:
            expected_categories = totals(rows, "categoria")
            expected_cities = totals(rows, "cidade")
            order = lambda mapping: sorted(mapping.items(), key=lambda item: (-item[1], item[0].casefold()))
            expected_chart_cat = [[name, self.format_currency(value)] for name, value in order(expected_categories)]
            expected_chart_city = [[name, self.format_currency(value)] for name, value in order(expected_cities)]
            self.assertEqual(result["category"], expected_chart_cat)
            self.assertEqual(result["city"], expected_chart_city)
            self.assertEqual(result["emptyMessages"], [])
            # A linha exibida na tabela deve ser identificável e seus valores numéricos devem bater.
            displayed_ids = [line[0] for line in result["table"]]
            self.assertEqual(displayed_ids, [str(row["id_venda"]) for row in rows])
            for displayed, expected in zip(result["table"], rows):
                expected_date = date.fromisoformat(str(expected["data"])).strftime("%d/%m/%Y")
                self.assertEqual(displayed[1], expected_date)
                self.assertEqual(displayed[2:5], [expected["cidade"], expected["categoria"], expected["produto"]])
                self.assertEqual(displayed[5], format(expected["quantidade"], ",d").replace(",", "."))
                self.assertEqual(displayed[6], self.format_currency(Decimal(str(expected["preco_unitario"]))))
                self.assertEqual(displayed[7], self.format_currency(Decimal(str(expected["valor_venda"]))))
        else:
            self.assertEqual(result["table"][0][0], "Nenhuma venda encontrada. Altere ou limpe os filtros para ver resultados.")
            self.assertEqual(len(result["category"]), 0)
            self.assertEqual(len(result["city"]), 0)
            self.assertEqual(len(result["emptyMessages"]), 2)
        self.assertNotIn("NaN", result["visibleText"])
        self.assertNotIn("Infinity", result["visibleText"])

    @staticmethod
    def format_currency(value: Decimal) -> str:
        value = cents(value)
        return "R$\u00a0" + format(value, ",.2f").replace(",", "X").replace(".", ",").replace("X", ".")

    def test_live_dashboard_filters_empty_reset_and_values(self) -> None:
        self.require_browser()
        self.reload_page()
        self.assert_render_matches()
        self.js("document.querySelector('#filter-city').value='Campinas'; document.querySelector('#filter-city').dispatchEvent(new Event('change',{bubbles:true}));")
        self.assert_render_matches(city="Campinas")
        self.js("document.querySelector('#filter-city').value=''; document.querySelector('#filter-category').value='Livros'; document.querySelector('#filter-category').dispatchEvent(new Event('change',{bubbles:true}));")
        self.assert_render_matches(category="Livros")
        self.js("document.querySelector('#filter-city').value='Santos'; document.querySelector('#filter-category').value='Acessórios'; document.querySelector('#filter-city').dispatchEvent(new Event('change',{bubbles:true})); document.querySelector('#filter-category').dispatchEvent(new Event('change',{bubbles:true}));")
        self.assert_render_matches(city="Santos", category="Acessórios")
        # Todas as combinações reais existem nesta base: injeta opção impossível somente no DOM
        # para executar o contrato de estado vazio, sem mudar produto nem arquivo de dados.
        self.js("const s=document.querySelector('#filter-category'); const o=new Option('Categoria sem vendas','__tester_empty__'); s.add(o); s.value='__tester_empty__'; s.dispatchEvent(new Event('change',{bubbles:true}));")
        self.assert_render_matches(category="__tester_empty__")
        self.js("document.querySelector('#clear-filters').click()")
        self.assertEqual(self.js("[document.querySelector('#filter-city').value,document.querySelector('#filter-category').value]"), ["", ""])
        self.assertEqual(self.js("document.activeElement.id"), "filter-city")
        self.assert_render_matches()

    def test_http_javascript_runtime_responsive_viewports_and_keyboard(self) -> None:
        self.require_browser()
        self.reload_page()
        # HTTP carregou todos os arquivos esperados; Node --check é validado na classe HTTP.
        self.assertEqual(self.js("location.protocol"), "http:")
        self.assertEqual(self.js("document.querySelectorAll('#sales-table-body tr').length"), 180)
        # Erros síncronos do runtime capturados pelo protocolo.
        self.assertFalse([event for event in self.cdp.events if event.get("method") == "Runtime.exceptionThrown"],
                         "Chrome reportou exceção JavaScript durante a carga")
        self.assertEqual(self.js("document.documentElement.scrollWidth <= window.innerWidth"), True,
                         "Página deve caber na largura do viewport desktop")

        for width, height in ((1440, 900), (390, 844), (320, 720)):
            self.cdp.command("Emulation.setDeviceMetricsOverride", {
                "width": width, "height": height, "deviceScaleFactor": 1, "mobile": width <= 480,
            })
            time.sleep(0.15)
            layout = self.js("""(() => ({
              viewport: innerWidth, document: document.documentElement.scrollWidth,
              city: document.querySelector('#filter-city').getBoundingClientRect().toJSON(),
              category: document.querySelector('#filter-category').getBoundingClientRect().toJSON(),
              clear: document.querySelector('#clear-filters').getBoundingClientRect().toJSON(),
              tableScroll: getComputedStyle(document.querySelector('.table-scroll')).overflowX,
              labels: [...document.querySelectorAll('.field label')].map(e=>getComputedStyle(e).fontSize)
            }))()""")
            self.assertLessEqual(layout["document"], layout["viewport"], f"Overflow em viewport {width}px")
            for key in ("city", "category", "clear"):
                self.assertGreater(layout[key]["width"], 0, f"{key} inutilizável em {width}px")
                self.assertGreaterEqual(layout[key]["height"], 24, f"{key} alvo muito pequeno em {width}px")
            self.assertEqual(layout["tableScroll"], "auto", "Tabela deve continuar rolável horizontalmente")
            self.assertTrue(all(float(size.rstrip("px")) >= 10 for size in layout["labels"]))

        self.cdp.command("Emulation.clearDeviceMetricsOverride")
        self.js("document.activeElement.blur()")
        tab_order = []
        for _ in range(10):
            self.cdp.command("Input.dispatchKeyEvent", {"type": "keyDown", "key": "Tab", "code": "Tab"})
            self.cdp.command("Input.dispatchKeyEvent", {"type": "keyUp", "key": "Tab", "code": "Tab"})
            active_id = self.js("document.activeElement.id")
            tab_order.append(active_id)
            if active_id == "filter-city":
                break
        self.assertIn("filter-city", tab_order, f"Tabulação não alcançou o filtro; sequência observada: {tab_order}")
        self.assertEqual(self.js("document.activeElement.id"), "filter-city")
        focused = self.js("document.querySelector('#filter-city').matches(':focus-visible')")
        self.assertTrue(focused, "Filtro deve exibir foco visível ao navegar pelo teclado")
        # Interação nativa de teclado: seta para baixo seleciona opção e atualiza a página.
        self.cdp.command("Input.dispatchKeyEvent", {"type": "keyDown", "key": "ArrowDown", "code": "ArrowDown"})
        self.cdp.command("Input.dispatchKeyEvent", {"type": "keyUp", "key": "ArrowDown", "code": "ArrowDown"})
        selected_city = self.js("document.querySelector('#filter-city').value")
        self.assertTrue(selected_city, "Seta para baixo não conseguiu selecionar uma cidade")
        self.assert_render_matches(city=selected_city)
        # O reset também é acionável pelo teclado e retorna o foco a um filtro.
        tab_to_clear = []
        for _ in range(8):
            self.cdp.command("Input.dispatchKeyEvent", {"type": "keyDown", "key": "Tab", "code": "Tab"})
            self.cdp.command("Input.dispatchKeyEvent", {"type": "keyUp", "key": "Tab", "code": "Tab"})
            active_id = self.js("document.activeElement.id")
            tab_to_clear.append(active_id)
            if active_id == "clear-filters":
                break
        self.assertIn("clear-filters", tab_to_clear, f"Tabulação não alcançou limpar filtros: {tab_to_clear}")
        self.js("window.__testerClearClicks=0; document.querySelector('#clear-filters').addEventListener('click',()=>window.__testerClearClicks++)")
        self.cdp.command("Input.dispatchKeyEvent", {"type": "keyDown", "key": "Enter", "code": "Enter", "windowsVirtualKeyCode": 13, "nativeVirtualKeyCode": 13, "text": "\r", "unmodifiedText": "\r"})
        self.cdp.command("Input.dispatchKeyEvent", {"type": "keyUp", "key": "Enter", "code": "Enter"})
        keyboard_clicks = self.js("window.__testerClearClicks")
        self.assertEqual(self.js("[document.querySelector('#filter-city').value,document.querySelector('#filter-category').value]"), ["", ""])
        self.assertGreaterEqual(keyboard_clicks, 1, "Enter não ativou o botão limpar filtros")
        self.assertEqual(self.js("document.activeElement.id"), "filter-city")
        self.assert_render_matches()

    def test_browser_console_and_requested_resources_have_no_errors(self) -> None:
        self.require_browser()
        self.reload_page()
        # Drena eventos que o CDP já entregou durante carga/estabilização.
        self.js("document.readyState")
        console_errors = [event for event in self.cdp.events
                          if event.get("method") == "Log.entryAdded"
                          and event.get("params", {}).get("entry", {}).get("level") == "error"]
        self.assertEqual(console_errors, [], f"Console do navegador reportou erros/recursos ausentes: {console_errors}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
