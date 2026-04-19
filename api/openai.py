from openai import OpenAI
import json
from api.response.response_template import response_template

class OpenAIClient:
    def __init__(self, api_key, base_url):
        self.client = OpenAI(base_url=base_url,api_key=api_key)

    def _response_to_dict(self, response):
        output_text = getattr(response, 'output_text', '')

        if not isinstance(output_text, str) or not output_text.strip():
            if hasattr(response, 'model_dump'):
                return response.model_dump()
            return {}

        text = output_text.strip()

        # Handle output wrapped in markdown code fences.
        if text.startswith('```') and text.endswith('```'):
            lines = text.splitlines()
            if len(lines) >= 3:
                text = '\n'.join(lines[1:-1]).strip()

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # Fallback: try to parse the first JSON object/array found in text.
            first_obj = text.find('{')
            first_arr = text.find('[')
            starts = [idx for idx in [first_obj, first_arr] if idx != -1]

            if not starts:
                return {'raw_output_text': output_text}

            start = min(starts)
            end_obj = text.rfind('}')
            end_arr = text.rfind(']')
            end = max(end_obj, end_arr)

            if end <= start:
                return {'raw_output_text': output_text}

            candidate = text[start:end + 1]
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                return {'raw_output_text': output_text}
    
    def generateText(self, user_prompt, system_prompt=None, model="gpt-5.4"):
        try:
            input_payload = user_prompt
            system_prompt_used = isinstance(system_prompt, str) and bool(system_prompt.strip())
            if system_prompt_used:
                input_payload = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ]

            response = self.client.responses.create(
                model=model,
                input=input_payload,
            )

            return response_template(
                status='success',
                message='Generate text berhasil',
                data={
                    'output_json': self._response_to_dict(response),
                    'id': response.id,
                    'model': response.model,
                },
                meta={
                    'provider': 'openai',
                    'operation': 'responses.create',
                    'system_promt_used': system_prompt_used,
                },
            )
        except Exception as err:
            return response_template(
                status='error',
                message=str(err),
                data={},
                meta={
                    'provider': 'openai',
                    'operation': 'responses.create',
                },
            )

    def generateTextWithTolls(self):
        return response_template(
            status='error',
            message='Fitur generateTextWithTolls belum diimplementasikan',
            data={},
            meta={
                'provider': 'openai',
                'operation': 'generateTextWithTolls',
            },
        )