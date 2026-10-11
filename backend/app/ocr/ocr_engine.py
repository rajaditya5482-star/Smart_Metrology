from rapidocr_onnxruntime import RapidOCR
import numpy as np

class OCREngine:
    def __init__(self):
        # RapidOCR ONNX model - fast, lightweight, runs locally on CPU
        self.engine = RapidOCR()

    def extract(self, image_path: str) -> dict:
        """
        Runs OCR on given image.
        Returns:
            - lines: list of {"text": str, "box": list, "confidence": float}
            - full_text: joined text representation
            - mean_confidence: float
        """
        try:
            results, elapse = self.engine(image_path)
        except Exception as e:
            return {
                "lines": [],
                "full_text": "",
                "mean_confidence": 0.0,
                "error": str(e)
            }

        if not results:
            return {
                "lines": [],
                "full_text": "",
                "mean_confidence": 0.0,
                "error": None
            }

        lines = []
        confidences = []
        all_texts = []

        for item in results:
            box, text, score = item
            # Ensure box coordinates are native python numbers
            box_clean = [[int(pt[0]), int(pt[1])] for pt in box]
            conf = float(score)
            lines.append({
                "text": text.strip(),
                "box": box_clean,
                "confidence": round(conf, 4)
            })
            confidences.append(conf)
            all_texts.append(text.strip())

        mean_conf = float(np.mean(confidences)) if confidences else 0.0

        return {
            "lines": lines,
            "full_text": "\n".join(all_texts),
            "mean_confidence": round(mean_conf, 4),
            "error": None
        }
