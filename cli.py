from api.openai import OpenAIClient
from api.blogger import BloggerClient
from api.config.app import OPENAI_API_KEY, OPENAI_API_URL
from api.system_pormt import SystemPrompt


client = OpenAIClient(
    api_key=OPENAI_API_KEY,
    base_url=OPENAI_API_URL
)
blogger_client = BloggerClient()
system_prompt_client = SystemPrompt()


def generate_article():
    user_prompt = input("Masukkan prompt artikel: ").strip()
    if not user_prompt:
        print({
            "status": "error",
            "message": "Prompt artikel tidak boleh kosong",
        })
        return

    prompt_result = system_prompt_client.getSystemPrompt("CONTENT_WRITER.md")
    if not isinstance(prompt_result, dict) or prompt_result.get("status") != "success":
        print(prompt_result)
        return

    system_prompt = prompt_result.get("data", "")
    result = client.generateText(user_prompt=user_prompt, system_prompt=system_prompt)
    print(result)


def check_blogger_credential_status():
    result = blogger_client.get_credential_status()
    print(result)


print("""=== Blogger Agent Writer Specialist ===
Pilih opsi:
1. Cek status Blogger credential
2. Generate artikel
q. Keluar
""")

while True:
    user_input = input("Masukkan pilihan Anda: ").strip().lower()

    if user_input == "1":
        check_blogger_credential_status()
    elif user_input == "2":
        generate_article()
    elif user_input == "q":
        print("Selesai.")
        break
    else:
        print({
            "status": "error",
            "message": "Pilihan tidak valid",
            "data": {"available_options": ["1", "2", "q"]},
        })

