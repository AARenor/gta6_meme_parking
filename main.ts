// gta6_meme_parking — the entry program for make.fun's gta6-meme-x-01 bounty.
//
// The entry is the X post itself. This program has one job: hand the post's
// address to the gate by copying POST.json from the repository root (the
// grader mounts it at /bot) into the output directory (the grader mounts it at
// /output). It prints nothing when the copy works.
//
// Outside the grader, the two directories are environment variables:
//   mkdir -p out && MAKEFUN_BOT_DIR=. MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, mkdirSync } from 'node:fs';
import { join } from 'node:path';

const POST_FILE = 'POST.json';

function directories(): { botDir: string; outDir: string } {
  return {
    botDir: process.env.MAKEFUN_BOT_DIR ?? '/bot',
    outDir: process.env.MAKEFUN_OUTPUT_DIR ?? '/output',
  };
}

function main(): void {
  const { botDir, outDir } = directories();
  mkdirSync(outDir, { recursive: true });
  const source = join(botDir, POST_FILE);
  const target = join(outDir, POST_FILE);
  try {
    copyFileSync(source, target);
  } catch (error) {
    console.error(`could not copy ${source} to ${target}: ${(error as Error).message}`);
    process.exitCode = 1;
  }
}

main();
