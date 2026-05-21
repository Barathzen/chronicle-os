import React, {useEffect, useState} from 'react'
import axios from 'axios'

export default function App(){
  const [msg, setMsg] = useState('Loading...')

  useEffect(()=>{
    // simple health-check to backend root (proxied at /api/)
    axios.get('/api/').then(res=> setMsg(res.data.message || 'Backend reachable'))
      .catch(()=> setMsg('Backend not reachable'))
  },[])

  return (
    <div style={{fontFamily:'Arial, sans-serif', padding:24}}>
      <h1>Chronicle Frontend</h1>
      <p>Status: {msg}</p>
      <p>Try the API via the backend at <code>/api/</code>.</p>
    </div>
  )
}
