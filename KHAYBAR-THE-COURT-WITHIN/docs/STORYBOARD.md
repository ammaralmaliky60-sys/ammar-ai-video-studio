# STORYBOARD — THE COURT WITHIN (Animatic v0.1)

**الحالة:** PHASE 3 — بانتظار GATE 3. مُولَّد من `SHOT_LIST.json` (المصدر الوحيد للقطات) — لا تعدّل هنا يدوياً.
**التوقيت:** مشتق من توقيت الأسطر المقاس آلياً (`alignment/COMPLETENESS_CHECK.json`) وبدايات الفصول في `AUDIO_CUES.json`. القطع يقع على بداية الجملة.
**المراجع البصرية:** ⛔ الصور الـ17 لم تصل — التأطير مبني على التوجيه المعتمد فقط وسيُراجع بعد تدقيقها.

## الرحلة البصرية
مرآة باردة → محكمة غامضة → سجن الأعذار → بصيرة قرآنية → اختلال الميزان → الانكشاف → التحرر → باب الإصلاح.
**Callback:** إطار مرآة الافتتاح (S01_01) = إطار المرآة المتماسكة (S07_01) = قوس باب الإصلاح (S07_04–05) — نفس هندسة قوس خيبر.

## منطق الكاميرا والإضاءة
| الحالة الدرامية | الكاميرا | الإضاءة |
|---|---|---|
| غموض/استدعاء (CH01) | دفع بطيء، عبور شظايا، اختراق بوابة | P1 باردة → P2 علوية مركزة |
| تراكم الأعذار (CH02) | ثابتة عند السقوط، Crane عند بناء الجدار، علوية عند السجن | P3 تضييق تدريجي حتى شق ضوء واحد |
| الدليل (CH03، CH04 عند الآية) | **ثابتة تماماً** | P4 مستقرة مقروءة |
| الاختلال (CH04) | ثابتة أمامية + Orbit بطيء | P4 |
| الانكشاف (CH05) | Orbit متسارع → توقف عند كل «إنت» → سكون → Crane خارج مع الانهيار | P5 ضوء يتسرب ثم يغمر |
| المنهج (CH06) | Lock عند الرواية، دفع ناعم في المراحل الثلاث، Orbit للتحول | P6 دفء تدريجي |
| الحكم/الباب (CH07) | Lock أمام المرآة، Dolly-out واسع نحو الباب | P7 ذهبي/عاجي، اتساع |


## CH01 — الاستدعاء

| Shot | إطارات | ث | السرد | المرسى | الكاميرا / العدسة | التكوين | الإضاءة | الطباعة | الانتقال | الصوت | التقنية |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **S01_01** | 0–135 | 0.00–4.50 | تخيّل لو كل عذر گُلته بحياتك… صار دليل ضدّك. | تخيّل لو كل عذر گُلته بحياتك (F0)<br>صار دليل ضدّك (F84) | Slow dolly-in (locked axis); micro-push on major fracture · 50mm | Centered mirror (KHAYBAR arch frame), reflection fills 60% height; Faceless figure seen ONLY as reflection, still | P1 Mirror — cold, deep shadows, teal reflections, gold only inside cracks | Editorial line low-third (IBM Plex) — optional subtitle | Cut from frame 0 (no logo, no black) | Hairline crack creep from f15; MAJOR fracture hit on «صار دليل ضدّك» | Three.js: pre-fractured glass (Voronoi, seeded) + reflection render target |
| | | | ↳ *Hook: conflict readable in <2s — reflection + spreading crack + voice* | | | | | | | | |
| **S01_02** | 135–261 | 4.50–8.70 | وكل موقف حاولت تنساه… رجع حتى يشهد عليك. | — | Controlled fly-through between suspended shards, slight orbit · 35mm | Shards at 3 depths; one hero shard center-right; — | P1 Mirror — cold, deep shadows, teal reflections, gold only inside cracks | — | Continuous from fracture | Glass tinkle bed (low), air | Three.js instanced shards + rack focus |
| | | | ↳ *On «رجع حتى يشهد عليك» the courtroom reflection appears inside the hero shard* | | | | | | | | |
| **S01_03** | 261–364 | 8.70–12.13 | وفجأة، تلگه نفسك واقف بمحكمة غريبة. | وفجأة (F261) | Push-in → penetrate shard (T01 Mirror Portal) → crane down into hall · 35mm → 24mm | Shard edge wipes frame; hall revealed symmetrical; Figure small, standing at accused platform | P2 Courtroom — focused top light, dark walnut, architectural shadows | TITLE «المحكمة التي بداخلك» (Impact, gold) ~1s after portal, 2.5s hold | T01 Mirror Portal | Portal whoosh (non-musical air), glass pass-by, room-tone bloom | Three.js camera path + 2.5D hall plates |
| | | | ↳ *Title appears after hook started (≈ 9.5s)* | | | | | | | | |
| **S01_04** | 364–467 | 12.13–15.57 | ما تعرف منو جابك. / ولا تعرف شنو التهمة. | — | Very slow dolly-in · 24–28mm | Symmetric vanishing point, figure at lower third; Figure still, head lowers on «التهمة» | P2 Courtroom — focused top light, dark walnut, architectural shadows | Impact word «التهمة؟» (IBM Plex 600) brief | Cut | Room tone, distant echo | 2.5D parallax plates (style frame) — CPU-cheap |
| **S01_05** | 467–502 | 15.57–16.73 | القاضي ساكت… | القاضي ساكت (F467) | Locked · 50mm | Judge bench towering, faceless judge silhouette backlit; Judge motionless | P2 Courtroom — focused top light, dark walnut, architectural shadows | — | Cut on «القاضي» | Silence pocket + faint creak | 2.5D + rim-lit silhouette card (same body model as accused) |
| | | | ↳ *Identity hidden: silhouette, height & costume match but no face* | | | | | | | | |
| **S01_06** | 502–566 | 16.73–18.87 | والشاهد ينتظر دوره… | — | Rack focus bench → witness stand · 50mm | Witness stand right third; Witness silhouette, waiting | P2 Courtroom — focused top light, dark walnut, architectural shadows | — | Rack focus | Wood creak | 2.5D + depth-of-field blur |
| **S01_07** | 566–629 | 18.87–20.97 | والأدلة كلها موجودة. | — | Slow drift upward · 85mm | Suspended papers in light shaft; — | P2 Courtroom — focused top light, dark walnut, architectural shadows | — | Match-cut on light | Paper flutter | 2.5D sprites + deterministic particles |
| **S01_08** | 629–770 | 20.97–25.67 | تحاول تتذكّر شنو سويت حتى وصلت لهنا. / بس الغريب بالموضوع… | — | Slow pan following his gaze across hall · 35mm | Figure's shoulder fg-left, hall bg; Figure turns head searching memory | P2 Courtroom — focused top light, dark walnut, architectural shadows | — | Cut | Footstep shift, room tone | 2.5D |
| **S01_09** | 770–920 | 25.67–30.67 | إنك تعرف هاي المحكمة أكثر مما تتصور. | إنك تعرف هاي المحكمة أكثر مما تتصور (F770) | Slow push to a mirror fragment lying on bench · 50mm → 85mm | Fragment reflects the hall — familiarity hint; Figure static | P2 Courtroom — focused top light, dark walnut, architectural shadows | — | Hold into 1.5s silence | Low tonal air (non-musical), silence | Three.js reflection or 2.5D card |
| | | | ↳ *No identity reveal; only a sense of familiarity* | | | | | | | | |

## CH02 — الشاهد

| Shot | إطارات | ث | السرد | المرسى | الكاميرا / العدسة | التكوين | الإضاءة | الطباعة | الانتقال | الصوت | التقنية |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **S02_01** | 920–1008 | 30.67–33.60 | تبدأ المحاكمة… / ويطلع أول دليل. | ويطلع أول دليل (F964) | Locked; gavel strike · 50mm | Gavel center; Judge hand (silhouette) strikes | P2 Courtroom — focused top light, dark walnut, architectural shadows | — | Cut on «تبدأ المحاكمة» | GAVEL IMPACT + short shockwave dust | Three.js gavel (walnut + aged gold ring) — inertia curve |
| | | | ↳ *Trial begins* | | | | | | | | |
| **S02_02** | 1008–1131 | 33.60–37.70 | ذاك اليوم اللي جرحت بيه إنسان بكلمة. / تتذكره؟ | — | Dolly-in through shard (T02 Memory Immersion) · 85mm → 35mm | Memory scene inside glass: two faceless silhouettes, one recoils; Memory figures | P3 Excuses — narrowing light, cold shift, enclosure | — | T02 | Glass shimmer, distant voice-less murmur (no words) | 2.5D memory card inside glass shader |
| | | | ↳ *Evidence #1: wounding word* | | | | | | | | |
| **S02_03** | 1131–1182 | 37.70–39.40 | إنت گُلت: چنت معصّب. | چنت معصّب (F1150 ⚑يدوي) | Locked; block drops in · 50mm | Basalt block lands beside figure; Figure flinches | P3 Excuses — narrowing light, cold shift, enclosure | ENGRAVED «چنت معصّب» on block (Canvas texture) | T03 Excuse Formation | STONE FORM + heavy impact | Three.js block + Canvas text texture |
| | | | ↳ *Anchor flagged (low confidence) — verify drop timing manually* | | | | | | | | |
| **S02_04** | 1182–1316 | 39.40–43.87 | ويطلع دليل ثاني… / موقف چنت تعرف بيه الحق، بس سكتّ. | — | Drift · 85mm → 35mm | Silent bystander memory; Memory figure turns away | P3 Excuses — narrowing light, cold shift, enclosure | — | T02 | Glass shimmer | 2.5D |
| **S02_05** | 1316–1378 | 43.87–45.93 | گُلت: ما چنت أريد مشاكل. | — | Locked · 50mm | Second block lands; — | P3 Excuses — narrowing light, cold shift, enclosure | ENGRAVED «ما چنت أريد مشاكل» | T03 | STONE impact | Three.js |
| **S02_06** | 1378–1479 | 45.93–49.30 | ودليل ثالث… / حچيت على إنسان بغيابه. | — | Drift · 85mm → 35mm | Whispering memory: two figures leaning toward each other; — | P3 Excuses — narrowing light, cold shift, enclosure | — | T02 | Glass shimmer | 2.5D |
| **S02_07** | 1479–1563 | 49.30–52.10 | گُلت: مو بس آني… الكل چان يحچي. | مو بس آني (F1496) | Locked · 50mm | Third block lands; — | P3 Excuses — narrowing light, cold shift, enclosure | ENGRAVED «مو بس آني… الكل چان يحچي» | T03 | STONE impact | Three.js |
| **S02_08** | 1563–1677 | 52.10–55.90 | وكل مرة تقدم عذر، تحس إنك نجحت بالدفاع عن نفسك. | — | Slow push-in · 35mm | Figure framed between blocks, posture 'victorious'; Figure straightens | P3 Excuses — narrowing light, cold shift, enclosure | — | Cut | Low stone settle | Three.js / 2.5D |
| **S02_09** | 1677–1817 | 55.90–60.57 | بس ما تنتبه إن كل عذر من هاي الأعذار، دا يبني جدار حواليك. | دا يبني جدار حواليك (F1766) | Crane up and out · 28mm | Blocks forming a ring-wall around figure; Figure static | P3 Excuses — narrowing light, cold shift, enclosure | — | Continuous | Stone grind, rising | Three.js instanced blocks |
| **S02_10** | 1817–1866 | 60.57–62.20 | حجر فوق حجر… | حجر فوق حجر (F1817) | Locked; rhythmic block drops · 35mm | Stone on stone; — | P3 Excuses — narrowing light, cold shift, enclosure | Impact words «حجر… فوق… حجر» optional | Cut | 2 rhythmic STONE impacts (on each «حجر») | Three.js |
| **S02_11** | 1866–2064 | 62.20–68.80 | لحد ما يصير دفاعك عن نفسك، هو السجن اللي حابس نفسك بيه. | هو السجن اللي حابس نفسك بيه (F1931) | Slow vertical pull-up then stop · 24mm | Figure enclosed; single slit of light; Figure looks up | P3 Excuses — narrowing light, cold shift, enclosure | — | Hold into 2.0s silence | Silence (deliberate) + faint air | Three.js |

## CH03 — الدليل القرآني

| Shot | إطارات | ث | السرد | المرسى | الكاميرا / العدسة | التكوين | الإضاءة | الطباعة | الانتقال | الصوت | التقنية |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **S03_01** | 2064–2141 | 68.80–71.37 | بس أكو حقيقة ما تگدر تهرب منها. | — | Locked · 35mm | Light slit on wall; Figure turns to light | P4 Evidence — stable light, readable contrast, calm gold arch | — | Cut | Air | 2.5D |
| **S03_02** | 2141–2408 | 71.37–80.27 | القرآن الكريم يگول: / بَلِ الْإِنسَانُ عَلَىٰ نَفْسِهِ بَصِيرَةٌ، وَلَوْ أَلْقَىٰ مَعَاذِيرَهُ. | القرآن الكريم يگول (F2141)<br>[Q01 quotation start] (F2215 ⚑يدوي)<br>[Q01 quotation end] (F2308 ⚑يدوي) | LOCKED — camera stops · 50mm | Cinematic Knowledge Arch (KHAYBAR arch geometry) centered; sacred text inside; — | P4 Evidence — stable light, readable contrast, calm gold arch | SACRED Q01 — Amiri Quran, static, + reference | T05 Knowledge Reveal | NO dramatic SFX — ambience ducked | Remotion typography layer over dimmed plate |
| | | | ↳ *Protected interval F2200–2398* | | | | | | | | |
| **S03_03** | 2408–2461 | 80.27–82.03 | تأمّل هاي الآية. | — | Very slow push · 35mm | Hairline fractures appear in excuse wall; Figure watches | P4 Evidence — stable light, readable contrast, calm gold arch | — | Dissolve from arch | Hairline crack (soft) | Three.js crack mask |
| | | | ↳ *Wall must NOT collapse yet* | | | | | | | | |
| **S03_04** | 2461–2748 | 82.03–91.60 | ممكن تقنع الناس بعذرك. / ممكن ترتّب كلامك حتى تطلع إنت المظلوم. / وممكن تخفي جزء من الحقيقة، حتى تحافظ على صورتك گدامهم. | — | Gentle lateral track · 50mm | Three shards: persuading, rearranging words, hiding a piece; Shard figures | P4 Evidence — stable light, readable contrast, calm gold arch | — | Cut | Glass shimmer | 2.5D |
| **S03_05** | 2748–3043 | 91.60–101.43 | بس بينك وبين نفسك… / إنت تعرف شنو صار. / وتعرف شنو چان قصدك. / وتعرف الفرق بين السبب الحقيقي، والعذر اللي اخترعته حتى… | بس بينك وبين نفسك (F2748) | Slow push-in · 50mm → 85mm | Figure facing his own reflection in polished stone; Figure still | P4 Evidence — stable light, readable contrast, calm gold arch | — | Cut | Breath-like air (non-musical) | 2.5D / reflection pass |
| **S03_06** | 3043–3339 | 101.43–111.30 | المشكلة مو دائماً إنك ما تعرف الحقيقة. / أحياناً، المشكلة إنك تعرفها… وما تريد تواجهها. | إنك تعرفها… وما تريد تواجهها (F3212) | Locked → slow push into light · 85mm | Single crack glowing; — | P4 Evidence — stable light, readable contrast, calm gold arch | — | Hold into gap | Low resonance, silence | Three.js crack emissive |

## CH04 — ميزان العدالة

| Shot | إطارات | ث | السرد | المرسى | الكاميرا / العدسة | التكوين | الإضاءة | الطباعة | الانتقال | الصوت | التقنية |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **S04_01** | 3339–3550 | 111.30–118.33 | خل أسألك سؤال. / لو واحد غيرك سوّى نفس الغلط اللي إنت سويته… / راح تقبل منه نفس العذر؟ | راح تقبل منه نفس العذر؟ (F3484) | Slow orbit 30° · 50mm | Antique gold scale on black basalt base, centered; — | P4 Evidence — stable light, readable contrast, calm gold arch | — | Cut | Metal chain settle | Three.js scale (gold PBR) |
| **S04_02** | 3550–3729 | 118.33–124.30 | من واحد يجرحك بكلمة، تعتبره قليل احترام. / بس من إنت تجرحه، تگول چنت معصّب. | [contrast 1] من واحد يجرحك بكلمة… (F3550) | Locked · 50mm | Left pan = others (heavy), right pan = self (light); — | P4 Evidence — stable light, readable contrast, calm gold arch | Labels «قليل احترام» vs «چنت معصّب» (IBM Plex) | Cut | Metal tilt creak | Three.js |
| **S04_03** | 3729–3919 | 124.30–130.63 | من واحد يسكت عن حقك، تعتبره خذلك. / بس من إنت تسكت عن حق غيرك، تسميها حكمة. | [contrast 2] من واحد يسكت عن حقك… (F3729) | Locked · 50mm | Tilt increases; — | P4 Evidence — stable light, readable contrast, calm gold arch | «خذلك» vs «حكمة» | Cut | Metal creak | Three.js |
| **S04_04** | 3919–4090 | 130.63–136.33 | من واحد يحچي عليك، تعتبرها إساءة. / بس من إنت تحچي عليه، تگول مجرد فضفضة. | [contrast 3] من واحد يحچي عليك… (F3919) | Locked · 50mm | Maximum imbalance; — | P4 Evidence — stable light, readable contrast, calm gold arch | «إساءة» vs «فضفضة» | Cut | Metal creak (strongest) | Three.js |
| **S04_05** | 4090–4205 | 136.33–140.17 | نفس الفعل… / بس الحكم يختلف، حسب منو اللي سواه. | نفس الفعل (F4090) | Locked · 85mm | Identical stones in both pans — still imbalanced; — | P4 Evidence — stable light, readable contrast, calm gold arch | Impact «نفس الفعل» | Cut | Silence beat | Three.js |
| **S04_06** | 4205–4442 | 140.17–148.07 | القرآن الكريم يگول: / كُونُوا قَوَّامِينَ بِالْقِسْطِ شُهَدَاءَ لِلَّهِ وَلَوْ عَلَىٰ أَنفُسِكُمْ. | [Q02 quotation start] (F4252 ⚑يدوي)<br>[Q02 quotation end] (F4364 ⚑يدوي) | LOCKED · 50mm | Knowledge Arch, scale dim behind; — | P4 Evidence — stable light, readable contrast, calm gold arch | SACRED Q02 — Amiri Quran + «النساء: من الآية ١٣٥» | T05 | NO dramatic SFX | Remotion typography layer |
| | | | ↳ *Protected F4237–4425* | | | | | | | | |
| **S04_07** | 4442–4689 | 148.07–156.30 | فإذا ميزانك يتغيّر كلما صارت القضية تخصّك… / شلون راح تعرف إنك فعلاً منصف؟ | شلون راح تعرف إنك فعلاً منصف؟ (F4545) | Slow pull-out · 50mm | Scale restrained return toward balance (not fully); — | P4 Evidence — stable light, readable contrast, calm gold arch | — | Hold into gap | Soft metal settle | Three.js |

## CH05 — انكشاف الحقيقة

| Shot | إطارات | ث | السرد | المرسى | الكاميرا / العدسة | التكوين | الإضاءة | الطباعة | الانتقال | الصوت | التقنية |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **S05_01** | 4689–4768 | 156.30–158.93 | وهنا… / تلتفت للقاضي. | تلتفت للقاضي (F4703) | Controlled pan to judge · 35mm | Judge silhouette; Judge still | P5 Collapse — light spreads through cracks, controlled contrast rise | — | Cut on «وهنا» | Low pulse (non-musical) | 2.5D |
| **S05_02** | 4768–4809 | 158.93–160.30 | وتباوع للشاهد. | وتباوع للشاهد (F4768) | Pan to witness · 35mm | Witness silhouette; — | P5 Collapse — light spreads through cracks, controlled contrast rise | — | Whip-free pan | Low pulse | 2.5D |
| **S05_03** | 4809–4978 | 160.30–165.93 | وترجع تباوع للمتهم. / وتكتشف الحقيقة اللي چنت تهرب منها من البداية. | وترجع تباوع للمتهم (F4809) | Orbit begins (adaptive camera, accelerating) · 35mm | Three silhouettes in triangle; All three still | P5 Collapse — light spreads through cracks, controlled contrast rise | — | Continuous orbit | Rising air | Three.js orbit (same body model ×3) |
| **S05_04** | 4978–5052 | 165.93–168.40 | القاضي… إنت. | القاضي… إنت (F4978) | Orbit pause; light turns on judge · 50mm | Judge revealed with SAME silhouette/costume as accused; Judge mirrors accused gesture | P5 Collapse — light spreads through cracks, controlled contrast rise | Impact «القاضي… إنت» | Cut on anchor | Identity hit (low thud, non-musical) | Three.js |
| | | | ↳ *Reveal only here — never earlier* | | | | | | | | |
| **S05_05** | 5052–5113 | 168.40–170.43 | والشاهد… إنت. | والشاهد… إنت (F5052) | Pause; light · 50mm | Witness same silhouette; Same gesture | P5 Collapse — light spreads through cracks, controlled contrast rise | Impact «والشاهد… إنت» | Cut | Identity hit #2 | Three.js |
| **S05_06** | 5113–5176 | 170.43–172.53 | والمتهم… هم إنت. | والمتهم… هم إنت (F5113) | Orbit completes 360° → stop · 35mm | All three in sync; Three figures perform identical gesture | P5 Collapse — light spreads through cracks, controlled contrast rise | Impact «والمتهم… هم إنت» | Cut | Identity hit #3 + silence | Three.js |
| **S05_07** | 5176–5306 | 172.53–176.87 | هاي المحكمة ما چانت بمكان غريب. / هاي المحكمة بداخلك. | هاي المحكمة بداخلك (F5255) | Dolly-out · 35mm → 28mm | Judge & witness dissolve into reflections inside shards; one figure remains; Figure alone | P5 Collapse — light spreads through cracks, controlled contrast rise | Impact «بداخلك» (gold) | Dissolve | Glass breath | Three.js |
| **S05_08** | 5306–5577 | 176.87–185.90 | كل مرة حكمت بيها على غيرك، ورفضت تطبّق نفس الحكم على نفسك. / كل مرة عرفت بيها غلطك، واخترت تبرّره بدل ما تصلحه. | — | Slow push · 28mm | Cracks spread across all blocks, light leaking; — | P5 Collapse — light spreads through cracks, controlled contrast rise | Engraved excuse words FRACTURE (non-sacred only) | Continuous | Stone cracking (progressive) | Three.js crack masks + Typography Fracture |
| **S05_09** | 5577–5693 | 185.90–189.77 | بس لحظة الاعتراف بالحقيقة… / مو نهاية المحاكمة. | — | Locked — stillness · 50mm | Figure stands; cracks glowing; — | P5 Collapse — light spreads through cracks, controlled contrast rise | — | Hold | DRAMATIC SILENCE (ambience ducked) | — |
| | | | ↳ *Deliberate pause before collapse* | | | | | | | | |
| **S05_10** | 5693–5848 | 189.77–194.93 | هي بداية التحرر من سجن الأعذار. | هي بداية التحرر من سجن الأعذار (F5693) | Crane up & out as wall falls · 24mm | Wall collapses outward; courtroom dissolves to open psychological space; Figure intact, standing | P5 Collapse — light spreads through cracks, controlled contrast rise | — | Hold 2.5s gap (dust settles) | WALL COLLAPSE → long tail → silence | Three.js pre-fractured blocks (no live physics) |
| | | | ↳ *Character never harmed* | | | | | | | | |

## CH06 — منهج الإمام الكاظم عليه السلام

| Shot | إطارات | ث | السرد | المرسى | الكاميرا / العدسة | التكوين | الإضاءة | الطباعة | الانتقال | الصوت | التقنية |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **S06_01** | 5848–6064 | 194.93–202.13 | بس شلون الإنسان يطلع من هاي الدائرة؟ / شلون يحاسب نفسه، بدون ما يتحول إلى إنسان يائس من نفسه؟ | — | Gentle dolly-out · 28mm | Figure amid fallen stones in open twilight; Figure kneels/stands quietly | P6 Kadhim — soft light, progressive warmth, visual stability | — | Cut | Quiet resolution air | 2.5D |
| **S06_02** | 6064–6213 | 202.13–207.10 | الإمام موسى الكاظم، عليه السلام، يرسم إلنا منهج واضح. / يگول: | الإمام موسى الكاظم، عليه السلام (F6064 ⚑يدوي) | Settling to lock · 50mm | Knowledge Arch forms; name in respectful typography only; — | P6 Kadhim — soft light, progressive warmth, visual stability | «الإمام موسى الكاظم عليه السلام» (Amiri) | T05 | Ambience low | Remotion typography |
| | | | ↳ *NO depiction of the Imam* | | | | | | | | |
| **S06_03** | 6213–6592 | 207.10–219.73 | لَيْسَ مِنَّا مَنْ لَمْ يُحَاسِبْ نَفْسَهُ فِي كُلِّ يَوْمٍ، فَإِنْ عَمِلَ حَسَناً اسْتَزَادَ اللهَ، وَإِنْ عَمِلَ سَ… | [H01 narration start] (F6213 ⚑يدوي)<br>[H01 narration end] (F6479 ⚑يدوي) | LOCKED · 50mm | Arch with narration text + source line; — | P6 Kadhim — soft light, progressive warmth, visual stability | SACRED H01 — Amiri, static + «الكافي — ج٢ — باب محاسبة العمل — ح٢» | Hold | NO SFX | Remotion typography |
| | | | ↳ *Protected F6198–6581* | | | | | | | | |
| **S06_04** | 6592–6833 | 219.73–227.77 | لاحظ دقة هذا المنهج. / أولاً: المحاسبة كل يوم. / مو بس من تصير مصيبة، أو من أحد يواجهك بغلطك. | أولاً: المحاسبة كل يوم (F6650) | Slow push · 50mm | Stage 1: a daily ring/cycle mark around the arch (day ↔ night); Figure faces arch | P6 Kadhim — soft light, progressive warmth, visual stability | «أولاً: المحاسبة كل يوم» (IBM Plex) | Cut | Soft air | 2.5D |
| | | | ↳ *Three-part structure* | | | | | | | | |
| **S06_05** | 6833–6984 | 227.77–232.80 | ثانياً: إذا سويت خير، لا تكتفي بيه. اطلب من الله المزيد. | ثانياً: إذا سويت خير (F6833) | Slow push · 50mm | Stage 2: golden particles gather gently (increase in good); — | P6 Kadhim — soft light, progressive warmth, visual stability | «ثانياً: إذا سويت خير» | Cut | Soft shimmer (non-musical) | Deterministic particles |
| **S06_06** | 6984–7359 | 232.80–245.30 | وثالثاً: إذا أخطأت، لا تبرّر الخطأ، ولا تيأس من نفسك. / استغفر الله… وتُب إليه. / وإذا ظلمت إنسان، حاول تصلح الظلم وت… | وثالثاً: إذا أخطأت (F6984)<br>استغفر الله… وتُب إليه (F7136) | Slow push → stillness · 50mm | Stage 3: cracks in a stone fill with gold (repair, not erasure); Figure places hand on stone | P6 Kadhim — soft light, progressive warmth, visual stability | «وثالثاً: إذا أخطأت» / «استغفر الله… وتُب إليه» (calm) | Cut | Very soft | 2.5D / shader |
| **S06_07** | 7359–7613 | 245.30–253.77 | المحاسبة مو حتى تكره نفسك. / المحاسبة حتى تعرف وين أخطأت… وتصلح اللي تگدر تصلحه. | المحاسبة مو حتى تكره نفسك (F7359)<br>وتصلح اللي تگدر تصلحه (F7506) | Slow orbit 90° · 85mm → 50mm | Gavel rises, rotates; head unfolds into arched Mirror of Insight (intact); Figure faces new mirror | P6 Kadhim — soft light, progressive warmth, visual stability | — | T06 Gavel to Mirror (AFTER religious evidence) | Wood → glass transformation tone | Three.js morph or hidden cut (POC 03) |
| | | | ↳ *Starts after H01 ends* | | | | | | | | |

## CH07 — الحكم النهائي

| Shot | إطارات | ث | السرد | المرسى | الكاميرا / العدسة | التكوين | الإضاءة | الطباعة | الانتقال | الصوت | التقنية |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **S07_01** | 7613–7751 | 253.77–258.37 | الليلة، قبل لا تنام… / جرّب توقف دقيقة وحدة ويا نفسك. | الليلة، قبل لا تنام (F7613) | Locked · 50mm | Intact mirror; figure before it at night; Figure stands still | P7 Gateway — warm gold & ivory, expanding space, heavy shadows recede | — | Cut | Quiet night air | Three.js reflection / 2.5D |
| | | | ↳ *Visual callback: same framing as S01_01, but intact* | | | | | | | | |
| **S07_02** | 7751–7978 | 258.37–265.93 | منو جرحت اليوم؟ / أكو حق قصّرت بيه؟ / أكو غلط بعدك دا تدافع عنه، رغم إنك تعرفه غلط؟ | [question 1] منو جرحت اليوم؟ (F7751)<br>[question 2] أكو حق قصّرت بيه؟ (F7814)<br>[question 3] أكو غلط بعدك دا تدافع عنه… (F7869) | Slow push per question · 85mm | Three questions appear one by one beside reflection; Figure lowers gaze | P7 Gateway — warm gold & ivory, expanding space, heavy shadows recede | Resolution typography (IBM Plex) — 3 questions | Cut | Soft breaths of air | Remotion typography |
| **S07_03** | 7978–8098 | 265.93–269.93 | لا تبحث عن عذر جديد. / ابحث عن شي تگدر تصلحه. | لا تبحث عن عذر جديد (F7978)<br>ابحث عن شي تگدر تصلحه (F8026) | Locked · 50mm | A new basalt block starts forming — then dissolves into light; — | P7 Gateway — warm gold & ivory, expanding space, heavy shadows recede | — | Cut | Reverse stone-form → dissolve | Three.js |
| **S07_04** | 8098–8279 | 269.93–275.97 | لأن المحكمة اللي بداخلك، مو لازم تبقى سجن إلك. / ممكن تصير بداية لتغيير حياتك. | بداية لتغيير حياتك (F8224) | Dolly-out wide as mirror frame expands into open gateway (T07) · 50mm → 24mm | Mirror frame → monumental open KHAYBAR arch gateway; Figure walks toward light | P7 Gateway — warm gold & ivory, expanding space, heavy shadows recede | — | T07 Mirror to Gateway | Footsteps on stone, open air | Three.js / 2.5D |
| **S07_05** | 8279–8475 | 275.97–282.50 | وتذكّر… / قبل لا تحاسب غيرك… / حاسب نفسك. | قبل لا تحاسب غيرك (F8318)<br>حاسب نفسك (F8380) | Locked · 24mm | Gateway; figure small inside light; Figure stops at threshold | P7 Gateway — warm gold & ivory, expanding space, heavy shadows recede | FINAL: «قبل لا تحاسب غيرك…» (ivory) then «حاسب نفسك» (gold) | Hold → T into outro | Silence under final phrase; soft air | Remotion typography |
| | | | ↳ *Callback: arch = opening mirror frame* | | | | | | | | |

## OUTRO — خاتمة خيبر

| Shot | إطارات | ث | السرد | المرسى | الكاميرا / العدسة | التكوين | الإضاءة | الطباعة | الانتقال | الصوت | التقنية |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **S08_01** | 8475–8550 | 282.50–285.00 | — | — | — · — | Official KHAYBAR outro (short, 2.5s); — | Brand | Official | Gateway light → logo (cut/dissolve TBD in integration test) | Optional KHAYBAR sonic signature (pending decision) | Existing KhaybarOutro (public/brand/reference/khaybar-outro-short.mp4) |
| | | | ↳ *Final timing pending integration test* | | | | | | | | |

## قواعد ثابتة
- الراوي من الإطار 0؛ لا شعار افتتاحي ولا شاشة سوداء.
- الهوية المشتركة للقاضي/الشاهد/المتهم لا تُكشف قبل S05_04 (F4978).
- النصوص المقدسة (S03_02، S04_06، S06_03): كاميرا ثابتة، بلا مؤثرات درامية، نص ثابت غير مفكك.
- لا تجسيد للإمام الكاظم عليه السلام — اسمه طباعياً فقط.
- الشخصية لا تتحطم؛ الذي ينهار هو جدار الأعذار.
- تحول المطرقة إلى مرآة (S06_07) يبدأ **بعد** انتهاء الرواية.
