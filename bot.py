import discord
import requests
import re
import os
from bs4 import BeautifulSoup
import sqlite3

class MyClient(discord.Client):
    async def on_ready(self):
        """
        Asynchronous function to prepare database and print status when activated.
        """

        db = sqlite3.connect('history.sqlite')
        cursor = db.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS history(
            user_id TEXT,
            search_phrase TEXT
        )
        ''')
        print('Bot online, logged on as', self.user)

    async def on_message(self, message):
        """
        Asynchronous function to chat with the active user.
        """

        if message.author == self.user:
            return

        # The bot returns 'hey' when the user enters 'hi'.

        if message.content == 'hi':
            await message.channel.send('hey')

        functionality_type = message.content[0:7]
        url_list = []

        # To google users query or search phrase and return top five results provided.
        # It also stores the user's id and the query phrase as search history.
        #  To google via game bot user user has to enter '!google {search_phrase}'
         
        if functionality_type == '!google':
            results = 5
            search = message.content.replace('!google ', '')
            db = sqlite3.connect('history.sqlite')
            cursor = db.cursor()
            sql = ("INSERT INTO history(user_id, search_phrase) VALUES(?,?)")
            val = (message.author.id, search)
            cursor.execute(sql, val)
            db.commit()
            cursor.close()
            db.close()
            page = requests.get(f"https://www.google.com/search?q={search}&num={results+1}")
            soup = BeautifulSoup(page.content)
            links = soup.findAll("a")
            for link in links :
                link_href = link.get('href')
                if "url?q=" in link_href and not "webcache" in link_href:
                    url_list.append(link.get('href').split("?q=")[1].split("&sa=U")[0])
        for url in url_list[0:5]:
            await message.channel.send(url)
        
        # The user can retrive its recent history of a phrase.
        # The history is persistent and stored in sqlite database.
        # This is a partial search implementation.

        if functionality_type == '!recent':
            check_history = message.content.replace('!recent ', '')
            db = sqlite3.connect('history.sqlite')
            cursor = db.cursor()
            cursor.execute(f"SELECT DISTINCT search_phrase FROM history WHERE search_phrase LIKE '%{check_history}%' AND user_id = {message.author.id}")
            result = cursor.fetchall()
            if result == []:
                await message.channel.send("No result found in history :(")
            else:
                for phrase in result:
                    await message.channel.send(phrase[0])

        

client = MyClient()
client.run(os.environ.get('TOKEN'))
