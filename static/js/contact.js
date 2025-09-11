document.addEventListener('DOMContentLoaded', function () {
    if (window.lucide) lucide.createRicons?.() || lucide.createIcons();


    const form = document.getElementById('contact-form');
    const btn = form.querySelector('button[type="submit"]');
    const alertBox = document.getElementById('form-alert');

    const setAlert = (type, msg) => {
      if (!msg) { alertBox.innerHTML = ''; return; }
      const cls = type === 'success'
        ? 'border-green-500/40 bg-green-500/10 text-green-200'
        : 'border-red-500/40 bg-red-500/10 text-red-200';
      alertBox.innerHTML =
        `<div class="rounded-md border px-4 py-3 ${cls}">${msg}</div>`;
    };

    const clearErrors = () => {
      form.querySelectorAll('.js-error').forEach(p => { p.textContent = ''; p.hidden = true; });
      form.querySelectorAll('[aria-invalid="true"]').forEach(i => {
        i.setAttribute('aria-invalid', 'false');
        i.classList.remove('ring-2', 'ring-red-500/70');
      });
    };

    const setFieldError = (field, msg) => {
      const p = form.querySelector(`.js-error[data-field="${field}"]`);
      const input = form.querySelector(`[name="${field}"]`);
      if (p) { p.textContent = msg; p.hidden = false; }
      if (input) {
        input.setAttribute('aria-invalid', 'true');
        input.classList.add('ring-2', 'ring-red-500/70');
      }
    };

    const getCSRF = () => {
      const m = document.cookie.match(/csrftoken=([^;]+)/);
      return m ? decodeURIComponent(m[1]) : '';
    };

    // Limpieza de errores al escribir
    form.addEventListener('input', (e) => {
      const t = e.target;
      if (t && t.name) {
        const p = form.querySelector(`.js-error[data-field="${t.name}"]`);
        if (p && !t.classList.contains('ring-red-500/70')) {
          p.textContent = ''; p.hidden = true;
        }
        t.setAttribute('aria-invalid', 'false');
        t.classList.remove('ring-2', 'ring-red-500/70');
      }
    });

    form.addEventListener('submit', async (ev) => {
      ev.preventDefault();
      clearErrors(); setAlert('', '');

      btn.disabled = true;
      btn.classList.add('opacity-60', 'pointer-events-none');

      try {
        const res = await fetch(form.action, {
          method: 'POST',
          headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': getCSRF(),
          },
          body: new FormData(form),
        });

        // Puede devolver 200 (ok) o 4xx/5xx con JSON
        const data = await res.json().catch(() => ({}));

        if (!data.ok) {
          if (data && data.errors) {
            // Errores por campo + globales
            Object.entries(data.errors).forEach(([field, arr]) => {
              const first = Array.isArray(arr) ? arr[0] : String(arr);
              if (field === '__all__') setAlert('error', first);
              else setFieldError(field, first);
            });
          } else {
            setAlert('error', data.message || 'No se pudo enviar. Inténtalo de nuevo.');
          }
          return;
        }

        // Éxito
        setAlert('success', data.message || '¡Mensaje enviado! Te contactaré pronto.');
        form.reset();

      } catch (err) {
        setAlert('error', 'No se pudo conectar. Revisa tu red e inténtalo de nuevo.');
      } finally {
        btn.disabled = false;
        btn.classList.remove('opacity-60', 'pointer-events-none');
      }
    });

    // Autofocus inicial
    const name = document.getElementById('name');
    if (name) name.focus();
  });