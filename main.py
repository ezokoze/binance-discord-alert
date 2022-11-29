import requests
import json
from discord_webhook import DiscordWebhook, DiscordEmbed
import time
import threading
import discord
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem


def main(uid, username):

    with open('config.json', 'r') as f:
        config = json.load(f)
    webhookurl = config['webhook']
    s = requests.Session()
    data2 = {
        "encryptedUid": uid
    }

    r = s.post('https://www.binance.com/bapi/futures/v2/public/future/leaderboard/getOtherLeaderboardBaseInfo',
               json=data2)
    dats2 = json.loads(r.text)
    last_trade = {}
    while True:
        try:
            software_names = [SoftwareName.CHROME.value]
            operating_systems = [
                OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value]

            user_agent_rotator = UserAgent(
                software_names=software_names, operating_systems=operating_systems, limit=100)
            useragent = user_agent_rotator.get_random_user_agent()
            headers = {
                'User-Agent': useragent,
                "Accept-Encoding": "*",
                "Connection": "keep-alive"
            }

            data = {
                "encryptedUid": uid,
                "tradeType": "PERPETUAL"
            }

            r = requests.post("https://www.binance.com/bapi/futures/v1/public/future/leaderboard/getOtherPosition",
                              json=data, headers=headers)

            dats = json.loads(r.text)

            alltradeactive = []
            for trade in dats['data']['otherPositionRetList']:
                alltradeactive.append(str(trade['updateTimeStamp']))
                if str(trade['updateTimeStamp']) not in last_trade.keys():
                    currency = trade['symbol']
                    user = username
                    img = dats2['data']['userPhotoUrl']
                    marketprice = trade['markPrice']
                    if '-' in str(trade['amount']):
                        longorshot = "Vente 🔴"
                    else:
                        longorshot = "Achat 🟢"
                    levier = trade['leverage']
                    taille = str(trade['amount'])
                    entry = "$" + str(trade['entryPrice'])
                    times = time.time()
                    embed = DiscordEmbed(
                        title="📊 Nouvelle position ouverte sur $" + currency, color=0x32CD32)
                    embed.description = "***Version: *** ``0.0.1``\n\n"
                    embed.set_thumbnail(
                        url="https://logodownload.org/wp-content/uploads/2021/03/binance-logo-0-2048x2048.png")
                    embed.set_author(name=user, icon_url=img)
                    embed.add_embed_field(
                        name="Prix d'entrée:", value=f"> {entry}", inline=False)
                    embed.add_embed_field(
                        name="Prix du marché:", value="> $" + str(marketprice), inline=False)
                    embed.add_embed_field(
                        name="Long ou Short:", value="> " + longorshot, inline=False)
                    embed.add_embed_field(
                        name="Taille:", value="> " + str(taille), inline=False)
                    embed.add_embed_field(
                        name="Levier", value="> x" + str(levier), inline=False)
                    embed.set_footer(text="Binance Futures by f1tch",
                                     icon_url="https://logodownload.org/wp-content/uploads/2021/03/binance-logo-0-2048x2048.png")
                    embed.set_timestamp()

                    webhook = DiscordWebhook(
                        url=webhookurl, username="Binance Tracker", avatar_url=img, rate_limit_retry=True)
                    webhook.add_embed(embed)
                    response = webhook.execute()
                    end = time.time() - times

                    last_trade[str(trade['updateTimeStamp'])] = {'user': user, 'currency': currency, 'img': img, 'longorshot': longorshot,
                                                                 'amount': trade["amount"], 'entry': entry, 'levier': levier, 'marketprice': marketprice}
                    print("New trade detected + Time to send: " +
                          str(round(end*1000)) + "ms")

            listtradetodelete = []
            for traded in last_trade.keys():
                if traded not in alltradeactive:
                    print('traded', traded)
                    data = last_trade[traded]
                    user = username
                    img = dats2['data']['userPhotoUrl']
                    currency = data['currency']
                    listtradetodelete.append(traded)
                    print('data', data)

                    embed = DiscordEmbed(
                        title='Position fermée sur $' + currency, color=0xFF0000)

                    embed.set_thumbnail(
                        url="https://logodownload.org/wp-content/uploads/2021/03/binance-logo-0-2048x2048.png")

                    embed.description = "***Version: *** ``0.0.1``\n\n"

                    embed.set_author(name=user, icon_url=img)

                    embed.add_embed_field(
                        name="Market price:", value=f"> {str(data['marketprice'])}", inline=False)

                    embed.add_embed_field(
                        name="Long ou Short:", value="> " + data['longorshot'], inline=False)

                    embed.add_embed_field(
                        name="Taille:", value="> " + str(data['amount']), inline=False)

                    embed.add_embed_field(
                        name="Levier", value="> x" + str(data['levier']), inline=False)

                    embed.set_footer(text="Binance Futures by f1tch",
                                     icon_url="https://logodownload.org/wp-content/uploads/2021/03/binance-logo-0-2048x2048.png")

                    embeds.set_timestamp()

                    webhooks = DiscordWebhook(
                        url=webhookurl, username="Binance Tracker", avatar_url=data['img'], rate_limit_retry=True)

                    webhooks.add_embed(embed)
                    response = webhooks.execute()

            for i in listtradetodelete:
                del last_trade[i]

            time.sleep(3)
        except Exception as e:
            print(e)
            time.sleep(3)
            pass


if __name__ == "__main__":
    f = open('profiles.json')
    profiles = json.load(f)

    for p in profiles:
        threading.Thread(target=main, args=(p['uid'], p['username'])).start()
