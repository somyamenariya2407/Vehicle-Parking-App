document.addEventListener("DOMContentLoaded", function () {
    const commonOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                labels: {
                    color: '#f5f5f5',
                    font: { size: 12 }
                }
            }
        },
        scales: {
            x: {
                ticks: { color: '#f5f5f5' },
                grid: { color: 'rgba(255,255,255,0.1)' }
            },
            y: {
                ticks: { color: '#f5f5f5' },
                grid: { color: 'rgba(255,255,255,0.1)' }
            }
        },
        layout: {
            padding: 10
        }
    };

    new Chart(document.getElementById("reservationCountChart"), {
        type: 'bar',
        data: {
            labels: window.chartData.dates,
            datasets: [{
                label: 'Reservations',
                data: window.chartData.counts,
                backgroundColor: '#00BFFF'
            }]
        },
        options: commonOptions
    });

    new Chart(document.getElementById("lotUsageChart"), {
        type: 'doughnut',
        data: {
            labels: window.chartData.lot_labels,
            datasets: [{
                data: window.chartData.lot_data,
                backgroundColor: ['#e67e22', '#3498db', '#9b59b6', '#2ecc71', '#f1c40f']
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { color: '#f5f5f5' }
                }
            }
        }
    });

    new Chart(document.getElementById("monthlyCostChart"), {
        type: 'line',
        data: {
            labels: window.chartData.months,
            datasets: [{
                label: 'Cost (₹)',
                data: window.chartData.monthly_costs,
                borderColor: '#9B59B6',
                backgroundColor: 'rgba(155, 89, 182, 0.2)',
                fill: true,
                tension: 0.4
            }]
        },
        options: commonOptions
    });



    const ctx4 = document.getElementById('durationChart').getContext('2d');
    new Chart(ctx4, {
        type: 'bar',
        data: {
            labels: durationLabels,
            datasets: [{
                label: 'Avg. Reservation Duration (hours)',
                data: durationData,
                backgroundColor: 'rgba(214, 207, 228, 1)',
                borderColor: 'rgba(214, 207, 228, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Hours'
                    }
                }
            }
        }
    });


});
