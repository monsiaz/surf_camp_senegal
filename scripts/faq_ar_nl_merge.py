# -*- coding: utf-8 -*-
"""Arabic + Dutch strings merged into SECTIONS in 22_build_surfing_faq.build_super_faq."""
import copy


def merge_faq_sections(sections):
    """Deep-copy sections and add missing nl/ar (and section titles) for Super FAQ."""
    out = copy.deepcopy(sections)
    by_id = {s["id"]: s for s in out}

    # Section titles missing nl/ar in base data
    if "accommodation" in by_id:
        by_id["accommodation"]["title"].setdefault(
            "nl", "Accommodatie & wat is inbegrepen"
        )
        by_id["accommodation"]["title"].setdefault(
            "ar", "الإقامة وما يشمله السعر"
        )
    if "surf-conditions" in by_id:
        by_id["surf-conditions"]["title"].setdefault(
            "nl", "Surfomstandigheden & beste seizoen"
        )
        by_id["surf-conditions"]["title"].setdefault(
            "ar", "ظروف الأمواج وأفضل موسم"
        )
    if "practical" in by_id:
        by_id["practical"]["title"].setdefault("nl", "Praktische informatie")
        by_id["practical"]["title"].setdefault("ar", "معلومات عملية")

    # Per-section FAQ (q_patch, a_patch) — only nl/ar keys; merged into existing dicts
    patches = {
        "getting-there": [
            (
                {
                    "nl": "Waar ligt Ngor Island precies?",
                    "ar": "أين تقع جزيرة نغور بالضبط؟",
                },
                {
                    "nl": "Ngor Island ligt op ongeveer 800 meter voor het schiereiland Cap-Vert bij Dakar, Senegal, in West-Afrika. Het is een klein, autovrij eiland dat je met een korte pirogue (traditionele houten boot) vanaf het strand van Ngor bereikt. Vanaf Dakar-Yoff International Airport (DSS) is het ongeveer 20 minuten met taxi of Uber.",
                    "ar": "تقع جزيرة نغور على بعد نحو 800 متر من شبه جزيرة كاب فيرت في داكار، السنغال، غرب أفريقيا. هي جزيرة صغيرة خالية من السيارات، تُرسو إليها بعبور قصير بالبيروغ (قارب خشبي تقليدي) من شاطئ نغور. تبعد نحو 20 دقيقة عن مطار داكار يوف الدولي (DSS) بالسيارة أو أوبر.",
                },
            ),
            (
                {
                    "nl": "Hoe kom ik van de luchthaven van Dakar naar Ngor Island?",
                    "ar": "كيف أصل من مطار داكار إلى جزيرة نغور؟",
                },
                {
                    "nl": "Stap 1: Neem een taxi of Uber van Blaise Diagne International Airport (DSS) naar het strand van Ngor. De rit duurt ongeveer 20–30 minuten en kost circa 5.000–8.000 CFA (ongeveer €8–12). Stap 2: Loop naar de kleine steiger op het strand van Ngor en neem de pirogue naar Ngor Island. De overtocht duurt ongeveer 5 minuten en kost minder dan 500 CFA (minder dan €1). Pirogues varen de hele dag door tot ongeveer 22:00. Ons team kan ook een ophaalservice regelen; laat het ons vooraf weten via WhatsApp.",
                    "ar": "الخطوة 1: خذ سيارة أجرة أو أوبر من مطار بليز دياغن الدولي (DSS) إلى شاطئ نغور. تستغرق الرحلة نحو 20–30 دقيقة وتكلف حوالي 5000–8000 فرنك غرب أفريقي (نحو 8–12 يورو). الخطوة 2: امشِ إلى الرصيف الصغير في شاطئ نغور واركب البيروغ إلى الجزيرة. تستغرق العبور نحو 5 دقائق وتكلف أقل من 500 فرنك (أقل من يورو واحد). تتوفر القوارب طوال اليوم حتى حوالي 22:00. يمكن لفريقنا ترتيب استقبالك؛ أخبرنا مسبقاً عبر واتساب.",
                },
            ),
            (
                {
                    "nl": "Zijn er directe vluchten naar Dakar?",
                    "ar": "هل توجد رحلات جوية مباشرة إلى داكار؟",
                },
                {
                    "nl": "Ja. Blaise Diagne International Airport (DSS) heeft directe verbindingen vanuit onder meer Parijs (Air France, Transavia, Air Sénégal), Brussel, Casablanca, Madrid, Londen, Frankfurt, Amsterdam en vele Afrikaanse hubs. Vluchtduur: Parijs circa 6 uur, Londen 7 uur, Madrid 5 uur, Frankfurt en Amsterdam circa 7 uur.",
                    "ar": "نعم. يستقبل مطار بليز دياغن الدولي (DSS) رحلات مباشرة من باريس (إير فرانس، ترانافيا، إير سنغال)، وبروكسل، والدار البيضاء، ومدريد، ولندن، وفرانكفورت، وأمستردام، وعدة محاور أفريقية. مدة الرحلة تقريباً: باريس 6 ساعات، لندن 7، مدريد 5، فرانكفورت وأمستردام نحو 7 ساعات.",
                },
            ),
        ],
        "surf-levels": [
            (
                {
                    "nl": "Welk surfniveau heb ik nodig om mee te doen?",
                    "ar": "ما مستوى ركوب الأمواج المطلوب للانضمام؟",
                },
                {
                    "nl": "Geen ervaring nodig. We verwelkomen complete beginners tot gevorderde surfers. Onze coaches maken voor elke gast gepersonaliseerde sessies, ongeacht het niveau. Beginners starten op grote foamboards bij Ngor Left, een vergevingsgezinde en constante golf. Gevorderden tussen surfers werken bij Ngor Left en op kleinere dagen aan Ngor Right. Zeer gevorderden surfen Ngor Right op volle grootte met video-analyse.",
                    "ar": "لا حاجة لأي خبرة. نرحب بالمبتدئين تماماً وللمتقدمين. يصمم المدربون جلساتاً مخصصة لكل ضيف بغض النظر عن المستوى. يبدأ المبتدئون على ألواح فوم كبيرة في Ngor Left، وهي موجة متسامحة ومنتظمة. المتوسطون يتدربون في Ngor Left وأيام Ngor Right الأصغر. المتقدمون يتعاملون مع Ngor Right بحجمها الكامل مع تدريب بالفيديو.",
                },
            ),
            (
                {
                    "nl": "Is video-analyse inbegrepen bij het coaching?",
                    "ar": "هل تحليل الفيديو مشمول في التدريب؟",
                },
                {
                    "nl": "Ja, video-analyse is een kernonderdeel van ons coachingprogramma zonder extra kosten. We filmen je surfsessies vanaf het strand of uit het water en bekijken het materiaal samen op een tablet. Je ziet precies wat je lichaam doet in elke fase van de golf: peddelen, pop-up, bottom turn en trim. Deze visuele feedback versnelt het leren sterk vergeleken met alleen verbale coaching — vooral handig als je als intermediate vastzit op een plateau.",
                    "ar": "نعم، يعد تحليل الفيديو جزءاً أساسياً من برنامج التدريب دون تكلفة إضافية. نصوّر جلساتك من الشاطئ أو من الماء ثم نراجع اللقطات معك على جهاز لوحي. ترى بالضبط ما يفعله جسمك في كل مرحلة: التجديف، النهوض، المنعطف السفلي، والتوازن على الموجة. هذه الملاحظات البصرية تسرّع التعلم كثيراً مقارنة بالتوجيه الشفهي فقط — وهي مفيدة جداً للمتوسطين الذين يشعرون بجمود في التقدم.",
                },
            ),
            (
                {
                    "nl": "Wat zijn Ngor Right en Ngor Left?",
                    "ar": "ما هما Ngor Right وNgor Left؟",
                },
                {
                    "nl": "Ngor Right is een beroemde rechtse point break die te zien was in de surffilm ‘The Endless Summer’ (1964). Het is een krachtige, constante golf die over een rotsrif breekt, met lange rides van 50–100+ meter. Het is het beste voor intermediate tot gevorderde surfers en werkt vaak het best bij middel- tot hoogwater met stevige noord- of noordwestelijke swell. Ngor Left is een vergevingsgezindere linkse golf dichter bij het strand, met zand- en rotsbodem. Uitstekend voor beginners en intermediates, ook op kleinere dagen. Beide spots bereik je in ongeveer 5 minuten met de pirogue vanaf Ngor Island.",
                    "ar": "Ngor Right هو موج يميني شهير ظهر في فيلم التصفح «The Endless Summer» عام 1964. موجة قوية وثابتة تنكسر فوق شعاب صخرية وتمنح ركوباً طويلاً بين 50 و100+ متر. أنسب للمتوسطين والمتقدمين، وغالباً بمد متوسط إلى مرتفع وسويل شمالي أو شمالي غربي قوي. أما Ngor Left فهي موجة يسرى أكثر تسامحاً أقرب إلى الشاطئ، بقاعة من الرمل والصخر. ممتازة للمبتدئين والمتوسطين، وتعمل جيداً حتى في الأيام الأهدأ. يمكن الوصول إلى الموجتين بعبور قصير بالبيروغ من جزيرة نغور.",
                },
            ),
        ],
        "accommodation": [
            (
                {
                    "nl": "Wat zit er in de prijs inbegrepen?",
                    "ar": "ماذا يشمل السعر؟",
                },
                {
                    "nl": "Je verblijf bij Ngor Surfcamp Teranga omvat: accommodatie in een eigen of gedeelde kamer, dagelijks ontbijt en diner (authentieke Senegalese keuken), dagelijkse surf guiding naar de beste spot, gratis theorielessen, boottransfers naar Ngor Right en Left, zwembad en gemeenschappelijke ruimtes, gratis wifi overal en dagelijkse schoonmaak. Videocoaching hoort bij het programma. Extra’s zijn optioneel: trips naar andere Dakar-spots en materiaalhuur indien nodig.",
                    "ar": "يشمل إقامتك في Ngor Surfcamp Teranga: السكن في غرفة خاصة أو مشتركة، إفطار وعشاء يوميين (مطبخ سنغالي أصيل)، إرشاداً يومياً لأفضل نقطة، دروس نظرية مجانية يومية، تنقلاً بالقوارب إلى Ngor Right وLeft، مسبحاً ومساحات مشتركة، واي فاي مجاناً في كل مكان، وتنظيفاً يومياً للغرف. جلسات التدريب بالفيديو جزء من البرنامج. الإضافات الاختيارية: رحلات إلى مواقع أخرى في داكار، واستئجار معدات إن لزم.",
                },
            ),
            (
                {
                    "nl": "Kan ik alleen accommodatie boeken zonder surfcoaching?",
                    "ar": "هل يمكنني حجز الإقامة فقط دون تدريب على التصفح؟",
                },
                {
                    "nl": "Absoluut. We bieden verblijf-only opties voor ervaren surfers die het eiland als basis en het eten willen, zonder de vaste coachingssessies. Je kunt wel deelnemen aan dagelijkse surf guiding, theorielessen en boottransfers. Geef je voorkeur door bij het boeken via WhatsApp.",
                    "ar": "بالتأكيد. نوفر خيارات إقامة فقط لمن لديهم خبرة ويريدون قاعدة على الجزيرة والطعام دون جلسات تدريب منظمة. يمكنك مع ذلك الانضمام إلى الإرشاد اليومي ودروس النظرية وتنقلات القوارب. أخبرنا بتفضيلاتك عند الحجز عبر واتساب.",
                },
            ),
        ],
        "surf-conditions": [
            (
                {
                    "nl": "Wanneer is de beste tijd om te surfen bij Ngor Island?",
                    "ar": "متى أفضل وقت للتصفح في جزيرة نغور؟",
                },
                {
                    "nl": "Je kunt het hele jaar surfen in Ngor — een groot voordeel t.o.v. veel Europese bestemmingen. Het hoogseizoen loopt van oktober tot april, wanneer regelmatige noordelijke en noordwestelijke Atlantische swell de beste golven bij Ngor Right geeft (2–4 m face). De zomer (mei–september) is warmer met lichtere swell, ideaal voor beginners en intermediates. Watertemperatuur het hele jaar ongeveer 22–27 °C; lucht 24–34 °C.",
                    "ar": "يمكن ركوب الأمواج على مدار السنة في نغور — من مزاياها الكبرى مقارنة بوجهات أوروبية كثيرة. موسم الذروة من أكتوبر إلى أبريل، عندما تجلب سويل الأطلسي الشمالي والشمالي الغربي أفضل الأمواج في Ngor Right (وجه الموجة نحو 2–4 أمتار). الصيف (مايو–سبتمبر) أدفأ مع سويل أخف، مناسب للمبتدئين والمتوسطين. حرارة الماء طوال العام بين 22 و27°م، والهواء بين 24 و34°م.",
                },
            ),
            (
                {
                    "nl": "Heb ik een wetsuit nodig?",
                    "ar": "هل أحتاج بدلة غوص (النيوبرين)؟",
                },
                {
                    "nl": "Meestal niet. Het water in Senegal blijft het hele jaar tussen 22–27 °C. Zwembroek of boardshorts volstaan vaak van april tot november. Sommigen kiezen in de winter (december–maart) voor een shorty of lange rashguard tegen zon en lichte afkoeling (water soms 22–23 °C). Rashguards en basis wetsuits kun je bij ons lenen.",
                    "ar": "غالباً لا. تبقى حرارة الماء في السنغال بين 22 و27°م طوال العام. يكفي ملابس سباحة أو شورت من أبريل إلى نوفمبر. قد يفضّل البعض بدلة قصيرة أو قميصاً طويلاً للحماية من الشمس في الشتاء (ديسمبر–مارس) عندما يهبط الماء إلى 22–23°م. نوفر قمصان حماية وبدلات أساسية للضيوف.",
                },
            ),
        ],
        "practical": [
            (
                {
                    "nl": "Welk visum heb ik nodig voor Senegal?",
                    "ar": "ما التأشيرة المطلوبة للسنغال؟",
                },
                {
                    "nl": "Staatsburgers van de EU, VK, VS, Canada en de meeste westerse landen hebben geen visum nodig. Bij aankomst op Blaise Diagne krijg je een gratis stempel voor 90 dagen. Controleer vóór je vlucht altijd de actuele inreisregels bij je ambassade of overheidsreisadvies.",
                    "ar": "مواطنو الاتحاد الأوروبي وبريطانيا والولايات المتحدة وكندا ومعظم الدول الغربية لا يحتاجون تأشيرة. تحصل عند الوصول إلى مطار بليز دياغن على ختم مجاني لمدة 90 يوماً. تحقق دائماً من قواعد الدخول الحالية لدى قنصليتك أو جهة السفر الرسمية قبل حجز الرحلة.",
                },
            ),
            (
                {
                    "nl": "Welke munteenheid wordt gebruikt? Kan ik met pin betalen?",
                    "ar": "ما العملة المستخدمة؟ هل يمكن الدفع بالبطاقة؟",
                },
                {
                    "nl": "Senegal gebruikt de West-Afrikaanse CFA-frank (XOF). Op Ngor Island zijn de meeste betalingen contant; pininfrastructuur is beperkt. Haal CFA bij geldautomaten in Dakar voordat je de pirogue neemt. Grote automaten op de luchthaven en in centraal Dakar accepteren Visa en Mastercard. 1 EUR ≈ 650–660 XOF. Voor aanbetalingen accepteren we bankoverschrijving of PayPal.",
                    "ar": "تستخدم السنغال فرنك غرب أفريقيا (XOF). أغلب المعاملات في جزيرة نغور نقداً؛ بنية الدفع بالبطاقة محدودة. يُنصح بسحب الفرنك من صرافات داكار قبل ركوب البيروغ. الصرافات الكبيرة في المطار ووسط المدينة تقبل فيزا وماستركارد. اليورو الواحد نحو 650–660 XOF. نقبل تحويلاً بنكياً أو باي بال لدفعات الحجز.",
                },
            ),
            (
                {
                    "nl": "Hoe boek ik? Hoe snel antwoorden jullie?",
                    "ar": "كيف أحجز؟ وما سرعة ردكم؟",
                },
                {
                    "nl": "Het makkelijkst: stuur ons een WhatsApp (+221 78 925 70 25) met je data, aantal gasten en surfniveau. Je kunt ook het boekingsformulier op de site invullen; dat opent een vooringevulde WhatsApp. We reageren binnen 24 uur, meestal sneller tijdens de Senegalese dag (8:00–20:00 GMT). Na bevestiging sturen we een boekingsbevestiging en betaallink voor de aanbetaling.",
                    "ar": "الطريقة الأسهل: راسلنا على واتساب (+221 78 925 70 25) مع التواريخ وعدد الضيوف ومستوى التصفح. يمكنك أيضاً ملء نموذج الحجز في الموقع فيفتح رسالة واتساب جاهزة. نرد خلال 24 ساعة، وغالباً أسرع في أوقات النهار في السنغال (8:00–20:00 بتوقيت غرينتش). بعد التأكيد نرسل تأكيد الحجز ورابط دفع العربون.",
                },
            ),
        ],
    }

    for sec_id, faq_tuples in patches.items():
        sec = by_id.get(sec_id)
        if not sec:
            continue
        for i, (q_extra, a_extra) in enumerate(faq_tuples):
            if i >= len(sec["faqs"]):
                break
            q, a = sec["faqs"][i]
            q.update(q_extra)
            a.update(a_extra)

    return out
