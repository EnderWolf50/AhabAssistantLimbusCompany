import logging

import cv2
import numpy as np
from cv2 import createCLAHE
from PIL import Image
from rapidocr import EngineType, LangDet, LangRec, ModelType, OCRVersion, RapidOCR
from rapidocr.utils.output import RapidOCROutput

from utils.singletonmeta import SingletonMeta


class OCR(metaclass=SingletonMeta):
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        params = {
            "Det.engine_type": EngineType.ONNXRUNTIME,
            "Det.lang_type": LangDet.CH,
            "Det.model_type": ModelType.MOBILE,
            "Det.ocr_version": OCRVersion.PPOCRV4,
            "Rec.engine_type": EngineType.ONNXRUNTIME,
            "Rec.lang_type": LangRec.CH,
            "Rec.model_type": ModelType.MOBILE,
            "Rec.ocr_version": OCRVersion.PPOCRV4,
        }
        config_path = r"assets\config\default_rapidocr.yaml"
        self.engine = RapidOCR(params=params, config_path=config_path)
        # 快速模式：小裁剪的短边只放大到 320（默认 736），约快 3 倍。
        # 只用于已验证过的调用（文字标签）；小号数字（如商店金钱）在 320 下会读错，不要使用
        self.fast_engine = RapidOCR(params={**params, "Det.limit_side_len": 320}, config_path=config_path)

    def run(self, image: Image.Image | np.ndarray | str, fast: bool = False) -> RapidOCROutput:
        """执行OCR识别，支持Image对象、文件路径和np.ndarray对象"""
        try:
            if isinstance(image, str):
                with Image.open(image) as image_file:
                    image_array = np.array(image_file)
            elif isinstance(image, Image.Image):
                image_array = np.array(image)
            elif isinstance(image, np.ndarray):
                image_array = image
            else:
                image_array = np.array(image)

            if image_array.ndim == 2:
                img_cv_gray = image_array
            elif image_array.ndim == 3:
                channel_count = image_array.shape[2]
                if channel_count == 1:
                    img_cv_gray = image_array[:, :, 0]
                elif channel_count == 3:
                    img_cv = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
                    img_cv_gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
                elif channel_count == 4:
                    img_cv = cv2.cvtColor(image_array, cv2.COLOR_RGBA2BGR)
                    img_cv_gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
                else:
                    raise ValueError(f"不支持的图像通道数: {channel_count}")
            else:
                raise ValueError(f"不支持的图像维度: {image_array.ndim}")

            # 自适应均衡化(均值化后更亮)
            clahe = createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            processed_image = clahe.apply(img_cv_gray)
            results = (self.fast_engine if fast else self.engine)(processed_image)
            self.log_results(results)
            return results
        except Exception as e:
            self.logger.error(e)
            return RapidOCROutput()

    def log_results(self, ocr_results: RapidOCROutput) -> None:
        """记录OCR识别记录"""
        self.logger.debug(f"OCR识别结果：{ocr_results.txts}")
