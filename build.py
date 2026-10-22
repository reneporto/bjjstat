"""Static site builder for bjjstat.com. Run: python3 build.py  (outputs into ./docs, served by GitHub Pages)"""
import os, shutil, html, json, datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, 'docs')
DOMAIN = 'https://bjjstat.com'
IG = 'https://www.instagram.com/bjj.stat/'
LOGO = '<svg viewBox="0 0 100 100" aria-hidden="true"><rect x="8" y="56" width="20" height="36" rx="10" fill="#FF2E88"/><rect x="38" y="32" width="20" height="60" rx="10" fill="#FF2E88"/><circle cx="78" cy="18" r="11" fill="#19E3B1"/></svg>'
e = html.escape

# ---------------------------------------------------------------- helpers
def bars(title, sub, rows, unit='', src='', maxv=None, dec=False):
    """rows: (label, value, small, cls)  cls in '', 'hl', 'v', 's'"""
    maxv = maxv or max(r[1] for r in rows)
    out = [f'<figure class="chart"><div class="ct">{title}</div>' + (f'<div class="cs">{sub}</div>' if sub else '') + '<div class="bars">']
    for lab, v, small, cls in rows:
        w = max(2, v / maxv * 100)
        val = (f'{v:.2f}' if dec else (f'{v:g}')) + unit
        out.append(f'<div class="br"><div class="lb">{lab}' + (f'<small>{small}</small>' if small else '') +
                   f'</div><div class="tr"><div class="bar {cls}" style="width:{w:.1f}%"></div><div class="v">{val}</div></div></div>')
    out.append('</div>' + (f'<figcaption class="src">{src}</figcaption>' if src else '') + '</figure>')
    return ''.join(out)

def video(slug, label):
    return (f'<div class="media"><video controls playsinline muted preload="none" poster="/assets/media/{slug}.webp" '
            f'width="1080" height="1350" aria-label="{e(label)}"><source src="/assets/media/{slug}.mp4" type="video/mp4"></video></div>')

def slides(prefix, n, label):
    items = ''.join(f'<a href="/assets/media/{prefix}-{i:02d}.webp" aria-label="{e(label)} slide {i}"><img src="/assets/media/{prefix}-{i:02d}.webp" alt="{e(label)}, slide {i} of {n}" width="1080" height="1350" loading="lazy"></a>' for i in range(1, n + 1))
    return f'<div class="slides">{items}</div>'

# ---------------------------------------------------------------- events data
EVENTS = [
    ('OCT', '24', 'ADCC Poland Open', 'Nowa Iwiczna, Poland', 'ADCC', False, False),
    ('OCT', '27', 'IBJJF Rome Open', 'Rome, Italy', 'IBJJF', False, False),
    ('OCT–NOV', '28–1', 'IBJJF European No-Gi Championship', 'Lido di Ostia, Italy', 'IBJJF', False, False),
    ('OCT', '31', 'ISBJJA World Cup', 'Cascais, Portugal', 'ISBJJA', True, False),
    ('NOV', '7–8', 'FPJJB Nacional Open 2026', 'Odivelas, Portugal', 'FPJJB', True, False),
    ('NOV', '28', 'ISBJJA EuroCup', 'Coimbra, Portugal', 'ISBJJA', True, False),
    ('NOV', '28–29', 'IBJJF Paris Fall Open', 'Paris, France', 'IBJJF', False, False),
    ('NOV', '29', 'ADCC France Paris Open', 'Clamart, France', 'ADCC', False, False),
    ('DEC', '5', 'ADCC Polish Cup', 'Warsaw, Poland', 'ADCC', False, False),
    ('DEC', '5–6', 'IBJJF Dublin Fall Open', 'Dublin, Ireland', 'IBJJF', False, False),
    ('JAN 2027', '13–23', 'IBJJF European Championship 2027', 'Odivelas, Portugal · registration closes Jan 3', 'IBJJF', True, True),
]
def ev_html(rows):
    return ''.join(f'<div class="ev{" hl" if hl else ""}"><div class="d"><div class="m">{m}</div><div class="dd">{d}</div></div>'
                   f'<div><div class="nm">{e(n)}</div><div class="ct">{e(c)}</div></div><div class="org">{o}</div></div>'
                   for m, d, n, c, o, pt, hl in rows)

# ---------------------------------------------------------------- posts
POSTS = []
def post(**k): POSTS.append(k)

post(slug='alliance-athletes-per-academy', date='2026-10-22', series='Nacional Open 2026', img='alliance-per-academy',
     title='54 athletes, one academy: Alliance leads the Nacional Open per location',
     dek='Gracie Barra brings the most athletes. But divide by academies and Alliance’s single Lisbon gym comes out on top.',
     body=f'''
<div class="big-stat"><div class="n">54</div><div class="t">registrations from a single Alliance academy in Lisbon.</div></div>
<p>The IBJJF list for the <strong>Nacional Open Portugal 2026</strong> shows Alliance under five names (Parque das Nações, SP, Portugal, International, Porto Alegre). They all train at the same Lisbon academy, so we count them as one. That makes Alliance the <strong>4th team by registrations</strong> and the <strong>#1 team per academy</strong>.</p>
{bars('Athletes per academy', 'Teams with 20+ registrations · registrations ÷ academy entries on the IBJJF list', [
  ('Alliance', 54, '54 ÷ 1', 'hl'), ('Marcão Artsuave', 37, '37 ÷ 1', ''), ('Fight Nation Portugal', 33, '33 ÷ 1', ''),
  ('Five Elements', 25, '25 ÷ 1', ''), ('Brazilian Power Team', 24.3, '73 ÷ 3', ''), ('Focus Jiu-Jitsu', 17.8, '71 ÷ 4', ''),
  ('Icon JJ Team', 15.5, '31 ÷ 2', ''), ('Família André Marola', 15, '30 ÷ 2', ''), ('GF Team', 10.3, '31 ÷ 3', ''), ('Gracie Barra', 8.5, '178 ÷ 21', '')],
  src='Source: IBJJF athletes list by academy, Oct 22, 2026 19:50.')}
<h2>From outside the top 10 to #4</h2>
<p>At the 2025 Nacional Open, Alliance won <strong>16 medals (6 gold)</strong> and did not make the team top 10. One year later, only Gracie Barra, Brazilian Power Team and Focus have more athletes registered.</p>
<div class="callout">2025 is measured in medals and 2026 in registrations, so this is a signal of growth, not a like-for-like result. We will compare medals after Nov 7–8.</div>
<h2>Adults, masters and new blood</h2>
{bars('Alliance vs event average', 'Share of registrations', [
  ('Masters (30+) · Alliance', 41, '22 of 54', 'hl'), ('Masters (30+) · event', 33, '335 of 1,007', 's'),
  ('Adults · Alliance', 28, '15 of 54', 'hl'), ('Adults · event', 23, '227 of 1,007', 's'),
  ('White belts · Alliance', 31, '17 of 54', 'hl'), ('White belts · event', 25, '254 of 1,007', 's')], unit='%', maxv=45)}
<p>Alliance is lighter on kids: 26% of its registrations, against 37% across the event.</p>
<h2>Watch the motion graphic</h2>
{video('alliance-per-academy', 'Alliance athletes per academy motion graphic')}
''', sources=[('IBJJF · Nacional Open Portugal 2026 athletes list', 'https://ibjjf.com/events/3423/athletes-list-by-academy-teams'), ('IBJJF · Nacional Open Portugal 2025 results', 'https://ibjjf.com/events/2989/results')])

post(slug='nacional-open-2026-registrations', date='2026-10-22', series='Nacional Open 2026', img='nacional-teams',
     title='Nacional Open 2026: 1,007 athletes, 100 teams and a Gracie Barra wall',
     dek='We grouped every branch on the IBJJF list. One team brings more athletes than the next two combined.',
     body=f'''
<div class="big-stat"><div class="n">1,007</div><div class="t">registrations, 148 team entries, 100 teams once branches are grouped.</div></div>
{bars('Most registrations by team', 'Branches of the same team grouped', [
  ('Gracie Barra', 178, '21 branches', 'hl'), ('Brazilian Power Team', 73, '3 entries', ''), ('Focus Jiu-Jitsu', 71, '4 entries', ''),
  ('Alliance', 54, '1 academy', ''), ('Marcão Artsuave', 37, '', ''), ('Fight Nation Portugal', 33, '', ''), ('GF Team', 31, '3 entries', ''),
  ('Icon JJ Team', 31, '2 entries', ''), ('Família André Marola', 30, '2 entries', ''), ('2 Brothers BFC', 27, '5 entries', '')],
  src='Source: IBJJF athletes list by academy, Oct 22, 2026 19:50.')}
<h2>More than #2 and #3 combined</h2>
<p>Gracie Barra’s 178 registrations beat Brazilian Power Team and Focus together (144). Its five biggest branches are Montijo (27), Cascais (26), Paço de Arcos (25), Belas (24) and Carnaxide e Queijas (18). Counted one entry at a time, the biggest single school is <strong>Brazilian Power Team with 69</strong>, followed by Focus Jiu-Jitsu with 66.</p>
<h2>Who’s on the mats</h2>
{bars('Registrations by age group', '', [('Kids (4–15)', 368, '37%', 'hl'), ('Masters (30+)', 335, '33%', ''), ('Adults', 227, '23%', 'v'), ('Juvenile (16–17)', 77, '8%', 's')])}
<ul><li><strong>1 in 4</strong> registrations are women (256).</li><li>White belts outnumber black belts about <strong>3 to 1</strong> (254 vs 85).</li>
<li><strong>216 of 455</strong> divisions have only one athlete so far. The busiest is white belt, adult male, feather, with 15.</li></ul>
<div class="callout">Registrations are still open, so these numbers will move. In 2025 only 14% of divisions ended with a single athlete.</div>
{video('nacional-teams', 'Nacional Open 2026 teams motion graphic')}
''', sources=[('IBJJF · Nacional Open Portugal 2026 athletes list', 'https://ibjjf.com/events/3423/athletes-list-by-academy-teams')])

post(slug='upcoming-events-portugal-europe', date='2026-10-22', series='Calendar', img='portugal-events',
     title='Save the dates: the big Jiu-Jitsu events until the Euro',
     dek='Four events in Portugal and nine across Europe between now and the IBJJF European Championship in Odivelas.',
     body=f'''
<p>The road to the <strong>IBJJF European Championship 2027</strong> (Jan 13–23, Pavilhão Multiusos de Odivelas) runs through Rome, Paris, Dublin, Poland and three stops in Portugal. The full list lives on our <a href="/events/">events page</a>.</p>
<h2>Portugal</h2>{video('portugal-events', 'Portugal events motion graphic')}
<h2>Europe</h2>{video('europe-events', 'Europe events motion graphic')}
<div class="callout">Dates checked on the organisers’ official pages on Oct 22, 2026. Always confirm with the organiser before booking travel.</div>
''', sources=[('IBJJF events', 'https://ibjjf.com/events'), ('ADCC events', 'https://adcombat.com/'), ('FPJJB calendar', 'https://www.fpjjb.com/calendario'), ('ISBJJA', 'https://isbjja.com/')])

post(slug='lisbon-open-2026-teammates-final', date='2026-10-22', series='Lisbon Open 2026', img='teammates-final',
     title='Teammates in the final: 9 gi finals were decided inside the same team',
     dek='At the Lisbon Open, gold and silver went to the same academy in nine gi divisions.',
     body=f'''
<div class="big-stat"><div class="n">9</div><div class="t">gi finals with gold and silver from the same team.</div></div>
{bars('Same-team finals by team', 'Gi divisions where gold and silver came from the same academy', [('Gracie Barra', 3, '', 'hl'), ('Focus Jiu-Jitsu', 2, '', ''), ('CheckMat', 1, '', ''), ('Sigma Jiu-Jitsu', 1, '', ''), ('Duna Jiu-Jitsu', 1, '', ''), ('Brazilian Power Team', 1, '', '')], src='Source: IBJJF official results, Lisbon International Open 2026 (gi).')}
{video('teammates-final', 'Teammates in the final motion graphic')}
''', sources=[('IBJJF results', 'https://ibjjf.com/events')])

post(slug='lisbon-open-2026-perfect-weekend', date='2026-10-22', series='Lisbon Open 2026', img='bjjstat-perfect-weekend-01',
     title='The perfect weekend: three athletes won every gold they could',
     dek='Weight and open class, gi and no-gi. 4 golds out of 4, and all three compete in Master 3.',
     body=f'''
<div class="big-stat"><div class="n">4/4</div><div class="t">golds for three athletes at the Lisbon Open 2026.</div></div>
<p>Of the <strong>559</strong> athletes who reached a podium, <strong>25</strong> took home four medals and only <strong>3</strong> made all four of them gold: Rebeca Cifrian Montoya (VA Jiu-Jitsu Luxembourg), Leigh Snowden (Lucio Sergio BJJ Lifestyle) and Anca Cublesan (Brazilian Power Team International).</p>
<p>Three different teams, two brown belts and one black belt, 12 golds between them. Every perfect weekend came from the Master 3 (41+) division.</p>
{slides('bjjstat-perfect-weekend', 5, 'The perfect weekend')}
''', sources=[('IBJJF results', 'https://ibjjf.com/events')])

post(slug='lisbon-open-2026-medals-per-athlete', date='2026-10-22', series='Lisbon Open 2026', img='bjjstat-medals-per-athlete-01',
     title='Medals per athlete: the most efficient team in Lisbon wasn’t the biggest',
     dek='Bigger teams win more medals. So we divided by the athletes each team put on the podium.',
     body=f'''
<div class="big-stat"><div class="n">2.30</div><div class="t">medals per athlete for VA Jiu-Jitsu Luxembourg (23 ÷ 10).</div></div>
{bars('Medals per athlete', 'Gi + no-gi · teams with 4+ athletes on the podium', [
  ('VA Jiu-Jitsu Luxembourg', 2.30, '23 medals · 10 athletes', 'hl'), ('Cleyton Bastos Team', 2.25, '', ''), ('Âmbar Peposo Team', 2.20, '', ''),
  ('Brazilian Power Team', 2.00, '', ''), ('GF Team', 2.00, '', ''), ('ZR Team Association', 1.78, '', ''), ('Art of Roll', 1.75, '', ''),
  ('CheckMat', 1.64, '', ''), ('Blvckout Grappling HQ', 1.57, '', ''), ('Carlson Gracie Team', 1.56, '', ''), ('Gracie Barra (reference)', 1.36, '90 medals · 66 athletes', 's')],
  dec=True, src='Weight and open class both count. Source: IBJJF official results.')}
<p>Counting only golds, VA Luxembourg still leads with <strong>1.40 golds per athlete</strong> (14 golds, 10 athletes), ahead of Cleyton Bastos Team (1.25) and Brazilian Power Team (1.21).</p>
{slides('bjjstat-medals-per-athlete', 5, 'Medals per athlete')}
''', sources=[('IBJJF results', 'https://ibjjf.com/events')])

post(slug='lisbon-open-2026-nogi-medal-table', date='2026-10-22', series='Lisbon Open 2026', img='bjjstat-nogi-medal-table-01',
     title='No-gi medal table: CheckMat on top with 12 golds from 16 medals',
     dek='Take off the gi and the table changes. Same weekend, two different leaderboards.',
     body=f'''
{bars('No-gi medals · top 10', '', [('CheckMat', 16, '12 golds', 'hl'), ('Gracie Barra', 14, '', ''), ('VA Jiu-Jitsu Luxembourg', 11, '', ''), ('Brazilian Power Team', 8, '', ''), ('Mathias Ribeiro Team', 7, '', ''), ('Team Gil Catarino', 6, '', ''), ('Carlson Gracie Team', 6, '', ''), ('ECJJA', 6, '', ''), ('ZR Team Association', 4, '', ''), ('Academie Caio Terra', 4, '', '')], src='Source: IBJJF official results, Lisbon International Open 2026 (no-gi).')}
<p>Gracie Barra won <strong>35 golds in the gi</strong> but just <strong>4 in no-gi</strong>. VA Jiu-Jitsu Luxembourg won twice as many no-gi golds (8). Mathias Ribeiro Team jumped from #27 in the gi to #5 in no-gi.</p>
{slides('bjjstat-nogi-medal-table', 5, 'No-gi medal table')}
''', sources=[('IBJJF results', 'https://ibjjf.com/events')])

post(slug='lisbon-open-2026-gi-medal-table', date='2026-10-22', series='Lisbon Open 2026', img='bjjstat-gi-medal-table-01',
     title='Gi medal table: Gracie Barra won twice as many medals as anyone else',
     dek='614 gi medals, 157 academies. 76 went to one team.',
     body=f'''
{bars('Gi medals · top 10', '', [('Gracie Barra', 76, '35 golds', 'hl'), ('CheckMat', 38, '', ''), ('Focus Jiu-Jitsu', 36, '', ''), ('Alliance', 22, '', ''), ('Carlson Gracie Team', 22, '', ''), ('Brazilian Power Team', 20, '', ''), ('Team Gil Catarino', 20, '', ''), ('Nova União', 13, '', ''), ('VA Jiu-Jitsu Luxembourg', 12, '', ''), ('ZR Team Association', 12, '', '')], src='Source: IBJJF official results, Lisbon International Open 2026 (gi).')}
<p>Gracie Barra’s <strong>35 golds</strong> were more than CheckMat (14) and Focus (13) combined. The best conversion rate belonged to Alliance: <strong>59% of its medals were gold</strong> (13 of 22).</p>
{bars('Gold rate · top 7 teams', 'Share of each team’s gi medals that were gold', [('Alliance', 59, '13 of 22', 'hl'), ('Brazilian Power Team', 55, '11 of 20', ''), ('Gracie Barra', 46, '35 of 76', ''), ('Carlson Gracie Team', 41, '9 of 22', ''), ('Team Gil Catarino', 40, '8 of 20', ''), ('CheckMat', 37, '14 of 38', ''), ('Focus Jiu-Jitsu', 36, '13 of 36', '')], unit='%', maxv=60)}
{slides('bjjstat-gi-medal-table', 5, 'Gi medal table')}
''', sources=[('IBJJF results', 'https://ibjjf.com/events')])

post(slug='lisbon-open-2026-in-numbers', date='2026-10-22', series='Lisbon Open 2026', img='bjjstat-lisbon-open-01',
     title='Lisbon Open 2026 in numbers: 843 medals, 559 athletes, 185 academies',
     dek='The gi took almost 3 of every 4 medals, masters took 58% of the gi podiums and blue was the busiest belt.',
     body=f'''
<div class="big-stat"><div class="n mag">843</div><div class="t">medals across 348 divisions (614 gi, 229 no-gi).</div></div>
{bars('Gi vs no-gi', '', [('Medals · gi', 614, '', ''), ('Medals · no-gi', 229, '', 'hl'), ('Athletes on the podium · gi', 486, '', ''), ('Athletes on the podium · no-gi', 162, '', 'hl'), ('Academies with a medal · gi', 157, '', ''), ('Academies with a medal · no-gi', 92, '', 'hl')])}
{bars('How many medals each athlete took home', '559 athletes on the podium', [('1 medal', 349, '', ''), ('2 medals', 161, '', ''), ('3 medals', 24, '', ''), ('4 medals', 25, '', 'hl')])}
<p><strong>89</strong> athletes won a medal in both gi and no-gi. In the gi, <strong>58% of medals went to masters</strong> (356 of 614), and blue was the busiest belt with 174 medals.</p>
{bars('Most medals · gi + no-gi', '', [('Gracie Barra', 90, '', 'hl'), ('CheckMat', 54, '', ''), ('Focus Jiu-Jitsu', 36, '', ''), ('Brazilian Power Team', 28, '', ''), ('Carlson Gracie Team', 28, '', '')], src='Source: IBJJF official results, Lisbon International Open 2026, Oct 9–10.')}
{slides('bjjstat-lisbon-open', 6, 'Lisbon Open in numbers')}
''', sources=[('IBJJF results', 'https://ibjjf.com/events')])

# ---------------------------------------------------------------- layout
def fmt_date(d):
    return datetime.date.fromisoformat(d).strftime('%b %-d, %Y')

def page(path, title, desc, body, nav='', og_img='/assets/img/og.png', article=None):
    canon = DOMAIN + path
    ld = ''
    if article:
        ld = '<script type="application/ld+json">' + json.dumps({"@context": "https://schema.org", "@type": "BlogPosting", "headline": article['title'],
              "datePublished": article['date'], "image": DOMAIN + f"/assets/media/{article['img']}.webp", "author": {"@type": "Organization", "name": "bjj.stat"},
              "publisher": {"@type": "Organization", "name": "bjj.stat"}, "mainEntityOfPage": canon}) + '</script>'
    def cur(k): return ' aria-current="page"' if nav == k else ''
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{canon}">
<meta name="theme-color" content="#0A0A0F">
<meta property="og:type" content="{'article' if article else 'website'}">
<meta property="og:site_name" content="bjj.stat">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{DOMAIN}{og_img}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/assets/img/apple-touch-icon.png">
<link rel="preload" href="/assets/fonts/SpaceGrotesk.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/css/style.css">
{ld}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site-head"><div class="wrap">
  <a class="brand" href="/" aria-label="bjj.stat home">{LOGO}<span>bjj<span class="dot">.</span>stat</span></a>
  <nav class="nav" aria-label="Main"><a href="/blog/"{cur('blog')}>Stats</a><a href="/events/"{cur('events')}>Events</a><a href="/about/"{cur('about')}>About</a><a class="btn" href="{IG}" rel="me noopener" target="_blank">Follow</a></nav>
</div></header>
<main id="main">
{body}
</main>
<footer class="site-foot"><div class="wrap">
  <div><a class="brand" href="/" style="font-size:20px">{LOGO}<span>bjj<span class="dot">.</span>stat</span></a><div style="margin-top:8px">Jiu-Jitsu by the numbers. Data from official results.</div></div>
  <nav aria-label="Footer"><a href="/blog/">Stats</a><a href="/events/">Events</a><a href="/about/">About</a><a href="{IG}" rel="me noopener" target="_blank">Instagram</a></nav>
  <div>© 2026 bjj.stat</div>
</div></footer>
</body>
</html>'''

def card(p, feature=False):
    return (f'<a class="pcard{" feature" if feature else ""}" href="/blog/{p["slug"]}/"><img src="/assets/media/{p["img"]}.webp" alt="" width="1080" height="1350" loading="lazy">'
            f'<div class="b"><div class="tag mag">{e(p["series"])} · {fmt_date(p["date"])}</div><h3>{e(p["title"])}</h3><p>{e(p["dek"])}</p></div></a>')

def write(rel, s):
    path = os.path.join(OUT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, 'w').write(s)

def build():
    shutil.rmtree(OUT, ignore_errors=True)
    shutil.copytree(os.path.join(ROOT, 'assets'), os.path.join(OUT, 'assets'))
    for f in os.listdir(os.path.join(ROOT, 'static')):
        shutil.copy(os.path.join(ROOT, 'static', f), OUT)
    posts = list(POSTS)

    # home
    home = f'''
<section class="hero"><div class="wrap">
  <div class="tag mag">Stats · results · rankings</div>
  <h1>Jiu-Jitsu<br>by the <em>numbers.</em></h1>
  <p>We read the official results so you don’t have to. Medal tables, team rankings and the stories hidden in the brackets, from Portugal and the rest of Europe.</p>
  <div class="ctas"><a class="btn" href="/blog/">Read the stats</a><a class="btn ghost" href="{IG}" rel="me noopener" target="_blank">Follow @bjj.stat</a></div>
  <div class="tiles">
    <div class="tile mag"><div class="tag">Lisbon Open 2026</div><div class="n">843</div><div class="l">medals analysed</div></div>
    <div class="tile"><div class="tag">Nacional Open 2026</div><div class="n">1,007</div><div class="l">registrations so far</div></div>
    <div class="tile"><div class="tag">Teams tracked</div><div class="n">185</div><div class="l">academies with a Lisbon medal</div></div>
    <div class="tile mint"><div class="tag">Next big one</div><div class="n">Nov 7</div><div class="l">Nacional Open, Odivelas</div></div>
  </div>
</div></section>
<section class="block"><div class="wrap">
  <div class="sec-head"><div><div class="tag">Latest</div><h2>Fresh from the data</h2></div><a href="/blog/">All stats →</a></div>
  <div class="grid">{card(posts[0], True)}{''.join(card(p) for p in posts[1:5])}</div>
</div></section>
<section class="block"><div class="wrap">
  <div class="sec-head"><div><div class="tag">Calendar</div><h2>Coming up in Portugal</h2></div><a href="/events/">Full calendar →</a></div>
  {ev_html([r for r in EVENTS if r[5]])}
</div></section>'''
    write('index.html', page('/', 'bjj.stat · Jiu-Jitsu by the numbers', 'Jiu-Jitsu stats, results and rankings from official data. Medal tables, team rankings and event calendars for Portugal and Europe.', home))

    # blog index
    blog = f'''<section class="post-head"><div class="wrap"><div class="tag mag">Stats</div><h1>Every story, by the numbers.</h1>
<p class="dek">Medal tables, team rankings and registration data, counted from official results.</p></div></section>
<section style="padding-bottom:72px"><div class="wrap"><div class="grid">{''.join(card(p) for p in posts)}</div></div></section>'''
    write('blog/index.html', page('/blog/', 'Stats · bjj.stat', 'All bjj.stat articles: Jiu-Jitsu medal tables, team rankings and data stories.', blog, 'blog'))

    # posts
    for p in posts:
        series_links = ''.join(f'<li><a href="/blog/{q["slug"]}/">{e(q["title"])}</a></li>' for q in posts if q is not p)[:4000]
        srcs = ''.join(f'<li><a href="{u}" rel="noopener" target="_blank">{e(t)}</a></li>' for t, u in p['sources'])
        body = f'''<article>
<header class="post-head"><div class="wrap"><div class="tag mag">{e(p["series"])}</div><h1>{e(p["title"])}</h1><p class="dek">{e(p["dek"])}</p>
<div class="meta"><span>{fmt_date(p["date"])}</span><span>·</span><span>bjj.stat</span></div></div></header>
<div class="wrap article"><div class="prose">{p["body"]}
<h2>Sources</h2><ul>{srcs}</ul></div>
<aside class="side">
  <div class="box"><div class="tag mint">Follow</div><h3>New stats every week</h3><p>Motion graphics and data stories on Instagram.</p><a class="btn" href="{IG}" rel="me noopener" target="_blank">@bjj.stat</a></div>
  <div class="box"><div class="tag">More stats</div><ul>{series_links}</ul></div>
</aside></div></article>'''
        write(f'blog/{p["slug"]}/index.html', page(f'/blog/{p["slug"]}/', f'{p["title"]} · bjj.stat', p['dek'], body, 'blog', f'/assets/media/{p["img"]}.webp', p))

    # events
    ev = f'''<section class="post-head"><div class="wrap"><div class="tag mag">Calendar</div><h1>Big events until the Euro.</h1>
<p class="dek">IBJJF, ADCC, FPJJB and ISBJJA events in Portugal and across Europe, from now to January 2027.</p></div></section>
<section style="padding-bottom:40px"><div class="wrap"><div class="sec-head"><h2>Portugal</h2></div>{ev_html([r for r in EVENTS if r[5]])}</div></section>
<section style="padding-bottom:72px"><div class="wrap"><div class="sec-head"><h2>Europe</h2></div>{ev_html([r for r in EVENTS if not r[5] or r[6] or r[4]=='FPJJB'])}
<div class="callout" style="margin-top:24px">Dates checked on each organiser’s official page on Oct 22, 2026 (ibjjf.com, adcombat.com, fpjjb.com, isbjja.com). Dates can change; confirm with the organiser.</div></div></section>'''
    write('events/index.html', page('/events/', 'Jiu-Jitsu events in Portugal and Europe · bjj.stat', 'Upcoming IBJJF, ADCC, FPJJB and ISBJJA Jiu-Jitsu events in Portugal and Europe until the 2027 European Championship.', ev, 'events'))

    # about
    ab = f'''<section class="post-head"><div class="wrap"><div class="tag mag">About</div><h1>We count. You read the story.</h1>
<p class="dek">bjj.stat turns official Jiu-Jitsu results into numbers you can share: medal tables, team rankings, records and fun facts.</p></div></section>
<div class="wrap article"><div class="prose">
<h2>How we work</h2>
<ul><li><strong>Official sources only.</strong> IBJJF results and registration lists, federation calendars and organiser pages.</li>
<li><strong>Counted with code.</strong> Every number is computed from the published podiums or lists, then checked twice.</li>
<li><strong>Honest wording.</strong> If a division had one athlete, we don’t call it a win over anyone. If registrations are still open, we say so.</li></ul>
<h2>Spotted a mistake?</h2>
<p>Send us a message on <a href="{IG}" rel="me noopener" target="_blank">Instagram</a> and we’ll fix it.</p>
</div><aside class="side"><div class="box"><div class="tag mint">Follow</div><h3>@bjj.stat</h3><p>New stats every week.</p><a class="btn" href="{IG}" rel="me noopener" target="_blank">Follow on Instagram</a></div></aside></div>'''
    write('about/index.html', page('/about/', 'About · bjj.stat', 'About bjj.stat: Jiu-Jitsu stats from official results.', ab, 'about'))

    # 404
    nf = '''<section class="hero"><div class="wrap"><div class="tag mag">404</div><h1>Tapped out.</h1><p>This page doesn’t exist. Try the latest stats instead.</p><a class="btn" href="/blog/">Read the stats</a></div></section>'''
    write('404.html', page('/404.html', 'Page not found · bjj.stat', 'Page not found.', nf))

    # sitemap + robots
    urls = ['/', '/blog/', '/events/', '/about/'] + [f'/blog/{p["slug"]}/' for p in posts]
    write('sitemap.xml', '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + ''.join(f'<url><loc>{DOMAIN}{u}</loc></url>' for u in urls) + '</urlset>\n')
    write('robots.txt', f'User-agent: *\nAllow: /\nSitemap: {DOMAIN}/sitemap.xml\n')
    print('built', len(posts), 'posts →', OUT)

if __name__ == '__main__':
    build()
