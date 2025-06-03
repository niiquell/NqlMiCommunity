# DesbloqueioXiaomi

Script Python para automação de solicitações de desbloqueio de bootloader em dispositivos Xiaomi. O script suporta até 5 contas e aguarda o horário de pico (23:57 CST, equivalente a 12:57 BRT) para maximizar as chances de sucesso.

## Funcionalidades
- Suporte para até 5 contas Xiaomi, com gerenciamento via menu interativo.
- Adição, remoção e listagem de contas.
- Autenticação segura na conta Xiaomi.
- Verificação do status da conta (nível, pontos, dias registrados).
- Solicitação automática de desbloqueio no horário de reset da cota diária (23:57 CST, 12:57 BRT).
- Sincronização de tempo com servidores NTP para precisão.
- Interface em português brasileiro com mensagens claras.

## Requisitos
- **Sistema**: Android com Termux instalado ou qualquer sistema com Python 3.6+.
- **Conta Xiaomi**:
  - Deve estar registrada há pelo menos 30 dias.
  - E-mail associado para verificação de código, se necessário.
- **Internet**: Conexão wi-fi estável.
- **Permissões no Termux**: Dar acesso a todas permissões no app do termux.

## Passo a Passo para Uso
1. **Instalar o Termux** (se usar Android):
   - Baixe o Termux do [F-Droid](https://f-droid.org) ou [GitHub](https://github.com/termux/termux-app).
   - Atualize os pacotes: `pkg update && pkg upgrade`.
   - Instale o Python: `pkg install python3`.

2. **Baixar o Script**:
   - No Termux, execute:
     ```bash
     curl -sSL https://github.com/seu_usuario/DesbloqueioXiaomi/raw/main/desbloqueio_xiaomi.py -o "$PREFIX/bin/minql" && chmod +x "$PREFIX/bin/minql"
     ```

3. **Executar o Script**:
   - Digite ```minql``` no Termux.

4. **Acompanhar**:
   - O script exibe informações da conta (dias registrados, nível, pontos).
   - Ele tentará a solicitação automaticamente para cada conta no horário de pico até obter sucesso ou encontrar um erro definitivo.

## Riscos
- **Segurança**:
  - O arquivo `dados_contas.json` armazena tokens de até 5 contas. Não Compartilhe o arquivo e Proteja seu dispositivo contra acesso não autorizado.
  - O uso de bots ou scripts automáticos pode ser contra as regras da Xiaomi.

## Créditos
- @Offici5l - Criador do script de inspiração que foi usado como base para o NqlMiCommunity.
