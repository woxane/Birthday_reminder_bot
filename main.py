#!/usr/bin/python3

from telethon.sync import TelegramClient , events , Button 
import logging 
import mysql.connector
import config
from datetime import datetime


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



#using old school version for finding where the user is . 
Giving_Name = 0 
Giving_Birthday = 0


def is_valid(Birthday) :
    Year , Month , Day = Birthday.split('/') 
    try :
        return datetime(int(Year) , int(Month) , int(Day))
    except :
        return False 

@client.on(events.NewMessage(pattern = '/start')) 
async def Start(event) :  
    markup = event.client.build_reply_markup([
        [Button.text('Add Birthday date .')]])

    cursor.execute('SELECT user_id FROM Users')
    output = [user_id[0] for user_id in  cursor] #user_id[0] cause the output executed command is like this (1231235,)
    if event.message.chat_id in output :
        await event.respond("You're already started the bot !" , buttons = markup)
    else :
        cursor.execute(f'INSERT INTO Users (user_id) VALUES(%s)' , (event.message.chat_id)) #if useres started the bot for the first time , we add the user_id to users table 
        await event.respond('Welcome !' , buttons = markup) 

@client.on(events.NewMessage(pattern = r'[^/start]'))
async def Check(event) :
    global Giving_Name , Giving_Birthday , name
    if event.raw_text == 'Add Birthday date .' :
        Giving_Name = 1 
        await client.send_message(event.chat_id , 'What is name to be saved ?') 
    
    elif Giving_Name == 1 :
        if event.raw_text.isalpha() :
            Giving_Birthday = 1
            Giving_Name = 0 
            name = event.raw_text
            await client.send_message(event.chat_id , 'birtday (format : {Y/M/D} , example : 2001/8/7) :')

        else :
            await client.send_message(event.chat_id , 'this name is invalid !\n back to main menu .') 
            Giving_Name = 0

    
    elif Giving_Birthday == 1 :
        if Bd := is_valid(event.raw_text) :
            await client.send_message(event.chat_id , f'done ! {name} : {Bd.strftime("%Y/%m/%d")}') 
            cursor.execute('INSERT INTO Data (User_id , name , birthday ) VALUES (%s , %s , %s)' , (event.message.chat_id , name , Bd))

        else :
            await client.send_message(event.chat_id , 'The birthday is invalid , Please type like this format : {Y/M/D}\n for example : 2001/8/7')

    else : 
        await client.send_message(event.chat_id , 'Please use the menu !')




if __name__ == '__main__' :
    client.start(bot_token = config.TOKEN)
    client.run_until_disconnected()
