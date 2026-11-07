"""ReelStudio IA v2: local, single-worker video editor API."""
import json, os, re, shutil, subprocess, threading, uuid, queue, time
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

ROOT=Path(__file__).resolve().parent
os.environ["PATH"]="/opt/homebrew/bin:/usr/local/bin:"+os.environ.get("PATH","")
HOME=ROOT/"work_jobs"; JOBS=HOME/"jobs"; INBOX=HOME/"inbox"
for p in (JOBS,INBOX):p.mkdir(parents=True,exist_ok=True)
app=FastAPI(title="ReelStudio IA",version="2.0.0")
app.add_middleware(CORSMiddleware,allow_origins=["http://127.0.0.1:8765","http://localhost:8765","http://127.0.0.1:8787","http://localhost:8787","*"],allow_methods=["*"],allow_headers=["*"])
Q=queue.Queue(); active={}; lock=threading.RLock(); running={}
FORMATS={"9:16":(1080,1920,"9x16"),"4:5":(1080,1350,"4x5"),"1:1":(1080,1080,"1x1")}
EXT={".mp4":"video",".mov":"video",".webm":"video",".mkv":"video",".jpg":"image",".jpeg":"image",".png":"image",".mp3":"audio",".wav":"audio",".m4a":"audio"}

def ff(args, timeout=1200, proc_register=None):
    p=subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    if proc_register:proc_register(p)
    try:out,err=p.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:p.kill();p.communicate();raise RuntimeError("Tiempo límite de render excedido")
    if p.returncode:raise RuntimeError(err[-1600:] or "FFmpeg falló")
    return out

def data_path(id):return JOBS/id/"job.json"
def save(d):
    with lock:
        target=data_path(d['job_id']);tmp=target.with_suffix('.tmp');tmp.write_text(json.dumps(d,ensure_ascii=False,indent=2));tmp.replace(target)
def get(id):
    p=data_path(id)
    if not re.fullmatch(r'[a-f0-9]{32}',id) or not p.exists():raise HTTPException(404,"Trabajo no encontrado")
    return json.loads(p.read_text())
def process(id):
    d=get(id); d['status']='processing';d['progress']=5;save(d)
    try:
        root=JOBS/id; inputs=d['inputs']; videos=[x for x in inputs if x['type'] in ('video','image')]
        if not videos:raise ValueError('Incluye al menos un video o imagen')
        durations=[]
        for x in videos:
            if x['type']=='image':durations.append(3.0)
            else:
                v=subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(root/'input'/x['filename'])],capture_output=True,text=True)
                if v.returncode:raise ValueError('Video ilegible: '+x['filename'])
                durations.append(float(v.stdout.strip()))
        maxlen=max(1,min(180,float(d.get('duration_seconds') or 30)))
        # Clamp clip lengths while keeping both input order and room for transitions.
        each=min(15,maxlen/len(videos));lens=[min(v,each) for v in durations]
        style=d.get('edit',{}).get('style','corporativo'); transition={'dinamico':0.22,'comercial':0.3,'cinematografico':0.55,'corporativo':0.35}.get(style,.3)
        transition=min(transition,min(lens)*.15) if len(lens)>1 else 0
        edl={'version':1,'style':style,'clips':[{'source':v['filename'],'seconds':round(t,3)} for v,t in zip(videos,lens)],'transition':{'type':'fade','seconds':round(transition,3)}}
        output=root/'output'/f"v{d['version']}";output.mkdir(parents=True,exist_ok=True)
        (output/'edl.json').write_text(json.dumps(edl,indent=2,ensure_ascii=False))
        d['progress']=12;save(d)
        for i,(fmt,(w,h,suffix)) in enumerate(FORMATS.items()):
            if fmt not in d['outputs']:continue
            temp=root/'work'/suffix;temp.mkdir(parents=True,exist_ok=True)
            prepared=[]
            for n,(x,sec) in enumerate(zip(videos,lens)):
                src=root/'input'/x['filename'];dst=temp/f'{n:03d}.mp4'
                vf=f'scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:black,setsar=1,fps=30,format=yuv420p'
                cmd=['ffmpeg','-y','-hide_banner','-loglevel','error']
                if x['type']=='image':cmd+=['-loop','1','-framerate','30','-i',str(src),'-t',str(sec)]
                else:cmd+=['-i',str(src),'-t',str(sec)]
                cmd+=['-vf',vf,'-an','-c:v','libx264','-preset','ultrafast','-crf','25',str(dst)]
                ff(cmd,proc_register=lambda p: running.__setitem__(id,p));prepared.append(dst)
            target=output/f'reel_{suffix}.mp4'
            if len(prepared)==1:shutil.copy2(prepared[0],target)
            else:
                # Dissolves on video only; 1 source stream per segment.
                graph=[];running_time=lens[0]
                for n in range(1,len(prepared)):
                    left='[0:v]' if n==1 else f'[v{n-1}]'; right=f'[{n}:v]'
                    graph.append(f'{left}{right}xfade=transition=fade:duration={transition:.3f}:offset={max(0,running_time-transition):.3f}[v{n}]')
                    running_time+=lens[n]-transition
                cmd=['ffmpeg','-y','-hide_banner','-loglevel','error']
                for path in prepared:cmd+=['-i',str(path)]
                cmd+=['-filter_complex',';'.join(graph),'-map',f'[v{len(prepared)-1}]','-an','-c:v','libx264','-preset','ultrafast','-crf','25','-movflags','+faststart',str(target)]
                ff(cmd,proc_register=lambda p: running.__setitem__(id,p))
            d['progress']=min(95,d['progress']+int(80/len(d['outputs'])));save(d)
        d['status']='ready_for_review';d['progress']=100
        (output/'report.json').write_text(json.dumps({'note':'Edición de clips con disolvencias; no hay IA semántica ni subtítulos automáticos en esta versión.','edl':edl},ensure_ascii=False,indent=2))
        save(d)
    except Exception as e:d['status']='failed' if d.get('status')!='cancelled' else 'cancelled';d['error']=str(e);save(d)
    finally:running.pop(id,None)

def worker():
    while True:
        id=Q.get()
        try:
            if get(id)['status']=='queued':process(id)
        finally:Q.task_done()
threading.Thread(target=worker,daemon=True).start()

@app.get('/')
def index():return FileResponse(ROOT/'static'/'index.html')
@app.get('/health')
def health():return {'version':'2.0.0','ffmpeg_available':bool(shutil.which('ffmpeg')),'ffprobe_available':bool(shutil.which('ffprobe')),'subtitles_model_loaded':False,'features':['multiclip','fade_transitions','three_formats','persistent_queue','revisions']}
@app.get('/presets')
def presets():return [p.stem for p in (ROOT/'presets').glob('*.json')]
@app.post('/jobs')
async def create_job(files:list[UploadFile]=File(...),brief:str=Form(''),duration_seconds:float=Form(30),style:str=Form('corporativo'),outputs:str=Form('9:16,4:5,1:1'),client_id:str=Form('general'),campaign_id:str=Form('general')):
    if not re.fullmatch(r'[\w-]{1,64}',client_id) or not re.fullmatch(r'[\w-]{1,64}',campaign_id):raise HTTPException(400,'Identificador de cliente/campaña inválido')
    if style not in ('comercial','corporativo','cinematografico','dinamico'):raise HTTPException(400,'Estilo no válido')
    out=[x.strip() for x in outputs.split(',') if x.strip()]
    if not out or any(x not in FORMATS for x in out):raise HTTPException(400,'Formato no válido')
    if len(files)>20:raise HTTPException(400,'Máximo 20 archivos')
    id=uuid.uuid4().hex;root=JOBS/id
    for dirname in ('input','work','output'): (root/dirname).mkdir(parents=True)
    inp=[]
    try:
        for i,f in enumerate(files):
            ext=Path(f.filename or '').suffix.lower()
            if ext not in EXT:raise ValueError('Formato no permitido: '+ext)
            filename=f'{i:03d}{ext}';dst=root/'input'/filename
            size=0
            with dst.open('wb') as dest:
                while chunk:=await f.read(1024*1024):
                    size+=len(chunk)
                    if size>350*1024*1024:raise ValueError('Máximo 350 MB por archivo')
                    dest.write(chunk)
            inp.append({'filename':filename,'original_name':Path(f.filename or '').name,'type':EXT[ext]})
        d={'job_id':id,'status':'queued','progress':0,'version':1,'error':None,'client_id':client_id,'campaign_id':campaign_id,'brief':brief[:2000],'duration_seconds':max(1,min(duration_seconds,180)),'edit':{'style':style},'outputs':list(dict.fromkeys(out)),'inputs':inp}
        save(d);Q.put(id);return d
    except Exception as e:shutil.rmtree(root,ignore_errors=True);raise HTTPException(400,str(e))
@app.get('/jobs/{job_id}')
def status(job_id:str):return get(job_id)
@app.get('/jobs/{job_id}/outputs')
def outputs(job_id:str):
    d=get(job_id);p=JOBS/job_id/'output'/f"v{d['version']}"
    return {'job_id':job_id,'status':d['status'],'files':[{'name':f.name,'url':f'/jobs/{job_id}/files/{f.name}'} for f in p.glob('*') if f.is_file()] if p.exists() else []}
@app.get('/jobs/{job_id}/files/{filename}')
def download(job_id:str,filename:str):
    d=get(job_id)
    if not re.fullmatch(r'[\w.-]+',filename):raise HTTPException(400,'Nombre inválido')
    p=JOBS/job_id/'output'/f"v{d['version']}"/filename
    if not p.is_file():raise HTTPException(404,'Archivo no encontrado')
    return FileResponse(p,filename=filename)
@app.post('/jobs/{job_id}/revisions')
def revise(job_id:str, notes:dict):
    d=get(job_id)
    if d['status'] not in ('ready_for_review','failed'):raise HTTPException(409,'Trabajo no disponible para revisión')
    d['version']+=1;d['brief']=(d['brief']+'\nRevisión: '+str(notes.get('notes',''))[:1000])[:2000]
    if notes.get('style') in ('comercial','corporativo','cinematografico','dinamico'):d['edit']['style']=notes['style']
    d.update(status='queued',progress=0,error=None);save(d);Q.put(job_id);return d
@app.post('/jobs/{job_id}/cancel')
def cancel(job_id:str):
    d=get(job_id)
    if d['status'] in ('queued','processing'):
        d['status']='cancelled';save(d)
        p=running.get(job_id)
        if p:p.terminate()
    return d
