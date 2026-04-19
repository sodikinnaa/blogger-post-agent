from pathlib import Path

from api.response.response_template import response_template


class SystemPrompt:
	def __init__(self, prompt_dir='promt'):
		self.base_dir = Path(__file__).resolve().parent.parent
		self.prompt_dir = self.base_dir / prompt_dir

	def _resolve_prompt_path(self, file_name):
		return self.prompt_dir / file_name

	def getWriterPrompt(self):
		prompt_path = self._resolve_prompt_path('CONTENT_WRITER.md')

		if not prompt_path.exists():
			return response_template(
				status='error',
				message=f'File prompt tidak ditemukan: {prompt_path}',
				data='',
				meta={
					'prompt_name': 'CONTENT_WRITER.md',
					'prompt_path': str(prompt_path),
				},
			)

		content = prompt_path.read_text(encoding='utf-8')
		return response_template(
			status='success',
			message='System prompt writer berhasil diambil',
			data=content,
			meta={
				'prompt_name': 'CONTENT_WRITER.md',
				'prompt_path': str(prompt_path),
				'content_length': len(content),
			},
		)

	def getSystemPrompt(self, file_name):
		prompt_path = self._resolve_prompt_path(file_name)

		if not prompt_path.exists():
			return response_template(
				status='error',
				message=f'File prompt tidak ditemukan: {prompt_path}',
				data='',
				meta={
					'prompt_name': file_name,
					'prompt_path': str(prompt_path),
				},
			)

		content = prompt_path.read_text(encoding='utf-8')
		return response_template(
			status='success',
			message='System prompt berhasil diambil',
			data=content,
			meta={
				'prompt_name': file_name,
				'prompt_path': str(prompt_path),
				'content_length': len(content),
			},
		)
