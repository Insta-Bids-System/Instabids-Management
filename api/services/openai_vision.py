"""Integration with OpenAI Vision for SmartScope AI."""

from __future__ import annotations

import asyncio
import base64
import io
import json
import logging
import time
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional

import httpx
from openai import AsyncOpenAI
from PIL import Image, ImageEnhance, ImageOps

from ..config import settings
from ..models.smartscope import AnalysisRequest, MaterialItem, ScopeItem
from .smartscope_config import CATEGORY_SCOPE_TEMPLATES, SYSTEM_PROMPT, build_category_guidance


logger = logging.getLogger(__name__)


@dataclass
class ProcessedImage:
    """Represents an image prepared for the Vision API."""

    source_url: str
    base64_data: str
    width: int
    height: int
    quality_score: float


class ImagePreprocessor:
    """Fetches and normalises images prior to Vision analysis."""

    def __init__(self, timeout: float = 20.0) -> None:
        self.timeout = timeout

    async def preprocess(self, image_urls: Iterable[str]) -> List[ProcessedImage]:
        tasks = [self._process_single(url) for url in image_urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        processed: List[ProcessedImage] = []
        for result in results:
            if isinstance(result, ProcessedImage):
                processed.append(result)
        return processed

    async def _process_single(self, url: str) -> ProcessedImage:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url)
            response.raise_for_status()

        image_bytes = response.content
        image = Image.open(io.BytesIO(image_bytes))
        image = ImageOps.exif_transpose(image)
        image = image.convert("RGB")

        # Resize oversized images to reduce token usage while preserving detail
        max_dimension = 1600
        if max(image.size) > max_dimension:
            image.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)

        # Improve clarity for dark or low contrast captures
        image = ImageEnhance.Brightness(image).enhance(1.05)
        image = ImageEnhance.Contrast(image).enhance(1.1)

        buffered = io.BytesIO()
        image.save(buffered, format="JPEG", quality=90)
        base64_data = base64.b64encode(buffered.getvalue()).decode("utf-8")

        quality_score = self._estimate_quality(image)
        return ProcessedImage(
            source_url=url,
            base64_data=base64_data,
            width=image.width,
            height=image.height,
            quality_score=quality_score,
        )

    @staticmethod
    def _estimate_quality(image: Image.Image) -> float:
        width, height = image.size
        megapixels = (width * height) / 1_000_000
        aspect_ratio = max(width, height) / max(1, min(width, height))
        ratio_penalty = 1.0 if aspect_ratio < 2.2 else 0.85
        score = min(1.0, 0.1 + megapixels / 12) * ratio_penalty
        return round(score, 2)


class OpenAIVisionService:
    """Handles prompting and parsing for OpenAI Vision analyses."""

    def __init__(
        self,
        client: Optional[AsyncOpenAI] = None,
        preprocessor: Optional[ImagePreprocessor] = None,
    ) -> None:
        if client is None and not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required for SmartScope analysis")

        self.client = client or AsyncOpenAI(api_key=settings.openai_api_key)
        self.preprocessor = preprocessor or ImagePreprocessor()

    async def analyse(self, request: AnalysisRequest) -> Dict[str, Any]:
        """Execute the full analysis workflow returning structured data."""

        start_time = time.perf_counter()
        processed_images = await self.preprocessor.preprocess(request.photo_urls)
        if not processed_images:
            raise ValueError("No valid images were processed for analysis")

        payload = self._build_prompt_payload(request, processed_images)
        try:
            response = await self.client.responses.create(**payload)
        except Exception as exc:  # pragma: no cover - network failure path
            logger.exception("OpenAI Vision request failed: %s", exc)
            raise RuntimeError("Failed to analyse photos with OpenAI Vision") from exc
        elapsed_ms = int((time.perf_counter() - start_time) * 1000)

        content = self._extract_text(response)
        data = self._parse_response(content)

        data.setdefault("confidence", self._calculate_confidence(data, processed_images))
        data.setdefault("additional_observations", [])
        data.setdefault("materials", [])
        data.setdefault("scope_items", [])

        return {
            "analysis": data,
            "metadata": {
                "model_version": settings.smartscope_model,
                "processing_status": "completed",
                "processing_time_ms": elapsed_ms,
                "tokens_used": getattr(response, "usage", {}).get("total_tokens"),
            },
            "raw_response": response.model_dump() if hasattr(response, "model_dump") else response,  # type: ignore[arg-type]
        }

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _build_prompt_payload(
        self, request: AnalysisRequest, images: List[ProcessedImage]
    ) -> Dict[str, Any]:
        image_inputs = [
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": self._build_user_prompt(request, images)}
                ]
            }
        ]

        for processed in images:
            image_inputs[0]["content"].append(
                {
                    "type": "input_image",
                    "image": {
                        "data": processed.base64_data,
                        "format": "jpeg",
                    },
                }
            )

        return {
            "model": settings.smartscope_model,
            "input": [
                {
                    "role": "system",
                    "content": [{"type": "input_text", "text": SYSTEM_PROMPT}],
                },
                *image_inputs,
            ],
            "temperature": settings.smartscope_temperature,
            "max_output_tokens": settings.smartscope_max_output_tokens,
        }

    def _build_user_prompt(
        self, request: AnalysisRequest, images: List[ProcessedImage]
    ) -> str:
        guidance = build_category_guidance(request.category)
        templates = CATEGORY_SCOPE_TEMPLATES.get(request.category, [])
        template_str = "\n".join(f"- {item}" for item in templates)

        return (
            f"Analyze the following maintenance issue photos.\n"
            f"Project ID: {request.project_id}\n"
            f"Property Type: {request.property_type}\n"
            f"Area: {request.area}\n"
            f"Reported Issue: {request.reported_issue}\n"
            f"Category: {request.category}\n"
            f"Image Quality Scores: {[img.quality_score for img in images]}\n"
            f"{guidance}\n"
            "Respond with JSON using this schema:\n"
            "{\n"
            "  \"primary_issue\": str,\n"
            "  \"severity\": str (Emergency|High|Medium|Low),\n"
            "  \"scope_items\": [\n"
            "    {\n"
            "      \"title\": str,\n"
            "      \"description\": str,\n"
            "      \"trade\": str,\n"
            "      \"materials\": [str],\n"
            "      \"safety_notes\": [str],\n"
            "      \"estimated_hours\": float\n"
            "    }\n"
            "  ],\n"
            "  \"materials\": [\n"
            "    {\"name\": str, \"quantity\": str, \"specifications\": str}\n"
            "  ],\n"
            "  \"estimated_hours\": float,\n"
            "  \"safety_notes\": str,\n"
            "  \"additional_observations\": [str],\n"
            "  \"confidence\": float\n"
            "}\n"
            f"Recommended workflow outline:\n{template_str}\n"
            "Ensure numbers are realistic and cite uncertainties."
        )

    @staticmethod
    def _extract_text(response: Any) -> str:
        if hasattr(response, "output") and response.output:
            contents = response.output[0].get("content")  # type: ignore[index]
            if contents:
                text_parts = [part.get("text") for part in contents if part.get("type") == "output_text"]
                return "\n".join(filter(None, text_parts))

        if hasattr(response, "choices") and response.choices:
            return response.choices[0].message.content  # type: ignore[return-value]

        raise ValueError("Unexpected OpenAI response format")

    @staticmethod
    def _parse_response(content: str) -> Dict[str, Any]:
        content = content.strip()
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # Attempt to salvage JSON embedded in markdown
            start = content.find("{")
            end = content.rfind("}")
            if start != -1 and end != -1:
                return json.loads(content[start : end + 1])
            raise

    @staticmethod
    def _calculate_confidence(
        data: Dict[str, Any], images: List[ProcessedImage]
    ) -> float:
        base_confidence = data.get("confidence")
        if isinstance(base_confidence, (int, float)):
            return max(0.0, min(1.0, float(base_confidence)))

        quality_avg = sum(img.quality_score for img in images) / max(len(images), 1)
        scope_items = data.get("scope_items") or []
        detail_bonus = 0.05 if len(scope_items) >= 3 else 0.0
        return round(min(1.0, 0.6 + 0.3 * quality_avg + detail_bonus), 2)

    @staticmethod
    def build_scope_items(payload: Dict[str, Any]) -> List[ScopeItem]:
        items = []
        for item in payload.get("scope_items", []) or []:
            items.append(
                ScopeItem(
                    title=item.get("title", "Task"),
                    description=item.get("description", ""),
                    trade=item.get("trade"),
                    materials=item.get("materials", []),
                    safety_notes=item.get("safety_notes", []),
                    estimated_hours=item.get("estimated_hours"),
                )
            )
        return items

    @staticmethod
    def build_materials(payload: Dict[str, Any]) -> List[MaterialItem]:
        materials = []
        for item in payload.get("materials", []) or []:
            materials.append(
                MaterialItem(
                    name=item.get("name", "Material"),
                    quantity=item.get("quantity"),
                    specifications=item.get("specifications"),
                )
            )
        return materials


__all__ = ["OpenAIVisionService", "ImagePreprocessor", "ProcessedImage"]
