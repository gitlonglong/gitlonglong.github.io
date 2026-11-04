(() => {
  'use strict';
  const select = document.querySelector('#topic-filter');
  const papers = [...document.querySelectorAll('.paper')];
  document.querySelector('.topic-control').hidden = false;
  select.addEventListener('change', () => {
    let visible = 0;
    papers.forEach(paper => {
      paper.hidden = select.value !== 'all' && paper.dataset.category !== select.value;
      if (!paper.hidden) visible++;
      paper.querySelectorAll('details').forEach(detail => { detail.open = false; });
    });
    document.querySelectorAll('.year-group').forEach(group => {
      group.hidden = ![...group.querySelectorAll('.paper')].some(paper => !paper.hidden);
    });
    document.querySelector('#result-count').textContent = `${visible} ${visible === 1 ? 'paper' : 'papers'}`;
    document.querySelector('#empty-state').hidden = visible !== 0;
  });
  document.querySelectorAll('.copy-button').forEach(button => {
    button.hidden = false;
    button.addEventListener('click', async () => {
      const panel = button.closest('.citation-panel');
      const pre = panel.querySelector('pre');
      const status = panel.querySelector('.copy-status');
      try {
        await navigator.clipboard.writeText(pre.textContent);
        status.textContent = 'Copied';
      } catch {
        const range = document.createRange();
        range.selectNodeContents(pre);
        const selection = window.getSelection();
        selection.removeAllRanges();
        selection.addRange(range);
        status.textContent = 'Text selected — press Ctrl/Cmd+C';
      }
    });
  });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape') document.querySelectorAll('details[open]').forEach(detail => {
      detail.open = false;
      detail.querySelector('summary').focus();
    });
  });
})();
