import os, json

# Save the list of dictionaries to a JSON file
def save_to_file(cars_list, filename='cars_data.json'):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(cars_list, f, ensure_ascii=False, indent=4)


# פונקציה לשליחת קובץ JSON לקבוצת טלגרם
def send_json_to_group(bot, cars_list ,json_file_path, chat_id):
    with open(json_file_path, 'w', encoding='utf-8') as f:
        json.dump(cars_list, f, ensure_ascii=False, indent=4)
    with open(json_file_path, 'rb') as json_file:
        sent_message = bot.send_document(chat_id, json_file)
        # Pin the message
        bot.pin_chat_message(chat_id, sent_message.message_id,
            disable_notification=True  # Don't notify members about pinning
        )



# Create a dictionary's list of cars data
def create_dict(list_details: list) -> dict:
    dict_var = {}
    list_var = []

    for i in list_details:
        list_var.append(i.split(':')[0])
        list_var.append(i.split(':')[1])

    i = 0
    while i < (len(list_var)):
        dict_var[list_var[i]] = list_var[i+1]
        i += 2

    dict_var["id"] = int(dict_var["id"])
    images = [f'{dict_var["uniq_name"]}/{photo}' for photo in os.listdir(f'static/images/{dict_var["uniq_name"]}')]
    dict_var["images"] = images
    return dict_var
