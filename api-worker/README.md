# AMMAR AI DIRECTOR — Worker Backend

هذا خادم توليد مخطط السيناريو بالذكاء الاصطناعي، مستقل عن واجهة GitHub Pages.

## تشغيل من الهاتف (Cloudflare Dashboard)

1. سجّل الدخول في https://dash.cloudflare.com/
2. Workers & Pages -> Create application -> GitHub
3. اسمح لمشروع ammar-ai-video-studio ثم حدد Root directory: `api-worker`
4. اسم Worker: `ammar-ai-director` (يطابق wrangler.jsonc)
5. Build command: `npm install` (إذا طُلب)، Deploy command: `npx wrangler deploy`
6. بعد النشر، Settings -> Variables and Secrets -> Add -> Secret. الاسم: `STUDIO_PASS` والقيمة: رمز قوي خاص بك من إنشائك، لا تضفه إلى GitHub ولا ترسله في المحادثة.
7. تحقق من `https://YOUR-SUBDOMAIN.workers.dev/health`، يجب أن تظهر `ready:true` بعد إعداد السر وربط AI.

## API

POST `/api/storyboard`
- Headers: `Content-Type: application/json`, `Authorization: Bearer <your-private-pass>`
- JSON: `{"idea":"...","duration":60,"ratio":"9:16","voice":"عراقي","style":"وثائقي سينمائي"}`
- CORS مقيد بعنوان GitHub Pages للمشروع.
- يوجد حد تقريبي 3 محاولات / 60 ثانية لحماية رصيد الاستدلال.
- endpoint يولد سيناريو فقط، وليس فيديو أو ملفاً صوتياً.

## أمان وتكلفة
- مفتاح الدخول محفوظ كـ **Cloudflare Secret** فقط.
- لا تضع أي مفتاح API أو رمز دخول في index.html أو git.
- Cloudflare Workers AI له حصة مجانية يومية محدودة؛ الاستخدام الزائد يتوقف عند حد الخطة.
- قبل مشاركة الموقع مع الآخرين، أضف تسجيل دخول حقيقياً وحصص استخدام مركزية أكثر صرامة.

## GitHub Pages
هذا المجلد لا يؤثر في نشر واجهة GitHub Pages الموجودة بالجذر.
