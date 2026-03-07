from pydantic import BaseModel, ConfigDict


class CountryBase(BaseModel):
    name: str
    iso_code: str
    visa_type: str | None = None


class CountryDetail(CountryBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
