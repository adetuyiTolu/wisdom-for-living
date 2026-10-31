import subprocess,json,re,pathlib,tempfile
import argparse
parser=argparse.ArgumentParser(description='Normalize and verify final intro film masters.')
parser.add_argument('--builders-master')
parser.add_argument('--books-master')
args=parser.parse_args()
root=pathlib.Path(__file__).resolve().parents[1]
for name,dest in [('builders','the-builders-intro'),('books','books-coming-soon')]:
 src=getattr(args,name+'_master')
 if not src: continue
 result=subprocess.run(['ffmpeg','-hide_banner','-i',src,'-af','loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True,check=True)
 raw=re.findall(r'\{\s*"input_i".*?\}',result.stderr,re.S)[-1];stats=json.loads(raw)
 filt='loudnorm=I=-16:TP=-1.5:LRA=11:linear=true:'+':'.join(f'{key}={stats[value]}' for key,value in [('measured_I','input_i'),('measured_TP','input_tp'),('measured_LRA','input_lra'),('measured_thresh','input_thresh'),('offset','target_offset')])
 output=root/'videos'/f'{dest}.mp4'
 subprocess.run(['ffmpeg','-y','-v','error','-i',src,'-t','30','-c:v','copy','-af',filt,'-c:a','aac','-b:a','192k','-ar','48000','-movflags','+faststart',str(output)],check=True)
 result=subprocess.run(['ffmpeg','-hide_banner','-i',str(output),'-af','loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True,check=True)
 measured=json.loads(re.findall(r'\{\s*"input_i".*?\}',result.stderr,re.S)[-1])
 probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration,size:stream=codec_name,width,height,r_frame_rate','-of','json',str(output)]))
 if abs(float(measured['input_i'])+16)>=.5:
  # Dynamic mixes can need another pass after AAC encoding. Measure the actual
  # delivered file rather than trusting the first filter's prediction.
  with tempfile.NamedTemporaryFile(suffix='.mp4') as temp:
   subprocess.run(['ffmpeg','-y','-v','error','-i',str(output),'-t','30','-c:v','copy','-af','loudnorm=I=-16:TP=-1.5:LRA=9','-c:a','aac','-b:a','192k','-ar','48000','-movflags','+faststart',temp.name],check=True)
   output.write_bytes(pathlib.Path(temp.name).read_bytes())
  result=subprocess.run(['ffmpeg','-hide_banner','-i',str(output),'-af','loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True,check=True)
  measured=json.loads(re.findall(r'\{\s*"input_i".*?\}',result.stderr,re.S)[-1])
  probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration,size:stream=codec_name,width,height,r_frame_rate','-of','json',str(output)]))
 assert abs(float(probe['format']['duration'])-30)<.1,probe
 assert float(measured['input_tp'])<=-1,measured
 assert abs(float(measured['input_i'])+16)<.5,measured
 (root/'video-projects'/('the-builders' if name=='builders' else 'books')/'DELIVERY.json').write_text(json.dumps({'media':dest+'.mp4','probe':probe,'audio_measured':measured,'audio_note':'Measured with FFmpeg; not listened to by the agent.'},indent=2)+'\n')
 print(name,probe['format'],measured['input_i']+' LUFS',measured['input_tp']+' dBTP')
 for t in [0,6,14,20,27]:
  subprocess.run(['ffmpeg','-y','-v','error','-ss',str(t),'-i',str(output),'-frames:v','1',f'/tmp/{name}-decoded-{t}.jpg'],check=True)
 subprocess.run(['ffmpeg','-y','-v','error','-ss','2','-i',str(output),'-frames:v','1',str(root/'videos'/f'{dest}-poster.jpg')],check=True)
