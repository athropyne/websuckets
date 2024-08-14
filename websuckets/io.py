from websuckets.models import OutputModel
from websuckets.types import IO_TYPE


def ClientEvent(event: str, payload: IO_TYPE | None) -> str:
    return OutputModel(event=event, payload=payload).model_dump_json()
