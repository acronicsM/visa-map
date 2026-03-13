import axios from 'axios';
import type { GeoJSONResponse, Country } from '../types';

const API_BASE_URL = 'http://127.0.0.1:8000';

export const api = {
  // Получить GeoJSON всех стран
  getCountriesGeoJSON: async (): Promise<GeoJSONResponse> => {
    const response = await axios.get(`${API_BASE_URL}/countries.geojson`);
    return response.data;
  },

  // Получить список стран (для выпадающего списка)
  getCountriesList: async (): Promise<Country[]> => {
    const response = await axios.get(`${API_BASE_URL}/countries`);
    return response.data;
  },

  // Получить типы виз для конкретного гражданства
  getVisaTypesForCitizenship: async (citizenshipIso: string): Promise<Record<string, string>> => {
    const response = await axios.get(`${API_BASE_URL}/visa-types/${citizenshipIso}`);
    return response.data;
  }
};