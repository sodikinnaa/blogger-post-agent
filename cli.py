from api.openai import OpenAIClient
from api.blogger import BloggerClient
from api.config.app import BLOG_ID, OPENAI_API_KEY, OPENAI_API_URL
from api.system_pormt import SystemPrompt
import json

client = OpenAIClient(
    api_key=OPENAI_API_KEY,
    base_url=OPENAI_API_URL
)
blogger_client = BloggerClient()
system_prompt_client = SystemPrompt()


def _extract_generated_article(result):
    if not isinstance(result, dict) or result.get("status") != "success":
        return None

    data = result.get("data", {})
    output_json = data.get("output_json")

    if isinstance(output_json, list) and output_json:
        first_item = output_json[0]
        if isinstance(first_item, dict):
            return first_item

    if isinstance(output_json, dict):
        return output_json

    return None


def _build_blogger_payload(article):
    if not isinstance(article, dict):
        return None

    title = article.get("title", "")
    content = article.get("content", "")
    labels = article.get("labels", [])
    status = article.get("status", "DRAFT")
    meta_description = article.get("meta_description", "")
    thumbnail_url = article.get("thumbnail_url", "")

    if not isinstance(labels, list):
        labels = []

    if not title or not content:
        return None

    content_parts = []
    if thumbnail_url:
        content_parts.append(
            f'<img src="{thumbnail_url}" alt="{title}" style="max-width:100%;height:auto;aspect-ratio:16/9;object-fit:cover;" />'
        )
    if meta_description:
        content_parts.append(f"<!-- meta_description: {meta_description} -->")
    content_parts.append(content)

    return {
        "title": title,
        "content": "\n".join(content_parts),
        "labels": labels,
        "status": status.upper(),
    }


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
    generated_article = _extract_generated_article(result)
    if not generated_article:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return

    blogger_payload = _build_blogger_payload(generated_article)
    if not blogger_payload:
        print(
            json.dumps(
                {
                    "status": "error",
                    "message": "Hasil generate artikel tidak valid untuk diposting ke Blogger",
                    "data": {
                        "generated_article": generated_article,
                    },
                },
                indent=2,
                ensure_ascii=False,
            )
        )
        return

    publish_result = blogger_client.post_to_blogger(
        payload=blogger_payload,
        blog_id=BLOG_ID,
    )
    print(
        json.dumps(
            {
                "generate_result": result,
                "publish_result": publish_result,
            },
            indent=2,
            ensure_ascii=False,
        )
    )


def check_blogger_credential_status():
    result = blogger_client.get_credential_status()
    print(json.dumps(result, indent=2, ensure_ascii=False))

while True:
    print("""=== Blogger Agent Writer Specialist ===
Pilih opsi:
1. Cek status Blogger credential
2. Generate artikel
q. Keluar
""")

    user_input = input("Masukkan pilihan Anda: ").strip().lower()

    if user_input == "1":
        check_blogger_credential_status()
    elif user_input == "2":
        generate_article()
    elif user_input == "q":
        print("Selesai.")
        break
    else:
        print(json.dumps({
            "status": "error",
            "message": "Pilihan tidak valid",
            "data": {"available_options": ["1", "2", "q"]},
        }, indent=2, ensure_ascii=False))

