async function loadPdfFiles({ 
  owner = 'ByteMe25', 
  repo = 'ByteMe', 
  branch = 'main', 
  path, 
  divId, 
  maxFiles = Infinity, 
  exclude = [],
  sortOrder = 'ASC',
  GITHUB_TOKEN = '' 
}) {
  if (!path || !divId) {
    console.error('Parametri mancanti: serve almeno "path" e "divId".');
    return;
  }

  const container = document.getElementById(divId);
  if (!container) {
    console.warn(`Elemento con id "${divId}" non trovato.`);
    return;
  }

  const headers = GITHUB_TOKEN ? { Authorization: 'token ' + GITHUB_TOKEN } : {};
  const apiUrl = `https://api.github.com/repos/${encodeURIComponent(owner)}/${encodeURIComponent(repo)}/contents/${encodeURIComponent(path)}?ref=${encodeURIComponent(branch)}`;

  const humanFileSize = (size) => {
    if (size === 0) return '0 B';
    const i = Math.floor(Math.log(size) / Math.log(1024));
    const units = ['B','KB','MB','GB','TB'];
    return (size / Math.pow(1024, i)).toFixed(i ? 1 : 0) + ' ' + units[i];
  };

  const openPdfInBrowser = async (url) => {
    try {
      const response = await fetch(url);
      if (!response.ok) throw new Error('Errore nel download del file');
      const blob = await response.blob();
      const pdfBlob = new Blob([blob], { type: 'application/pdf' });
      const blobUrl = URL.createObjectURL(pdfBlob);

      const a = document.createElement('a');
      a.href = blobUrl;
      a.target = '_blank';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);

      setTimeout(() => URL.revokeObjectURL(blobUrl), 1000);
    } catch (err) {
      alert('Errore nel caricamento del PDF: ' + err.message);
    }
  };

  try {
    const res = await fetch(apiUrl, { headers });
    if (!res.ok) throw new Error(`GitHub API errore: ${res.status} ${res.statusText}`);
    
    const items = await res.json();
    if (!Array.isArray(items)) throw new Error('La risposta non è una lista (controlla path/branch).');
    
    let pdfs = items
      .filter(it => it.type === 'file' && /\.pdf$/i.test(it.name))
      .filter(it => ![exclude].flat().includes(it.name))
      .map(it => ({ name: it.name, size: it.size, download_url: it.download_url }));

    pdfs.sort((a, b) => {
      const compare = a.name.localeCompare(b.name, undefined, { sensitivity: 'base' });
      return sortOrder.toUpperCase() === 'DESC' ? -compare : compare;
    });

    if (Number.isFinite(maxFiles)) {
      pdfs = pdfs.slice(0, maxFiles);
    }

    container.innerHTML = '';

    if (pdfs.length === 0) {
      container.textContent = 'Nessun file trovato in questa cartella.';
      return;
    }

    const ul = document.createElement('ul');
    ul.style.listStyle = 'none';
    ul.style.padding = '0';
    ul.style.margin = '0';

    pdfs.forEach(p => {
      const li = document.createElement('li');
      li.classList.add('file_item');

      const link = document.createElement('a');
      link.textContent = p.name;
      link.style.fontWeight = '600';

      const meta = document.createElement('small');
      meta.textContent = ` — ${humanFileSize(p.size)}`;
      meta.style.color = '#666';
      meta.style.marginLeft = '6px';

      li.onclick = () => openPdfInBrowser(p.download_url);
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
