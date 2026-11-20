// Renders the formulas of the site with KaTeX. Called by tools/build_site.py.
// Usage: node render_tex.js in.json out.json
const katex = require('katex');
const fs = require('fs');
const items = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const out = items.map(it => katex.renderToString(it.tex, { displayMode: !!it.display, throwOnError: true, output: 'html', strict: 'ignore' }));
fs.writeFileSync(process.argv[3], JSON.stringify(out));
