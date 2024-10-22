import json
from datetime import datetime

def get_pinned_message(bot, channel_id):
    """
    Get the pinned message from a Telegram channel.

    Parameters:
    bot_token (str): Your Telegram bot token
    channel_id (str): Channel username (with @) or channel ID

    Returns:
    dict: Information about the pinned message
    """
    try:
        # Get channel information including pinned message
        chat = bot.get_chat(channel_id)

        if not chat.pinned_message:
            return {
                'status': 'no_pin',
                'message': 'No pinned message found in this channel'
            }

        # Extract pinned message information
        pinned = chat.pinned_message

        # Create base message info
        message_info = {
            'status': 'success',
            'message_id': pinned.message_id,
            'date': datetime.fromtimestamp(pinned.date),
            'type': pinned.content_type,
            'channel_name': chat.title,
            'message_link': f"https://t.me/{chat.username}/{pinned.message_id}" if chat.username else None
        }

        # Add sender information if available
        if pinned.from_user:
            message_info['from_user'] = {
                'username': pinned.from_user.username,
                'first_name': pinned.from_user.first_name,
                'last_name': pinned.from_user.last_name
            }

        if pinned.content_type == 'document':
            message_info['file_id'] = pinned.document.file_id
            message_info['file_name'] = pinned.document.file_name
            message_info['caption'] = pinned.caption
            message_info['size'] = pinned.document.file_size

        # You can add more types as needed

        return message_info

    except Exception as e:
        return {
            'status': 'error',
            'message': f'General Error: {str(e)}'
        }


def download_pinned_media(bot, bot_token, channel_id, download_path = './'):
    """
    Download media from pinned message if it exists.

    Parameters:
    bot_token (str): Your Telegram bot token
    channel_id (str): Channel username or ID
    download_path (str): Path to save the downloaded file

    Returns:
    dict: Information about the download
    """
    try:
        pinned_info = get_pinned_message(bot, channel_id)
        if pinned_info['status'] == 'success':
            print("\nPinned Message Details:")
            print(f"Type: {pinned_info['type']}")
            print(f"Date: {pinned_info['date']}")

            if pinned_info['type'] in ['document']:
                print(f"Caption: {pinned_info.get('caption', 'No caption')}")
        else:
            return f"Error: {pinned_info['message']}"

        if pinned_info['status'] != 'success':
            return pinned_info

        if pinned_info['type'] == 'document':
            file_info = bot.get_file(pinned_info['file_id'])
            downloaded_file = bot.download_file(file_info.file_path)
            file_path = f"{download_path}{pinned_info['file_name']}"

        else:
            return {
                'status': 'error',
                'message': 'No downloadable JSON in pinned message'
            }

        with open(file_path, 'wb') as new_file:
            new_file.write(downloaded_file)

        return {
            'status': 'success',
            'message': 'Media downloaded successfully',
            'file_path': file_path
        }

    except Exception as e:
        return {
            'status': 'error',
            'message': f'Download Error: {str(e)}'
        }

# טעינת הקובץ למאגר
def load_catalog_from_json(json_file_path):
    with open(json_file_path, 'r', encoding='utf-8') as file:
        catalog = json.load(file)
    return catalog
