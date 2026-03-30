(function(){'use strict';const $=(sel,ctx=document)=>ctx.querySelector(sel);const $$=(sel,ctx=document)=>[...ctx.querySelectorAll(sel)];const clamp=(v,min,max)=>Math.min(max,Math.max(min,v));const lerp=(a,b,t)=>a+(b-a)*t;const ease=(t)=>t<0.5?2*t*t:-1+(4-2*t)*t;function initScrollProgress(){const bar=$('#scroll-progress');if(!bar)return;const update=()=>{const pct=(scrollY/(document.body.scrollHeight-innerHeight))*100;bar.style.width=clamp(pct,0,100)+'%';};window.addEventListener('scroll',update,{passive:true});update();}
function initHeader(){const nav=$('#nav');if(!nav)return;const update=()=>{const y=scrollY;nav.classList.toggle('scrolled',y>40);};window.addEventListener('scroll',update,{passive:true});update();}
function initHeroText(){const h1=$('.hero-h1');if(!h1)return;$$('[data-lang]',h1).forEach(span=>{const words=span.textContent.split(' ');span.innerHTML=words.map((w,i)=>`<span class="word-reveal"style="animation-delay:${0.05 + i * 0.04}s">${w}</span>`).join(' ');});}
function initReveal(){const obs=new IntersectionObserver((entries)=>{entries.forEach(entry=>{if(entry.isIntersecting){const el=entry.target;const delay=el.dataset.delay||'0';el.style.transitionDelay=delay+'ms';el.classList.add('up');obs.unobserve(el);}});},{threshold:0.08,rootMargin:'0px 0px -40px 0px'});$$('.grid-3, .grid-2, .feat, .related-grid, .blog-grid').forEach(container=>{$$(':scope > *, :scope > .card',container).forEach((child,i)=>{child.dataset.delay=(i*80).toString();});});$$('.gallery-masonry').forEach(container=>{$$(':scope > .gallery-item',container).forEach((child,i)=>{child.dataset.delay=(i*55).toString();});});$$('.reveal').forEach(el=>obs.observe(el));}
function initFaqPageAccordion(){$$('.faq-q').forEach((btn)=>{btn.addEventListener('click',()=>{const item=btn.closest('.faq-item');if(!item)return;const wasOpen=item.classList.contains('open');const block=item.closest('.faq-section')||item.parentElement;block?.querySelectorAll('.faq-item.open').forEach((o)=>{if(o!==item)o.classList.remove('open');});item.classList.toggle('open',!wasOpen);});});}
function revealChain(el){let n=el;while(n&&n!==document.body){if(n.classList&&n.classList.contains('reveal'))n.classList.add('up');n=n.parentElement;}}
function getArticleScrollOffset(){const nav=document.getElementById('nav');const artBar=document.getElementById('art-progress');let o=nav&&nav.offsetHeight?nav.offsetHeight+16:96;if(artBar){const st=getComputedStyle(artBar);if(st.display!=='none'&&st.visibility!=='hidden'&&st.opacity!=='0'){o+=artBar.offsetHeight||2;}}
return o;}
function scrollElementIntoViewUnderHeader(el){if(!el)return;revealChain(el);requestAnimationFrame(()=>{requestAnimationFrame(()=>{const top=el.getBoundingClientRect().top+window.scrollY-getArticleScrollOffset();window.scrollTo({top:Math.max(0,top),behavior:'smooth'});});});}
function scrollToHashTarget(){const id=decodeURIComponent((location.hash||'').slice(1));if(!id)return;const el=document.getElementById(id);if(!el)return;scrollElementIntoViewUnderHeader(el);}
function initProseHashLinks(){document.addEventListener('click',(e)=>{const a=e.target.closest('a[href^="#"]');if(!a)return;const href=a.getAttribute('href');if(!href||href==='#')return;const prose=a.closest('article .prose');if(!prose)return;const id=decodeURIComponent(href.slice(1));if(!id)return;const target=document.getElementById(id);if(!target)return;e.preventDefault();if(history.replaceState){history.replaceState(null,'',location.pathname+location.search+'#'+id);}else{location.hash='#'+id;}
scrollElementIntoViewUnderHeader(target);},true);}
function initArticleToc(){const toc=document.querySelector('article .prose nav.toc-block');if(!toc||toc.dataset.tocShell==='1')return;const title=toc.querySelector('.toc-title');const list=toc.querySelector('.toc-list');if(!title||!list)return;toc.dataset.tocShell='1';const details=document.createElement('details');details.className='art-toc-details';const summary=document.createElement('summary');summary.className='art-toc-summary';const label=document.createElement('span');label.className='art-toc-summary-label';label.textContent=title.textContent.trim();const chev=document.createElement('span');chev.className='art-toc-chevron';chev.setAttribute('aria-hidden','true');summary.appendChild(label);summary.appendChild(chev);title.remove();details.appendChild(summary);details.appendChild(list);toc.appendChild(details);const mq=window.matchMedia('(min-width: 769px)');function syncTocOpen(){details.open=mq.matches;}
syncTocOpen();if(typeof mq.addEventListener==='function'){mq.addEventListener('change',syncTocOpen);}else{mq.addListener(syncTocOpen);}}
function initHeroVideoLoop(){const vid=document.getElementById('hero-video');if(!vid||vid.dataset.heroLoopArmed==='1')return;vid.dataset.heroLoopArmed='1';vid.removeAttribute('loop');const LOOP_START_SEC=1.7;const LOOP_END_SEC=4.5;const wrap=document.querySelector('.hero-video-wrap');const poster=vid.getAttribute('poster');if(wrap&&poster){wrap.style.backgroundColor='#071726';wrap.style.backgroundImage=`url("${poster.replace(/"/g,'\\"')}")`;
      wrap.style.backgroundSize = 'cover';
      wrap.style.backgroundPosition = 'center';
    }

    const jumpToLoopStart = () => {
      try {
        if (typeof vid.fastSeek === 'function') vid.fastSeek(LOOP_START_SEC);
        else vid.currentTime = LOOP_START_SEC;
      } catch (_) {
        vid.currentTime = LOOP_START_SEC;
      }
      vid.play().catch(() => {});
    };

    vid.addEventListener(
      'loadedmetadata',
      () => {
        if (vid.currentTime < LOOP_START_SEC) vid.currentTime = LOOP_START_SEC;
      },
      { once: true }
    );

    vid.addEventListener('timeupdate', () => {
      if (vid.currentTime >= LOOP_END_SEC) jumpToLoopStart();
    });
    vid.addEventListener('ended', jumpToLoopStart);
  }

  /* ── Home “Getting here” teaser: CARTO light_all (neutral) via Leaflet, lazy-loaded ── */
  function initGhTeaserMap() {
    const el = document.querySelector('.gh-preview-map-el');
    if (!el || el.dataset.ghMapReady === '1') return;

    function injectCss(href) {
      if (document.querySelector('link[data-gh-leaflet-css]')) return;
      const l = document.createElement('link');
      l.rel = 'stylesheet';
      l.href = href;
      l.crossOrigin = '';
      l.setAttribute('data-gh-leaflet-css', '1');
      document.head.appendChild(l);
    }

    function loadScript(src, onload) {
      const s = document.createElement('script');
      s.src = src;
      s.crossOrigin = '';
      s.onload = onload;
      document.body.appendChild(s);
    }

    function buildMap() {
      if (typeof L === 'undefined' || el.dataset.ghMapReady === '1') return;
      el.dataset.ghMapReady = '1';
      const NGOR = [14.7498, -17.5228]; /* Ngor Island — exact centre (OSM verified) */
      const map = L.map(el, {
        center: [14.7492, -17.5185],
        zoom: 16,
        scrollWheelZoom: false,
        zoomControl: true,
        attributionControl: true,
      });
      L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
        subdomains: 'abcd',
        maxZoom: 19,
      }).addTo(map);
      const icon = L.divIcon({className:'gh-preview-marker-wrap',html:'<div class="gh-preview-marker" aria-hidden="true"></div>',iconSize:[36,36],iconAnchor:[18,18]});
      L.marker(NGOR,{icon}).addTo(map);
      requestAnimationFrame(()=>{map.invalidateSize();setTimeout(()=>map.invalidateSize(),250);});
    }
    function start(){injectCss('https://unpkg.com/leaflet@1.9.4/dist/leaflet.css');if(typeof L!=='undefined')buildMap();else loadScript('https://unpkg.com/leaflet@1.9.4/dist/leaflet.js',buildMap);}
    const obs=new IntersectionObserver((entries)=>{entries.forEach((e)=>{if(!e.isIntersecting)return;obs.disconnect();start();});},{rootMargin:'120px',threshold:0.02});obs.observe(el);
  }
function initGalleryLightbox(){const lb=$('#lb');const lbImg=$('#lb-img');if(!lb||!lbImg||lb.dataset.lbInit==='1')return;lb.dataset.lbInit='1';const lbCls=$('#lb-close');function openLb(src,altText){if(!src)return;lbImg.alt=altText||'';lbImg.src=src;lb.classList.add('open');document.documentElement.classList.add('lb-open');}
function closeLb(){lb.classList.remove('open');document.documentElement.classList.remove('lb-open');}
$$('.gallery-item').forEach((item)=>{item.addEventListener('click',()=>{const full=item.dataset.full;const img=item.querySelector('img');const src=(full&&String(full).trim())||(img&&img.src)||'';const altText=img?img.alt:'';openLb(src,altText);});});lb.addEventListener('click',(e)=>{if(e.target===lb)closeLb();});if(lbCls){lbCls.addEventListener('click',(e)=>{e.stopPropagation();closeLb();});}
document.addEventListener('keydown',(e)=>{if(e.key==='Escape')closeLb();});}
function initGalleryImgFade(){$$('.gallery-item img').forEach((img)=>{const done=()=>img.classList.add('is-loaded');if(img.complete&&img.naturalWidth>0)done();else{img.addEventListener('load',done,{once:true});img.addEventListener('error',done,{once:true});}});}
function initTrustStatsMotion(){const block=document.querySelector('.home-proof-strip')||document.querySelector('.trust-stats-block');if(!block)return;const visClass=block.classList.contains('home-proof-strip')?'home-proof--visible':'trust-stats--visible';if(window.matchMedia('(prefers-reduced-motion: reduce)').matches){block.classList.add(visClass);return;}
const obs=new IntersectionObserver((entries)=>{entries.forEach((e)=>{if(e.isIntersecting){block.classList.add(visClass);obs.unobserve(block);}});},{threshold:0.1,rootMargin:'0px 0px -5% 0px'});obs.observe(block);}
document.addEventListener('DOMContentLoaded',()=>{initScrollProgress();initHeader();initArticleToc();initHeroText();initHeroVideoLoop();initTrustStatsMotion();initGhTeaserMap();initGalleryLightbox();initGalleryImgFade();initReveal();initFaqPageAccordion();initProseHashLinks();scrollToHashTarget();});window.addEventListener('hashchange',scrollToHashTarget);window.toggleMenu=function(){const links=document.getElementById('nav-links');if(links)links.classList.toggle('open');};window.toggleLangDD=function(e){if(e&&e.stopPropagation)e.stopPropagation();const dd=document.getElementById('lang-dd');if(dd)dd.classList.toggle('open');};document.addEventListener('click',()=>{const dd=document.getElementById('lang-dd');if(dd)dd.classList.remove('open');});})();function copyURL(){navigator.clipboard.writeText(location.href).then(()=>{const el=document.querySelector('.copy-success');if(el){el.style.display='inline';setTimeout(()=>{el.style.display='none';},2000);}});}
function shareWA(){const msg=encodeURIComponent(document.title+' — '+location.href);window.open('https://wa.me/?text='+msg,'_blank');}
function toggleArticleFaq(btn){const item=btn.closest('.article-faq-item');const isOpen=item.classList.contains('open');const answer=item.querySelector('.article-faq-answer');const section=item.closest('.article-faq-section');if(section){section.querySelectorAll('.article-faq-item.open').forEach(other=>{if(other!==item){other.classList.remove('open');other.querySelector('button').setAttribute('aria-expanded','false');}});}
item.classList.toggle('open',!isOpen);btn.setAttribute('aria-expanded',String(!isOpen));}
document.addEventListener('DOMContentLoaded',()=>{document.querySelectorAll('.article-faq-section').forEach(section=>{const first=section.querySelector('.article-faq-item');if(first&&!first.classList.contains('open')){first.classList.add('open');const btn=first.querySelector('button');if(btn)btn.setAttribute('aria-expanded','true');}});});document.addEventListener('DOMContentLoaded',function initFooterQuotes(){const wrap=document.querySelector('[id^="fq-wrap-"]');if(!wrap)return;const phrases=wrap.querySelectorAll('.fq-phrase');const total=phrases.length;if(!total)return;phrases[0].classList.add('active');let cur=0;function show(idx){phrases[cur].classList.remove('active');cur=(idx+total)%total;phrases[cur].classList.add('active');}
setInterval(()=>show(cur+1),3800);});(function initHomeGallery(){const viewport=document.getElementById('hg-viewport');const prevBtn=document.getElementById('hg-prev');const nextBtn=document.getElementById('hg-next');const dotsEl=document.getElementById('hg-dots');const progFill=document.getElementById('hg-progress-fill');const curNumEl=document.getElementById('hg-cur-num');const captionEl=document.getElementById('hg-caption');if(!viewport)return;const imgs=viewport.querySelectorAll('.hg-img');const total=imgs.length;if(!total)return;const INTERVAL=3000;let cur=0;let timer=null;let paused=false;const dots=[];if(dotsEl){imgs.forEach((_,i)=>{const d=document.createElement('button');d.className='hg-dot'+(i===0?' hg-dot-active':'');d.setAttribute('aria-label','Photo '+(i+1));d.addEventListener('click',()=>{stopAuto();goTo(i);startAuto();});dotsEl.appendChild(d);dots.push(d);});}
function pad(n){return String(n+1).padStart(2,'0');}
function showCaption(img){if(!captionEl)return;const cap=(img&&img.getAttribute('data-caption'))||'';captionEl.textContent=cap;captionEl.classList.toggle('hg-cap-visible',cap.length>0);}
function updateUI(idx){imgs.forEach((img,i)=>{img.classList.toggle('hg-active',i===idx);});dots.forEach((d,i)=>d.classList.toggle('hg-dot-active',i===idx));if(curNumEl)curNumEl.textContent=pad(idx);if(imgs[idx])showCaption(imgs[idx]);}
function goTo(idx){cur=((idx%total)+total)%total;updateUI(cur);}
function runProgress(){if(!progFill)return;progFill.style.transition='none';progFill.style.width='0%';requestAnimationFrame(()=>requestAnimationFrame(()=>{progFill.style.transition='width '+INTERVAL+'ms linear';progFill.style.width='100%';}));}
function startAuto(){stopAuto();runProgress();timer=setInterval(()=>{if(!paused){goTo(cur+1);runProgress();}},INTERVAL);}
function stopAuto(){clearInterval(timer);if(progFill){progFill.style.transition='none';progFill.style.width='0%';}}
if(prevBtn)prevBtn.addEventListener('click',()=>{stopAuto();goTo(cur-1);startAuto();});if(nextBtn)nextBtn.addEventListener('click',()=>{stopAuto();goTo(cur+1);startAuto();});viewport.addEventListener('mouseenter',()=>{paused=true;});viewport.addEventListener('mouseleave',()=>{paused=false;});let touchX0=null;viewport.addEventListener('touchstart',e=>{touchX0=e.touches[0].clientX;},{passive:true});viewport.addEventListener('touchend',e=>{if(touchX0===null)return;const dx=e.changedTouches[0].clientX-touchX0;touchX0=null;if(Math.abs(dx)<30)return;stopAuto();goTo(dx<0?cur+1:cur-1);startAuto();});
/* Scroll parallax: image moves at 70% of scroll speed */
(function(){const frame=document.querySelector('.hg-frame');if(!frame)return;function applyParallax(){const r=frame.getBoundingClientRect();if(r.bottom<0||r.top>window.innerHeight)return;const p=(window.innerHeight-r.top)/(window.innerHeight+r.height);const off=(p-0.5)*54;frame.style.setProperty('--hg-py',off+'px');}window.addEventListener('scroll',applyParallax,{passive:true});applyParallax();})();
goTo(0);startAuto();})();(function initReviewsSlider(){function gapForTrack(track){const g=parseFloat(getComputedStyle(track).gap);return Number.isFinite(g)?g:16;}
function bindTrack(track){if(!track)return;const bookingMode=track.getAttribute('data-booking-slider')==='1';const cards=track.querySelectorAll('.review-card');const total=cards.length;if(!total)return;let cur=0;function visCount(){if(bookingMode)return 1;if(window.innerWidth>=960)return 3;if(window.innerWidth>=600)return 2;return 1;}
function maxIdx(){return Math.max(0,total-visCount());}
function go(idx){const max=maxIdx();cur=Math.max(0,Math.min(idx,max));const card=cards[0];const cardW=card?card.getBoundingClientRect().width:0;const gap=gapForTrack(track);track.style.transform='translateX(-'+(cur*(cardW+gap))+'px)';}
go(0);let resizeTimer;window.addEventListener('resize',()=>{clearTimeout(resizeTimer);resizeTimer=setTimeout(()=>{go(Math.min(cur,maxIdx()));},200);},{passive:true});setInterval(()=>{if(cur<maxIdx())go(cur+1);else go(0);},bookingMode?6000:5000);}
bindTrack(document.getElementById('reviews-inner'));bindTrack(document.getElementById('booking-reviews-inner'));document.querySelectorAll('.rc-text').forEach(el=>{el.addEventListener('click',()=>el.classList.toggle('expanded'));el.style.cursor='pointer';if(!el.title||!String(el.title).trim())el.title='Click to expand';});})();
/* ══ Surf Forecast Widget — Open-Meteo API ══ */
(function(){
  /* SVG icons — stroke-based, matches site DA */
  var FC_SVG={
    wave:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M2 12c1.5 2 3.5 2 5 0s3.5-2 5 0 3.5 2 5 0"/><path d="M2 17c1.5 2 3.5 2 5 0s3.5-2 5 0 3.5 2 5 0"/><path d="M7 4l3-3 4 3M14 4v4"/></svg>',
    period:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 3"/></svg>',
    dir:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M12 3v2M12 19v2M3 12h2M19 12h2"/><path d="M12 8l-2 8 2-2 2 2z" fill="currentColor" stroke="none"/></svg>',
    swell:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M2 10c2-3 4-3 6 0s4 3 6 0 4-3 6 0"/><path d="M2 16c2-3 4-3 6 0s4 3 6 0 4-3 6 0"/></svg>',
    wind:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M9.59 4.59A2 2 0 1111 8H2"/><path d="M12.59 19.41A2 2 0 1014 16H2"/><path d="M17.5 8A2.5 2.5 0 1120 10.5H2"/></svg>',
    temp:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M14 14.76V3.5a2.5 2.5 0 00-5 0v11.26a4.5 4.5 0 105 0z"/></svg>'
  };
  /* Icon accent colours aligned with site palette */
  var FC_COL={wave:'var(--ocean)',period:'var(--navy)',dir:'var(--fire)',swell:'var(--ocean)',wind:'var(--navy)',temp:'var(--fire)'};

  function runWidget(w){
    var L={now:w.dataset.lblNow||'Right now',height:w.dataset.lblHeight||'Wave height',
      period:w.dataset.lblPeriod||'Period',dir:w.dataset.lblDir||'Direction',
      swell:w.dataset.lblSwell||'Swell',wind:w.dataset.lblWind||'Wind',
      temp:w.dataset.lblTemp||'Water temp',sevenday:w.dataset.lbl7day||'7-day forecast',
      powered:w.dataset.lblPowered||'Data: Open-Meteo.com',
      err:w.dataset.lblErr||'Forecast temporarily unavailable'};

    var DIRS=['N','NNE','NE','ENE','E','ESE','SE','SSE','S','SSW','SW','WSW','W','WNW','NW','NNW'];
    function degToDir(d){return DIRS[Math.round(d/22.5)%16];}
    function dayName(iso){var d=new Date(iso+'T12:00:00');return d.toLocaleDateString(undefined,{weekday:'short'});}
    function dayDate(iso){var d=new Date(iso+'T12:00:00');return d.toLocaleDateString(undefined,{day:'numeric',month:'short'});}
    function windLabel(kt){if(kt<4)return'Calm';if(kt<11)return'Light';if(kt<17)return'Moderate';if(kt<28)return'Fresh';return'Strong';}

    var mURL='https://marine-api.open-meteo.com/v1/marine?latitude=14.75&longitude=-17.51'+
      '&current=wave_height,wave_direction,wave_period,swell_wave_height,swell_wave_direction,swell_wave_period'+
      '&hourly=sea_surface_temperature&daily=wave_height_max,wave_period_max,swell_wave_height_max'+
      '&timezone=Africa/Dakar&forecast_days=7';
    var wURL='https://api.open-meteo.com/v1/forecast?latitude=14.75&longitude=-17.51'+
      '&current=wind_speed_10m,wind_direction_10m&timezone=Africa/Dakar&forecast_days=1';

    Promise.all([fetch(mURL).then(function(r){return r.json();}),
                 fetch(wURL).then(function(r){return r.json();})])
    .then(function(res){
      var m=res[0],wd=res[1];
      var c=m.current||{};
      var wc=wd.current||{};
      var sst='--';
      if(m.hourly&&m.hourly.sea_surface_temperature){
        var temps=m.hourly.sea_surface_temperature.filter(function(v){return v!==null;});
        if(temps.length)sst=Math.round(temps[0])+'°C';
      }
      var windKt=wc.wind_speed_10m?Math.round(wc.wind_speed_10m/1.852):0;
      var windDir=wc.wind_direction_10m?degToDir(wc.wind_direction_10m):'';

      function stat(key,val,unit,lbl){
        return '<div class="fc-stat"><div class="fc-stat-icon" style="color:'+FC_COL[key]+'">'+FC_SVG[key]+'</div>'
          +'<div class="fc-stat-val">'+val+(unit?'<span class="fc-stat-unit">'+unit+'</span>':'')+'</div>'
          +'<div class="fc-stat-lbl">'+lbl+'</div></div>';
      }

      var html='<div class="fc-now-label">'+L.now+'</div>';
      html+='<div class="fc-current">';
      html+=stat('wave',(c.wave_height||'--'),'m',L.height);
      html+=stat('period',(c.wave_period?c.wave_period.toFixed(1):'--'),'s',L.period);
      html+=stat('dir',(c.wave_direction?degToDir(c.wave_direction):'--'),'',L.dir);
      html+=stat('swell',(c.swell_wave_height||'--'),'m',L.swell);
      html+=stat('wind',windKt,'kt',L.wind+(windDir?' · '+windDir:''));
      html+=stat('temp',sst,'',L.temp);
      html+='</div>';

      if(m.daily&&m.daily.wave_height_max){
        var days=m.daily.time||[];
        var maxH=m.daily.wave_height_max||[];
        var ceil=Math.max.apply(null,maxH.map(function(v){return v||0;}))||2;
        html+='<div class="fc-chart-wrap"><p class="fc-chart-title">'+L.sevenday+'</p><div class="fc-chart">';
        for(var i=0;i<days.length&&i<7;i++){
          var hv=maxH[i]||0;
          var pct=Math.max(6,Math.round((hv/ceil)*88));
          /* colour-code bars: >1.5m = fire accent, else ocean */
          var barCol=hv>=1.5?'var(--fire)':'var(--ocean)';
          html+='<div class="fc-bar-group"><div class="fc-bar-wrap"><div class="fc-bar" style="height:'+pct+'%;background:'+barCol+'"><span class="fc-bar-val">'+hv.toFixed(1)+'m</span></div></div><div class="fc-bar-day">'+dayName(days[i])+'</div><div class="fc-bar-date">'+dayDate(days[i])+'</div></div>';
        }
        html+='</div></div>';
      }
      html+='<div class="fc-credit"><a href="https://open-meteo.com/" target="_blank" rel="noopener">'+L.powered+'</a></div>';
      w.innerHTML=html;
    }).catch(function(){
      w.innerHTML='<div class="fc-err">'+L.err+'</div>';
    });
  }

  /* Run on every fc-widget instance (surfing page + homepage) */
  document.querySelectorAll('.fc-widget').forEach(function(el){runWidget(el);});
  var legacy=document.getElementById('fc-widget');
  if(legacy&&!legacy.classList.contains('fc-widget'))runWidget(legacy);
})();
