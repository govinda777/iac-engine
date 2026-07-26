# Documentação da Plataforma Centralizada de IaC (Hub)

Bem-vindo à documentação do **iac-engine**. Esta pasta centraliza todo o conhecimento técnico, decisões de arquitetura e guias de governança da nossa plataforma de entrega contínua de infraestrutura de TI.

A **iac-engine** não é apenas um executor ou runner de comandos de infraestrutura como código (IaC). Ela atua como um **gatekeeper de segurança de alta governança** e um **gestor de ciclo de vida ponta a ponta**.

A jornada de execução do usuário baseia-se na seguinte espinha dorsal lógica:

```
[ Usuário fornece Autenticação via OIDC ]
                     |
                     v
[ Gateways de Segurança & Critérios de Governança (Validação) ]
                     |
                     v
[ Gestão de Ciclo de Vida Efémera e Serverless (Plan/Apply) ]
```

---

## Estrutura da Pasta `/docs`

Abaixo está a árvore de diretórios que organiza a nossa base de conhecimento:

```text
docs/
├── adr/
│   ├── 001_initial_architecture.md       # Decisão da arquitetura inicial da plataforma
│   └── 002_inversion_of_control_lifecycle.md # Inversão de Controle do Ciclo de Vida (Engine Hub decide)
├── templates/
│   ├── adr_template.md                  # Template para novas Architectural Decision Records
│   └── rfc_template.md                  # Template para novas Request For Comments (Foco em Segurança/Ciclo de Vida)
├── architectural_roadmap_paradigms.md    # Evolução para modelos avançados (Crossplane/vCluster)
├── authentication_onboarding.md         # Manual de onboarding do OIDC e políticas de confiança IAM
├── business_documentation.md             # Visão estratégica de negócios, métricas de ROI e roadmap do produto
├── lifecycle_management.md              # Gerenciamento de ciclo de vida (Git Event -> Execução Hub)
├── security_gateways.md                 # Detalhes de conformidade, auditorias, políticas globais e RCPs
├── serverless_native_iac_engine.md      # Especificação detalhada da execução Serverless/Efémera
└── README.md                            # Este guia técnico global da pasta docs
```

---

## Os Quatro Pilares do Nosso Fluxo de Governança

### 1. [Onboarding de Autenticação](authentication_onboarding.md)
O cliente (Spoke) estabelece uma identidade federada forte utilizando **OpenID Connect (OIDC)** com a nuvem, eliminando totalmente o uso de credenciais estáticas ou de longa duração. As IAM Roles possuem *Trust Policies* estritamente parametrizadas ao nível de repositório Git do cliente para evitar acessos cruzados ou vazamentos.

### 2. [Gateways de Segurança](security_gateways.md)
Antes de qualquer alteração física ser realizada na AWS, a engine intercepta o código do Spoke e valida o seguimento estrito de critérios de conformidade e segurança da organização, servindo como uma barreira automática (Guardrails) integrada ao processo de entrega.

### 3. [Gestão de Ciclo de Vida](lifecycle_management.md)
A engine é inteligente o suficiente para detectar automaticamente se a execução se dá em um contexto consultivo de **Preview** (disparado por Pull Requests) ou em um contexto definitivo de **Deploy** (disparado pelo Merge em Main), liberando os desenvolvedores de tomarem decisões ou rodarem comandos manuais complexos.

### 4. [Operações Serverless](serverless_native_iac_engine.md)
A arquitetura funciona de forma 100% efémera, sob demanda e serverless. Com a remoção do DynamoDB para state locking — substituído pelo **S3 Native Locking** do Terraform 1.10+ / OpenTofu 1.8+ —, a plataforma reduz a zero o seu custo fixo operacional na nuvem.
