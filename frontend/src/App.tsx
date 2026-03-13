import React, { useEffect, useRef, useState } from 'react';
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import { api } from './services/api';
import type { Country, GeoJSONResponse } from './types';
import './App.css';

// Цвета для разных типов виз
const visaColors: Record<string, string> = {
  visa_free: '#2ecc71',      // зелёный
  visa_on_arrival: '#f1c40f', // жёлтый
  evisa: '#e67e22',           // оранжевый
  embassy: '#e74c3c',         // красный
  restricted: '#9b59b6',      // фиолетовый
  unknown: '#95a5a6',         // серый
};

function App() {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<maplibregl.Map | null>(null);
  const [countries, setCountries] = useState<Country[]>([]);
  const [selectedCitizenship, setSelectedCitizenship] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);

  // Загружаем список стран для выпадающего списка
  useEffect(() => {
    const loadCountries = async () => {
      try {
        const data = await api.getCountriesList();
        setCountries(data);
      } catch (error) {
        console.error('Failed to load countries list:', error);
      }
    };
    loadCountries();
  }, []);

  // Инициализация карты
  useEffect(() => {
    if (map.current || !mapContainer.current) return;

    map.current = new maplibregl.Map({
      container: mapContainer.current,
      style: 'https://basemaps.cartocdn.com/gl/positron-gl-style/style.json', // светлая тема
      center: [0, 20],
      zoom: 1.5,
    });

    map.current.addControl(new maplibregl.NavigationControl(), 'top-right');

    // Ждём загрузки карты
    map.current.on('load', async () => {
      setLoading(false);
      
      try {
        // Загружаем GeoJSON с границами стран
        const geojson = await api.getCountriesGeoJSON();
        
        // Добавляем источник данных
        map.current!.addSource('countries', {
          type: 'geojson',
          data: geojson,
        });

        // Добавляем слой заливки
        map.current!.addLayer({
          id: 'country-fills',
          type: 'fill',
          source: 'countries',
          paint: {
            'fill-color': [
              'match',
              ['get', 'visa_type'],
              'visa_free', visaColors.visa_free,
              'visa_on_arrival', visaColors.visa_on_arrival,
              'evisa', visaColors.evisa,
              'embassy', visaColors.embassy,
              'restricted', visaColors.restricted,
              visaColors.unknown
            ],
            'fill-opacity': 0.7,
            'fill-outline-color': '#ffffff',
          },
        });

        // Добавляем слой границ
        map.current!.addLayer({
          id: 'country-borders',
          type: 'line',
          source: 'countries',
          paint: {
            'line-color': '#2c3e50',
            'line-width': 0.5,
          },
        });

        // Добавляем всплывающие подсказки при наведении
        map.current!.on('mousemove', 'country-fills', (e) => {
          if (e.features && e.features.length > 0) {
            const feature = e.features[0];
            const props = feature.properties as any;
            map.current!.getCanvas().style.cursor = 'pointer';
            
            // Создаём popup с информацией о стране
            new maplibregl.Popup({ closeButton: false })
              .setLngLat(e.lngLat)
              .setHTML(`
                <strong>${props.name}</strong><br/>
                Visa type: ${props.visa_type?.replace(/_/g, ' ') || 'unknown'}
              `)
              .addTo(map.current!);
          }
        });

        map.current!.on('mouseleave', 'country-fills', () => {
          map.current!.getCanvas().style.cursor = '';
          // Удаляем все popup'ы
          const popups = document.getElementsByClassName('maplibregl-popup');
          while (popups[0]) {
            popups[0].remove();
          }
        });

      } catch (error) {
        console.error('Failed to load GeoJSON:', error);
      }
    });

  }, []);

  // Обработчик изменения гражданства
  const handleCitizenshipChange = async (e: React.ChangeEvent<HTMLSelectElement>) => {
    const isoCode = e.target.value;
    setSelectedCitizenship(isoCode);
    
    if (!isoCode) return;
    
    try {
      // Получаем типы виз для выбранного гражданства
      const visaData = await api.getVisaTypesForCitizenship(isoCode);
      
      // Обновляем слой на карте с новыми цветами
      if (map.current && map.current.getLayer('country-fills')) {
        map.current.setPaintProperty('country-fills', 'fill-color', [
          'match',
          ['get', 'visa_type'],
          ...Object.entries(visaData).flatMap(([type, color]) => [type, color]),
          visaColors.unknown
        ]);
      }
    } catch (error) {
      console.error('Failed to load visa types:', error);
    }
  };

  return (
    <div style={{ position: 'relative', width: '100vw', height: '100vh' }}>
      <div ref={mapContainer} style={{ width: '100%', height: '100%' }} />
      
      {/* Контроллер выбора гражданства */}
      <div style={{
        position: 'absolute',
        top: 20,
        left: 20,
        zIndex: 1,
        background: 'white',
        padding: '15px 20px',
        borderRadius: '8px',
        boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
        maxWidth: '300px',
      }}>
        <h3 style={{ margin: '0 0 10px 0', color: '#2c3e50' }}>🌍 Visa Map</h3>
        <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
          Your citizenship:
        </label>
        <select
          value={selectedCitizenship}
          onChange={handleCitizenshipChange}
          style={{
            width: '100%',
            padding: '8px',
            borderRadius: '4px',
            border: '1px solid #bdc3c7',
            fontSize: '14px',
          }}
        >
          <option value="">Select your country</option>
          {countries.map((country) => (
            <option key={country.iso_code} value={country.iso_code}>
              {country.name}
            </option>
          ))}
        </select>

        {/* Легенда */}
        <div style={{ marginTop: '15px' }}>
          <h4 style={{ margin: '0 0 8px 0', fontSize: '14px', color: '#7f8c8d' }}>Legend:</h4>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '5px' }}>
            {Object.entries(visaColors).map(([type, color]) => (
              <div key={type} style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                <div style={{ width: '12px', height: '12px', backgroundColor: color, borderRadius: '3px' }} />
                <span style={{ fontSize: '12px', textTransform: 'capitalize' }}>
                  {type.replace(/_/g, ' ')}
                </span>
              </div>
            ))}
          </div>
        </div>

        {loading && (
          <div style={{ marginTop: '10px', color: '#3498db' }}>
            Loading map...
          </div>
        )}
      </div>
    </div>
  );
}

export default App;