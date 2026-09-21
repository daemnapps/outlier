// Reusable run_script snippets for the Figma email format bank workflow.
// These are TESTED — every one ran in the <brand> build (see references/worked-example.md).
// Paste the body of the function you need into a run_script call and set the config at the top.
// Two hard constraints: run_script has a ~30s timeout and cannot define globals that survive
// across calls. Chunk board lists ~6 at a time and inline helpers every call.

// ─────────────────────────────────────────────────────────────
// 1. CLONE THE MASTER BOARD PAGE (workflow-a §6)
// Build + verify ONE board page, then generate the rest from it.
// ─────────────────────────────────────────────────────────────
async function cloneBoardPages() {
  const TEMPLATE = 'Format Bank - <MASTER BOARD>.dc.html';
  const MASTER_SLUG = '<master-slug>';
  const MASTER_GLOBAL = '<MasterGlobal>';
  const MASTER_TITLE = '<Master Board Title>';
  const MASTER_CODE = '<MCODE>';
  const MASTER_SUB = '<the exact subtitle string in the master file>';
  // [slug, globalName, boardTitle, code]
  const boards = [
    // ['jan-2025', 'January2025Campaign', 'January 2025 - Campaign', 'JAN25'],
  ];
  const tpl = await readFile(TEMPLATE);
  for (const [dir, global, title, code] of boards) {
    let f = tpl;
    f = replaceText(f, 'boards/' + MASTER_SLUG, 'boards/' + dir);
    f = replaceText(f, MASTER_GLOBAL, global);
    f = replaceText(f, '>' + MASTER_TITLE + '<', '>' + title + '<');
    f = replaceText(f, MASTER_SUB, 'Approved emails, 600px artboards, verbatim from Figma. Codes: ' + code + '-xx.');
    f = replaceText(f, MASTER_TITLE + ' board', title + ' board');
    f = replaceText(f, 'CODE = "' + MASTER_CODE + '"', 'CODE = "' + code + '"');
    await saveFile('Format Bank - ' + title + '.dc.html', f);
    if (f.includes(MASTER_SLUG)) log('WARN residual master slug in ' + dir);
  }
  log('wrote ' + boards.length + ' board pages');
}

// ─────────────────────────────────────────────────────────────
// 2. INJECT fonts.css INTO EVERY PAGE (workflow-a §4)
// ─────────────────────────────────────────────────────────────
async function linkFonts() {
  const files = (await ls('')).filter(f => f.endsWith('.dc.html'));
  let n = 0;
  for (const p of files) {
    let f = await readFile(p);
    if (f.includes('fonts.css')) continue;
    const i = f.indexOf('<style>');
    if (i < 0) { log('no <style> in ' + p); continue; }
    f = f.slice(0, i) + '<link rel="stylesheet" href="fonts.css">\n' + f.slice(i);
    await saveFile(p, f); n++;
  }
  log('linked fonts in ' + n + ' files');
}

// ─────────────────────────────────────────────────────────────
// 3. FIND MISSING IMAGES (workflow-c §1–2)
// Parses vfs-src/<slug>.jsx for image refs and diffs against what the
// extractor actually wrote. Two ref kinds: inline style blocks, and
// component-override arrays. Writes a first-pass patch.json per board.
// ─────────────────────────────────────────────────────────────
async function findMissingImages() {
  const slugs = [/* 'jan-2026', … chunk ~6 per call */];
  const report = {};
  for (const slug of slugs) {
    const src = await readFile('vfs-src/' + slug + '.jsx');
    const have = new Set(await ls('boards/' + slug + '/assets'));
    const entries = [];
    const re = /style=\{\{([\s\S]*?)\}\}/g;
    let m;
    while ((m = re.exec(src)) !== null) {
      const body = m[1];
      const urlM = body.match(/url\(\.\/assets\/([0-9a-f]{16})\.(png|jpe?g|webp)\)/i);
      if (!urlM) continue;
      const w = (body.match(/width:\s*([\d.]+)/) || [])[1];
      const h = (body.match(/height:\s*([\d.]+)/) || [])[1];
      // capture the FULL background shorthand — crop/position values matter
      const bgM = body.match(/background(?:Color)?:\s*(?:props\.[A-Za-z0-9]+ \?\? )?"((?:[^"\\]|\\.)*url\(\.\/assets\/[^"]*)"/);
      if (!w || !h || !bgM) continue;
      entries.push({ w: parseFloat(w), h: parseFloat(h), file: urlM[1] + '.' + urlM[2], bg: bgM[1] });
    }
    // component-override images (geometry comes from the component file — see #4)
    const propFiles = new Set();
    const re2 = /Image:\s*"\.\/assets\/([0-9a-f]{16}\.(?:png|jpe?g|webp))"/gi;
    let m2; while ((m2 = re2.exec(src)) !== null) propFiles.add(m2[1]);
    const missingGeo = entries.filter(e => !have.has(e.file));
    const missingProp = [...propFiles].filter(f => !have.has(f) && !missingGeo.some(e => e.file === f));
    report[slug] = { refs: entries.length, missingGeo: missingGeo.length, missingProp: missingProp.length };
    await saveFile('boards/' + slug + '/patch.json', JSON.stringify({ geo: missingGeo, propOnly: missingProp }));
  }
  log(JSON.stringify(report, null, 1));
}

// ─────────────────────────────────────────────────────────────
// 4. MAP COMPONENT-OVERRIDE IMAGES (workflow-c §3)
// For `[{xImage:"./assets/h.png"}, …].map(...)` blocks: geometry + background
// template live in the COMPONENT jsx, the per-instance file in the array.
// Requires the component .jsx copied to vfs-src/<slug>-c/<Name>.jsx first.
// Filters out anything fig-assets.css already serves.
// ─────────────────────────────────────────────────────────────
async function buildPatchMaps() {
  const slugs = [/* chunk ~6 */];
  const need = JSON.parse(await readFile('vfs-src/needed-components.json')); // {blocks:{slug:[{comp,files,missing}]}}
  for (const slug of slugs) {
    const assets = new Set(await ls('boards/' + slug + '/assets'));
    let css = ''; try { css = await readFile('boards/' + slug + '/fig-assets.css'); } catch (e) {}
    const inCss = f => css.includes('/' + f + ')');
    const old = JSON.parse(await readFile('boards/' + slug + '/patch.json'));
    const entries = old.geo.filter(e => e.bg && assets.has(e.file) && !inCss(e.file));
    const blocks = need.blocks[slug] || [];
    if (blocks.length) {
      const src = await readFile('vfs-src/' + slug + '.jsx');
      // collect every map block once: {comp, items[]}
      const found = [];
      const mapRe = /\]\.map\(\(item, i\) => \(/g;
      let m;
      while ((m = mapRe.exec(src)) !== null) {
        const rest = src.slice(m.index, m.index + 600);
        const cm = rest.match(/\{\/\* \d+× → (\/[^ ]+\.jsx)/);
        if (!cm) continue;
        let i = m.index, depth = 1;
        while (i > 0 && depth > 0) { i--; if (src[i] === ']') depth++; else if (src[i] === '[') depth--; }
        const arr = src.slice(i, m.index + 1);
        found.push({ comp: cm[1], items: arr.slice(arr.indexOf('{')).split(/\},/) });
      }
      for (const b of blocks) {
        const name = b.comp.split('/').pop().replace('.jsx', '');
        let csrc; try { csrc = await readFile('vfs-src/' + slug + '-c/' + name + '.jsx'); } catch (e) { continue; }
        const w = parseFloat((csrc.match(/width:\s*([\d.]+)/) || [])[1]);
        const h = parseFloat((csrc.match(/height:\s*([\d.]+)/) || [])[1]);
        const bgT = (csrc.match(/"(url\(\.\/assets\/[^"]+?)"/) || [])[1];
        const defFile = ((csrc.match(/url\(\.\/assets\/([0-9a-f]{16}\.(?:png|jpe?g|webp))\)/i)) || [])[1];
        if (!w || !h || !bgT) continue;
        for (const blk of found.filter(x => x.comp === b.comp)) {
          for (const it of blk.items) {
            const fm = it.match(/Image:\s*"\.\/assets\/([0-9a-f]{16}\.(?:png|jpe?g|webp))"/i);
            const file = fm ? fm[1] : defFile;
            if (!file || !assets.has(file) || inCss(file)) continue;
            entries.push({ w, h, file, bg: bgT.replace(/[0-9a-f]{16}\.(?:png|jpe?g|webp)/i, file) });
          }
        }
      }
    }
    await saveFile('boards/' + slug + '/patch.json', JSON.stringify({ geo: entries }));
    log(slug + ': ' + entries.length + ' patch entries');
  }
}

// ─────────────────────────────────────────────────────────────
// 5. WIRE applyPatch + markPlaceholders INTO EVERY BOARD PAGE
// (workflow-c §5, workflow-a §8). Anchors must match the MASTER exactly.
// ─────────────────────────────────────────────────────────────
async function wireRuntimePatching() {
  const files = (await ls('')).filter(f => f.startsWith('Format Bank - ') && f.endsWith('.dc.html'));
  for (const p of files) {
    let f = await readFile(p);
    const sm = f.match(/boards\/([a-z0-9-]+)\/Components\.bundle\.js/);
    if (!sm) throw new Error('no slug in ' + p);
    const dir = 'boards/' + sm[1];
    // ... insert the applyPatch/markPlaceholders methods before `scan() {`
    //     and call this.applyPatch(root) at both the success and fallback anchors.
    //     Copy the method bodies verbatim from assets/MASTER-board-page.md.
    log('would wire ' + p + ' → ' + dir);
  }
}

// ─────────────────────────────────────────────────────────────
// 6. GLOBAL TWEAK ACROSS ALL BOARD PAGES
// Pattern for any sweeping change (detection filter, padding, height caps).
// Throw on a missing anchor so a silent no-op is impossible.
// ─────────────────────────────────────────────────────────────
async function tweakAllBoards() {
  const OLD = '<exact current source text>';
  const NEW = '<replacement>';
  const files = (await ls('')).filter(f => f.startsWith('Format Bank - ') && f.endsWith('.dc.html'));
  let n = 0;
  for (const p of files) {
    let f = await readFile(p);
    if (!f.includes(OLD)) throw new Error('pattern missing in ' + p);
    f = replaceText(f, OLD, NEW);
    await saveFile(p, f); n++;
  }
  log('updated ' + n);
}
