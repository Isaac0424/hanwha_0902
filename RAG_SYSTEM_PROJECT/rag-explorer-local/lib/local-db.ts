import {DatabaseSync} from 'node:sqlite';
import {mkdirSync} from 'node:fs';
import {resolve,dirname} from 'node:path';
type Value=string|number|null;
export function openDatabase(filename:string){
 if(filename!==':memory:')mkdirSync(dirname(filename),{recursive:true});
 const db=new DatabaseSync(filename);
 db.exec(`PRAGMA journal_mode=WAL; PRAGMA busy_timeout=5000;
 CREATE TABLE IF NOT EXISTS experiments(id TEXT PRIMARY KEY,owner TEXT NOT NULL,created INTEGER NOT NULL,snapshot TEXT NOT NULL,estimate TEXT NOT NULL);
 CREATE INDEX IF NOT EXISTS experiments_owner_created ON experiments(owner,created);
 CREATE TABLE IF NOT EXISTS runs(id TEXT PRIMARY KEY,owner TEXT NOT NULL,created INTEGER NOT NULL,status TEXT NOT NULL,output TEXT,input_tokens INTEGER,output_tokens INTEGER,cost REAL);
 CREATE INDEX IF NOT EXISTS runs_owner_created ON runs(owner,created);
 CREATE TABLE IF NOT EXISTS run_attempts(attempt_id TEXT PRIMARY KEY,run_id TEXT NOT NULL,owner TEXT NOT NULL,created INTEGER NOT NULL,status TEXT NOT NULL,output TEXT,input_tokens INTEGER,output_tokens INTEGER,cost REAL);
 CREATE INDEX IF NOT EXISTS run_attempts_run_created ON run_attempts(run_id,created);`);
 return {
  prepare(sql:string){const stmt=db.prepare(sql);
   function bound(values:Value[]){return {
    bind(...next:Value[]){return bound(next)},
    async run(){const r=stmt.run(...values);return {meta:{changes:Number(r.changes)}}},
    async first<T=Record<string,unknown>>():Promise<T|null>{return (stmt.get(...values) as T|undefined)??null},
    async all(){return {results:stmt.all(...values)}}
   }}return bound([]);
  },close(){db.close()}
 };
}
const state=globalThis as typeof globalThis&{ragDatabase?:ReturnType<typeof openDatabase>};
export function localDatabase(){return state.ragDatabase??=openDatabase(resolve(process.cwd(),'data','rag-explorer.sqlite'));}
