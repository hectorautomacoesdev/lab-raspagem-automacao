# Ethical Hacking — 20 formas de ganhar dinheiro no setor (mapeamento)

> ⚠️ **Leia primeiro:** isto é um **mapeamento informativo do setor** — como as pessoas/empresas ganham dinheiro com segurança ofensiva. **NÃO é um plano de negócio nosso.** A pedido do Hector, os **nossos** planos de ação com ethical hacking ficam para uma fase futura (ele pedirá). Aqui o objetivo é só **enxergar o terreno** e ter as ideias na mesa.
>
> Base: [`07-ethical-hacking.md`](07-ethical-hacking.md) (estudo) + pesquisa externa (fontes lá). "Barreira" = dificuldade de entrada; "Potencial" = renda realista com base nas fontes.

**Legenda:** Barreira (🟢 baixa / 🟡 média / 🔴 alta) · 🔗 = forte sinergia com as skills que estudamos (scraping/automação/Android/performance).

---

## Emprego / consultoria

### 1. Pentester (CLT ou consultoria) 🔗
Executar testes de intrusão para clientes/empresa. **Barreira:** 🔴 (OSCP/PNPT abrem portas). **Potencial:** BR R$ 13,4-18,4k/mês (sênior até ~R$ 19-23k); global ~US$ 102-105k/ano. Demanda alta (déficit de profissionais).

### 2. Red Team / operações ofensivas
Simulações adversárias avançadas (evasão, persistência, engenharia social). **Barreira:** 🔴 (OSEP). **Potencial:** topo das faixas salariais.

### 3. Blue Team / SOC / Detection Engineering
O lado defensivo: monitorar, caçar ameaças, responder a incidentes. **Barreira:** 🟡. **Potencial:** **o maior volume de vagas** (déficit global de 3,4-4,8 mi).

### 4. Auditoria & compliance (PCI-DSS, ISO 27001, LGPD)
Pentests e *gap assessments* exigidos por norma. **Barreira:** 🟡 (conhecimento regulatório). **Potencial:** **recorrente** — empresas precisam todo ano.

### 5. vCISO / consultoria estratégica
Assessoria de segurança de alto nível para empresas sem CISO próprio. **Barreira:** 🔴 (experiência). **Potencial:** muito alto por hora.

### 6. Forense digital & resposta a incidentes (DFIR)
Investigar pós-incidente (vazamento, ransomware). **Barreira:** 🔴. **Potencial:** alto, sobretudo em emergência.

## Crowdsourced / por resultado

### 7. Bug bounty (público) 🔗
Caçar bugs em plataformas (HackerOne/Bugcrowd/Intigriti/YesWeHack). **Barreira:** 🟢 entrar, 🔴 lucrar. **Potencial:** mediana ~US$ 1,6k/ano (~40% não recebem nada); topo US$ 100-500k/ano. **Sinergia:** automação de recon cobre mais superfície.

### 8. Programas privados / elite (Synack, Bugcrowd Elite, HackerOne private) 🔗
Convites por desempenho — melhor sinal/ruído que o bounty público. **Barreira:** 🔴 (seleção). **Potencial:** bem acima da média do bounty aberto.

### 9. CTFs com prêmio 🔗
Competições pagas (Google CTF, Plaid, Hackerverse US$ 100k, DEF CON). **Barreira:** 🔴 (skill). **Potencial:** prêmios pontuais + **valor enorme de portfólio/recrutamento**.

### 10. Pesquisa de vulnerabilidade / venda legítima de 0-day
Via Zero Day Initiative ou programas de fabricantes (Google/Apple/MS pagam US$ 1mi+ por certos 0-days). **Barreira:** 🔴🔴 (muito alta). **Potencial:** altíssimo, porém raro.

## Especializações técnicas (alta sinergia conosco)

### 11. 🔥 Pentest MOBILE (Android/iOS) 🔗
Testar apps com **emulador + root/Magisk + Frida + Burp** — exatamente o quintal do Hans. **Barreira:** 🟡 (Frida/objection/MASTG). **Potencial:** **alto**, poucos especialistas. *A maior sinergia de todas — ver [`07`](07-ethical-hacking.md) §4e.*

### 12. AppSec / segurança de APIs 🔗
Revisar e testar apps web/APIs (área em alta). **Barreira:** 🟡. **Potencial:** alto e crescente.

### 13. Cloud security (AWS/Azure/GCP) 🔗
Misconfigurations, IAM, exposições. **Barreira:** 🟡-🔴 (certs cloud). **Potencial:** alto, em crescimento.

### 14. OSINT como serviço 🔗
Investigação, *due diligence*, *threat intel* — **scraping/automação aplicados**. **Barreira:** 🟡. **Potencial:** bom em jurídico/corporativo.

### 15. Vulnerability/Attack Surface Management 🔗
Scanning contínuo da superfície de ataque (automação de recon como SaaS/serviço). **Barreira:** 🟡. **Potencial:** **recorrente**.

### 16. Engenharia social / phishing simulado (autorizado)
Campanhas de conscientização e teste. **Barreira:** 🟡. **Potencial:** bom (complementa red team).

## Produto / conteúdo (escalável)

### 17. Escrever e monetizar ferramentas de segurança 🔗
*Tooling* em Python/Cython/C: scanners, fuzzers, módulos Frida, plugins/BApps de Burp. **Barreira:** 🟡 (programação forte — **perfil do Hans**). **Potencial:** indireto (reputação→consultoria) a direto (licenças, sponsors).

### 18. Treinamento, cursos e conteúdo 🔗
YouTube, Udemy, write-ups, livros, bootcamps — **em PT-BR há lacuna**. **Barreira:** 🟢-🟡. **Potencial:** escalável (renda passiva + autoridade), igual à ideia #11 do plano principal.

### 19. "In-house hacker" / programa interno
Emprego dedicado a achar bugs no produto da própria empresa. **Barreira:** 🟡-🔴. **Potencial:** salário sênior estável.

### 20. Freelance / contratos curtos 🔗
Projetos pontuais de pentest para PMEs/startups (PNPT + CTFs credenciam). **Barreira:** 🟡. **Potencial:** variável; bom para começar.

---

## Observação (informativa, não é plano)

Se um dia formos por esse caminho, as avenidas com **🔗 (sinergia com o que já sabemos)** seriam as portas naturais — em especial **#11 pentest mobile** (emulador+root+Frida+Burp), **#14/#15 OSINT e ASM** (scraping/recon automatizado), **#17 ferramentas** (Python/Cython) e **#18 conteúdo PT-BR**. Mas, conforme combinado, **o plano de ação fica para quando o Hector pedir** — aqui paramos no mapeamento.

> ⚖️ **Lembrete ético/legal:** tudo isso exige **autorização** (ver [`07`](07-ethical-hacking.md) §9 — Lei Carolina Dieckmann, art. 154-A). A mesma régua de [`06-fontes-externas.md`](06-fontes-externas.md): sem autorização, não tem negócio.
