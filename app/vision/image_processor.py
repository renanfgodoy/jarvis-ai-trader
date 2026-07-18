from __future__ import annotations

import hashlib
import struct

from app.core.config import settings
from app.vision.exceptions import VisionValidationError
from app.vision.models import ProcessedVisionImage, VisionImageMetadata


MIME_BY_FORMAT = {
    "png": "image/png",
    "jpeg": "image/jpeg",
    "jpg": "image/jpeg",
    "webp": "image/webp",
}


class VisionImageProcessor:
    min_width = 320
    min_height = 240
    max_side = 2048

    def process(self, *, image_bytes: bytes, filename: str | None, content_type: str | None) -> ProcessedVisionImage:
        if not image_bytes:
            raise VisionValidationError("Empty image.", error_code="VISION_IMAGE_EMPTY")
        max_bytes = settings.friday_vision_max_image_mb * 1024 * 1024
        if len(image_bytes) > max_bytes:
            raise VisionValidationError("Image too large.", error_code="VISION_IMAGE_TOO_LARGE")

        image_format, width, height = self._detect_format_and_size(image_bytes)
        allowed = set(settings.friday_vision_allowed_formats_tuple)
        if image_format not in allowed and not (image_format == "jpeg" and "jpg" in allowed):
            raise VisionValidationError("Unsupported image format.", error_code="VISION_IMAGE_UNSUPPORTED")
        if width < self.min_width or height < self.min_height:
            raise VisionValidationError("Image is too small.", error_code="VISION_IMAGE_TOO_SMALL")

        processed = self._strip_jpeg_app1(image_bytes) if image_format == "jpeg" else image_bytes
        mime_type = MIME_BY_FORMAT[image_format]
        if content_type and content_type.lower().split(";")[0].strip() not in {mime_type, "application/octet-stream"}:
            raise VisionValidationError("MIME type does not match image signature.", error_code="VISION_IMAGE_UNSUPPORTED")

        digest = hashlib.sha256(processed).hexdigest()
        return ProcessedVisionImage(
            metadata=VisionImageMetadata(
                filename=filename,
                content_type=content_type,
                size_bytes=len(processed),
                width=width,
                height=height,
                image_hash=digest,
                format=image_format,
                exif_removed=image_format == "jpeg",
            ),
            image_bytes=processed,
            mime_type=mime_type,
        )

    def _detect_format_and_size(self, image_bytes: bytes) -> tuple[str, int, int]:
        if image_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
            if len(image_bytes) < 33 or image_bytes[12:16] != b"IHDR":
                raise VisionValidationError("Corrupted PNG.", error_code="VISION_IMAGE_CORRUPTED")
            width, height = struct.unpack(">II", image_bytes[16:24])
            return "png", int(width), int(height)
        if image_bytes.startswith(b"\xff\xd8"):
            return self._read_jpeg_size(image_bytes)
        if image_bytes.startswith(b"RIFF") and image_bytes[8:12] == b"WEBP":
            return self._read_webp_size(image_bytes)
        raise VisionValidationError("Unsupported image signature.", error_code="VISION_IMAGE_UNSUPPORTED")

    def _read_jpeg_size(self, image_bytes: bytes) -> tuple[str, int, int]:
        index = 2
        while index + 9 < len(image_bytes):
            if image_bytes[index] != 0xFF:
                index += 1
                continue
            marker = image_bytes[index + 1]
            index += 2
            if marker in {0xD8, 0xD9}:
                continue
            if index + 2 > len(image_bytes):
                break
            length = int.from_bytes(image_bytes[index : index + 2], "big")
            if length < 2 or index + length > len(image_bytes):
                break
            if marker in {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}:
                height = int.from_bytes(image_bytes[index + 3 : index + 5], "big")
                width = int.from_bytes(image_bytes[index + 5 : index + 7], "big")
                return "jpeg", int(width), int(height)
            index += length
        raise VisionValidationError("Corrupted JPEG.", error_code="VISION_IMAGE_CORRUPTED")

    def _read_webp_size(self, image_bytes: bytes) -> tuple[str, int, int]:
        chunk = image_bytes[12:16]
        if chunk == b"VP8X" and len(image_bytes) >= 30:
            width = int.from_bytes(image_bytes[24:27], "little") + 1
            height = int.from_bytes(image_bytes[27:30], "little") + 1
            return "webp", width, height
        if chunk == b"VP8L" and len(image_bytes) >= 25:
            bits = int.from_bytes(image_bytes[21:25], "little")
            width = (bits & 0x3FFF) + 1
            height = ((bits >> 14) & 0x3FFF) + 1
            return "webp", width, height
        if chunk == b"VP8 " and len(image_bytes) >= 30:
            start = image_bytes.find(b"\x9d\x01\x2a")
            if start != -1 and start + 7 < len(image_bytes):
                width = int.from_bytes(image_bytes[start + 3 : start + 5], "little") & 0x3FFF
                height = int.from_bytes(image_bytes[start + 5 : start + 7], "little") & 0x3FFF
                return "webp", width, height
        raise VisionValidationError("Corrupted WEBP.", error_code="VISION_IMAGE_CORRUPTED")

    def _strip_jpeg_app1(self, image_bytes: bytes) -> bytes:
        output = bytearray(image_bytes[:2])
        index = 2
        while index + 4 <= len(image_bytes):
            if image_bytes[index] != 0xFF:
                output.extend(image_bytes[index:])
                break
            marker = image_bytes[index + 1]
            if marker == 0xDA:
                output.extend(image_bytes[index:])
                break
            length = int.from_bytes(image_bytes[index + 2 : index + 4], "big")
            segment_end = index + 2 + length
            if segment_end > len(image_bytes) or length < 2:
                output.extend(image_bytes[index:])
                break
            if marker != 0xE1:
                output.extend(image_bytes[index:segment_end])
            index = segment_end
        return bytes(output)
