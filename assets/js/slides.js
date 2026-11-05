// Slides: active section in menu/dots, reveal on view, carousels, theme toggle
(function () {
  var me = document.currentScript;
  var slides = [].slice.call(document.querySelectorAll('.slide'));
  var links = [].slice.call(document.querySelectorAll('[data-target]'));

  // Active section + reveal
  function update() {
    var cur = slides[0] && slides[0].id, mid = window.innerHeight * 0.45;
    slides.forEach(function (s) {
      var r = s.getBoundingClientRect();
      if (r.top <= mid) cur = s.id;
      if (r.top < window.innerHeight * 0.85 && r.bottom > 0) s.classList.add('in-view');
    });
    links.forEach(function (a) { a.classList.toggle('is-active', a.dataset.target === cur); });
  }
  window.addEventListener('scroll', update, { passive: true });
  window.addEventListener('resize', update);
  update(); setTimeout(update, 250);

  // Group a section's content into blocks by its h3 headings (for grid layouts)
  function blocks(sel) {
    var body = document.querySelector(sel + ' .slide__body'); if (!body) return;
    var kids = [].slice.call(body.childNodes), cur = null, lead = document.createElement('div');
    lead.className = 'block block--lead';
    var out = [];
    kids.forEach(function (n) {
      if (n.nodeType === 1 && n.tagName === 'H3') { cur = document.createElement('div'); cur.className = 'block'; out.push(cur); }
      (cur || lead).appendChild(n);
    });
    if (lead.childNodes.length) body.appendChild(lead);
    out.forEach(function (b, i) { b.classList.add('block--' + (i + 1)); body.appendChild(b); });
    body.classList.add('has-blocks');
  }
  blocks('.slide--research');
  blocks('.slide--cv');

  // Carousels for news and projects
  function carousel(slideSel, itemSel) {
    var slide = document.querySelector(slideSel); if (!slide) return;
    var items = [].slice.call(slide.querySelectorAll(itemSel)); if (items.length < 2) return;
    var wrap = document.createElement('div'); wrap.className = 'carousel';
    var track = document.createElement('div'); track.className = 'carousel__track';
    items[0].parentNode.insertBefore(wrap, items[0]);
    items.forEach(function (it) { track.appendChild(it); });
    wrap.appendChild(track);
    var nav = document.createElement('div'); nav.className = 'carousel__nav';
    var dots = document.createElement('div'); dots.className = 'carousel__dots';
    items.forEach(function () { dots.appendChild(document.createElement('i')); });
    var prev = document.createElement('button'); prev.type = 'button'; prev.innerHTML = '&#8592;'; prev.setAttribute('aria-label', me.dataset.prev);
    var next = document.createElement('button'); next.type = 'button'; next.innerHTML = '&#8594;'; next.setAttribute('aria-label', me.dataset.next);
    nav.append(dots, prev, next); wrap.appendChild(nav);
    function step() { return items[0].getBoundingClientRect().width + 19; }
    prev.onclick = function () { track.scrollBy({ left: -step(), behavior: 'smooth' }); };
    next.onclick = function () { track.scrollBy({ left: step(), behavior: 'smooth' }); };
    function sync() {
      var i = Math.round(track.scrollLeft / step()), max = track.scrollWidth - track.clientWidth - 4;
      [].forEach.call(dots.children, function (d, j) { d.classList.toggle('on', j === i); });
      prev.disabled = track.scrollLeft < 4; next.disabled = track.scrollLeft >= max;
    }
    track.addEventListener('scroll', sync, { passive: true }); window.addEventListener('resize', sync); sync();
  }
  carousel('.slide--news', '.news-card');
  carousel('.slide--projects', '.project-card');

  // Theme toggle
  var btn = document.querySelector('.theme');
  function icon() { btn.innerHTML = document.documentElement.getAttribute('data-theme') === 'dark' ? '<i class="fas fa-sun"></i>' : '<i class="fas fa-moon"></i>'; }
  if (btn) { icon(); btn.onclick = function () {
    var dark = document.documentElement.getAttribute('data-theme') !== 'dark';
    if (dark) document.documentElement.setAttribute('data-theme', 'dark'); else document.documentElement.removeAttribute('data-theme');
    localStorage.setItem('theme', dark ? 'dark' : 'light'); icon(); }; }
})();
