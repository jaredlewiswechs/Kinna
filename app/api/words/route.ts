import sqlite3 from 'sqlite3';
import { open } from 'sqlite';
import { NextResponse } from 'next/server';

export async function GET(request: Request) {
  const url = new URL(request.url);
  const q = url.searchParams.get('q');
  const limit = Number(url.searchParams.get('limit') || '10');

  const dbPath = process.cwd() + '/kinematic.db';
  const db = await open({ filename: dbPath, driver: sqlite3.Database });

  let rows;
  if (q) {
    rows = await db.all(
      'SELECT word, synset_id, definition, vec_structure AS structure, vec_force AS force, vec_flow AS flow, density, regime_tags FROM words WHERE word LIKE ? ORDER BY synset_id LIMIT ?',
      [`%${q.toUpperCase()}%`, limit]
    );
  } else {
    rows = await db.all(
      'SELECT word, synset_id, definition, vec_structure AS structure, vec_force AS force, vec_flow AS flow, density, regime_tags FROM words ORDER BY RANDOM() LIMIT ?',
      [limit]
    );
  }

  await db.close();
  return NextResponse.json(rows);
}
