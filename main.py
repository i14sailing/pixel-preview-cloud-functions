
from google.cloud import storage
from PIL import Image
import requests
from io import BytesIO
import math
import os
from datetime import datetime

PIXEL_PREVIEW_WIDTH = 64


# deploy with:
# gcloud functions deploy test_file_change --entry-point=test_file_change --runtime python37 --trigger-resource i14-worlds-2021-upload --trigger-event google.storage.object.finalize
def test_file_change(data, context):
    # data (dict): The Cloud Functions event payload.
    # context (google.cloud.functions.Context): Metadata of triggering event.
    # print(f"File: /{data['name']}")
    print(f"data={data}, context={context}")


# deploy with:
# gcloud functions deploy process_file_data --entry-point=process_file_data --runtime python37 --trigger-resource i14-worlds-2021-upload --trigger-event google.storage.object.finalize
def process_file_data(data, context):
    # data (dict): The Cloud Functions event payload.
    # context (google.cloud.functions.Context): Metadata of triggering event.

    # Prevent infinite processing loops!!!
    # Does not work, stupid gcloud storage :(
    # Object including its "created at" and "updated at"
    # properties get
    now = datetime.utcnow()
    last_updated_string = data['updated']
    last_updated = datetime.strptime(last_updated_string[:10] + " " + last_updated_string[11:-5], '%Y-%m-%d %H:%M:%S')

    if (now - last_updated).seconds > 30:
        process_image(data['bucket'], data['name'])
    else:
        print(f"Cooldown time required for file {data['name']}")


# read logs with (takes approx 20-30 seconds until the logs show up):
# gcloud functions logs read --min-log-level=info


# ---------------------------------------------------------------------------------------------------------------------


def process_image(bucket_name, src_file_name):

    file_extension = src_file_name.split(".")[-1]
    file_name = src_file_name.split(".")[-2]

    tmp_path_crop = "/tmp/tmp-crop." + file_extension
    tmp_path_pixel = "/tmp/tmp-pixel." + file_extension

    if file_extension in ["jpg", "jpeg", "png", "gif"] and not ends_with(file_name, "-pixel-preview"):

        # Fetch image from the given bucket_name + file_name
        file_url = "https://storage.googleapis.com/" + bucket_name + "/" + src_file_name
        response = requests.get(file_url)
        img = Image.open(BytesIO(response.content))

        # Connect to google storage bucket
        dst_file_name = generate_pixel_preview_file_path(src_file_name)
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        src_blob = bucket.blob(src_file_name)
        dst_blob = bucket.blob(dst_file_name)

        # generate_interpolation_examples(img, file_extension)
        print(f"\nOriginal Size = {img.size}")
        print(f"New Size = {get_snap_size(img.size)}")
        print(f"PixelPreview Size = {get_resize_region(img.size)}")

        # Generate cropped version that sufficed aspect ration of pixel image
        print("cropping ...")
        img.crop(get_crop_region(img.size)).save(tmp_path_crop)

        # Generate pixel preview version
        print("resizing ...")
        img.resize(get_resize_region(img.size), resample=Image.LANCZOS).save(tmp_path_pixel)

        # Upload Cropped Version
        print("uploading cropped version ...")
        src_blob.upload_from_filename(tmp_path_crop)

        # Upload Pixel Preview Version
        print("uploading pixeled version ...")
        dst_blob.upload_from_filename(tmp_path_pixel)

        # TODO: Update the metadata in any database where this upload is logged (e.g. strapi cms)

        # Remove temporary files
        print("removing local storage ...")
        # os.remove(tmp_path_crop)
        # os.remove(tmp_path_pixel)

        print(f"New pixel-preview for file {src_file_name}")
    else:
        print(f"No pixel-preview for file {src_file_name} due to invalid file extension")


def ends_with(string, ending):
    if len(string) < len(ending):
        return False
    else:
        return string[-len(ending):] == ending


def generate_pixel_preview_file_path(file_path):
    # Generate the new filename for pixel preview files
    # Example: .../image.jpeg -> .../image-pixel-preview.jpeg

    path_list = file_path.split(".")

    new_path_string = ""
    for string in path_list[:-1]:
        new_path_string += string
    new_path_string += "-pixel-preview"     # Insert "-pixel-preview" slice
    new_path_string += "." + path_list[-1]  # Append extension

    return new_path_string


def get_snap_size(size):
    # size given as (width, height) 2-tuple
    ratio = size[1]/size[0]

    new_width = size[0]
    new_height = (round(ratio * PIXEL_PREVIEW_WIDTH) / PIXEL_PREVIEW_WIDTH) * size[0]

    while round(new_height) != new_height:
        new_width -= 1
        new_height = (math.floor(ratio * PIXEL_PREVIEW_WIDTH) / PIXEL_PREVIEW_WIDTH) * new_width

    return (new_width, int(new_height))


def get_crop_region(size):
    # size given as (width, height) 2-tuple
    new_size = get_snap_size(size)

    dx = size[0] - new_size[0]
    dy = size[1] - new_size[1]

    x0 = math.floor(dx/2)
    y0 = math.floor(dy/2)
    x1 = size[0] - math.ceil(dx/2)
    y1 = size[1] - math.ceil(dy/2)

    return (x0, y0, x1, y1)


def get_resize_region(size):
    # size given as (width, height) 2-tuple
    new_size = get_snap_size(size)
    new_height = int(PIXEL_PREVIEW_WIDTH * (new_size[1]/new_size[0]))
    return (PIXEL_PREVIEW_WIDTH, new_height)


def generate_interpolation_examples(img, file_extension):
    # Generate examples for different interpolation functions:

    for interpolation in [
        {"interpolator": Image.NEAREST, "tmp_path": "./tmp-pixel-nearest"},
        {"interpolator": Image.BILINEAR, "tmp_path": "./tmp-pixel-bilinear"},
        {"interpolator": Image.BICUBIC, "tmp_path": "./tmp-pixel-bicubic"},
        {"interpolator": Image.LANCZOS, "tmp_path": "./tmp-pixel-lanczos"},
    ]:
        # I have to resize them to the original size because Github strips away all inline styles from markdown.
        # Therefore i cannot disable interpolation in the displayed html version of the README.md
        # In a regular HTML this is no problem -> See React component implementation

        img.resize((PIXEL_PREVIEW_WIDTH, int(PIXEL_PREVIEW_WIDTH * (img.size[1] / img.size[0]))),
                   resample=interpolation["interpolator"]) \
            .resize(img.size, resample=0).save(interpolation["tmp_path"] + "." + file_extension)
