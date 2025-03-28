"""Provider factory implementation"""

from typing import Dict, Any
from providers.file import FileProvider
from providers.iso import IsoProvider
from providers.image import ImageProvider
from .base import BaseProvider


def get_provider(inputs: Dict[str, Any]) -> BaseProvider:
    """
    ## Factory function to create the appropriate provider
    ### Args:
        inputs: Dictionary of input parameters
    ### Returns:
        An instance of the appropriate provider
    """

    _type_to_provider = {
        "iso": IsoProvider,
        "image": ImageProvider,
        "file": FileProvider,
    }

    if inputs.get("target_type") in _type_to_provider:
        provider_class = _type_to_provider[inputs["target_type"]]
        return provider_class(inputs)

    raise ValueError(f"Unsupported target type: {inputs['target_type']}")
