import sharp from 'sharp';
import { mkdir, writeFile } from 'node:fs/promises';
import { join } from 'node:path';

const root = process.cwd();
await mkdir(join(root, 'public'), { recursive: true });

function icon(size) {
  const fontSize = Math.round(size * 0.34);
  return Buffer.from(`<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}" viewBox="0 0 ${size} ${size}">
    <rect width="${size}" height="${size}" fill="#171717"/>
    <text x="50%" y="54%" text-anchor="middle" dominant-baseline="middle" fill="#ffffff" font-family="Helvetica Neue, Arial, sans-serif" font-size="${fontSize}" font-weight="700" letter-spacing="-${Math.round(size * 0.02)}">sk</text>
  </svg>`);
}

await writeFile(join(root, 'app/icon.png'), await sharp(icon(512)).png().toBuffer());
await writeFile(join(root, 'app/apple-icon.png'), await sharp(icon(180)).png().toBuffer());

const faviconSizes = [16, 32, 48];
const faviconPngs = await Promise.all(faviconSizes.map(async (size) => sharp(icon(size)).png().toBuffer()));
const icoHeader = Buffer.alloc(6 + faviconSizes.length * 16);
icoHeader.writeUInt16LE(1, 2);
icoHeader.writeUInt16LE(faviconSizes.length, 4);
let offset = icoHeader.length;
faviconSizes.forEach((size, index) => {
  const pos = 6 + index * 16;
  icoHeader.writeUInt8(size, pos);
  icoHeader.writeUInt8(size, pos + 1);
  icoHeader.writeUInt16LE(1, pos + 4);
  icoHeader.writeUInt16LE(32, pos + 6);
  icoHeader.writeUInt32LE(faviconPngs[index].length, pos + 8);
  icoHeader.writeUInt32LE(offset, pos + 12);
  offset += faviconPngs[index].length;
});
await writeFile(join(root, 'app/favicon.ico'), Buffer.concat([icoHeader, ...faviconPngs]));

const canvas = `<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630">
  <rect width="1200" height="630" fill="#ffffff"/>
  <path d="M74 111H1126M74 524H1126" stroke="#d9d9d9" stroke-width="2"/>
  <text x="75" y="74" fill="#171717" font-family="Helvetica Neue, Arial, sans-serif" font-size="27" font-weight="700" letter-spacing="-1">skills reader</text>
  <text x="75" y="250" fill="#171717" font-family="Helvetica Neue, Arial, sans-serif" font-size="78" font-weight="700" letter-spacing="-4">The skills</text>
  <text x="75" y="338" fill="#171717" font-family="Helvetica Neue, Arial, sans-serif" font-size="78" font-weight="700" letter-spacing="-4">guide</text>
  <text x="78" y="404" fill="#525252" font-family="Helvetica Neue, Arial, sans-serif" font-size="26">Matt Pocock's agent skills, in reading order.</text>
  <text x="75" y="573" fill="#525252" font-family="Helvetica Neue, Arial, sans-serif" font-size="22">skills-reader.vercel.app</text>
</svg>`;
await sharp(Buffer.from(canvas)).png({ compressionLevel: 9 }).toFile(join(root, 'public/opengraph-image.png'));
console.log('Generated favicon, app icons, and 1200\u00d7630 share image.');
