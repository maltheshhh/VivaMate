import os, io, re, json, sqlite3, tempfile
from datetime import date, timedelta
import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.responses import StreamingResponse, FileResponse, Response

load_dotenv()
KEY = os.getenv("VIVAMATE_API_KEY", "")
BASE = os.getenv("VIVAMATE_API_BASE", "").rstrip("/")
MODEL = os.getenv("VIVAMATE_MODEL") or "qwen2.5:7b"
OLLAMA = os.getenv("OLLAMA_HOST", "http://localhost:11434")
CLOUD_OK = bool(KEY and BASE)

app = FastAPI()
db = sqlite3.connect("vivamate.db", check_same_thread=False)
db.row_factory = sqlite3.Row
db.executescript("""
create table if not exists profile(id integer primary key, name, role, github, resume, repos);
create table if not exists msgs(id integer primary key autoincrement, session, role, content);
create table if not exists scores(id integer primary key autoincrement, session, topic, score real, clarity real, day);
create table if not exists kv(k primary key, v);""")


def q(sql, *a):
    return db.execute(sql, a).fetchall()


def run(sql, *a):
    db.execute(sql, a)
    db.commit()


def use_cloud():
    r = q("select v from kv where k='mode'")
    return CLOUD_OK and bool(r) and r[0]["v"] == "cloud"


async def llm(msgs, cloud):
    async with httpx.AsyncClient(timeout=None) as c:
        if cloud:
            async with c.stream("POST", BASE + "/chat/completions", headers={"Authorization": "Bearer " + KEY},
                                json={"model": MODEL, "messages": msgs, "stream": True}) as r:
                async for l in r.aiter_lines():
                    if l.startswith("data: ") and l != "data: [DONE]":
                        d = json.loads(l[6:])["choices"][0]["delta"].get("content")
                        if d:
                            yield d
        else:
            async with c.stream("POST", OLLAMA + "/api/chat", json={"model": MODEL, "messages": msgs, "stream": True}) as r:
                async for l in r.aiter_lines():
                    if l:
                        yield json.loads(l).get("message", {}).get("content", "")


MODES = {
    "mock": "Mock Interview: ask exactly ONE question at a time, wait for the answer, give 1-2 lines of feedback, then ask the next.",
    "explain": "Explain Mode: teach the concept the candidate missed in simple steps with a small example, then check understanding with one question.",
    "hr": "HR Round: behavioural and situational questions (strengths, conflict, goals). One at a time, use STAR feedback.",
    "dsa": "DSA Round: one data-structures/algorithms question at a time, ask for approach and complexity before code.",
    "project": "Project Deep-Dive: pick ONE of the candidate's GitHub repos and grill them on design, trade-offs, bugs and testing, one question at a time.",
    "roast": "Resume Roast: critique the resume bluntly with specific line-level fixes (quote the line, then give the rewrite).",
    "report": "Write a session report: strengths, weaknesses, and exactly 5 revision topics.",
}
CMD = {
    "/quiz": ("dsa", "Run a rapid-fire 5-question quiz, one question at a time. Ask the first now."),
    "/weak": ("explain", "Teach me my weakest topic from scratch."),
    "/resume-tips": ("roast", "Roast my resume."),
    "/hr": ("hr", "Start the HR round."),
    "/report": ("report", "Write my session report."),
}
GRADED = {"mock", "hr", "dsa", "project"}


def topics():
    return q("select topic, avg(score) a, count(*) n from scores group by topic order by a")


async def evaluate(question, answer, cloud):
    p = [{"role": "system", "content": 'Score the candidate answer. Reply ONLY JSON: {"score":0-10,"clarity":0-10,"topic":"<1-2 word topic>"}'},
         {"role": "user", "content": f"Q: {question}\nA: {answer}"}]
    r = "".join([t async for t in llm(p, cloud)])
    return json.loads(re.search(r"\{.*\}", r, re.S).group())


@app.post("/api/chat")
async def chat(req: Request):
    b = await req.json()
    s, mode, msg = b["session"], b.get("mode", "mock"), b["message"].strip()
    text, cmd = msg, msg.split()[0] if msg.startswith("/") else None
    if cmd in CMD:
        mode, text = CMD[cmd]
    p = q("select * from profile where id=1")
    ctx = ""
    if p:
        p = p[0]
        ctx = f"Candidate: {p['name']}, targeting {p['role']}.\nResume:\n{(p['resume'] or '')[:3000]}\nGitHub repos: {p['repos']}"
    weak = [f"{t['topic']} ({t['a']:.1f}/10)" for t in topics()[:3]]
    sysmsg = ("You are VivaMate, a sharp but supportive placement interviewer. Be concise. " + MODES.get(mode, MODES["mock"]) + "\n" + ctx
              + ("\nWeakest topics: " + ", ".join(weak) + ". Early on, revisit one: 'Last time you struggled with X. Let's try again.'" if weak else "")
              + ("\nPRESSURE MODE: the candidate has 60 seconds per question. Be strict, terse and demanding." if b.get("pressure") else ""))
    hist = [{"role": m["role"], "content": m["content"]} for m in reversed(q("select role,content from msgs where session=? order by id desc limit 12", s))]
    prev = next((m["content"] for m in reversed(hist) if m["role"] == "assistant"), None)
    cloud = use_cloud()
    ms = [{"role": "system", "content": sysmsg}] + hist + [{"role": "user", "content": text}]

    async def gen():
        out = ""
        try:
            async for t in llm(ms, cloud):
                out += t
                yield f"data: {json.dumps({'t': t})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e) or 'LLM unreachable'})}\n\n"
        if out:
            run("insert into msgs(session,role,content) values(?,?,?)", s, "user", msg)
            run("insert into msgs(session,role,content) values(?,?,?)", s, "assistant", out)
            if mode in GRADED and prev and not cmd:
                try:
                    d = await evaluate(prev, msg, cloud)
                    run("insert into scores(session,topic,score,clarity,day) values(?,?,?,?,?)", s, str(d["topic"]).lower(),
                        float(d["score"]), float(d.get("clarity", 5)), date.today().isoformat())
                    yield f"data: {json.dumps({'score': d['score'], 'topic': d['topic']})}\n\n"
                except Exception:
                    pass
        yield "data: [DONE]\n\n"

    return StreamingResponse(gen(), media_type="text/event-stream")


def readiness_val():
    r = q("select avg(score) a, avg(clarity) c, count(distinct topic) n from scores")[0]
    if r["a"] is None:
        return 0
    return round(r["a"] * 6 + min(r["n"], 10) * 2.5 + r["c"] * 1.5)


def streak():
    days = {r["day"] for r in q("select distinct day from scores")}
    d, n = date.today(), 0
    if d.isoformat() not in days:
        d -= timedelta(days=1)
    while d.isoformat() in days:
        n, d = n + 1, d - timedelta(days=1)
    return n


def build_report():
    t = [{"topic": r["topic"], "avg": round(r["a"], 1), "n": r["n"]} for r in topics()]
    total = q("select count(*) c from scores")[0]["c"]
    badges = (["10 questions answered"] if total >= 10 else [])
    for x in t:
        sc = [r["score"] for r in q("select score from scores where topic=? order by id", x["topic"])]
        if len(sc) > 1 and sc[0] < 5 and sc[-1] >= 7:
            badges.append("Weak spot cleared: " + x["topic"])
    return {"topics": t, "strengths": [x for x in reversed(t) if x["avg"] >= 6][:3], "weaknesses": t[:5],
            "revision": [x["topic"] for x in t[:5]], "readiness": readiness_val(), "streak": streak(),
            "badges": badges, "answered": total}


@app.get("/api/report")
def report():
    return build_report()


@app.get("/api/readiness")
def readiness():
    return {"readiness": readiness_val(), "streak": streak()}


@app.get("/api/export")
def export():
    from reportlab.pdfgen import canvas
    r, buf = build_report(), io.BytesIO()
    c = canvas.Canvas(buf)
    y = 800
    lines = ["VivaMate Session Report", f"Readiness: {r['readiness']}/100   Streak: {r['streak']}d   Answers: {r['answered']}", "",
             "Strengths:"] + [f"  {x['topic']} ({x['avg']}/10)" for x in r["strengths"]] + ["Weaknesses:"] + \
            [f"  {x['topic']} ({x['avg']}/10)" for x in r["weaknesses"]] + ["5 revision topics:"] + [f"  - {x}" for x in r["revision"]]
    for l in lines:
        c.drawString(60, y, l)
        y -= 20
    c.save()
    return Response(buf.getvalue(), media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=vivamate-report.pdf"})


@app.get("/api/profile")
def get_profile():
    p = q("select name,role,github from profile where id=1")
    return dict(p[0]) if p else {}


@app.post("/api/profile")
async def set_profile(name: str = Form(...), role: str = Form(""), github: str = Form(""), resume: UploadFile = File(None)):
    text = ""
    if resume and resume.filename:
        from pypdf import PdfReader
        text = "\n".join(pg.extract_text() or "" for pg in PdfReader(io.BytesIO(await resume.read())).pages)
    repos = []
    if github:
        try:
            async with httpx.AsyncClient(timeout=10) as c:
                for r in (await c.get(f"https://api.github.com/users/{github}/repos?per_page=30")).json():
                    repos.append(f"{r['name']} [{r.get('language')}]: {r.get('description') or ''}")
        except Exception:
            pass
    run("insert or replace into profile values(1,?,?,?,?,?)", name, role, github, text, "; ".join(repos))
    return {"ok": True, "repos": len(repos), "resume_chars": len(text)}


_w = None


@app.post("/api/transcribe")
async def transcribe(audio: UploadFile = File(...)):
    global _w
    from faster_whisper import WhisperModel
    _w = _w or WhisperModel("base", compute_type="int8")
    with tempfile.NamedTemporaryFile(suffix=".webm") as f:
        f.write(await audio.read())
        f.flush()
        segs, _ = _w.transcribe(f.name)
        return {"text": " ".join(s.text for s in segs).strip()}


@app.get("/api/settings")
def get_settings():
    return {"mode": "cloud" if use_cloud() else "local", "cloud_available": CLOUD_OK, "model": MODEL}


@app.post("/api/settings")
async def set_settings(req: Request):
    m = (await req.json()).get("mode")
    if m == "local" or (m == "cloud" and CLOUD_OK):
        run("insert or replace into kv values('mode',?)", m)
    return get_settings()


@app.get("/")
def index():
    return FileResponse("index.html")
