# DesbloqueioXiaomi

Script Python para automação de solicitações de desbloqueio de bootloader em dispositivos Xiaomi, utilizando a API oficial da Xiaomi. O script aguarda o horário de pico (23:57 CST, equivalente a 12:57 BRT) para maximizar as chances de sucesso.

## Funcionalidades
- Autenticação segura na conta Xiaomi.
- Verificação do status da conta (nível, pontos, dias registrados).
- Solicitação automática de desbloqueio no horário de reset da cota diária (23:57 CST).
- Sincronização de tempo com servidores NTP para precisão.
- 
## Requisitos
- **Sistema**: Android com Termux instalado ou qualquer sistema com Python 3.6+.
- **Dependências Python**:
  - `requests`: Para requisições HTTP.
  - `ntplib`: Para sincronização de tempo NTP.
  - O script instala essas dependências automaticamente via `pip`.
- **Conta Xiaomi**:
  - Deve estar registrada há pelo menos 30 dias.
  - E-mail associado para verificação de código, se necessário.
- **Internet**: Conexão estável para acessar a API da Xiaomi.
- **Permissões no Termux**: Acesso à internet e armazenamento para salvar `dados_conta.json`.

## Passo a Passo para Uso
1. **Instalar o Termux** (se usar Android):
   - Baixe o Termux do [F-Droid](https://f-droid.org) ou [GitHub](https://github.com/termux/termux-app).
   - Atualize os pacotes: `pkg update && pkg upgrade`.
   - Instale o Python: `pkg install python3`.

2. **Baixar o Script**:
   - No Termux, execute:
     ```bash
     curl -sSL <URL_DO_REPOSITÓRIO>/raw/main/NqlMiCommunity.py -o "$PREFIX/bin/nqlmi" && chmod +x "$PREFIX/bin/nqlmi"
     ```
     
3. **Executar o Script**:
   - Digite `nqlmi` no Termux.
   - Insira seu usuário e senha da conta Xiaomi.
   - Se solicitado, insira o código de verificação enviado ao e-mail.
   - O script aguardará o horário de pico (23:57 CST, 12:57 BRT) para fazer a solicitação.

4. **Acompanhar**:
   - O script exibe informações da conta (dias registrados, nível, pontos).
   - Ele tentará a solicitação automaticamente no horário de pico até obter sucesso ou encontrar um erro definitivo.

## Riscos
- **Segurança**:
  - O script usa hash MD5 para a senha (padrão da API da Xiaomi), que é menos seguro. Use uma senha exclusiva.
  - O arquivo `dados_conta.json` armazena informações sensíveis (como tokens de autenticação). Proteja seu dispositivo contra acesso não autorizado.
- **API da Xiaomi**:
  - Mudanças nos endpoints da API podem quebrar o script.
  - Contas com menos de 30 dias ou que atingiram a cota diária/semanal serão bloqueadas pela API.
- **Uso Indevido**:
  - Desbloquear o bootloader pode violar a garantia do dispositivo. Verifique as políticas da Xiaomi.
  - Uso excessivo pode levar a bloqueios temporários ou permanentes da conta.

## Créditos
@Offici5l pela base e todo o script
@niiquell pela adaptação e tradução do script.

## Licença
Este projeto está licenciado sob a [Licença MIT](LICENSE). Veja o arquivo `LICENSE` para detalhes.
