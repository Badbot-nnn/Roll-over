#!/usr/bin/env python3
"""Recompute every analyst's stats from league.json "tickets" (the source of truth).
Usage: python3 update.py   -> writes computed "stats" per bot + per-ticket "xp", sets updated_at (WAT)."""
import json,math,datetime as dt
L=json.load(open("league.json")); WAT=dt.timezone(dt.timedelta(hours=1))
RANKS=[("Legendary Oracle",10000,14,True),("Master Predictor",4000,7,False),("Pro Strategist",1000,0,False),("Rookie Analyst",0,0,False)]
def smult(s): return 2.0 if s>=14 else 1.5 if s>=7 else 1.25 if s>=3 else 1.0
today=dt.datetime.now(WAT).date()
DAYS=["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
MONS=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
for b in L["bots"]:
    if b["role"]!="analyst": continue
    T=sorted([t for t in L["tickets"] if t["bot"]==b["id"]],key=lambda t:t["date"])
    xp=streak=best=w=l=0; stake=ret=0.0; shield=False; last_loss=None; shield_date=None
    for t in T:
        if t.get("result") not in ("won","lost"): t["xp"]=None; continue
        d=dt.date.fromisoformat(t["date"]); k=math.log(t["odds"])/math.log(2.5)
        if shield and shield_date and (d-shield_date).days>14: shield=False
        tier="Hot" if streak>=5 else "Cold" if last_loss and (d-last_loss).days<=2 else "Normal"
        stake+=L["stake"]
        if t["result"]=="won":
            streak+=1; w+=1; ret+=L["stake"]*t["odds"]
            g=100*k*smult(streak)*(1.1 if tier=="Hot" else 1.0)
            g+={3:150,7:500,14:1500}.get(streak,0)
            if streak==7: shield=True; shield_date=d
            last_loss=None
        else:
            l+=1; g=-60*k; last_loss=d
            if shield: shield=False
            else: streak=0
        g+=t.get("penalty",0); g=round(g,1); t["xp"]=g; xp=max(0,xp+g); best=max(best,streak)
    if shield and shield_date and (today-shield_date).days>14: shield=False
    s30=[t for t in T if t.get("result") in("won","lost") and (today-dt.date.fromisoformat(t["date"])).days<30]
    rank=next(r for r,x,s,roi in RANKS if xp>=x and best>=s and (not roi or ret>stake))
    tier="Hot" if streak>=5 else "Cold" if last_loss and (today-last_loss).days<=2 else "Normal"
    b["stats"]=dict(xp=round(xp,1),rank=rank,tier=tier,streak=streak,best_streak=best,wins=w,losses=l,
      win_rate=round(100*w/(w+l),1) if w+l else None,
      win_rate_30d=round(100*sum(t["result"]=="won" for t in s30)/len(s30),1) if s30 else None,
      roi=round((ret-stake)/L["stake"],2) if stake else None,shield=shield)
by={}
for t in L["tickets"]:
    res=t.get("result")
    if res not in ("won","lost","void"): continue
    rec=by.setdefault(t["date"],{"won":0,"lost":0,"void":0}); rec[res]+=1
L["rounds"]=[]
for i,d in enumerate(sorted(by),1):
    day=dt.date.fromisoformat(d); w,ls,vd=by[d]["won"],by[d]["lost"],by[d]["void"]
    when=f"{DAYS[day.weekday()]} {day.day} {MONS[day.month-1]}"
    bits=[f"{w} won", f"{ls} lost"]+( [f"{vd} void"] if vd else [] )
    L["rounds"].append({"round":i,"date":d,"won":w,"lost":ls,"void":vd,"summary":f"Round {i} · {when} · {', '.join(bits)}"})
L["updated_at"]=dt.datetime.now(WAT).isoformat(timespec="seconds")
json.dump(L,open("league.json","w"),indent=2,ensure_ascii=False); print("updated",L["updated_at"])
