// Optional UX enhancements could go here. Intentionally minimal.
document.addEventListener('DOMContentLoaded', () => {
  const firstRadio = document.querySelector('input[type="radio"][name="choice"]');
  if (firstRadio) {
    // Enable keyboard-friendly selection on card click
    document.querySelectorAll('.choice').forEach((el) => {
      el.addEventListener('click', () => {
        const input = el.querySelector('input[type="radio"]');
        if (input) input.checked = true;
        document.querySelectorAll('.choice').forEach(c => c.classList.remove('selected'));
        el.classList.add('selected');
      });
    });
  }
});


