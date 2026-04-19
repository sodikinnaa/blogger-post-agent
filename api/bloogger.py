import httplib2
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run_flow
from googleapiclient import discovery
from googleapiclient.errors import HttpError
import time

def create_storage():
    autorze_crendentals()
    print('create storage')
    return 'data'


def postToBlogger(payload, idBlog):
    service = getBloggerService()
    post = service.posts()

    while True:
        try:
            # insert = post.insert(blogId='4636102614400807013', body=payload).execute()
            insert = post.insert(blogId=idBlog, body=payload).execute()
            if insert:
                # print(f"Postingan berhasil diposting")
                print(f"Postingan ke-: ")

            break # Keluar dari loop jika posting berhasil
        except HttpError as e:
            if "rateLimitExceeded" in str(e):
                print(
                    "Batas kecepatan permintaan API telah terlampaui. Menunggu 5 detik sebelum mencoba lagi..."
                )
                time.sleep(5)
                continue # Coba lagi setelah penundaan 5 detik
            else:
                print(f"Terjadi kesalahan HTTP: {e}")
                break # Keluar dari loop jika ada kesalahan lain


def autorze_crendentals():
    CLIENT_SECRET = f"data/json/secret.json"
    SCOPE = "https://www.googleapis.com/auth/blogger"
    STORAGE = Storage(f"data/json/credentials.storage")

    credentials = STORAGE.get()
    if credentials is None or credentials.invalid:
        flow = flow_from_clientsecrets(CLIENT_SECRET, scope=SCOPE)
        http = httplib2.Http()
        credentials = run_flow(flow, STORAGE, http=http)
    return credentials


def getBloggerService():
    credentials = autorze_crendentals()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = "https://blogger.googleapis.com/$discovery/rest?version=v3"
    service = discovery.build(
        "blogger", "v3", http=http, discoveryServiceUrl=discoveryUrl
    )
    return service

payload = {
    "content": "Konten postingan di sini untuk waktu terjadwal",
    "title": "Posting data",
    "labels": ["informasi", "terjadwal", "posting"],
    "status": "DRAFT",  # Menyimpan sebagai draft terlebih dahulu
    # "published": "2024-11-15T10:00:00Z"  # Waktu UTC yang dijadwalkan
}



# postToBlogger(payload,"6996243353161849151")