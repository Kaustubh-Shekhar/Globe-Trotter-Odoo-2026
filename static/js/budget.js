/* Budget doughnut chart. The ONE place in this project that talks JSON —
   everything else is form POST -> redirect -> flash. */

(function () {
    "use strict";

    var canvas = document.getElementById("budgetChart");
    if (!canvas) { return; }

    var tripId = canvas.dataset.tripId;
    var empty = document.getElementById("chartEmpty");

    var COLORS = ["#FF6B4A", "#2B3A67", "#4C9F70", "#E8B44A", "#8B7BA8"];

    fetch("/api/trips/" + tripId + "/budget")
        .then(function (res) {
            if (!res.ok) { throw new Error("HTTP " + res.status); }
            return res.json();
        })
        .then(function (data) {
            var labels = [];
            var values = [];

            Object.keys(data.by_category).forEach(function (key) {
                if (data.by_category[key] > 0) {
                    labels.push(key);
                    values.push(data.by_category[key]);
                }
            });

            if (!labels.length) {
                canvas.style.display = "none";
                if (empty) { empty.textContent = "Nothing costed yet — add activities or expenses."; }
                return;
            }

            new Chart(canvas, {
                type: "doughnut",
                data: {
                    labels: labels,
                    datasets: [{
                        data: values,
                        backgroundColor: COLORS,
                        borderColor: "#fff",
                        borderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    cutout: "58%",
                    plugins: {
                        legend: {
                            position: "bottom",
                            labels: { padding: 14, font: { size: 12 } }
                        },
                        tooltip: {
                            callbacks: {
                                label: function (ctx) {
                                    var pct = Math.round(ctx.parsed / data.total * 100);
                                    return " " + ctx.label + ": Rs " +
                                           ctx.parsed.toLocaleString("en-IN") +
                                           " (" + pct + "%)";
                                }
                            }
                        }
                    }
                }
            });
        })
        .catch(function (err) {
            canvas.style.display = "none";
            if (empty) { empty.textContent = "Could not load the chart (" + err.message + ")."; }
        });
})();
