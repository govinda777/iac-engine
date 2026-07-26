# Onboarding de Autenticação: OIDC e IAM Trust Policies

O **iac-engine** adota um modelo de segurança robusto baseado em **federação de identidade e autenticação keyless**. Para que a nossa engine centralizada gerencie a infraestrutura de um repositório cliente (Spoke), o Spoke precisa autorizar a engine a agir em seu nome de forma segura.

---

## 1. O Modelo OpenID Connect (OIDC) Keyless

Eliminamos de forma absoluta o uso de credenciais da nuvem estáticas (AWS Access Key e Secret Access Key) salvas como Secrets no GitHub. Em vez disso, utilizamos o fluxo OIDC nativo do GitHub Actions para assumir papéis temporários na AWS.

O fluxo de autenticação baseia-se na confiança criptográfica e possui validade curta por execução (em média 15 minutos):

```
+-------------------+             1. Requisita JWT             +-----------------------+
|  Runner Efémero   | ---------------------------------------> |  GitHub Actions OIDC  |
|  do GitHub (Hub)  | <--------------------------------------- |      IdP Server       |
+-------------------+             2. Retorna JWT               +-----------------------+
          |
          | 3. AssumeRoleWithWebIdentity(JWT, RoleARN)
          v
+-------------------+
|  AWS STS Service  |
+-------------------+
          |
          | 4. Valida assinatura do JWT e confirma as condições (sub claim)
          v
+-------------------+             5. Devolve credenciais temporárias (STS Token)
|  Runner Efémero   | <---------------------------------------
+-------------------+
```

---

## 2. Como Configurar o OIDC na AWS (Onboarding)

Para registrar o GitHub como um provedor de identidade (IdP) na conta AWS de destino, configure um **Identity Provider** com as seguintes especificações:

*   **Provider URL:** `https://token.actions.githubusercontent.com`
*   **Audience (Client ID):** `sts.amazonaws.com`

---

## 3. Configurando as IAM Roles com Trust Policies Estritas

O principal risco em uma arquitetura Hub-and-Spoke de multilocação (*multi-tenancy*) é o "Acesso Cruzado", onde um Spoke malicioso ou comprometido tenta executar ações ou ler o estado de outro Spoke.

Para mitigar isso, as IAM Roles criadas em cada conta de destino AWS devem conter uma **Trust Policy (Política de Confiança)** extremamente restrita, condicionada ao *Subject Claim* (`sub`) enviado pelo GitHub Actions.

### Exemplo de Trust Policy para o Spoke `spoke-app-a`

Cada papel IAM criado deve especificar e validar estritamente qual repositório e branch estão autorizados a assumir as credenciais:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::123456789012:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        },
        "StringLike": {
          "token.actions.githubusercontent.com:sub": [
            "repo:govinda777/spoke-app-a:ref:refs/heads/main",
            "repo:govinda777/spoke-app-a:pull_request"
          ]
        }
      }
    }
  ]
}
```

### Análise de Segurança dos Atributos
*   `token.actions.githubusercontent.com:aud`: Garante que o token foi emitido especificamente para o público oficial do AWS STS (`sts.amazonaws.com`).
*   `token.actions.githubusercontent.com:sub`: É o identificador único do gatilho do evento. Ao amarrar ao repositório `govinda777/spoke-app-a` e ramificações como `refs/heads/main` ou o evento `pull_request`, garantimos isolamento absoluto. Se o repositório `spoke-app-b` tentar passar a Role ARN do `spoke-app-a` em suas variáveis de pipeline, a AWS rejeitará a chamada de imediato.

---

## 4. Práticas Recomendadas de Menor Privilégio (IAM Least Privilege)

Ao configurar as políticas de acesso associadas à Role federada, lembre-se de restringir ao escopo estrito das necessidades de infraestrutura daquela aplicação:
1.  **Permissões de Estado (S3):** Conceda acesso de leitura e escrita somente sob o prefixo correspondente àquela aplicação dentro do bucket central (ex: `arn:aws:s3:::govinda777-iac-states-prod/clientes/govinda777/spoke-app-a/*`).
2.  **Operações em Recursos AWS:** Restrinja quais serviços e famílias de recursos aquela aplicação pode provisionar (por exemplo, permitindo instâncias EC2, S3 e RDS, mas bloqueando edições em recursos globais de rede corporativa).
