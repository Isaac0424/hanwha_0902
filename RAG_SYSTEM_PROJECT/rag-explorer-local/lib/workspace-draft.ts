import {validateConfig} from "./rag-engine";
import {validateGeneration} from "./generation";
import type {ExperimentInput} from "./cost";
export const DRAFT_KEY="rag-explorer:tab-draft:v1";
export type Draft={input:ExperimentInput;baseline:ExperimentInput};
function valid(v:ExperimentInput){if(!v||typeof v.query!=="string"||v.query.length>300||typeof v.document!=="string"||v.document.length>6000||typeof v.system!=="string"||v.system.length>1500)throw Error("Invalid draft");validateConfig(v.config);validateGeneration(v.settings);}
export function parseDraft(raw:string|null):Draft|null{try{if(!raw)return null;const d=JSON.parse(raw);if(d.version!==1||typeof d.savedAt!=="number"||Date.now()-d.savedAt>86400000)return null;valid(d.input);valid(d.baseline);return {input:d.input,baseline:d.baseline};}catch{return null;}}
export function serializeDraft(d:Draft){return JSON.stringify({version:1,savedAt:Date.now(),input:d.input,baseline:d.baseline});}
