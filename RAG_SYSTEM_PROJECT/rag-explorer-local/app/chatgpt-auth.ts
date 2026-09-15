import {headers} from 'next/headers';
// Single-user local edition; not suitable for public deployment.
export async function getChatGPTUser(){
 const h=await headers(),host=h.get('host')??'';
 if(!/^(localhost|127\.0\.0\.1)(:\d+)?$/.test(host)||h.get('sec-fetch-site')==='cross-site')return null;
 const origin=h.get('origin');if(origin&&origin!==`http://${host}`)return null;
 return {userId:'local-user',displayName:'로컬 사용자',email:'',fullName:null};
}
