let cassettes = {};


fetch('cassettes.json')
  .then(response => response.json())
  .then(data => {
    cassettes = data;

    const dropdown = document.getElementById('cassette');
    for (const name in cassettes) {
      const option = document.createElement('option');
      option.value = name;
      option.textContent = name;
      dropdown.appendChild(option);
    }

    update();  // render initial plot after loading
  });



    const defaultDist = Array.from({ length: 300 }, (_, i) => i).map(i => i * 10);
    const defaultSpeed = Array.from({ length: 300 }, (_, i) => 2 + 9 * i / 299);
    let rideData = undefined;



    function speedFromGear(front, rear, rpm) {
      return (front / rear) * rpm * 2.105 / 60;
    }

    function update() {
      const mid = +document.getElementById('cadence-mid').value;
      const width = +document.getElementById('cadence-width').value;
      const chainringSize = +document.getElementById('chainring').value;
      const cassetteKey = document.getElementById('cassette').value;
      document.getElementById('mid-label').innerText = mid;
      document.getElementById('width-label').innerText = width;
      document.getElementById('chainring-label').innerText = chainringSize;

      const rpmRange = [mid - width, mid + width];
      const cassette = cassettes[cassetteKey];

      const dist = rideData ? rideData.dist : defaultDist;
      const speed = rideData ? rideData.speed : defaultSpeed;

      const traces = [{
        x: dist,
        y: speed,
        mode: 'lines',
        name: 'Speed Profile',
        line: { color: 'black' }
      }];

      cassette.forEach(rear => {
        const vmin = speedFromGear(chainringSize, rear, rpmRange[0]);
        const vmax = speedFromGear(chainringSize, rear, rpmRange[1]);
        const xmin = dist[0];
        const xmax = dist[dist.length - 1];

        const xfill = [xmin, xmax, xmax, xmin];
        const yfill = [vmin, vmin, vmax, vmax];

        traces.push({
          x: xfill,
          y: yfill,
          fill: 'toself',
          mode: 'lines',
          name: `${rear}t`,
          line: { width: 0 },
          opacity: 0.4
        });
      });

      const titleStr = `Optimal Zones for Chainring ⚙️${chainringSize}T and cadence 🚴🏽‍♂️${rpmRange[0]}-${rpmRange[1]}`;
      Plotly.newPlot('plot', traces, {
        title: titleStr,
        xaxis: { title: 'Distance (m)', range: [Math.min(...dist), Math.max(...dist)] },
        yaxis: { title: 'Speed (m/s)', range: [0, 15] },
        legend: { title: { text: 'Rear Cog' } },
        hovermode: 'closest',
        plot_bgcolor: 'white',
        paper_bgcolor: 'white'
      });
    }

document.getElementById("tcx-upload").addEventListener("change", function (event) {
  const file = event.target.files[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = function (e) {
    const parser = new DOMParser();
    const xmlDoc = parser.parseFromString(e.target.result, "text/xml");

    const trackpoints = xmlDoc.getElementsByTagNameNS("*", "Trackpoint");
    let distVals = [];
    let speedVals = [];
    let prevDist = 0;

    for (let i = 0; i < trackpoints.length; i++) {
      const tp = trackpoints[i];
      const distEl = tp.getElementsByTagNameNS("*", "DistanceMeters")[0];
      const speedEl = tp.getElementsByTagNameNS("*", "Speed")[0];

      if (distEl && speedEl) {
        const currDist = parseFloat(distEl.textContent);
        const speed = parseFloat(speedEl.textContent);

        speedVals.push(speed);
        const deltaDist = currDist - prevDist;
        distVals.push(deltaDist);
        prevDist = currDist;
      }
    }

    if (speedVals.length === 0 || distVals.length === 0) {
      document.getElementById("upload-status").textContent = "No valid data in file.";
      return;
    }

    // Sort (speed, dist) pairs by speed
    const pairs = speedVals.map((s, i) => [s, distVals[i]]);
    pairs.sort((a, b) => a[0] - b[0]);
    speedVals = pairs.map(p => p[0]);
    distVals = pairs.map(p => p[1]);

    // Compute cumulative distance
    let commulDistVals = [];
    let acc = 0;
    for (let i = 0; i < distVals.length; i++) {
      acc += distVals[i];
      commulDistVals.push(acc);
    }

    rideData = {
      dist: commulDistVals,
      speed: speedVals
    };

    document.getElementById("upload-status").textContent = "File parsed successfully.";
    update();  // re-render plot with rideData
  };

  reader.readAsText(file);
});
