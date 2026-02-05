import requests
import torch
from PIL import Image
from io import BytesIO
from tqdm import tqdm
from transformers import Qwen2_5_VLForConditionalGeneration, AutoProcessor

class OCREngine:
    def __init__(self, model_id: str = "Qwen/Qwen2.5-VL-7B-Instruct"):
        """
        Initialize the OCR Engine with Qwen2.5-VL.
        """
        self.model_id = model_id
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = None
        self.processor = None
        
    def load_model(self):
        if self.model is None:
            print(f"🧠 Loading OCR model {self.model_id} on {self.device}...")
            self.model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
                self.model_id, 
                torch_dtype=torch.bfloat16 if self.device == "cuda" else torch.float32, 
                device_map="auto"
            )
            self.processor = AutoProcessor.from_pretrained(self.model_id)
            print("✅ Model loaded.")

    def process_images_batch(self, image_urls: list):
        """
        Process a list of image URLs and return text extractions.
        """
        if not self.model:
            self.load_model()
            
        ocr_results = {}
        prompt_text = (
            "Extract all text from this image. Keep Thai and English exactly as written. "
            "If there is a diagram, describe its structure. Format as Markdown."
        )

        print(f"🔍 Processing {len(image_urls)} images...")
        for url in tqdm(image_urls, desc="OCR Processing"):
            try:
                # Download image
                resp = requests.get(url, timeout=10)
                img = Image.open(BytesIO(resp.content)).convert("RGB")

                # Prepare inputs
                messages = [
                    {
                        "role": "user",
                        "content": [
                            {"type": "image", "image": img},
                            {"type": "text", "text": prompt_text},
                        ],
                    }
                ]

                # Inference
                text_input = self.processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
                inputs = self.processor(text=[text_input], images=[img], padding=True, return_tensors="pt")
                inputs = inputs.to(self.device)

                generated_ids = self.model.generate(**inputs, max_new_tokens=1024)
                
                # Decode
                generated_ids_trimmed = [
                    out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
                ]
                output_text = self.processor.batch_decode(
                    generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
                )

                ocr_results[url] = output_text[0]

            except Exception as e:
                print(f"⚠️ Error processing {url}: {e}")
                ocr_results[url] = "[OCR Failed]"
        
        return ocr_results
