#!/usr/bin/env node
/**
 * Transforme un JSON complet (export box-positionner) en plusieurs JSON
 * "un niveau" : un fichier par boîte non feuille, contenant uniquement
 * ses enfants directs avec coordonnées relatives au parent.
 *
 * Usage: node split-layouts.js <fichier-complet.json> [--out <dossier>] [--root <nom>]
 *
 * Fichiers générés:
 *   - Pour chaque boîte non feuille: <nom-boite>_layout.json (ou box-<id>_layout.json)
 *   - Si --root <nom>: <nom>_layout.json avec les boîtes racine (niveau écran)
 */

const fs = require('fs');
const path = require('path');

function slugify(name) {
  if (name == null || String(name).trim() === '') return null;
  return String(name)
    .trim()
    .toLowerCase()
    .normalize('NFD')
    .replace(/\p{Diacritic}/gu, '')
    .replace(/[\s_]+/g, '-')
    .replace(/[^a-z0-9-]/g, '')
    .replace(/-+/g, '-')
    .replace(/^-|-$/g, '') || null;
}

function getNonLeafBoxIds(boxes) {
  const parentIds = new Set();
  for (const b of boxes) {
    if (b.parentId != null) parentIds.add(b.parentId);
  }
  return parentIds;
}

function getRelativeCoords(child, parent) {
  // L'outil exporte déjà parent: { parentId, xPct, yPct, wPct, hPct } → on les réutilise
  if (child.parent && child.parent.parentId === parent.id) {
    const p = child.parent;
    return {
      xPct: Number(p.xPct),
      yPct: Number(p.yPct),
      wPct: Number(p.wPct),
      hPct: Number(p.hPct),
    };
  }
  // Secours si pas de parent dans le JSON : recalcul à partir des absolus
  const pw = parent.wPct ?? 0;
  const ph = parent.hPct ?? 0;
  if (pw <= 0 || ph <= 0) return null;
  return {
    xPct: +(((child.xPct ?? 0) - (parent.xPct ?? 0)) / pw * 100).toFixed(2),
    yPct: +(((child.yPct ?? 0) - (parent.yPct ?? 0)) / ph * 100).toFixed(2),
    wPct: +((child.wPct ?? 0) / pw * 100).toFixed(2),
    hPct: +((child.hPct ?? 0) / ph * 100).toFixed(2),
  };
}

function buildChildEntry(child, parent) {
  const rel = getRelativeCoords(child, parent);
  if (rel == null) return null;
  return {
    id: child.id,
    ...(child.name != null && child.name !== '' ? { name: child.name } : {}),
    ...rel,
  };
}

function main() {
  const args = process.argv.slice(2);
  let inputPath = null;
  let outDir = null;
  let rootFileName = null;

  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--out' && args[i + 1]) {
      outDir = args[++i];
    } else if (args[i] === '--root' && args[i + 1]) {
      rootFileName = args[++i];
    } else if (!args[i].startsWith('-')) {
      inputPath = args[i];
    }
  }

  if (!inputPath) {
    console.error('Usage: node split-layouts.js <fichier-complet.json> [--out <dossier>] [--root <nom>]');
    process.exit(1);
  }

  const absInput = path.resolve(inputPath);
  if (!fs.existsSync(absInput)) {
    console.error('Fichier introuvable:', absInput);
    process.exit(1);
  }

  if (outDir == null) {
    outDir = path.join(path.dirname(absInput), 'layouts');
  }
  const absOut = path.resolve(outDir);

  let boxes;
  try {
    const raw = fs.readFileSync(absInput, 'utf8');
    boxes = JSON.parse(raw);
  } catch (e) {
    console.error('Erreur lecture/JSON:', e.message);
    process.exit(1);
  }

  if (!Array.isArray(boxes)) {
    console.error('Le JSON doit être un tableau de boîtes.');
    process.exit(1);
  }

  const byId = new Map(boxes.map(b => [b.id, b]));
  const nonLeafIds = getNonLeafBoxIds(boxes);

  if (!fs.existsSync(absOut)) {
    fs.mkdirSync(absOut, { recursive: true });
  }

  let written = 0;

  if (rootFileName != null) {
    const roots = boxes
      .filter(b => b.parentId == null)
      .map(b => ({
        id: b.id,
        ...(b.name != null && b.name !== '' ? { name: b.name } : {}),
        xPct: +(Number(b.xPct).toFixed(2)),
        yPct: +(Number(b.yPct).toFixed(2)),
        wPct: +(Number(b.wPct).toFixed(2)),
        hPct: +(Number(b.hPct).toFixed(2)),
      }));
    if (roots.length > 0) {
      const name = rootFileName.replace(/\.json$/i, '').replace(/_layout$/i, '');
      const outPath = path.join(absOut, `${name}_layout.json`);
      fs.writeFileSync(outPath, JSON.stringify(roots, null, 2), 'utf8');
      console.log(outPath);
      written++;
    }
  }
  for (const parentId of nonLeafIds) {
    const parent = byId.get(parentId);
    if (!parent) continue;

    const children = boxes.filter(b => b.parentId === parent.id);
    const entries = [];
    for (const child of children) {
      const entry = buildChildEntry(child, parent);
      if (entry) entries.push(entry);
    }
    if (entries.length === 0) continue;

    const baseName = slugify(parent.name) || `box-${parent.id}`;
    const fileName = `${baseName}_layout.json`;
    const outPath = path.join(absOut, fileName);

    fs.writeFileSync(outPath, JSON.stringify(entries, null, 2), 'utf8');
    console.log(outPath);
    written++;
  }

  console.error(`${written} fichier(s) généré(s) dans ${absOut}`);
}

main();
