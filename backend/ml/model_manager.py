"""
ML Model versioning and management system.

This module provides version control for ML models, allowing multiple
model versions to coexist and enabling seamless model updates.
"""

import os
import json
import pickle
import hashlib
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
from datetime import datetime
import logging
import shutil

logger = logging.getLogger(__name__)


class ModelVersion:
    """Represents a specific version of an ML model."""
    
    def __init__(
        self,
        version: str,
        model_path: str,
        tfidf_path: str,
        metadata: Optional[Dict] = None,
    ):
        """
        Initialize model version.
        
        Args:
            version: Version identifier (e.g., "1.0.0", "2023-12-01")
            model_path: Path to model file
            tfidf_path: Path to TF-IDF vectorizer file
            metadata: Optional metadata (accuracy, training date, etc.)
        """
        self.version = version
        self.model_path = model_path
        self.tfidf_path = tfidf_path
        self.metadata = metadata or {}
        self.loaded_at: Optional[datetime] = None
        self.model = None
        self.tfidf = None
    
    def load(self):
        """Load model and vectorizer into memory."""
        try:
            logger.info(f"Loading model version {self.version}...")
            
            with open(self.model_path, "rb") as f:
                self.model = pickle.load(f)
            
            with open(self.tfidf_path, "rb") as f:
                self.tfidf = pickle.load(f)
            
            self.loaded_at = datetime.utcnow()
            logger.info(f"Model version {self.version} loaded successfully")
        
        except Exception as e:
            logger.error(f"Failed to load model version {self.version}: {e}")
            raise
    
    def unload(self):
        """Unload model from memory."""
        self.model = None
        self.tfidf = None
        self.loaded_at = None
        logger.info(f"Model version {self.version} unloaded")
    
    def is_loaded(self) -> bool:
        """Check if model is loaded in memory."""
        return self.model is not None and self.tfidf is not None
    
    def get_checksum(self) -> str:
        """Calculate checksum of model files."""
        hasher = hashlib.sha256()
        
        with open(self.model_path, "rb") as f:
            hasher.update(f.read())
        
        with open(self.tfidf_path, "rb") as f:
            hasher.update(f.read())
        
        return hasher.hexdigest()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary representation."""
        return {
            "version": self.version,
            "model_path": self.model_path,
            "tfidf_path": self.tfidf_path,
            "metadata": self.metadata,
            "loaded": self.is_loaded(),
            "loaded_at": self.loaded_at.isoformat() if self.loaded_at else None,
            "checksum": self.get_checksum(),
        }


class ModelManager:
    """
    Manages multiple versions of ML models.
    
    Provides version control, hot-swapping, and rollback capabilities.
    """
    
    def __init__(self, models_dir: str = "models"):
        """
        Initialize model manager.
        
        Args:
            models_dir: Directory containing model versions
        """
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(exist_ok=True)
        
        self.versions: Dict[str, ModelVersion] = {}
        self.active_version: Optional[str] = None
        self.config_file = self.models_dir / "versions.json"
        
        self._load_config()
    
    def _load_config(self):
        """Load model versions configuration."""
        if self.config_file.exists():
            try:
                with open(self.config_file, "r") as f:
                    config = json.load(f)
                
                self.active_version = config.get("active_version")
                
                for version_data in config.get("versions", []):
                    version = ModelVersion(
                        version=version_data["version"],
                        model_path=version_data["model_path"],
                        tfidf_path=version_data["tfidf_path"],
                        metadata=version_data.get("metadata", {}),
                    )
                    self.versions[version.version] = version
                
                logger.info(f"Loaded {len(self.versions)} model versions from config")
            
            except Exception as e:
                logger.error(f"Failed to load model config: {e}")
    
    def _save_config(self):
        """Save model versions configuration."""
        try:
            config = {
                "active_version": self.active_version,
                "versions": [
                    {
                        "version": v.version,
                        "model_path": v.model_path,
                        "tfidf_path": v.tfidf_path,
                        "metadata": v.metadata,
                    }
                    for v in self.versions.values()
                ],
                "updated_at": datetime.utcnow().isoformat(),
            }
            
            with open(self.config_file, "w") as f:
                json.dump(config, f, indent=2)
            
            logger.info("Model config saved")
        
        except Exception as e:
            logger.error(f"Failed to save model config: {e}")
    
    def register_version(
        self,
        version: str,
        model_path: str,
        tfidf_path: str,
        metadata: Optional[Dict] = None,
        set_active: bool = False,
    ) -> ModelVersion:
        """
        Register a new model version.
        
        Args:
            version: Version identifier
            model_path: Path to model file
            tfidf_path: Path to TF-IDF file
            metadata: Optional metadata
            set_active: Whether to set as active version
            
        Returns:
            ModelVersion instance
        """
        if version in self.versions:
            raise ValueError(f"Version {version} already exists")
        
        # Validate files exist
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")
        
        if not os.path.exists(tfidf_path):
            raise FileNotFoundError(f"TF-IDF file not found: {tfidf_path}")
        
        # Create version
        model_version = ModelVersion(
            version=version,
            model_path=model_path,
            tfidf_path=tfidf_path,
            metadata=metadata or {},
        )
        
        self.versions[version] = model_version
        
        if set_active or self.active_version is None:
            self.active_version = version
        
        self._save_config()
        
        logger.info(f"Registered model version {version}")
        return model_version
    
    def get_version(self, version: str) -> Optional[ModelVersion]:
        """Get a specific model version."""
        return self.versions.get(version)
    
    def get_active_version(self) -> Optional[ModelVersion]:
        """Get the currently active model version."""
        if self.active_version:
            return self.versions.get(self.active_version)
        return None
    
    def set_active_version(self, version: str, load: bool = True):
        """
        Set the active model version.
        
        Args:
            version: Version to activate
            load: Whether to load the model immediately
        """
        if version not in self.versions:
            raise ValueError(f"Version {version} not found")
        
        old_version = self.active_version
        self.active_version = version
        
        if load:
            model_version = self.versions[version]
            if not model_version.is_loaded():
                model_version.load()
        
        self._save_config()
        
        logger.info(f"Active version changed: {old_version} -> {version}")
    
    def list_versions(self) -> List[Dict]:
        """List all registered model versions."""
        return [
            {
                **v.to_dict(),
                "is_active": v.version == self.active_version,
            }
            for v in self.versions.values()
        ]
    
    def delete_version(self, version: str, delete_files: bool = False):
        """
        Delete a model version.
        
        Args:
            version: Version to delete
            delete_files: Whether to delete model files from disk
        """
        if version not in self.versions:
            raise ValueError(f"Version {version} not found")
        
        if version == self.active_version:
            raise ValueError("Cannot delete active version")
        
        model_version = self.versions[version]
        
        if delete_files:
            try:
                os.remove(model_version.model_path)
                os.remove(model_version.tfidf_path)
                logger.info(f"Deleted model files for version {version}")
            except Exception as e:
                logger.warning(f"Failed to delete model files: {e}")
        
        del self.versions[version]
        self._save_config()
        
        logger.info(f"Deleted model version {version}")
    
    def rollback(self, target_version: Optional[str] = None):
        """
        Rollback to a previous model version.
        
        Args:
            target_version: Version to rollback to (if None, uses previous version)
        """
        if target_version:
            self.set_active_version(target_version, load=True)
        else:
            # Find previous version (by registration order)
            versions_list = list(self.versions.keys())
            if len(versions_list) < 2:
                raise ValueError("No previous version available for rollback")
            
            current_idx = versions_list.index(self.active_version)
            if current_idx == 0:
                raise ValueError("Already at oldest version")
            
            previous_version = versions_list[current_idx - 1]
            self.set_active_version(previous_version, load=True)
        
        logger.info(f"Rolled back to version {self.active_version}")
    
    def deploy_new_version(
        self,
        version: str,
        model_file: str,
        tfidf_file: str,
        metadata: Optional[Dict] = None,
        activate: bool = True,
    ) -> ModelVersion:
        """
        Deploy a new model version.
        
        Copies model files to the models directory and registers the version.
        
        Args:
            version: Version identifier
            model_file: Source model file path
            tfidf_file: Source TF-IDF file path
            metadata: Optional metadata
            activate: Whether to activate immediately
            
        Returns:
            ModelVersion instance
        """
        # Create version directory
        version_dir = self.models_dir / version
        version_dir.mkdir(exist_ok=True)
        
        # Copy model files
        model_dest = version_dir / "model.pkl"
        tfidf_dest = version_dir / "tfidf.pkl"
        
        shutil.copy2(model_file, model_dest)
        shutil.copy2(tfidf_file, tfidf_dest)
        
        logger.info(f"Copied model files to {version_dir}")
        
        # Register version
        model_version = self.register_version(
            version=version,
            model_path=str(model_dest),
            tfidf_path=str(tfidf_dest),
            metadata=metadata,
            set_active=activate,
        )
        
        if activate:
            model_version.load()
        
        logger.info(f"Deployed model version {version}")
        return model_version


# Global model manager instance
_model_manager: Optional[ModelManager] = None


def get_model_manager(models_dir: str = "models") -> ModelManager:
    """
    Get global model manager instance.
    
    Args:
        models_dir: Directory containing model versions
        
    Returns:
        ModelManager instance
    """
    global _model_manager
    
    if _model_manager is None:
        _model_manager = ModelManager(models_dir)
    
    return _model_manager
