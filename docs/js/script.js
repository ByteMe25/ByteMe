(async () => {
  const owner = 'ByteMe25';
  const repo  = 'ByteMe';
  const branch = 'main';
  const GITHUB_TOKEN = ''; // opzionale
  
  const folders = [
    { idDiv: 'verbali_files', path: 'Verbali' },
    { idDiv: 'candidatura_files', path: 'Candidatura' }
  ];
  
  const headers = GITHUB_TOKEN ? { Authorization: 'token ' + GITHUB_TOKEN } : {};
  
  const humanFileSize = (size) => {
    if (size === 0) return '0 B';
    const i = Math.floor(Math.log(size) / Math.log(1024));
    const units = ['B','KB','MB','GB','TB'];
    return (size / Math.pow(1024, i)).toFixed(i ? 1 : 0) + ' ' + units[i];
  };
  
  // Funzione per aprire il PDF nel viewer del browser
  const openPdfInBrowser = async (url, filename) => {
    try {
      const response = await fetch(url);
      if (!response.ok) throw new Error('Errore nel download del file');
      
      const blob = await response.blob();
      // Crea un nuovo blob con il MIME type corretto
      const pdfBlob = new Blob([blob], { type: 'application/pdf' });
      const blobUrl = URL.createObjectURL(pdfBlob);
      
      // Crea un link temporaneo e simulane il click
      const a = document.createElement('a');
      a.href = blobUrl;
      a.target = '_blank';
      a.rel = 'noopener noreferrer';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      
      // Libera la memoria dopo che il PDF è stato aperto
      setTimeout(() => URL.revokeObjectURL(blobUrl), 1000);
      
    } catch (err) {
      alert('Errore nel caricamento del PDF: ' + err.message);
    }
  };
  
  for (const folder of folders) {
    const container = document.getElementById(folder.idDiv);
    if (!container) {
      console.warn(`Elemento con id "${folder.idDiv}" non trovato.`);
      continue;
    }
    
    const apiUrl = `https://api.github.com/repos/${encodeURIComponent(owner)}/${encodeURIComponent(repo)}/contents/${encodeURIComponent(folder.path)}?ref=${encodeURIComponent(branch)}`;
    
    try {
      const res = await fetch(apiUrl, { headers });
      if (!res.ok) throw new Error(`GitHub API errore: ${res.status} ${res.statusText}`);
      
      const items = await res.json();
      if (!Array.isArray(items)) throw new Error('La risposta non è una lista (controlla path/branch).');
      
      const pdfs = items
        .filter(it => it.type === 'file' && /\.pdf$/i.test(it.name))
        .map(it => ({ name: it.name, size: it.size, download_url: it.download_url }));
      
      pdfs.sort((a, b) => b.name.localeCompare(a.name, undefined, { sensitivity: 'base' }));
      
      container.innerHTML = '';
      
      if (pdfs.length === 0) {
        container.textContent = 'Nessun file trovato in questa cartella.';
        continue;
      }
      
      const ul = document.createElement('ul');
      ul.style.listStyle = 'none';
      ul.style.padding = '0';
      ul.style.margin = '0';
      
      pdfs.forEach(p => {
        const li = document.createElement('li');
        li.style.margin = '6px 0';
        li.style.padding = '6px';
        li.style.borderRadius = '6px';
        li.style.display = 'flex';
        li.style.gap = '10px';
        li.style.alignItems = 'center';
        li.style.cursor = 'pointer';
        li.style.width = 'fit-content';
        
        const link = document.createElement('a');
        link.textContent = p.name;
        link.style.fontWeight = '600';
        
        const meta = document.createElement('small');
        meta.textContent = ` — ${humanFileSize(p.size)}`;
        meta.style.color = '#666';
        meta.style.marginLeft = '6px';
        
        li.onclick = () => openPdfInBrowser(p.download_url, p.name);
        
        li.appendChild(link);
        li.appendChild(meta);
        ul.appendChild(li);
      });
      
      container.appendChild(ul);
      
    } catch (err) {
      console.error(err);
      container.innerHTML = `<div style="color:crimson">Errore: ${err.message}</div>`;
    }
  }
})();
