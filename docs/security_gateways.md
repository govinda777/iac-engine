# Gateways de Segurança: Validação de Conformidade e Governança

O **iac-engine** adota uma filosofia de **Segurança baseada em Gatekeepers (Shift-Left)**. No modelo de Inversão de Controle, o código proposto pelo Spoke não é implantado diretamente sem antes passar por um rigoroso processo de auditoria automatizada em tempo de execução no Hub.

Estes portões de qualidade (Gateways de Segurança) garantem que todas as alterações de infraestrutura sigam as boas práticas corporativas de conformidade e as diretrizes regulatórias globais antes mesmo da aplicação de qualquer plano.

---

## 1. Verificações de Segurança na Pipeline do Hub

O motor central executa nativamente as seguintes etapas de validação e verificação de conformidade na pipeline de análise estática:

```
[ Git Pull / Checkout ]
          |
          v
[ Validação de Sintaxe (Tofu/Terraform Validate) ]
          |
          v
[ Detecção de Segredos Estáticos & Chaves Vazadas ]
          |
          v
[ Análise de Vulnerabilidades em Configurações de Nuvem ]
          |
          v
[ Auditoria de Políticas Organizacionais Customizadas ]
```

### 1.1. Detecção de Segredos Estáticos (Secrets Scanning)
Verifica ativamente se os arquivos de configuração do Spoke contêm chaves estáticas vazadas (`AWS_ACCESS_KEY_ID`, senhas de banco de dados, chaves SSH). Caso sejam detectados segredos, a pipeline falha imediatamente e sinaliza o risco no Pull Request.

### 1.2. Análise de Vulnerabilidades (Static Application Security Testing - SAST)
Utiliza analisadores estáticos da comunidade (como Checkov, TFSec ou Trivy) para varrer arquivos de infraestrutura à procura de configurações inseguras. Exemplos comuns interceptados:
*   Buckets S3 públicos ou sem criptografia ativa em repouso.
*   Grupos de Segurança (Security Groups) com portas sensíveis (ex: SSH `22`, RDP `3389`) expostas globalmente para o mundo (`0.0.0.0/0`).
*   Bancos de dados RDS sem chaves de criptografia KMS ou com persistência de backups desabilitada.

### 1.3. Auditoria de Políticas Customizadas (OPA / Rego)
Aplica políticas organizacionais específicas que garantem a padronização e o controle de custos. Por exemplo:
*   Permitir apenas certos tipos de instâncias EC2 homologadas para ambientes de desenvolvimento (ex: `t3.micro`, `t3.small`).
*   Exigir a presença obrigatória de tags corporativas cruciais (como `Environment`, `Owner`, `ProjectID` e `CostCenter`).

---

## 2. Fortalecimento Global com Resource Control Policies (RCPs)

No lado da nuvem AWS, mesmo que uma identidade federada do Spoke seja de alguma forma comprometida ou obtenha permissões excessivas temporariamente, as **Resource Control Policies (RCPs)** na raiz do AWS Organizations impõem limites rigorosos e intransponíveis:

### 2.1. Perímetro de Dados sobre o Bucket de Estados (S3 State Perimeter)
A RCP global é configurada para garantir que os buckets de estado (`.tfstate`) estejam protegidos contra acessos não autorizados de fora das redes e serviços controlados da organização:
*   **Restrição de Origem de Rede:** Qualquer requisição de leitura ou gravação aos buckets S3 de estados corporativos deve se originar obrigatoriamente de conexões controladas de VPC da corporação ou de IPs efémeros de runners oficiais do GitHub Actions.
*   **Bloqueio de Download Manual Local:** Impede o download ou visualização de ficheiros de estado cruciais por engenheiros e desenvolvedores a partir de suas estações de trabalho locais, bloqueando o acesso direto à console web para download de estados. Isso previne o vazamento de metadados sensíveis e dados criptografados de conexão de recursos.

---

## 3. Validação de Segurança Pré-Envio (Target Local `lint-security`)

Para otimizar o fluxo de trabalho dos desenvolvedores e mitigar falhas tardias em pipelines, disponibilizamos um comando de validação local no `Makefile` da raiz:

```bash
make lint-security
```

Este comando executa scripts de lint automatizados em sua máquina local para verificar o cumprimento dos seguintes critérios mínimos de envio antes do commit:
1.  **Backend Sem Parâmetros (Backend-Less):** O arquivo `backend.tf` deve conter um bloco `terraform { backend "s3" {} }` estritamente vazio. Não é permitido declarar buckets, chaves de estado ou regiões localmente.
2.  **Ausência de Credenciais Estáticas:** Garante que o código proposto não expõe chaves AWS em disco ou em variáveis fixas.
