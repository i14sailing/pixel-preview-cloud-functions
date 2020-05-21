
from PIL import Image
import requests
from io import BytesIO


PIXEL_PREVIEW_WIDTH = 64

# deploy with:
# gcloud functions deploy print_file_data --entry-point=print_file_data --runtime python37
# --trigger-resource i14-worlds-2021-upload --trigger-event google.storage.object.finalize
def print_file_data(data, context):
    # data (dict): The Cloud Functions event payload.
    # context (google.cloud.functions.Context): Metadata of triggering event.
    print(f"File: /{data['name']}")


# deploy with:
# gcloud functions deploy process_file_data --entry-point=process_file_data --runtime python37
# --trigger-resource i14-worlds-2021-upload --trigger-event google.storage.object.finalize
def process_file_data(data, context):
    # data (dict): The Cloud Functions event payload.
    # context (google.cloud.functions.Context): Metadata of triggering event.
    process_image(data['bucket'], data['name'])
    print(f"File: /{data['name']}")


# read logs with (takes approx 20-30 seconds until the logs show up):
# gcloud functions logs read --min-log-level=info


# ---------------------------------------------------------------------------------------------------------------------
def process_image(bucket_name, src_file_name):
    # bucket_name = "your-bucket-name"
    # source_file_name = "local/path/to/file"
    # destination_blob_name = "storage-object-name"

    file_extension = src_file_name.split(".")[-1]
    file_name = src_file_name.split(".")[-2]

    tmp_path_pixel = "./tmp-pixel." + file_extension

    if file_extension in ["jpg", "jpeg", "png", "gif"] and not ends_with(file_name, "-pixel-preview"):

        # Fetch image from the given bucket_name + file_name
        file_url = "https://storage.googleapis.com/" + bucket_name + "/" + src_file_name
        response = requests.get(file_url)
        img = Image.open(BytesIO(response.content))

        """
        # Generate examples for different interpolation functions:
        
        for iteration in [
            {"interpolator": Image.NEAREST, "tmp_path": "./tmp-pixel-nearest"},
            {"interpolator": Image.BILINEAR, "tmp_path": "./tmp-pixel-bilinear"},
            {"interpolator": Image.BICUBIC, "tmp_path": "./tmp-pixel-bicubic"},
            {"interpolator": Image.LANCZOS, "tmp_path": "./tmp-pixel-lanczos"},
        ]:
            
            # I have to resize them to the original size because Github strips away all inline styles from markdown.
            # Therefore i cannot disable interpolation in the displayed html version of the README.md
            # In a regular HTML this is no problem -> See React component implementation
            
            img.resize((PIXEL_PREVIEW_WIDTH, int(PIXEL_PREVIEW_WIDTH * (img.size[1]/img.size[0]))), resample=iteration["interpolator"])\
                .resize(img.size, resample=0).save(iteration["tmp_path"] + "." + file_extension)
        """

        print(f"New pixel-preview: /{src_file_name}")
    else:
        print(f"No pixel-preview for videos: /{src_file_name}")


def ends_with(string, ending):
    if len(string) < len(ending):
        return False
    else:
        return string[-len(ending):] == ending

