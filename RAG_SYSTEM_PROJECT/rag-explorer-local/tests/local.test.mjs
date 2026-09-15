import assert from 'node:assert/strict';
import {mkdtempSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {openDatabase} from '../lib/local-db.ts';
const dir=mkdtempSync(join(tmpdir(),'rag-test-')),file=join(dir,'db.sqlite');
let db=openDatabase(file);
try{
 const insert=()=>db.prepare('INSERT INTO experiments VALUES (?,?,?,?,?) ON CONFLICT(id) DO NOTHING').bind('a','local-user',1,'{}','{}').run();
 assert.equal((await insert()).meta.changes,1);assert.equal((await insert()).meta.changes,0);
 assert.equal((await db.prepare('SELECT * FROM experiments WHERE owner=?').bind('other').all()).results.length,0);
 await db.prepare('INSERT INTO runs(id,owner,created,status) VALUES(?,?,?,?)').bind('a','local-user',1,'complete').run();
 await db.prepare('UPDATE runs SET input_tokens=?,output_tokens=?,cost=? WHERE id=?').bind(20,10,.000006,'a').run();
 await db.prepare('INSERT INTO run_attempts(attempt_id,run_id,owner,created,status) VALUES(?,?,?,?,?)').bind('attempt-1','a','local-user',1,'unknown').run();
 db.close();db=openDatabase(file);
 assert.equal((await db.prepare('SELECT count(*) AS n FROM experiments').first()).n,1);
 const run=await db.prepare('SELECT * FROM runs WHERE id=?').bind('a').first();assert.equal(run.input_tokens,20);assert.equal(run.cost,.000006);
 assert.equal((await db.prepare('SELECT status FROM run_attempts WHERE attempt_id=?').bind('attempt-1').first()).status,'unknown');
 console.log('PASS: local SQLite initialization, duplicate protection, scoped reads, usage totals and restart persistence.');
}finally{db.close();rmSync(dir,{recursive:true,force:true});}
