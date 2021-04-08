"""
Endpoint API Query per controllare i valori del modem 4G TIM

Resources: https://discord.com/developers/docs/resources/webhook

Compilare file di configurazione generato all'avvio.

Uso: python3 saponetto.py -setMin 50 -setInt 5

setMin -> Imposta percentuale batteria per entrare in zona critica!

SetInt -> Imposta intervallo di controllo, espresso in minuti!

"""

import os
import sys
import time
from time import gmtime, strftime
import datetime
import argparse
import json
import random
import requests
from discordwebhook import Discord


class SAPONETTO:

    @staticmethod
    def getConfig():
        try:
            if not os.path.exists("config"):
                with open("config", "w") as config:
                    print('discord_webhook = <url>', file=config)
                    print('dashboard_password = <password>', file=config)
                    print('wifi_credentials = <password-wifi>', file=config)
                    print('SIM_PIN = <PIN>', file=config)
                    print('SIM_PUK = <PUK>', file=config)
                    print('File di configurazione <config> creato,\nriempilo con i tuoi dati\ne riavvia lo script !')
                    sys.exit(1)
            
            dConfig = {}
            with open("config" , "r") as config_file:
                for line in config_file:
                    (key,value) = line.rstrip("\n").split(" = ")
                    dConfig[str(key)] = value
                return dConfig
        except Exception as e:
            print('Errore: ', e)
            sys.exit(-2)

    @staticmethod
    def postRequest():
        try:
            endpoint = 'http://192.168.1.1/jrd/webapi?api=GetSystemStatus'
            body = {"jsonrpc": "2.0",
            "method" : "GetSystemStatus",
            "params" : "null",
            "id" : "13.4"}

            post_request = requests.post(endpoint, json = body)
            json_request = post_request.json()
            json_result = json_request['result']
            json_battery = json_result['bat_cap']
            json_totalConnNum = json_result['TotalConnNum']

            return json_battery, json_totalConnNum


        except Exception as e:
            print('Errore: ', e)
            sys.exit(-2)
    
    @staticmethod
    def webHook(data_battery, data_totalConnNum, setMin, config):
        if int(data_battery) < int(setMin):
            discord = Discord(url=f"{config['discord_webhook']}")
            discord.post(
            embeds=[{"title": "ALLARME BATTERIA - SOGLIA CRITICA", "description": f"```diff\n-> Allarme - Batteria al {data_battery}% - {strftime('%H:%M:%S', gmtime())}\n```"}],
            )
        try:
            discord = Discord(url=f"{config['discord_webhook']}")
            discord.post(
            avatar_url="https://www.naturplus.it/3625-tm_thickbox_default/saponetta-al-muschio-bianco-detersione-delicata.jpg",
            embeds=[
            {
                "author": {
                    "name": "Saponetta TIM - Università",
                    "url": "http://192.168.1.1/index.html",
                    "icon_url": "https://pbs.twimg.com/profile_images/687250413788106753/Of-4AHDY_400x400.png",
                },
                "title": "Saponetta chiama, Saponetto risponde.. qui stats e creds ",
                "description": "",
                "fields": [
                    {"name": "Batteria", "value": f"**{data_battery}%**"},
                    {"name": "Dispositivi Connessi", "value": f"**{data_totalConnNum}**"},
                    {"name": "Credenziali Dashboard", "value": f"|| {config['dashboard_password']} ||", "inline": True},
                    {"name": "Credenziali Wi-Fi", "value": f"|| {config['wifi_credentials']} ||", "inline": True},
                    {"name": "PIN SIM", "value": f"|| {config['SIM_PIN']} ||", "inline": True},
                    {"name": "PUK SIM", "value": f"|| {config['SIM_PUK']} ||", "inline": True},
                    {"name": "Amore per te", "value": f"{random.randint(0,100)}%"}

                ],
                "footer": {
                    "text": "Powered By Donato Di Pasquale",
                    "icon_url": "https://pbs.twimg.com/profile_images/687250413788106753/Of-4AHDY_400x400.png",
                },
            }
            ],
            )     
        except Exception as e:
            print('Errore: ', e)
            sys.exit(-2)
    
if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='MONITORING MODEM - Crea il tuo WebHook su Discord, riempi il file di configurazione ed avvia lo script!')
    parser.add_argument(
    '-setMin',
    help = 'Imposta percentuale batteria per entrare in zona critica! -> -setMin 30',
    required=True
    )
    parser.add_argument(
    '-setInt',
    help = 'Imposta intervallo di controllo, espresso in minuti -> -setInt 5',
    required=True
    )
    parser.add_argument(
    '-mode',
    help = 'COMING SOON...',
    required=False
    )

    args = parser.parse_args()

    config_file = SAPONETTO.getConfig()

    while True:
        if datetime.datetime.now().minute % int(args.setInt) == 0: 
            battery, connect = SAPONETTO.postRequest()
            SAPONETTO.webHook(battery,connect,args.setMin, config_file)
        time.sleep(60)