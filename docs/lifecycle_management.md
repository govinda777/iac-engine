# Gestão de Ciclo de Vida: Transparência e Execução Automática

A essência do **iac-engine** baseia-se na **Inversão de Controle do Ciclo de Vida**. Isto significa que o cliente (Spoke) não precisa disparar comandos de execução, instalar binários locais do Terraform/OpenTofu ou decidir manualmente quando rodar um planejamento ou aplicação.

O motor reutilizável do Hub detecta o contexto do evento do Git de forma autônoma e gerencia todo o ciclo de vida IaC do Spoke com integridade e segurança.

---

## 1. Fluxo do Ciclo de Vida Reativo

O ciclo de vida operacional é mapeado diretamente para o processo de desenvolvimento e revisão de código da organização (GitOps), dividindo-se em duas fases claras:

```
                  +-----------------------------------+
                  |   Desenvolvedor propõe alteração  |
                  |     (Criação de Pull Request)     |
                  +-----------------------------------+
                                    |
                                    v
                  +-----------------------------------+
                  |      Fase 1: Preview (Plan)       |
                  |  - Inicializa backend dinâmico    |
                  |  - Roda tofu plan sem alterações  |
                  |  - Comenta resultado no PR        |
                  +-----------------------------------+
                                    |
                  [ Revisão de Código & Aprovação ]
                                    |
                                    v
                  +-----------------------------------+
                  |     Merge do PR na Branch Main     |
                  +-----------------------------------+
                                    |
                                    v
                  +-----------------------------------+
                  |      Fase 2: Deploy (Apply)       |
                  |  - Inicializa backend dinâmico    |
                  |  - Executa tofu apply             |
                  |  - Atualiza estado e lock nativo  |
                  +-----------------------------------+
```

---

## 2. Fase 1: Preview (Pull Request)

Disparado automaticamente quando um Pull Request (PR) é aberto, atualizado ou sincronizado contra a branch principal `main`.

### Comportamento da Engine
1.  **Isolamento de Estado:** A engine lê o metadado `${{ github.repository }}` e inicializa o backend S3 apontando para o arquivo de estado específico daquele repositório cliente.
2.  **Execução Consultiva:** Executa o comando `tofu plan -no-color -out=tfplan` de forma estritamente consultiva. Nenhuma mudança física é executada na AWS.
3.  **Feedback no PR (Visibilidade):** O plano gerado é formatado em um bloco Markdown limpo e amigável e é publicado automaticamente como um comentário na interface do Pull Request. Os desenvolvedores e revisores podem analisar detalhadamente o impacto financeiro e arquitetural da alteração diretamente pelo GitHub, sem precisar acessar o terminal ou consoles em nuvem.

---

## 3. Fase 2: Deploy (Merge em Main)

Disparado estritamente quando um commit é mesclado (*merged*) ou empurrado diretamente para a branch padrão `main`.

### Comportamento da Engine
1.  **Isolamento de Estado:** Inicializa o backend de estado seguro dinamicamente.
2.  **Execução Definitiva:** Executa o comando `tofu apply -auto-approve` para efetivar as mudanças declaradas no código da infraestrutura física da AWS.
3.  **Proteção Concorrente (Locking):** Toda a operação de gravação de estado é protegida pelo **S3 Native Locking** (com `use_lockfile = true`), garantindo que execuções simultâneas ou consecutivas muito próximas não corrompam o estado da aplicação.

---

## 4. Vantagens do Gerenciamento Automático de Ciclo de Vida

*   **Padronização Absoluta:** Todas as equipes e produtos seguem exatamente o mesmo ciclo de qualidade e validação de infraestrutura, eliminando scripts caseiros ou execuções locais parciais.
*   **Tranquilidade e Produtividade:** Os engenheiros de software focam exclusivamente no código de sua infraestrutura. Toda a mecânica de execução, autenticação em nuvem e persistência segura é delegada à plataforma central.
*   **Rastreabilidade Total (Audit Trail):** Como a aplicação final de infraestrutura ocorre unicamente por meio de merges na branch `main` disparados pelo GitHub Actions, há um histórico completo, imutável e auditável de quem, quando e por que cada recurso foi provisionado ou alterado na AWS.
