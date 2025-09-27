document.addEventListener('DOMContentLoaded', function () {
    const ctx1 = document.getElementById('userEarningsChart');
    new Chart(ctx1, {
        type: 'bar',
        data: {
            labels: chartData.user_labels,
            datasets: [{
                label: 'Earnings by User',
                data: chartData.user_earnings,
                backgroundColor: 'rgba(75, 192, 192, 0.7)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1
            }]
        }
    });

    const ctx2 = document.getElementById('reservationCountChart');
    new Chart(ctx2, {
        type: 'bar',
        data: {
            labels: chartData.user_labels,
            datasets: [{
                label: 'Reservations by User',
                data: chartData.user_reservations,
                backgroundColor: 'rgba(255, 99, 132, 0.7)',
                borderColor: 'rgba(255, 99, 132, 1)',
                borderWidth: 1
            }]
        }
    });

    const ctx3 = document.getElementById('lotRevenueChart');
    new Chart(ctx3, {
        type: 'pie',
        data: {
            labels: chartData.lot_labels,
            datasets: [{
                label: 'Parking Lot Revenue',
                data: chartData.lot_earnings,
                backgroundColor: [
                    'rgba(255, 159, 64, 0.7)',
                    'rgba(153, 102, 255, 0.7)',
                    'rgba(54, 162, 235, 0.7)',
                    'rgba(255, 205, 86, 0.7)'
                ]
            }]
        }
    });

    const ctx4 = document.getElementById('monthlyRevenueChart');
    new Chart(ctx4, {
        type: 'bar',
        data: {
            labels: chartData.months,
            datasets: [{
                label: 'Monthly Revenue',
                data: chartData.monthly_revenue,
                backgroundColor: 'rgba(54, 162, 235, 0.7)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }]
        }
    });
});
