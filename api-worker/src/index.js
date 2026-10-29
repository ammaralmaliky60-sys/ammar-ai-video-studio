// AMMAR AI VIDEO STUDIO — AI Director (Cloudflare Workers AI)
// This server runs independently from GitHub Pages. Never store STUDIO_PASS in public code.
const FRONTEND_ORIGIN = "https://ammaralmaliky60-sys.github.io";
const MODEL = "@cf/meta/llama-3.3-70b-instruct-fp8-fast";
const json = (body,status=200,origin="") => new Response(JSON.stringify(body),{
  status,headers:{"content-type":"application/json; charset=utf-8","cache-control":"no-store",
    ...(origin===FRONTEND_ORIGIN?{"access-control-allow-origin":FRONTEND_ORIGIN,"vary":"Origin"}:{})}
});
function extract(raw){
  if(typeof raw==="string")return raw;
  if(typeof raw?.response==="string")return raw.response;
  if(typeof raw?.result?.response==="string")return raw.result.response;
  return raw?.choices?.[0]?.message?.content || "";
}
export default {
 async fetch(request,env){
  const origin=request.headers.get("Origin")||"";
  const url=new URL(request.url);
  if(request.method==="OPTIONS"){
    if(origin!==FRONTEND_ORIGIN)return new Response(null,{status:403});
    return new Response(null,{status:204,headers:{
      "access-control-allow-origin":FRONTEND_ORIGIN,"access-control-allow-methods":"POST,OPTIONS",
      "access-control-allow-headers":"content-type,authorization","access-control-max-age":"600","vary":"Origin"
    }});
  }
  if(url.pathname==="/health"&&request.method==="GET")
    return json({service:"ammar-ai-director",ready:Boolean(env.AI && env.STUDIO_PASS),model:MODEL});
  if(url.pathname!=="/api/storyboard")return json({error:"المسار غير موجود"},404,origin);
  if(request.method!=="POST")return json({error:"استخدم POST"},405,origin);
  if(origin!==FRONTEND_ORIGIN)return json({error:"مصدر الطلب غير مسموح"},403,origin);
  if(!env.STUDIO_PASS||!env.AI)return json({error:"الخادم غير مجهز بعد"},503,origin);
  if(request.headers.get("Authorization")!==`Bearer ${env.STUDIO_PASS}`)
    return json({error:"رمز الدخول غير صحيح"},401,origin);
  if(request.headers.get("content-type")?.split(";")[0]?.trim()!=="application/json")
    return json({error:"تنسيق الطلب غير مدعوم"},415,origin);
  if(env.STUDIO_LIMITER){
    const {success}=await env.STUDIO_LIMITER.limit({key:"studio-owner"});
    if(!success)return json({error:"وصلت الحد المؤقت، جرّب لاحقاً"},429,origin);
  }
  const bodyText=await request.text();
  if(bodyText.length>5000)return json({error:"حجم النص كبير"},413,origin);
  let data;
  try{data=JSON.parse(bodyText)}catch{return json({error:"JSON غير صحيح"},400,origin)}
  const idea=String(data.idea||"").trim();
  const duration=Number(data.duration);
  const ratio=String(data.ratio||"9:16");
  const voice=data.voice==="فصيح"?"فصيح":"عراقي";
  const style=["وثائقي سينمائي","غموض وتشويق","تاريخي"].includes(data.style)?data.style:"وثائقي سينمائي";
  if(idea.length<10||idea.length>1200||![30,60,180].includes(duration)||!["9:16","16:9"].includes(ratio))
    return json({error:"تأكد من طول الفكرة والمدة والأبعاد"},400,origin);
  const count=duration/10;
  const system=[
    "أنت مخرج وثائقي محترف تكتب بالعربية مع تعليق صوتي بأسلوب عراقي طبيعي عند الطلب.",
    "لا تقدم ادعاءات عن وقائع تاريخية غير موثقة. إذا افتقر الطلب إلى مصادر، صغ قصة خيالية مستوحاة من أجواء العراق وأشر بوضوح أنها معالجة تخيلية.",
    "أخرج كائن JSON واحد فقط دون مقدمات أو markdown وبالبنية:",
    '{"title":"عنوان","disclaimer":"توضيح التوثيق","narration":"نص الراوي الكامل","scenes":[{"number":1,"title":"لقطة","visual":"وصف تصوير سينمائي دقيق","narration":"نص تعليق لهذا المشهد"}]}',
    `عدد المشاهد بالضبط ${count}، كل مشهد 10 ثوانٍ، المدة ${duration} ثانية.`,
    "تأكد أن النص الصوتي متناسب تقريبياً مع مدة العرض، بلا ادعاء مصادر غير متاحة."
  ].join("\n");
  try{
   const result=await env.AI.run(MODEL,{
     messages:[{role:"system",content:system},{role:"user",content:`الموضوع: ${idea}\nالأسلوب: ${style}\nالنطق: ${voice}\nالأبعاد: ${ratio}\nالمدة: ${duration}`}],
     max_tokens:3000,temperature:0.7
   });
   const raw=extract(result).trim();
   let generated;
   try{generated=JSON.parse(raw)}catch{
     const match=raw.match(/\{[\s\S]*\}/);
     if(!match)throw new Error("AI_RESPONSE_NOT_JSON");
     generated=JSON.parse(match[0]);
   }
   if(!generated||!Array.isArray(generated.scenes)||!generated.scenes.length)throw new Error("AI_RESPONSE_INVALID");
   const scenes=generated.scenes.slice(0,count).map((s,i)=>({
     number:i+1,start:i*10,end:(i+1)*10,
     title:String(s.title||`المشهد ${i+1}`).slice(0,150),
     visual:String(s.visual||"").slice(0,900),
     narration:String(s.narration||"").slice(0,900)
   }));
   return json({title:String(generated.title||idea).slice(0,200),
     disclaimer:String(generated.disclaimer||"النص مولّد آلياً؛ تحقّق من الوقائع قبل النشر.").slice(0,500),
     narration:String(generated.narration||scenes.map(s=>s.narration).join(" ")).slice(0,6000),
     duration,ratio,voice,style,scenes,source:"cloudflare-workers-ai",videoGenerated:false,audioGenerated:false
   },200,origin);
  }catch(error){
   console.error("AI Director inference failed",String(error));
   return json({error:"تعذر إنشاء السيناريو بواسطة النموذج حالياً؛ حاول مرة أخرى."},502,origin);
  }
 }
};
