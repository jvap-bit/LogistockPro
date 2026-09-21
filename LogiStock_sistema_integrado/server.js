const http=require('node:http');
const fs=require('node:fs');
const path=require('node:path');
const crypto=require('node:crypto');
const os=require('node:os');
const QRCode=require('qrcode');
const {DatabaseSync}=require('node:sqlite');
const root=__dirname;
const port=Number(process.env.PORT||3000);
const db=new DatabaseSync(path.join(root,'data','producao.db'));
db.exec(`PRAGMA journal_mode=WAL; PRAGMA busy_timeout=5000; PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS pedidos(id INTEGER PRIMARY KEY AUTOINCREMENT,numero TEXT NOT NULL UNIQUE,produto TEXT NOT NULL,quantidade TEXT NOT NULL,cliente TEXT NOT NULL,rua TEXT,casa TEXT,bairro TEXT,cep TEXT,prioridade TEXT NOT NULL DEFAULT 'Normal',status TEXT NOT NULL DEFAULT 'A Fazer',descricao TEXT);
CREATE TABLE IF NOT EXISTS logs(id INTEGER PRIMARY KEY AUTOINCREMENT,data_hora TEXT NOT NULL,acao TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS usuarios(id INTEGER PRIMARY KEY AUTOINCREMENT,email TEXT NOT NULL UNIQUE,senha TEXT,perfil TEXT NOT NULL,data_cadastro TEXT);
CREATE TABLE IF NOT EXISTS sessoes(token_hash TEXT PRIMARY KEY,usuario_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,expira_em INTEGER NOT NULL);`);
const columns=db.prepare('PRAGMA table_info(usuarios)').all().map(x=>x.name);
if(!columns.includes('salt'))db.exec('ALTER TABLE usuarios ADD COLUMN salt TEXT');
if(!columns.includes('password_hash'))db.exec('ALTER TABLE usuarios ADD COLUMN password_hash TEXT');
const orderColumns=db.prepare('PRAGMA table_info(pedidos)').all().map(x=>x.name);
if(!orderColumns.includes('descricao'))db.exec('ALTER TABLE pedidos ADD COLUMN descricao TEXT');
if(!orderColumns.includes('qr_token'))db.exec('ALTER TABLE pedidos ADD COLUMN qr_token TEXT');
db.exec('CREATE UNIQUE INDEX IF NOT EXISTS pedidos_qr_token ON pedidos(qr_token)');
// A base original não exige unicidade de OP. Validamos ao criar e indexamos quando não há duplicatas existentes.
try{db.exec('CREATE UNIQUE INDEX IF NOT EXISTS pedidos_numero_unico ON pedidos(numero)')}catch(e){console.warn('OPs duplicadas na base antiga; verifique os dados antes de cadastrar novas OPs.')} 
const fields=['numero','produto','quantidade','cliente','rua','casa','bairro','cep','prioridade','descricao'];
const profiles=['PCP','Produção','Gestão','Entregador'];
const hash=(password,salt)=>crypto.scryptSync(password,salt,64).toString('hex');
const tokenHash=token=>crypto.createHash('sha256').update(token).digest('hex');
const timingEqual=(a,b)=>{if(!a||!b||a.length!==b.length)return false;return crypto.timingSafeEqual(Buffer.from(a),Buffer.from(b))};
const log=action=>db.prepare('INSERT INTO logs(data_hora,acao) VALUES(?,?)').run(new Date().toLocaleString('pt-BR'),action);
const send=(res,status,value)=>{res.writeHead(status,{'Content-Type':'application/json; charset=utf-8','Cache-Control':'no-store'});res.end(JSON.stringify(value))};
const err=(res,message,status=400)=>send(res,status,{error:message});
const cookies=req=>Object.fromEntries((req.headers.cookie||'').split(';').map(x=>{const at=x.indexOf('=');return at<0?[x.trim(),'']:[x.slice(0,at).trim(),x.slice(at+1)]}));
const currentUser=req=>{const token=cookies(req).session;if(!token)return null;return db.prepare('SELECT u.id,u.email,u.perfil AS profile FROM sessoes s JOIN usuarios u ON u.id=s.usuario_id WHERE s.token_hash=? AND s.expira_em>?').get(tokenHash(token),Date.now())||null};
async function body(req){let chunks=[],size=0;for await(const chunk of req){size+=chunk.length;if(size>1e6)throw Error('Dados muito grandes');chunks.push(chunk)}return JSON.parse(Buffer.concat(chunks).toString()||'{}')}
const escapeHtml=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const server=http.createServer(async(req,res)=>{try{
 const url=new URL(req.url,'http://localhost'),p=url.pathname,method=req.method;
 if(p==='/documento'&&method==='GET'){
  const token=url.searchParams.get('token')||'';
  const order=/^[a-f0-9]{48}$/.test(token)?db.prepare('SELECT * FROM pedidos WHERE qr_token=?').get(token):null;
  res.writeHead(order?200:404,{'Content-Type':'text/html; charset=utf-8','Cache-Control':'no-store','Referrer-Policy':'no-referrer','X-Content-Type-Options':'nosniff'});
  if(!order)return res.end('<!doctype html><html lang="pt-BR"><meta name="viewport" content="width=device-width,initial-scale=1"><title>OP não encontrada</title><body><h1>OP não encontrada</h1></body></html>');
  const fieldsToShow=[['OP',order.numero],['Produto',order.produto],['Quantidade',order.quantidade],['Cliente',order.cliente],['Endereço de entrega',[order.rua,order.casa,order.bairro,order.cep].filter(Boolean).join(', ')],['Prioridade',order.prioridade],['Status atual',order.status]];
  const details=fieldsToShow.map(([label,value])=>`<dt>${escapeHtml(label)}</dt><dd>${escapeHtml(value)}</dd>`).join('');
  return res.end(`<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>OP ${escapeHtml(order.numero)} | LogiStock PRO</title><style>body{font:16px Arial,sans-serif;background:#0a1628;color:#e6edf3;margin:0;padding:24px}.card{max-width:600px;margin:auto;background:#162040;padding:24px;border:1px solid #1e3a5f;border-radius:16px}h1{color:#f5c518}dt{font-weight:bold;margin-top:18px;color:#f5c518}dd{margin:6px 0 0}a{display:inline-block;background:#f5c518;color:#0a1628;padding:12px 18px;border-radius:22px;margin-top:24px;font-weight:bold;text-decoration:none}</style></head><body><main class="card"><h1>LogiStock PRO</h1><p>Dados da ordem de produção</p><dl>${details}</dl><a href="/?op=${encodeURIComponent(order.numero)}">Entrar como Entregador</a></main></body></html>`);
 }
 if(p==='/api/register'&&method==='POST'){
  const b=await body(req),email=String(b.email||'').trim().toLowerCase();if(!/^\S+@\S+\.\S+$/.test(email)||String(b.password||'').length<6||!profiles.includes(b.profile))return err(res,'Confira e-mail, senha (mínimo 6 caracteres) e perfil.');
  if(db.prepare('SELECT id FROM usuarios WHERE email=?').get(email))return err(res,'E-mail já cadastrado.');
  const salt=crypto.randomBytes(16).toString('hex');db.prepare('INSERT INTO usuarios(email,senha,perfil,data_cadastro,salt,password_hash) VALUES(?,?,?,?,?,?)').run(email,'',b.profile,new Date().toLocaleString('pt-BR'),salt,hash(b.password,salt));log('Novo usuário cadastrado: '+email+' | Perfil: '+b.profile);return send(res,201,{ok:true});
 }
 if(p==='/api/login'&&method==='POST'){
  const b=await body(req),email=String(b.email||'').trim().toLowerCase(),u=db.prepare('SELECT * FROM usuarios WHERE email=?').get(email);if(!u)return err(res,'Credenciais inválidas.',401);
  let valid=false;if(u.password_hash&&u.salt)valid=timingEqual(hash(String(b.password||''),u.salt),u.password_hash);
  else if(u.senha){const legacy=crypto.createHash('sha256').update(String(b.password||'')).digest('hex');valid=timingEqual(legacy,u.senha);if(valid){const salt=crypto.randomBytes(16).toString('hex');db.prepare("UPDATE usuarios SET salt=?,password_hash=?,senha='' WHERE id=?").run(salt,hash(b.password,salt),u.id)}}
  if(!valid)return err(res,'Credenciais inválidas.',401);
  const token=crypto.randomBytes(32).toString('hex');db.prepare('INSERT INTO sessoes(token_hash,usuario_id,expira_em) VALUES(?,?,?)').run(tokenHash(token),u.id,Date.now()+7*86400000);res.setHeader('Set-Cookie',`session=${token}; HttpOnly; SameSite=Lax; Path=/; Max-Age=604800`);return send(res,200,{email:u.email,profile:u.perfil});
 }
 if(p==='/api/logout'&&method==='POST'){const token=cookies(req).session;if(token)db.prepare('DELETE FROM sessoes WHERE token_hash=?').run(tokenHash(token));res.setHeader('Set-Cookie','session=; HttpOnly; SameSite=Lax; Path=/; Max-Age=0');return send(res,200,{ok:true})}
 if(p==='/api/me'){let u=currentUser(req);return send(res,200,u?{email:u.email,profile:u.profile}:null)}
 if(p==='/api/track'&&method==='GET'){return send(res,200,db.prepare('SELECT numero,produto,cliente,status FROM pedidos WHERE numero=?').all(url.searchParams.get('numero')||''))}
 const user=currentUser(req);if(p.startsWith('/api/')&&!user)return err(res,'Entre na sua conta.',401);
 const qrMatch=p.match(/^\/api\/orders\/(\d+)\/qr$/);
 if(qrMatch&&method==='GET'){
  const order=db.prepare('SELECT * FROM pedidos WHERE id=?').get(Number(qrMatch[1]));
  if(!order)return err(res,'OP não encontrada.',404);
  if(!order.qr_token){const token=crypto.randomBytes(24).toString('hex');db.prepare('UPDATE pedidos SET qr_token=? WHERE id=? AND qr_token IS NULL').run(token,order.id);order.qr_token=db.prepare('SELECT qr_token FROM pedidos WHERE id=?').get(order.id).qr_token}
  const host=req.headers.host||'';
  let base=process.env.APP_BASE_URL;
  if(!base){if(!/^[a-z0-9.-]+(?::[0-9]{1,5})?$/i.test(host))return err(res,'Endereço inválido.',400);
   if(/^(localhost|127\.0\.0\.1)(:\d+)?$/i.test(host)){
    let ips=[];try{ips=Object.values(os.networkInterfaces()).flat().filter(x=>x&&x.family==='IPv4'&&!x.internal&&/^(192\.168\.|10\.|172\.(1[6-9]|2[0-9]|3[01])\.)/.test(x.address)).map(x=>x.address)}catch{}
    if(!ips.length)return err(res,'Defina APP_BASE_URL com o IP ou domínio acessível pelo celular antes de gerar o PDF.',400);
    base=`http://${ips[0]}:${port}`;
   }else base=`http://${host}`;
  }
  let target;try{target=new URL(base);if(!['http:','https:'].includes(target.protocol)||['localhost','127.0.0.1'].includes(target.hostname))throw Error('Endereço inválido')}catch{return err(res,'APP_BASE_URL precisa ser um endereço HTTP ou HTTPS acessível pelo celular, sem localhost.',400)}
  target.pathname='/documento';target.search='';target.searchParams.set('token',order.qr_token);target.searchParams.set('op',order.numero);
  const image=await QRCode.toDataURL(target.href,{errorCorrectionLevel:'M',margin:5,width:600});
  return send(res,200,{image,url:target.href});
 }
 if(p==='/api/orders'&&method==='GET')return send(res,200,db.prepare('SELECT * FROM pedidos ORDER BY id').all());
 if(p==='/api/logs'&&method==='GET')return send(res,200,db.prepare('SELECT * FROM logs ORDER BY id DESC').all());
 if(p==='/api/orders'&&method==='POST'){
  if(user.profile!=='PCP')return err(res,'Somente PCP pode cadastrar ordens.',403);let b=await body(req);
  if(!b.numero||!b.produto||!b.cliente||!b.quantidade)return err(res,'Preencha OP, produto, cliente e quantidade.');
  const values=fields.map(f=>String(b[f]||'').trim());if(db.prepare('SELECT id FROM pedidos WHERE numero=?').get(values[0]))return err(res,'OP já cadastrada.');
  db.exec('BEGIN IMMEDIATE');try{const info=db.prepare('INSERT INTO pedidos(numero,produto,quantidade,cliente,rua,casa,bairro,cep,prioridade,descricao,status) VALUES(?,?,?,?,?,?,?,?,?,? ,?)').run(...values,'A Fazer');log(user.email+' cadastrou OP '+values[0]);db.exec('COMMIT');return send(res,201,db.prepare('SELECT * FROM pedidos WHERE id=?').get(info.lastInsertRowid))}catch(e){db.exec('ROLLBACK');throw e}
 }
 const match=p.match(/^\/api\/orders\/(\d+)$/);if(match&&(method==='PATCH'||method==='DELETE')){
  const id=Number(match[1]);db.exec('BEGIN IMMEDIATE');try{
   let o=db.prepare('SELECT * FROM pedidos WHERE id=?').get(id);if(!o){db.exec('ROLLBACK');return err(res,'OP não encontrada.',404)}
   if(method==='DELETE'){
    if(!['PCP','Gestão'].includes(user.profile)||!['Finalizado','Em Rota','Entregue'].includes(o.status)){db.exec('ROLLBACK');return err(res,'Remoção não permitida.',403)}
    db.prepare('DELETE FROM pedidos WHERE id=?').run(id);log(user.email+' removeu OP '+o.numero);db.exec('COMMIT');return send(res,200,{ok:true});
   }
   const b=await body(req),next=b.status,allowed=user.profile==='PCP'?{'A Fazer':'Em Andamento','Em Andamento':'Qualidade','Qualidade':'Finalizado'}:user.profile==='Entregador'?{'Finalizado':'Em Rota','Em Rota':'Entregue'}:{};
   if(allowed[o.status]!==next){db.exec('ROLLBACK');return err(res,'Mudança de etapa não permitida.',403)}
   db.prepare('UPDATE pedidos SET status=? WHERE id=?').run(next,id);log(user.email+' alterou OP '+o.numero+' para '+next);db.exec('COMMIT');return send(res,200,db.prepare('SELECT * FROM pedidos WHERE id=?').get(id));
  }catch(e){db.exec('ROLLBACK');throw e}
 }
 if(p.startsWith('/api/'))return err(res,'Rota inexistente.',404);
 const publicDir=path.join(root,'public'),target=path.resolve(publicDir,'.'+(p==='/'?'/index.html':p));if(!target.startsWith(publicDir+path.sep)||!fs.existsSync(target)||!fs.statSync(target).isFile()){res.writeHead(404);return res.end('Arquivo não encontrado')}
 const type={'.html':'text/html','.css':'text/css','.js':'text/javascript'}[path.extname(target)]||'text/plain';res.writeHead(200,{'Content-Type':type+'; charset=utf-8'});fs.createReadStream(target).pipe(res);
 }catch(e){console.error(e);err(res,'Erro ao processar solicitação.',500)}});
server.listen(port,()=>console.log('LogiStock PRO: http://localhost:'+port));
