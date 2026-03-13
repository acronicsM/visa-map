export interface Country {
  name: string;
  iso_code: string;
  visa_type: string;
}

export interface CountryFeature {
  type: 'Feature';
  geometry: {
    type: string;
    coordinates: any;
  };
  properties: Country;
}

export interface GeoJSONResponse {
  type: 'FeatureCollection';
  features: CountryFeature[];
}