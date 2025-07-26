# ========================== Part 1: Imports & Initial Config ==========================

from Config import *
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

bot = telebot.TeleBot(token)

import logging

logging.basicConfig(
    filename='logging.log',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def listener(messages):
    for m in messages:
        user_info = f"{m.chat.first_name} [{m.chat.id}]"

        if m.content_type == 'text':
            content = f'Text Message: "{m.text}"'

        elif m.content_type == 'photo':
            photo_id = m.photo[-1].file_id
            content = f'Photo Received - File ID: {photo_id}'

        elif m.content_type == 'document':
            filename = m.document.file_name
            content = f'Document Received - File Name: {filename}'

        else:
            content = f'Other Content Received - Type: {m.content_type}'

        log = f'{user_info}: {content}'
        print(log)
        logging.info(log)

bot.set_update_listener(listener)

import mysql.connector

def insert_product_info(name, desc=None, price=0, inv=0,discount=0, file_id=None):

    if not 0 <= discount <= 100:
        logging.error('Admin entered a number that was not between 0 and 100!')
        print('Admin entered a number that was not between 0 and 100!')
        return
    
    conn = None
    cur = None

    try:

        conn = mysql.connector.connection.MySQLConnection(**config)
        cur = conn.cursor()
        cur.execute(
            'INSERT INTO PRODUCT (NAME,DESCRIPTION,PRICE,INV,DISCOUNT,FILE_ID) VALUES (%s,%s,%s,%s,%s,%s)',
            (name, desc, price, inv, discount, file_id)
        )
        conn.commit()
        product_id = cur.lastrowid
        print(f"Product '{name}' inserted successfully.")
        return product_id
    
    except mysql.connector.Error as err:

        logging.error(f'Database error: {err}')
        print(f'Database error: {err}')

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

def get_product_info(product_id):
    conn = mysql.connector.connection.MySQLConnection(**config)
    cur = conn.cursor(dictionary=True)
    cur.execute('SELECT * FROM PRODUCT WHERE ID=%s',(product_id,))
    info = cur.fetchone()
    cur.close()
    conn.close()
    return info

# ========================== Part 2: Definitions & Globals ==========================

channel_cid = "@Penora_market"

user_step = {}  # {cid: step}

cart = {}    # {cid : {code : qty}}

commands = {
    'start': 'استارت دوباره ی ربات ↩️',
    'help': 'لیست دستورات و توضیحات آنها 📜',
}

admin_commands = {
    'add_product': 'اضافه کردن محصولی جدید ➕'
}


# ========================== Part 3: Bot Handlers ==========================

@bot.message_handler(commands=['start'])
def send_welcome(message):
    cid = message.chat.id
    bot.reply_to(message,"""👋 سلام! به Penora خوش اومدی! 🎉
اینجا فروشگاه تخصصی لوازم تحریر، طراحی، نقاشی و لوازم اداریه.
هر چی برای خلاقیت و کار نیاز داری اینجاست! ✏️🎨📚

برای دیدن دستورات، از /help استفاده کن.
""")
    if len(message.text) > 1:
        text = message.text
        invite_value = text.split()[-1]
        if invite_value.startswith('product'):
            product_id = int(invite_value.split('_')[-1])
            product_info = get_product_info(product_id)
            if not product_info:
                bot.send_message(cid, 'محصولی با این شناسه یافت نشد ❌')
                return
            product_photo_id = product_info['FILE_ID']
            name = product_info['NAME']
            desc = product_info['DESCRIPTION']
            price = product_info['PRICE']
            inv = product_info['INV']
            discount = product_info['DISCOUNT']
            caption = create_caption(name,desc,price,discount,product_id,for_channel=False)
            bot.send_photo(cid,product_photo_id,caption=caption,reply_markup=gen_product_markup(product_id,1))

def gen_product_markup(code,qty):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('➖',callback_data=f'change_{code}_{qty-1}'),InlineKeyboardButton(qty,callback_data='Nothing'),InlineKeyboardButton('➕',callback_data=f'change_{code}_{qty+1}'))
    markup.add(InlineKeyboardButton('افزودن به سبد خرید 🛒',callback_data=f'add_{code}_{qty}'))
    markup.add(InlineKeyboardButton('انصراف ✖️',callback_data='cancle'))
    return markup

@bot.callback_query_handler(func=lambda call :True)
def callback_handler(call):
    call_id = call.id
    cid = call.message.chat.id
    mid = call.message.message_id
    data = call.data
    if data.startswith('change'):
        _,code,new_qty = data.split('_')
        if int(new_qty) == 0:
            bot.answer_callback_query(call_id,'Quantity can not be zero!')
            return
        new_markup = gen_product_markup(int(code),int(new_qty))
        bot.edit_message_reply_markup(cid,mid,reply_markup=new_markup)
    elif data == 'cancle':
        bot.answer_callback_query(call_id,'cancle proccess')
        bot.edit_message_reply_markup(cid,mid,reply_markup=None)
        try:
            bot.delete_message(cid,mid)
        except:
            pass
    elif data.startswith('add'):
        _,code,qty = data.split('_')
        cart.setdefault(cid,{})
        cart[cid].setdefault(code,0)
        cart[cid][code] += int(qty)
        bot.edit_message_reply_markup(cid,mid,reply_markup=None)
        bot.send_message(cid,f'محصول مورد نظر با موفقیت به سبد خرید اضافه شد ✅')


@bot.message_handler(commands=['help'])
def command_help(message):
    cid = message.chat.id

    help_text = "───── 📜 لیست دستورات فروشگاه ─────\n\n"
    for cmd, desc in commands.items():
        help_text += f"/{cmd}\n  » {desc}\n\n"

    if cid in admins:
        help_text += "───── 📌لیست دستورات ادمین ها ─────\n\n"
        for cmd, desc in admin_commands.items():
            help_text += f"/{cmd}\n  » {desc}\n\n"

    bot.send_message(cid, help_text)


def create_caption(name, desc, price, discount,product_id,for_channel=True):

    if discount != 0:
        final_price = int(price * (1 - (discount / 100)))
        result_price = f"💰 قیمت قبلی: {price} ریال\n🔥 تخفیف: %{discount}\n✅ قیمت نهایی: {final_price} ریال"
    else:
        result_price = f"💰 قیمت: {price} ریال"
        
    text = f"""
📝 نام محصول: {name}
🖊️ توضیحات: {desc}

{result_price}"""
    if for_channel:
        text += f'''\n
🛒 برای خرید کلیک کنید:
👉 [BUY](https://t.me/PenoraBot?start=product_{product_id})'''

    return text


@bot.message_handler(commands=['add_product'])
def add_product(message):
    cid = message.chat.id
    if cid in admins:
        bot.send_message(cid,'''
لطفاً تصویر محصول به همراه اطلاعات خواسته شده را به فرمت زیر ارسال نمایید 👇
                         
نام:
توضیحات:
قیمت:
موجودی:
تخفیف:
                         ''')
        user_step[cid] = 'add_product'
    else:
        command_default(message)


@bot.message_handler(content_types=['photo'])
def message_photo_handler(message):
    cid = message.chat.id

    if cid in admins and user_step.get(cid) == 'add_product':
        caption = message.caption
        if not caption:
            bot.send_message(cid,'عکس ارسال شده حتماً باید با اطلاعات خواسته شده باشد!')
            user_step.pop(cid, None)
            return
        
        try:

            lines = caption.split('\n')
            name = [line.split(':')[-1] for line in lines if line.startswith('نام')][0]
            desc = [line.split(':')[-1] for line in lines if line.startswith('توضیحات')][0]
            price = int([line.split(':')[-1] for line in lines if line.startswith('قیمت')][0])
            inv = int([line.split(':')[-1] for line in lines if line.startswith('موجودی')][0])
            discount = int([line.split(':')[-1] for line in lines if line.startswith('تخفیف')][0])

            file_id = message.photo[-1].file_id
            product_id = insert_product_info(name,desc,price,inv,discount,file_id)
            caption = create_caption(name,desc,price,discount,product_id)
            bot.send_photo(channel_cid,file_id,caption=caption,parse_mode='MarkDownV2')
            bot.send_message(cid,'محصول با موفقیت به انبار فروشگاه اضافه شد ✅')
            user_step.pop(cid, None)

        except Exception as e:
            bot.send_message(cid,'فرمت توضیحات نامعتبر است. لطفاً توضیحات را با فرمت خواسته شده ارسال نمایید ❌')
            user_step.pop(cid, None)
            return
    else:
        command_default(message)


@bot.message_handler(func=lambda message: True)
def command_default(message):
    cid = message.chat.id
    bot.send_message(cid, f'''
🤔 متوجه نشدم چی گفتی!
🔤 پیام: "{message.text}"

برای شروع دوباره از دستور /start یا /help زیر استفاده کن👇
''')

bot.infinity_polling()
