from pathlib import Path
import sys
import time

import httplib2
from googleapiclient import discovery
from googleapiclient.errors import HttpError
from oauth2client.client import HttpAccessTokenRefreshError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run_flow

from api.response.response_template import response_template


def _get_runtime_base_dir():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


class BloggerClient:
    SCOPE = "https://www.googleapis.com/auth/blogger"
    DISCOVERY_URL = "https://blogger.googleapis.com/$discovery/rest?version=v3"

    def __init__(self, secret_path=None, credential_path=None, retry_delay=5):
        base_path = _get_runtime_base_dir()
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
            self.authorize_credentials(force_reauth=True)
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

    def get_credential_status(self, auto_authorize=False):
        secret_exists = self.secret_path.exists()
        storage_exists = self.credential_path.exists()

        data = {
            "secret_file_exists": secret_exists,
            "credential_storage_exists": storage_exists,
            "secret_path": str(self.secret_path),
            "credential_path": str(self.credential_path),
            "is_authorized": False,
            "needs_reauthorization": False,
        }

        if not secret_exists:
            return response_template(
                status="error",
                message="Secret file Blogger belum tersedia",
                data=data,
                meta=self._meta("credentials.status"),
            )

        if not auto_authorize:
            if storage_exists:
                data["is_authorized"] = True
                return response_template(
                    status="success",
                    message="File credential Blogger ditemukan",
                    data=data,
                    meta=self._meta("credentials.status"),
                )

            data["needs_reauthorization"] = True
            return response_template(
                status="warning",
                message="Credential storage belum tersedia. Jalankan otorisasi Blogger saat diperlukan.",
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
        except HttpAccessTokenRefreshError as error:
            data["needs_reauthorization"] = True
            return self._build_reauth_response("credentials.status", error)
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

    def _delete_credential_storage(self):
        if self.credential_path.exists():
            self.credential_path.unlink()

    def authorize_credentials(self, force_reauth=False):
        self.credential_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.secret_path.exists():
            raise FileNotFoundError(
                f"Secret file tidak ditemukan di {self.secret_path}"
            )

        if force_reauth:
            self._delete_credential_storage()
            storage = Storage(str(self.credential_path))
            flow = flow_from_clientsecrets(str(self.secret_path), scope=self.SCOPE)
            http = httplib2.Http()
            return run_flow(flow, storage, http=http)

        storage = Storage(str(self.credential_path))
        credentials = storage.get()

        if credentials is None or credentials.invalid:
            flow = flow_from_clientsecrets(str(self.secret_path), scope=self.SCOPE)
            http = httplib2.Http()
            credentials = run_flow(flow, storage, http=http)

        return credentials

    def _build_reauth_response(self, operation, error, blog_id=None, payload=None):
        return response_template(
            status="error",
            message=(
                "Credential Blogger tidak valid atau sudah kedaluwarsa. "
                "Hapus file credentials.storage lalu otorisasi ulang aplikasi."
            ),
            data={},
            meta=self._meta(
                operation,
                blog_id=blog_id,
                extra={
                    "exception_type": type(error).__name__,
                    "original_error": str(error),
                    "payload_status": payload.get("status") if isinstance(payload, dict) else None,
                    "label_count": len(payload.get("labels", [])) if isinstance(payload, dict) else 0,
                },
            ),
        )

    def get_service(self):
        try:
            credentials = self.authorize_credentials()
            http = credentials.authorize(httplib2.Http())
            return discovery.build(
                "blogger",
                "v3",
                http=http,
                discoveryServiceUrl=self.DISCOVERY_URL,
            )
        except HttpAccessTokenRefreshError:
            credentials = self.authorize_credentials(force_reauth=True)
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
        except HttpAccessTokenRefreshError as error:
            return self._build_reauth_response(
                "posts.insert",
                error,
                blog_id=blog_id,
                payload=payload,
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