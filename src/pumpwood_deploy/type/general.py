"""Default dataclass helpers for Pumpwood deploy."""
import dataclasses
from abc import ABC
from typing import ClassVar


class PumpwoodDeploySentinel(ABC):
    """Sentinel placeholder for missing dataclass values."""

    _RETURN_VALUE: str = ""
    """Default value returned by ``value``."""

    _HELP_TEXT: str = ""
    """Help text associated with the sentinel."""

    @classmethod
    def value(cls):
        """Return the sentinel default value.

        Returns:
            str:
                Configured default value for the sentinel class.
        """
        return cls._RETURN_VALUE

    @classmethod
    def help_text(cls):
        """Return the sentinel help text.

        Returns:
            str:
                Configured help text for the sentinel class.
        """
        return cls._HELP_TEXT


class PumpwoodDeployDataclassMixin(ABC):
    """Pumpwood dataclass mixin with dict-like access helpers.

    Instances can be read like mappings through ``obj['key']`` while
    preserving dataclass field semantics.
    """

    _RENAME_FIELDS: ClassVar[dict[str, str]] = {}
    """Field rename map applied when exporting to dictionaries."""

    def to_dict(self):
        """Convert the dataclass instance into a dictionary recursively.

        Returns:
            dict:
                Serialized field values with sentinel and nested
                dataclass handling applied.
        """
        clean_data = {}
        # Iterate over the fields of the current dataclass
        for field in dataclasses.fields(self):
            key = field.name
            value = getattr(self, key)

            # Rename the keys
            new_key = self._RENAME_FIELDS.get(key, key)
            clean_data[new_key] = self._process_value(value)
        return clean_data

    def _process_value(self, value):
        """Normalize nested values for dictionary export.

        Args:
            value (object):
                Field value to serialize.

        Returns:
            object:
                Serialized value with sentinel and nested dataclass
                handling applied.
        """
        # Handle Sentinels
        if isinstance(value, PumpwoodDeploySentinel):
            return value.value()

        # Handle Nested Pumpwood Dataclasses (Recursion)
        if isinstance(value, PumpwoodDeployDataclassMixin):
            return value.to_dict()

        # Handle Lists (check each element)
        if isinstance(value, list):
            return [
                self._process_value(item)
                for item in value]

        # Handle Dicts (check each value)
        if isinstance(value, dict):
            return {
                k: self._process_value(v)
                for k, v in value.items()}
        return value

    def __iter__(self):
        """Iterate over exported key-value pairs.

        Yields:
            tuple:
                Key and serialized value pairs from ``to_dict``.
        """
        for key, value in self.to_dict().items():
            yield key, value

    def __getitem__(self, key):
        """Return a dataclass field by name.

        Args:
            key (str):
                Dataclass field name.

        Returns:
            object:
                Value stored on the requested field.
        """
        return getattr(self, key)

    def keys(self):
        """Return dataclass field names.

        Returns:
            list[str]:
                Names of fields declared on the dataclass.
        """
        return [f.name for f in dataclasses.fields(self)]
