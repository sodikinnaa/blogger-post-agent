from api.openai import OpenAIClient 
from api.sheet_db import SheetDB
from config.app import BLOGGER_KEY, BLOGGER_URL, OPENAI_API_KEY, OPENAI_API_URL, BLOG_ID, BLOGGER_KEY
from api.system_pormt import SystemPrompt
from api.blogs import BlogAPI
import json


client_ai = OpenAIClient(
    api_key=OPENAI_API_KEY,
    base_url=OPENAI_API_URL
)

get_promt = SystemPrompt()


def _extract_generated_record(result):
    if not isinstance(result, dict) or result.get('status') != 'success':
        return None

    data = result.get('data', {})
    output_json = data.get('output_json')

    if isinstance(output_json, list) and output_json:
        first_item = output_json[0]
        if isinstance(first_item, dict):
            return first_item

    if isinstance(output_json, dict):
        return output_json

    return None


def _build_sheet_payload(record, content_columns):
    if not isinstance(record, dict):
        return {}

    normalized = dict(record)

    # Handle common key typo from prompts/models.
    if 'target_audiens' in normalized and 'target_audience' not in normalized:
        normalized['target_audience'] = normalized.get('target_audiens', '')

    return {column: normalized.get(column, '') for column in content_columns}

print('''

======================================================
Blogger Posting - CLI Version : {}
======================================================
masukan pilihan anda 
      1. Generate Text
      2. Get Sheet Data
      3. Insert Content Data
      4. Get Blog Detail
      5. Posting ke Blogger 
      q. Quit
            
      ''')

while True:
    choice = input('Masukan pilihan: ').strip().lower()

    if choice == '1':
        db_data = SheetDB()
        user_prompt = input('Masukan prompt untuk AI: ')
        system_prompt_result = get_promt.getSystemPrompt('CONTENT_WRITER.md')
        system_prompt = None
        if isinstance(system_prompt_result, dict) and system_prompt_result.get('status') == 'success':
            system_prompt = system_prompt_result.get('data')
        result = client_ai.generateText(user_prompt, system_prompt)
        meta = result.get('meta', {}) if isinstance(result, dict) else {}
        if not isinstance(meta, dict):
            meta = {}

        generated_record = _extract_generated_record(result)
        if not generated_record:
            meta['spreadsheet_save'] = {
                'status': 'skipped',
                'message': 'Auto insert ke sheet dilewati: output_json AI tidak valid atau kosong.',
            }
            result['meta'] = meta
            print(json.dumps(result, indent=2, ensure_ascii=False))
            continue

        payload = _build_sheet_payload(generated_record, db_data.content_columns)
        if not any(payload.values()):
            meta['spreadsheet_save'] = {
                'status': 'skipped',
                'message': 'Auto insert ke sheet dilewati: data hasil AI tidak memuat kolom yang dibutuhkan.',
                'required_columns': db_data.content_columns,
            }
            result['meta'] = meta
            print(json.dumps(result, indent=2, ensure_ascii=False))
            continue

        insert_output = db_data.insertContentData(payload)
        meta['spreadsheet_save'] = {
            'status': 'saved' if insert_output.get('status') == 'success' else 'failed',
            'message': insert_output.get('message', ''),
            'sheet_name': db_data.sheet_name,
            'response_status': insert_output.get('status', ''),
        }
        result['meta'] = meta
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif choice == '2':
        db_data = SheetDB()
        output = db_data.getSheetData()
        print(json.dumps(output, indent=2, ensure_ascii=False))

    elif choice == '3':
        db_data = SheetDB()
        payload = {
            'id-website': input('id-website: '),
            'topik': input('topik: '),
            'tanggal_create': input('tanggal_create: '),
            'target_audience': input('target_audience: '),
            'category': input('category: '),
            'keyword': input('keyword: '),
            'judul': input('judul: '),
            'meta_description': input('meta_description: '),
            'aff_link': input('aff_link: '),
            'content': input('content: '),
            'thumbnail_url': input('thumbnail_url: '),
            'status': input('status: '),
            'tanggal_publish': input('tanggal_publish: '),
            'url_publish': input('url_publish: '),
        }
        output = db_data.insertContentData(payload)
        print(json.dumps(output, indent=2, ensure_ascii=False))

    elif choice == '4':
        print('Mengambil detail blog...')
        blog_api = BlogAPI(
            api_url=BLOGGER_URL,
            api_key=BLOGGER_KEY
        )

        blog_details = blog_api.getDetailBlog(BLOG_ID)
        print(json.dumps(blog_details, indent=2, ensure_ascii=False))

    elif choice == '5':
        blog_api = BlogAPI(
            api_url=BLOGGER_URL,
            api_key=BLOGGER_KEY,
            blog_id=BLOG_ID
        )

        post = blog_api.createPost(content_data=[], api_key=BLOGGER_KEY, blog_id=BLOG_ID)
        print(json.dumps(post, indent=2, ensure_ascii=False))
    elif choice == 'q':
        print('Terima kasih telah menggunakan Blogger Posting CLI. Sampai jumpa!')
        break

    else:
        print('Pilihan tidak valid. Silakan coba lagi.')