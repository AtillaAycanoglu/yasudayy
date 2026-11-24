// Renders the launcher icon (192x192) using the game's own drawBird(). usage: node make_icon.js <game/index.html> <out.png>
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage();
  await p.goto('file://' + path.resolve(process.argv[2])); await p.waitForTimeout(300);
  const data = await p.evaluate(() => {
    const c = document.createElement('canvas'); c.width = c.height = 192; const g = c.getContext('2d');
    const r = 42; g.beginPath(); g.moveTo(r,0); g.arcTo(192,0,192,192,r); g.arcTo(192,192,0,192,r); g.arcTo(0,192,0,0,r); g.arcTo(0,0,192,0,r); g.closePath(); g.clip();
    const bg = g.createLinearGradient(0,0,0,192); bg.addColorStop(0,'#1b0a45'); bg.addColorStop(.6,'#5a1470'); bg.addColorStop(1,'#ff3d9a'); g.fillStyle = bg; g.fillRect(0,0,192,192);
    const sg = g.createLinearGradient(0,90,0,190); sg.addColorStop(0,'#ffe36e'); sg.addColorStop(1,'#ff2d8a');
    g.fillStyle = sg; g.beginPath(); g.arc(120,150,55,0,Math.PI*2); g.fill();
    g.fillStyle = '#1b0a45'; for(let i=0;i<4;i++) g.fillRect(60,150+i*10,130,2+i);
    g.strokeStyle = '#29f0ff'; g.lineWidth = 2; g.shadowColor = '#29f0ff'; g.shadowBlur = 8; g.beginPath(); g.moveTo(0,172); g.lineTo(192,172); g.stroke(); g.shadowBlur = 0;
    g.save(); g.scale(3.6,3.6); drawBird(g, 27, 25, -.25, .8, SKINS[0], 0, false); g.restore();
    return c.toDataURL('image/png').split(',')[1];
  });
  require('fs').writeFileSync(process.argv[3], Buffer.from(data, 'base64')); await b.close();
})();
