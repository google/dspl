for (var td of document.querySelectorAll('td:first-child')) {
  var sibling = td.nextElementSibling;
  if (sibling) {
    if (sibling.querySelector('table')) {
      if (sibling.children.length < 20) {
        td.classList.toggle('open');
      } else {
        td.classList.toggle('closed');
        sibling.classList.toggle('hidden');
      }
      td.addEventListener('click', (ev) => {
        ev.target.classList.toggle('open');
        ev.target.classList.toggle('closed');
        ev.target.nextElementSibling.classList.toggle('hidden');
      });
    }
  }
}

function onclick(ev) {
  document.querySelectorAll('h2').forEach((elt) => {
    elt.classList.remove('active');
  });
  ev.target.classList.add('active');

  document.querySelectorAll('div').forEach((elt) => {
    elt.classList.add('hidden');
  });
  document.querySelector('div#'+ev.target.textContent.trim().toLowerCase()).classList.remove('hidden');
}

document.querySelectorAll('h2').forEach((elt) => {
  elt.addEventListener('click', onclick);
});
