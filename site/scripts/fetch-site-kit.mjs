// Sparse-fetch the shared @weft/site-kit out of the weft hub repo into
// vendor/site-kit/, so this site can depend on it as a `file:` dependency.
//
// WHY: the kit lives in a SUBDIRECTORY (packages/site-kit) of a DIFFERENT repo
// (foundryside-dev/weft). npm cannot install a git subdirectory dependency
// directly, so the sanctioned realization of the "git subdirectory dependency"
// decision (IA §1.3, §6) is: sparse-checkout just that subdirectory and vendor
// it locally. The vendor copy is gitignored and regenerated on every
// install/build — never hand-maintained, never committed, never a submodule.
//
// This runs as the `preinstall` hook (so the file: dep resolves) and is also
// invoked explicitly by the deploy workflow before `npm install`.
import { execFileSync } from 'node:child_process';
import { cp, rm, mkdir } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import { tmpdir } from 'node:os';

const here = dirname(fileURLToPath(import.meta.url));
const siteRoot = join(here, '..');
const vendorDir = join(siteRoot, 'vendor', 'site-kit');

const REPO = process.env.WEFT_SITE_KIT_REPO || 'https://github.com/foundryside-dev/weft.git';
const REF = process.env.WEFT_SITE_KIT_REF || 'main';
const SUBDIR = 'packages/site-kit';

// Local-dev escape hatch: if the weft repo is checked out next to lacuna, copy
// from there instead of hitting the network (keeps offline builds working).
const LOCAL_KIT = join(siteRoot, '..', '..', 'weft', 'packages', 'site-kit');

function run(cmd, args, cwd) {
  execFileSync(cmd, args, { cwd, stdio: 'inherit' });
}

async function vendorFrom(src) {
  await rm(vendorDir, { recursive: true, force: true });
  await mkdir(dirname(vendorDir), { recursive: true });
  await cp(src, vendorDir, { recursive: true });
}

async function main() {
  if (existsSync(LOCAL_KIT)) {
    console.log(`[fetch-site-kit] vendoring from local checkout: ${LOCAL_KIT}`);
    await vendorFrom(LOCAL_KIT);
    console.log(`[fetch-site-kit] -> ${vendorDir}`);
    return;
  }

  const tmp = join(tmpdir(), `weft-site-kit-${process.pid}-${Date.now()}`);
  console.log(`[fetch-site-kit] sparse-fetching ${SUBDIR} from ${REPO}@${REF}`);
  try {
    run('git', ['clone', '--depth', '1', '--filter=blob:none', '--sparse', '--branch', REF, REPO, tmp]);
    run('git', ['sparse-checkout', 'set', SUBDIR], tmp);
    const src = join(tmp, SUBDIR);
    if (!existsSync(src)) {
      throw new Error(`expected ${SUBDIR} in the checkout but it was not found`);
    }
    await vendorFrom(src);
    console.log(`[fetch-site-kit] -> ${vendorDir}`);
  } finally {
    await rm(tmp, { recursive: true, force: true });
  }
}

main().catch((err) => {
  console.error('[fetch-site-kit] failed:', err.message);
  process.exit(1);
});
