import sys, json, subprocess, numpy as np, onnxruntime as ort, base64
sys.argv=[sys.argv[0]]+sys.argv[1:]
from whisper_onnx import mel_filters, log_mel, SR, HOP, N_FRAMES
md=sys.argv[1].rstrip('/'); name=md.split('/')[-1].replace('sherpa-onnx-whisper-','')
so=ort.SessionOptions(); so.intra_op_num_threads=2; so.enable_cpu_mem_arena=False
so.graph_optimization_level=ort.GraphOptimizationLevel.ORT_ENABLE_BASIC
enc=ort.InferenceSession(f'{md}/{name}-encoder.int8.onnx',so,providers=['CPUExecutionProvider'])
dec=ort.InferenceSession(f'{md}/{name}-decoder.int8.onnx',so,providers=['CPUExecutionProvider'])
meta=enc.get_modelmeta().custom_metadata_map
n_mels=int(meta['n_mels']); L=int(meta['n_text_layer']); C=int(meta['n_text_ctx']); S=int(meta['n_text_state'])
sot=int(meta['sot']); eot=int(meta['eot']); tr=int(meta['transcribe']); nots=int(meta['no_timestamps'])
langs=dict(zip(meta['all_language_codes'].split(','),map(int,meta['all_language_tokens'].split(','))))
vocab={}
for line in open(f'{md}/{name}-tokens.txt',encoding='utf-8'):
    p=line.rstrip('\n').split(' ')
    if len(p)==2: vocab[int(p[1])]=base64.b64decode(p[0])
audio=np.frombuffer(subprocess.run(['ffmpeg','-v','error','-i','audio16.wav','-f','s16le','-'],capture_output=True).stdout,np.int16).astype(np.float32)/32768
filt=mel_filters(n_mels)
isl=json.loads(sys.argv[2])
res=[]
for s,e in isl:
    a=audio[int(max(0,s-0.25)*SR):int((e+0.3)*SR)]
    mel=log_mel(a,n_mels,filt)[:, :N_FRAMES]
    ck,cv=enc.run(None,{'mel':mel[None]})
    k=np.zeros((L,1,C,S),np.float32); v=np.zeros_like(k)
    toks=np.array([[sot,langs['ar'],tr,nots]],np.int64); off=np.zeros(1,np.int64); out=[]
    for i in range(80):
        lg,k,v=dec.run(None,{'tokens':toks,'in_n_layer_self_k_cache':k,'in_n_layer_self_v_cache':v,'n_layer_cross_k':ck,'n_layer_cross_v':cv,'offset':off})
        off=off+toks.shape[1]; l=lg[0,-1].copy(); l[eot+1:]=-np.inf
        if i==0: l[eot]=-np.inf; l[220]=-np.inf
        t=int(l.argmax())
        if t==eot: break
        out.append(t); toks=np.array([[t]],np.int64)
    txt=b''.join(vocab.get(t,b'') for t in out).decode('utf-8','ignore').strip()
    print(f'{s:6.2f}-{e:6.2f} {txt}',flush=True); res.append({'s':s,'e':e,'text':txt})
json.dump(res,open(sys.argv[3],'w'),ensure_ascii=False,indent=1)
