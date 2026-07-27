import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import MengudoStore from './MengudoStore.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <MengudoStore/>
  </StrictMode>,
)
