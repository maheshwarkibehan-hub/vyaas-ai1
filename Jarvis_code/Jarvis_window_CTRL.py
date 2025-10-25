import os
import subprocess
import logging
import sys
import asyncio
from fuzzywuzzy import process

try:
    from livekit.agents import function_tool
except ImportError:
    def function_tool(func): 
        return func

try:
    import win32gui
    import win32con
except ImportError:
    win32gui = None
    win32con = None

try:
    import pygetwindow as gw
except ImportError:
    gw = None

# Setup encoding and logger
sys.stdout.reconfigure(encoding='utf-8')
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- APP MAPPINGS ---
APP_MAPPINGS = {
    "notepad": "notepad",
    "calculator": "calc",
    "chrome": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
    "vlc": "C:\\Program Files\\VideoLAN\\VLC\\vlc.exe",
    "command prompt": "cmd",
    "control panel": "control",
    "settings": "start ms-settings:",
    "paint": "mspaint",
    "vs code": "C:\\Users\\gaura\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe",
    "postman": "C:\\Users\\gaura\\AppData\\Local\\Postman\\Postman.exe",
    "youtube": "https://www.youtube.com",
    "play youtube": "https://www.youtube.com/results?search_query="
}

# --- Global focus utility ---
async def focus_window(title_keyword: str) -> bool:
    if not gw:
        logger.warning("⚠ pygetwindow")
        return False

    await asyncio.sleep(1.5)
    title_keyword = title_keyword.lower().strip()

    for window in gw.getAllWindows():
        if title_keyword in window.title.lower():
            if window.isMinimized:
                window.restore()
            window.activate()
            return True
    return False

# --- App control - open_app function ---
@function_tool()
async def open_app(app_title: str) -> str:
    app_title_lower = app_title.lower().strip()

    # Handle YouTube
    if "youtube" in app_title_lower:
        search_query = app_title_lower.replace("youtube", "").replace("play", "").strip()
        url = APP_MAPPINGS["youtube"] if not search_query else f"https://www.youtube.com/results?search_query={search_query.replace(' ', '+')}&sp=EgIQAQ%3D%3D&autoplay=1"
        try:
            await asyncio.create_subprocess_shell(f'start "" "{url}"', shell=True)
            await focus_window("youtube")
            return f"🎵 YouTube open: {search_query or 'Home'}"
        except Exception as e:
            return f"❌ YouTube open failed: {e}"

    # Regular apps
    app_command = APP_MAPPINGS.get(app_title_lower, app_title_lower)
    try:
        await asyncio.create_subprocess_shell(f'start "" "{app_command}"', shell=True)
        focused = await focus_window(app_title_lower)
        return f"🚀 App launched: {app_title}" if focused else f"🚀 {app_title} launched, but not focused."
    except Exception as e:
        return f"❌ {app_title} launch failed: {e}"

# --- System Control: Shutdown / Restart / Logoff / Sleep ---
@function_tool()
async def vyaas_system_control(command: str) -> str:
    """
    System control by Vyaas assistant.
    Supports shutdown, restart, logoff, sleep.
    """
    command_lower = command.lower()
    if "shutdown" in command_lower:
        os.system("shutdown /s /t 3")
        return "✅ Vyaas: System will shutdown in 3 seconds."
    elif "restart" in command_lower:
        os.system("shutdown /r /t 3")
        return "✅ Vyaas: System will restart in 3 seconds."
    elif "log off" in command_lower or "sign out" in command_lower:
        os.system("shutdown /l")
        return "✅ Vyaas: Logging off now."
    elif "sleep" in command_lower or "hibernate" in command_lower:
        os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
        return "✅ Vyaas: System going to sleep."
    else:
        return "❌ Vyaas: Command not recognized. Use shutdown, restart, log off, or sleep."

# --- Index and File/Folder Operations ---
async def index_items(base_dirs):
    item_index = []
    for base_dir in base_dirs:
        for root, dirs, files in os.walk(base_dir):
            for d in dirs:
                item_index.append({"name": d, "path": os.path.join(root, d), "type": "folder"})
            for f in files:
                item_index.append({"name": f, "path": os.path.join(root, f), "type": "file"})
    logger.info(f"✅ Indexed {len(item_index)} items.")
    return item_index

async def search_item(query, index, item_type):
    filtered = [item for item in index if item["type"] == item_type]
    choices = [item["name"] for item in filtered]
    if not choices:
        return None
    best_match, score = process.extractOne(query, choices)
    logger.info(f"🔍 Matched '{query}' to '{best_match}' with score {score}")
    if score > 70:
        for item in filtered:
            if item["name"] == best_match:
                return item
    return None

async def open_folder(path):
    try:
        os.startfile(path)
        await focus_window(os.path.basename(path))
    except Exception as e:
        logger.error(f"❌ Error opening folder: {e}")

async def play_file(path):
    try:
        os.startfile(path)
        await focus_window(os.path.basename(path))
    except Exception as e:
        logger.error(f"❌ Error opening file: {e}")

async def create_folder(path):
    try:
        os.makedirs(path, exist_ok=True)
        return f"✅ Folder created: {path}"
    except Exception as e:
        return f"❌ Folder creation failed: {e}"

async def rename_item(old_path, new_path):
    try:
        os.rename(old_path, new_path)
        return f"✅ Renamed to: {new_path}"
    except Exception as e:
        return f"❌ Rename failed: {e}"

async def delete_item(path):
    try:
        if os.path.isdir(path):
            os.rmdir(path)
        else:
            os.remove(path)
        return f"🗑️ Deleted: {path}"
    except Exception as e:
        return f"❌ Delete failed: {e}"

# --- Close App ---
@function_tool()
async def close_app(window_title: str) -> str:
    if not win32gui:
        return "❌ win32gui missing."
    def enumHandler(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            if window_title.lower() in win32gui.GetWindowText(hwnd).lower():
                win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
    win32gui.EnumWindows(enumHandler, None)
    return f"✅ Window closed: {window_title}"

# --- Folder/File command logic ---
@function_tool()
async def folder_file(command: str) -> str:
    folders_to_index = ["D:/"]
    index = await index_items(folders_to_index)
    command_lower = command.lower()

    if "create folder" in command_lower:
        folder_name = command.replace("create folder", "").strip()
        path = os.path.join("D:/", folder_name)
        return await create_folder(path)

    if "rename" in command_lower:
        parts = command_lower.replace("rename", "").strip().split("to")
        if len(parts) == 2:
            old_name = parts[0].strip()
            new_name = parts[1].strip()
            item = await search_item(old_name, index, "folder")
            if item:
                new_path = os.path.join(os.path.dirname(item["path"]), new_name)
                return await rename_item(item["path"], new_path)
        return "❌ rename command invalid."

    if "delete" in command_lower:
        item = await search_item(command, index, "folder") or await search_item(command, index, "file")
        if item:
            return await delete_item(item["path"])
        return "❌ Delete item not found."

    if "folder" in command_lower or "open folder" in command_lower:
        item = await search_item(command, index, "folder")
        if item:
            await open_folder(item["path"])
            return f"✅ Folder opened: {item['name']}"
        return "❌ Folder not found."

    item = await search_item(command, index, "file")
    if item:
        await play_file(item["path"])
        return f"✅ File opened: {item['name']}"

    return "⚠ No match found."
