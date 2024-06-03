window.addEventListener('load', function() {
    const ctx = document.getElementById("myChart").getContext("2d");

    // Benutzerdefiniertes Icon als Bild laden
    const img = new Image();
    img.src = "static/images/droplet.svg";

    // Daten und Optionen für das Line Chart
    const data = {
        datasets: [
            {
                label: "Temperature",
                yAxisID: "y",
                data: [
                // temps 
                ],
                borderColor: "rgba(255, 99, 132, 1)",
                backgroundColor: "rgba(255, 99, 132, 0.2)",
                fill: false,
            },
            {
                label: "Humidity",
                yAxisID: "y1",
                data: [
                    // humiditys
                ],
                borderColor: "rgba(54, 162, 235, 1)",
                backgroundColor: "rgba(54, 162, 235, 0.2)",
                fill: false,
            },
            {
                label: "Soil moisture",
                yAxisID: "y",
                data: [
                    // soil moisture
                ],
                borderColor: "rgba(168, 113, 50, 1)",
                backgroundColor: "rgba(168, 113, 50, 0.2)",
                fill: false,
            },
            {
                label: "Watered",
                type: "scatter",
                data: [
                    // watered
                ],
                pointStyle: img,
                pointRadius: 10,
                showLine: false,
                legend: {
                    display: false, // This will hide the legend for this dataset
                },
            },
        ],
    };

    const options = {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
            mode: "index",
            intersect: false,
        },
        plugins: {
            tooltip: {
                callbacks: {
                    title: (context) => {
                        const selectedPoint = context[0];
                        if (selectedPoint.dataset.label === "Watered") {
                            const title = `Ereignis am ${selectedPoint.label}`;
                            document.title = title;
                        }
                        return selectedPoint.label;
                    },
                },
            },
            annotation: {
                annotations: {
                },
            },
            legend: {
                labels: {
                    filter: (item) => item.text !== "Watered",
                },
            },
        },
        scales: {
            x: {
                type: "time",
                time: {
                    unit: "day",
                    tooltipFormat: "ll",
                    displayFormats: {
                        day: "MMM D",
                    },
                },
                title: {
                    display: true,
                    text: "Datum",
                },
            },
            y: {
                type: "linear",
                position: "left",
                min: 5,
                max: 50,
            },
            y1: {
                type: "linear",
                position: "right",
                min: 0,
                max: 100,
                grid: {
                    drawOnChartArea: false,
                },
            },
        },
    };

    // Erstellen des Chart-Objekts
    const chart = new Chart(ctx, {
        type: "line",
        data: data,
        options: options,
    });

    // Event-Listener für Klick-Events auf dem Chart
    document.getElementById("myChart").onclick = (evt) => {
        const points = chart.getElementsAtEventForMode(
            evt,
            "nearest",
            { intersect: true },
            true
        );
        if (points.length) {
            const firstPoint = points[0];
            const label = new Date(
                firstPoint.element.x
            ).toLocaleDateString();
            if (
                chart.data.datasets[firstPoint.datasetIndex].label ===
                "Ereignisse"
            ) {
                document.title = `Ereignis am ${label}`;
            } else {
                const value1 = chart.data.datasets[firstPoint.index].y;
                const value2 = chart.data.datasets[firstPoint.index].y;
                document.title = `Tag ${label}: Dataset 1 - ${value1}, Dataset 2 - ${value2}`;
            }
        }
    };

    const forwardBtn = document.getElementById("forward");
    const backwardBtn = document.getElementById("backward");
    const fforwardBtn = document.getElementById("fforward");
    const fbackwardBtn = document.getElementById("fbackward");
    const datepicker = document.getElementById("datepicker");
    const duration = document.getElementById("duration-select");

    loadData(datepicker.value, duration.value);

    forwardBtn.addEventListener("click", () => {
        const date = new Date(datepicker.value);
        date.setDate(date.getDate() + 1);
        datepicker.valueAsDate = date;
        loadData(datepicker.value, duration.value);
    });
    backwardBtn.addEventListener("click", () => {
        const date = new Date(datepicker.value);
        date.setDate(date.getDate() - 1);
        datepicker.valueAsDate = date;
        loadData(datepicker.value, duration.value);
    });
    fforwardBtn.addEventListener("click", () => {
        const date = new Date(datepicker.value);
        date.setDate(date.getDate() + 7);
        datepicker.valueAsDate = date;
        loadData(datepicker.value, duration.value);
    });
    fbackwardBtn.addEventListener("click", () => {
        const date = new Date(datepicker.value);
        date.setDate(date.getDate() - 7);
        datepicker.valueAsDate = date;
        loadData(datepicker.value, duration.value);
    });
    datepicker.addEventListener("change", () => {
        loadData(datepicker.value, duration.value);
    });
    duration.addEventListener("change", () => {
        loadData(datepicker.value, duration.value);
    });

    function loadData(dt_to, duration) {
        let from = new Date(dt_to);
        from.setDate(from.getDate() - parseInt(duration));
        let from_date_str = from.toISOString().split("T")[0];

        const img_file_name = '/static/photos/photo_' + dt_to + '.jpg';
        const imgEle = document.getElementById('plant-img');
        imgEle.src = img_file_name;

        if (duration == 1) {
            chart.options.scales.x.time.unit = "hour";
            chart.options.scales.x.time.displayFormats = {
                hour: "HH:mm",
            };
        } else {
            chart.options.scales.x.time.unit = "day";
            chart.options.scales.x.time.displayFormats = {
                day: "MMM D",
            };
        }

        fetch(`/chart_data?from=${from_date_str}&to=${dt_to}`)
            .then((response) => response.json())
            .then((data) => {
                // remove datates
                chart.data.datasets[0].data = [];
                chart.data.datasets[1].data = [];
                chart.data.datasets[2].data = [];
                chart.data.datasets[3].data = [];
                options.plugins.annotation.annotations = {};

                data['sensors'].forEach((item) => {
                    chart.data.datasets[0].data.push({
                        x: item[0],
                        y: item[1],
                    });
                    chart.data.datasets[1].data.push({
                        x: item[0],
                        y: item[2],
                    });
                    chart.data.datasets[2].data.push({
                        x: item[0],
                        y: item[3],
                    });
                });
                if ('pump' in data['actions']) {
                    data['actions']['pump'].forEach((action, index) => {
                        chart.data.datasets[3].data.push({
                            x: action['dt_from'],
                            y: 6.3,
                        });
                    });
                }

                if ('light' in data['actions']) {
                    data['actions']['light'].forEach((action, index) => {
                        options.plugins.annotation.annotations[`box_light_${index}`] = {
                            type: "box",
                            xMin: action['dt_from'],
                            xMax: action['dt_to'],
                            yMin: 0,
                            yMax: "max",
                            backgroundColor: "rgba(255, 255, 0, 0.3)",
                            borderColor: "rgba(255, 255, 0, 0.3)",
                            borderWidth: 1,
                        };
                    });
                }
                if ('fan' in data['actions']) {
                    data['actions']['fan'].forEach((action, index) => {
                        options.plugins.annotation.annotations[`box_fan_${index}`] = {
                            type: "box",
                            xMin: action['dt_from'],
                            xMax: action['dt_to'],
                            yMin: 5,
                            yMax: 10,
                            backgroundColor: "rgba(0, 0, 0, 0.3)",
                            borderColor: "rgba(0, 0, 0, 0.3)",
                            borderWidth: 1,
                        };
                    });
                }

                chart.update();
            });
    }
});