/* ============================================================
   共享组件：导航 / 质感层 / 数据加载 / Coverflow / RingGallery
   ============================================================ */

const NAV_ITEMS = [
  { href: "index.html", label: "首页" },
  { href: "olympics.html", label: "奥运百年" },
  { href: "champions.html", label: "中国冠军" },
  { href: "stars.html", label: "巨星曲线" },
  { href: "spirit.html", label: "体育精神" },
  { href: "match.html", label: "精神同类" },
];

const ACCENTS = [
  ["purple", "幻紫"], ["blue", "钴蓝"], ["green", "翡翠"], ["orange", "暖橙"], ["red", "绯红"],
];

/* 滚动入场：.rise 进视口才播（IO 驱动）。先给 html 加 js-reveal，
   样式里只有 js-reveal 下才隐藏待入场元素——JS 失效时内容直接可见 */
const reduceMotion = matchMedia("(prefers-reduced-motion: reduce)");
const revealIO = new IntersectionObserver((entries) => {
  entries.forEach((en) => {
    if (en.isIntersecting) { en.target.classList.add("is-in"); revealIO.unobserve(en.target); }
  });
}, { threshold: 0.12, rootMargin: "0px 0px -7% 0px" });

function bindReveals(root = document) {
  const els = root.querySelectorAll(".rise:not(.is-in)");
  if (reduceMotion.matches) { els.forEach((el) => el.classList.add("is-in")); return; }
  els.forEach((el) => revealIO.observe(el));
}

function initChrome() {
  document.documentElement.classList.add("js-reveal");
  const nav = document.createElement("header");
  nav.className = "topnav";
  const here = location.pathname.split("/").pop() || "index.html";
  nav.innerHTML = `
    <a class="brand" href="index.html">
      <span class="brand-mark">体</span>
      <span>体育人物与体育精神<small>SPORTS LEGENDS</small></span>
    </a>
    <div class="nav-side">
      <nav class="navlinks">
        ${NAV_ITEMS.map((n) => `<a href="${n.href}" class="${n.href === here ? "on" : ""}">${n.label}</a>`).join("")}
      </nav>
      <div class="theme-dots" role="group" aria-label="切换主题色">
        ${ACCENTS.map(([k, n]) => `<button class="t-dot" data-accent="${k}" title="${n}" aria-label="主题色：${n}" aria-pressed="false"></button>`).join("")}
      </div>
    </div>`;
  document.body.prepend(nav);

  /* 主题色切换：换一组强调色 token，选择存 localStorage（"red" 即默认，不写属性） */
  const rootEl = document.documentElement;
  const dotsEl = nav.querySelector(".theme-dots");
  const syncDots = () => {
    const cur = rootEl.dataset.accent || "purple";
    dotsEl.querySelectorAll(".t-dot").forEach((d) =>
      d.setAttribute("aria-pressed", String(d.dataset.accent === cur)));
  };
  dotsEl.addEventListener("click", (e) => {
    const b = e.target.closest(".t-dot"); if (!b) return;
    try {
      if (b.dataset.accent === "purple") { delete rootEl.dataset.accent; localStorage.removeItem("site-accent"); }
      else { rootEl.dataset.accent = b.dataset.accent; localStorage.setItem("site-accent", b.dataset.accent); }
    } catch (err) { rootEl.dataset.accent = b.dataset.accent === "purple" ? "" : b.dataset.accent; }
    syncDots();
  });
  try {
    const saved = localStorage.getItem("site-accent");
    if (saved && saved !== "red") rootEl.dataset.accent = saved;
  } catch (err) { /* localStorage 不可用时保持默认 */ }
  syncDots();

  bindReveals();

  const foot = document.createElement("footer");
  foot.className = "footer";
  foot.innerHTML = `<div class="wrap">
    <div>体育人物与体育精神 · 交互式数据展陈<br>数据来源：国家体育总局、KeithGalli/Olympics-Dataset、Kaggle、百度百科图片搜索（学习交流用途）</div>
    <div><a href="index.html">首页</a> · <a href="https://github.com/CJJ-008/sports-legends" target="_blank" rel="noopener">GitHub 仓库</a></div>
  </div>`;
  document.body.append(foot);
}

async function loadJSON(name) {
  const r = await fetch(`data/${name}`);
  if (!r.ok) throw new Error(`load ${name}: ${r.status}`);
  return r.json();
}

/* 数据加载失败时的统一提示（各页面在 catch 中调用） */
function showLoadError() {
  if (document.querySelector(".load-fail")) return;
  const d = document.createElement("div");
  d.className = "load-fail";
  d.textContent = "数据加载失败，请检查网络后刷新重试。";
  document.querySelector(".wrap")?.prepend(d);
}

/* 照片缺失时返回首字母渐变卡的 DOM */
function personVisual(item, cls) {
  const wrap = document.createElement("div");
  wrap.className = cls;
  if (item.photo) {
    const img = document.createElement("img");
    img.src = `data/${item.photo}`;
    img.alt = item.name;
    img.loading = "eager";
    img.onerror = () => { img.remove(); wrap.appendChild(initialCard(item.name)); };
    wrap.appendChild(img);
  } else {
    wrap.appendChild(initialCard(item.name));
  }
  return wrap;
}
function initialCard(name) {
  const d = document.createElement("div");
  d.className = "init-card";
  d.textContent = (name || "?").trim()[0];
  return d;
}

/* ============================================================
   CoverflowStage（封面流）— 原生 JS 版
   offset 公式 + CSS transition 补间，来自 coverflow-stage 配方
   ============================================================ */
class CoverflowStage {
  constructor(el, items, { onSelect } = {}) {
    this.el = el; this.items = items; this.idx = 0; this.onSelect = onSelect;
    el.classList.add("cf-stage");
    el.innerHTML = items.map(() => `<div class="cf-card"></div>`).join("");
    this.cards = [...el.children];
    items.forEach((it, i) => {
      const c = this.cards[i];
      const visual = personVisual(it, "cf-photo");
      const meta = document.createElement("div");
      meta.className = "cf-meta";
      meta.innerHTML = `
        <span class="cf-no">LB-${String(i + 1).padStart(4, "0")}</span>
        <span class="cf-name">${it.name}</span>
        <span class="cf-sub">${it.sport || ""} · ${it.country || ""}</span>`;
      c.append(visual, meta);
      c.addEventListener("click", () => {
        if (i === this.idx) { this.onSelect && this.onSelect(it, i); }
        else { this.go(i); }
      });
    });
    this.render();
    this._key = (e) => {
      if (e.key === "ArrowRight") this.go(this.idx + 1);
      if (e.key === "ArrowLeft") this.go(this.idx - 1);
    };
    window.addEventListener("keydown", this._key);
    /* 拖拽翻页 */
    let sx = null;
    el.addEventListener("pointerdown", (e) => { sx = e.clientX; });
    el.addEventListener("pointerup", (e) => {
      if (sx === null) return;
      const dx = e.clientX - sx; sx = null;
      if (Math.abs(dx) > 50) this.go(this.idx + (dx < 0 ? 1 : -1));
    });
  }
  go(i) { this.idx = (i + this.items.length) % this.items.length; this.render(); }
  render() {
    const n = this.items.length;
    this.cards.forEach((c, i) => {
      let d = i - this.idx;
      if (d > n / 2) d -= n;
      if (d < -n / 2) d += n;
      const abs = Math.abs(d);
      c.classList.toggle("is-center", d === 0);
      if (abs > 3) {
        c.style.transform = `translateX(${Math.sign(d) * 560}px) translateZ(-480px) rotateY(${Math.sign(d) * -28}deg)`;
        c.style.opacity = "0";
        c.style.pointerEvents = "none";
      } else {
        c.style.transform = `translateX(${d * 152}px) translateY(${abs * 12}px) translateZ(${-abs * 160}px) rotateY(${d * -30}deg)`;
        c.style.filter = `brightness(${1 - abs * 0.22})`;
        c.style.opacity = "1";
        c.style.pointerEvents = "auto";
      }
      const nm = c.querySelector(".cf-name");
      if (nm) nm.style.opacity = d === 0 ? "0" : "1";
    });
    this.onchange && this.onchange(this.idx, this.items[this.idx]);
  }
  destroy() { window.removeEventListener("keydown", this._key); }
}

/* ============================================================
   RingGallery（环形画廊）— 原生 JS 版
   三层嵌套 + 拖拽吸附 + 背面连续压暗，来自 ring-gallery 配方
   ============================================================ */
class RingGallery {
  constructor(el, items, { cardWidth = 208, tilt = 16, minCards = 14, margin = 150, onFront } = {}) {
    this.el = el; this.items = items; this.onFront = onFront;
    this.rot = 0; this.cardWidth = cardWidth; this.tilt = tilt;
    const copies = Math.max(1, Math.ceil(minCards / items.length));
    this.display = [];
    for (let k = 0; k < copies; k++)
      items.forEach((it, i) => this.display.push({ it, src: i }));
    this.n = this.display.length;
    this.step = 360 / this.n;
    const W = cardWidth;
    this.radius = Math.round(W / 2 / Math.tan(Math.PI / this.n)) + margin;

    el.classList.add("rgs-stage");
    el.innerHTML = `<div class="rgs-tilt"><div class="rgs-ring"></div></div>`;
    this.ringEl = el.querySelector(".rgs-ring");
    this.display.forEach((d, i) => {
      const slot = document.createElement("div");
      slot.className = "rgs-slot";
      /* 环形定位与抬升全部走 slot 的 transform 链（JS 内联）；
         卡片绝不使用 filter —— filter 会使 preserve-3d 子树在 Chrome 扁平化，
         压暗改用卡内遮罩层 */
      const card = document.createElement("div");
      card.className = "rgs-card";
      card.style.width = W + "px";
      const visual = personVisual(d.it, "rgs-photo");
      const filmTop = document.createElement("div"); filmTop.className = "film";
      const filmBot = document.createElement("div"); filmBot.className = "film-bottom";
      filmBot.textContent = `CHN·${String(d.src + 1).padStart(3, "0")} ${d.it.name}`;
      const name = document.createElement("div"); name.className = "rgs-name"; name.textContent = d.it.name;
      const dim = document.createElement("div"); dim.className = "rgs-dim";
      card.append(filmTop, visual, name, filmBot, dim);
      slot.appendChild(card);
      card.addEventListener("click", () => {
        const target = -(i * this.step);
        const delta = ((mod360(target - this.rot) + 540) % 360) - 180;
        this.rot += delta;
        this.apply(true);
      });
      this.ringEl.appendChild(slot);
    });
    this.apply(false);
    let dragging = false, sx = 0, sr = 0, moved = 0;
    el.addEventListener("pointerdown", (e) => {
      dragging = true; sx = e.clientX; sr = this.rot; moved = 0;
      this.ringEl.style.transition = "none";
    });
    el.addEventListener("pointermove", (e) => {
      if (!dragging) return;
      const dx = e.clientX - sx;
      moved = Math.max(moved, Math.abs(dx));
      this.rot = sr + dx * 0.28;
      this.apply(false);
    });
    el.addEventListener("pointerup", () => {
      if (!dragging) return;
      dragging = false;
      this.rot = Math.round(this.rot / this.step) * this.step;
      this.apply(true);
    });
  }
  apply(animate) {
    this.ringEl.style.transition = animate ? "transform .55s var(--ease)" : "none";
    this.ringEl.style.transform = `translateZ(${-this.radius}px) rotateY(${this.rot}deg)`;
    const n = this.n;
    this.display.forEach((d, i) => {
      const world = mod360(i * this.step + this.rot);
      const facing = Math.cos((world * Math.PI) / 180);
      const bright = 0.22 + 0.78 * Math.max(0, facing) ** 2;
      const slot = this.ringEl.children[i];
      const card = slot.firstChild;
      const dim = card.querySelector(".rgs-dim");
      /* 抬升并入 slot 的 transform 链（沿卡片自身 z 轴再推 42px），
         slot 基础定位不变：rotateY(θ) translateZ(radius) [+42] */
      const lift = facing > 0.985 ? 42 : 0;
      slot.style.transform = `rotateY(${(i * this.step).toFixed(4)}deg) translateZ(${this.radius}px) translateZ(${lift}px)`;
      if (dim) dim.style.opacity = (1 - Math.min(bright, 1)).toFixed(3);
      if (facing > 0.985) this.frontSrc = d.src;
    });
    this.onFront && this.onFront(this.frontSrc);
  }
}
function mod360(x) { return ((x % 360) + 360) % 360; }

document.addEventListener("DOMContentLoaded", initChrome);
