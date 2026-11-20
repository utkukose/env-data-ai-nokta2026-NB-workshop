// Refreshes docs/assets/vendor: the three.js bundle, KaTeX (CSS and woff2 fonts) and the
// Atkinson Hyperlegible font (Latin and Latin Extended subsets), each with its license file.
// Usage: npm install, then node build_vendor.js
const fs = require('fs');
const path = require('path');
const esbuild = require('esbuild');

const VENDOR = path.resolve(__dirname, '..', '..', 'docs', 'assets', 'vendor');
const mod = (p) => path.join(__dirname, 'node_modules', p);
fs.mkdirSync(path.join(VENDOR, 'katex', 'fonts'), { recursive: true });
fs.mkdirSync(path.join(VENDOR, 'fonts'), { recursive: true });

esbuild.buildSync({ entryPoints: [path.join(__dirname, 'three-entry.js')], bundle: true, minify: true,
  format: 'iife', outfile: path.join(VENDOR, 'three.bundle.min.js') });
fs.copyFileSync(path.join(mod('three'), 'LICENSE'), path.join(VENDOR, 'LICENSE-three.txt'));

const katexDist = path.join(mod('katex'), 'dist');
fs.copyFileSync(path.join(katexDist, 'katex.min.css'), path.join(VENDOR, 'katex', 'katex.min.css'));
for (const f of fs.readdirSync(path.join(katexDist, 'fonts'))) {
  if (f.endsWith('.woff2')) fs.copyFileSync(path.join(katexDist, 'fonts', f), path.join(VENDOR, 'katex', 'fonts', f));
}
fs.copyFileSync(path.join(mod('katex'), 'LICENSE'), path.join(VENDOR, 'LICENSE-katex.txt'));

const font = mod('@fontsource/atkinson-hyperlegible');
const faces = [];
for (const [w, st] of [['400', 'normal'], ['400', 'italic'], ['700', 'normal'], ['700', 'italic']]) {
  const css = fs.readFileSync(path.join(font, w + (st === 'italic' ? '-italic' : '') + '.css'), 'utf8');
  for (const block of css.match(/@font-face\s*{[^}]+}/g)) {
    const file = block.match(/files\/([\w-]+\.woff2)/)[1];
    const range = block.match(/unicode-range:\s*([^;]+);/)[1];
    fs.copyFileSync(path.join(font, 'files', file), path.join(VENDOR, 'fonts', file));
    faces.push(`@font-face {\n  font-family: 'Atkinson Hyperlegible';\n  font-style: ${st};\n  font-display: swap;\n  font-weight: ${w};\n  src: url(./${file}) format('woff2');\n  unicode-range: ${range};\n}\n`);
  }
}
fs.writeFileSync(path.join(VENDOR, 'fonts', 'atkinson.css'),
  '/* Atkinson Hyperlegible, Braille Institute of America, SIL Open Font License 1.1 (see ../LICENSE-atkinson-hyperlegible.txt) */\n' + faces.join('\n'));
fs.copyFileSync(path.join(font, 'LICENSE'), path.join(VENDOR, 'LICENSE-atkinson-hyperlegible.txt'));
console.log('vendor files written to', VENDOR);
