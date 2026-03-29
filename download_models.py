import os
import urllib.request

def download_age_models():
    """
    Downloads the pre-trained Age Estimation models from the OpenCV GitHub repository.
    """
    model_dir = "models"
    os.makedirs(model_dir, exist_ok=True)

    base_url = "https://raw.githubusercontent.com/opencv/opencv_3rdparty/dnn_samples_face_detector_20170830/"
    
    # 1. Prototxt (Model architecture)
    prototxt_url = "https://raw.githubusercontent.com/GilLevi/AgeGenderDeepLearning/master/age_net_definitions/deploy.prototxt"
    # 2. Caffemodel (Weights)
    caffemodel_url = "https://github.com/GilLevi/AgeGenderDeepLearning/raw/master/models/age_net.caffemodel"

    files = {
        "age_deploy.prototxt": prototxt_url,
        "age_net.caffemodel": caffemodel_url
    }

    print("[AI Download] Checking for model files...")
    for filename, url in files.items():
        target_path = os.path.join(model_dir, filename)
        if not os.path.exists(target_path):
            print(f"[AI Download] Downloading {filename}...")
            try:
                urllib.request.urlretrieve(url, target_path)
                print(f"[AI Download] Success: Saved to {target_path}")
            except Exception as e:
                print(f"[AI Download] Error downloading {filename}: {e}")
        else:
            print(f"[AI Download] {filename} already exists.")

if __name__ == "__main__":
    download_age_models()
