# Deep-dive: Ethical Hacking (estudo)

> Estudo do campo de **hacking ético / segurança ofensiva** e — principalmente — de **como ele se conecta com as habilidades que estudamos** (scraping, automação de Android/Windows, performance em Python/Cython/C). Pesquisa feita com apoio de subagente; fontes 2025-2026 citadas ao longo e consolidadas no fim.
>
> 📌 **Escopo desta fase:** a pedido do Hector, aqui é **só estudo + referências**. O **mapeamento de 20 formas de ganhar dinheiro no setor** está em [`ethical-hacking-oportunidades.md`](ethical-hacking-oportunidades.md) (informativo). Os **nossos** planos de negócio de ethical hacking ficam para quando o Hector pedir.

## TL;DR

Hacking ético é usar as **mesmas técnicas de um atacante**, mas **com autorização** e para **defender**. A grande notícia para nós: as skills do Hans mapeiam **quase 1:1** para segurança ofensiva — Python é a língua franca do pentester, recon/OSINT **é scraping**, fuzzing é automação de requests acelerada (Cython/C), e — o ponto mais forte — **pentest mobile** usa exatamente **emulador Android + root/Magisk + interceptação de tráfego**, que é o quintal do Hans. A fronteira entre crime e profissão é **uma só palavra: autorização**.

---

## 1. O que é (e o que não é)

"Ethical hacking" é guarda-chuva. Dentro dele há modalidades com escopos diferentes:

| Modalidade | O que é | Foco |
|---|---|---|
| **Pentest** | avaliação técnica e **pontual** contra uma metodologia, muitas vezes por compliance (PCI-DSS, ISO 27001) | achar e demonstrar vulnerabilidades num escopo definido |
| **Ethical hacking (amplo)** | avaliação mais abrangente da postura de segurança | superfície maior que o pentest pontual |
| **Red Team** | simulação adversária **realista e furtiva**, ponta a ponta, sem aviso à defesa | testa **detecção e resposta**, não só falhas |
| **Blue Team** | a defesa: monitorar, caçar ameaças, endurecer, responder a incidentes | proteção contínua |
| **Purple Team** | red + blue colaborando | maximizar aprendizado defensivo |
| **Bug bounty** | pesquisadores independentes pagos por bug válido reportado | contínuo, crowdsourced, paga por resultado |

**Tipos de pentest por superfície:** web (o mais demandado), rede/infra (incl. Active Directory), **mobile (Android/iOS)** ⭐, cloud (AWS/Azure/GCP), wireless, engenharia social (phishing), física.

## 2. Como se faz: metodologia

Fluxo consolidado de um pentest:

```
1. Pré-engajamento   → escopo, regras de engajamento, CONTRATO, autorização
2. Recon / OSINT     → coletar info (subdomínios, e-mails, tecnologias)      ← É SCRAPING
3. Scanning/enum     → portas, serviços, versões, vulnerabilidades
4. Exploração        → obter acesso usando as falhas
5. Pós-exploração    → escalar privilégio, mover-se lateralmente, persistir
6. Relatório         → achados, impacto, evidências, remediação              ← entregável nº1
```

**Frameworks que valem conhecer:**
- **PTES** — padrão de execução em 7 fases (do pré-engajamento ao relatório) + guia técnico.
- **OWASP WSTG** — o checklist técnico aberto de teste **web/API** (a referência de casos de teste). **OWASP Top 10** — as 10 categorias de risco mais críticas.
- **OWASP MASVS/MASTG** — os equivalentes para **mobile**.
- **MITRE ATT&CK** — base de táticas/técnicas de adversários reais; liga o que o red team faz ao que o blue team detecta.
- **NIST SP 800-115** — guia governamental dos EUA para avaliação de segurança (compliance).

## 3. Ferramentas do ofício (por fase)

| Fase | Ferramentas |
|------|-------------|
| Recon/OSINT | `theHarvester`, `Amass`/`subfinder`, `Shodan`, `recon-ng`, `Maltego` |
| Scanning | **Nmap** (mapeamento de rede), `Nessus`/`OpenVAS` (scanners de vuln) |
| Web | **Burp Suite** (padrão de mercado: proxy + scanner + Intruder/Repeater), OWASP ZAP, `ffuf`/`gobuster` (fuzzing), **Nuclei** (templates), **sqlmap** (SQLi), Nikto |
| Exploração | **Metasploit Framework** |
| Senhas | **Hashcat** (GPU), Hydra, John the Ripper |
| AD / pós-exploração | **BloodHound**, **Impacket** (Python!), NetExec, Mimikatz |
| Tráfego | **Wireshark** |
| Mobile | **Frida**, **objection**, `apktool`, `jadx`, **ADB**, **Magisk** |

## 4. A conexão com o que estudamos (o coração) ⭐

As habilidades do Hans são, em boa parte, **as mesmas** da segurança ofensiva:

**a) Recon/OSINT = scraping.** Enumerar subdomínios, coletar e-mails/nomes, consultar `whois`/`Shodan` — `theHarvester` é, na essência, um **scraper de OSINT**. Quem já faz coletores resilientes (proxy, parsing, paginação) **já tem o motor de recon**.

**b) Fuzzing = scraping concorrente acelerado.** `ffuf`/`Nuclei` são *request engines* de alta vazão. As técnicas de scraping (async/threads, throttling, rate-limit) viram fuzzers; **Cython/C** ([`04`](04-velocidade-cython.md)) aceleram os laços de geração/comparação de payloads. O `Hashcat` mostra por que performance importa: quebrar hash é throughput bruto.

**c) Escrever ferramentas/exploits em Python.** `Scapy` (forja pacotes), `Impacket` (dump de hash NTLM, execução remota, movimento lateral) — quem programa em Python já produz PoCs e *tooling* sob medida. O perfil do Hans (micro-libs focadas + performance) é **ideal** para isso.

**d) Automação de browser testa apps web.** Selenium/Playwright (do scraping moderno) mantêm sessão autenticada, populam formulários e testam *business logic*/XSS dinâmico durante o pentest.

**e) 🔥 Pentest MOBILE com emulador + root/Magisk — a sinergia mais forte.** O fluxo padrão de mobile pentest em 2025 é **exatamente** o que o Hans domina ([`02`](02-android-adb-magisk.md)):
   - rodar a app em **emulador/AVD rooteado** com **Magisk** (automatizado);
   - usar **Magisk** para instalar a **CA do Burp** no *system trust store* e **interceptar HTTPS**;
   - usar **Frida/objection** para burlar **certificate pinning**, **detecção de root** e checagens em memória, e extrair chaves;
   - descompilar (`apktool`/`jadx`), controlar via **ADB**;
   - seguir o checklist **OWASP MASTG**.
   > Quem já automatiza Android (ADB, controle de UI, emuladores) **e entende root/Magisk** tem **vantagem direta e rara** aqui. É o ponto onde o conhecimento do Hans vale ouro em segurança.

**f) Análise de memória.** Frida instrumenta processos em runtime; saber ler/escrever memória e hookar funções (o "pé de cabra"/`pdmemedit` do Hans — ver [`01`](01-web-scraping-anti-bot.md) §4) é a mesma família de habilidade.

**g) Proxies / interceptação.** Domínio de proxy HTTP(S), rotação e MITM (já usado em scraping resiliente) **é** a base de interceptar tráfego no Burp.

## 5. Trilha de aprendizado e certificações

| Cert | Nível | Custo aprox. | Observação |
|------|-------|--------------|------------|
| CompTIA **Security+** | iniciante | ~US$ 400 | porta de entrada, RH reconhece |
| **eJPT** | iniciante prático | baixo | ótimo 1º degrau hands-on |
| CompTIA **PenTest+** | iniciante/inter. | ~US$ 404 | todas as fases + compliance |
| **CEH** | inter. | ~US$ 950-1.300 | muito pedido em vagas/governo |
| **PNPT** (TCM) | inter./avançado | ~US$ 499 | rede realista (OSINT+AD+relatório), ótimo custo-benefício |
| **OSCP** (OffSec) | **muito difícil** | ~US$ 1.499-2.499 | **padrão-ouro**, exame de 24h |
| **OSEP / OSWE** | avançado | alto | red team / web avançado |

**Trilha sugerida:** Security+/eJPT → PNPT ou PenTest+ → **OSCP** → especialização (OSWE web / OSEP red team).

**Praticar (com foco no que é grátis):**
- **PortSwigger Web Security Academy** — **100% grátis**, o melhor recurso para web.
- **picoCTF** — grátis, curado pela Carnegie Mellon (ótimo para começar).
- **TryHackMe** (tier grátis + Premium ~US$ 10,50/mês), **Hack The Box** (free + VIP ~US$ 25/mês), **VulnHub** (VMs grátis), **PentesterLab**.

## 6. Bug bounty — com honestidade nos números

Como funciona: a empresa publica escopo + tabela de recompensas; o pesquisador caça e faz **divulgação responsável** via plataforma (**HackerOne**, **Bugcrowd**, **Intigriti**, **YesWeHack**). Paga só por bug **válido e único**.

**O que mais paga em 2025:** o mercado migrou de XSS (em queda) para **falhas de controle de acesso/autorização** — **IDOR** subiu (+23% em recompensa), **SSRF** e **Information Disclosure** em alta; **RCE** e **business logic** no topo. Faixas (Bugcrowd): P4 US$ 175-600 · P3 US$ 500-2.500 · P2 US$ 1.500-7.500 · **P1 US$ 3.500-20.000+** (críticas em programas grandes: US$ 50k-200k+).

**A realidade (importante):**
- HackerOne pagou **US$ 81 mi** em 12 meses, mas a **média por pesquisador é ~US$ 1.620/ano**.
- **~40%** de quem envia ≥1 relatório **nunca recebe nada** (duplicado/fora de escopo/informativo).
- O topo (poucos %) faz **US$ 100k-500k/ano**; "side-hustlers" bons fazem US$ 20k-50k/ano.

> **Tradução:** bug bounty é **excelente para aprender e montar portfólio**, mas **ruim como renda principal no começo**. A vantagem de quem automatiza (recon/scraping em escala) é cobrir mais superfície e achar IDOR/SSRF antes dos outros.

## 7. Mercado e salários (2025-2026)

- **Brasil — cybersecurity:** US$ 4,61 bi (2025) → US$ 6,98 bi (2030), **CAGR 8,6%**.
- **Déficit global de profissionais:** ~**3,4 a 4,8 milhões** de vagas não preenchidas; Brasil ~200 mil.
- **Salários — Brasil (Robert Half 2025, mensal):** Analista de Segurança Jr **R$ 6,1-10,2k**, Pleno **R$ 8,4-14,1k**, Sr **R$ 11,4-19,3k**; **PenTester R$ 13,4-18,4k** (topo citado até ~R$ 23k).
- **Global:** pentester ~**US$ 102-105k/ano**.
- **Tendências:** **IA na segurança** (HackerOne reportou **+210%** em relatórios de vuln de IA), **cloud**, **AppSec/API**, automação de recon/*attack surface management*.

## 8. CTFs (Capture The Flag)

Competições de resolver desafios (web, cripto, reversing, pwn, forense, OSINT) capturando "flags". Há **prêmio em dinheiro** (Google CTF >US$ 31k; Plaid CTF US$ 8.192 ao 1º; **Hackerverse/EC-Council US$ 100k**; DEF CON CTF é a final mais prestigiada), mas o **maior ROI é em carreira**: write-ups e rankings **provam que você sabe fazer** (mais que uma prova teórica) e empresas recrutam ali. Praticar: picoCTF, HTB, TryHackMe, CyberTalents, agenda no **CTFtime.org**.

> **Conexão com o Hans:** reversing/pwn exploram C e internals; web/OSINT premiam quem automatiza em Python. Write-ups viram portfólio.

## 9. Legalidade e ética (Brasil em foco)

**A linha entre profissão e crime é a AUTORIZAÇÃO.** Princípios inegociáveis:
1. **Autorização explícita e por escrito** (escopo + *rules of engagement*).
2. **Contrato** com limites, janelas, dados sensíveis e responsabilidades.
3. **Divulgação responsável** (reportar ao dono / via bug bounty, dar prazo antes de publicar).
4. **Ficar dentro do escopo** — não pivotar para sistemas/dados não autorizados.

**Leis:**
- 🇧🇷 **Lei Carolina Dieckmann (12.737/2012)** — o **art. 154-A** pune invadir dispositivo "**sem autorização expressa ou tácita** do titular" (pena 1-4 anos + multa). É literalmente a palavra "autorização" que separa pentest de crime.
- 🇧🇷 **Marco Civil (12.965/2014)** e **LGPD (13.709/2018)** — uso da internet, privacidade e proteção de dados (pentest que toca dado pessoal precisa respeitar a LGPD no manuseio/descarte).
- 🇺🇸 **CFAA** — criminaliza acesso não autorizado ou além do autorizado.

> É **a mesma lógica do scraping**: dado público + autorização/ToS respeitados = legal; acesso não autorizado = crime. A ética que adotamos em [`06-fontes-externas.md`](06-fontes-externas.md) vale aqui também.

---

## Fontes (principais)

- [NCC Group — Pentest vs Red Team vs Bug Bounty](https://www.nccgroup.com/research/pentesting-v-red-teaming-v-bug-bounty/) · [IBM — Red Teaming](https://www.ibm.com/think/topics/red-teaming)
- [Security Boulevard — Pentest Methodology 2025](https://securityboulevard.com/2025/08/penetration-testing-methodology-step-by-step-breakdown-for-2025/) · [OWASP WSTG](https://owasp.org/www-project-web-security-testing-guide/latest/3-The_OWASP_Testing_Framework/1-Penetration_Testing_Methodologies.html)
- [Intruder — Top Pentesting Tools](https://www.intruder.io/blog/pentesting-tools) · [EC-Council — 35+ Pentest/AI Tools](https://www.eccouncil.org/cybersecurity-exchange/penetration-testing/35-pentesting-tools-and-ai-pentesting-tools-for-cybersecurity/)
- [Infosec — Python for Pentesters](https://www.infosecinstitute.com/skills/learning-paths/python-for-pentesters/) · [OWASP MASTG — Bypass Cert Pinning](https://mas.owasp.org/MASTG/techniques/android/MASTG-TECH-0012/) · [blog.lrvt.de — Android Pentest Lab](https://blog.lrvt.de/android-penetration-testing-lab-environment/) · [Sekurno — Mobile Pentesting](https://www.sekurno.com/post/a-definitive-guide-to-mobile-pentesting)
- [FlashGenius — OSCP vs CEH vs eJPT 2025](https://flashgenius.net/blog-article/best-ethical-hacking-certifications-2025-oscp-ceh-and-ejpt) · [CompTIA PenTest+](https://www.comptia.org/en-us/certifications/pentest/) · [TryHackMe Pricing](https://tryhackme.com/pricing)
- [BleepingComputer — HackerOne US$ 81mi](https://www.bleepingcomputer.com/news/security/hackerone-paid-81-million-in-bug-bounties-over-the-past-year/) · [Bug Bounty Economics](https://bug-bounties.as93.net/learn/bug-bounty-economics-what-hunters-actually-earn/) · [AceFortis — Realistic Earnings](https://acefortis.com/2026/04/24/bug-bounty-payouts-explained-realistic-earnings-beginners/)
- [MarketsandMarkets — Brazil Cybersecurity](https://www.marketsandmarkets.com/Market-Reports/brazil-cybersecurity-market-155811757.html) · [DeepStrike — Skills Gap](https://deepstrike.io/blog/cybersecurity-skills-gap) · [BoletimSec — Salários BR 2025](https://boletimsec.com/salarios-de-ciberseguranca-no-brasil/) · [electroIQ — Job Stats](https://electroiq.com/stats/cybersecurity-job-statistics/)
- [DEF CON CTF](https://defcon.org/html/links/dc-ctf.html) · [Google CTF Rules](https://capturetheflag.withgoogle.com/rules) · [EC-Council Hackerverse US$ 100k](https://www.eccouncil.org/ec-council-in-news/ec-council-launches-the-hackerverse-ctf-a-free-global-capture-the-flag-competition-with-100000-in-prizes/) · [CTFtime](https://ctftime.org/event/list/)
- [Aurum — Lei Carolina Dieckmann](https://www.aurum.com.br/blog/lei-carolina-dieckmann/) · [LGPD/FURG — Lei 12.737/2012](https://lgpd.furg.br/legislacao/lei-n-12-737-de-30-de-novembro-de-2012-lei-carolina-dieckmann)

→ Mapeamento das **20 formas de monetizar no setor**: [`ethical-hacking-oportunidades.md`](ethical-hacking-oportunidades.md).
