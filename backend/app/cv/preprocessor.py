import cv2
import numpy as np
import os
import uuid

class ImagePreprocessor:
    def __init__(self, upload_dir: str):
        self.upload_dir = upload_dir
        os.makedirs(upload_dir, exist_ok=True)

    def enhance_image(self, image_path: str) -> dict:
        """
        Enhance packaging image for improved OCR accuracy:
        - Contrast Limited Adaptive Histogram Equalization (CLAHE)
        - Bilateral filtering to reduce printing texture/noise while preserving text edges
        - Unsharp masking for crisp text rendering
        """
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not read image from {image_path}")

        # Convert to LAB color space to equalize lightness without distorting colors
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)

        clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
        l_enhanced = clahe.apply(l)

        enhanced_lab = cv2.merge((l_enhanced, a, b))
        enhanced_bgr = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)

        # Bilateral filter to smooth packaging reflections while keeping text crisp
        denoised = cv2.bilateralFilter(enhanced_bgr, d=7, sigmaColor=50, sigmaSpace=50)

        # Unsharp mask for crisp text edges
        gaussian = cv2.GaussianBlur(denoised, (0, 0), 2.0)
        sharpened = cv2.addWeighted(denoised, 1.4, gaussian, -0.4, 0)

        # Detect image quality metrics (Laplacian blur variance)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blur_variance = float(cv2.Laplacian(gray, cv2.CV_64F).var())
        is_blurry = blur_variance < 80.0

        enhanced_filename = f"enhanced_{uuid.uuid4().hex[:8]}.jpg"
        enhanced_path = os.path.join(self.upload_dir, enhanced_filename)
        cv2.imwrite(enhanced_path, sharpened)

        return {
            "enhanced_path": enhanced_path,
            "blur_variance": round(blur_variance, 2),
            "is_blurry": is_blurry,
            "original_resolution": [image.shape[1], image.shape[0]],
        }

    def annotate_detections(self, image_path: str, detections: list) -> str:
        """
        Draw bounding boxes and field badges onto the packaging photo.
        detections: list of dicts with box [[x1,y1],[x2,y1],[x2,y2],[x1,y2]] and text/label
        """
        image = cv2.imread(image_path)
        if image is None:
            return image_path

        h, w = image.shape[:2]
        annotated = image.copy()

        # Color palette for Legal Metrology fields
        colors = {
            "mrp": (0, 165, 255),          # Amber / Orange
            "net_quantity": (255, 144, 30), # Blue-cyan
            "mfg_date": (50, 205, 50),     # Lime Green
            "manufacturer": (147, 20, 255),# Purple
            "consumer_care": (0, 215, 255),# Yellow-gold
            "product_name": (205, 90, 106),# Slate Blue
            "default": (0, 255, 127)       # Spring Green
        }

        for item in detections:
            box = item.get("box")
            label = item.get("label", "Declaration")
            field_type = item.get("field_type", "default")
            color = colors.get(field_type, colors["default"])

            if box is not None and len(box) >= 4:
                pts = np.array(box, np.int32).reshape((-1, 1, 2))
                cv2.polylines(annotated, [pts], isClosed=True, color=color, thickness=2)

                # Draw semi-transparent background tag for label
                x, y = int(pts[0][0][0]), int(pts[0][0][1])
                badge_text = f"{label}"
                (tw, th), _ = cv2.getTextSize(badge_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
                
                # Tag box
                y_tag = max(y - 6, th + 6)
                cv2.rectangle(annotated, (x, y_tag - th - 4), (x + tw + 8, y_tag + 4), color, -1)
                cv2.putText(annotated, badge_text, (x + 4, y_tag), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)

        annotated_filename = f"annotated_{uuid.uuid4().hex[:8]}.jpg"
        annotated_path = os.path.join(self.upload_dir, annotated_filename)
        cv2.imwrite(annotated_path, annotated)
        return annotated_path
