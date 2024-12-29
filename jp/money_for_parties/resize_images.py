import PIL.Image
import sys
import os
from tqdm.auto import tqdm
def main():
    balance_dir = sys.argv[1]
    factor = int(sys.argv[2])


    for date_dir in tqdm(os.listdir(balance_dir)):
        date_path = f"{balance_dir}/{date_dir}"
        for party_dir in os.listdir(date_path):
            party_path = f"{date_path}/{party_dir}"
            if os.path.isdir(party_path) and not ("_factor_1_" in party_path):
                resized_images_dir = party_path+f"_factor_1_{factor}"
                os.makedirs(resized_images_dir, exist_ok=True)
                for image_name in tqdm(os.listdir(party_path)):
                    if image_name.endswith(".jpg"):
                        image_path = f"{party_path}/{image_name}"
                        target_image_path = image_path.replace(party_path, resized_images_dir)
                        if os.path.exists(target_image_path):
                            continue
                        image = PIL.Image.open(image_path)
                        width, height = image.size
                        target_image = image.resize((width//factor, height//factor))
                        target_image.save(target_image_path)

if __name__ == "__main__":
    main()