#!/usr/bin/python

versionCode = '500418'
versionName = '5.4.18'

import os
import importlib

while True:
    for lib in ['requests', 'ntplib']:
        try:
            importlib.import_module(lib)
        except ModuleNotFoundError:
            os.system(f'pip install {lib}')
            break
    else:
        break

import requests, json, hashlib, urllib.parse, time, sys, os, base64, ntplib
from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qs, urlparse, quote

version = "1.0.3"

print(f"\n[Versão {version}] Script para solicitação de desbloqueio de dispositivos Xiaomi.\n")

User = "okhttp/4.12.0"
headers = {"User-Agent": User}

def login():
    base_url = "https://account.xiaomi.com"
    sid = "18n_bbs_global"

    user = input('\nDigite o usuário: ')
    pwd = input('\nDigite a senha: ')
    hash_pwd = hashlib.md5(pwd.encode()).hexdigest().upper()
    cookies = {}

    def parse(res): return json.loads(res.text[11:])

    r = requests.get(f"{base_url}/pass/serviceLogin", params={'sid': sid, '_json': True}, headers=headers, cookies=cookies)
    cookies.update(r.cookies.get_dict())

    deviceId = cookies["deviceId"]

    data = {k: v[0] for k, v in parse_qs(urlparse(parse(r)['location']).query).items()}
    data.update({'user': user, 'hash': hash_pwd})

    r = requests.post(f"{base_url}/pass/serviceLoginAuth2", data=data, headers=headers, cookies=cookies)
    cookies.update(r.cookies.get_dict())
    res = parse(r)

    if res["code"] == 70016:
        print("Usuário ou senha inválidos")
        return None
    if 'notificationUrl' in res:
        url = res['notificationUrl']
        if any(x in url for x in ['callback','SetEmail','BindAppealOrSafePhone']):
            print(f"Erro na autenticação: {url}")
            return None

        cookies.update({"NativeUserAgent": base64.b64encode(User.encode()).decode()})
        params = parse_qs(urlparse(url).query)
        cookies.update(requests.get(f"{base_url}/identity/list", params=params, headers=headers, cookies=cookies).cookies.get_dict())

        email = parse(requests.get(f"{base_url}/identity/auth/verifyEmail", params={'_json': True}, cookies=cookies, headers=headers))['maskedEmail']
        quota = parse(requests.post(f"{base_url}/identity/pass/sms/userQuota", data={'addressType': 'EM', 'contentType': 160040}, cookies=cookies, headers=headers))['info']
        print(f"Autenticação da conta\nE-mail: {email}, Tentativas restantes: {quota}")
        input("\nPressione Enter para enviar o código de verificação")

        code_res = parse(requests.post(f"{base_url}/identity/auth/sendEmailTicket", cookies=cookies, headers=headers))

        if code_res["code"] == 0:
            print(f"\nCódigo de verificação enviado para {email}")
        elif code_res["code"] == 70022:
            print("Muitos códigos enviados. Tente novamente amanhã.")
            return None
        else:
            print(f"Erro ao enviar código: {code_res}")
            return None

        while True:
            ticket = input("Digite o código: ").strip()
            v_res = parse(requests.post(f"{base_url}/identity/auth/verifyEmail", data={'ticket':ticket, 'trust':True}, cookies=cookies, headers=headers))
            if v_res["code"] == 70014:
                print("Código de verificação inválido")
            elif v_res["code"] == 0:
                cookies.update(requests.get(v_res['location'], headers=headers, cookies=cookies).history[1].cookies.get_dict())
                cookies.pop("pass_ua", None)
                break
            else:
                print(f"Erro na verificação: {v_res}")
                return None

        r = requests.get(f"{base_url}/pass/serviceLogin", params={'_json': "true", 'sid': sid}, cookies=cookies, headers=headers)
        res = parse(r)

    region = json.loads(requests.get(f"https://account.xiaomi.com/pass/user/login/region", headers=headers, cookies=cookies).text[11:])["data"]["region"]    

    nonce, ssecurity = res['nonce'], res['ssecurity']
    res['location'] += f"&clientSign={quote(base64.b64encode(hashlib.sha1(f'nonce={nonce}&{ssecurity}'.encode()).digest()))}"
    serviceToken = requests.get(res['location'], headers=headers, cookies=cookies).cookies.get_dict()

    dados_conta = {"userId": res['userId'], "new_bbs_serviceToken": serviceToken["new_bbs_serviceToken"], "region": region, "deviceId": deviceId}
    return dados_conta

def load_accounts():
    try:
        with open('dados_contas.json') as f:
            accounts = json.load(f)
        return [acc for acc in accounts if all(acc.get(k) for k in ("userId", "new_bbs_serviceToken", "region", "deviceId"))]
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_accounts(accounts):
    with open('dados_contas.json', 'w') as f:
        json.dump(accounts, f)

def add_account():
    accounts = load_accounts()
    if len(accounts) >= 5:
        print("Limite de 5 contas atingido. Remova uma conta para adicionar outra.")
        return
    print("\nAdicionando nova conta:")
    dados_conta = login()
    if dados_conta:
        accounts.append(dados_conta)
        save_accounts(accounts)
        print(f"Conta {dados_conta['userId']} adicionada com sucesso.")
    else:
        print("Falha ao adicionar conta.")

def remove_account():
    accounts = load_accounts()
    if not accounts:
        print("Nenhuma conta registrada.")
        return
    print("\nContas registradas:")
    for i, acc in enumerate(accounts, 1):
        print(f"{i}. ID: {acc['userId']}, Região: {acc['region']}")
    try:
        index = int(input("Digite o número da conta a remover (ou 0 para cancelar): ")) - 1
        if index == -1:
            return
        if 0 <= index < len(accounts):
            removed = accounts.pop(index)
            save_accounts(accounts)
            print(f"Conta {removed['userId']} removida com sucesso.")
        else:
            print("Número inválido.")
    except ValueError:
        print("Entrada inválida. Use um número.")

def list_accounts():
    accounts = load_accounts()
    if not accounts:
        print("Nenhuma conta registrada.")
        return
    print("\nContas registradas:")
    for i, acc in enumerate(accounts, 1):
        print(f"{i}. ID: {acc['userId']}, Região: {acc['region']}")

def get_account_info(dados_conta):
    headers = {
        'User-Agent': User,
        'Accept-Encoding': "gzip",
        'Content-Type': "application/json",
        'content-type': "application/json; charset=utf-8",
        'Cookie': f"new_bbs_serviceToken={dados_conta['new_bbs_serviceToken']};versionCode={versionCode};versionName={versionName};deviceId={dados_conta['deviceId']};"
    }
    api = "https://sgp-api.buy.mi.com/bbs/api/global/"
    U_info = api + "user/data"
    try:
        info = requests.get(U_info, headers=headers).json()['data']
        print(f"\n[INFORMAÇÕES - Conta {dados_conta['userId']}]:")
        print(f"{info['registered_day']} dias na comunidade")
        print(f"Nível {info['level_info']['level']} {info['level_info']['level_title']}")
        print(f"Faltam {info['level_info']['max_value'] - info['level_info']['current_value']} pontos para o próximo nível")
        print(f"Pontos: {info['level_info']['current_value']}")
        return True
    except Exception as e:
        print(f"Erro ao obter informações da conta {dados_conta['userId']}: {e}")
        return False

def state_request(dados_conta):
    headers = {
        'User-Agent': User,
        'Accept-Encoding': "gzip",
        'Content-Type': "application/json",
        'content-type': "application/json; charset=utf-8",
        'Cookie': f"new_bbs_serviceToken={dados_conta['new_bbs_serviceToken']};versionCode={versionCode};versionName={versionName};deviceId={dados_conta['deviceId']};"
    }
    api = "https://sgp-api.buy.mi.com/bbs/api/global/"
    U_state = api + "user/bl-switch/state"
    print(f"\n[ESTADO - Conta {dados_conta['userId']}]:")
    try:
        state = requests.get(U_state, headers=headers).json().get("data", {})
        is_ = state.get("is_pass")
        button_ = state.get("button_state")
        deadline_ = state.get("deadline_format", "")
        if is_ == 1:
            print(f"Permissão de desbloqueio concedida até {deadline_} (horário de Pequim, mm/dd/aaaa)")
            return True
        msg = {
            1: "Solicitar desbloqueio",
            2: f"Erro na conta. Tente novamente após {deadline_} (mm/dd)",
            3: "A conta precisa estar registrada por mais de 30 dias"
        }
        print(msg.get(button_, ""))
        if button_ in [2, 3]:
            return True
        return False
    except Exception as e:
        print(f"Erro ao verificar estado: {e}")
        return False

def apply_request(dados_conta):
    headers = {
        'User-Agent': User,
        'Accept-Encoding': "gzip",
        'Content-Type': "application/json",
        'content-type': "application/json; charset=utf-8",
        'Cookie': f"new_bbs_serviceToken={dados_conta['new_bbs_serviceToken']};versionCode={versionCode};versionName={versionName};deviceId={dados_conta['deviceId']};"
    }
    api = "https://sgp-api.buy.mi.com/bbs/api/global/"
    U_apply = api + "apply/bl-auth"
    print(f"\n[SOLICITAÇÃO - Conta {dados_conta['userId']}]:")
    try:
        apply = requests.post(U_apply, data=json.dumps({"is_retry": True}), headers=headers)
        print(f"Resposta do servidor em: {apply.headers['Date']}")
        if apply.json().get("code") != 0:
            print(f"Erro na solicitação: {apply.json()}")
            return False
        data_ = apply.json().get("data", {}) or {}
        apply_ = data_.get("apply_result", 0)
        deadline_ = data_.get("deadline_format", "")
        messages = {
            1: "Solicitação bem-sucedida",
            4: f"Erro na conta. Tente novamente após {deadline_} (mm/dd)",
            3: f"Limite de cota atingido. Tente novamente após {deadline_.split()[0]} (mm/dd) {deadline_.split()[1]} (GMT+8)",
            5: "Falha na solicitação. Tente novamente mais tarde",
            6: "Tente novamente em um minuto",
            7: "Tente novamente mais tarde"
        }
        print(messages.get(apply_, ""))
        if apply_ == 1:
            return state_request(dados_conta)
        elif apply_ in [4, 5, 6, 7]:
            return False
        elif apply_ == 3:
            return "quota"
    except Exception as e:
        print(f"Erro na solicitação: {e}")
        return False

def get_ntp_time(servers=["pool.ntp.org", "time.google.com", "time.windows.com"]):
    client = ntplib.NTPClient()
    for server in servers:
        try:
            response = client.request(server, version=3, timeout=5)
            return datetime.fromtimestamp(response.tx_time, timezone.utc)
        except Exception:
            continue
    return datetime.now(timezone.utc)

def get_beijing_time():
    utc_time = get_ntp_time()
    return utc_time.astimezone(timezone(timedelta(hours=8)))

def precise_sleep(target_time, precision=0.01):
    while True:
        diff = (target_time - datetime.now(target_time.tzinfo)).total_seconds()
        if diff <= 0:
            return
        sleep_time = max(min(diff - precision/2, 1), precision)
        time.sleep(sleep_time)

def measure_latency(url, samples=5):
    latencies = []
    for _ in range(samples):
        try:
            start = time.perf_counter()
            requests.post(url, headers=headers, data='{}', timeout=2)
            latencies.append((time.perf_counter() - start) * 1000)
        except Exception:
            continue
    if len(latencies) < 3:
        return 200
    latencies.sort()
    trim = int(len(latencies) * 0.2)
    trimmed = latencies[trim:-trim] if trim else latencies
    return sum(trimmed)/len(trimmed) * 1.3

def schedule_daily_task(accounts):
    beijing_tz = timezone(timedelta(hours=8))
    brasilia_tz = timezone(timedelta(hours=-3))
    api = "https://sgp-api.buy.mi.com/bbs/api/global/"
    U_apply = api + "apply/bl-auth"

    while accounts:
        now = get_beijing_time()
        target = now.replace(hour=23, minute=57, second=0, microsecond=0)
        if now >= target:
            target += timedelta(days=1)

        target_brasilia = target.astimezone(brasilia_tz)
        print(f"\nPróxima execução em: {target.strftime('%Y-%m-%d %H:%M:%S.%f')} CST ({target_brasilia.strftime('%H:%M:%S')} BRT)")
        while datetime.now(beijing_tz) < target:
            time_left = (target - datetime.now(beijing_tz)).total_seconds()
            if time_left > 300:
                time.sleep(60)
            else:
                precise_sleep(target)

        latency = measure_latency(U_apply)
        execution_time = target + timedelta(minutes=3) - timedelta(milliseconds=latency)

        print(f"Horário ajustado para execução: {execution_time.strftime('%H:%M:%S.%f')} CST")
        precise_sleep(execution_time)

        accounts_to_keep = []
        any_quota = False
        for dados_conta in accounts:
            print(f"\nProcessando conta {dados_conta['userId']}...")
            if get_account_info(dados_conta):
                if not state_request(dados_conta):
                    result = apply_request(dados_conta)
                    if result == True:
                        print(f"Conta {dados_conta['userId']} concluiu o desbloqueio com sucesso.")
                        continue
                    elif result == "quota":
                        any_quota = True
                        accounts_to_keep.append(dados_conta)
                    else:
                        accounts_to_keep.append(dados_conta)
                else:
                    continue
            else:
                accounts_to_keep.append(dados_conta)
        accounts = accounts_to_keep
        save_accounts(accounts)
        if not any_quota:
            break
        print("Cota diária atingida para algumas contas. Aguardando próxima janela de solicitação.")

def main_menu():
    accounts = load_accounts()
    while True:
        print("\n=== Menu de Gerenciamento de Contas ===")
        print("1. Adicionar nova conta")
        print("2. Remover conta")
        print("3. Listar contas")
        print("4. Iniciar solicitações de desbloqueio")
        print("5. Sair")
        choice = input("Escolha uma opção (1-5): ").strip()
        
        if choice == '1':
            add_account()
        elif choice == '2':
            remove_account()
        elif choice == '3':
            list_accounts()
        elif choice == '4':
            accounts = load_accounts()
            if not accounts:
                print("Nenhuma conta registrada. Adicione pelo menos uma conta.")
                continue
            print(f"\nIniciando solicitações para {len(accounts)} conta(s)...")
            schedule_daily_task(accounts)
            break
        elif choice == '5':
            print("Saindo...")
            exit()
        else:
            print("Opção inválida. Tente novamente.")

if __name__ == "__main__":
    main_menu()
