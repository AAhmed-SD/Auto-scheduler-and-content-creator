import torch
import clip
from PIL import Image
import numpy as np
from typing import List, Dict, Union, Optional, Any, TypedDict
import os
from app.core.config import settings


class StyleAnalysis(TypedDict):
    elements: List[str]
    scores: List[float]


class StyleResult(TypedDict):
    features: List[List[float]]
    style_analysis: Dict[str, StyleAnalysis]
    device: str


class CLIPService:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model, self.preprocess = clip.load("ViT-B/32", device=self.device)

    async def analyze_style(
        self, image_path: str, style_categories: Optional[Dict[str, List[str]]] = None
    ) -> StyleResult:
        """Analyze an image and return its style characteristics."""
        try:
            image = Image.open(image_path)
            image = self.preprocess(image).unsqueeze(0).to(self.device)

            with torch.no_grad():
                image_features = self.model.encode_image(image)
                image_features /= image_features.norm(dim=-1, keepdim=True)

                # Use default categories if none provided
                if style_categories is None:
                    style_categories = {
                        "composition": [
                            "symmetrical composition",
                            "rule of thirds",
                            "leading lines",
                            "framing",
                            "depth of field",
                            "minimalist",
                            "complex",
                            "balanced",
                        ],
                        "color": [
                            "warm tones",
                            "cool tones",
                            "monochromatic",
                            "complementary colors",
                            "analogous colors",
                            "high contrast",
                            "low contrast",
                            "vibrant colors",
                        ],
                        "lighting": [
                            "natural lighting",
                            "artificial lighting",
                            "dramatic shadows",
                            "soft lighting",
                            "backlighting",
                            "golden hour",
                            "low key",
                            "high key",
                        ],
                        "mood": [
                            "peaceful",
                            "energetic",
                            "mysterious",
                            "joyful",
                            "serious",
                            "nostalgic",
                            "modern",
                            "traditional",
                        ],
                    }

                # Analyze against style elements
                style_analysis: Dict[str, StyleAnalysis] = {}
                for category, elements in style_categories.items():
                    text = clip.tokenize(elements).to(self.device)
                    text_features = self.model.encode_text(text)
                    text_features /= text_features.norm(dim=-1, keepdim=True)

                    similarity = (100.0 * image_features @ text_features.T).softmax(
                        dim=-1
                    )
                    values, indices = similarity[0].topk(3)

                    style_analysis[category] = {
                        "elements": [elements[idx] for idx in indices],
                        "scores": values.cpu().numpy().tolist(),
                    }

            return {
                "features": image_features.cpu().numpy().tolist(),
                "style_analysis": style_analysis,
                "device": self.device,
            }
        except Exception as e:
            raise Exception(f"Error analyzing image: {str(e)}")

    async def generate_style_guidelines(
        self,
        reference_images: List[str],
        style_categories: Optional[Dict[str, List[str]]] = None,
    ) -> Dict[str, Dict[str, float]]:
        """Generate style guidelines based on multiple reference images."""
        try:
            style_guidelines: Dict[str, Dict[str, List[float]]] = {
                "composition": {},
                "color": {},
                "lighting": {},
                "mood": {},
            }

            for image_path in reference_images:
                analysis = await self.analyze_style(image_path, style_categories)

                for category, data in analysis["style_analysis"].items():
                    for element, score in zip(data["elements"], data["scores"]):
                        if element not in style_guidelines[category]:
                            style_guidelines[category][element] = []
                        style_guidelines[category][element].append(float(score))

            # Average the scores and sort by importance
            result: Dict[str, Dict[str, float]] = {}
            for category in style_guidelines:
                result[category] = {}
                for element in style_guidelines[category]:
                    result[category][element] = float(np.mean(
                        style_guidelines[category][element]
                    ))
                result[category] = dict(
                    sorted(
                        result[category].items(),
                        key=lambda x: x[1],
                        reverse=True,
                    )
                )

            return result

        except Exception as e:
            raise Exception(f"Error generating style guidelines: {str(e)}")

    async def suggest_content_variations(
        self,
        reference_image_path: str,
        num_variations: int = 3,
        style_categories: Optional[Dict[str, List[str]]] = None,
    ) -> List[Dict[str, str]]:
        """Suggest variations of content while maintaining style consistency."""
        try:
            analysis = await self.analyze_style(reference_image_path, style_categories)

            variations = []
            for i in range(num_variations):
                variation = {
                    "composition": np.random.choice(
                        analysis["style_analysis"]["composition"]["elements"]
                    ),
                    "color": np.random.choice(
                        analysis["style_analysis"]["color"]["elements"]
                    ),
                    "lighting": np.random.choice(
                        analysis["style_analysis"]["lighting"]["elements"]
                    ),
                    "mood": np.random.choice(
                        analysis["style_analysis"]["mood"]["elements"]
                    ),
                    "description": f"Variation {i+1} - A unique combination of visual elements",
                }
                variations.append(variation)

            return variations

        except Exception as e:
            raise Exception(f"Error suggesting content variations: {str(e)}")

    async def evaluate_content_originality(
        self,
        new_image_path: str,
        reference_images: List[str],
        style_categories: Optional[Dict[str, List[str]]] = None,
    ) -> Dict[str, Union[float, Dict[str, StyleAnalysis]]]:
        """Evaluate how original a new piece of content is compared to references."""
        try:
            new_analysis = await self.analyze_style(new_image_path, style_categories)
            reference_features = []

            for ref_path in reference_images:
                ref_analysis = await self.analyze_style(ref_path, style_categories)
                reference_features.append(torch.tensor(ref_analysis["features"]))

            new_features = torch.tensor(new_analysis["features"])
            similarities = []

            for ref_feat in reference_features:
                similarity = torch.cosine_similarity(new_features, ref_feat)
                similarities.append(float(similarity.item()))

            # Originality score (lower similarity = more original)
            originality_score = 1.0 - float(np.mean(similarities))

            return {
                "originality_score": originality_score,
                "style_consistency": float(np.mean(similarities)),
                "analysis": new_analysis["style_analysis"],
            }

        except Exception as e:
            raise Exception(f"Error evaluating content originality: {str(e)}")
