"""Local UI budget and throttled Chromium checks; excludes real third-party media."""
import gzip,json,os
from pathlib import Path
from playwright.sync_api import sync_playwright
files=[Path('index.html'),Path('support.js'),Path('playback.js'),Path('assets/fonts.css'),*Path('assets/vendor').glob('*.js'),*Path('assets/fonts').glob('*.woff2')]
size=sum(len(p.read_bytes()) if p.suffix=='.woff2' else len(gzip.compress(p.read_bytes())) for p in files)
assert size<220*1024,size
print(f'UI payload budget: {size} bytes (gzip text + WOFF2; excludes logos/media)')
results=[]
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 for width,height,slow in [(390,844,True),(1440,900,False)]:
  page=browser.new_page(viewport={'width':width,'height':height},reduced_motion='reduce')
  page.route('https://**/*',lambda route:route.abort())
  page.add_init_script("""window.auditCLS=0;new PerformanceObserver(list=>{for(const e of list.getEntries())if(!e.hadRecentInput)window.auditCLS+=e.value}).observe({type:'layout-shift',buffered:true});""")
  if slow:
   cdp=page.context.new_cdp_session(page)
   cdp.send('Network.enable')
   cdp.send('Emulation.setCPUThrottlingRate',{'rate':4})
   cdp.send('Network.emulateNetworkConditions',{'offline':False,'latency':150,'downloadThroughput':200000,'uploadThroughput':90000})
  page.goto(os.environ.get('WFL_TEST_URL','http://127.0.0.1:8001'),wait_until='networkidle')
  page.evaluate('document.fonts.ready')
  page.wait_for_timeout(500)
  assert page.locator('h1').is_visible()
  assert page.locator('h1').evaluate('e=>getComputedStyle(e).animationName')=='none'
  assert page.evaluate('document.fonts.check("700 32px \'Space Grotesk\'")')
  metrics=page.evaluate("""({width:innerWidth,fcpMs:performance.getEntriesByName('first-contentful-paint')[0]?.startTime,domReadyMs:performance.getEntriesByType('navigation')[0].domContentLoadedEventEnd,cls:window.auditCLS,externalUI:performance.getEntriesByType('resource').filter(r=>/unpkg.com|fonts.googleapis.com|fonts.gstatic.com/.test(r.name)).map(r=>r.name)})""")
  assert metrics['externalUI']==[],metrics
  assert metrics['fcpMs'] and metrics['fcpMs']<5000,metrics
  assert metrics['cls']<.1,metrics
  results.append({'throttled':slow,**metrics})
  print(json.dumps(results[-1]))
  page.close()
 browser.close()
Path('/tmp/wfl-performance-results.json').write_text(json.dumps({'uiBudgetBytes':size,'measurements':results},indent=2))
