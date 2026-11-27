"""Add safe legacy SCORM resume support to one generated BFSdual package, in place."""
from pathlib import Path
import re
import shutil
import xml.etree.ElementTree as ET

HERE=Path(__file__).resolve().parent


def replace_once(src,old,new):
    if src.count(old)!=1:
        raise ValueError('Unerwartete Runtime-Struktur: '+old[:90])
    return src.replace(old,new)


def common_runtime(src):
    if 'BFS_RESUME.lesson(' in src: return src
    start=src.index('  function parseState(raw) {')
    stop=src.index('  function findAPI(start) {',start)
    src=src[:start]+'''  function parseState(raw) {
    return window.BFS_RESUME.lesson(raw, fresh(), window.GB_REQUIREMENTS || {}, checkCount, safePage);
  }
'''+src[stop:]
    src=replace_once(src,"    let error = '';","    let error = '';\n    let practiceMessage = '';")
    src=replace_once(src,"        state = parseState(get('cmi.suspend_data'));", """        readOnly = ['review', 'browse'].includes(get('cmi.core.lesson_mode'));
        const saved = get('cmi.suspend_data');
        state = parseState(saved);""")
    src=replace_once(src,"        if (bookmark) state.page = safePage(bookmark);", """        if (bookmark && safePage(bookmark) === bookmark) state.page = bookmark;
        else if (validPages.has(bookmark)) state.page = bookmark+'.html';""")
    src=replace_once(src,"        readOnly = ['review', 'browse'].includes(get('cmi.core.lesson_mode'));\n        dirty = !state.completed && !readOnly;", """        // Merely viewing an older compatible attempt need not rewrite its stored bytes.
        if (saved) sent = JSON.stringify(state);
        dirty = !saved && !state.completed && !readOnly;""")
    src=replace_once(src,"      readOnly = true;\n      error = cause.message || 'Der gespeicherte Lernstand ist nicht verfügbar.';", """      if (cause instanceof window.BFS_RESUME.StateIssue) {
        practiceMessage = window.BFS_RESUME.practiceNotice(cause, Boolean(api));
      } else {
        readOnly = true;
        error = 'Der Lernstand ist nicht verfügbar. Öffne die Moodle-Aktivität erneut.';
      }""")
    src=replace_once(src,"      if (!dirty || finished || readOnly) return !error;", """      if (!dirty || finished || readOnly) return !error;
      if (practiceMessage) {
        dirty = false;
        notify();
        return true;
      }""")
    src=replace_once(src,"      get error() { return error; },", "      get error() { return error || practiceMessage; },")
    src=replace_once(src,"        if (error) return error;", "        if (error || practiceMessage) return error || practiceMessage;")
    return src


def office_runtime(src,package_id):
    if 'BFS_RESUME.office(' in src:return src
    marker="const storage='global-bike-buero-v1'"
    src=replace_once(src,marker,"let practiceMessage='';\nconst officeId='"+package_id+"';\nstate.id=officeId;state.version=1;\n"+marker)
    start=src.index('try{api=window.BFS_EDITOR?.preview')
    stop=src.index('function save(){',start)
    src=src[:start]+'''try {
  api=window.BFS_EDITOR?.preview ? null : (find(window)||find(window.opener));
  if(api){
    active=String(api.LMSInitialize('')).toLowerCase()==='true';
    if(!active) throw Error('Moodle-Verbindung nicht verfügbar.');
    const get=key=>{
      const value=api.LMSGetValue(key);
      if(typeof api.LMSGetLastError==='function' && String(api.LMSGetLastError())!=='0') throw Error('Lernstand nicht verfügbar.');
      return String(value ?? '');
    };
    readonly=['browse','review'].includes(get('cmi.core.lesson_mode'));
    state=window.BFS_RESUME.office(get('cmi.suspend_data'),state,officeId,ids);
    if(['completed','passed'].includes(get('cmi.core.lesson_status')))state.done=true;
    if(!readonly&&!state.done)set('cmi.core.lesson_status','incomplete');
  }else{
    state=window.BFS_RESUME.office(localStorage.getItem(storage),state,officeId,ids);
  }
}catch(cause){
  if(cause instanceof window.BFS_RESUME.StateIssue)practiceMessage=window.BFS_RESUME.practiceNotice(cause,Boolean(api));
  else {readonly=true;practiceMessage='Der gespeicherte Lernstand ist nicht verfügbar. Öffne die Moodle-Aktivität erneut.';}
}
'''+src[stop:]
    src=replace_once(src,"if(readonly)return;try{if(active)","if(readonly||practiceMessage)return;try{if(active)")
    src=replace_once(src,"$('#status').textContent=active?'Moodle-Verbindung aktiv.': 'Lokale Vorschau: Fortschritt wird nur in diesem Browser gespeichert.';", "$('#status').textContent=practiceMessage || (active?'Moodle-Verbindung aktiv.':'Lokale Vorschau: Fortschritt wird nur in diesem Browser gespeichert.');")
    src=replace_once(src,"if(active&&!location.hash){", "if(active&&!practiceMessage&&!location.hash){")
    return src


def apply(folder):
    folder=Path(folder)
    manifest=folder/'imsmanifest.xml'
    xml=manifest.read_text(encoding='utf-8')
    package_id=ET.fromstring(xml).get('identifier')
    ordinary=(folder/'assets/runtime.js').is_file()
    if not ordinary and package_id!='BFS_GLOBAL_BIKE_BUERO_SCORM12':
        raise ValueError(f'Kein unterstütztes BFSdual-Paket im Ordner {folder}')
    runtime=folder/('assets/runtime.js' if ordinary else 'app.js')
    old=runtime.read_text(encoding='utf-8')
    new=common_runtime(old) if ordinary else office_runtime(old,package_id)
    files={runtime:new}
    pattern=re.compile(r'''<script\b[^>]*\bsrc\s*=\s*(["'])(?P<prefix>(?:\.\./)*)(?:assets/runtime\.js|app\.js)(?:\?[^"']*)?\1[^>]*>\s*</script>''',re.I)
    for page in folder.rglob('*.html'):
        source=page.read_text(encoding='utf-8')
        if 'assets/bfs-resume.js' in source or not pattern.search(source):continue
        def inject(m):
            base=m['prefix']+'assets/'
            return f'<script defer src="{base}pako.min.js"></script><script defer src="{base}bfs-resume.js"></script>'+m.group(0)
        files[page]=pattern.sub(inject,source)
    vendor=[('pako.min.js',HERE/'vendor/pako.min.js'),('pako-LICENSE.txt',HERE/'vendor/pako-LICENSE.txt'),('bfs-resume.js',HERE/'bfs-resume.js')]
    included={e.attrib['href'] for e in ET.fromstring(xml).findall('.//{*}file')}
    missing=[f'assets/{name}' for name,_ in vendor if f'assets/{name}' not in included]
    if missing:
        pattern_xml=re.compile(r'^(\s*)</resource>',re.M)
        if len(pattern_xml.findall(xml))!=1:raise ValueError('Eine SCORM-Startressource ist erforderlich.')
        xml=pattern_xml.sub(lambda m:''.join(m[1]+'  <file href="'+file+'" />\n' for file in missing)+m[0],xml)
        ET.fromstring(xml);files[manifest]=xml
    for path,content in files.items():
        if path.read_text(encoding='utf-8')!=content:path.write_text(content,encoding='utf-8')
    for name,source in vendor:
        destination=folder/'assets'/name
        if not destination.exists() or destination.read_bytes()!=source.read_bytes():shutil.copyfile(source,destination)
    return package_id

if __name__=='__main__':
    import sys
    for folder in sys.argv[1:]:print(apply(folder))
