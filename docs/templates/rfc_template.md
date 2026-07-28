# Template de Request For Comments (RFC)
## RFC-[000]: [Título da Proposta de Mudança de Segurança/Ciclo de Vida]

**Autor(es):** [Seu Nome/Time]
**Data:** AAAA-MM-DD
**Status:** Proposto / Em Discussão / Aprovado / Rejeitado
**Área de Impacto:** Critérios de Segurança / Fluxo do Ciclo de Vida / Integração de Spokes

---

## 1. Sumário Executivo

Uma breve descrição em alto nível da funcionalidade ou mudança de segurança proposta. Qual problema ela resolve no contexto da plataforma centralizada de IaC e qual é o valor agregado para os Spokes?

## 2. Contexto e Motivação

Explique os detalhes do cenário atual e as razões por trás desta mudança:
*   Qual vulnerabilidade de segurança ou limitação de ciclo de vida motivou esta RFC?
*   Quais dados técnicos dão suporte a esta proposta (logs, relatórios de auditoria, solicitações de desenvolvedores)?

## 3. Desenho Técnico Proposto

Forneça um detalhamento profundo sobre a implementação técnica da mudança.

### 3.1. Arquitetura Lógica
Se aplicável, adicione diagramas (ex: diagramas Mermaid) ou fluxogramas detalhando o novo gateway de segurança ou comportamento do ciclo de vida.

### 3.2. Mudanças no Motor do Hub (`iac-engine`)
Quais alterações serão feitas no workflow reutilizável, em scripts em memória (`GIT_ASKPASS`, etc) ou em validadores estáticos?
*   Alterações de arquivos:
*   Novas entradas/saídas do workflow:

### 3.3. Impacto nos Spokes Clientes
Descreva o que muda para as equipes clientes. Haverá necessidade de migração, alteração de parâmetros ou nova configuração de Trust Policy na AWS?

## 4. Implicações de Segurança e Governança

Esta seção deve detalhar estritamente como a proposta afeta as garantias de multilocação (*multi-tenancy*) e segurança da informação:
*   Como a mudança impede desvios cruzados entre Spokes?
*   Como as Resource Control Policies (RCPs) ou políticas IAM são afetadas?
*   Quais ferramentas de análise de código estático (SAST/Checkov/OPA) serão usadas para garantir o cumprimento da regra proposta?

## 5. Plano de Rollout e Release Management

Seguindo as diretrizes do nosso gerenciamento de lançamentos:
*   A mudança será introduzida em qual versão (`MAJOR`, `MINOR` ou `PATCH`)?
*   Como será feito o teste de compatibilidade local (sandbox Floci.io)?
*   Haverá um período de testes beta com Spokes "Canary"?

## 6. Alternativas Consideradas

Quais outras abordagens foram cogitadas para resolver o mesmo problema e por que foram descartadas em favor deste desenho proposto?
