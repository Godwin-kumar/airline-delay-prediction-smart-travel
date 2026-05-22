
window.onload = function () {

    const map = L.map('map').setView([22.9734, 78.6569], 5);

L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {

    attribution: '&copy; OpenStreetMap &copy; CARTO',

    subdomains: 'abcd',

    maxZoom: 19

}).addTo(map);

    // ✈ AIRPORT COORDS
    const AIRPORTS = {
        "DEL": [28.5562, 77.1000],
        "BOM": [19.0896, 72.8656],
        "BLR": [13.1986, 77.7066],
        "MAA": [12.9941, 80.1709],
        "HYD": [17.2403, 78.4294],
        "CCU": [22.6547, 88.4467],
        "PNQ": [18.5822, 73.9197],
        "AMD": [23.0772, 72.6347],
        "COK": [10.1520, 76.4019],
        "LKO": [26.7606, 80.8893]
    };

    let markers = {};

    function updateFlights() {

        fetch("/api/flights")
            .then(res => res.json())
            .then(data => {

                data.forEach(f => {

                    const id = f.number || Math.random();

                    let lat = f.lat;
                    let lon = f.lon;

                    // 🔥 HANDLE ALL DATA TYPES
                    if (!lat || !lon) {

                        let airportCode = null;

                        if (f.origin) airportCode = f.origin;
                        else if (f.to) airportCode = f.to;
                        else if (f.movement && f.movement.airport) {
                            airportCode = f.movement.airport.iata;
                        }

                        if (airportCode && AIRPORTS[airportCode]) {

                            lat = AIRPORTS[airportCode][0];
                            lon = AIRPORTS[airportCode][1];

                            // ✨ spread effect
                            lat += (Math.random() - 0.5) * 1;
                            lon += (Math.random() - 0.5) * 1;

                        } else {
                            return;
                        }
                    }

                    // 🔥 ROTATION (only if route exists)
                    const start = AIRPORTS[f.origin];
                    const end = AIRPORTS[f.to];

                    let angle = 0;

                    if (start && end) {
                        angle = Math.atan2(
                            end[1] - start[1],
                            end[0] - start[0]
                        ) * 180 / Math.PI - 90;
                    }

                    if (!markers[id]) {

                        const marker = L.marker([lat, lon], {
                            icon: L.divIcon({
                                html: `<div style="
                                    font-size:22px;
                                    transform: rotate(${angle}deg);
                                    color:#0078d4;
                                    transition: transform 0.5s linear;
                                ">✈</div>`,
                                className: ""
                            })
                        }).addTo(map);

                        // 🔥 CLICK PANEL
                        marker.on("click", () => {

                            const panel = document.getElementById("flightPanel");
                            const content = document.getElementById("flightContent");

                            if (!panel || !content) return;

                            panel.classList.add("active");

                            const route =
                                f.origin && f.to
                                    ? `${f.origin} ➝ ${f.to}`
                                    : f.movement?.airport?.iata
                                    ? `→ ${f.movement.airport.iata}`
                                    : "Unknown";

                            content.innerHTML = `
                                <h2>✈ ${f.number || "Unknown"}</h2>

                                <div class="info-box">
                                    <b>Route:</b> ${route}
                                </div>

                                <div class="info-box">
                                    <b>Airline:</b> ${f.airline?.name || f.airline || "Unknown"}
                                </div>

                                <div class="info-box">
                                    <b>Aircraft:</b> ${f.aircraft?.model || f.aircraft || "Unknown"}
                                </div>

                                <div class="info-box">
                                    <b>Status:</b> ${f.status || "Unknown"}
                                </div>
                            `;
                        });

                        markers[id] = marker;

                    } else {

                        // 🔄 MOVE
                        markers[id].setLatLng([lat, lon]);

                        // 🔄 UPDATE ROTATION
                        markers[id].setIcon(L.divIcon({
                            html: `<div style="
                                font-size:22px;
                                transform: rotate(${angle}deg);
                                color:#0078d4;
                                transition: transform 0.5s linear;
                            ">✈</div>`,
                            className: ""
                        }));
                    }

                });

            })
            .catch(err => console.log("❌ Fetch error:", err));
    }

    // ❌ CLOSE PANEL
    document.getElementById("closeBtn").onclick = function () {
        document.getElementById("flightPanel").classList.remove("active");
    };

    updateFlights();
    setInterval(updateFlights, 2000);
};