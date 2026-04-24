#!/usr/bin/env node
// Fetches aliases from Google Sheet and merges them into data.json
// Run via GitHub Actions on a schedule, or manually

const fs = require('fs');
const https = require('https');

const ALIASES_URL = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vRPBDTtNa5mZMaRpVkHIGF26iXZBr1AU6XQpTV3JX8M6MawD8jXlRZbrQlvOqxKjqahHEpamMpYgJBh/pub?gid=1248367953&single=true&output=csv';

function fetchCSV(url) {
  return new Promise((resolve, reject) => {
    const fetch = (u) => {
      https.get(u, (res) => {
        if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
          fetch(res.headers.location);
          return;
        }
        let data = '';
        res.on('data', chunk => data += chunk);
        res.on('end', () => resolve(data));
      }).on('error', reject);
    };
    fetch(url);
  });
}

function parseAliases(csv) {
  const lines = csv.split('\n');
  const nameAliases = {};
  const athleteAliases = {};

  for (let i = 1; i < lines.length; i++) {
    const line = lines[i].trim();
    if (!line) continue;

    const parts = line.split(',').map(p => p.trim().replace(/^"|"$/g, ''));
    if (parts.length < 2) continue;

    const canonical = parts[0];
    if (!canonical) continue;

    const aliases = [];
    for (let j = 1; j < parts.length; j++) {
      const alias = parts[j];
      if (alias) {
        nameAliases[alias.toLowerCase()] = canonical;
        aliases.push(alias);
      }
    }
    if (aliases.length > 0) {
      athleteAliases[canonical] = aliases;
    }
  }

  return { nameAliases, athleteAliases };
}

async function main() {
  const dataFile = process.argv[2] || 'files/data.json';

  console.log('Fetching aliases from Google Sheet...');
  const csv = await fetchCSV(ALIASES_URL);
  const sheet = parseAliases(csv);
  console.log(`Parsed ${Object.keys(sheet.nameAliases).length} name aliases, ${Object.keys(sheet.athleteAliases).length} athletes`);

  const data = JSON.parse(fs.readFileSync(dataFile, 'utf8'));

  // Merge nameAliases: sheet values take precedence
  if (!data.nameAliases) data.nameAliases = {};
  Object.entries(sheet.nameAliases).forEach(([alias, canonical]) => {
    data.nameAliases[alias] = canonical;
  });

  // Merge athleteAliases: combine alias lists, sheet values take precedence for canonical name
  if (!data.athleteAliases) data.athleteAliases = {};
  Object.entries(sheet.athleteAliases).forEach(([canonical, aliases]) => {
    const existing = data.athleteAliases[canonical] || [];
    const merged = [...new Set([...existing, ...aliases])];
    data.athleteAliases[canonical] = merged;
  });

  fs.writeFileSync(dataFile, JSON.stringify(data, null, null).replace(/,"/g, ',"').replace(/:{/g, ':{'));
  // Write minified
  fs.writeFileSync(dataFile, JSON.stringify(data));

  console.log(`Updated ${dataFile}`);
}

main().catch(e => { console.error(e); process.exit(1); });
