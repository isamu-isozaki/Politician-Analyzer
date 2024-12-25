import os
from pdf2image import convert_from_bytes
from tqdm.auto import tqdm
from pathlib import PurePath

def convert_pdfs_to_images(balance_dir):
    for folder_path in tqdm(os.listdir(balance_dir)):
        folder_dir = os.path.join(balance_dir, folder_path)
        print("Converting folder", folder_dir)
        for file in os.listdir(folder_dir):
            file_path = os.path.join(folder_dir, file)
            file_image_dirs = os.path.join(folder_dir, file.split(".pdf")[0])
            if os.path.exists(file_image_dirs) and os.path.exists(os.path.join(file_image_dirs, "0.jpg")):
                continue
            os.makedirs(file_image_dirs, exist_ok=True)


            if file_path.endswith(".pdf"):
                with open(file_path, "rb") as f:
                    images = convert_from_bytes(f.read())
                for i in range(len(images)):
                    images[i].save(file_image_dirs+f"/{i}.jpg", "JPEG")
if __name__ == "__main__":
    balance_dir = "data/jp/money_for_parties/balance"
    while True:
        convert_pdfs_to_images(balance_dir)