# ADR-002: Inversão de Controle do Ciclo de Vida

*   **Status:** Accepted
*   **Autor(es):** Jules (Arquiteto de Soluções)
*   **Data:** 2025-02-17
*   **Decisões Relacionadas:** ADR-001 (Initial Architecture)

---

## 1. Contexto (Context)

No modelo tradicional de entrega de Infraestrutura como Código (IaC), as equipes de desenvolvimento (clientes/Spokes) são responsáveis por definir quando e como o código de infraestrutura é executado. Isso geralmente significa que:
1.  Cada Spoke mantém seus próprios scripts complexos e pipelines no GitHub Actions.
2.  Desenvolvedores decidem manualmente através de comandos de terminal, botões ou flags quando rodar o planejamento (`plan`) e a aplicação (`apply`).
3.  Esta fragmentação aumenta drasticamente a chance de erros humanos, além de dificultar o enforcement centralizado de regras de segurança e conformidade organizacional, deixando o estado (`terraform.tfstate`) exposto a concorrências e desvios descontrolados.

Para centralizar e padronizar o processo, precisamos decidir quem assume o controle do fluxo operacional de ciclo de vida da infraestrutura corporativa.

---

## 2. Decisão (Decision)

Adotamos a **Inversão de Controle do Ciclo de Vida**. Sob este modelo arquitetural:
1.  **A Engine Central (Hub) assume a inteira responsabilidade** de gerenciar, monitorar e acionar o ciclo de vida IaC do cliente de forma autônoma.
2.  **O cliente (Spoke) perde a capacidade de disparar comandos IaC manuais**. O fluxo de ciclo de vida é disparado de forma reativa e estritamente atrelado aos eventos e contextos de estado do GitHub (Git Events):
    *   **Contexto de Preview (Fase de Planejamento):** Interceptado automaticamente em eventos de `pull_request`. A engine executa um `tofu plan` puramente analítico e publica o resultado em markdown no PR.
    *   **Contexto de Deploy (Fase de Aplicação):** Interceptado automaticamente no evento `push` ou `merge` direto na branch padrão (`main`). A engine realiza o `tofu apply -auto-approve` físico e atualiza o estado com trava de gravação nativa.
3.  A injeção do backend de persistência e das permissões de nuvem temporárias (OIDC JWT) ocorre dinamicamente em memória no Hub Actions Runner efémero, blindando o Spoke contra erros manuais ou configurações locais incorretas.

---

## 3. Justificativa (Justification)

A Inversão de Controle traz benefícios indiscutíveis de governança e estabilidade para a plataforma:

*   **Segurança e Guardrails Automáticos:** Como a engine gerencia a execução, ela consegue forçar a passagem obrigatória de Gateways de Segurança (Static Application Security Testing - SAST, lint-security, e validações OPA) *antes* de rodar comandos de alteração física na nuvem.
*   **Simplificação de Onboarding:** Reduz o arquivo de workflow do Spoke a uma chamada simples e parametrizada do workflow reutilizável, eliminando toda a sobrecarga técnica e de manutenção por parte das equipes de produto.
*   **Rastreabilidade Imutável:** Todas as alterações físicas de infraestrutura em produção passam a ter um histórico imutável ligado de forma unívoca a um merge de Pull Request aprovado e documentado na branch `main`.
*   **Proteção de Persistência:** A engine gerencia o concorrência de escrita usando **S3 Native Locking**, eliminando dores de cabeça do cliente com arquivos de estado corrompidos.

---

## 4. Consequências (Consequences)

### Positivas
*   **Eliminação de Erros Manuais:** Desenvolvedores não podem errar ou esquecer parâmetros de backend na inicialização, pois eles são injetados automaticamente a partir do contexto do repositório (`github.repository`).
*   **Auditoria Centralizada de Pipeline:** Alterações no motor do pipeline (como a adição de uma nova regra de conformidade global) são aplicadas no Hub e herdadas instantaneamente por todos os Spokes clientes, sem necessidade de enviar Pull Requests para dezenas de repositórios individuais.
*   **Experiência de Desenvolvedor Unificada (DX):** O feedback do plano de infraestrutura é entregue de forma polida diretamente no corpo do Pull Request, simplificando as revisões de código de infraestrutura.

### Negativas / Trade-offs
*   **Perda de Flexibilidade:** Projetos individuais que precisavam de loops e rotinas de ciclo de vida atípicos ou fora do padrão (ex: aprovações de deploy fora da branch main) devem se adaptar ao modelo organizacional restrito, dependendo de aprovações formais de exceção pela equipe de Plataforma.
*   **Dependência da Disponibilidade do GitHub:** O ciclo de vida depende estritamente do disparo estável de webhooks de eventos do GitHub Actions. Interrupções na plataforma do GitHub travam a execução e aplicação de infraestruturas físicas na AWS.
