# ADR 0002: Adoção do Paradigma de Engine Agnóstica com Validação de Backend e OIDC Keyless

*   **Status:** Aceito
*   **Autor(es):** Jules (Arquiteto de Soluções)
*   **Data:** 2025-02-17
*   **Decisões Relacionadas:** ADR-001 (Initial Architecture), ADR-002 (Inversion of Control Lifecycle)

---

## 1. Contexto (Context)

Necessidade de simplificar o `iac-engine`, eliminar pontos de acoplamento excessivo e evitar a introdução de frameworks de orquestração complexos (ex: Terragrunt/Atmos) na camada de plataforma, mantendo custo zero e baixa curva de aprendizado. No modelo anterior, a Engine forçava a injeção do estado usando argumentos parciais do backend (`-backend-config`), o que criava uma forte dependência e acoplamento entre a Engine e a configuração exata da stack, diminuindo a autonomia dos times (stacks).

## 2. Decisão (Decision)

1. A Stack gerencia a declaração do seu backend S3 (usando `use_lockfile = true` nativo).
2. A Engine valida os requisitos de segurança e compliance do backend antes da execução, não injetando mais de forma implícita.
3. A autenticação é 100% baseada em OIDC Keyless com escopo por repositório/diretório.
4. Módulos HCL compostos e versionados via Git são o padrão primário para reuso de arquitetura.

## 3. Justificativa (Justification)

A adoção deste modelo descentraliza a persistência, transferindo a propriedade e gerência da estrutura do projeto para a Stack, mantendo a Engine como guardiã de segurança (gatekeeper) de maneira agnóstica ao invés de um injetor mandatório. Isso facilita o suporte a variados layouts de diretórios, frameworks e orquestrações locais, exigindo apenas que respeitem os contratos de segurança estipulados e validados pelo CI/CD.

## 4. Consequências (Consequences)

### Positivas
*   Custo zero de infraestrutura de controle/gerenciamento (Zero-Ops).
*   Flexibilidade para as stacks evoluírem ou escolherem frameworks sem depender da alteração da Engine.
*   Eliminação de chaves estáticas de credencial AWS, aumentando a segurança.
*   Baixa manutenção e facilidade no onboarding de novos times.

### Negativas / Trade-offs
*   Exige que cada stack declare seu backend S3 conforme a convenção estipulada (mitigado pelas etapas de validação automática da Engine na pipeline).
