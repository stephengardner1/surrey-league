#!/usr/bin/env node
/**
 * Surrey League Weather Fetcher
 * 
 * Fetches historical weather from Open-Meteo API and merges directly into data.json
 * Only fetches for races with exact ISO dates (e.g., "2024-10-12")
 * Uses 2pm (14:00) hourly data for race conditions
 * 
 * Usage: node fetch-weather-merge.js [data.json]
 */

const fs = require('fs');

// ============================================================
// VENUE COORDINATES
// ============================================================

const VENUE_COORDINATES = {
  // Current and recent venues
  "Wimbledon Common": { lat: 51.4347, lon: -0.2217 },
  "Beckenham Place Park": { lat: 51.4235, lon: -0.0154 },
  "Richmond Park": { lat: 51.4427, lon: -0.2752 },
  "Mitcham Common": { lat: 51.3962, lon: -0.1545 },
  "Lloyd Park": { lat: 51.3753, lon: -0.0789 },
  "Epsom Downs": { lat: 51.3148, lon: -0.2389 },
  "Hurst Green": { lat: 51.2464, lon: -0.0028 },
  "West Horsley Place": { lat: 51.2580, lon: -0.4380 },
  "Effingham Common": { lat: 51.2833, lon: -0.4167 },
  
  // Historic venues
  "Addington": { lat: 51.3614, lon: -0.0431 },
  "Aldershot": { lat: 51.2480, lon: -0.7600 },
  "Brockwell Park": { lat: 51.4500, lon: -0.1089 },
  "Coulsdon": { lat: 51.3189, lon: -0.1378 },
  "Croydon": { lat: 51.3753, lon: -0.0789 },
  "Denbies Vineyard": { lat: 51.2458, lon: -0.3497 },
  "Dorking": { lat: 51.2333, lon: -0.3333 },
  "Esher": { lat: 51.3689, lon: -0.3642 },
  "Farthing Downs": { lat: 51.3033, lon: -0.1278 },
  "Farthing Downs, Coulsdon": { lat: 51.3033, lon: -0.1278 },
  "Fleet": { lat: 51.2833, lon: -0.8333 },
  "Ham Lands": { lat: 51.4350, lon: -0.3150 },
  "Hayes": { lat: 51.3750, lon: 0.0139 },
  "Kingston Vale": { lat: 51.4300, lon: -0.2600 },
  "Milford": { lat: 51.1600, lon: -0.6500 },
  "Morden Park": { lat: 51.3900, lon: -0.2000 },
  "Newlands Corner": { lat: 51.2200, lon: -0.5000 },
  "Petersham": { lat: 51.4400, lon: -0.2900 },
  "Priory Park, Reigate": { lat: 51.2378, lon: -0.2067 },
  "Putney Vale": { lat: 51.4400, lon: -0.2350 },
  "Reigate": { lat: 51.2378, lon: -0.2067 },
  "Reigate Priory Park": { lat: 51.2378, lon: -0.2067 },
  "Streatham Common": { lat: 51.4278, lon: -0.1333 },
  "Walton": { lat: 51.3864, lon: -0.4136 },
  "West Wickham": { lat: 51.3753, lon: -0.0150 },
  "Woking": { lat: 51.3167, lon: -0.5500 },
};

// ============================================================
// WMO WEATHER CODES
// ============================================================

const WEATHER_CODES = {
  0: { icon: "☀️", description: "Clear", category: "sun" },
  1: { icon: "🌤️", description: "Mainly clear", category: "sun" },
  2: { icon: "⛅", description: "Partly cloudy", category: "cloud" },
  3: { icon: "☁️", description: "Overcast", category: "cloud" },
  45: { icon: "🌫️", description: "Fog", category: "fog" },
  48: { icon: "🌫️", description: "Rime fog", category: "fog" },
  51: { icon: "🌧️", description: "Light drizzle", category: "rain" },
  53: { icon: "🌧️", description: "Drizzle", category: "rain" },
  55: { icon: "🌧️", description: "Heavy drizzle", category: "rain" },
  56: { icon: "🌧️", description: "Freezing drizzle", category: "rain" },
  57: { icon: "🌧️", description: "Heavy freezing drizzle", category: "rain" },
  61: { icon: "🌧️", description: "Light rain", category: "rain" },
  63: { icon: "🌧️", description: "Rain", category: "rain" },
  65: { icon: "🌧️", description: "Heavy rain", category: "rain" },
  66: { icon: "🌧️", description: "Freezing rain", category: "rain" },
  67: { icon: "🌧️", description: "Heavy freezing rain", category: "rain" },
  71: { icon: "🌨️", description: "Light snow", category: "snow" },
  73: { icon: "🌨️", description: "Snow", category: "snow" },
  75: { icon: "❄️", description: "Heavy snow", category: "snow" },
  77: { icon: "🌨️", description: "Snow grains", category: "snow" },
  80: { icon: "🌦️", description: "Light showers", category: "rain" },
  81: { icon: "🌦️", description: "Showers", category: "rain" },
  82: { icon: "🌧️", description: "Heavy showers", category: "rain" },
  85: { icon: "🌨️", description: "Light snow showers", category: "snow" },
  86: { icon: "❄️", description: "Heavy snow showers", category: "snow" },
  95: { icon: "⛈️", description: "Thunderstorm", category: "storm" },
  96: { icon: "⛈️", description: "Thunderstorm with hail", category: "storm" },
  99: { icon: "⛈️", description: "Thunderstorm with heavy hail", category: "storm" },
};

// ============================================================
// HELPERS
// ============================================================

function hasExactDate(dateStr) {
  return dateStr && dateStr.match(/^\d{4}-\d{2}-\d{2}$/);
}

function getVenueCoordinates(venueName) {
  if (VENUE_COORDINATES[venueName]) {
    return VENUE_COORDINATES[venueName];
  }
  
  const lower = venueName.toLowerCase();
  for (const [key, coords] of Object.entries(VENUE_COORDINATES)) {
    if (key.toLowerCase() === lower) return coords;
  }
  
  for (const [key, coords] of Object.entries(VENUE_COORDINATES)) {
    if (key.toLowerCase().includes(lower) || lower.includes(key.toLowerCase())) {
      return coords;
    }
  }
  
  return null;
}

// ============================================================
// API FETCHING - Hourly data at 2pm
// ============================================================

async function fetchWeather(lat, lon, date) {
  const url = `https://archive-api.open-meteo.com/v1/archive?` +
    `latitude=${lat}&longitude=${lon}` +
    `&start_date=${date}&end_date=${date}` +
    `&hourly=temperature_2m,weather_code,wind_speed_10m` +
    `&timezone=Europe/London`;
  
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }
  
  const data = await response.json();
  
  if (!data.hourly || !data.hourly.time || data.hourly.time.length === 0) {
    return null;
  }
  
  // Find the 14:00 (2pm) index
  const targetHour = 14;
  const hourIndex = data.hourly.time.findIndex(t => t.endsWith(`T${String(targetHour).padStart(2, '0')}:00`));
  
  if (hourIndex === -1) {
    return null;
  }
  
  const temp = data.hourly.temperature_2m[hourIndex];
  const weatherCode = data.hourly.weather_code[hourIndex];
  const windSpeed = data.hourly.wind_speed_10m[hourIndex];
  
  const weatherInfo = WEATHER_CODES[weatherCode] || { icon: "❓", description: "Unknown", category: "unknown" };
  
  return {
    temp: Math.round(temp),
    windSpeed: Math.round(windSpeed),
    weatherCode: weatherCode,
    icon: weatherInfo.icon,
    description: weatherInfo.description,
    category: weatherInfo.category
  };
}

// ============================================================
// MAIN SCRIPT
// ============================================================

async function main() {
  console.log('Surrey League Weather Fetcher');
  console.log('==============================\n');
  
  const DATA_FILE = process.argv[2] || './data.json';
  const API_DELAY = 200;
  
  if (!fs.existsSync(DATA_FILE)) {
    console.error(`Data file not found: ${DATA_FILE}`);
    process.exit(1);
  }
  
  const data = JSON.parse(fs.readFileSync(DATA_FILE, 'utf8'));
  console.log(`Loaded ${data.races.length} races from ${DATA_FILE}\n`);
  
  // Find races with exact dates
  const racesWithDates = data.races.filter(r => hasExactDate(r.date));
  console.log(`${racesWithDates.length} races have exact dates\n`);
  
  // Find unknown venues
  const unknownVenues = new Set();
  for (const race of racesWithDates) {
    if (!getVenueCoordinates(race.venue)) {
      unknownVenues.add(race.venue);
    }
  }
  
  if (unknownVenues.size > 0) {
    console.log('⚠️  Unknown venues (need coordinates):');
    unknownVenues.forEach(v => console.log(`   - "${v}"`));
    console.log();
  }
  
  // Filter races to fetch
  const maxDate = new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
  
  const toFetch = racesWithDates.filter(race => {
    if (race.weather) return false; // Already has weather
    const coords = getVenueCoordinates(race.venue);
    if (!coords) return false;
    if (race.date > maxDate) return false; // Future or too recent
    return true;
  });
  
  console.log(`${toFetch.length} races need weather data\n`);
  
  if (toFetch.length === 0) {
    console.log('All eligible races already have weather data!');
    return;
  }
  
  let success = 0, errors = 0;
  
  for (let i = 0; i < toFetch.length; i++) {
    const race = toFetch[i];
    const coords = getVenueCoordinates(race.venue);
    
    process.stdout.write(`[${i + 1}/${toFetch.length}] ${race.season} M${race.match} (${race.date}) @ ${race.venue}... `);
    
    try {
      const weather = await fetchWeather(coords.lat, coords.lon, race.date);
      
      if (weather) {
        const raceIdx = data.races.findIndex(r => r.season === race.season && r.match === race.match);
        if (raceIdx >= 0) {
          data.races[raceIdx].weather = weather;
        }
        console.log(`${weather.icon} ${weather.temp}°C ${weather.windSpeed}km/h`);
        success++;
      } else {
        console.log('⚠️  No data');
        errors++;
      }
    } catch (err) {
      console.log(`❌ ${err.message}`);
      errors++;
    }
    
    await new Promise(r => setTimeout(r, API_DELAY));
    
    if ((i + 1) % 50 === 0) {
      fs.writeFileSync(DATA_FILE, JSON.stringify(data));
      console.log(`   💾 Saved progress`);
    }
  }
  
  fs.writeFileSync(DATA_FILE, JSON.stringify(data));
  
  console.log('\n==============================');
  console.log(`✅ Success: ${success}`);
  console.log(`❌ Errors: ${errors}`);
  console.log(`📁 Updated: ${DATA_FILE}`);
}

main().catch(console.error);
