// Interactive map of countries studied / visited. Data: _data/places.yml
import * as d3 from "https://cdn.jsdelivr.net/npm/d3@7/+esm";
import { feature } from "https://cdn.jsdelivr.net/npm/topojson-client@3/+esm";

const root = document.querySelector(".world-map");
if (root) {
  const lang = root.dataset.lang || "en";
  const places = JSON.parse(document.querySelector(".world-map__data").textContent);
  const byId = Object.fromEntries(places.map(p => [p.id, p]));
  const svg = d3.select(root.querySelector("svg"));
  const tip = root.querySelector(".world-map__tip");
  const card = root.querySelector(".world-map__card");
  const W = 960, H = 500;
  svg.attr("viewBox", `0 0 ${W} ${H}`);

  const world = await (await fetch("https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json")).json();
  const countries = feature(world, world.objects.countries).features.filter(f => f.id !== "010");
  const projection = d3.geoNaturalEarth1().fitSize([W, H], { type: "FeatureCollection", features: countries });
  const path = d3.geoPath(projection);

  const show = p => {
    const t = p.type === "studied" ? (lang === "es" ? "Estudié aquí" : "Studied here") : (lang === "es" ? "Visitado" : "Visited");
    const body = p.type === "studied"
      ? `<ul>${p.items.map(i => `<li>${i[lang]}</li>`).join("")}</ul>`
      : `<p>${p.note ? p.note[lang] : ""}</p>`;
    card.innerHTML = `<p class="kicker">${t}</p><h3>${p.name[lang]}</h3>${body}`;
    card.classList.add("is-filled");
  };

  svg.append("g").selectAll("path").data(countries).join("path")
    .attr("d", path)
    .attr("class", d => "country" + (byId[d.id] ? " country--" + byId[d.id].type : ""))
    .attr("tabindex", d => byId[d.id] ? 0 : null)
    .on("mousemove", (ev, d) => {
      const p = byId[d.id]; const name = p ? p.name[lang] : d.properties.name;
      const r = root.querySelector(".world-map__canvas").getBoundingClientRect();
      tip.hidden = false; tip.textContent = name;
      tip.style.left = (ev.clientX - r.left + 12) + "px"; tip.style.top = (ev.clientY - r.top + 12) + "px";
    })
    .on("mouseleave", () => { tip.hidden = true; })
    .on("click keydown", (ev, d) => {
      if (ev.type === "keydown" && ev.key !== "Enter") return;
      if (!byId[d.id]) return;
      svg.selectAll(".country").classed("is-selected", false);
      d3.select(ev.currentTarget).classed("is-selected", true);
      show(byId[d.id]);
    });
}
