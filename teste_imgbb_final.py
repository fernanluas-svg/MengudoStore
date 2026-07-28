import base64
import os
import requests

API_KEY = "f3d8bddf095bfb533ceb1fd069595b7e"
IMAGE_FILENAME = "taça liberta.png"


def upload_to_imgbb(image_path: str) -> str | None:
    with open(image_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode("utf-8")

    response = requests.post(
        "https://api.imgbb.com/1/upload",
        data={
            "key": API_KEY,
            "image": encoded_image,
        },
        timeout=30,
    )
    response.raise_for_status()
    result = response.json()

    if result.get("success"):
        return result["data"]["url"]

    raise RuntimeError(f"ImgBB upload failed: {result}")


if __name__ == "__main__":
    project_root = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(project_root, IMAGE_FILENAME)

    if not os.path.isfile(image_path):
        raise FileNotFoundError(f"Imagem não encontrada: {image_path}")

    print("🚀 Enviando imagem para o ImgBB...")
    link = upload_to_imgbb(image_path)
    print(f"✅ Upload concluído: {link}")
