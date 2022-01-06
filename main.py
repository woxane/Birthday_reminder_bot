#!/usr/bin/python3

from telethon.sync import TelegramClient , events , Button 
import logging 
import mysql.connector
import config



logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)
client = TelegramClient('data' , config.API_ID , config.API_HASH , proxy = ('socks5' , '127.0.0.1' , 8080))
db = mysql.connector.connect(
        user = config.DB_USERNAME , 
        password = config.DB_PASSWORD , 
        host = config.DB_HOST , 
        database = config.DB_DATABASE ,
        autocommit = True )
cursor = db.cursor() 


@client.on(events.NewMessage(pattern = '/start')) 
async def start(event) : 
    cursor.execute('SELECT user_id FROM Users')
    output = [user_id[0] for user_id in  cursor] #user_id[0] cause the output executed command is like this (1231235,)
    if event.message.chat_id in output :
        await client.send_message(event.chat_id , "You're already started the bot !")
    else :
        cursor.execute(f'INSERT INTO Users (user_id) VALUES({event.message.chat_id})') #if useres started the bot for the first time , we add the user_id to users table 
        await event.reply('Welcome !') 














if __name__ == '__main__' :
    client.start(bot_token = config.TOKEN)
    client.run_until_disconnected()
