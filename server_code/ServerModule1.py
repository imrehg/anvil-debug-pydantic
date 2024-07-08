from __future__ import annotations

import anvil.server

import json
from pydantic import BaseModel, ConfigDict, Field
from typing import Any, ClassVar, Dict, List, Optional, Union, Set
from enum import Enum
from typing_extensions import Annotated, Self

class VariableType(str, Enum):
    """
    allowed enum values
    """
    MEAN = 'mean'
    VARIANCE = 'variance'
    STANDARD_ERROR_OF_MEAN = 'standard_error_of_mean'
    QUANTILE = 'quantile'

    @classmethod
    def from_json(cls, json_str: str) -> Self:
        """Create an instance of VariableType from a JSON string"""
        return cls(json.loads(json_str))

class CustomVariable(BaseModel):
    type: VariableType = Field(description="Custom Variable type")
    quantile: Optional[Union[Annotated[float, Field(le=1.0, strict=True, ge=0.0)], Annotated[int, Field(le=1, strict=True, ge=0)]]] = None
    __properties: ClassVar[List[str]] = ["type", "quantile"]

    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        protected_namespaces=(),
    )

    def to_str(self) -> str:
        """Returns the string representation of the model using alias"""
        return pprint.pformat(self.model_dump(by_alias=True))

    def to_json(self) -> str:
        """Returns the JSON representation of the model using alias"""
        # TODO: pydantic v2: use .model_dump_json(by_alias=True, exclude_unset=True) instead
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> Optional[Self]:
        """Create an instance of CustomVariable from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self) -> Dict[str, Any]:
        """Return the dictionary representation of the model using alias.

        This has the following differences from calling pydantic's
        `self.model_dump(by_alias=True)`:

        * `None` is only added to the output dict for nullable fields that
          were set at model initialization. Other fields with value `None`
          are ignored.
        """
        excluded_fields: Set[str] = set([
        ])

        _dict = self.model_dump(
            by_alias=True,
            exclude=excluded_fields,
            exclude_none=True,
        )
        # set to None if quantile (nullable) is None
        # and model_fields_set contains the field
        if self.quantile is None and "quantile" in self.model_fields_set:
            _dict['quantile'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of CustomVariable from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "type": obj.get("type"),
            "quantile": obj.get("quantile")
        })
        return _obj


@anvil.server.callable
def trigger():
    input = CustomVariable(type=VariableType.QUANTILE, quantile=0.5)
    
    # Have to work around to serialise into JSON and then deserialise on the other end
    input_json = input.to_json()
    anvil.server.launch_background_task('background', input_json=input_json)

    # Or serialise to a dict
    input_dict = input.to_dict()
    anvil.server.launch_background_task('background', input_dict=input_dict)

    # Expected this to work
    anvil.server.launch_background_task('background', input=input)

@anvil.server.background_task
def background(
    input: CustomVariable | None = None,
    input_json: str | None = None,
    input_dict: dict[str, Any] | None = None):
    
    if input_json is not None:
        input = CustomVariable.from_json(input_json)
        print(f"From JSON: {input}")
    elif input_dict is not None:
        input = CustomVariable.from_dict(input_dict)
        print(f"From dict: {input}")
    else:
        print(f"From bare: {input}")