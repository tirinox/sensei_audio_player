import getpass
import json
import os

import requests
import vk_api
from dotenv import load_dotenv
from vk_api.exceptions import AuthError

load_dotenv()

# Replace these with your actual VK credentials and group ID
# ACCESS_TOKEN = os.environ.get('VK_SERVER_KEY')
GROUP_ID = os.environ.get('VK_GROUP_ID')
VK_APP_ID = int(os.environ.get('VK_APP_ID'))
VK_CLIENT_SECRET = os.environ.get('VK_CLIENT_SECRET')

VK_LOGIN = os.environ.get('VK_LOGIN')
VK_PASSWORD = os.environ.get('VK_PASSWORD')

# Directory to save downloaded audio files
DOWNLOAD_DIR = 'vk_audios'


def auth_handler():
    """Handles two-factor authentication (if enabled)."""
    # Prompt the user to input the 2FA code
    code = input("Enter the 2FA code: ")
    return code, True  # True means the code was entered successfully


def captcha_handler(captcha):
    """Handles CAPTCHA challenges."""
    # Display CAPTCHA URL to the user and prompt for input
    print(f"CAPTCHA required: {captcha.get_url()}")
    captcha_key = input("Enter CAPTCHA code: ")
    return captcha.try_again(captcha_key)


VK_TOKEN_FILE = '.vk_access.json'


def load_vk_token(file=VK_TOKEN_FILE):
    """Load the VK access token from a file."""
    try:
        with open(file, 'r') as f:
            t = json.load(f)
            return t['access_token']
    except FileNotFoundError:
        return None


def save_vk_token(token, file=VK_TOKEN_FILE):
    """Save the VK access token to a file."""
    with open(file, 'w') as f:
        json.dump(token, f)


def get_vk_session(username, password):
    """Authenticate and return a VK session."""
    try:
        token = load_vk_token()
        if token:
            vk_session = vk_api.VkApi(
                token=token,
                app_id=VK_APP_ID, client_secret=VK_CLIENT_SECRET,
            )
        else:
            vk_session = vk_api.VkApi(
                login=username,
                password=password,
                scope='audio,groups',
                auth_handler=auth_handler,
                captcha_handler=captcha_handler,
                # app_id=VK_APP_ID,
                # client_secret=VK_CLIENT_SECRET,
                app_id=VK_APP_ID, client_secret=VK_CLIENT_SECRET
            )
            vk_session.auth()
        print("Authentication successful.")

        token = vk_session.token
        save_vk_token(token)

        return vk_session
    except AuthError as e:
        print(f"Authentication failed: {e}")
        return None


def get_group_audios(vk, group_id):
    """Retrieve audio tracks from the specified VK group."""
    try:
        response = vk.method('audio.get', {
            'owner_id': f'-{group_id}',  # Negative ID for groups
            'count': 10  # Maximum number of audios to retrieve
        })
        return response.get('items', [])
    except vk_api.exceptions.ApiError as e:
        print(f"An error occurred: {e}")
        return []


def download_audio(audio, download_dir):
    """Download a single audio file."""
    artist = audio.get('artist', 'Unknown Artist').replace('/', '_').replace('\\', '_')
    title = audio.get('title', 'Unknown Title').replace('/', '_').replace('\\', '_')
    url = audio.get('url')

    if not url:
        print(f"URL not found for {artist} - {title}")
        return

    file_name = f"{artist} - {title}.mp3"
    file_path = os.path.join(download_dir, file_name)

    if os.path.exists(file_path):
        print(f"Already exists: {file_name}")
        return

    try:
        print(f"Downloading: {file_name}")
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(1024):
                if chunk:
                    f.write(chunk)
        print(f"Downloaded: {file_name}")
    except requests.exceptions.RequestException as e:
        print(f"Failed to download {file_name}: {e}")


def main():
    # Prompt the user for VK credentials securely
    username = VK_LOGIN or input("Enter your VK username (phone/email): ")
    password = VK_PASSWORD or getpass.getpass("Enter your VK password: ")

    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)

    vk_session = get_vk_session(username, password)
    if not vk_session:
        print("Exiting due to authentication failure.")
        return

    # info = vk_session.method('account.getInfo')
    # print(info)

    audio = '-11_22'
    r = vk_session.method('audio.getById', {
        'ids': audio
    })
    print(r)

    # download_audio(audio, DOWNLOAD_DIR)

    # audios = get_group_audios(vk_session, GROUP_ID)
    # print(f"Found {len(audios)} audio tracks.")
    #
    # for audio in audios:
    #     download_audio(audio, DOWNLOAD_DIR)


if __name__ == "__main__":
    main()
