"""
Machine Learning module.

Provides ML model management, versioning, performance tracking,
A/B testing, and explainability features.
"""

from .model_manager import ModelManager, ModelVersion, get_model_manager

__all__ = ["ModelManager", "ModelVersion", "get_model_manager"]
