# 載入需要的模組
from __future__ import unicode_literals
import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
import configparser
from linebot.models import MessageEvent,TextMessage,FlexSendMessage,TextSendMessage,QuickReply,QuickReplyButton,MessageAction

import os
import psycopg2
import requests
import json
#import time
import re

app = Flask(__name__)

# LINE 聊天機器人的基本資料
config = configparser.ConfigParser()
config.read('config.ini')

line_bot_api = LineBotApi(config.get('line-bot', 'channel_access_token'))
handler = WebhookHandler(config.get('line-bot', 'channel_secret'))

#DATABASE_URL = os.environ['DATABASE_URL']
#DATABASE_URL = os.popen('heroku config:get DATABASE_URL -a thistest8').read()[:-1] #取得heroku資料庫連結
#conn = psycopg2.connect(DATABASE_URL, sslmode='require') #用剛剛拿到的連結連到資料庫
#cursor = conn.cursor() #宣告一個cursor 用來執行指令

# 接收 LINE 的資訊
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    
    
    #print(body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'



#聊天機器人撰寫


@handler.add(MessageEvent, message=TextMessage)
def echo(event):
    mtext=event.message.text
    user_id=str(event.source.user_id)
    
    if mtext=='n':
        DATABASE_URL = os.environ['DATABASE_URL']
        #DATABASE_URL = os.popen('heroku config:get DATABASE_URL -a thistest8').read()[:-1] #取得heroku資料庫連結
        conn = psycopg2.connect(DATABASE_URL, sslmode='require') #用剛剛拿到的連結連到資料庫
        cursor = conn.cursor() #宣告一個cursor 用來執行指令
        postgres_delete = """DELETE FROM record_basic WHERE record_basic.user_id=%s AND state!='99';"""
        cursor.execute(postgres_delete,(user_id,))
        postgres_delete = """DELETE FROM QA_basic WHERE QA_basic.user_id=%s AND state!='99';"""
        cursor.execute(postgres_delete,(user_id,))
        postgres_delete = """DELETE FROM comment_basic WHERE comment_basic.user_account=%s AND state!='99';"""
        cursor.execute(postgres_delete,(user_id,))
        conn.commit()
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="已成功結束之前的對話，可重新開始了喔~"))
        cursor.close() 
        conn.close()
    
    #取所有課程名稱
    DATABASE_URL = os.environ['DATABASE_URL']
    #DATABASE_URL = os.popen('heroku config:get DATABASE_URL -a thistest8').read()[:-1] #取得heroku資料庫連結
    conn = psycopg2.connect(DATABASE_URL, sslmode='require') #用剛剛拿到的連結連到資料庫
    cursor = conn.cursor() #宣告一個cursor 用來執行指令
    class_nameall=[]
    postgres_select_query = """SELECT class_name FROM class_basic;"""
    cursor.execute(postgres_select_query)
    conn.commit()
    raw = cursor.fetchall()
    if raw:
        for i in raw:
            class_nameall.append(i[0]) 
    cursor.close() #關閉cursor
    conn.close() #關閉資料庫連線
    
    #取所有user_id
    DATABASE_URL = os.environ['DATABASE_URL']
    #DATABASE_URL = os.popen('heroku config:get DATABASE_URL -a thistest8').read()[:-1] #取得heroku資料庫連結
    conn = psycopg2.connect(DATABASE_URL, sslmode='require') #用剛剛拿到的連結連到資料庫
    cursor = conn.cursor() #宣告一個cursor 用來執行指令
    user_idall=[]
    postgres_select_query = """SELECT user_id FROM record_basic WHERE record_basic.state= '0' AND record_basic.user_id = %s;"""
    cursor.execute(postgres_select_query,(user_id,))
    conn.commit()
    raw = cursor.fetchall()
    if raw:
        for i in raw:
            user_idall.append(i[0])  
    cursor.close() #關閉cursor
    conn.close() #關閉資料庫連線
    
    
    if mtext in class_nameall and user_id in user_idall:
        DATABASE_URL = os.environ['DATABASE_URL']
        #DATABASE_URL = os.popen('heroku config:get DATABASE_URL -a thistest8').read()[:-1] #取得heroku資料庫連結
        conn = psycopg2.connect(DATABASE_URL, sslmode='require') #用剛剛拿到的連結連到資料庫
        cursor = conn.cursor() #宣告一個cursor 用來執行指令
        
        postgres_select_query = """SELECT * FROM class_basic WHERE class_basic.class_name = %s ORDER BY class_year DESC;"""
        cursor.execute(postgres_select_query,(mtext,))
        conn.commit()
        raw = cursor.fetchall()
        
        class_id=''
        class_name=''
        teacher_id=''
        teacher_name=''
        op_stdy=''
        op_quality=''
        op_credit=''
        
        class_year=[]           
        assessment=[]
        assessment_split=[]
        
        if raw:   
           for i in raw:
                class_id=i[1]
                class_name=i[3]
                teacher_id=i[4]
                op_stdy=str(i[11])
                op_quality=str(i[12])
                op_credit=str(i[5])
                break;
           for i in raw:
                class_year.append(i[2])           
                assessment.append(i[6])
        assessment[0]=assessment[0].strip('{}')
        assessment[0]=assessment[0].replace("'","")
        assessment_split=re.split(',|:',assessment[0])
        
        assessment[1]=assessment[1].strip('{}')
        assessment[1]=assessment[1].replace("'","")
        assessment_split2=re.split(',|:',assessment[1])
                
        postgres_select_query = """SELECT * FROM teacher_basic WHERE teacher_basic.teacher_id = %s;"""
        cursor.execute(postgres_select_query,(teacher_id,))
        conn.commit()
        raw = cursor.fetchall()
        if raw:   
            for i in raw:
                teacher_name=i[1]
                break;
            teacher_name=teacher_name.strip('[]')
            teacher_name=teacher_name.replace("'","")
            
            line_bot_api.reply_message(
                event.reply_token,
                FlexSendMessage(
                    alt_text='查課',
                    contents={
                      "type": "bubble",
                      "body": {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                          {
                            "type": "text",
                            "text": class_id,
                            "weight": "bold",
                            "color": "#4C7FB9",
                            "size": "sm"
                          },
                          {
                            "type": "text",
                            "text": class_name,
                            "weight": "bold",
                            "size": "xxl",
                            "margin": "md"
                          },
                          {
                            "type": "text",
                            "text": teacher_name,
                            "size": "xs",
                            "color": "#aaaaaa",
                          },
                          {
                            "type": "text",
                            "text": op_stdy+'/'+op_quality+'/'+op_credit,
                            "size": "xs",
                            "color": "#aaaaaa"
                          },
                          {
                            "type": "separator",
                            "margin": "xxl"
                          },
                          {
                            "type": "box",
                            "layout": "vertical",
                            "margin": "xxl",
                            "spacing": "sm",
                            "contents": [
                              {
                                "type": "box",
                                "layout": "horizontal",
                                "contents": [
                                  {
                                    "type": "text",
                                    "text": class_year[0],
                                    "size": "md",
                                    "color": "#555555",
                                    "flex": 0,
                                    "weight": "bold"
                                  }
                                ]
                              },
                              {
                                "type": "box",
                                "layout": "horizontal",
                                "contents": [
                                  {
                                    "type": "text",
                                    "text": " "+assessment_split[0],
                                    "color": "#555555",
                                    "size": "sm"
                                  },
                                  {
                                    "type": "text",
                                    "text": assessment_split[1]+"%",
                                    "color": "#111111",
                                    "size": "sm",
                                    "align": "end"
                                  }
                                ]
                              },
                              {
                                "type": "box",
                                "layout": "horizontal",
                                "contents": [
                                  {
                                    "type": "text",
                                    "text": assessment_split[2],
                                    "color": "#555555",
                                    "size": "sm"
                                  },
                                  {
                                    "type": "text",
                                    "text": assessment_split[3]+"%",
                                    "color": "#111111",
                                    "size": "sm",
                                    "align": "end"
                                  }
                                ]
                              },
                              {
                                "type": "box",
                                "layout": "horizontal",
                                "contents": [
                                  {
                                    "type": "text",
                                    "text": assessment_split[4],
                                    "size": "sm",
                                    "color": "#555555",
                                    "flex": 0
                                  },
                                  {
                                    "type": "text",
                                    "text": assessment_split[5]+"%",
                                    "color": "#111111",
                                    "size": "sm",
                                    "align": "end"
                                  }
                                ]
                              },
                              {
                                "type": "box",
                                "layout": "horizontal",
                                "contents": [
                                  {
                                    "type": "text",
                                    "text": assessment_split[6],
                                    "size": "sm",
                                    "color": "#555555",
                                    "flex": 0
                                  },
                                  {
                                    "type": "text",
                                    "text": assessment_split[7]+"%",
                                    "color": "#111111",
                                    "size": "sm",
                                    "align": "end"
                                  }
                                ]
                              },
                              {
                                "type": "separator",
                                "margin": "xxl"
                              },
                              {
                                "type": "box",
                                "layout": "horizontal",
                                "contents": [
                                  {
                                    "type": "text",
                                    "text": class_year[1],
                                    "size": "md",
                                    "color": "#555555",
                                    "flex": 0,
                                    "weight": "bold"
                                  }
                                ]
                              },
                              {
                                "type": "box",
                                "layout": "horizontal",
                                "contents": [
                                  {
                                    "type": "text",
                                    "text": " "+assessment_split2[0],
                                    "color": "#555555",
                                    "size": "sm"
                                  },
                                  {
                                    "type": "text",
                                    "text": assessment_split2[1]+"%",
                                    "color": "#111111",
                                    "size": "sm",
                                    "align": "end"
                                  }
                                ]
                              },
                              {
                                "type": "box",
                                "layout": "horizontal",
                                "contents": [
                                  {
                                    "type": "text",
                                    "text": assessment_split2[2],
                                    "color": "#555555",
                                    "size": "sm"
                                  },
                                  {
                                    "type": "text",
                                    "text": assessment_split2[3]+"%",
                                    "color": "#111111",
                                    "size": "sm",
                                    "align": "end"
                                  }
                                ]
                              },
                              {
                                "type": "box",
                                "layout": "horizontal",
                                "contents": [
                                  {
                                    "type": "text",
                                    "text": assessment_split2[4],
                                    "size": "sm",
                                    "color": "#555555",
                                    "flex": 0
                                  },
                                  {
                                    "type": "text",
                                    "text": assessment_split2[5]+"%",
                                    "size": "sm",
                                    "color": "#111111",
                                    "align": "end"
                                  }
                                ]
                              },
                              {
                                "type": "box",
                                "layout": "horizontal",
                                "contents": [
                                  {
                                    "type": "text",
                                    "text": assessment_split2[6],
                                    "size": "sm",
                                    "color": "#555555",
                                    "flex": 0
                                  },
                                  {
                                    "type": "text",
                                    "text": assessment_split2[7]+"%",
                                    "size": "sm",
                                    "color": "#111111",
                                    "align": "end"
                                  }
                                ]
                              }
                            ]
                          }
                        ]
                      },
                    "footer": {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                          {
                            "type": "button",
                            "action": {
                              "type": "message",
                              "label": "課堂評論",
                              "text": "@課堂評論"
                            },
                            "color": "#4C7FB9",
                            "style": "primary"
                          }
                        ]
                      }
                    }
                )
            )
            
        update_class_name = mtext
        postgres_update_query = f"""UPDATE record_basic SET state = '99',class_name = %s WHERE state = '0' AND user_id = %s"""
        cursor.execute(postgres_update_query, (update_class_name,user_id,))
        conn.commit()
        
        cursor.close() #關閉cursor
        conn.close() #關閉資料庫連線
        
    if mtext not in class_nameall and user_id in user_idall:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='找不到此課程，請輸入正確的課程名稱~')
        )
        
    elif mtext=='@查課': 
        DATABASE_URL = os.environ['DATABASE_URL']
        #DATABASE_URL = os.popen('heroku config:get DATABASE_URL -a thistest8').read()[:-1] #取得heroku資料庫連結
        conn = psycopg2.connect(DATABASE_URL, sslmode='require') #用剛剛拿到的連結連到資料庫
        cursor = conn.cursor() #宣告一個cursor 用來執行指令
        postgres_select_query = """SELECT state FROM comment_basic WHERE user_account = %s ORDER BY state ASC;"""
        cursor.execute(postgres_select_query,(user_id,))
        conn.commit()
        raw = cursor.fetchone()
        postgres_select_query = """SELECT state FROM record_basic WHERE user_id = %s ORDER BY state ASC;"""
        cursor.execute(postgres_select_query,(user_id,))
        conn.commit()
        raw2 = cursor.fetchone()
        postgres_select_query = """SELECT state FROM QA_basic WHERE user_id = %s ORDER BY state ASC;"""
        cursor.execute(postgres_select_query,(user_id,))
        conn.commit()
        raw3 = cursor.fetchone()
        
        if raw and raw[0]!='99':
            #請結束上一個對話 
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text='請先結束上一個對話')
            )  
        if raw2 and raw2[0]!='99':
            #請結束上一個對話 
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text='請先結束上一個對話')
            )
        if raw3 and raw3[0]!='99':
            #請結束上一個對話 
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text='請先結束上一個對話')
            )
        
        DATABASE_URL = os.environ['DATABASE_URL']
        #DATABASE_URL = os.popen('heroku config:get DATABASE_URL -a thistest8').read()[:-1] #取得heroku資料庫連結
        conn = psycopg2.connect(DATABASE_URL, sslmode='require') #用剛剛拿到的連結連到資料庫
        cursor = conn.cursor() #宣告一個cursor 用來執行指令
        
        record = (user_id, '0')
        table_columns = '(user_id, state)'
        postgres_insert_query = f"""INSERT INTO record_basic {table_columns} VALUES (%s, %s);"""
        cursor.execute(postgres_insert_query, record)
        conn.commit()
        
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='請輸入課程名稱: ')
        )
        
        cursor.close() #關閉cursor
        conn.close() #關閉資料庫連線
             
        cursor.close() #關閉cursor
        conn.close() #關閉資料庫連線
        
    elif mtext=='@課堂評論':
        DATABASE_URL = os.environ['DATABASE_URL']
        #DATABASE_URL = os.popen('heroku config:get DATABASE_URL -a thistest8').read()[:-1] #取得heroku資料庫連結
        conn = psycopg2.connect(DATABASE_URL, sslmode='require') #用剛剛拿到的連結連到資料庫
        cursor = conn.cursor() #宣告一個cursor 用來執行指令
        
        class_name=''
        postgres_select_query = """SELECT class_name FROM record_basic WHERE record_basic.state = '99' AND user_id = %s ORDER BY code DESC;"""
        cursor.execute(postgres_select_query,(user_id,))
        conn.commit()
        raw = cursor.fetchone()
        if raw:   
            class_name=raw[0]
        
        class_id=''
        postgres_select_query = """SELECT class_id FROM class_basic WHERE class_basic.class_name = %s;"""
        cursor.execute(postgres_select_query,(class_name,))
        conn.commit()
        raw = cursor.fetchone()
        if raw:   
            class_id=raw[0]
        
        content=''
        star=''
        contentall=''
        postgres_select_query = """SELECT comment_content,comment_star FROM comment_basic WHERE comment_basic.class_id = %s AND comment_basic.state='99' ORDER BY comment_id DESC;"""
        cursor.execute(postgres_select_query,(class_id,))
        conn.commit()
        raw = cursor.fetchmany(3)
        if raw:   
            for i in raw:
                content=i[0]
                content=content.strip('()')
                content=content.replace("'","")
                content=content.replace(",","")
                star=i[1]
                contentall+=(content+"\n星評:"+star+"\n--------------------------------------\n")
        
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=contentall)
            )
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="目前沒有此課程的課堂評論喔")
            )
            
        cursor.close() #關閉cursor
        conn.close() #關閉資料庫連線
        
    elif mtext=='@QA':
        DATABASE_URL = os.environ['DATABASE_URL']
        #DATABASE_URL = os.popen('heroku config:get DATABASE_URL -a thistest8').read()[:-1] #取得heroku資料庫連結
        conn = psycopg2.connect(DATABASE_URL, sslmode='require') #用剛剛拿到的連結連到資料庫
        cursor = conn.cursor() #宣告一個cursor 用來執行指令
        postgres_select_query = """SELECT state FROM comment_basic WHERE user_account = %s ORDER BY state ASC;"""
        cursor.execute(postgres_select_query,(user_id,))
        conn.commit()
        raw = cursor.fetchone()
        postgres_select_query = """SELECT state FROM record_basic WHERE user_id = %s ORDER BY state ASC;"""
        cursor.execute(postgres_select_query,(user_id,))
        conn.commit()
        raw2 = cursor.fetchone()
        postgres_select_query = """SELECT state FROM QA_basic WHERE user_id = %s ORDER BY state ASC;"""
        cursor.execute(postgres_select_query,(user_id,))
        conn.commit()
        raw3 = cursor.fetchone()
        
        if raw and raw[0]!='99':
            #請結束上一個對話 
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text='請先結束上一個對話')
            )  
        if raw2 and raw2[0]!='99':
            #請結束上一個對話 
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text='請先結束上一個對話')
            )
        if raw3 and raw3[0]!='99':
            #請結束上一個對話 
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text='請先結束上一個對話')
            )

        DATABASE_URL = os.environ['DATABASE_URL']
        #DATABASE_URL = os.popen('heroku config:get DATABASE_URL -a thistest8').read()[:-1] #取得heroku資料庫連結
        conn = psycopg2.connect(DATABASE_URL, sslmode='require') #用剛剛拿到的連結連到資料庫
        cursor = conn.cursor() #宣告一個cursor 用來執行指令
        
        postgres_insert_query ="""SELECT * FROM  QA_final;"""
        cursor.execute(postgres_insert_query)
        conn.commit()
        raw = cursor.fetchall()
        if raw:
            QA_Q=[]
            QA_A=[]
            for i in raw:
                QA_Q.append(i[1])
                QA_A.append(i[2])
        message=TextSendMessage(
            text='Q&A',
            quick_reply=QuickReply(
                items=[
                    QuickReplyButton(
                        action=MessageAction(label=QA_Q[0],text=QA_A[0])
                    ),
                    QuickReplyButton(
                        action=MessageAction(label=QA_Q[1],text=QA_A[1])
                    ),
                    QuickReplyButton(
                        action=MessageAction(label=QA_Q[2],text=QA_A[2])
                    ),
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token,message)
        cursor.close() #關閉cursor
        conn.close() #關閉資料庫連線
        cursor.close() #關閉cursor
        conn.close() #關閉資料庫連線        


    
    user = str(event.source.user_id)
    text = str(event.message.text)
    if text=='@問題回饋':
    #collect user id
        DATABASE_URL = os.environ['DATABASE_URL']
        #DATABASE_URL = os.popen('heroku config:get DATABASE_URL -a thistest8').read()[:-1] #取得heroku資料庫連結
        conn = psycopg2.connect(DATABASE_URL, sslmode='require') #用剛剛拿到的連結連到資料庫
        cursor = conn.cursor() #宣告一個cursor 用來執行指令
        postgres_select_query = """SELECT state FROM comment_basic WHERE user_account = %s ORDER BY state ASC;"""
        cursor.execute(postgres_select_query,(user_id,))
        conn.commit()
        raw = cursor.fetchone()
        postgres_select_query = """SELECT state FROM record_basic WHERE user_id = %s ORDER BY state ASC;"""
        cursor.execute(postgres_select_query,(user_id,))
        conn.commit()
        raw2 = cursor.fetchone()
        postgres_select_query = """SELECT state FROM QA_basic WHERE user_id = %s ORDER BY state ASC;"""
        cursor.execute(postgres_select_query,(user_id,))
        conn.commit()
        raw3 = cursor.fetchone()
        
        if raw and raw[0]!='99':
            #請結束上一個對話 
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text='請先結束上一個對話')
            )  
        if raw2 and raw2[0]!='99':
            #請結束上一個對話 
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text='請先結束上一個對話')
            )
        if raw3 and raw3[0]!='99':
            #請結束上一個對話 
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text='請先結束上一個對話')
            )
        
        #open
        DATABASE_URL = os.environ['DATABASE_URL']
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')  
        cursor = conn.cursor() 

        user_id = user
        state = '0'

        record = (user_id, '', '0')
        table_columns = '(user_id, QA_Q ,state)'
        postgres_insert_query = f"""INSERT INTO QA_basic {table_columns} VALUES (%s, %s, %s);"""
        cursor.execute(postgres_insert_query, record) 
        conn.commit()

        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='請輸入問題回饋: '))

        cursor.close() 
        conn.close() 
        #close
            
        cursor.close() 
        conn.close() 

    #collect the user id that it's state is 0
    #open  
    DATABASE_URL = os.environ['DATABASE_URL']
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')  
    cursor = conn.cursor()         
    QA_ids =[]
    postgres_select_query = """SELECT user_id FROM QA_basic WHERE QA_basic.state = '0';"""
    cursor.execute(postgres_select_query, (user,))
    conn.commit()
    data = cursor.fetchall()
    if data: 
        for i in data:
            QA_ids.append(i[0]) 
    cursor.close() 
    conn.close() 
    #close


    if text!='@問題回饋' and user in QA_ids :  
    # clooect question

        #open
        DATABASE_URL = os.environ['DATABASE_URL']
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')  
        cursor = conn.cursor() 

        QA_Q = text
        record = (QA_Q, user)
        table_columns = '(QA_Q, state)'
        postgres_update_query = f"""UPDATE QA_basic SET QA_Q = %s ,state = '99' WHERE state = '0' AND user_id = %s """
        cursor.execute(postgres_update_query, record)
        conn.commit()

        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='感謝您的回饋～ '))


        cursor.close() 
        conn.close() 
        #close




    if text=='@留評論': 
    #collect data user first entered
        DATABASE_URL = os.environ['DATABASE_URL']
        #DATABASE_URL = os.popen('heroku config:get DATABASE_URL -a thistest8').read()[:-1] #取得heroku資料庫連結
        conn = psycopg2.connect(DATABASE_URL, sslmode='require') #用剛剛拿到的連結連到資料庫
        cursor = conn.cursor() #宣告一個cursor 用來執行指令
        postgres_select_query = """SELECT state FROM comment_basic WHERE user_account = %s ORDER BY state ASC;"""
        cursor.execute(postgres_select_query,(user_id,))
        conn.commit()
        raw = cursor.fetchone()
        postgres_select_query = """SELECT state FROM record_basic WHERE user_id = %s ORDER BY state ASC;"""
        cursor.execute(postgres_select_query,(user_id,))
        conn.commit()
        raw2 = cursor.fetchone()
        postgres_select_query = """SELECT state FROM QA_basic WHERE user_id = %s ORDER BY state ASC;"""
        cursor.execute(postgres_select_query,(user_id,))
        conn.commit()
        raw3 = cursor.fetchone()
        
        if raw and raw[0]!='99':
            #請結束上一個對話 
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text='請先結束上一個對話')
            )  
        if raw2 and raw2[0]!='99':
            #請結束上一個對話 
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text='請先結束上一個對話')
            )
        if raw3 and raw3[0]!='99':
            #請結束上一個對話 
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text='請先結束上一個對話')
            )  
        
        #open
        DATABASE_URL = os.environ['DATABASE_URL']
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')  
        cursor = conn.cursor() 

        user_account = user
        school_id = '1004'
        state = '0'

        record = (user_account, school_id, '', '', '', '0')
        table_columns = '(user_account, school_id, class_id, comment_content, comment_star, state)'
        postgres_insert_query = f"""INSERT INTO comment_basic {table_columns} VALUES (%s, %s, %s, %s, %s, %s);"""
        cursor.execute(postgres_insert_query, record)
        conn.commit()

        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請問課堂代碼為？"))

        cursor.close() 
        conn.close() 
        #close
        cursor.close() 
        conn.close() 


    #collect data of all class ids
    #open  
    DATABASE_URL = os.environ['DATABASE_URL']
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')  
    cursor = conn.cursor()         
    class_ids =[]
    postgres_select_query = """SELECT class_id FROM class_basic;"""
    cursor.execute(postgres_select_query)
    conn.commit()
    data = cursor.fetchall()
    if data: 
        for i in data:
            class_ids.append(i[0]) 
    cursor.close() 
    conn.close() 
    #close

    #collect data of all user ids
    #open  
    DATABASE_URL = os.environ['DATABASE_URL']
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')  
    cursor = conn.cursor()         
    user_ids =[]
    postgres_select_query = """SELECT user_account FROM comment_basic WHERE comment_basic.state = '0';"""
    cursor.execute(postgres_select_query, (user,))
    conn.commit()
    daTa = cursor.fetchall()
    if daTa: 
        for i in daTa:
            user_ids.append(i[0]) 
    cursor.close() 
    conn.close() 
    #close

    #fetch the previous state, the one state = '0'
    #open  
    DATABASE_URL = os.environ['DATABASE_URL']
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')  
    cursor = conn.cursor()         
    status =[]
    postgres_select_query = """SELECT state FROM comment_basic WHERE comment_basic.state= '0' AND user_account = user_account;"""
    cursor.execute(postgres_select_query)
    conn.commit()
    daTa = cursor.fetchall()
    if daTa: 
        for i in daTa:
            status.append(i[0]) 
    cursor.close() 
    conn.close() 
    #close 



    if text in class_ids and user in user_ids and '0' in status : 


        #open
        DATABASE_URL = os.environ['DATABASE_URL']
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')  
        cursor = conn.cursor() 

        class_id = text
        state = '1'

        record = (class_id, user)
        table_columns = '(class_id, state)'
        postgres_update_query = f"""UPDATE comment_basic SET class_id = %s, state = '1' WHERE user_account = %s AND state = '0' """
        cursor.execute(postgres_update_query, record)
        conn.commit()

        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請輸入您的課堂評論～"))

        cursor.close() 
        conn.close() 
        #close
        
    if text not in class_ids and user in user_ids and '0' in status : 
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="找不到此課程，請輸入正確的課堂代碼"))


    #collect data of all user ids
    #open  
    DATABASE_URL = os.environ['DATABASE_URL']
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')  
    cursor = conn.cursor()         
    user_ids =[]
    postgres_select_query = """SELECT user_account FROM comment_basic WHERE comment_basic.state = '1';"""
    cursor.execute(postgres_select_query, (user,))
    conn.commit()
    daTa = cursor.fetchall()
    if daTa: 
        for i in daTa:
            user_ids.append(i[0]) 
    cursor.close() 
    conn.close() 
    #close

    #fetch the previous state, the one state = '0'
    #open  
    DATABASE_URL = os.environ['DATABASE_URL']
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')  
    cursor = conn.cursor()         
    status =[]
    postgres_select_query = """SELECT state FROM comment_basic WHERE comment_basic.state= '1' AND user_account = user_account;"""
    cursor.execute(postgres_select_query)
    conn.commit()
    daTa = cursor.fetchall()
    if daTa: 
        for i in daTa:
            status.append(i[0]) 
    cursor.close() 
    conn.close() 
    #close



    if text not in class_ids and user in user_ids and '1' in status  :  

        #open
        DATABASE_URL = os.environ['DATABASE_URL']
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')  
        cursor = conn.cursor() 
        
        comment_content = text
        if comment_content!='@查課' and comment_content!='@留評論' and comment_content!='@QA' and comment_content!='@問題回饋' and comment_content!='@課堂評論':
            state = '2'
            
            record = (comment_content, user)  
            table_columns = '(comment_content, state)'
            postgres_update_query = f"""UPDATE comment_basic SET comment_content = %s, state = '2' WHERE comment_basic.user_account = %s AND comment_basic.state = '1' """
            cursor.execute(postgres_update_query, record)
            conn.commit()
    
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="5為最高分0為最低分，請問您覺得這堂課的分數為 ？"))
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text='您是誤觸按鈕了嗎? 請再次輸入您的評論~')
            )
        cursor.close() 
        conn.close() 
        #close



    #collect data of all user ids
    #open  
    DATABASE_URL = os.environ['DATABASE_URL']
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')  
    cursor = conn.cursor()         
    user_ids =[]
    postgres_select_query = """SELECT user_account FROM comment_basic WHERE comment_basic.state = '2';"""
    cursor.execute(postgres_select_query, (user,))
    conn.commit()
    daTa = cursor.fetchall()
    if daTa: 
        for i in daTa:
            user_ids.append(i[0]) 
    cursor.close() 
    conn.close() 
    #close

    #fetch the previous state, the one state = '2'
    #open  
    DATABASE_URL = os.environ['DATABASE_URL']
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')  
    cursor = conn.cursor()         
    status =[]
    postgres_select_query = """SELECT state FROM comment_basic WHERE comment_basic.state = '2' AND user_account = user_account;"""
    cursor.execute(postgres_select_query)
    conn.commit()
    daTa = cursor.fetchall()
    if daTa: 
        for i in daTa:
            status.append(i[0]) 
    cursor.close() 
    conn.close() 
    #close

    #fetch the comment of this user
    #open  
    DATABASE_URL = os.environ['DATABASE_URL']
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')  
    cursor = conn.cursor()         
    comments =[]
    postgres_select_query = """SELECT comment_content FROM comment_basic WHERE user_account = user_account;"""
    cursor.execute(postgres_select_query)
    conn.commit()
    daTa = cursor.fetchall()
    if daTa: 
        for i in daTa:
            comments.append(i[0]) 
    cursor.close() 
    conn.close() 
    #close



    if  user in user_ids and '2' in status :
        if '0' == text or '1' == text or '2' == text or '3' == text or '4' == text or '5' == text:
            
            # open
            DATABASE_URL = os.environ['DATABASE_URL']
            conn = psycopg2.connect(DATABASE_URL, sslmode='require')   
            cursor = conn.cursor()  

            comment_star = text
            state = '3'
        
            record = (comment_star, user)  
            table_columns = '(comment_star, state)'
            postgres_update_query = f"""UPDATE comment_basic SET comment_star = %s, state = '99' WHERE state = '2' AND user_account = %s"""
            cursor.execute(postgres_update_query, record)
            conn.commit()

            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="感謝您回覆這堂課的相關評論～"))
        
            cursor.close() 
            conn.close() 
            #close
            
        else:
            
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請輸入0~5的數字哦～"))
            
        
    
'''     
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='無法判斷喵~')
        )

'''

if __name__ == "__main__":
    app.run()
