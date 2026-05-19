import sharp from 'sharp';
import { readdir, mkdir, writeFile } from 'fs/promises';
import { join } from 'path';

const SRC = join(import.meta.dirname, '..', 'public', 'images', 'food');
const OUT = join(import.meta.dirname, '..', 'public', 'images', 'food-opt');
const MANIFEST_PATH = join(import.meta.dirname, '..', 'src', 'assets', 'image-manifest.json');

const MAX_WIDTH = 800;
const WEBP_QUALITY = 78;
const BLUR_WIDTH = 20;

async function run() {
  await mkdir(OUT, { recursive: true });

  const files = (await readdir(SRC)).filter(f => /\.(jpe?g|png|webp)$/i.test(f));
  const manifest = {};

  for (const file of files) {
    const src = join(SRC, file);
    const baseName = file.replace(/\.[^.]+$/, '');
    const outName = baseName + '.webp';
    const outPath = join(OUT, outName);

    // Resize + WebP
    const img = sharp(src);
    const meta = await img.metadata();
    const width = Math.min(meta.width, MAX_WIDTH);

    await img
      .resize({ width, withoutEnlargement: true })
      .webp({ quality: WEBP_QUALITY, effort: 6 })
      .toFile(outPath);

    // Tiny blur placeholder as base64 data URI
    const blurBuf = await sharp(src)
      .resize({ width: BLUR_WIDTH })
      .webp({ quality: 20 })
      .toBuffer();
    const blurDataUri = `data:image/webp;base64,${blurBuf.toString('base64')}`;

    // Get final file size
    const outMeta = await sharp(outPath).metadata();

    manifest[file] = {
      webp: `/images/food-opt/${outName}`,
      blur: blurDataUri,
      width: outMeta.width,
      height: outMeta.height
    };

    const srcSize = (await sharp(src).metadata()).size || meta.size;
    const { size: outSize } = await sharp(outPath).metadata();
    console.log(`✓ ${file} → ${outName}  (${width}w, ${(blurBuf.length / 1024).toFixed(1)}KB blur)`);
  }

  await writeFile(MANIFEST_PATH, JSON.stringify(manifest, null, 2));
  console.log(`\n✅ Manifest written: ${MANIFEST_PATH}`);
  console.log(`   ${files.length} images compressed into ${OUT}`);
}

run().catch(err => { console.error(err); process.exit(1); });
