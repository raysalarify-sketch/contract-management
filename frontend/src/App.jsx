import { useState, useEffect, useRef, useCallback } from "react";

const API = import.meta.env.VITE_API_URL || "https://contract-backend-final.onrender.com/api/v1";
async function api(endpoint, opts = {}) {
  const token = localStorage.getItem("access_token");
  const headers = { ...opts.headers };
  if (!(opts.body instanceof FormData)) headers["Content-Type"] = "application/json";
  if (token) headers["Authorization"] = `Bearer ${token}`;
  try {
    const res = await fetch(`${API}${endpoint}`, { ...opts, headers });
    if (res.status === 401) { localStorage.removeItem("access_token"); return null; }
    if (!res.ok) throw await res.json().catch(() => ({ error: "err" }));
    return res.json();
  } catch(e) { if (e.status) throw e; return null; }
}

const T = {
  bg:"#faf9f7",card:"#ffffff",cardInner:"#f5f3ef",border:"#e8e4dd",borderLight:"#d5d1c9",
  text:"#1a1a1a",textSub:"#6b6560",textMuted:"#9c9590",
  accent:"#4f6ef7",accentSoft:"rgba(79,110,247,0.08)",accentText:"#3b5de7",
  success:"#10b981",successSoft:"rgba(16,185,129,0.08)",
  warning:"#f59e0b",warningSoft:"rgba(245,158,11,0.08)",
  danger:"#ef4444",dangerSoft:"rgba(239,68,68,0.08)",
};
const font="'Pretendard',-apple-system,'Segoe UI',sans-serif";
const fmtMoney=n=>{if(!n)return"0";if(n>=100000000){const v=n/100000000;return n%100000000===0?`${v.toFixed(0)}\u{C5B5}`:`${v.toFixed(1)}\u{C5B5}`}if(n>=10000)return`${(n/10000).toFixed(0)}\u{B9CC}`;return n.toLocaleString()};
const fmtMoneyFull=n=>n?n.toLocaleString()+"\u{C6D0}":"0\u{C6D0}";
const getDDay=d=>{const t=new Date();t.setHours(0,0,0,0);const x=new Date(d);x.setHours(0,0,0,0);const diff=Math.ceil((x-t)/86400000);return diff===0?"D-Day":diff>0?`D-${diff}`:`D+${Math.abs(diff)}`};
const typeLabel=t=>({"전세":"전세","반전세":"반전세","월세":"월세"}[t]||t);

function Card({children,style,onClick}){return<div onClick={onClick} style={{background:T.card,borderRadius:14,padding:18,border:`1px solid ${T.border}`,...style}}>{children}</div>}
function Badge({children,color="accent",style}){const cs={accent:[T.accentSoft,T.accentText],success:[T.successSoft,"#059669"],warning:[T.warningSoft,"#d97706"],danger:[T.dangerSoft,"#dc2626"]};const c=cs[color]||cs.accent;return<span style={{display:"inline-flex",alignItems:"center",gap:4,fontSize:11,fontWeight:700,padding:"4px 10px",borderRadius:8,background:c[0],color:c[1],...style}}>{children}</span>}
function Btn({children,variant="primary",size="md",disabled,style,...p}){const vs=variant==="primary"?{background:T.accent,color:"#fff"}:variant==="ghost"?{background:"transparent",color:T.textSub,border:`1px solid ${T.border}`}:{background:T.cardInner,color:T.text};const sz=size==="lg"?{padding:"14px 24px",fontSize:15}:{padding:"10px 18px",fontSize:13};return<button disabled={disabled} style={{borderRadius:10,border:"none",fontWeight:700,cursor:disabled?"not-allowed":"pointer",fontFamily:font,opacity:disabled?.5:1,...vs,...sz,...style}} {...p}>{children}</button>}

function MoneyInput({label,value,onChange,placeholder}){
  const display=value?Number(value).toLocaleString():"";
  const handleChange=e=>{const raw=e.target.value.replace(/[^0-9]/g,"");onChange(raw?Number(raw):0)};
  return<div>{label&&<label style={{fontSize:11,color:T.textMuted,fontWeight:600,display:"block",marginBottom:4}}>{label}</label>}<div style={{position:"relative"}}><input style={{width:"100%",padding:"10px 40px 10px 12px",borderRadius:10,border:`1px solid ${T.border}`,background:T.cardInner,color:T.text,fontSize:14,outline:"none",fontFamily:font,boxSizing:"border-box"}} value={display} onChange={handleChange} placeholder={placeholder||"0"} inputMode="numeric"/><span style={{position:"absolute",right:12,top:"50%",transform:"translateY(-50%)",fontSize:12,color:T.textMuted}}>원</span></div></div>
}

function Input({label,suffix,...p}){return<div>{label&&<label style={{fontSize:11,color:T.textMuted,fontWeight:600,display:"block",marginBottom:4}}>{label}</label>}<div style={{position:"relative"}}><input style={{width:"100%",padding:"10px 12px",paddingRight:suffix?"40px":"12px",borderRadius:10,border:`1px solid ${T.border}`,background:T.cardInner,color:T.text,fontSize:14,outline:"none",fontFamily:font,boxSizing:"border-box"}} {...p}/>{suffix&&<span style={{position:"absolute",right:12,top:"50%",transform:"translateY(-50%)",fontSize:12,color:T.textMuted}}>{suffix}</span>}</div></div>}
function Select({label,options,...p}){return<div>{label&&<label style={{fontSize:11,color:T.textMuted,fontWeight:600,display:"block",marginBottom:4}}>{label}</label>}<select style={{width:"100%",padding:"10px 12px",borderRadius:10,border:`1px solid ${T.border}`,background:T.cardInner,color:T.text,fontSize:14,fontFamily:font}} {...p}>{options.map(o=><option key={o.value} value={o.value}>{o.label}</option>)}</select></div>}
function SectionTitle({icon,title}){return<div style={{fontSize:14,fontWeight:700,color:T.text,marginBottom:12,display:"flex",alignItems:"center",gap:6}}><span style={{fontSize:16}}>{icon}</span>{title}</div>}

function Page({title,subtitle,onBack,children}){
  return<div style={{fontFamily:font,background:T.bg,minHeight:"100vh",maxWidth:480,margin:"0 auto",padding:"0 16px 40px"}}>
    <style>{`@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');@keyframes spin{to{transform:rotate(360deg)}}*{box-sizing:border-box;margin:0;padding:0}::-webkit-scrollbar{width:4px}::-webkit-scrollbar-thumb{background:${T.border};border-radius:2px}`}</style>
    <div style={{padding:"20px 0 16px",borderBottom:`1px solid ${T.border}`,marginBottom:16,display:"flex",alignItems:"center",gap:10}}>
      {onBack&&<button onClick={onBack} style={{background:"none",border:"none",color:T.textMuted,fontSize:18,cursor:"pointer",padding:4}}>←</button>}
      <div>
        <div style={{fontSize:10,color:T.accent,fontWeight:700,letterSpacing:".1em"}}>계약관리</div>
        <div style={{fontSize:18,fontWeight:800,color:T.text}}>{title}</div>
        {subtitle&&<div style={{fontSize:13,color:T.textSub,marginTop:4}}>{subtitle}</div>}
      </div>
    </div>
    <div style={{display:"flex",flexDirection:"column",gap:14}}>{children}</div>
  </div>
}

const mockOCR=fileName=>{
  const isValid=/임대차계약서|전세계약|월세계약|부동산임대차/.test(fileName||"");
  if(!isValid)return null;
  return{contractType:"월세",deposit:50000000,monthlyRent:800000,maintenanceFee:100000,rentDay:25,startDate:"2025-03-01",endDate:"2027-02-28",address:"서울특별시 강남구 테헤란로 123, 456호",tenantName:"",tenantPhone:"",landlordName:"",landlordPhone:"",landlordBank:"",landlordAccount:""};
};

function LandingPage({onStart,onLogin}){
  return<Page title="임대차계약 관리" subtitle="안전한 계약관리를 시작하세요">
    <Card style={{textAlign:"center",padding:32}}>
      <div style={{fontSize:48,marginBottom:16}}>🏠</div>
      <div style={{fontSize:20,fontWeight:800,color:T.text,marginBottom:8}}><span style={{color:T.accent}}>계약관리</span>로 시작하세요</div>
      <div style={{fontSize:14,color:T.textSub,lineHeight:1.6,marginBottom:24}}>임대차계약서를 등록하면<br/>월세 납부일 알림, 계약만료 안내를<br/>자동으로 받으실 수 있습니다.</div>
      <Btn size="lg" style={{width:"100%"}} onClick={onStart}>계약 등록 시작</Btn>
    </Card>
    <div style={{textAlign:"center",marginTop:8}}>
      <span style={{fontSize:13,color:T.textMuted}}>이미 계정이 있으신가요? </span>
      <span style={{fontSize:13,color:T.accent,fontWeight:700,cursor:"pointer"}} onClick={onLogin}>로그인</span>
    </div>
  </Page>
}

function SimpleLoginPage({onLoginSuccess,onBack}){
  const[name,setName]=useState("");const[pin,setPin]=useState("");const[loading,setLoading]=useState(false);const[error,setError]=useState("");
  const handleLogin=async()=>{
    if(!name||!pin){setError("성함과 6자리 PIN을 입력하세요");return}
    setLoading(true);setError("");
    try{
      const d=await api("/accounts/token/",{method:"POST",body:JSON.stringify({name,pin})});
      if(d?.token){localStorage.setItem("access_token",d.token.access);localStorage.setItem("refresh_token",d.token.refresh);onLoginSuccess()}
      else{setError(d?.error||"로그인에 실패했습니다")}
    }catch(e){setError("서버 연결 실패")}setLoading(false)
  };
  return<Page title="로그인" subtitle="계약관리 시스템 로그인" onBack={onBack}>
    <Card style={{padding:24}}>
      {error&&<div style={{background:T.dangerSoft,borderRadius:10,padding:"10px 14px",marginBottom:16,fontSize:13,color:"#dc2626",fontWeight:600}}>{error}</div>}
      <div style={{display:"flex",flexDirection:"column",gap:14}}>
        <Input label="성함" placeholder="성함 입력" value={name} onChange={e=>setName(e.target.value)}/>
        <Input label="6자리 PIN" type="password" placeholder="PIN 번호" value={pin} onChange={e=>setPin(e.target.value)} maxLength={6}/>
      </div>
      <Btn size="lg" style={{width:"100%",marginTop:16}} onClick={handleLogin} disabled={loading}>{loading?"확인 중...":"로그인"}</Btn>
    </Card>
  </Page>
}

function ContractUploadPage({onNext}){
  const [step, setStep] = useState("manual");
  const [data, setData] = useState({
    contractType: "월세", deposit: "", monthlyRent: "", rentDay: "25",
    startDate: "", endDate: "", address: "", 
    landlordName: "", landlordPhone: "", landlordBank: "", landlordAccount: "",
    tenantName: "", tenantPhone: "", pin: ""
  });

  const next = () => {
    if (step === "manual") setStep("tenant");
    else if (step === "tenant") {
      if(!data.tenantName || !data.tenantPhone) { alert("본인 정보를 입력해주세요."); return; }
      setStep("pin");
    }
    else {
      if(data.pin.length !== 6) { alert("PIN 6자리를 입력해주세요."); return; }
      onNext(data);
    }
  };
  const[uploading,setUploading]=useState(false);const[ocrFailed,setOcrFailed]=useState(false);const fileRef=useRef(null);
  const handleFile=e=>{const file=e.target.files[0];if(!file)return;setUploading(true);setTimeout(()=>{const r=mockOCR(file.name);if(r){setData(r);setStep("ocr_result")}else{setOcrFailed(true);setStep("manual")}setUploading(false)},2000)};

  if(step==="ocr_result")return<Page title="OCR 추출 완료" subtitle="추출된 정보를 확인해주세요" onBack={()=>setStep("manual")}>
    <Badge color="success" style={{marginBottom:12}}>✓ 자동 추출 완료</Badge>
    <Card><div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:14}}>
      {[["계약유형",typeLabel(data.contractType)],["보증금",fmtMoneyFull(data.deposit)],["월세",data.contractType==="전세"?"없음":fmtMoneyFull(data.monthlyRent)],["납부일",data.contractType==="전세"?"-":`매월 ${data.rentDay}일`],["시작일",data.startDate],["종료일",data.endDate]].map(([l,v])=><div key={l}><div style={{fontSize:11,color:T.textMuted,marginBottom:3}}>{l}</div><div style={{fontSize:14,color:T.text,fontWeight:600}}>{v}</div></div>)}
    </div></Card>
    <div style={{display:"flex",gap:10}}><Btn variant="ghost" style={{flex:1}} onClick={()=>setStep("manual")}>다시 입력</Btn><Btn style={{flex:2}} onClick={()=>setStep("manual")}>정보 보정 및 등록 →</Btn></div>
  </Page>;

  return<Page title="임대차계약 등록" subtitle={step==="manual"?"계약 정보를 입력해주세요":step==="tenant"?"본인 정보를 입력해주세요":"6자리 PIN을 설정해주세요"}>
    {ocrFailed&&<Badge color="warning" style={{marginBottom:8}}>임대차계약서 양식이 아닌 파일입니다. 수기입력으로 진행합니다.</Badge>}
      {step === "manual" && <div style={{display:"flex",flexDirection:"column",gap:12}}>
        <SectionTitle icon="📋" title="기본 정보"/>
        <div style={{display:"flex",gap:8}}>{["전세", "월세"].map(t => <button key={t} onClick={() => setData({...data, contractType: t})} style={{flex: 1, padding: "10px 0", borderRadius: 8, border: data.contractType === t ? `2px solid ${T.accent}` : `1px solid ${T.border}`, background: data.contractType === t ? T.accentSoft : "white", color: data.contractType === t ? T.accentText : T.textSub, fontWeight: 700, fontSize: 13, cursor: "pointer", fontFamily: font}}>{t}</button>)}</div>
        <MoneyInput label="보증금" value={data.deposit} onChange={v => setData({...data, deposit: v})} placeholder="예: 50,000,000"/>
        {data.contractType === "월세" && <MoneyInput label="월세" value={data.monthlyRent} onChange={v => setData({...data, monthlyRent: v})} placeholder="예: 500,000"/>}
        <Input label="물건지 주소" value={data.address} onChange={e => setData({...data, address: e.target.value})} placeholder="도로명 또는 지번 주소"/>
        <div style={{display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8}}>
          <Input label="시작일" type="date" value={data.startDate} onChange={e => setData({...data, startDate: e.target.value})}/>
          <Input label="종료일" type="date" value={data.endDate} onChange={e => setData({...data, endDate: e.target.value})}/>
        </div>
        <SectionTitle icon="🏢" title="임대인/계좌 정보"/>
        <div style={{display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8}}>
          <Input label="성함" value={data.landlordName} onChange={e => setData({...data, landlordName: e.target.value})} placeholder="임대인 성함"/>
          <Input label="연락처" value={data.landlordPhone} onChange={e => setData({...data, landlordPhone: e.target.value})} placeholder="010-0000-0000"/>
        </div>
        <div style={{display: "grid", gridTemplateColumns: "100px 1fr", gap: 8}}>
          <Input label="은행" value={data.landlordBank} onChange={e => setData({...data, landlordBank: e.target.value})} placeholder="은행명"/>
          <Input label="계좌번호" value={data.landlordAccount} onChange={e => setData({...data, landlordAccount: e.target.value})} placeholder="계좌번호 (숫자만)"/>
        </div>
        <Btn onClick={next} style={{marginTop: 8}}>다음 (본인 정보 입력)</Btn>
      </div>}

      {step === "tenant" && <div style={{display:"flex",flexDirection:"column",gap:12}}>
        <SectionTitle icon="👤" title="임차인 정보 (본인)"/>
        <Input label="성함" value={data.tenantName} onChange={e => setData({...data, tenantName: e.target.value})} placeholder="성함 입력"/>
        <Input label="연락처" value={data.tenantPhone} onChange={e => setData({...data, tenantPhone: e.target.value})} placeholder="010-0000-0000"/>
        <Btn onClick={next} style={{marginTop: 8}}>다음 (PIN 설정)</Btn>
        <Btn variant="ghost" onClick={() => setStep("manual")}>이전으로</Btn>
      </div>}

      {step === "pin" && <div style={{display:"flex",flexDirection:"column",gap:12}}>
        <SectionTitle icon="🔑" title="보안 비밀번호"/>
        <Input label="6자리 PIN" type="password" value={data.pin} onChange={e => setData({...data, pin: e.target.value})} placeholder="숫자 6자리 입력" maxLength={6} inputMode="numeric"/>
        <div style={{fontSize:12,color:T.textSub,lineHeight:1.5,marginTop:4}}>로그인 시 사용할 6자리 숫자를 입력해주세요.</div>
        <Btn onClick={next} style={{marginTop: 16}}>계약 등록 완료</Btn>
        <Btn variant="ghost" onClick={() => setStep("tenant")}>이전으로</Btn>
      </div>}
  </Page>
}

function PhoneLoginPage({contractData,onLoginSuccess}){
  const[loading,setLoading]=useState(false);const[error,setError]=useState("");
  useEffect(()=>{doLogin()},[]);
  const doLogin=async()=>{setLoading(true);const ph=contractData.tenantPhone.replace(/-/g,"");const nm=contractData.tenantName;
    try{let d=await api("/accounts/token/",{method:"POST",body:JSON.stringify({username:ph,password:ph})}).catch(()=>null);
      if(!d?.access){await api("/accounts/register/",{method:"POST",body:JSON.stringify({username:ph,password:ph,password_confirm:ph,first_name:nm.slice(1)||nm,last_name:nm[0]||"",phone:contractData.tenantPhone,role:"tenant"})}).catch(()=>{});d=await api("/accounts/token/",{method:"POST",body:JSON.stringify({username:ph,password:ph})}).catch(()=>null)}
      if(d?.access){localStorage.setItem("access_token",d.access);localStorage.setItem("refresh_token",d.refresh);await api("/contracts/register-contract/",{method:"POST",body:JSON.stringify({contract_type:contractData.contractType,deposit:contractData.deposit,monthly_rent:contractData.monthlyRent||0,rent_day:contractData.rentDay||25,start_date:contractData.startDate,end_date:contractData.endDate,address:contractData.address,landlord_name:contractData.landlordName,landlord_phone:contractData.landlordPhone,landlord_bank:contractData.landlordBank||"",landlord_account:contractData.landlordAccount||""})}).catch(()=>{});onLoginSuccess()}
      else{setError("로그인에 실패했습니다")}
    }catch(e){setError("서버 연결에 실패했습니다")}setLoading(false)};
  return<Page title="계약관리" subtitle="계약 등록 중..."><Card style={{textAlign:"center",padding:40}}>
    {loading?<><div style={{width:44,height:44,borderRadius:"50%",border:`3px solid ${T.accent}`,borderTopColor:"transparent",animation:"spin .8s linear infinite",margin:"0 auto 16px"}}/><div style={{color:T.text,fontSize:15,fontWeight:600}}>계약 등록 및 알림 설정 중...</div><div style={{color:T.textMuted,fontSize:13,marginTop:8}}>{contractData.tenantName} ({contractData.tenantPhone})</div></>
    :error?<><div style={{fontSize:36,marginBottom:12}}>⚠️</div><div style={{color:T.danger,fontSize:14,fontWeight:600}}>{error}</div><Btn style={{marginTop:16}} onClick={doLogin}>재시도</Btn></>
    :<><div style={{fontSize:36,marginBottom:12}}>✅</div><div style={{color:T.success,fontSize:15,fontWeight:600}}>등록 완료!</div></>}
  </Card></Page>
}

function ContractListPage({contracts,onSelect,onAdd,onLogout}){
  return<Page title="계약 목록" subtitle={`${contracts.length}건의 계약을 관리하고 있습니다`}>
    {onLogout&&<div style={{display:"flex",justifyContent:"flex-end",marginBottom:4}}><Btn variant="ghost" onClick={onLogout} style={{padding:"6px 12px",fontSize:12}}>로그아웃</Btn></div>}
    {contracts.map((c,i)=>{const dl=Math.ceil((new Date(c.end_date)-new Date())/86400000);return<Card key={c.id||i} onClick={()=>onSelect(c)} style={{cursor:"pointer",marginBottom:10}}>
      <div style={{display:"flex",justifyContent:"space-between",alignItems:"flex-start"}}>
        <div style={{flex:1}}><Badge color={c.contract_type==="전세"?"accent":c.contract_type==="반전세"?"warning":"success"} style={{marginBottom:8}}>{typeLabel(c.contract_type)}</Badge>
          <div style={{fontSize:15,fontWeight:700,color:T.text,marginTop:4}}>{c.address}</div>
          <div style={{fontSize:13,color:T.textSub,marginTop:4}}>보증금 {fmtMoney(c.deposit)} {c.monthly_rent>0?`/ 월세 ${fmtMoney(c.monthly_rent)}`:""}</div>
          <div style={{fontSize:12,color:T.textMuted,marginTop:4}}>{c.start_date} ~ {c.end_date}</div></div>
        <div style={{textAlign:"right",flexShrink:0}}><div style={{fontSize:20,fontWeight:800,color:dl<90?T.danger:dl<180?T.warning:T.accent}}>{dl}</div><div style={{fontSize:11,color:T.textMuted}}>일 남음</div></div>
      </div></Card>})}
    <Btn variant="ghost" style={{width:"100%",marginTop:8}} onClick={onAdd}>+ 새 계약 등록</Btn>
  </Page>
}

function ContractDetailPage({contract,onBack,onTestNotify}){
  const[tab,setTab]=useState("dashboard");const[schedules,setSchedules]=useState([]);const[notifications,setNotifications]=useState([]);
  useEffect(()=>{if(contract.id){api(`/contracts/${contract.id}/schedules/`).then(d=>{if(d)setSchedules(d)}).catch(()=>{});api(`/contracts/${contract.id}/notifications/`).then(d=>{if(d)setNotifications(d)}).catch(()=>{})};},[contract.id]);
  const markPaid=async id=>{await api(`/contracts/schedules/${id}/mark-paid/`,{method:"POST"}).catch(()=>{});setSchedules(s=>s.map(x=>x.id===id?{...x,status:"paid"}:x))};
  const dl=Math.ceil((new Date(contract.end_date)-new Date())/86400000);const pc=schedules.filter(s=>s.status==="paid").length;const tp=schedules.length;const nd=schedules.find(s=>s.status!=="paid");const hm=contract.monthly_rent>0;
  const tabs=[{id:"dashboard",label:"대시보드"},{id:"payments",label:"납부"},{id:"alerts",label:"알림"},{id:"info",label:"계약"}];
  return<div style={{fontFamily:font,background:T.bg,minHeight:"100vh",maxWidth:480,margin:"0 auto",padding:"0 16px 100px"}}>
    <style>{`@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');@keyframes spin{to{transform:rotate(360deg)}}*{box-sizing:border-box;margin:0;padding:0}`}</style>
    <div style={{padding:"16px 0",borderBottom:`1px solid ${T.border}`,display:"flex",justifyContent:"space-between",alignItems:"center"}}>
      <div style={{display:"flex",alignItems:"center",gap:10}}><button onClick={onBack} style={{background:"none",border:"none",color:T.textMuted,fontSize:18,cursor:"pointer"}}>←</button><div><div style={{fontSize:10,color:T.accent,fontWeight:700,letterSpacing:".1em"}}>계약관리</div><div style={{fontSize:14,fontWeight:700,color:T.text,maxWidth:220,overflow:"hidden",textOverflow:"ellipsis",whiteSpace:"nowrap"}}>{contract.address?.split(",")[0]||"계약 상세"}</div></div></div>
      <Badge color={contract.contract_type==="전세"?"accent":contract.contract_type==="반전세"?"warning":"success"}>{typeLabel(contract.contract_type)}</Badge>
    </div>
    <div style={{display:"flex",gap:4,padding:"12px 0",borderBottom:`1px solid ${T.border}`}}>{tabs.map(t=><button key={t.id} onClick={()=>setTab(t.id)} style={{flex:1,padding:"8px 0",borderRadius:8,border:"none",background:tab===t.id?T.accentSoft:"transparent",color:tab===t.id?T.accentText:T.textMuted,fontSize:12,fontWeight:700,cursor:"pointer",fontFamily:font}}>{t.label}</button>)}</div>
    <div style={{paddingTop:16,display:"flex",flexDirection:"column",gap:14}}>
      {tab==="dashboard"&&<>
        <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:10}}>
          <Card style={{textAlign:"center",padding:14}}><div style={{fontSize:24,fontWeight:800,color:dl<90?T.danger:dl<180?T.warning:T.accent}}>{dl}</div><div style={{fontSize:11,color:T.textMuted}}>잔여일</div></Card>
          <Card style={{textAlign:"center",padding:14}}><div style={{fontSize:24,fontWeight:800,color:T.text}}>{fmtMoney(contract.deposit)}</div><div style={{fontSize:11,color:T.textMuted}}>보증금</div></Card>
        </div>
        {dl<=90&&<Card style={{background:T.dangerSoft,border:"1px solid rgba(239,68,68,0.3)",padding:14}}><div style={{fontSize:13,fontWeight:700,color:"#dc2626"}}>🚨 계약 만료 {dl}일 전</div><div style={{fontSize:12,color:"#b91c1c",marginTop:4}}>갱신/종료 여부를 임대인과 협의하세요</div></Card>}
        {hm&&<><Card><div style={{display:"flex",justifyContent:"space-between",alignItems:"center",marginBottom:10}}><div style={{fontSize:14,fontWeight:700,color:T.text}}>납부 현황</div><div style={{fontSize:12,color:T.textSub}}>{pc}/{tp}회</div></div><div style={{height:6,borderRadius:3,background:T.cardInner,overflow:"hidden"}}><div style={{height:"100%",borderRadius:3,background:T.accent,width:`${tp?pc/tp*100:0}%`}}/></div></Card>
          {nd&&<Card><div style={{fontSize:11,color:T.textMuted,marginBottom:6}}>다음 납부</div><div style={{display:"flex",justifyContent:"space-between",alignItems:"center"}}><div><div style={{fontSize:16,fontWeight:700,color:T.text}}>{fmtMoneyFull(nd.amount)}</div><div style={{fontSize:12,color:T.textSub,marginTop:2}}>{nd.due_date}</div></div><Badge color={getDDay(nd.due_date)==="D-Day"?"danger":"accent"}>{getDDay(nd.due_date)}</Badge></div></Card>}</>}
        <Card><SectionTitle icon="🏢" title="임대인"/><div style={{fontSize:14,color:T.text,fontWeight:600}}>{contract.landlord_name||"-"}</div><div style={{fontSize:13,color:T.textSub,marginTop:2}}>{contract.landlord_phone||"-"}</div>{contract.landlord_bank&&<div style={{fontSize:12,color:T.textMuted,marginTop:4}}>💳 {contract.landlord_bank} {contract.landlord_account}</div>}</Card>
      </>}
      {tab==="payments"&&<>{!hm?<Card style={{textAlign:"center",padding:32}}><div style={{fontSize:36,marginBottom:8}}>🏠</div><div style={{fontSize:15,fontWeight:700,color:T.text}}>전세 계약</div><div style={{fontSize:13,color:T.textSub,marginTop:6}}>월세 납부가 없는 전세 계약입니다.<br/>계약 만료일 알림을 자동으로 받으실 수 있습니다.</div></Card>
        :<><div style={{display:"flex",gap:8}}><Badge color="success">{pc}건 납부</Badge><Badge color="danger">{tp-pc}건 미납</Badge></div>
          {schedules.map(s=>{const ip=s.status==="paid";const dd=getDDay(s.due_date);return<Card key={s.id} style={{padding:14}}><div style={{display:"flex",justifyContent:"space-between",alignItems:"center"}}><div style={{flex:1}}><div style={{display:"flex",alignItems:"center",gap:8}}><span style={{fontSize:14,fontWeight:600,color:T.text}}>{s.due_date}</span><Badge color={ip?"success":dd==="D-Day"?"danger":"accent"}>{ip?"납부완료":dd}</Badge></div><div style={{fontSize:13,color:T.textSub,marginTop:4}}>{fmtMoneyFull(s.amount)}</div></div>{!ip&&<Btn onClick={()=>markPaid(s.id)} style={{padding:"6px 14px",fontSize:12}}>납부확인</Btn>}</div></Card>})}</>}</>}
      {tab==="alerts"&&<>
        <div style={{display:"flex",justifyContent:"space-between",alignItems:"center"}}><div style={{fontSize:14,fontWeight:700,color:T.text}}>발송 이력</div><Btn variant="ghost" onClick={()=>onTestNotify(contract)} style={{padding:"6px 14px",fontSize:12}}>테스트 발송</Btn></div>
        {notifications.length===0?<Card style={{textAlign:"center",padding:28}}><div style={{fontSize:32,marginBottom:8}}>📭</div><div style={{color:T.textMuted,fontSize:13}}>아직 발송 이력이 없습니다</div></Card>
        :notifications.map((n,i)=><Card key={n.id||i} style={{padding:14}}><div style={{display:"flex",justifyContent:"space-between",alignItems:"center",marginBottom:6}}><div style={{display:"flex",gap:6}}><Badge color={n.channel==="kakao"?"warning":"accent"} style={{fontSize:10}}>{n.channel==="kakao"?"알림톡":"SMS"}</Badge><Badge color={n.status==="sent"?"success":"danger"} style={{fontSize:10}}>{n.status==="sent"?"발송완료":"실패"}</Badge></div><span style={{fontSize:11,color:T.textMuted}}>{n.sent_at?new Date(n.sent_at).toLocaleString("ko"):"-"}</span></div><div style={{fontSize:12,color:T.textSub,whiteSpace:"pre-line",lineHeight:1.5}}>{n.content?.slice(0,120)}{n.content?.length>120?"...":""}</div></Card>)}
        <Card><div style={{fontSize:13,fontWeight:700,color:T.text,marginBottom:10}}>알림 규칙</div>
          {[hm&&{icon:"📅",label:"월세/관리비 D-3",desc:"3일 전 사전 안내"},hm&&{icon:"🔔",label:"납부일 당일",desc:"당일 납부 안내 + 계좌 정보"},hm&&{icon:"⚠️",label:"미납 알림",desc:"납부일 3일 경과 시"},{icon:"📋",label:"만료 3개월 전",desc:"갱신/종료 결정 안내"},{icon:"🚨",label:"만료 1개월 전",desc:"보증금 반환 확인 안내"}].filter(Boolean).map((r,i)=><div key={i} style={{display:"flex",gap:10,alignItems:"center",padding:"8px 0",borderTop:i?`1px solid ${T.border}`:"none"}}><span style={{fontSize:16}}>{r.icon}</span><div><div style={{fontSize:13,color:T.text,fontWeight:600}}>{r.label}</div><div style={{fontSize:11,color:T.textMuted}}>{r.desc}</div></div><div style={{marginLeft:"auto",width:8,height:8,borderRadius:"50%",background:T.success}}/></div>)}</Card>
      </>}
      {tab==="info"&&<Card><SectionTitle icon="📋" title="계약 정보"/>
        {[["계약유형",typeLabel(contract.contract_type)],["보증금",fmtMoneyFull(contract.deposit)],["월세",contract.monthly_rent?fmtMoneyFull(contract.monthly_rent):"없음"],["계약기간",`${contract.start_date} ~ ${contract.end_date}`],["물건지",contract.address],["임대인",`${contract.landlord_name||"-"} (${contract.landlord_phone||"-"})`]].map(([l,v],i)=><div key={l} style={{display:"flex",justifyContent:"space-between",padding:"10px 0",borderTop:i?`1px solid ${T.border}`:"none"}}><span style={{fontSize:13,color:T.textMuted}}>{l}</span><span style={{fontSize:13,color:T.text,fontWeight:600,textAlign:"right",maxWidth:"60%"}}>{v}</span></div>)}
      </Card>}
    </div>
  </div>
}

export default function App(){
  const[page,setPage]=useState("loading");const[contracts,setContracts]=useState([]);const[selectedContract,setSelectedContract]=useState(null);const[pendingContract,setPendingContract]=useState(null);
  useEffect(()=>{const tk=localStorage.getItem("access_token");if(tk){loadContracts().then(l=>setPage(l.length>0?"list":"landing")).catch(()=>setPage("landing"))}else{setPage("landing")}},[]);
  const loadContracts=async()=>{const d=await api("/contracts/my-contracts/");if(d&&d.length>0){setContracts(d);return d}return[]};
  const handleContractUpload=data=>{const tk=localStorage.getItem("access_token");saveContract(data,!!tk)};
  const saveContract=async(data,isLoggedIn)=>{
    try{
      const payload={
        contract_type:data.contractType,deposit:data.deposit,monthly_rent:data.monthlyRent||0,rent_day:data.rentDay||25,
        start_date:data.startDate,end_date:data.endDate,address:data.address,
        landlord_name:data.landlordName,landlord_phone:data.landlordPhone,landlord_bank:data.landlordBank||"",landlord_account:data.landlordAccount||""
      };
      if(!isLoggedIn){
        payload.tenant_name=data.tenantName;
        payload.tenant_phone=data.tenantPhone;
        payload.pin=data.pin;
      }
      const r=await api("/contracts/register-contract/",{method:"POST",body:JSON.stringify(payload)});
      if(r?.token){
        localStorage.setItem("access_token",r.token.access);
        localStorage.setItem("refresh_token",r.token.refresh);
      }
      const l=await loadContracts();
      setPage(l.length>0?"list":"landing");
    }catch(e){
      alert("등록 중 오류가 발생했습니다: "+(e.message||"알 수 없는 오류"));
    }
  };
  const handleLoginSuccess=async()=>{const l=await loadContracts();setPage(l.length>0?"list":"upload")};
  const handleTestNotify=async contract=>{try{const r=await api("/contracts/test-notification/",{method:"POST",body:JSON.stringify({template:"PAYMENT_D3",variables:{tenant_name:contract.tenant_name||"임차인",payment_type:"월세",address:contract.address||"",due_date:"2025-04-25",amount:fmtMoney(contract.monthly_rent||0),bank:contract.landlord_bank||"",account:contract.landlord_account||"",landlord_name:contract.landlord_name||""}})});alert(r?.success?"알림톡 + SMS 발송 완료!":"발송 실패")}catch(e){alert("발송 오류")}};
  const handleLogout=()=>{localStorage.removeItem("access_token");localStorage.removeItem("refresh_token");setContracts([]);setSelectedContract(null);setPage("landing")};

  if(page==="loading")return<div style={{fontFamily:font,background:T.bg,minHeight:"100vh",display:"flex",alignItems:"center",justifyContent:"center"}}><style>{`@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');*{box-sizing:border-box;margin:0;padding:0}`}</style><div style={{textAlign:"center"}}><div style={{fontSize:10,color:T.accent,fontWeight:700,letterSpacing:".1em"}}>계약관리</div><div style={{fontSize:14,color:T.textMuted,marginTop:8}}>로딩 중...</div></div></div>;
  if(page==="landing")return<LandingPage onStart={()=>setPage("upload")} onLogin={()=>setPage("login")}/>;
  if(page==="login")return<SimpleLoginPage onLoginSuccess={handleLoginSuccess} onBack={()=>setPage("landing")}/>;
  if(page==="upload")return<ContractUploadPage onNext={handleContractUpload}/>;
  if(page==="detail"&&selectedContract)return<ContractDetailPage contract={selectedContract} onBack={()=>{setSelectedContract(null);loadContracts();setPage("list")}} onTestNotify={handleTestNotify}/>;
  return<ContractListPage contracts={contracts} onSelect={c=>{setSelectedContract(c);setPage("detail")}} onAdd={()=>setPage("upload")} onLogout={handleLogout}/>
}
