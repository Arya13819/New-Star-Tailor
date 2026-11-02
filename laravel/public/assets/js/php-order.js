(() => {
  const form = document.querySelector('#online-order');
  if (!form) return;
  const rows = form.querySelector('#item-rows');
  let next = rows.children.length;
  const setPrice = row => {
    const select = row.querySelector('[data-service]');
    const price = row.querySelector('[data-stitch]');
    if (price) price.value = select.selectedOptions[0]?.dataset.price || '';
  };
  rows.addEventListener('change', event => {
    if (event.target.matches('[data-service]')) setPrice(event.target.closest('[data-row]'));
  });
  rows.addEventListener('click', event => {
    if (event.target.closest('[data-remove]') && rows.children.length > 1) {
      event.target.closest('[data-row]').remove();
    }
  });
  form.querySelector('#add-item-row').addEventListener('click', () => {
    if (rows.children.length >= 20) return;
    const clone = rows.firstElementChild.cloneNode(true);
    clone.querySelectorAll('input').forEach(input => { input.value = input.name === 'quantity[]' ? '1' : input.name === 'material_price[]' ? '0' : ''; });
    clone.querySelector('select').value = '';
    clone.querySelectorAll('[id]').forEach(el => {
      const previous = el.id;
      el.id = previous.replace(/-\d+$/, '-' + next);
      clone.querySelector(`label[for="${previous}"]`)?.setAttribute('for', el.id);
    });
    next++;
    rows.appendChild(clone);
  });
  const toggle = form.querySelector('#provide_measurements');
  const measurements = form.querySelector('#measurement-fields');
  const sync = () => {
    measurements.hidden = !toggle.checked;
    measurements.disabled = !toggle.checked;
  };
  toggle.addEventListener('change', sync);
  sync();
})();
