import { NextApiRequest, NextApiResponse } from 'next';
import sqlite3 from 'sqlite3';
import { open } from 'sqlite';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const { q, limit } = req.query;
  const db = await open({ filename: 'kinematic.db', driver: sqlite3.Database });
  let rows;
  if (q) {
    rows = await db.all(
      'SELECT * FROM words WHERE word LIKE ? ORDER BY synset_id LIMIT ?',
      [`%${q.toString().toUpperCase()}%`, Number(limit) || 10]
    );
  } else {
    rows = await db.all('SELECT * FROM words ORDER BY RANDOM() LIMIT ?', [Number(limit) || 10]);
  }
  res.status(200).json(rows);
}
