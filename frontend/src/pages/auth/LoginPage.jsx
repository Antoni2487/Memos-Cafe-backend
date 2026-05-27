import { useState } from "react";
import { useNavigate } from "react-router-dom";
import authService from "../../services/authService";

function FloralWatermark() {
  return (
    <svg viewBox="0 0 600 600" xmlns="http://www.w3.org/2000/svg" className="absolute inset-0 w-full h-full" style={{ opacity: 0.07 }}>
      <g transform="translate(300,300)">
        {[0,45,90,135,180,225,270,315].map((angle,i)=>(<ellipse key={i} cx={0} cy={-110} rx={22} ry={65} fill="white" transform={`rotate(${angle})`}/>))}
        {[22.5,67.5,112.5,157.5,202.5,247.5,292.5,337.5].map((angle,i)=>(<ellipse key={i} cx={0} cy={-75} rx={15} ry={45} fill="white" transform={`rotate(${angle})`}/>))}
        <circle cx={0} cy={0} r={28} fill="white"/>
        <circle cx={0} cy={0} r={16} fill="none" stroke="white" strokeWidth={2}/>
        {[0,60,120,180,240,300].map((angle,i)=>(<circle key={i} cx={Math.cos((angle*Math.PI)/180)*10} cy={Math.sin((angle*Math.PI)/180)*10} r={3} fill="white"/>))}
      </g>
      <g transform="translate(300,300)">
        {[0,60,120,180,240,300].map((angle,i)=>{
          const rad=(angle*Math.PI)/180;
          const x=Math.cos(rad)*180; const y=Math.sin(rad)*180;
          return(<g key={i} transform={`translate(${x},${y}) rotate(${angle+90})`}><ellipse cx={0} cy={0} rx={12} ry={35} fill="white"/><ellipse cx={0} cy={-50} rx={8} ry={22} fill="white"/><ellipse cx={0} cy={50} rx={8} ry={22} fill="white"/></g>);
        })}
      </g>
      {[[80,80],[520,80],[80,520],[520,520]].map(([tx,ty],idx)=>(
        <g key={idx} transform={`translate(${tx},${ty})`}>
          {[0,72,144,216,288].map((angle,i)=>(<ellipse key={i} cx={0} cy={-35} rx={10} ry={28} fill="white" transform={`rotate(${angle})`}/>))}
          <circle cx={0} cy={0} r={12} fill="white"/>
          <ellipse cx={-45} cy={idx<2?-20:20} rx={8} ry={25} fill="white" transform={`rotate(${idx<2?-30:30},-45,${idx<2?-20:20})`}/>
          <ellipse cx={45} cy={idx<2?-20:20} rx={8} ry={25} fill="white" transform={`rotate(${idx<2?30:-30},45,${idx<2?-20:20})`}/>
          <ellipse cx={0} cy={idx<2?-65:65} rx={8} ry={25} fill="white"/>
        </g>
      ))}
      <path d="M 80 300 Q 150 200 300 180 Q 450 160 520 300 Q 450 440 300 420 Q 150 400 80 300 Z" fill="none" stroke="white" strokeWidth={1.5}/>
      <path d="M 120 300 Q 190 230 300 215 Q 410 200 480 300 Q 410 400 300 385 Q 190 370 120 300 Z" fill="none" stroke="white" strokeWidth={1}/>
      {[[180,120],[420,120],[150,480],[450,480],[80,200],[520,200],[80,400],[520,400],[220,80],[380,80],[220,520],[380,520]].map(([cx,cy],i)=>(
        <g key={i} transform={`translate(${cx},${cy})`}>
          {[0,60,120,180,240,300].map((angle,j)=>(<ellipse key={j} cx={0} cy={-14} rx={5} ry={12} fill="white" transform={`rotate(${angle})`}/>))}
          <circle cx={0} cy={0} r={5} fill="white"/>
        </g>
      ))}
    </svg>
  );
}

function MemosLogo() {
  return (
    <div className="w-32 h-32 flex items-center justify-center">
      {/*
        REEMPLAZA ESTE SVG CON TU LOGO
        Opción A: <img src="/logo.png" alt="Memo's" className="w-full h-full object-contain" style={{ filter: "brightness(0) invert(1)" }} />
        Opción B: pega aquí el SVG del logo con fill="white"
      */}
      <svg viewBox="0 0 100 100" fill="white" xmlns="http://www.w3.org/2000/svg">
        {/* Tu logo aquí */}
      </svg>
    </div>
  );
}

function EnvelopeIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <rect x="2" y="4" width="20" height="16" rx="2"/>
      <path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>
    </svg>
  );
}

function LockIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
      <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
    </svg>
  );
}

function EyeIcon({ open }) {
  if (open) return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/>
      <circle cx="12" cy="12" r="3"/>
    </svg>
  );
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M9.88 9.88a3 3 0 1 0 4.24 4.24"/>
      <path d="M10.73 5.08A10.43 10.43 0 0 1 12 5c7 0 10 7 10 7a13.16 13.16 0 0 1-1.67 2.68"/>
      <path d="M6.61 6.61A13.526 13.526 0 0 0 2 12s3 7 10 7a9.74 9.74 0 0 0 5.39-1.61"/>
      <line x1="2" x2="22" y1="2" y2="22"/>
    </svg>
  );
}

function Spinner() {
  return (
    <svg className="animate-spin w-4 h-4" viewBox="0 0 24 24" fill="none">
      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
    </svg>
  );
}

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await authService.login(email, password);
      navigate("/dashboard");
    } catch (err) {
      setError("Correo o contraseña incorrectos.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen w-full flex items-center justify-center relative overflow-hidden" style={{ backgroundColor: "#2C5545" }}>

      {/* Floral watermark */}
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none select-none">
        <div className="w-full h-full max-w-3xl mx-auto">
          <FloralWatermark />
        </div>
      </div>

      {/* Card */}
      <div className="relative w-full max-w-lg mx-4 rounded-xl overflow-hidden" style={{ boxShadow: "0 30px 80px rgba(0,0,0,0.4), 0 0 0 1px rgba(255,255,255,0.08)" }}>

        {/* Top bar decorativo */}
        <div className="px-4 py-3 flex items-center gap-2" style={{ backgroundColor: "#234A3A", borderBottom: "1px solid rgba(255,255,255,0.08)" }}>
          <div className="w-3 h-3 rounded-full bg-red-400 opacity-80"/>
          <div className="w-3 h-3 rounded-full bg-yellow-400 opacity-80"/>
          <div className="w-3 h-3 rounded-full bg-green-400 opacity-80"/>
        </div>

        {/* Contenido */}
        <div className="px-8 pb-10 pt-8 flex flex-col items-center" style={{ backgroundColor: "#2C5545" }}>

          {/* Logo */}
          <div className="mb-8">
            <MemosLogo />
          </div>

          {/* Tarjeta crema */}
          <div className="w-full rounded-lg px-8 py-8" style={{ backgroundColor: "#F8F4EE", boxShadow: "0 8px 32px rgba(0,0,0,0.25), inset 0 1px 0 rgba(255,255,255,0.6)" }}>

            {/* Título */}
            <div className="text-center mb-7">
              <h1 style={{ fontFamily: "'Playfair Display', Georgia, serif", color: "#2C5545", fontSize: "1.35rem", fontWeight: 500, letterSpacing: "0.01em" }}>
                Inicio de Sesión
              </h1>
              <div className="mx-auto mt-3 w-10 h-px opacity-30" style={{ backgroundColor: "#2C5545" }}/>
            </div>

            <form onSubmit={handleSubmit} className="flex flex-col gap-4">

              {/* Email */}
              <div className="flex flex-col gap-1.5">
                <label className="text-xs text-[#4a4a4a] tracking-wide" style={{ fontFamily: "'Playfair Display', Georgia, serif" }}>
                  Correo electrónico
                </label>
                <div className="flex items-center gap-3 px-3.5 py-2.5 rounded-md bg-white border border-[#C8C8C8] focus-within:border-[#2C5545] transition-colors">
                  <span className="text-[#8a8a8a]"><EnvelopeIcon /></span>
                  <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="correo@ejemplo.com" required className="flex-1 outline-none bg-transparent text-sm text-[#333] placeholder-gray-300"/>
                </div>
              </div>

              {/* Password */}
              <div className="flex flex-col gap-1.5">
                <label className="text-xs text-[#4a4a4a] tracking-wide" style={{ fontFamily: "'Playfair Display', Georgia, serif" }}>
                  Contraseña
                </label>
                <div className="flex items-center gap-3 px-3.5 py-2.5 rounded-md bg-white border border-[#C8C8C8] focus-within:border-[#2C5545] transition-colors">
                  <span className="text-[#8a8a8a]"><LockIcon /></span>
                  <input type={showPassword ? "text" : "password"} value={password} onChange={(e) => setPassword(e.target.value)} placeholder="••••••••" required className="flex-1 outline-none bg-transparent text-sm text-[#333] placeholder-gray-300"/>
                  <button type="button" onClick={() => setShowPassword(!showPassword)} className="text-[#8a8a8a] hover:text-[#2C5545] transition-colors" tabIndex={-1}>
                    <EyeIcon open={showPassword} />
                  </button>
                </div>
              </div>

              {/* Error */}
              {error && (
                <p className="text-xs text-red-600 text-center bg-red-50 rounded py-2 px-3">{error}</p>
              )}

              {/* Botón */}
              <button type="submit" disabled={loading}
                className="w-full py-3 rounded-md mt-1 text-[#F8F4EE] text-xs font-semibold tracking-[0.18em] transition-all disabled:opacity-70 disabled:cursor-not-allowed hover:opacity-90 active:scale-[0.99]"
                style={{ backgroundColor: "#1E4A37", fontFamily: "'Playfair Display', Georgia, serif", boxShadow: loading ? "none" : "0 4px 14px rgba(30,74,55,0.35)" }}
              >
                {loading ? (<span className="flex items-center justify-center gap-2"><Spinner /> Iniciando...</span>) : "INICIAR SESIÓN"}
              </button>

            </form>
          </div>

          {/* Footer */}
          <p className="mt-6 text-center text-[0.68rem] tracking-[0.12em]" style={{ color: "rgba(248,244,238,0.45)", fontFamily: "'Playfair Display', Georgia, serif" }}>
            COFFEE · POSTRES · CHAMPAGNE
          </p>

        </div>
      </div>
    </div>
  );
}