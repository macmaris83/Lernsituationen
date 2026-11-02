/* Reusable 1.8.3 learning-video preview. Optional materials never gate learning progress. */
(()=>{'use strict';
 const script=document.currentScript;
 const previewURL=new URL('lernvideo-preview.png',script?.src||new URL('assets/',document.baseURI)).href;
 let serial=0,scheduled=false;
 function previewImage(value){if(typeof value!=='string'||!/^assets\/[A-Za-z0-9_./-]+\.(?:png|jpe?g|webp|svg)$/i.test(value)||value.split('/').includes('..'))return previewURL;return new URL(value,document.baseURI).href;}
 function videoURL(value){
  if(typeof value!=='string'||!value.trim())return null;
  let source;try{source=new URL(value,document.baseURI);}catch{return null;}
  if(!/^https?:$/.test(source.protocol))return null;
  const host=source.hostname.toLowerCase().replace(/^www\./,'');let id;
  if(host==='youtube.com'||host==='youtube-nocookie.com'||host==='youtu.be'){
   id=host==='youtu.be'?source.pathname.split('/')[1]:source.pathname.startsWith('/embed/')?source.pathname.split('/')[2]:source.pathname.startsWith('/shorts/')?source.pathname.split('/')[2]:source.searchParams.get('v');
   if(!/^[A-Za-z0-9_-]{11}$/.test(id||''))return null;
   const url=new URL('https://www.youtube-nocookie.com/embed/'+id);source.searchParams.forEach((v,k)=>{if(!['v','origin'].includes(k))url.searchParams.set(k,v);});
   url.searchParams.set('enablejsapi','1');url.searchParams.set('playsinline','1');url.searchParams.set('controls','1');
   if(/^https?:$/.test(location.protocol))url.searchParams.set('origin',location.origin);
   return {url:url.href,provider:'youtube'};
  }
  if(host==='vimeo.com'||host==='player.vimeo.com'){
   id=source.pathname.match(/(?:\/video)?\/(\d+)(?:\/|$)/)?.[1];if(!id)return null;
   const url=new URL('https://player.vimeo.com/video/'+id);source.searchParams.forEach((v,k)=>url.searchParams.set(k,v));
   url.searchParams.set('api','1');return {url:url.href,provider:'vimeo'};
  }
  return null;
 }
 function placeholder(frame){
  const video=videoURL(frame.getAttribute('src')||frame.getAttribute('data-src'));if(!video)return null;
  const node=document.createElement('div');node.dataset.learnvideoSrc=video.url;node.dataset.learnvideoProvider=video.provider;
  node.dataset.learnvideoTitle=frame.getAttribute('title')||'Lernvideo';const poster=frame.getAttribute('data-learnvideo-preview')||frame.getAttribute('data-poster');if(poster)node.dataset.learnvideoPreview=poster;
  const width=Number(frame.getAttribute('width')),height=Number(frame.getAttribute('height'));
  if(width>0&&height>0)node.dataset.learnvideoRatio=String(width/height);
  return node;
 }
 function prepareHTML(content){
  if(typeof content!=='string'||!/<iframe\b/i.test(content))return content;
  const template=document.createElement('template');template.innerHTML=content;
  template.content.querySelectorAll('iframe').forEach(frame=>{const node=placeholder(frame);if(node)frame.replaceWith(node);});
  return template.innerHTML;
 }
 function createPreview(node){
  if(node.dataset.learnvideoReady)return;
  const video=videoURL(node.dataset.learnvideoSrc);if(!video)return;
  node.dataset.learnvideoReady='true';node.classList.add('learnvideo');
  const panelID='learnvideo-panel-'+(++serial),title=node.dataset.learnvideoTitle||'Lernvideo';
  const open=document.createElement('button');open.type='button';open.className='learnvideo-preview';open.setAttribute('aria-expanded','false');open.setAttribute('aria-controls',panelID);open.setAttribute('aria-label',title+' öffnen');
  const image=document.createElement('img');image.src=previewImage(node.dataset.learnvideoPreview);image.alt=title+' · Lernvideo';image.width=1672;image.height=941;open.append(image);
  const panel=document.createElement('div');panel.id=panelID;panel.className='learnvideo-expanded';panel.hidden=true;
  const player=document.createElement('div');player.className='learnvideo-player';
  const ratio=Number(node.dataset.learnvideoRatio);if(Number.isFinite(ratio)&&ratio>.5&&ratio<4)player.style.aspectRatio=String(ratio);
  const close=document.createElement('button');close.type='button';close.className='learnvideo-close';close.textContent='Video einklappen';
  panel.append(player,close);node.replaceChildren(open,panel);let iframe;
  function pause(){if(iframe?.contentWindow){const origin=new URL(video.url).origin;const message=video.provider==='youtube'?{event:'command',func:'pauseVideo',args:[]}:{method:'pause'};iframe.contentWindow.postMessage(JSON.stringify(message),origin);}}
  open.addEventListener('click',()=>{
   if(!iframe){iframe=document.createElement('iframe');iframe.src=video.url;iframe.title=title;iframe.allow='accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share';iframe.allowFullscreen=true;iframe.referrerPolicy='strict-origin-when-cross-origin';iframe.addEventListener('load',()=>{if(panel.hidden)pause();});player.append(iframe);}
   panel.hidden=false;open.hidden=true;open.setAttribute('aria-expanded','true');close.focus({preventScroll:true});
  });
  close.addEventListener('click',()=>{
   pause();
   panel.hidden=true;open.hidden=false;open.setAttribute('aria-expanded','false');open.focus({preventScroll:true});
  });
 }
 function scan(){
  scheduled=false;if(!document.body?.dataset.page||document.body.dataset.teacher)return;
  const content=document.querySelector('.lesson-content');if(!content)return;
  content.querySelectorAll('iframe').forEach(frame=>{if(frame.closest('.learnvideo'))return;const node=placeholder(frame);if(node){frame.removeAttribute('src');frame.replaceWith(node);}});
  const config=window.SOZ_ACTIVE_CONFIG||window.SOZ_CONFIG||{};
  if(document.body.dataset.page==='index.html'&&videoURL(config.orientationVideoUrl)&&!content.querySelector('[data-learnvideo-src]')){
   const card=document.createElement('section');card.className='card learnvideo-card';const node=document.createElement('div');node.dataset.learnvideoSrc=config.orientationVideoUrl;node.dataset.learnvideoTitle='Lernvideo';card.append(node);
   const completion=content.querySelector('[data-orientation-completion]');if(completion)completion.before(card);else content.append(card);
  }
  content.querySelectorAll('[data-learnvideo-src]').forEach(createPreview);
 }
 function schedule(){if(!scheduled){scheduled=true;queueMicrotask(scan);}}
 window.SOZ_LEARNVIDEO={prepareHTML,scan,videoURL,previewImage};
 const data=window.SOZPAED;if(data?.pages){for(const key of Object.keys(data.pages))data.pages[key]=prepareHTML(data.pages[key]);}
 const config=window.SOZ_CONFIG;if(config?.overrides){for(const key of Object.keys(config.overrides))config.overrides[key]=prepareHTML(config.overrides[key]);}
 function init(){scan();new MutationObserver(schedule).observe(document.querySelector('.lesson-content')||document.body,{childList:true,subtree:true});}
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});else init();
})();
