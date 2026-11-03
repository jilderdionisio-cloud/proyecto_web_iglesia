import { useEffect, useState } from 'react'
import { apiGet, apiPost, apiPut } from './api'

export function DashboardHome({ session }) {
  const [data, setData] = useState(null)
  useEffect(() => { apiGet(session, '/dashboard/').then(setData).catch(() => setData({})) }, [session])
  const cards=[['Miembros activos',data?.active_members],['Próximos eventos',data?.upcoming_events],['Ministerios',data?.ministries],['Ingresos',data?.income !== undefined ? `$${data.income}` : 'Restringido']]
  return <><header className="topbar"><div><p className="eyebrow">Panel de control</p><h1>Resumen de iglesia</h1></div></header><section className="metrics">{cards.map(([label,value])=><article className="metric" key={label}><p>{label}</p><strong>{value ?? '...'}</strong><small>Datos actualizados</small></article>)}</section><section className="empty-panel"><h2>Asistencia por estado</h2><div className="bar-chart">{(data?.attendance||[]).map(x=><div key={x.status} style={{height:`${Math.max(12,x.count*16)}px`}} title={`${x.status}: ${x.count}`}><span>{x.count}</span><small>{x.status}</small></div>)}</div></section></>
}

export function CollectionModule({ session, title, endpoint, fields, detail }) {
  const [items,setItems]=useState([]); const [message,setMessage]=useState(''); const initial=Object.fromEntries(fields.map(f=>[f.key,f.default||''])); const [form,setForm]=useState(initial)
  const load=()=>apiGet(session,endpoint).then(setItems).catch(e=>setMessage(e.message))
  useEffect(load,[])
  async function submit(e){e.preventDefault();try{await apiPost(session,endpoint,form);setForm(initial);setMessage('Registro guardado.');load()}catch(err){setMessage(err.message)}}
  return <section className="module"><header className="module-header"><p className="eyebrow">Gestión</p><h1>{title}</h1></header><div className="member-layout"><form className="member-form" onSubmit={submit}><h2>Nuevo registro</h2>{fields.map(f=><label key={f.key}>{f.label}{f.type==='select'?<select required={f.required} value={form[f.key]} onChange={e=>setForm({...form,[f.key]:e.target.value})}>{f.options?.map(o=><option value={o.value} key={o.value}>{o.label}</option>)}</select>:<input required={f.required} type={f.type||'text'} value={form[f.key]} onChange={e=>setForm({...form,[f.key]:e.target.value})}/>}</label>)}<button className="primary">Guardar</button></form><div className="member-list">{message&&<p className="message">{message}</p>}<div className="table-wrap"><table><thead><tr><th>Registro</th><th>Detalle</th></tr></thead><tbody>{items.map(x=><tr key={x.id}><td>{x.title||x.name||x.concept}</td><td>{detail(x)}</td></tr>)}</tbody></table></div></div></div></section>
}

export function ChurchSettings({ session }) { const [form,setForm]=useState(null); const [message,setMessage]=useState(''); useEffect(()=>{apiGet(session,'/church-profile/').then(setForm).catch(e=>setMessage(e.message))},[]); if(!form)return <p>Cargando configuración…</p>; const keys=[['name','Nombre'],['address','Dirección'],['phone','Teléfono'],['email','Correo'],['regular_schedule','Horarios habituales']]; return <section className="module"><h1>Configuración de la iglesia</h1><form className="member-form" onSubmit={async e=>{e.preventDefault();try{setForm(await apiPut(session,'/church-profile/',form));setMessage('Configuración actualizada.')}catch(err){setMessage(err.message)}}}>{keys.map(([k,l])=><label key={k}>{l}<input value={form[k]||''} onChange={e=>setForm({...form,[k]:e.target.value})}/></label>)}<button className="primary">Guardar configuración</button>{message&&<p className="message">{message}</p>}</form></section> }
