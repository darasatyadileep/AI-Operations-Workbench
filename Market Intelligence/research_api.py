import os, json, sqlite3
from datetime import datetime, timezone
from pathlib import Path
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv(Path(__file__).with_name('.env'))
router = APIRouter()
DB = Path(__file__).with_name('research_history.db')
class ResearchRequest(BaseModel):
    query: str = Field(min_length=12, max_length=2500)

def init_db():
    with sqlite3.connect(DB) as con:
        con.execute('CREATE TABLE IF NOT EXISTS research_runs (id INTEGER PRIMARY KEY, query TEXT, report TEXT, sources TEXT, created_at TEXT)')

@router.post('/research')
def research(payload: ResearchRequest):
    if not os.getenv('OPENAI_API_KEY'):
        raise HTTPException(503, 'Add OPENAI_API_KEY to Market Intelligence/.env. API billing/credits are required for live research.')
    try:
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        response = client.responses.create(
            model=os.getenv('OPENAI_RESEARCH_MODEL','gpt-4.1'),
            tools=[{'type':'web_search_preview'}],
            input=[{'role':'system','content':('You are an evidence-first oil and gas technology intelligence researcher. Search the live web. Prioritize first-party company newsrooms and reliable industry sources. Give dated, specific developments, deployment maturity, verified facts, source citations and practical implications for gas operators. Separate evidence from inference. Never fabricate company announcements, metrics, or dates. Reject generic marketing noise. Cite original URLs in the report. If evidence is thin, say so.')},{'role':'user','content':payload.query}],
            max_output_tokens=2200
        )
        report=response.output_text or ''
        sources=[]
        for item in response.output:
            for content in getattr(item,'content',[]):
                for ann in getattr(content,'annotations',[]) or []:
                    if getattr(ann,'type',None)=='url_citation':
                        sources.append({'title':getattr(ann,'title','Source'),'url':getattr(ann,'url','')})
        sources=list({s['url']:s for s in sources if s['url']}.values())
        init_db()
        with sqlite3.connect(DB) as con:
            con.execute('INSERT INTO research_runs(query,report,sources,created_at) VALUES(?,?,?,?)',(payload.query,report,json.dumps(sources),datetime.now(timezone.utc).isoformat()))
        return {'report':report,'sources':sources,'mode':'LIVE_WEB_RESEARCH','saved':True}
    except Exception as exc:
        message=str(exc)
        if any(x in message for x in ['insufficient_quota','credit_balance_exhausted','no credits']):
            raise HTTPException(402,'OpenAI API credits are exhausted. Add credits to enable live web research.')
        raise HTTPException(502,f'Research request failed: {message[:400]}')

@router.get('/research/history')
def history():
    init_db()
    with sqlite3.connect(DB) as con:
        rows=con.execute('SELECT id,query,report,sources,created_at FROM research_runs ORDER BY id DESC LIMIT 30').fetchall()
    return [{'id':r[0],'query':r[1],'report':r[2],'sources':json.loads(r[3]),'created_at':r[4]} for r in rows]
