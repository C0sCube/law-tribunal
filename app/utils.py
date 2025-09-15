import os, re, json, string, random
from datetime import datetime
import unicodedata


class Helper:
    # ----------------------------
    # File + Directory Utilities
    # ----------------------------
    @staticmethod        
    def create_dirs(root_path: str, dirs: list) -> list:
        created_paths = []
        for dir_name in dirs:
            full_path = os.path.join(root_path, dir_name)
            os.makedirs(full_path, exist_ok=True)
            created_paths.append(full_path)
        return created_paths if len(created_paths) > 1 else created_paths[0]
    
    @staticmethod        
    def create_dir(root_path: str, *args) -> str:
        full_path = os.path.join(root_path, *args)
        os.makedirs(full_path, exist_ok=True)
        return full_path

    @staticmethod
    def create_path(path: str, *args) -> str:
        return os.path.join(path, *args)

    @staticmethod
    def read_file(filepath: str) -> str:
        with open(filepath, 'r', encoding="utf-8") as f:
            return f.read()

    @staticmethod
    def write_file(filepath: str, content: str):
        with open(filepath, 'w', encoding="utf-8") as f:
            f.write(content)

    @staticmethod
    def write_binary_file(filepath: str, binary_content: bytes):
        with open(filepath, 'wb') as f:
            f.write(binary_content)

    @staticmethod
    def get_file_extension(filename: str) -> str:
        return os.path.splitext(filename)[1]

    @staticmethod
    def delete_files_and_empty_folder(file_path: str) -> bool:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                parent_dir = os.path.dirname(file_path)
                if os.path.isdir(parent_dir) and not os.listdir(parent_dir):
                    os.rmdir(parent_dir)
                return True
            return False
        except Exception:
            return False


    # ----------------------------
    # JSON & Text Handling
    # ----------------------------
    @staticmethod
    def save_json(data: dict, path: str, indent: int = 2):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=indent)

    @staticmethod
    def load_json(path: str):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def save_text(data, path: str, mode='w'):
        if not data:
            raise ValueError("Empty data cannot be saved.")
        if mode not in ('w', 'a'):
            raise ValueError(f"Invalid mode '{mode}'. Use 'w' or 'a'.")
        
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, mode, encoding='utf-8') as f:
            if isinstance(data, dict):
                for k, v in data.items():
                    f.write(f"{k}:{v}\n")
            elif isinstance(data, list):
                for k in data:
                    f.write(f"{k}\n")
            elif isinstance(data, str):
                f.write(data)
            else:
                raise ValueError(f"Invalid data type: {type(data)}")


    # ----------------------------
    # String Normalization + Validation
    # ----------------------------
    @staticmethod
    def is_numeric(text):
        return bool(re.fullmatch(r'[+-]?(\d+(\.\d*)?|\.\d+)', text))

    @staticmethod
    def is_alphanumeric(text):
        return bool(re.fullmatch(r'[A-Za-z0-9]+', text))

    @staticmethod
    def is_alpha(text):
        return bool(re.fullmatch(r'[A-Za-z]+', text))

    @staticmethod
    def _normalize_whitespace(text: str) -> str:
        return re.sub(r"\s+", " ", text).strip() if isinstance(text, str) else text
    
    @staticmethod
    def _normalize_alphanumeric(text: str) -> str:
        if not isinstance(text, str):
            return text
        text = re.sub(r"[^a-zA-Z0-9]+", " ", str(text))
        return re.sub(r"\s+", " ", text).strip().lower()
    
    @staticmethod
    def _normalize_alpha(text: str) -> str:
        if not isinstance(text, str):
            return text
        text = re.sub(r"[^a-zA-Z]+", " ", str(text))
        return re.sub(r"\s+", " ", text).strip().lower()

    @staticmethod
    def _normalize_numeric(text: str) -> str:
        if not isinstance(text, str):
            return text
        text = re.sub(r"[^0-9\.]+", " ", str(text))
        return re.sub(r"\s+", " ", text).strip().lower()

    @staticmethod
    def snake_case(text: str) -> str:
        text = re.sub(r'([A-Z]+)', r' \1', text).strip()
        return re.sub(r'[_\s-]+', '_', text).lower()

    @staticmethod
    def camel_case(text: str) -> str:
        text = re.sub(r'[_\s-]+', ' ', text)
        text = text.title()
        return text[0].lower() + text[1:].replace(' ', '')

    @staticmethod
    def sanitize_Win_filename(name):
        return re.sub(r'[<>:"/\\|?*]', '_', name)

    @staticmethod
    def fix_mojibake(text: str) -> str:
        try:
            return text.encode("latin1").decode("utf-8")
        except:
            return text


    # ----------------------------
    # List Utilities
    # ----------------------------
    @staticmethod
    def chunk_list(data: list, size: int):
        return [data[i:i + size] for i in range(0, len(data), size)]

    @staticmethod
    def flatten_list(list_of_lists: list):
        return [item for sublist in list_of_lists for item in sublist]
    
    @staticmethod
    def remove_duplicates(data: list):
        return list(dict.fromkeys(data))


    # ----------------------------
    # Time / IDs
    # ----------------------------
    @staticmethod
    def get_timestamp(sep=":"):
        now = datetime.now()
        return now.strftime(f"%H{sep}%M{sep}%S")

    @staticmethod
    def generate_uid(segment_count=3, segment_length=3):
        segments = [
            ''.join(random.choices(string.ascii_uppercase, k=segment_length))
            for _ in range(segment_count)
        ]
        return '-'.join(segments)
