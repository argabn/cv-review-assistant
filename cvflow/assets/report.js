document.querySelectorAll('form').forEach(form => {
  const corrections = form.querySelector('.corrections');
  form.elements.correct.addEventListener('change', () => {
    corrections.hidden = !form.elements.correct.checked;
  });
  form.addEventListener('submit', event => {
    event.preventDefault();
    const feedback = form.querySelector('.feedback');
    try {
      const reviewer = form.elements.reviewer.value.trim();
      const notes = form.elements.notes.value.trim();
      if (!reviewer || !notes) throw Error('Isi nama reviewer dan catatan.');
      let corrected = null;
      if (form.elements.correct.checked) {
        corrected = {};
        form.querySelectorAll('[data-field]').forEach(group => {
          corrected[group.dataset.field] = [];
          group.querySelectorAll('[data-record]').forEach(record => {
            if (record.querySelector('[data-remove]')?.checked) return;
            const values = {};
            record.querySelectorAll('[data-key]').forEach(input => {
              values[input.dataset.key] = input.value.trim() || null;
            });
            if (record.hasAttribute('data-new') && Object.values(values).every(value => value === null)) return;
            if (!values.quote) throw Error('Setiap entri harus memiliki kutipan persis dari CV.');
            if (!Object.entries(values).some(([key,value]) => key !== 'quote' && value !== null)) throw Error('Entri fakta tidak boleh kosong.');
            corrected[group.dataset.field].push(values);
          });
        });
      }
      const payload = {reviewer, candidate_id:form.dataset.candidate, action:form.elements.action.value, notes, corrected_facts:corrected};
      const url = URL.createObjectURL(new Blob([JSON.stringify(payload,null,2)], {type:'application/json'}));
      const link = document.createElement('a');
      link.href = url; link.download = 'review_'+form.dataset.candidate+'.json'; link.click();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
      feedback.textContent = 'Review diunduh. Terapkan melalui aplikasi untuk memvalidasi koreksi.';
    } catch (error) { feedback.textContent = error.message; }
  });
});
