from pathlib import Path
import os


BASE_DIR = Path(__file__).resolve().parent.parent.parent


def _load_dotenv():
	env_path = BASE_DIR / '.env'
	if not env_path.exists():
		return

	for raw_line in env_path.read_text(encoding='utf-8').splitlines():
		line = raw_line.strip()
		if not line or line.startswith('#') or '=' not in line:
			continue

		key, value = line.split('=', 1)
		key = key.strip()
		value = value.strip().strip('"').strip("'")

		if key and key not in os.environ:
			os.environ[key] = value


_load_dotenv()

OPENAI_API_URL = os.getenv('OPENAI_API_URL', 'https://api.openai.com/v1')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
BLOG_ID = os.getenv('BLOG_ID', '')


