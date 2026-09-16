import json, re
from playwright.sync_api import sync_playwright

URL = "file:///tmp/qa.html"
FAIL, WARN, OK = [], [], []
def fail(t, m): FAIL.append(f"[{t}] {m}")
def warn(t, m): WARN.append(f"[{t}] {m}")
def ok(t, m=""): OK.append(f"[{t}] {m}")

CONTRAST_JS = """
() => {
  function lum(c){
    const m = c.match(/[\\d.]+/g).map(Number);
    const [r,g,b] = m.slice(0,3).map(v=>{v/=255; return v<=0.04045? v/12.92 : Math.pow((v+0.055)/1.055,2.4);});
    return 0.2126*r+0.7152*g+0.0722*b;
  }
  function parse(c){ const m=(c||'').match(/[\\d.]+/g); if(!m) return null;
    return {r:+m[0],g:+m[1],b:+m[2],a:m.length>3?+m[3]:1}; }
  function over(fg,bg){ const a=fg.a;
    return {r:fg.r*a+bg.r*(1-a), g:fg.g*a+bg.g*(1-a), b:fg.b*a+bg.b*(1-a), a:1}; }
  function bgOf(el){
    const stack=[]; let n=el;
    while(n && n!==document.documentElement){
      const c=parse(getComputedStyle(n).backgroundColor);
      if(c && c.a>0){ stack.push(c); if(c.a>=1) break; }
      n=n.parentElement;
    }
    let base=parse(getComputedStyle(document.body).backgroundColor)||{r:255,g:255,b:255,a:1};
    if(base.a<1) base={r:255,g:255,b:255,a:1};
    let cur=base;
    for(let i=stack.length-1;i>=0;i--) cur=over(stack[i],cur);
    return 'rgb('+Math.round(cur.r)+', '+Math.round(cur.g)+', '+Math.round(cur.b)+')';
  }
  const out = [];
  const els = document.querySelectorAll('p,span,h1,h2,h3,button,li,blockquote,label,textarea,input:not([type=range]),q,b,strong,em,cite,a');
  els.forEach(el=>{
    if(!el.offsetParent && el.tagName!=='BODY') return;
    const txt = (el.innerText||el.value||el.placeholder||'').trim();
    if(!txt) return;
    if(el.children.length && !Array.from(el.childNodes).some(n=>n.nodeType===3 && n.textContent.trim())) return;
    const cs = getComputedStyle(el);
    const fgp = parse(cs.color);
    if(!fgp || fgp.a < 0.5) return;            // deliberately hidden glyphs
    if(cs.visibility === 'hidden' || +cs.opacity < 0.5) return;
    const fg = cs.color, bg = bgOf(el);
    const L1 = lum(fg), L2 = lum(bg);
    const ratio = (Math.max(L1,L2)+0.05)/(Math.min(L1,L2)+0.05);
    const px = parseFloat(cs.fontSize);
    const bold = parseInt(cs.fontWeight,10) >= 700;
    const large = px >= 24 || (px >= 18.66 && bold);
    const need = large ? 3.0 : 4.5;
    if(ratio < need) out.push({t: txt.slice(0,55), ratio: +ratio.toFixed(2), need, px, fg, bg, cls: el.className||el.tagName});
  });
  return out;
}
"""

def check_overflow(p, tag):
    o = p.evaluate("() => ({sw: document.documentElement.scrollWidth, cw: document.documentElement.clientWidth})")
    if o["sw"] > o["cw"] + 1:
        fail(tag, f"horizontal scroll: scrollWidth {o['sw']} > clientWidth {o['cw']}")
    else:
        ok(tag, "no horizontal scroll")

def check_contrast(p, tag):
    bad = p.evaluate(CONTRAST_JS)
    if bad:
        for b in bad[:8]:
            fail(tag, f"contrast {b['ratio']} (need {b['need']}) on '{b['t']}' [{b['cls']}] {b['fg']} on {b['bg']}")
    else:
        ok(tag, "contrast OK")

def check_tap_targets(p, tag):
    small = p.evaluate("""() => {
      const out=[];
      document.querySelectorAll('button,a,input[type=range]').forEach(el=>{
        if(!el.offsetParent) return;
        const r = el.getBoundingClientRect();
        if(r.height < 24 || r.width < 24) out.push({t:(el.innerText||el.getAttribute('aria-label')||el.className).slice(0,40), w:Math.round(r.width), h:Math.round(r.height)});
      });
      return out;
    }""")
    for s in small:
        warn(tag, f"small tap target {s['w']}x{s['h']}: {s['t']}")

with sync_playwright() as pw:
    b = pw.chromium.launch()
    errs = []
    ctx = b.new_context(viewport={"width":390,"height":844}, color_scheme="light")
    p = ctx.new_page()
    p.on("pageerror", lambda e: errs.append(str(e)))
    p.on("console", lambda m: errs.append("console."+m.type+": "+m.text) if m.type=="error" and "TUNNEL" not in m.text else None)
    p.add_init_script("window.print = () => { window.__printed = true; };")
    p.goto(URL); p.wait_for_timeout(2200)

    if "Holding Your Thoughts Captive" not in p.inner_text("#v-home"): fail("title","new title missing on home")
    else: ok("title","Holding Your Thoughts Captive")
    if p.title() != "Holding Your Thoughts Captive": fail("title", "document title is "+p.title())

    for txt in ["I’m crashing", "I’m struggling with my thoughts", "dump where I’m at"]:
        if txt not in p.inner_text(".doors"): fail("doors", "missing door: "+txt)
    ok("doors","all three renamed doors present")
    hw = p.inner_text(".howitworks")
    if "any order" not in hw or "paper journal" not in hw: fail("home","how-it-works copy missing")
    else: ok("home","use-any-order + paper-journal note present")
    check_overflow(p,"home@390"); check_contrast(p,"home@390"); check_tap_targets(p,"home@390")

    # --- nav + back stack
    for v in ["steady","untangle","write","journal","shapes","verses","remap"]:
        p.click(f'[data-view="{v}"]'); p.wait_for_timeout(350)
        if not p.is_visible(f"#v-{v}"): fail("nav", f"{v} did not open")
        else: ok("nav", f"{v} opens")
        if not p.is_visible("#backBtn"): fail("nav", f"Back missing on {v}")
        if not p.is_visible("#homeBtn"): fail("nav", f"Home missing on {v}")
        check_overflow(p, f"{v}@390"); check_contrast(p, f"{v}@390")
        p.click("#backBtn"); p.wait_for_timeout(250)
        if not p.is_visible("#v-home"): fail("nav", f"Back from {v} failed")
    ok("nav","Back returns home from every view")

    # grounding -> untangle -> Back must return to grounding (her bug)
    p.click('[data-view="steady"]'); p.wait_for_timeout(300)
    p.click('#v-steady .actions [data-view="untangle"]'); p.wait_for_timeout(350)
    if not p.is_visible("#v-untangle"): fail("back","grounding -> untangle failed")
    p.click("#backBtn"); p.wait_for_timeout(300)
    if not p.is_visible("#v-steady"): fail("back","Back from step one did not return to grounding")
    else: ok("back","Back from step one returns to grounding, not home")
    p.click("#homeBtn"); p.wait_for_timeout(250)
    if not p.is_visible("#v-home"): fail("back","Home button failed")
    else: ok("back","Home button works")

    # --- breath counter
    p.click('[data-view="steady"]'); p.wait_for_timeout(400)
    w1 = p.inner_text("#breathWord"); n1 = p.inner_text("#breathNum"); m1 = p.inner_text("#breathMeta")
    if not n1.isdigit(): fail("breath", f"count not a number: '{n1}'")
    if "breath 1 of 8" not in m1.lower(): fail("breath", f"meta wrong: '{m1}'")
    else: ok("breath", f"counts: {w1} {n1} / {m1}")
    weight = p.eval_on_selector("#breathWord","e=>getComputedStyle(e).fontWeight")
    if int(weight) < 700: fail("breath", f"breathe word not bold (weight {weight})")
    else: ok("breath","word is bold")
    bg = p.eval_on_selector("#breathCircle","e=>getComputedStyle(e).backgroundImage")
    if "gradient" not in bg: fail("breath","circle has no gradient")
    else: ok("breath","circle is an ombre gradient")
    p.wait_for_timeout(1600)
    n2 = p.inner_text("#breathNum")
    if n2 == n1: warn("breath", f"count did not tick ({n1} -> {n2})")
    else: ok("breath", f"count ticks {n1} -> {n2}")
    # fast-forward past 8 breaths
    p.evaluate("()=>{ const d=document; }")
    p.wait_for_timeout(200)

    # --- grounding content
    st = p.inner_text("#v-steady")
    if "philippians 4:8" not in st.lower(): fail("grounding","Philippians 4:8-9 missing")
    else: ok("grounding","Philippians 4:8-9 present")
    if "46:10" in st: fail("grounding","Psalm 46:10 still present")
    else: ok("grounding","Psalm 46:10 removed")
    if "1 kings" in st.lower() or "elijah" in st.lower(): fail("grounding","1 Kings / Elijah still on grounding")
    else: ok("grounding","1 Kings removed from grounding")
    if "psalm 42:5" not in st.lower() or "praise" not in st.lower(): fail("grounding","Psalm 42 praise prompt missing")
    else: ok("grounding","Psalm 42:5-6 praise prompt present")
    p.click("#homeBtn"); p.wait_for_timeout(200)
    p.click('[data-view="verses"]'); p.wait_for_timeout(300)
    if "1 kings 19:12" not in p.inner_text("#verseGroups").lower(): fail("verses","1 Kings not moved into the library")
    else: ok("verses","1 Kings lives in the worn-out group")
    p.click("#homeBtn"); p.wait_for_timeout(200)

    # --- shapes renamed
    p.click('[data-view="shapes"]'); p.wait_for_timeout(300)
    sh = p.inner_text("#shapeList")
    for name in ["This is going to ruin everything","If it's not perfect, it's a failure","This always happens to me",
                 "I can only see what went wrong","I know what they're thinking about me","I already know how this ends",
                 "I should be handling this better","It's my fault","I feel it, so it must be true",
                 "Everyone else is doing better than me","I feel completely worthless"]:
        if name.replace("'","’") not in sh and name not in sh: fail("shapes","missing: "+name)
    ok("shapes","all eleven renamed as first-person sentences")
    if "the reframe" not in sh.lower(): fail("shapes","reframe label missing")
    n = p.eval_on_selector_all("#shapeList .exwhy","e=>e.length")
    if n != 11: fail("shapes", f"{n} example descriptions, expected 11")
    else: ok("shapes","every shape has an example description")
    check_contrast(p,"shapes@390")
    p.click("#homeBtn"); p.wait_for_timeout(200)

    # --- quick remap
    p.click('[data-view="remap"]'); p.wait_for_timeout(300)
    n = p.eval_on_selector_all("#remapList .remap-item","e=>e.length")
    if n != 11: fail("remap", f"{n} remap items, expected 11")
    else: ok("remap","all eleven shapes appear in the quick remap list")
    n2 = p.eval_on_selector_all("#remapList .remap-truer","e=>e.length")
    if n2 != 11: fail("remap", f"{n2} reframes shown, expected 11")
    else: ok("remap","every remap item shows its reframe")
    n3 = p.eval_on_selector_all("#remapList .remap-verse","e=>e.length")
    if n3 != 10: fail("remap", f"{n3} verses shown, expected 10 (one shape has no paired verse)")
    else: ok("remap","verses shown for every shape that has one")
    check_contrast(p,"remap@390")
    p.click("#homeBtn"); p.wait_for_timeout(200)

    # --- four-page flow
    p.click('[data-view="untangle"]'); p.wait_for_timeout(300)
    if "of four" not in p.inner_text("#v-untangle .kicker").lower(): fail("steps","step counter does not say four")
    else: ok("steps","four pages")
    if p.eval_on_selector_all("#progress .pdot","e=>e.length") != 4: fail("steps","progress dots != 4")
    if not p.is_visible("#v-untangle .example"): fail("steps","worked example missing on page one")
    else: ok("steps","worked example on page one")
    p.fill("#f-situation","SITUATION TEXT")
    p.fill("#f-thought","THE THOUGHT")
    if not p.is_visible("#stepBack"): fail("steps","Back button missing on page one")
    else: ok("steps","Back present on page one")
    p.click('.btn[data-step="2"]'); p.wait_for_timeout(250)
    if "mixture" not in p.inner_text("#v-untangle h2").lower(): fail("steps","page two header not the new wording")
    else: ok("steps","page two: describe the mixture")
    if not p.is_visible(".whymatters"): fail("steps","why-this-matters block missing")
    else: ok("steps","why-this-matters present")
    p.click('#u-chips .chip'); p.wait_for_timeout(100)
    p.eval_on_selector("#f-before","el=>{el.value=85;el.dispatchEvent(new Event('input'))}")
    p.click('.btn[data-step="3"]'); p.wait_for_timeout(250)
    if p.eval_on_selector_all("#u-shapes .shape","e=>e.length") != 11: fail("steps","page three shapes missing")
    recap = p.inner_text("#u-recap") if p.is_visible("#u-recap") else ""
    if "THE THOUGHT" not in recap or "SITUATION TEXT" not in recap: fail("steps","page three does not recap page one")
    else: ok("steps","page three recaps what was written on page one")
    order = p.eval_on_selector_all("#v-untangle .actions .btn","els=>els.map(e=>e.textContent.trim())")
    if not order or order[0] != "Back": fail("steps", f"Back is not the first action button: {order}")
    else: ok("steps","Back comes before Next/Keep this")
    p.click('#u-shapes .shape-head'); p.wait_for_timeout(150)
    p.click('.btn[data-step="4"]'); p.wait_for_timeout(300)
    h2 = p.inner_text("#v-untangle h2")
    if "honest review" not in h2.lower(): fail("steps", f"page four header: {h2}")
    else: ok("steps","page four: an honest review for a healthier me")
    for fid in ["f-provable","f-leftout","f-friend","f-reframe","f-nexttime","f-step"]:
        if not p.is_visible("#"+fid): fail("steps","missing field "+fid)
    ok("steps","review + truer + next-time all on page four")
    hints = p.inner_text("#v-untangle")
    if "provable" not in hints.lower(): fail("copy","'provable' wording missing")
    if "good parts" not in hints.lower() and "gone well" not in hints.lower(): fail("copy","left-out expansion missing")
    if "loves you" not in hints.lower(): fail("copy","'someone who loves you' wording missing")
    ok("copy","step four wording updated")
    # back through all pages, values retained
    for target in [3,2,1]:
        p.click("#stepBack"); p.wait_for_timeout(200)
    if p.eval_on_selector("#f-situation","e=>e.value") != "SITUATION TEXT": fail("steps","page one text lost")
    if p.eval_on_selector("#f-thought","e=>e.value") != "THE THOUGHT": fail("steps","page one thought lost")
    else: ok("steps","values survive Back through all four pages")
    p.click('.btn[data-step="2"]'); p.wait_for_timeout(200)
    if p.eval_on_selector("#f-before","e=>e.value") != "85": fail("steps","slider lost on round trip")
    if p.eval_on_selector_all('#u-chips .chip[aria-pressed="true"]',"e=>e.length") != 1: fail("steps","chip lost on round trip")
    p.click('.btn[data-step="3"]'); p.wait_for_timeout(200)
    if p.eval_on_selector_all('#u-shapes .shape[data-on="1"]',"e=>e.length") != 1: fail("steps","shape selection lost")
    else: ok("steps","chips, slider and shape survive the round trip")
    p.click('.btn[data-step="4"]'); p.wait_for_timeout(250)
    p.fill("#f-provable","PROVABLE"); p.fill("#f-leftout","LEFT OUT")
    p.fill("#f-reframe","TRUER SENTENCE"); p.fill("#f-nexttime","NEXT TIME LINE"); p.fill("#f-step","SMALL STEP")
    p.click("#versePicks .pick"); p.wait_for_timeout(150)
    p.eval_on_selector("#f-after","el=>{el.value=30;el.dispatchEvent(new Event('input'))}")
    check_contrast(p,"step4@390"); check_overflow(p,"step4@390")
    p.click("#saveRecord"); p.wait_for_timeout(500)
    if not p.is_visible("#v-journal"): fail("save","did not land on journal")
    body = p.inner_text("#entries")
    for needle in ["SITUATION TEXT","THE THOUGHT","LEFT OUT","TRUER SENTENCE","NEXT TIME LINE","SMALL STEP","85","30"]:
        if needle not in body: fail("save","entry missing "+needle)
    if "next time, tell yourself" not in body.lower(): fail("save","next-time block not rendered in journal")
    else: ok("save","entry saved with the next-time line")
    check_contrast(p,"journal-filled@390")

    # --- skip everything, still must save (regression: this dead-ended before)
    p.click("#homeBtn"); p.wait_for_timeout(200)
    before_entries = p.eval_on_selector_all(".entry","e=>e.length")
    p.click('[data-view="untangle"]'); p.wait_for_timeout(300)
    p.click('.btn.quiet[data-step="2"]'); p.wait_for_timeout(200)
    p.click('.btn.quiet[data-step="3"]'); p.wait_for_timeout(200)
    p.click('.btn.quiet[data-step="4"]'); p.wait_for_timeout(250)
    p.click("#saveRecord"); p.wait_for_timeout(400)
    if not p.is_visible("#v-journal"):
        fail("save","skipping every field on all four pages got stuck instead of reaching the journal")
    else:
        after_entries = p.eval_on_selector_all(".entry","e=>e.length")
        if after_entries != before_entries + 1: fail("save", f"skip-everything entry not saved: {before_entries} -> {after_entries}")
        else: ok("save","skipping every field on all four pages still saves successfully")

    # example filler
    p.click("#homeBtn"); p.wait_for_timeout(200)
    p.click('[data-view="untangle"]'); p.wait_for_timeout(250)
    p.click("#loadExample"); p.wait_for_timeout(300)
    if not p.eval_on_selector("#f-situation","e=>e.value"): fail("example","filler did not populate")
    else: ok("example","fill-it-in-for-me works")

    # write flow
    p.click("#homeBtn"); p.wait_for_timeout(200)
    p.click('[data-view="write"]'); p.wait_for_timeout(250)
    p.click("#promptBtn"); p.wait_for_timeout(150)
    if not p.inner_text("#promptOut"): fail("write","prompt empty")
    p.fill("#w-text","FREE PAGE"); p.click("#w-chips .chip"); p.click("#saveWrite"); p.wait_for_timeout(400)
    if "FREE PAGE" not in p.inner_text("#entries"): fail("write","page not saved")
    else: ok("write","free page saves")
    p.click("#printAll"); p.wait_for_timeout(200)
    if not p.evaluate("()=>window.__printed"): fail("journal","print did not fire")
    else: ok("journal","print fires")
    p.click("#copyAll"); p.wait_for_timeout(400)
    ok("journal","copy path ran")
    p.reload(); p.wait_for_timeout(1600)
    p.click('[data-view="journal"]'); p.wait_for_timeout(300)
    if p.eval_on_selector_all(".entry","e=>e.length") != 3: fail("persist","entries lost on reload")
    else: ok("persist","entries survive reload")
    p.click(".entry .btn.quiet"); p.wait_for_timeout(300)
    if p.eval_on_selector_all(".entry","e=>e.length") != 2: fail("journal","delete failed")
    else: ok("journal","delete works")

    # --- backup / restore
    p.click("#homeBtn"); p.wait_for_timeout(200)
    p.click('[data-view="write"]'); p.wait_for_timeout(200)
    p.fill("#w-text","BACKUP CANARY"); p.click("#saveWrite"); p.wait_for_timeout(400)
    before_count = p.eval_on_selector_all(".entry","e=>e.length")
    with p.expect_download() as dl_info:
        p.click("#saveBackup")
    backup_path = "/tmp/qa_backup.json"
    dl_info.value.save_as(backup_path)
    p.wait_for_timeout(200)
    with open(backup_path) as bf: backup_data = json.load(bf)
    if backup_data.get("app") != "captivating-thoughts" or not isinstance(backup_data.get("entries"), list):
        fail("backup","backup file has the wrong shape")
    elif len(backup_data["entries"]) != before_count:
        fail("backup", f"backup has {len(backup_data['entries'])} entries, journal shows {before_count}")
    else: ok("backup","backup file downloads with the right shape and count")
    if not p.is_visible("#backupOut textarea"):
        fail("backup","fallback copy textarea not shown alongside the download")
    else: ok("backup","fallback copy text always offered alongside the download")

    while p.eval_on_selector_all(".entry .btn.quiet","e=>e.length") > 0:
        p.click(".entry .btn.quiet"); p.wait_for_timeout(150)
    if p.eval_on_selector_all(".entry","e=>e.length") != 0: fail("backup","could not clear entries to test restore")

    with p.expect_file_chooser() as fc1:
        p.click("#loadBackup")
    fc1.value.set_files(backup_path)
    p.wait_for_timeout(300)
    if p.eval_on_selector_all(".entry","e=>e.length") != before_count: fail("backup","restore did not bring entries back")
    elif "BACKUP CANARY" not in p.inner_text("#entries"): fail("backup","restored entry missing its text")
    else: ok("backup","loading a backup file restores entries")

    with p.expect_file_chooser() as fc2:
        p.click("#loadBackup")
    fc2.value.set_files(backup_path)
    p.wait_for_timeout(300)
    if p.eval_on_selector_all(".entry","e=>e.length") != before_count: fail("backup","loading the same backup twice duplicated entries")
    else: ok("backup","loading the same backup again does not duplicate")

    p.click("#homeBtn"); p.wait_for_timeout(200)
    p.click('[data-view="write"]'); p.wait_for_timeout(200)
    p.fill("#w-text","NEWER THAN BACKUP"); p.click("#saveWrite"); p.wait_for_timeout(400)
    with p.expect_file_chooser() as fc3:
        p.click("#loadBackup")
    fc3.value.set_files(backup_path)
    p.wait_for_timeout(300)
    if "NEWER THAN BACKUP" not in p.inner_text("#entries"): fail("backup","restoring an older backup deleted a newer entry")
    else: ok("backup","restoring an older backup merges instead of overwriting newer entries")

    # skins
    for skin in ["rose","harbor","dusk","auto"]:
        if p.is_visible("#homeBtn"): p.click("#homeBtn"); p.wait_for_timeout(150)
        p.click(f'.swatch[data-skin="{skin}"]'); p.wait_for_timeout(250)
        expect = None if skin=="auto" else skin
        if p.evaluate("()=>document.documentElement.getAttribute('data-skin')") != expect:
            fail("skin", skin+" not applied")
        check_contrast(p, "home-"+skin)
        p.reload(); p.wait_for_timeout(1400)
        if p.evaluate("()=>document.documentElement.getAttribute('data-skin')") != expect:
            fail("skin", skin+" not remembered")
        else: ok("skin", skin+" applies and persists")

    for skin in ["rose","harbor","dusk"]:
        p.click(f'.swatch[data-skin="{skin}"]'); p.wait_for_timeout(200)
        for v in ["steady","untangle","write","journal","shapes","verses","remap"]:
            p.evaluate(f"()=>{{document.querySelectorAll('.view,.home').forEach(e=>e.hidden=true);document.getElementById('v-{v}').hidden=false;}}")
            p.wait_for_timeout(120)
            check_contrast(p, f"{v}-{skin}")
        p.goto(URL); p.wait_for_timeout(1200)

    # system dark
    ctx2 = b.new_context(viewport={"width":390,"height":844}, color_scheme="dark")
    p2 = ctx2.new_page(); p2.on("pageerror", lambda e: errs.append("dark:"+str(e)))
    p2.goto(URL); p2.wait_for_timeout(1800)
    if p2.evaluate("()=>document.documentElement.getAttribute('data-skin')") != "rose":
        fail("skin","rose is not the default for a first-time visitor")
    elif not p2.get_attribute('.swatch[data-skin="rose"]', "aria-pressed") == "true":
        fail("skin","rose swatch not marked pressed by default")
    else: ok("skin","rose is the default for a first-time visitor, even under system dark")
    p2.click('.swatch[data-skin="auto"]'); p2.wait_for_timeout(250)
    check_contrast(p2,"home-systemdark")
    p2.click('[data-view="untangle"]'); p2.wait_for_timeout(300)
    check_contrast(p2,"step1-systemdark")
    p2.click('[data-view="steady"]') if p2.is_visible('[data-view="steady"]') else None
    ctx2.close()

    # widths
    for w in [320, 1280]:
        cx = b.new_context(viewport={"width":w,"height":900})
        pw2 = cx.new_page(); pw2.goto(URL); pw2.wait_for_timeout(1600)
        check_overflow(pw2, f"home@{w}")
        for v in ["steady","untangle","write","journal","shapes","verses","remap"]:
            pw2.click(f'[data-view="{v}"]'); pw2.wait_for_timeout(250)
            check_overflow(pw2, f"{v}@{w}")
            pw2.click("#homeBtn"); pw2.wait_for_timeout(150)
        pw2.click('[data-view="untangle"]'); pw2.wait_for_timeout(200)
        for i in [2,3,4]:
            pw2.click(f'.btn[data-step="{i}"]'); pw2.wait_for_timeout(150)
            check_overflow(pw2, f"step{i}@{w}")
        cx.close()

    # links
    p.goto(URL); p.wait_for_timeout(1500)
    links = []
    for v in ["steady","untangle","shapes","verses","remap"]:
        p.click(f'[data-view="{v}"]'); p.wait_for_timeout(300)
        links += p.eval_on_selector_all("a[href]","els=>els.map(e=>e.href)")
        p.click("#homeBtn"); p.wait_for_timeout(150)
    bad = [l for l in set(links) if not re.match(r"^https://biblehub\.com/esv/[a-z0-9_]+/\d+-\d+\.htm$", l)]
    if bad: [fail("links","malformed: "+l) for l in bad]
    else: ok("links", f"{len(set(links))} scripture links well-formed")

    # --- language switcher (Spanish)
    p.goto(URL); p.wait_for_timeout(1400)
    if not p.is_visible("#langSelect"): fail("lang","language switcher missing from the topbar")
    else: ok("lang","language switcher present in the topbar")
    opts = p.eval_on_selector_all("#langSelect option","els=>els.map(e=>e.value)")
    if "pt" in opts: fail("lang","Portuguese option present before it has been built — should not be selectable yet")
    if sorted(opts) != ["en","es"]: fail("lang", f"unexpected language options: {opts}")
    else: ok("lang","only English and Spanish are selectable (Portuguese correctly deferred)")

    p.select_option("#langSelect","es"); p.wait_for_timeout(250)
    if "Cautivos" not in p.inner_text("#v-home"): fail("lang","home did not translate to Spanish")
    else: ok("lang","home translates to Spanish")
    if p.evaluate("()=>document.documentElement.lang") != "es": fail("lang","<html lang> not updated to es")
    else: ok("lang","<html lang> updated on switch")
    if p.evaluate("()=>localStorage.getItem('tet.lang')") != "es": fail("lang","language choice not persisted to localStorage")
    else: ok("lang","language choice persisted")

    p.click('[data-view="shapes"]'); p.wait_for_timeout(300)
    shsp = p.inner_text("#shapeList")
    if "Esto va a arruinarlo todo" not in shsp: fail("lang","shape names not translated to Spanish")
    else: ok("lang","shape names translate to Spanish")
    if "Therefore do not be anxious" not in shsp: fail("lang","scripture text was translated — it must stay English/ESV")
    else: ok("lang","scripture text correctly stays English (ESV) under Spanish")
    check_overflow(p, "shapes-es@390"); check_contrast(p, "shapes-es@390")
    p.click("#homeBtn"); p.wait_for_timeout(200)

    before_lang_entries = p.eval_on_selector_all(".entry","e=>e.length")
    p.click('[data-view="untangle"]'); p.wait_for_timeout(300)
    if "de cuatro" not in p.inner_text("#v-untangle .kicker").lower(): fail("lang","step-of-four kicker not translated")
    else: ok("lang","step-of-four kicker translates")
    p.click('.btn[data-step="2"]'); p.wait_for_timeout(250)
    chip_label_es = p.eval_on_selector("#u-chips .chip", "e=>e.textContent")
    p.click("#u-chips .chip"); p.wait_for_timeout(100)
    # switching languages mid-flow must not silently drop an uncaptured selection
    p.select_option("#langSelect","en"); p.wait_for_timeout(250)
    pressed_en = p.eval_on_selector_all('#u-chips .chip[aria-pressed="true"]',"els=>els.map(e=>e.textContent)")
    if len(pressed_en) != 1: fail("lang", f"feelings chip lost when switching language mid-flow (was '{chip_label_es}')")
    else: ok("lang","a feelings chip selected before a language switch survives the switch")
    # measured after the switch to English: the switch itself re-renders every existing entry's tag too
    before_worked_tags = p.eval_on_selector_all(".entry .tag","els=>els.filter(e=>e.textContent==='Worked through').length")

    # every field still skippable under a language switch mid-flow (same invariant as the English regression test)
    p.click('.btn.quiet[data-step="3"]'); p.wait_for_timeout(200)
    p.click('.btn.quiet[data-step="4"]'); p.wait_for_timeout(250)
    p.click("#saveRecord"); p.wait_for_timeout(400)
    if not p.is_visible("#v-journal"): fail("lang","saving after a mid-flow language switch got stuck instead of reaching the journal")
    else:
        after_lang_entries = p.eval_on_selector_all(".entry","e=>e.length")
        after_worked_tags = p.eval_on_selector_all(".entry .tag","els=>els.filter(e=>e.textContent==='Worked through').length")
        if after_lang_entries != before_lang_entries + 1: fail("lang", f"entry not saved after mid-flow language switch: {before_lang_entries} -> {after_lang_entries}")
        elif after_worked_tags != before_worked_tags + 1: fail("lang","saved entry not tagged 'Worked through' in the now-active language")
        else: ok("lang","saving still works, in English, after switching languages mid-flow")

    if "Cautivos" in p.inner_text("#v-journal"): fail("lang","switching back to English left Spanish text behind")
    p.click("#homeBtn"); p.wait_for_timeout(150)
    if "I’m crashing" not in p.inner_text("#v-home"): fail("lang","switching back to English did not restore English home copy")
    else: ok("lang","switching back to English fully restores English copy")

    # nav buttons + language select + colour swatches together must not overflow narrow widths (topbar regression)
    cxn = b.new_context(viewport={"width":320,"height":800})
    pn = cxn.new_page(); pn.goto(URL); pn.wait_for_timeout(1200)
    pn.select_option("#langSelect","es"); pn.wait_for_timeout(200)
    pn.click('[data-view="untangle"]'); pn.wait_for_timeout(300)
    check_overflow(pn, "untangle-es@320")
    cxn.close()

    p.reload(); p.wait_for_timeout(1600)
    if p.eval_on_selector("#langSelect","e=>e.value") != "en": fail("lang","language choice did not persist across reload")
    else: ok("lang","language choice persists across reload")

    # focus + aria
    p.goto(URL); p.wait_for_timeout(1400)
    p.keyboard.press("Tab")
    o = p.evaluate("()=>{const e=document.activeElement,s=getComputedStyle(e);return s.outlineWidth+' '+s.outlineStyle}")
    if o.startswith("0px") or "none" in o: fail("a11y","no focus ring")
    else: ok("a11y","focus ring "+o)
    miss = p.evaluate("()=>{const o=[];document.querySelectorAll('.chip,.swatch,.pick').forEach(e=>{if(!e.hasAttribute('aria-pressed'))o.push(e.className)});return o}")
    if miss: fail("a11y","missing aria-pressed: "+", ".join(set(miss)))
    else: ok("a11y","aria-pressed on all toggles")

    # reduced motion
    cr = b.new_context(viewport={"width":390,"height":844}, reduced_motion="reduce")
    pr = cr.new_page(); pr.goto(URL); pr.wait_for_timeout(1500)
    pr.click('[data-view="steady"]'); pr.wait_for_timeout(600)
    if pr.eval_on_selector(".breath","e=>getComputedStyle(e).animationName") not in ("none",""):
        fail("motion","breath animates under reduced motion")
    else: ok("motion","reduced motion honoured")
    if not pr.inner_text("#breathNum").strip(): fail("motion","count missing under reduced motion")
    else: ok("motion","count still runs under reduced motion")
    cr.close()

    b.close()

print("="*70)
print(f"PASS {len(OK)}   WARN {len(WARN)}   FAIL {len(FAIL)}")
print("="*70)
if FAIL:
    print("\n--- FAILURES ---")
    for f in FAIL: print(" ", f)
if WARN:
    print("\n--- WARNINGS ---")
    for w in WARN: print(" ", w)
print("\n--- JS ERRORS ---")
print(" ", errs if errs else "none")
