/* =========================================================
   📄 FUNZIONE CONDIVISA – apertura PDF in nuova tab
   ========================================================= */
async function openPdfInBrowser(url, name) {
  try {
    const response = await fetch(url);
    if (!response.ok) throw new Error('Errore nel download del file');

    const blob = await response.blob();
    const blobUrl = URL.createObjectURL(
      new Blob([blob], { type: 'application/pdf' })
    );

    const newTab = window.open();
    if (!newTab) {
      alert('Consenti i pop-up per aprire il PDF.');
      return;
    }

    newTab.document.write(`
      <html>
        <head>
          <title>${name}</title>
          <style>
            html, body {
              margin: 0;
              height: 100%;
              background: #121212;
            }
            embed {
              width: 100%;
              height: 100%;
              border: none;
            }
          </style>
        </head>
        <body>
          <embed src="${blobUrl}" type="application/pdf">
        </body>
      </html>
    `);

    newTab.document.close();
    setTimeout(() => URL.revokeObjectURL(blobUrl), 10000);
  } catch (err) {
    alert('Errore nel caricamento del PDF: ' + err.message);
  }
}

/* ==== CARICAMENTO LISTA PDF ===== */
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
  if (!path || !divId) return;

  const container = document.getElementById(divId);
  if (!container) return;

  const headers = GITHUB_TOKEN ? { Authorization: 'token ' + GITHUB_TOKEN } : {};
  const apiUrl = `https://api.github.com/repos/${owner}/${repo}/contents/${path}?ref=${branch}`;

  const humanFileSize = (size) => {
    if (!size) return '0 B';
    const i = Math.floor(Math.log(size) / Math.log(1024));
    return (size / Math.pow(1024, i)).toFixed(1) + ' ' + ['B','KB','MB','GB'][i];
  };

  try {
    const res = await fetch(apiUrl, { headers });
    const items = await res.json();
    const excludeList = Array.isArray(exclude) ? exclude : [exclude];

    if (!res.ok || !Array.isArray(items)) {
      const msg = items?.message || `Errore HTTP ${res.status}`;
      container.innerHTML = `<div style="color:crimson">Errore API GitHub: ${msg}</div>`;
      return;
    }

    let pdfs = items
      .filter(f => f.type === 'file' && /\.pdf$/i.test(f.name))
      .filter(f => !excludeList.some(e => f.name.toLowerCase().includes(e.toLowerCase())));

    pdfs.sort((a, b) => {
      const cmp = a.name.localeCompare(b.name, undefined, { numeric: true });
      return sortOrder === 'DESC' ? -cmp : cmp;
    });

    if (Number.isFinite(maxFiles)) pdfs = pdfs.slice(0, maxFiles);

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

/* ==== SINGOLO PDF ==== */
async function loadSinglePdfLink({
  owner = 'ByteMe25',
  repo = 'ByteMe',
  branch = 'main',
  path = '',
  fileName,
  divId,
  GITHUB_TOKEN = ''
}) {
  if (!path || !fileName || !divId) return;

  const target = document.getElementById(divId);
  if (!target) return;

  const headers = GITHUB_TOKEN ? { Authorization: 'token ' + GITHUB_TOKEN } : {};
  const apiUrl = `https://api.github.com/repos/${owner}/${repo}/contents/${path}?ref=${branch}`;

  try {
    const res = await fetch(apiUrl, { headers });
    const items = await res.json();

    const regex = new RegExp(`^${fileName}.*\\.pdf$`, 'i');

    const file = items
      .filter(f => f.type === 'file' && regex.test(f.name))
      .sort((a, b) => a.name.localeCompare(b.name, undefined, { numeric: true }))
      .at(-1); // ultima versione

    if (!file) {
      target.innerHTML = '<div style="color:crimson">File non trovato</div>';
      return;
    }

    const a = document.createElement('a');
    a.href = '#';
    a.onclick = e => {
      e.preventDefault();
      openPdfInBrowser(file.download_url, file.name);
    };

    const h3 = document.createElement('h3');
    h3.textContent = file.name
      .replace(/_/g, ' ')
      .replace(/\.pdf$/i, '');

    a.appendChild(h3);
    target.appendChild(a);
  } catch (err) {
    target.innerHTML = `<div style="color:crimson">${err.message}</div>`;
  }
}
