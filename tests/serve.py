"""Local static preview with byte ranges, matching production video delivery."""
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
class Handler(SimpleHTTPRequestHandler):
 def send_head(self):
  path=Path(self.translate_path(self.path))
  if path.is_file() and 'Range' in self.headers:
   total=path.stat().st_size
   start,end=self.headers['Range'].removeprefix('bytes=').split('-',1)
   start=int(start or 0);end=min(int(end) if end else total-1,total-1)
   self.send_response(206)
   self.send_header('Content-Type',self.guess_type(str(path)))
   self.send_header('Accept-Ranges','bytes')
   self.send_header('Content-Range',f'bytes {start}-{end}/{total}')
   self.send_header('Content-Length',str(end-start+1));self.end_headers()
   self.range_left=end-start+1
   file=path.open('rb');file.seek(start);return file
  return super().send_head()
 def copyfile(self,source,output):
  if not hasattr(self,'range_left'):return super().copyfile(source,output)
  while self.range_left>0:
   data=source.read(min(65536,self.range_left))
   if not data:break
   output.write(data);self.range_left-=len(data)
ThreadingHTTPServer(('0.0.0.0',8001),Handler).serve_forever()
