// Interactive map of countries studied / visited. Data: _data/places.yml
import * as d3 from "https://cdn.jsdelivr.net/npm/d3@7/+esm";
import { feature } from "https://cdn.jsdelivr.net/npm/topojson-client@3/+esm";

const root = document.querySelector(".world-map");
if (root) {
  const lang = root.dataset.lang || "en";
  const t = (en, es) => (lang === "es" ? es : en);
  const places = JSON.parse(document.querySelector(".world-map__data").textContent);
  const byId = Object.fromEntries(places.map(p => [p.id, p]));
  const svg = d3.select(root.querySelector("svg"));
  const tip = root.querySelector(".world-map__tip");
  const card = root.querySelector(".world-map__card");
  const W = 1000, H = 520;
  svg.attr("viewBox", `0 0 ${W} ${H}`);

  // 50m resolution so small countries (Andorra) exist
  const world = await (await fetch("https://cdn.jsdelivr.net/npm/world-atlas@2/countries-50m.json")).json();
  const countries = feature(world, world.objects.countries).features.filter(f => f.id !== "010");
  const projection = d3.geoNaturalEarth1().fitExtent([[6, 6], [W - 6, H - 6]], { type: "Sphere" });
  const path = d3.geoPath(projection);
  const g = svg.append("g");

  g.append("path").datum({ type: "Sphere" }).attr("class", "sphere").attr("d", path);
  const label = { studied: t("Studied here", "Estudié aquí"), sas: "Semester at Sea", visited: t("Visited", "Visitado") };
  const show = p => {
    const body = p.items ? `<ul>${p.items.map(i => `<li>${i[lang]}</li>`).join("")}</ul>`
               : p.note ? `<p>${p.note[lang]}</p>` : "";
    card.innerHTML = `<p class="kicker">${label[p.type]}</p><h3>${p.name[lang]}</h3>${body}`;
  };

  g.append("g").selectAll("path").data(countries).join("path")
    .attr("d", path)
    .attr("class", d => "country" + (byId[d.id] ? " country--" + byId[d.id].type : ""))
    .attr("tabindex", d => (byId[d.id] ? 0 : null))
    .on("mousemove", (ev, d) => {
      const p = byId[d.id]; const r = root.querySelector(".world-map__canvas").getBoundingClientRect();
      tip.hidden = false; tip.textContent = p ? p.name[lang] : d.properties.name;
      tip.style.left = (ev.clientX - r.left + 12) + "px"; tip.style.top = (ev.clientY - r.top + 12) + "px";
    })
    .on("mouseleave", () => { tip.hidden = true; })
    .on("click keydown", (ev, d) => {
      if (ev.type === "keydown" && ev.key !== "Enter") return;
      const p = byId[d.id]; if (!p) return;
      g.selectAll(".country").classed("is-selected", false);
      d3.select(ev.currentTarget).classed("is-selected", true).raise();
      show(p);
    });

  // Semester at Sea route (approximate sea path with waypoints)
  const route = [[100.5, 13.6], [102.5, 7], [104.0, 1.2], [100.3, 5.4], [95, 6], [80.5, 5.2], [76.2, 9.9], [55, 2],
                 [39.7, -4.1], [41, -12], [36.5, -20], [32.6, -26.0], [33, -32], [20, -36], [18.4, -33.9], [10, -20],
                 [6, -5], [0.0, 5.6], [-17.5, 13], [-18, 22], [-11, 32], [-5.8, 35.8], [-9.6, 39], [-8.6, 41.2],
                 [-9.8, 44], [-5, 48.5], [2, 51.2], [8.6, 53.6]];
  g.append("path").datum({ type: "LineString", coordinates: route }).attr("class", "sas-route").attr("d", path);
  const ports = [[100.5, 13.6], [100.3, 5.4], [76.2, 9.9], [39.7, -4.1], [32.6, -26.0], [18.4, -33.9], [0.0, 5.6], [-5.8, 35.8], [-8.6, 41.2], [8.6, 53.6]];
  g.append("g").selectAll("circle").data(ports).join("circle").attr("class", "sas-port")
    .attr("cx", d => projection(d)[0]).attr("cy", d => projection(d)[1]).attr("r", 2.6);

  root.querySelector(".world-map__count").textContent =
    t(`${places.length} countries`, `${places.length} países`);

  // Zoom: buttons + drag/pinch (wheel zoom only with Ctrl/⌘ so page scrolling still works)
  const zoom = d3.zoom().scaleExtent([1, 12]).translateExtent([[0, 0], [W, H]])
    .filter(ev => (ev.type === "wheel" ? ev.ctrlKey || ev.metaKey : !ev.button))
    .on("zoom", ev => { g.attr("transform", ev.transform); g.selectAll(".country, .sphere").attr("stroke-width", 0.5 / ev.transform.k);
                        g.select(".sas-route").attr("stroke-width", 1.6 / ev.transform.k); g.selectAll(".sas-port").attr("r", 2.6 / ev.transform.k); });
  svg.call(zoom);
  root.querySelectorAll("[data-zoom]").forEach(b => b.addEventListener("click", () => {
    const z = b.dataset.zoom;
    if (z === "reset") svg.transition().duration(400).call(zoom.transform, d3.zoomIdentity);
    else svg.transition().duration(300).call(zoom.scaleBy, z === "in" ? 1.8 : 1 / 1.8);
  }));
}
