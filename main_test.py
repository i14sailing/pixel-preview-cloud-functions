
import main
import os
from secrets import MONGO_DB_CONNECTION_STRING
import certifi
from pymongo import MongoClient

# Put the service-account.json within the same directory!
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "service-account.json"
os.environ["MONGO_DB_CONNECTION_STRING"] = MONGO_DB_CONNECTION_STRING
os.environ["ENVIRONMENT"] = "development"

# Set correct SSL certificate
os.environ['SSL_CERT_FILE'] = certifi.where()

client = MongoClient(os.getenv('MONGO_DB_CONNECTION_STRING'))
cms_database = client.get_database('strapi')
upload_collection = cms_database['upload_file']


def test_process_image():
    bucket_name = 'i14-worlds-2021-upload'
    src_file_name = 'AC75AmericanMagic_d41dbb268a/Int-14-Day-7-5b.jpg'
    main.process_image(bucket_name, src_file_name)


def manual_processing():
    file_records = upload_collection.find()
    file_urls = []

    for record in file_records:
        file_urls.append(record["url"])
        if "formats" in record:
            try:
                for size in ["thumbnail", "small", "medium", "large"]:
                    file_urls.append(record["formats"][size]["url"])
            except:
                # For very small images (e.g. flags there is no large or even no medium version
                # For these one there is a intentional key error
                pass

    for i in range(len(file_urls)):
        url = file_urls[i][len("https://storage.googleapis.com/i14-worlds-2021-upload/"):]
        print(f"\n{i+1}/{len(file_urls)}: {url}")
        main.process_image('i14-worlds-2021-upload', url)


if __name__ == '__main__':
    # test_process_image()
    # manual_processing()
    pass
