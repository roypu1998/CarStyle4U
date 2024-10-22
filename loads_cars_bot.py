import requests
from dotenv import load_dotenv
from static.cars_list import download_pinned_media, load_catalog_from_json
from static.utils import create_dict, send_json_to_group
import os
import telebot
import threading


# Load environment variables from .env file
load_dotenv()

bot_token = os.getenv('BOT_TOKEN')
bot_id = os.getenv("BOT_ID")
domain = os.getenv("DOMAIN")
catalog_chat_id = os.getenv("CATALOG_CHAT_ID")

add_car_flag = 0
bot = telebot.TeleBot(token=bot_id+ ':' + bot_token)

# Download media if desired
download_result = download_pinned_media(bot, bot_token, catalog_chat_id)
print(f"Download status: {download_result['status']}")
print(f"Download message: {download_result['message']}")
if download_result['status'] == 'success':
    print(f"Saved to: {download_result['file_path']}")
    cars = load_catalog_from_json(json_file_path=download_result['file_path'])


# set webhook
url = f"https://api.telegram.org/bot{bot_id}:{bot_token}/setWebhook?url=https://{domain}/webhook/telegram/{bot_id}:{bot_token}"
# Specify a directory to save the photos
save_dir = 'static/images'

response = requests.get(url)

@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    bot.reply_to(message, "Howdy, how are you doing?")


@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    # Get the highest resolution photo
    photo_id = message.photo[-1].file_id
    folder_name = str(message.json["caption"]).split('$')[0].lower()
    photo_name = str(message.json["caption"]).split('$')[1]
    # Download the photo
    file_info = bot.get_file(photo_id)
    # Create the directory
    try:
        os.mkdir(f'{save_dir}/{folder_name}')
        print(f"Directory '{save_dir}/{folder_name}' created successfully.")
    except FileExistsError:
        print(f"Directory '{save_dir}/{folder_name}' already exists.")
    except OSError as e:
        print(f"Error creating directory: {e}")

    file_path = os.path.join(f'{save_dir}/{folder_name}', f"{photo_name}.jpg")

    # Download the file from Telegram servers
    downloaded_file = bot.download_file(file_info.file_path)

    # Save the photo to the specified directory
    with open(file_path, 'wb') as new_file:
        new_file.write(downloaded_file)

    bot.reply_to(message, f"Photo saved as {file_path}")


@bot.message_handler(func=lambda msg: msg.content_type == 'text' and add_car_flag == 1 and msg.text[0] == '$' and msg.text[-1] == '$')
def add_car(message):
    global add_car_flag
    try:
        string_data = message.text[1:len(message.text)-1]
        cars.append(create_dict(string_data.replace('\n', '').replace('    ','').replace("'","").split('#')))
        send_json_to_group(bot=bot, cars_list=cars, json_file_path='cars_data.json', chat_id=catalog_chat_id)
        bot.reply_to(message, "Car added")
        bot.send_message(message.chat.id, "Cars file updated")
    except Exception as error:
        bot.reply_to(message, f"Oops! Something Wrong:\n{error}")


@bot.message_handler(func=lambda msg: msg.content_type == 'text' and add_car_flag == 1 and msg.text.isdigit() and msg.text not in ['/end', '/addorremovecars', '/displaycars'])
def remove_car(message):
    remove_var = 9999
    for i in range(len(cars)):
        if cars[i]["id"] == int(message.text):
            remove_var = i
    if remove_var != 9999:
        bot.reply_to(message, f'{cars[remove_var]["id"]} found')
        cars.pop(remove_var)
        send_json_to_group(bot=bot, cars_list=cars, json_file_path='cars_data.json', chat_id=catalog_chat_id)
        bot.reply_to(message, f'Car removed')
        bot.send_message(message.chat.id, "Cars file updated")
    else:
        bot.reply_to(message, f'No Car for id: {message.text}')


@bot.message_handler(commands=['end', 'addorremovecars', 'displaycars'])
def set_car(message):
    global add_car_flag
    if message.text == '/addorremovecars':
        global add_car_flag
        add_car_flag = 1
        bot.reply_to(message, "Please add/remove car")
    elif message.text == '/end':
        add_car_flag = 0
        bot.reply_to(message, "End add/remove action")
    elif message.text == '/displaycars':
        for car in cars:
            bot.send_message(message.chat.id, str(car))
    else:
        pass

def get_cars():
    return cars

def run():
    print("bot start")
    bot.infinity_polling()


thread = threading.Thread(target=run)

thread.start()
