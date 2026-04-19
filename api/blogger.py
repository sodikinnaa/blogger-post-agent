from pathlib import Path
import time

import httplib2
from googleapiclient import discovery
from googleapiclient.errors import HttpError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run_flow

from api.response.response_template import response_template


class BloggerClient:
    SCOPE = "https://www.googleapis.com/auth/blogger"
    DISCOVERY_URL = "https://blogger.googleapis.com/$discovery/rest?version=v3"

    def __init__(self, secret_path=None, credential_path=None, retry_delay=5):
        base_path = Path(__file__).resolve().parent
        credential_dir = base_path / "credential/blogs"
        self.secret_path = Path(secret_path or credential_dir / "secret.json")
        self.credential_path = Path(
            credential_path or credential_dir / "credentials.storage"
        )
        self.retry_delay = retry_delay

    def _meta(self, operation, blog_id=None, extra=None):
        meta = {
            "provider": "blogger",
            "operation": operation,
            "secret_path": str(self.secret_path),
            "credential_path": str(self.credential_path),
        }
        if blog_id:
            meta["blog_id"] = blog_id
        if extra:
            meta.update(extra)
        return meta

    def create_storage(self):
        try:
            self.credential_path.parent.mkdir(parents=True, exist_ok=True)
            self.authorize_credentials()
            return response_template(
                status="success",
                message="Storage credential berhasil dibuat",
                data={
                    "credential_path": str(self.credential_path),
                },
                meta=self._meta("storage.create"),
            )
        except Exception as error:
            return response_template(
                status="error",
                message=str(error),
                data={},
                meta=self._meta(
                    "storage.create",
                    extra={"exception_type": type(error).__name__},
                ),
            )

    def get_credential_status(self):
        secret_exists = self.secret_path.exists()
        storage_exists = self.credential_path.exists()

        data = {
            "secret_file_exists": secret_exists,
            "credential_storage_exists": storage_exists,
            "secret_path": str(self.secret_path),
            "credential_path": str(self.credential_path),
            "is_authorized": False,
        }

        if not secret_exists:
            return response_template(
                status="error",
                message="Secret file Blogger belum tersedia",
                data=data,
                meta=self._meta("credentials.status"),
            )

        try:
            credentials = self.authorize_credentials()
            data["is_authorized"] = bool(credentials and not credentials.invalid)
            return response_template(
                status="success",
                message="Status credential Blogger berhasil diperiksa",
                data=data,
                meta=self._meta("credentials.status"),
            )
        except Exception as error:
            return response_template(
                status="error",
                message=str(error),
                data=data,
                meta=self._meta(
                    "credentials.status",
                    extra={"exception_type": type(error).__name__},
                ),
            )

    def authorize_credentials(self):
        self.credential_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.secret_path.exists():
            raise FileNotFoundError(
                f"Secret file tidak ditemukan di {self.secret_path}"
            )

        storage = Storage(str(self.credential_path))
        credentials = storage.get()

        if credentials is None or credentials.invalid:
            flow = flow_from_clientsecrets(str(self.secret_path), scope=self.SCOPE)
            http = httplib2.Http()
            credentials = run_flow(flow, storage, http=http)

        return credentials

    def get_service(self):
        credentials = self.authorize_credentials()
        http = credentials.authorize(httplib2.Http())
        return discovery.build(
            "blogger",
            "v3",
            http=http,
            discoveryServiceUrl=self.DISCOVERY_URL,
        )

    def post_to_blogger(self, payload, blog_id):
        try:
            service = self.get_service()
            posts = service.posts()

            while True:
                insert = posts.insert(blogId=blog_id, body=payload).execute()
                if insert:
                    return response_template(
                        status="success",
                        message="Postingan berhasil diposting",
                        data=insert,
                        meta=self._meta(
                            "posts.insert",
                            blog_id=blog_id,
                            extra={
                                "payload_status": payload.get("status"),
                                "label_count": len(payload.get("labels", [])),
                            },
                        ),
                    )
            return response_template(
                status="error",
                message="Postingan gagal diproses",
                data={},
                meta=self._meta("posts.insert", blog_id=blog_id),
            )
        except HttpError as error:
            while True:
                if "rateLimitExceeded" in str(error):
                    print(
                        "Batas kecepatan permintaan API telah terlampaui. Menunggu 5 detik sebelum mencoba lagi..."
                    )
                    time.sleep(self.retry_delay)
                    try:
                        service = self.get_service()
                        posts = service.posts()
                        insert = posts.insert(blogId=blog_id, body=payload).execute()
                        return response_template(
                            status="success",
                            message="Postingan berhasil diposting setelah retry",
                            data=insert,
                            meta=self._meta(
                                "posts.insert",
                                blog_id=blog_id,
                                extra={
                                    "retried": True,
                                    "payload_status": payload.get("status"),
                                    "label_count": len(payload.get("labels", [])),
                                },
                            ),
                        )
                    except HttpError as retry_error:
                        error = retry_error
                        continue

                return response_template(
                    status="error",
                    message=str(error),
                    data={},
                    meta=self._meta(
                        "posts.insert",
                        blog_id=blog_id,
                        extra={
                            "exception_type": type(error).__name__,
                            "payload_status": payload.get("status"),
                            "label_count": len(payload.get("labels", [])),
                        },
                    ),
                )
        except Exception as error:
            return response_template(
                status="error",
                message=str(error),
                data={},
                meta=self._meta(
                    "posts.insert",
                    blog_id=blog_id,
                    extra={
                        "exception_type": type(error).__name__,
                        "payload_status": payload.get("status"),
                        "label_count": len(payload.get("labels", [])),
                    },
                ),
            )