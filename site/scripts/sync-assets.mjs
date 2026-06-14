// Copy the site-kit brand assets into the showcase site's public path.
//
// The kit's Nav/Footer/Layout reference the brand glyph at
// /_site-kit/weft-glyph.svg (and the favicon), so every consuming site must
// copy the kit's assets/* into public/_site-kit/ before build/dev. This runs
// automatically via the pre{dev,build} npm hooks. Resolved from the vendored
// @weft/site-kit (fetched by scripts/fetch-site-kit.mjs into vendor/site-kit/)
// or the installed package in node_modules.
import { cp, mkdir } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const here = dirname(fileURLToPath(import.meta.url));
const siteRoot = join(here, '..');

// Prefer the installed package; fall back to the vendored fetch.
const candidates = [
  join(siteRoot, 'node_modules', '@weft', 'site-kit', 'assets'),
  join(siteRoot, 'vendor', 'site-kit', 'assets'),
];
const src = candidates.find((p) => existsSync(p));
if (!src) {
  console.error('[sync-assets] could not find @weft/site-kit/assets in any of:\n  ' + candidates.join('\n  '));
  console.error('[sync-assets] run `npm run fetch-site-kit` first (or `npm install`).');
  process.exit(1);
}

const dest = join(siteRoot, 'public', '_site-kit');
await mkdir(dest, { recursive: true });
await cp(src, dest, { recursive: true });
console.log(`[sync-assets] copied ${src} -> ${dest}`);
