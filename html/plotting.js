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

      const traces = [{
        x: defaultDist,
        y: defaultSpeed,
        mode: 'lines',
        name: 'Speed Profile',
        line: { color: 'black' }
      }];

      cassette.forEach(rear => {
        const vmin = speedFromGear(chainringSize, rear, rpmRange[0]);
        const vmax = speedFromGear(chainringSize, rear, rpmRange[1]);
        const yfill = defaultDist.map(() => vmin).concat(defaultDist.map(() => vmax).reverse());
        const xfill = defaultDist.concat([...defaultDist].reverse());

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
        xaxis: { title: 'Distance (m)', range: [Math.min(...defaultDist), Math.max(...defaultDist)] },
        yaxis: { title: 'Speed (m/s)', range: [0, 15] },
        legend: { title: { text: 'Rear Cog' } },
        hovermode: 'closest',
        plot_bgcolor: 'white',
        paper_bgcolor: 'white'
      });
    }


//    update(); // initial render